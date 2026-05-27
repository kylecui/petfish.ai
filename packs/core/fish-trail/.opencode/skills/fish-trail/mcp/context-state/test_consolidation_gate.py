"""Tests for consolidation_gate.py — Consolidation Gate (§3.4)."""

import pytest
from datetime import datetime, timezone

from consolidation_gate import (
    ConsolidationConfig,
    ConsolidationContext,
    ConsolidationDecision,
    ConsolidationGate,
    ConsolidationResult,
    ConsolidationTrigger,
    Message,
    detect_redundancy,
    extract_exempt_messages,
    extract_key_decisions,
)
from memory_pressure_monitor import PressureLevel
from topic_registry_v2 import (
    KeyDecision,
    NeverConsolidateItem,
    NeverConsolidateType,
    TopicEntry,
    TopicState,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


def _make_topic(
    topic_id: str = "t1",
    state: TopicState = TopicState.WARM,
    summary: str = "",
    never_consolidate: list | None = None,
    key_decisions: list | None = None,
) -> TopicEntry:
    return TopicEntry(
        topic_id=topic_id,
        label="Test Topic",
        state=state,
        last_access_message_idx=10,
        compactions_since_last_access=0,
        never_consolidate_items=never_consolidate or [],
        summary=summary,
        key_decisions=key_decisions or [],
        last_raw_exchange=None,
        message_count=10,
        priority_boost=0.0,
    )


def _make_messages(
    n: int = 5, role: str = "user", content: str = "msg"
) -> list[Message]:
    return [
        Message(
            idx=i,
            role=role if i % 2 == 0 else "assistant",
            content=f"{content} {i}",
            tokens=10,
        )
        for i in range(n)
    ]


def _make_nci(idx: int = 0, type_: str = "decision") -> NeverConsolidateItem:
    return NeverConsolidateItem(
        item_id=f"nci_{idx}",
        type=type_,
        content=f"Important content {idx}",
        source_message_idx=idx,
        added_at=datetime.now(timezone.utc).isoformat(),
        reason="Test",
    )


# ---------------------------------------------------------------------------
# Tests: detect_redundancy
# ---------------------------------------------------------------------------


class TestDetectRedundancy:
    def test_no_redundancy_few_messages(self):
        msgs = _make_messages(2)
        assert detect_redundancy(msgs) is False

    def test_no_redundancy_diverse_messages(self):
        msgs = [
            Message(idx=i, role="user", content=f"unique content {i}", tokens=5)
            for i in range(10)
        ]
        assert detect_redundancy(msgs) is False

    def test_consecutive_similar_triggers(self):
        """4+ consecutive messages with same first 100 chars → redundancy."""
        msgs = [
            Message(
                idx=i,
                role="tool",
                content="read_file('/foo/bar.ts')" + " " * 50,
                tokens=5,
            )
            for i in range(5)
        ]
        assert detect_redundancy(msgs) is True

    def test_consecutive_error_messages(self):
        """3+ consecutive identical error messages → redundancy."""
        msgs = [
            Message(
                idx=i, role="assistant", content="Error: connection refused", tokens=5
            )
            for i in range(4)
        ]
        assert detect_redundancy(msgs) is True

    def test_high_duplication_count(self):
        """6+ messages with identical content → redundancy."""
        msgs = [
            Message(idx=i, role="user", content="same content", tokens=5)
            for i in range(7)
        ]
        assert detect_redundancy(msgs) is True

    def test_borderline_not_triggered(self):
        """Exactly 3 consecutive similar (not >3) → no redundancy."""
        msgs = [
            Message(
                idx=i,
                role="tool",
                content="read_file('/foo/bar.ts')" + " " * 50,
                tokens=5,
            )
            for i in range(3)
        ]
        # Add a different one to break the streak at exactly 3
        msgs.append(Message(idx=3, role="user", content="different", tokens=5))
        assert detect_redundancy(msgs) is False


# ---------------------------------------------------------------------------
# Tests: extract_key_decisions
# ---------------------------------------------------------------------------


class TestExtractKeyDecisions:
    def test_extracts_decision_with_keyword(self):
        msgs = [
            Message(idx=0, role="user", content="我决定用TypeScript写", tokens=10),
            Message(idx=1, role="assistant", content="好的，用TypeScript", tokens=10),
        ]
        decisions = extract_key_decisions(msgs, [])
        assert len(decisions) == 1
        assert "TypeScript" in decisions[0].description

    def test_no_decision_without_keyword(self):
        msgs = [
            Message(idx=0, role="user", content="hello world", tokens=5),
            Message(idx=1, role="assistant", content="hi", tokens=5),
        ]
        decisions = extract_key_decisions(msgs, [])
        assert len(decisions) == 0

    def test_skips_already_extracted(self):
        msgs = [
            Message(idx=0, role="user", content="我选择方案A", tokens=10),
            Message(idx=1, role="assistant", content="好的", tokens=5),
        ]
        # Extract once
        first = extract_key_decisions(msgs, [])
        # Extract again with existing
        second = extract_key_decisions(msgs, first)
        assert len(second) == 0

    def test_english_keywords(self):
        msgs = [
            Message(idx=0, role="user", content="I choose option B", tokens=10),
            Message(idx=1, role="assistant", content="Got it, option B", tokens=10),
        ]
        decisions = extract_key_decisions(msgs, [])
        assert len(decisions) == 1

    def test_only_user_messages_trigger(self):
        msgs = [
            Message(idx=0, role="assistant", content="I decide to use X", tokens=10),
            Message(idx=1, role="user", content="ok", tokens=5),
        ]
        decisions = extract_key_decisions(msgs, [])
        assert len(decisions) == 0


# ---------------------------------------------------------------------------
# Tests: extract_exempt_messages
# ---------------------------------------------------------------------------


class TestExtractExemptMessages:
    def test_nci_items_exempted(self):
        msgs = _make_messages(5)
        nci = [_make_nci(idx=0), _make_nci(idx=2)]
        exempt, consolidatable = extract_exempt_messages(msgs, nci)
        assert len(exempt) == 2
        assert len(consolidatable) == 3
        exempt_indices = {m.idx for m in exempt}
        assert 0 in exempt_indices
        assert 2 in exempt_indices

    def test_error_fix_pairs_preserved(self):
        msgs = [
            Message(
                idx=0,
                role="assistant",
                content="TypeError: x is not defined",
                tokens=10,
            ),
            Message(
                idx=1,
                role="assistant",
                content="Fixed by adding const x = 1",
                tokens=10,
            ),
            Message(idx=2, role="user", content="thanks", tokens=5),
        ]
        exempt, consolidatable = extract_exempt_messages(
            msgs, [], preserve_error_fix_pairs=True
        )
        assert len(exempt) == 2  # error + fix
        assert len(consolidatable) == 1

    def test_no_error_fix_when_disabled(self):
        msgs = [
            Message(
                idx=0,
                role="assistant",
                content="TypeError: x is not defined",
                tokens=10,
            ),
            Message(
                idx=1,
                role="assistant",
                content="Fixed by adding const x = 1",
                tokens=10,
            ),
            Message(idx=2, role="user", content="thanks", tokens=5),
        ]
        exempt, consolidatable = extract_exempt_messages(
            msgs, [], preserve_error_fix_pairs=False
        )
        assert len(exempt) == 0
        assert len(consolidatable) == 3

    def test_empty_nci_all_consolidatable(self):
        msgs = _make_messages(3)
        exempt, consolidatable = extract_exempt_messages(msgs, [])
        assert len(exempt) == 0
        assert len(consolidatable) == 3


# ---------------------------------------------------------------------------
# Tests: ConsolidationGate.should_consolidate
# ---------------------------------------------------------------------------


class TestShouldConsolidate:
    def setup_method(self):
        self.gate = ConsolidationGate()

    def test_warm_to_cold_no_summary(self):
        topic = _make_topic(state=TopicState.COLD, summary="")
        ctx = ConsolidationContext(
            trigger=ConsolidationTrigger.STATE_TRANSITION_WARM_TO_COLD,
            budget_pressure=PressureLevel.NORMAL,
            messages_since_last_consolidation=10,
        )
        decision = self.gate.should_consolidate(topic, ctx)
        assert decision.should_consolidate is True
        assert "COLD" in decision.reason

    def test_warm_to_cold_already_has_summary(self):
        topic = _make_topic(state=TopicState.COLD, summary="Existing summary")
        ctx = ConsolidationContext(
            trigger=ConsolidationTrigger.STATE_TRANSITION_WARM_TO_COLD,
            budget_pressure=PressureLevel.NORMAL,
            messages_since_last_consolidation=10,
        )
        decision = self.gate.should_consolidate(topic, ctx)
        assert decision.should_consolidate is False

    def test_budget_pressure_l1_triggers(self):
        topic = _make_topic()
        ctx = ConsolidationContext(
            trigger=ConsolidationTrigger.BUDGET_PRESSURE,
            budget_pressure=PressureLevel.L1,
            messages_since_last_consolidation=5,
        )
        decision = self.gate.should_consolidate(topic, ctx)
        assert decision.should_consolidate is True
        assert "l1" in decision.reason

    def test_budget_pressure_l3_triggers(self):
        topic = _make_topic()
        ctx = ConsolidationContext(
            trigger=ConsolidationTrigger.BUDGET_PRESSURE,
            budget_pressure=PressureLevel.L3,
            messages_since_last_consolidation=5,
        )
        decision = self.gate.should_consolidate(topic, ctx)
        assert decision.should_consolidate is True

    def test_budget_pressure_normal_no_trigger(self):
        topic = _make_topic()
        ctx = ConsolidationContext(
            trigger=ConsolidationTrigger.BUDGET_PRESSURE,
            budget_pressure=PressureLevel.NORMAL,
            messages_since_last_consolidation=5,
        )
        decision = self.gate.should_consolidate(topic, ctx)
        assert decision.should_consolidate is False

    def test_redundancy_always_triggers(self):
        topic = _make_topic()
        ctx = ConsolidationContext(
            trigger=ConsolidationTrigger.REDUNDANCY_DETECTED,
            budget_pressure=PressureLevel.NORMAL,
            messages_since_last_consolidation=10,
        )
        decision = self.gate.should_consolidate(topic, ctx)
        assert decision.should_consolidate is True

    def test_manual_always_triggers(self):
        topic = _make_topic()
        ctx = ConsolidationContext(
            trigger=ConsolidationTrigger.MANUAL_REQUEST,
            budget_pressure=PressureLevel.NORMAL,
            messages_since_last_consolidation=0,
        )
        decision = self.gate.should_consolidate(topic, ctx)
        assert decision.should_consolidate is True

    def test_exempt_items_included_in_decision(self):
        nci = [_make_nci(idx=0)]
        topic = _make_topic(never_consolidate=nci)
        ctx = ConsolidationContext(
            trigger=ConsolidationTrigger.MANUAL_REQUEST,
            budget_pressure=PressureLevel.NORMAL,
            messages_since_last_consolidation=5,
        )
        decision = self.gate.should_consolidate(topic, ctx)
        assert len(decision.exempt_items) == 1


# ---------------------------------------------------------------------------
# Tests: ConsolidationGate.consolidate
# ---------------------------------------------------------------------------


class TestConsolidate:
    def setup_method(self):
        self.gate = ConsolidationGate()

    def test_success_basic(self):
        topic = _make_topic()
        msgs = _make_messages(6)
        result = self.gate.consolidate(topic, msgs)
        assert result.success is True
        assert result.summary != ""
        assert result.tokens_before > 0
        assert result.compression_ratio >= 0

    def test_empty_messages_fails(self):
        topic = _make_topic()
        result = self.gate.consolidate(topic, [])
        assert result.success is False
        assert "No messages" in result.failure_reason

    def test_all_exempt_fails(self):
        nci = [_make_nci(idx=i) for i in range(3)]
        topic = _make_topic(never_consolidate=nci)
        msgs = [
            Message(idx=i, role="user", content=f"msg {i}", tokens=10) for i in range(3)
        ]
        result = self.gate.consolidate(topic, msgs)
        assert result.success is False
        assert "exempt" in result.failure_reason

    def test_quality_below_threshold_fails(self):
        """Inject a quality assessor that returns low score."""

        def bad_assessor(summary, msgs, decisions):
            return 0.3  # Below default 0.7

        gate = ConsolidationGate(quality_assessor=bad_assessor)
        topic = _make_topic()
        msgs = _make_messages(6)
        result = gate.consolidate(topic, msgs)
        assert result.success is False
        assert "Quality" in result.failure_reason
        assert result.quality_score == 0.3

    def test_failure_count_increments(self):
        def bad_assessor(summary, msgs, decisions):
            return 0.3

        gate = ConsolidationGate(quality_assessor=bad_assessor)
        topic = _make_topic(topic_id="fail_topic")
        msgs = _make_messages(6)

        gate.consolidate(topic, msgs)
        assert gate.get_failure_count("fail_topic") == 1

        gate.consolidate(topic, msgs)
        assert gate.get_failure_count("fail_topic") == 2

    def test_forced_accept_after_max_failures(self):
        """After max_consecutive_failures, force accept."""

        def bad_assessor(summary, msgs, decisions):
            return 0.2

        config = ConsolidationConfig(max_consecutive_failures=2)
        gate = ConsolidationGate(quality_assessor=bad_assessor, config=config)
        topic = _make_topic(topic_id="force_topic")
        msgs = _make_messages(6)

        # Fail twice
        gate.consolidate(topic, msgs)
        gate.consolidate(topic, msgs)
        assert gate.get_failure_count("force_topic") == 2

        # Third attempt: forced accept
        result = gate.consolidate(topic, msgs)
        assert result.success is True
        assert gate.get_failure_count("force_topic") == 0

    def test_custom_summarizer_used(self):
        def custom_summarizer(msgs, max_tokens, focus):
            return "CUSTOM SUMMARY"

        gate = ConsolidationGate(summarizer=custom_summarizer)
        topic = _make_topic()
        msgs = _make_messages(4)
        result = gate.consolidate(topic, msgs)
        assert "CUSTOM SUMMARY" in result.summary

    def test_key_decisions_extracted(self):
        topic = _make_topic()
        msgs = [
            Message(idx=0, role="user", content="我决定用Python", tokens=10),
            Message(idx=1, role="assistant", content="好的", tokens=5),
            Message(idx=2, role="user", content="hello", tokens=5),
            Message(idx=3, role="assistant", content="hi", tokens=5),
        ]
        result = self.gate.consolidate(topic, msgs)
        assert result.success is True
        assert len(result.key_decisions) >= 1

    def test_reset_failure_count(self):
        self.gate._failure_counts["topic_x"] = 5
        self.gate.reset_failure_count("topic_x")
        assert self.gate.get_failure_count("topic_x") == 0


# ---------------------------------------------------------------------------
# Tests: Default quality assessor edge cases
# ---------------------------------------------------------------------------


class TestDefaultQualityAssessor:
    def test_empty_summary_returns_zero(self):
        score = ConsolidationGate._default_quality_assessor("", _make_messages(3), [])
        assert score == 0.0

    def test_empty_messages_returns_zero(self):
        score = ConsolidationGate._default_quality_assessor("some summary", [], [])
        assert score == 0.0

    def test_reasonable_compression_high_score(self):
        msgs = [
            Message(idx=i, role="user", content="x" * 100, tokens=25) for i in range(10)
        ]
        # Summary is ~15% of original → should score well
        summary = "x" * 150
        score = ConsolidationGate._default_quality_assessor(summary, msgs, [])
        assert score >= 0.5


# ---------------------------------------------------------------------------
# Tests: Default summarizer edge cases
# ---------------------------------------------------------------------------


class TestDefaultSummarizer:
    def test_empty_messages(self):
        result = ConsolidationGate._default_summarizer([], 200, "outcomes")
        assert result == ""

    def test_respects_token_budget(self):
        msgs = [
            Message(idx=i, role="user", content="a" * 500, tokens=125)
            for i in range(20)
        ]
        result = ConsolidationGate._default_summarizer(msgs, 50, "outcomes")
        # 50 tokens * 4 chars = 200 char budget — should be constrained
        assert len(result) < 2000  # Rough upper bound
