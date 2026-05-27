"""Tests for v1.2 adaptive compression state machine.

Mirrors the TypeScript AdaptiveState logic in Python for deterministic
unit testing of state machine transitions, hysteresis, cooldown,
oscillation detection, and null-signal handling.

The entry point function is ``resolve_adaptive_mode``, which takes the
current state + signal + round counter and returns the next state.
All logic is self-contained — no MCP server or external imports needed.
"""

import pytest


# =============================================================================
# State machine mirror — matches TypeScript Plugin logic exactly
# =============================================================================


class AdaptiveState:
    """Mirror of the TypeScript AdaptiveState for testing."""

    def __init__(self):
        self.mode: str = "unknown"
        self.round_counter: int = 0
        self.cooldown_until: int = 0
        self.signal_history: list = []
        self.rounds_with_high_signal: int = 0
        self.rounds_with_low_signal: int = 0
        self.switch_history: list = []
        self.unstable: bool = False
        self.signal_cold: bool = False


def resolve_adaptive_mode(
    current: AdaptiveState,
    signal: float | None,
    total_rounds: int,
) -> AdaptiveState:
    """Mirror of the TypeScript resolveAdaptiveMode for testing.

    Parameters
    ----------
    current : AdaptiveState
        State from previous round.
    signal : float | None
        Memory pressure signal: None if cold/dead, 0.0–1.0 otherwise.
    total_rounds : int
        Current round counter (monotonic).

    Returns
    -------
    AdaptiveState
        Next state with updated mode, counters, and history.
    """
    next_state = AdaptiveState()
    next_state.round_counter = total_rounds
    next_state.cooldown_until = current.cooldown_until
    next_state.signal_history = (current.signal_history + [signal or 0])[-5:]
    next_state.rounds_with_high_signal = current.rounds_with_high_signal
    next_state.rounds_with_low_signal = current.rounds_with_low_signal
    next_state.switch_history = list(current.switch_history)
    next_state.unstable = current.unstable
    next_state.signal_cold = current.signal_cold

    # --- Null signal: no signal data available (cold / dead) ---
    if signal is None:
        next_state.signal_cold = True
        next_state.mode = current.mode if current.mode != "unknown" else "compact"
        return next_state

    next_state.signal_cold = False

    # --- UNKNOWN → initial decision ---
    if current.mode == "unknown":
        next_state.mode = "full" if signal > 0.3 else "compact"
        next_state.switch_history.append(
            {
                "ts": "2026-01-01T00:00:00Z",
                "from": "unknown",
                "to": next_state.mode,
                "round": total_rounds,
            }
        )
        next_state.cooldown_until = total_rounds + 10
        return next_state

    next_state.mode = current.mode

    # --- Cooldown check ---
    if total_rounds < current.cooldown_until:
        return next_state

    # --- Oscillation unlock ---
    if current.unstable:
        history = next_state.signal_history
        stable = len(history) >= 5 and all(
            s <= 0.1 or s >= 0.3 for s in history
        )
        if stable:
            next_state.unstable = False
            # Fall through — allow normal signal tracking and switching
        else:
            return next_state  # stay locked

    # --- Track consecutive signal ---
    if signal > 0.3:
        next_state.rounds_with_high_signal = current.rounds_with_high_signal + 1
        next_state.rounds_with_low_signal = 0
    elif signal <= 0.1:
        next_state.rounds_with_low_signal = current.rounds_with_low_signal + 1
        next_state.rounds_with_high_signal = 0
    else:
        # Ambiguous zone (0.1 < signal <= 0.3) — reset both
        next_state.rounds_with_high_signal = 0
        next_state.rounds_with_low_signal = 0

    # --- Switch with 3-round hysteresis ---
    if current.mode == "compact" and next_state.rounds_with_high_signal >= 3:
        next_state.mode = "full"
        next_state.rounds_with_high_signal = 0
        next_state.rounds_with_low_signal = 0
        next_state.cooldown_until = total_rounds + 10
        next_state.switch_history.append(
            {
                "ts": "2026-01-01T00:00:00Z",
                "from": "compact",
                "to": "full",
                "round": total_rounds,
            }
        )
    elif current.mode == "full" and next_state.rounds_with_low_signal >= 3:
        next_state.mode = "compact"
        next_state.rounds_with_high_signal = 0
        next_state.rounds_with_low_signal = 0
        next_state.cooldown_until = total_rounds + 10
        next_state.switch_history.append(
            {
                "ts": "2026-01-01T00:00:00Z",
                "from": "full",
                "to": "compact",
                "round": total_rounds,
            }
        )

    # --- Oscillation detection: ≥5 switches in <50 rounds → lock FULL ---
    recent_sw = next_state.switch_history[-5:]
    if len(recent_sw) >= 5:
        span = total_rounds - recent_sw[0]["round"]
        if span < 50:
            next_state.unstable = True
            next_state.mode = "full"
            next_state.cooldown_until = total_rounds + 20

    return next_state


# =============================================================================
# Test cases
# =============================================================================


class TestAdaptiveStateMachine:
    """6 core state machine transition tests."""

    # -- Initial state -------------------------------------------------------

    def test_unknown_to_compact(self):
        """Low signal (≤0.3) → UNKNOWN transitions to COMPACT."""
        state = AdaptiveState()
        result = resolve_adaptive_mode(state, 0.0, 1)
        assert result.mode == "compact"
        assert result.cooldown_until == 11  # round 1 + 10

    def test_unknown_to_full(self):
        """High signal (>0.3) → UNKNOWN transitions to FULL."""
        state = AdaptiveState()
        result = resolve_adaptive_mode(state, 0.5, 1)
        assert result.mode == "full"
        assert result.cooldown_until == 11

    # -- Hysteresis (3-round persistence) ------------------------------------

    def test_compact_to_full_hysteresis(self):
        """3 consecutive high signals needed to switch COMPACT→FULL."""
        state = AdaptiveState()
        state.mode = "compact"
        state.cooldown_until = 0  # no cooldown

        state = resolve_adaptive_mode(state, 0.5, 10)
        assert state.mode == "compact"  # 1st high — not yet
        assert state.rounds_with_high_signal == 1

        state = resolve_adaptive_mode(state, 0.5, 11)
        assert state.mode == "compact"  # 2nd high — not yet
        assert state.rounds_with_high_signal == 2

        state = resolve_adaptive_mode(state, 0.5, 12)
        assert state.mode == "full"  # 3rd high → switch!
        assert state.cooldown_until == 22  # 12 + 10
        assert state.rounds_with_high_signal == 0  # reset after switch

    def test_full_to_compact_hysteresis(self):
        """3 consecutive low signals needed to switch FULL→COMPACT."""
        state = AdaptiveState()
        state.mode = "full"
        state.cooldown_until = 0

        state = resolve_adaptive_mode(state, 0.0, 20)
        assert state.mode == "full"
        assert state.rounds_with_low_signal == 1

        state = resolve_adaptive_mode(state, 0.0, 21)
        assert state.mode == "full"
        assert state.rounds_with_low_signal == 2

        state = resolve_adaptive_mode(state, 0.0, 22)
        assert state.mode == "compact"
        assert state.cooldown_until == 32  # 22 + 10
        assert state.rounds_with_low_signal == 0

    # -- Cooldown ------------------------------------------------------------

    def test_cooldown_blocks_switch(self):
        """During cooldown, signal changes are tracked but don't switch."""
        state = AdaptiveState()
        state.mode = "compact"
        state.cooldown_until = 50  # locked until round 50

        # High signals during cooldown — tracked but mode unchanged
        for i in range(3):
            state = resolve_adaptive_mode(state, 0.5, 40 + i)
        assert state.mode == "compact"
        # Counters should still be tracking (since cooldown doesn't block
        # signal tracking, just switching decisions)
        # Actually wait — the cooldown return is BEFORE signal tracking.
        # Let's verify...
        #
        # Re-reading the code:
        #   if total_rounds < current.cooldown_until: return next_state
        # This returns BEFORE tracking consecutive signals.  So counters
        # are frozen during cooldown.
        assert state.rounds_with_high_signal == 0

    # -- Null signal ---------------------------------------------------------

    def test_null_signal_sets_cold(self):
        """None signal → signal_cold = True, mode preserved (or compact)."""
        # From COMPACT
        state = AdaptiveState()
        state.mode = "compact"
        result = resolve_adaptive_mode(state, None, 5)
        assert result.signal_cold is True
        assert result.mode == "compact"

        # From UNKNOWN → defaults to compact
        state2 = AdaptiveState()
        result2 = resolve_adaptive_mode(state2, None, 1)
        assert result2.signal_cold is True
        assert result2.mode == "compact"

    # -- Oscillation detection -----------------------------------------------

    def test_oscillation_detection(self):
        """≥5 switches in <50 rounds triggers oscillation → lock FULL."""
        state = AdaptiveState()
        state.mode = "compact"
        state.cooldown_until = 0

        # Pre-populate 4 switches spanning rounds 10–45
        state.switch_history = [
            {"ts": "t1", "from": "compact", "to": "full", "round": 10},
            {"ts": "t2", "from": "full", "to": "compact", "round": 25},
            {"ts": "t3", "from": "compact", "to": "full", "round": 35},
            {"ts": "t4", "from": "full", "to": "compact", "round": 45},
        ]

        # Feed 3 consecutive high signals to trigger another switch
        state = resolve_adaptive_mode(state, 0.5, 46)
        assert state.mode == "compact"  # 1st high
        state = resolve_adaptive_mode(state, 0.5, 47)
        assert state.mode == "compact"  # 2nd high
        state = resolve_adaptive_mode(state, 0.5, 48)
        # 3rd high → switch COMPACT→FULL (round 48)
        # Then oscillation check: 5 switches in span 48-10 = 38 < 50
        assert state.mode == "full"
        assert state.unstable is True
        assert state.cooldown_until == 68  # 48 + 20 (oscillation cooldown)

    # -- Hysteresis counter reset on ambiguous signal ------------------------

    def test_ambiguous_signal_resets_counters(self):
        """Signal in (0.1, 0.3] resets both consecutive counters."""
        state = AdaptiveState()
        state.mode = "compact"
        state.cooldown_until = 0

        # Build up 2 high signals
        state = resolve_adaptive_mode(state, 0.5, 1)
        assert state.rounds_with_high_signal == 1
        state = resolve_adaptive_mode(state, 0.5, 2)
        assert state.rounds_with_high_signal == 2

        # Ambiguous signal resets counter
        state = resolve_adaptive_mode(state, 0.2, 3)
        assert state.rounds_with_high_signal == 0
        assert state.rounds_with_low_signal == 0
        assert state.mode == "compact"  # no switch
