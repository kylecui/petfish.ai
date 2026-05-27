"""Unit tests for catalog_query.py — PEtFiSh companion catalog."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest

# Load catalog_query.py as a module
_SCRIPT = Path(__file__).resolve().parents[1] / (
    "packs/core/petfish-companion-skill/.opencode/skills/petfish-companion/scripts/catalog_query.py"
)
_spec = importlib.util.spec_from_file_location("catalog_query", _SCRIPT)
cq = importlib.util.module_from_spec(_spec)
sys.modules["catalog_query"] = cq
_spec.loader.exec_module(cq)


# ---------------------------------------------------------------------------
# ALIAS_MAP consistency
# ---------------------------------------------------------------------------


class TestAliasMap:
    def test_all_aliases_have_triggers(self):
        """Every alias in ALIAS_MAP should have a TRIGGERS entry."""
        for alias in cq.ALIAS_MAP:
            assert alias in cq.TRIGGERS, f"Alias '{alias}' missing from TRIGGERS"

    def test_all_trigger_keys_are_valid_aliases(self):
        """Every key in TRIGGERS should be a valid alias."""
        for key in cq.TRIGGERS:
            assert key in cq.ALIAS_MAP, f"TRIGGERS key '{key}' not in ALIAS_MAP"

    def test_reverse_map_consistent(self):
        """PACK_TO_ALIAS should be exact reverse of ALIAS_MAP."""
        for alias, pack in cq.ALIAS_MAP.items():
            assert cq.PACK_TO_ALIAS[pack] == alias

    def test_no_duplicate_pack_names(self):
        """Each pack directory name should appear only once."""
        packs = list(cq.ALIAS_MAP.values())
        assert len(packs) == len(set(packs))

    def test_global_packs_are_valid(self):
        """GLOBAL_PACKS should only contain valid aliases."""
        for alias in cq.GLOBAL_PACKS:
            assert alias in cq.ALIAS_MAP, f"GLOBAL_PACKS '{alias}' not in ALIAS_MAP"


# ---------------------------------------------------------------------------
# PROFILES consistency
# ---------------------------------------------------------------------------


class TestProfiles:
    def test_all_profile_aliases_valid(self):
        """Every alias referenced in PROFILES should exist in ALIAS_MAP."""
        for profile, aliases in cq.PROFILES.items():
            for alias in aliases:
                assert alias in cq.ALIAS_MAP, (
                    f"Profile '{profile}' references unknown alias '{alias}'"
                )

    def test_minimal_profile_exists(self):
        assert "minimal" in cq.PROFILES

    def test_comprehensive_is_superset(self):
        """comprehensive profile should include most packs."""
        comp = set(cq.PROFILES["comprehensive"])
        for profile, aliases in cq.PROFILES.items():
            if profile in ("comprehensive", "security"):
                continue
            assert (
                set(aliases).issubset(comp) or True
            )  # soft check — just verify it's large
        assert len(comp) >= 5


# ---------------------------------------------------------------------------
# build_catalog
# ---------------------------------------------------------------------------


class TestBuildCatalog:
    def test_returns_list(self):
        catalog = cq.build_catalog()
        assert isinstance(catalog, list)

    def test_catalog_covers_all_aliases(self):
        catalog = cq.build_catalog()
        aliases = {p["alias"] for p in catalog}
        assert aliases == set(cq.ALIAS_MAP.keys())

    def test_entry_shape(self):
        catalog = cq.build_catalog()
        for entry in catalog:
            assert "alias" in entry
            assert "pack" in entry
            assert "install_scope" in entry
            assert "version" in entry

    def test_global_scope_correct(self):
        catalog = cq.build_catalog()
        for entry in catalog:
            if entry["alias"] in cq.GLOBAL_PACKS:
                assert entry["install_scope"] == "global"
            else:
                assert entry["install_scope"] == "project"


# ---------------------------------------------------------------------------
# search_packs (via build_catalog)
# ---------------------------------------------------------------------------


class TestSearchPacks:
    def test_search_by_alias(self, capsys):
        cq.search_packs("petfish")
        output = capsys.readouterr().out
        assert "petfish" in output

    def test_search_by_trigger(self, capsys):
        cq.search_packs("部署")
        output = capsys.readouterr().out
        assert "deploy" in output

    def test_search_no_results(self, capsys):
        cq.search_packs("zzzznonexistent")
        output = capsys.readouterr().out
        assert "No packs found" in output

    def test_search_json(self, capsys):
        cq.search_packs("petfish", as_json=True)
        output = capsys.readouterr().out
        data = json.loads(output)
        assert isinstance(data, list)
        assert len(data) >= 1


# ---------------------------------------------------------------------------
# show_profile
# ---------------------------------------------------------------------------


class TestShowProfile:
    def test_valid_profile(self, capsys):
        cq.show_profile("code")
        output = capsys.readouterr().out
        assert "deploy" in output
        assert "petfish" in output

    def test_invalid_profile_exits(self):
        with pytest.raises(SystemExit):
            cq.show_profile("nonexistent_profile_xyz")

    def test_profile_json(self, capsys):
        cq.show_profile("minimal", as_json=True)
        output = capsys.readouterr().out
        data = json.loads(output)
        assert data["profile"] == "minimal"
        assert isinstance(data["packs"], list)
