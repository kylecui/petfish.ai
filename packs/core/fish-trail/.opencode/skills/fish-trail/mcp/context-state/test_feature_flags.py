"""Tests for feature_flags module."""

import json
import os
import tempfile
from pathlib import Path

import pytest

from feature_flags import FeatureFlags, load_feature_flags, _to_bool


# =============================================================================
# _to_bool tests
# =============================================================================


class TestToBool:
    """Test the _to_bool helper."""

    @pytest.mark.parametrize(
        "value,expected",
        [
            (True, True),
            (False, False),
            ("true", True),
            ("True", True),
            ("TRUE", True),
            ("1", True),
            ("yes", True),
            ("on", True),
            ("false", False),
            ("False", False),
            ("0", False),
            ("no", False),
            ("off", False),
            ("", False),
            ("random", False),
            (1, True),
            (0, False),
        ],
    )
    def test_conversion(self, value, expected):
        assert _to_bool(value) is expected


# =============================================================================
# FeatureFlags dataclass tests
# =============================================================================


class TestFeatureFlagsDefaults:
    """Test default values."""

    def test_defaults(self):
        flags = FeatureFlags()
        assert flags.v2_enabled is True
        assert flags.enable_continuous_detection is False
        assert flags.enable_tiered_retention is True
        assert flags.enable_budget_allocation is True
        assert flags.enable_never_consolidate is False
        assert flags.enable_auto_state_transitions is False
        assert flags.enable_pressure_degradation is False
        assert flags.v1_fallback_on_error is True

    def test_defaults_all_computed_false(self):
        """With all v2 features explicitly disabled, computed properties are False."""
        flags = FeatureFlags(v2_enabled=False)
        assert flags.registry_enabled is False
        assert flags.pressure_monitor_enabled is False
        assert flags.budget_allocator_enabled is False
        assert flags.eviction_enabled is False
        assert flags.memory_context_enabled is False


class TestComputedProperties:
    """Test computed property logic."""

    def test_registry_enabled_continuous_detection(self):
        flags = FeatureFlags(enable_continuous_detection=True)
        assert flags.registry_enabled is True
        assert flags.memory_context_enabled is True

    def test_registry_enabled_tiered_retention(self):
        flags = FeatureFlags(enable_tiered_retention=True)
        assert flags.registry_enabled is True

    def test_registry_enabled_auto_state_transitions(self):
        flags = FeatureFlags(enable_auto_state_transitions=True)
        assert flags.registry_enabled is True
        assert flags.eviction_enabled is True

    def test_pressure_monitor_enabled_budget(self):
        flags = FeatureFlags(enable_budget_allocation=True)
        assert flags.pressure_monitor_enabled is True
        assert flags.budget_allocator_enabled is True
        assert flags.memory_context_enabled is True

    def test_pressure_monitor_enabled_degradation(self):
        flags = FeatureFlags(enable_pressure_degradation=True, enable_budget_allocation=False)
        assert flags.pressure_monitor_enabled is True
        assert flags.budget_allocator_enabled is False

    def test_master_switch_disables_all(self):
        """v2_enabled=False disables all computed properties."""
        flags = FeatureFlags(
            v2_enabled=False,
            enable_continuous_detection=True,
            enable_budget_allocation=True,
            enable_auto_state_transitions=True,
            enable_pressure_degradation=True,
        )
        assert flags.registry_enabled is False
        assert flags.pressure_monitor_enabled is False
        assert flags.budget_allocator_enabled is False
        assert flags.eviction_enabled is False
        assert flags.memory_context_enabled is False

    def test_memory_context_needs_registry_or_pressure(self):
        """memory_context_enabled requires at least one subsystem."""
        flags = FeatureFlags(enable_tiered_retention=False, enable_budget_allocation=False, enable_never_consolidate=True)
        assert flags.registry_enabled is False
        assert flags.pressure_monitor_enabled is False
        assert flags.memory_context_enabled is False


class TestToDict:
    """Test to_dict serialization."""

    def test_includes_all_fields(self):
        flags = FeatureFlags()
        d = flags.to_dict()
        assert "v2_enabled" in d
        assert "enable_continuous_detection" in d
        assert "v1_fallback_on_error" in d

    def test_includes_computed_properties(self):
        flags = FeatureFlags(enable_budget_allocation=True, enable_tiered_retention=False)
        d = flags.to_dict()
        assert d["_pressure_monitor_enabled"] is True
        assert d["_registry_enabled"] is False
        assert d["_memory_context_enabled"] is True


# =============================================================================
# load_feature_flags tests
# =============================================================================


class TestLoadFeatureFlagsDefaults:
    """Test loading with no config and no env vars."""

    def test_no_args_returns_defaults(self, clean_env):
        flags = load_feature_flags()
        assert flags.v2_enabled is True
        assert flags.enable_continuous_detection is False

    def test_nonexistent_base_dir(self, clean_env):
        flags = load_feature_flags(base_dir="/nonexistent/path/xyz")
        assert flags.v2_enabled is True


class TestLoadFromConfigData:
    """Test loading from pre-loaded config dict."""

    def test_config_data_sets_flags(self, clean_env):
        config = {"feature_flags": {"enable_continuous_detection": True}}
        flags = load_feature_flags(config_data=config)
        assert flags.enable_continuous_detection is True

    def test_config_data_ignores_unknown_keys(self, clean_env):
        config = {
            "feature_flags": {"unknown_flag": True, "enable_budget_allocation": True}
        }
        flags = load_feature_flags(config_data=config)
        assert flags.enable_budget_allocation is True

    def test_config_data_string_booleans(self, clean_env):
        config = {
            "feature_flags": {
                "enable_tiered_retention": "true",
                "v1_fallback_on_error": "false",
            }
        }
        flags = load_feature_flags(config_data=config)
        assert flags.enable_tiered_retention is True
        assert flags.v1_fallback_on_error is False

    def test_empty_feature_flags_section(self, clean_env):
        config = {"feature_flags": {}}
        flags = load_feature_flags(config_data=config)
        assert flags == FeatureFlags()

    def test_missing_feature_flags_section(self, clean_env):
        config = {"other_section": {"key": "value"}}
        flags = load_feature_flags(config_data=config)
        assert flags == FeatureFlags()


class TestLoadFromFile:
    """Test loading from config.json on disk."""

    def test_reads_config_json(self, clean_env, tmp_path):
        config = {"feature_flags": {"enable_pressure_degradation": True}}
        (tmp_path / "config.json").write_text(json.dumps(config), encoding="utf-8")
        flags = load_feature_flags(base_dir=str(tmp_path))
        assert flags.enable_pressure_degradation is True

    def test_malformed_json_graceful(self, clean_env, tmp_path):
        (tmp_path / "config.json").write_text("not json {{{", encoding="utf-8")
        flags = load_feature_flags(base_dir=str(tmp_path))
        assert flags == FeatureFlags()

    def test_config_data_takes_precedence_over_base_dir(self, clean_env, tmp_path):
        """config_data param means base_dir is ignored."""
        file_config = {"feature_flags": {"enable_continuous_detection": True}}
        (tmp_path / "config.json").write_text(json.dumps(file_config), encoding="utf-8")

        override_config = {"feature_flags": {"enable_continuous_detection": False}}
        flags = load_feature_flags(base_dir=str(tmp_path), config_data=override_config)
        assert flags.enable_continuous_detection is False


class TestLoadEnvOverrides:
    """Test environment variable overrides."""

    def test_global_kill_switch(self, clean_env):
        os.environ["FISH_TRAIL_V2_ENABLED"] = "false"
        flags = load_feature_flags()
        assert flags.v2_enabled is False

    def test_per_flag_env_override(self, clean_env):
        os.environ["FISH_TRAIL_FLAG_ENABLE_BUDGET_ALLOCATION"] = "true"
        flags = load_feature_flags()
        assert flags.enable_budget_allocation is True

    def test_env_overrides_config(self, clean_env):
        """Env vars beat config.json."""
        config = {"feature_flags": {"enable_continuous_detection": True}}
        os.environ["FISH_TRAIL_FLAG_ENABLE_CONTINUOUS_DETECTION"] = "false"
        flags = load_feature_flags(config_data=config)
        assert flags.enable_continuous_detection is False

    def test_global_kill_switch_overrides_per_flag(self, clean_env):
        """FISH_TRAIL_V2_ENABLED sets v2_enabled, per-flag env for v2_enabled also works."""
        os.environ["FISH_TRAIL_V2_ENABLED"] = "false"
        os.environ["FISH_TRAIL_FLAG_V2_ENABLED"] = "true"
        # Per-flag env runs AFTER global, so it wins
        flags = load_feature_flags()
        assert flags.v2_enabled is True

    def test_multiple_env_overrides(self, clean_env):
        os.environ["FISH_TRAIL_FLAG_ENABLE_TIERED_RETENTION"] = "true"
        os.environ["FISH_TRAIL_FLAG_ENABLE_PRESSURE_DEGRADATION"] = "true"
        os.environ["FISH_TRAIL_FLAG_V1_FALLBACK_ON_ERROR"] = "false"
        flags = load_feature_flags()
        assert flags.enable_tiered_retention is True
        assert flags.enable_pressure_degradation is True
        assert flags.v1_fallback_on_error is False


class TestLoadPriority:
    """Test the 3-tier priority: env > config > defaults."""

    def test_full_priority_chain(self, clean_env, tmp_path):
        # Default: enable_continuous_detection=False
        # Config sets it True
        config = {
            "feature_flags": {
                "enable_continuous_detection": True,
                "enable_budget_allocation": True,
            }
        }
        (tmp_path / "config.json").write_text(json.dumps(config), encoding="utf-8")
        # Env overrides continuous_detection back to False
        os.environ["FISH_TRAIL_FLAG_ENABLE_CONTINUOUS_DETECTION"] = "false"

        flags = load_feature_flags(base_dir=str(tmp_path))
        # Env wins over config
        assert flags.enable_continuous_detection is False
        # Config wins over default
        assert flags.enable_budget_allocation is True
        # Default stays (tiered_retention defaults to True in v1.1.0+)
        assert flags.enable_tiered_retention is True


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def clean_env(monkeypatch):
    """Remove all FISH_TRAIL env vars for test isolation."""
    for key in list(os.environ.keys()):
        if key.startswith("FISH_TRAIL_"):
            monkeypatch.delenv(key)
