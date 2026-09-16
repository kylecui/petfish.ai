"""Legacy v0.9 layout migration, exercised against install.py (the sole installer).

Replaces tests/test_migration_e2e.py, which targeted the four shell installers
(install.sh / install.ps1 / remote-install.sh / remote-install.ps1) deleted in
v3.0. Because those files no longer exist, every case in that script was skipped
and the suite passed vacuously.
"""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]

_spec = importlib.util.spec_from_file_location("install_ref", REPO_ROOT / "install.py")
assert _spec is not None and _spec.loader is not None
_install = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_install)


@pytest.fixture()
def v09_project(tmp_path, monkeypatch):
    """Simulated v0.9 project, with HOME redirected so the real one is never touched.

    migrate_legacy_v0_9() inspects both the target and Path.home(); isolating HOME
    keeps the test from mutating a developer's real registry.
    """
    monkeypatch.setattr(Path, "home", staticmethod(lambda: tmp_path / "home"))
    (tmp_path / "home").mkdir()

    opencode = tmp_path / ".opencode"
    (opencode / "skills").mkdir(parents=True)
    (opencode / "agents-rules").mkdir(parents=True)

    legacy_pack = next(iter(_install.PACK_RENAMES))
    (opencode / "installed-packs.json").write_text(
        json.dumps({"packs": [legacy_pack, "companion"]}), encoding="utf-8"
    )
    (opencode / "opencode.json").write_text('{"plugin": []}\n', encoding="utf-8")

    legacy_skill = next(iter(_install.SKILL_RENAMES))
    (opencode / "skills" / legacy_skill).mkdir()
    (opencode / "skills" / legacy_skill / "SKILL.md").write_text("# x\n", encoding="utf-8")

    legacy_rule = next(iter(_install.RULES_RENAMES))
    (opencode / "agents-rules" / legacy_rule).write_text("# x\n", encoding="utf-8")

    _install.migrate_legacy_v0_9(
        tmp_path, ".opencode/skills", ".opencode/opencode.json", ".opencode/agents-rules"
    )
    return opencode


def test_array_registry_converted_and_pack_renamed(v09_project):
    legacy_pack = next(iter(_install.PACK_RENAMES))
    new_pack = _install.PACK_RENAMES[legacy_pack]
    data = json.loads((v09_project / "installed-packs.json").read_text(encoding="utf-8"))
    packs = data["packs"]
    assert isinstance(packs, dict), "v0.9 array registry must be converted to the v2 dict form"
    assert new_pack in packs
    assert legacy_pack not in packs


def test_skill_dir_renamed(v09_project):
    legacy_skill = next(iter(_install.SKILL_RENAMES))
    new_skill = _install.SKILL_RENAMES[legacy_skill]
    assert (v09_project / "skills" / new_skill).is_dir()
    assert not (v09_project / "skills" / legacy_skill).exists()


def test_rules_file_renamed(v09_project):
    legacy_rule = next(iter(_install.RULES_RENAMES))
    new_rule = _install.RULES_RENAMES[legacy_rule]
    assert (v09_project / "agents-rules" / new_rule).is_file()
    assert not (v09_project / "agents-rules" / legacy_rule).exists()
