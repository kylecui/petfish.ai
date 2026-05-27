"""Feature Flags for Fish-Trail Tiered Memory v2.

Provides per-component feature flags that control gradual rollout of v2
capabilities. Flags are loaded from config.json and can be overridden via
environment variables.

Config file location: {base_dir}/config.json under the "feature_flags" key.

Environment variable overrides follow the pattern:
    FISH_TRAIL_FLAG_{UPPER_SNAKE_NAME}=true|false
    e.g. FISH_TRAIL_FLAG_ENABLE_TIERED_RETENTION=false

The global kill-switch is:
    FISH_TRAIL_V2_ENABLED=false  (disables ALL v2 features)
"""

import json
import os
from dataclasses import dataclass, field, fields
from typing import Any, Dict, Optional


@dataclass
class FeatureFlags:
    """Per-component feature flags for tiered memory v2.

    All flags default to False (safe rollout — opt-in per component).
    The `v2_enabled` master switch must be True for any flag to take effect.
    """

    # Master switch — if False, ALL v2 features are disabled regardless of
    # individual flag values.
    v2_enabled: bool = True

    # --- Per-feature flags (spec §5.4) ---

    # Phase 1: Continuous topic detection (observe detection quality)
    enable_continuous_detection: bool = False

    # Phase 2: Tiered retention engine (hot/warm/cold/archive states)
    # Default True when v2_enabled — this is the headline v1.1.0 feature.
    enable_tiered_retention: bool = True

    # Phase 2: Budget allocation across topics
    # Default True when v2_enabled — required by get_memory_context.
    enable_budget_allocation: bool = True

    # Phase 3: Never-consolidate items preserved across compactions
    enable_never_consolidate: bool = False

    # Phase 3: Automatic state transitions based on access patterns
    enable_auto_state_transitions: bool = False

    # Phase 4: Pressure-based degradation (aggressive eviction under pressure)
    enable_pressure_degradation: bool = False

    # Safety: Fall back to v1 behavior on any v2 error
    v1_fallback_on_error: bool = True

    # --- Per-component convenience ---

    @property
    def registry_enabled(self) -> bool:
        """Whether TopicRegistryV2 should be active."""
        return self.v2_enabled and (
            self.enable_continuous_detection
            or self.enable_tiered_retention
            or self.enable_auto_state_transitions
        )

    @property
    def pressure_monitor_enabled(self) -> bool:
        """Whether MemoryPressureMonitor should be active."""
        return self.v2_enabled and (
            self.enable_budget_allocation or self.enable_pressure_degradation
        )

    @property
    def budget_allocator_enabled(self) -> bool:
        """Whether budget allocation logic runs."""
        return self.v2_enabled and self.enable_budget_allocation

    @property
    def eviction_enabled(self) -> bool:
        """Whether automatic eviction/state-transitions run."""
        return self.v2_enabled and self.enable_auto_state_transitions

    @property
    def memory_context_enabled(self) -> bool:
        """Whether get_memory_context tool should be registered."""
        return self.v2_enabled and (
            self.registry_enabled or self.pressure_monitor_enabled
        )

    def to_dict(self) -> Dict[str, Any]:
        """Serialize all flags to dict (for diagnostics/logging)."""
        result = {}
        for f in fields(self):
            result[f.name] = getattr(self, f.name)
        # Include computed properties
        result["_registry_enabled"] = self.registry_enabled
        result["_pressure_monitor_enabled"] = self.pressure_monitor_enabled
        result["_budget_allocator_enabled"] = self.budget_allocator_enabled
        result["_eviction_enabled"] = self.eviction_enabled
        result["_memory_context_enabled"] = self.memory_context_enabled
        return result


_ENV_PREFIX = "FISH_TRAIL_FLAG_"
_GLOBAL_KILL_SWITCH = "FISH_TRAIL_V2_ENABLED"


def load_feature_flags(
    base_dir: Optional[str] = None,
    config_data: Optional[Dict[str, Any]] = None,
) -> FeatureFlags:
    """Load feature flags from config.json and environment overrides.

    Priority (highest to lowest):
    1. Environment variables (FISH_TRAIL_FLAG_* and FISH_TRAIL_V2_ENABLED)
    2. config.json "feature_flags" section
    3. Dataclass defaults (all False except v1_fallback_on_error)

    Args:
        base_dir: Directory containing config.json. If None, uses defaults only.
        config_data: Pre-loaded config dict. If provided, base_dir is ignored.

    Returns:
        FeatureFlags instance with resolved values.
    """
    # Step 1: Load config.json if available
    file_flags: Dict[str, Any] = {}
    if config_data is not None:
        file_flags = config_data.get("feature_flags", {})
    elif base_dir is not None:
        config_path = os.path.join(base_dir, "config.json")
        if os.path.exists(config_path):
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                file_flags = data.get("feature_flags", {})
            except (OSError, ValueError, json.JSONDecodeError):
                pass  # Graceful degradation — use defaults

    # Step 2: Build kwargs from file config (only known fields)
    known_fields = {f.name for f in fields(FeatureFlags)}
    kwargs: Dict[str, Any] = {}
    for key, value in file_flags.items():
        if key in known_fields:
            kwargs[key] = _to_bool(value)

    # Step 3: Apply environment variable overrides
    # Global kill switch
    global_env = os.environ.get(_GLOBAL_KILL_SWITCH)
    if global_env is not None:
        kwargs["v2_enabled"] = _to_bool(global_env)

    # Per-flag overrides
    for f in fields(FeatureFlags):
        env_key = _ENV_PREFIX + f.name.upper()
        env_val = os.environ.get(env_key)
        if env_val is not None:
            kwargs[f.name] = _to_bool(env_val)

    return FeatureFlags(**kwargs)


def _to_bool(value: Any) -> bool:
    """Convert various truthy/falsy representations to bool."""
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.lower() in ("true", "1", "yes", "on")
    return bool(value)
