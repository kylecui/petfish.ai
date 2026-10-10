"""Pack plugin channel (#289) — install, register, dedup, uninstall reversal.

Covers the pack-manifest `plugins` array end to end at the unit level:
payload copy, opencode.json registration (idempotent, legacy-tuple-aware),
registry recording, and removal.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

import install as inst


@pytest.fixture
def fake_pack(tmp_path: Path) -> "tuple[Path, dict]":
    """A minimal pack payload with two plugin files."""
    pack = tmp_path / "pack"
    plugin_dir = pack / ".opencode" / "plugin"
    plugin_dir.mkdir(parents=True)
    (plugin_dir / "alpha.ts").write_text("// alpha\n", encoding="utf-8")
    (plugin_dir / "beta.ts").write_text("// beta\n", encoding="utf-8")
    manifest = {
        "name": "fake-pack",
        "version": "1.0.0",
        "description": "test pack",
        "plugins": [
            ".opencode/plugin/alpha.ts",
            {
                "source": ".opencode/plugin/beta.ts",
                "target": ".opencode/plugin/beta.ts",
                "options": {"enabled": True},
            },
        ],
        "plugin_count": 2,
    }
    return pack, manifest


@pytest.fixture
def workspace(tmp_path: Path) -> "tuple[Path, Path, dict]":
    """A fake install workspace: target dir + opencode.json + plat_dirs."""
    target = tmp_path / "ws"
    target.mkdir()
    config_file = target / "opencode.json"
    config_file.write_text('{\n  "plugin": []\n}\n', encoding="utf-8")
    plat_dirs = {"config_file": str(config_file)}
    return target, config_file, plat_dirs


class TestInstallPackPlugins:
    def test_copies_files_and_registers(self, fake_pack, workspace):
        pack, manifest = fake_pack
        target, config_file, plat_dirs = workspace

        installed = inst.install_pack_plugins(pack, target, plat_dirs, True, manifest)

        assert installed == [
            ".opencode/plugin/alpha.ts",
            ".opencode/plugin/beta.ts",
        ]
        assert (target / ".opencode" / "plugin" / "alpha.ts").is_file()
        assert (target / ".opencode" / "plugin" / "beta.ts").is_file()

        data = json.loads(config_file.read_text(encoding="utf-8"))
        assert ".opencode/plugin/alpha.ts" in data["plugin"]
        beta_tuple = next(
            e for e in data["plugin"] if isinstance(e, list) and e[0] == ".opencode/plugin/beta.ts"
        )
        assert beta_tuple[1] == {"enabled": True}

    def test_empty_manifest_plugins_is_noop(self, fake_pack, workspace):
        pack, manifest = fake_pack
        manifest["plugins"] = []
        target, config_file, plat_dirs = workspace

        assert inst.install_pack_plugins(pack, target, plat_dirs, True, manifest) == []
        data = json.loads(config_file.read_text(encoding="utf-8"))
        assert data["plugin"] == []

    def test_missing_source_skipped_gracefully(self, fake_pack, workspace):
        pack, manifest = fake_pack
        manifest["plugins"] = [
            ".opencode/plugin/ghost.ts",
            ".opencode/plugin/alpha.ts",
        ]
        target, config_file, plat_dirs = workspace

        installed = inst.install_pack_plugins(pack, target, plat_dirs, True, manifest)

        assert installed == [".opencode/plugin/alpha.ts"]

    def test_reinstall_does_not_duplicate_registration(self, fake_pack, workspace):
        pack, manifest = fake_pack
        target, config_file, plat_dirs = workspace

        inst.install_pack_plugins(pack, target, plat_dirs, True, manifest)
        inst.install_pack_plugins(pack, target, plat_dirs, True, manifest)

        data = json.loads(config_file.read_text(encoding="utf-8"))
        paths = [
            e[0] if isinstance(e, list) else e for e in data["plugin"]
        ]
        assert len(paths) == len(set(paths))

    def test_legacy_tuple_wins_over_plain_string(self, fake_pack, workspace):
        pack, manifest = fake_pack
        target, config_file, plat_dirs = workspace
        # Pre-seed a legacy [path, options] registration for alpha
        config_file.write_text(
            json.dumps(
                {
                    "plugin": [
                        [".opencode/plugin/alpha.ts", {"mode": "all"}],
                    ]
                }
            ),
            encoding="utf-8",
        )

        inst.install_pack_plugins(pack, target, plat_dirs, True, manifest)

        data = json.loads(config_file.read_text(encoding="utf-8"))
        alpha_entries = [
            e for e in data["plugin"]
            if e == ".opencode/plugin/alpha.ts"
            or (isinstance(e, list) and e[0] == ".opencode/plugin/alpha.ts")
        ]
        assert alpha_entries == [[".opencode/plugin/alpha.ts", {"mode": "all"}]]


class TestRemovePluginsFromConfig:
    def test_removes_matching_keeps_others(self, fake_pack, workspace):
        pack, manifest = fake_pack
        target, config_file, plat_dirs = workspace
        inst.install_pack_plugins(pack, target, plat_dirs, True, manifest)
        # An unrelated registration that must survive removal
        inst.register_plugins_in_config(
            config_file, [".opencode/plugin/unrelated.ts"]
        )

        inst.remove_plugins_from_config(
            config_file,
            [".opencode/plugin/alpha.ts", ".opencode/plugin/beta.ts"],
        )

        data = json.loads(config_file.read_text(encoding="utf-8"))
        assert data["plugin"] == [".opencode/plugin/unrelated.ts"]

    def test_noop_when_config_missing(self, tmp_path):
        inst.remove_plugins_from_config(tmp_path / "absent.json", ["x.ts"])


class TestRegistryRecordsPlugins:
    def test_update_registry_writes_plugins_and_count(self, fake_pack):
        _pack, manifest = fake_pack
        registry = {"packs": {}, "version": "2.0"}

        inst.update_registry(
            registry,
            "fake-pack",
            manifest,
            ["some-skill"],
            [],
            [],
            installed_plugins=[".opencode/plugin/alpha.ts", ".opencode/plugin/beta.ts"],
        )

        entry = registry["packs"]["fake-pack"]
        assert entry["plugins"] == [
            ".opencode/plugin/alpha.ts",
            ".opencode/plugin/beta.ts",
        ]
        assert entry["plugin_count"] == 2

    def test_update_registry_defaults_to_empty(self, fake_pack):
        _pack, manifest = fake_pack
        manifest = {k: v for k, v in manifest.items() if k != "plugin_count"}
        registry = {"packs": {}, "version": "2.0"}

        inst.update_registry(registry, "fake-pack", manifest, [], [], [])

        entry = registry["packs"]["fake-pack"]
        assert entry["plugins"] == []
        assert entry["plugin_count"] == 0

    def test_update_registry_manifest_count_wins(self, fake_pack):
        """plugin_count follows the skill_count convention: manifest value wins."""
        _pack, manifest = fake_pack
        registry = {"packs": {}, "version": "2.0"}

        inst.update_registry(registry, "fake-pack", manifest, [], [], [])

        assert registry["packs"]["fake-pack"]["plugin_count"] == manifest["plugin_count"]
