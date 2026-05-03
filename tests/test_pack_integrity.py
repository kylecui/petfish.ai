"""Pack integrity validation — manifest schema, contents, alias uniqueness."""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
PACKS_DIR = REPO_ROOT / "packs"


def _discover_manifests() -> list[Path]:
    return sorted(PACKS_DIR.glob("*/pack-manifest.json"))


MANIFESTS = _discover_manifests()


@pytest.fixture(params=MANIFESTS, ids=[m.parent.name for m in MANIFESTS])
def manifest_path(request) -> Path:
    return request.param


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


# ---------------------------------------------------------------------------
# JSON validity
# ---------------------------------------------------------------------------


class TestManifestJson:
    def test_valid_json(self, manifest_path):
        data = _load(manifest_path)
        assert isinstance(data, dict)


# ---------------------------------------------------------------------------
# Required fields
# ---------------------------------------------------------------------------


class TestManifestSchema:
    def test_has_name(self, manifest_path):
        data = _load(manifest_path)
        assert "name" in data, f"{manifest_path.parent.name}: missing 'name'"

    def test_has_version(self, manifest_path):
        data = _load(manifest_path)
        assert "version" in data, f"{manifest_path.parent.name}: missing 'version'"

    def test_version_format(self, manifest_path):
        data = _load(manifest_path)
        version = data.get("version", "")
        assert re.match(r"^\d+\.\d+\.\d+$", version), (
            f"{manifest_path.parent.name}: version '{version}' not semver"
        )

    def test_has_description(self, manifest_path):
        data = _load(manifest_path)
        assert "description" in data and data["description"], (
            f"{manifest_path.parent.name}: missing or empty 'description'"
        )

    def test_has_contents_or_skills(self, manifest_path):
        """Pack should have either 'contents' or 'skills' listing."""
        data = _load(manifest_path)
        has_contents = "contents" in data
        has_skills = "skills" in data
        assert has_contents or has_skills, (
            f"{manifest_path.parent.name}: missing both 'contents' and 'skills'"
        )


# ---------------------------------------------------------------------------
# Contents file existence
# ---------------------------------------------------------------------------


class TestContentsExist:
    def test_all_contents_files_exist(self, manifest_path):
        data = _load(manifest_path)
        pack_dir = manifest_path.parent
        contents = data.get("contents", [])
        missing = []
        for item in contents:
            # contents can be strings (file paths) or dicts with "path" key
            path_str = (
                item if isinstance(item, str) else item.get("path", item.get("src", ""))
            )
            if not path_str:
                continue
            full = pack_dir / path_str
            if not full.exists():
                missing.append(path_str)
        assert not missing, (
            f"{manifest_path.parent.name}: missing content files: {missing}"
        )


# ---------------------------------------------------------------------------
# Cross-pack alias uniqueness
# ---------------------------------------------------------------------------


class TestAliasUniqueness:
    def test_no_duplicate_pack_directory_names(self):
        """Each pack directory should be unique (enforced by filesystem, but verify manifests)."""
        names = [m.parent.name for m in MANIFESTS]
        assert len(names) == len(set(names))

    def test_manifest_names_unique(self):
        """The 'name' field in each manifest should be unique."""
        names = []
        for m in MANIFESTS:
            data = _load(m)
            names.append(data.get("name", m.parent.name))
        dupes = [n for n in names if names.count(n) > 1]
        assert not dupes, f"Duplicate manifest names: {set(dupes)}"
