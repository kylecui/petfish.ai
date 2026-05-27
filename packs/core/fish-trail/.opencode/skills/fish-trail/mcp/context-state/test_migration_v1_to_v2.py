"""Tests for V1 → V2 Topic Registry Migration.

Covers:
- Version detection (v1, v2, missing, unknown)
- Migration state detection
- Full migration from v1 to v2 format
- Idempotent on already-v2 registry
- Backup creation
- Migration marker writing
- Individual topic file loading
- Server-level auto-migration on _load_registry
- Server fallback on error (v1_fallback_on_error flag)
"""

import json
import os
import tempfile
from pathlib import Path

import pytest

from migration_v1_to_v2 import (
    MigrationError,
    MigrationState,
    detect_migration_state,
    detect_registry_version,
    get_migration_info,
    migrate_registry,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def base_dir(tmp_path: Path) -> Path:
    """Create a minimal fish-trail base directory."""
    bd = tmp_path / ".petfish" / "fish-trail"
    bd.mkdir(parents=True)
    (bd / "topics").mkdir()
    (bd / "sessions").mkdir()
    return bd


def _write_v1_registry(
    base_dir: Path, topics: dict, active_topic: str | None = None
) -> None:
    """Write a v1 format registry."""
    registry = {
        "version": 1,
        "topics": topics,
        "active_topic": active_topic,
        "links": [],
    }
    with open(base_dir / "topic-registry.json", "w", encoding="utf-8") as f:
        json.dump(registry, f)


def _write_v1_topic_file(base_dir: Path, topic_id: str, data: dict) -> None:
    """Write a v1 individual topic file."""
    topic_path = base_dir / "topics" / f"{topic_id}.json"
    with open(topic_path, "w", encoding="utf-8") as f:
        json.dump(data, f)


def _write_v2_registry(base_dir: Path, topics: dict | None = None) -> None:
    """Write a v2 format registry."""
    registry = {
        "version": "2.0",
        "topics": topics or {},
        "session_id": None,
        "last_compaction_id": None,
        "compaction_count": 0,
        "created_at": "2025-01-01T00:00:00+00:00",
        "updated_at": "2025-01-01T00:00:00+00:00",
        "config_hash": "",
    }
    with open(base_dir / "topic-registry.json", "w", encoding="utf-8") as f:
        json.dump(registry, f)


# ---------------------------------------------------------------------------
# detect_registry_version tests
# ---------------------------------------------------------------------------


class TestDetectRegistryVersion:
    def test_no_file_returns_none(self, base_dir: Path):
        result = detect_registry_version(base_dir / "topic-registry.json")
        assert result is None

    def test_v1_with_int_version(self, base_dir: Path):
        _write_v1_registry(base_dir, {})
        result = detect_registry_version(base_dir / "topic-registry.json")
        assert result == "1"

    def test_v1_with_string_version(self, base_dir: Path):
        registry = {"version": "1", "topics": {}}
        with open(base_dir / "topic-registry.json", "w") as f:
            json.dump(registry, f)
        result = detect_registry_version(base_dir / "topic-registry.json")
        assert result == "1"

    def test_v1_no_version_field(self, base_dir: Path):
        """Legacy v1 without version field."""
        registry = {"topics": {}, "active_topic": None}
        with open(base_dir / "topic-registry.json", "w") as f:
            json.dump(registry, f)
        result = detect_registry_version(base_dir / "topic-registry.json")
        assert result == "1"

    def test_v2_detected(self, base_dir: Path):
        _write_v2_registry(base_dir)
        result = detect_registry_version(base_dir / "topic-registry.json")
        assert result == "2.0"

    def test_unknown_version_raises(self, base_dir: Path):
        registry = {"version": 99, "topics": {}}
        with open(base_dir / "topic-registry.json", "w") as f:
            json.dump(registry, f)
        with pytest.raises(MigrationError, match="Unknown registry version"):
            detect_registry_version(base_dir / "topic-registry.json")

    def test_non_dict_raises(self, base_dir: Path):
        with open(base_dir / "topic-registry.json", "w") as f:
            json.dump([1, 2, 3], f)
        with pytest.raises(MigrationError, match="not a JSON object"):
            detect_registry_version(base_dir / "topic-registry.json")


# ---------------------------------------------------------------------------
# detect_migration_state tests
# ---------------------------------------------------------------------------


class TestDetectMigrationState:
    def test_no_registry_returns_v2_only(self, base_dir: Path):
        assert detect_migration_state(base_dir) == MigrationState.V2_ONLY

    def test_v1_registry_returns_v1_only(self, base_dir: Path):
        _write_v1_registry(base_dir, {})
        assert detect_migration_state(base_dir) == MigrationState.V1_ONLY

    def test_v2_without_marker_returns_v2_only(self, base_dir: Path):
        _write_v2_registry(base_dir)
        assert detect_migration_state(base_dir) == MigrationState.V2_ONLY

    def test_v2_with_marker_returns_migrated(self, base_dir: Path):
        _write_v2_registry(base_dir)
        marker = {"migrated_at": "2025-01-01T00:00:00+00:00"}
        with open(base_dir / ".migration-v1-to-v2.json", "w") as f:
            json.dump(marker, f)
        assert detect_migration_state(base_dir) == MigrationState.MIGRATED


# ---------------------------------------------------------------------------
# migrate_registry tests
# ---------------------------------------------------------------------------


class TestMigrateRegistry:
    def test_no_registry_returns_empty_v2(self, base_dir: Path):
        data, state = migrate_registry(base_dir)
        assert state == MigrationState.V2_ONLY
        assert data["version"] == "2.0"
        assert data["topics"] == {}

    def test_already_v2_is_noop(self, base_dir: Path):
        _write_v2_registry(
            base_dir, {"topic-1": {"topic_id": "topic-1", "label": "Test"}}
        )
        data, state = migrate_registry(base_dir)
        assert state == MigrationState.V2_ONLY
        assert "topic-1" in data["topics"]

    def test_v1_migration_basic(self, base_dir: Path):
        """Migrate a v1 registry with one topic."""
        _write_v1_registry(
            base_dir,
            {
                "topic-abc": {
                    "title": "My Topic",
                    "status": "active",
                    "created_at": "2025-01-01T00:00:00+00:00",
                    "updated_at": "2025-01-02T00:00:00+00:00",
                }
            },
        )

        data, state = migrate_registry(base_dir)

        assert state == MigrationState.MIGRATED
        assert data["version"] == "2.0"
        assert "topic-abc" in data["topics"]

        entry = data["topics"]["topic-abc"]
        assert entry["topic_id"] == "topic-abc"
        assert entry["label"] == "My Topic"
        assert entry["state"] == "active"
        assert entry["first_seen_at"] == "2025-01-01T00:00:00+00:00"
        assert entry["last_seen_at"] == "2025-01-02T00:00:00+00:00"

    def test_v1_status_mapping(self, base_dir: Path):
        """v1 paused → v2 warm, v1 archived → v2 archived."""
        _write_v1_registry(
            base_dir,
            {
                "t1": {
                    "title": "T1",
                    "status": "paused",
                    "created_at": "",
                    "updated_at": "",
                },
                "t2": {
                    "title": "T2",
                    "status": "archived",
                    "created_at": "",
                    "updated_at": "",
                },
                "t3": {
                    "title": "T3",
                    "status": "active",
                    "created_at": "",
                    "updated_at": "",
                },
            },
        )

        data, _ = migrate_registry(base_dir)
        assert data["topics"]["t1"]["state"] == "warm"
        assert data["topics"]["t2"]["state"] == "archived"
        assert data["topics"]["t3"]["state"] == "active"

    def test_v1_with_topic_files(self, base_dir: Path):
        """Migration enriches from individual topic files."""
        _write_v1_registry(
            base_dir,
            {
                "topic-xyz": {
                    "title": "Registry Title",
                    "status": "active",
                    "created_at": "2025-01-01T00:00:00+00:00",
                    "updated_at": "2025-01-02T00:00:00+00:00",
                }
            },
        )
        _write_v1_topic_file(
            base_dir,
            "topic-xyz",
            {
                "id": "topic-xyz",
                "title": "Full Title From File",
                "scope": "This topic covers XYZ",
                "status": "active",
                "parent": "parent-topic",
                "summary": "A summary from file",
                "created_at": "2025-01-01T00:00:00+00:00",
                "updated_at": "2025-01-03T00:00:00+00:00",
                "tags": ["tag1", "tag2"],
            },
        )

        data, state = migrate_registry(base_dir)
        entry = data["topics"]["topic-xyz"]

        assert entry["label"] == "Full Title From File"
        assert entry["description"] == "This topic covers XYZ"
        assert entry["parent_topic_id"] == "parent-topic"
        assert entry["summary"] == "A summary from file"
        # updated_at from file takes precedence
        assert entry["last_seen_at"] == "2025-01-03T00:00:00+00:00"

    def test_backup_created(self, base_dir: Path):
        """v1 backup is created before overwriting."""
        _write_v1_registry(
            base_dir,
            {
                "t": {
                    "title": "T",
                    "status": "active",
                    "created_at": "",
                    "updated_at": "",
                }
            },
        )

        migrate_registry(base_dir, backup=True)

        backup_path = base_dir / "topic-registry.v1.backup.json"
        assert backup_path.exists()
        with open(backup_path) as f:
            backup_data = json.load(f)
        assert backup_data["version"] == 1

    def test_no_backup_when_disabled(self, base_dir: Path):
        _write_v1_registry(
            base_dir,
            {
                "t": {
                    "title": "T",
                    "status": "active",
                    "created_at": "",
                    "updated_at": "",
                }
            },
        )

        migrate_registry(base_dir, backup=False)

        assert not (base_dir / "topic-registry.v1.backup.json").exists()

    def test_migration_marker_written(self, base_dir: Path):
        _write_v1_registry(
            base_dir,
            {
                "t1": {
                    "title": "T1",
                    "status": "active",
                    "created_at": "",
                    "updated_at": "",
                },
                "t2": {
                    "title": "T2",
                    "status": "paused",
                    "created_at": "",
                    "updated_at": "",
                },
            },
            active_topic="t1",
        )

        migrate_registry(base_dir)

        info = get_migration_info(base_dir)
        assert info is not None
        assert info["v1_topic_count"] == 2
        assert info["v2_topic_count"] == 2
        assert info["v1_active_topic"] == "t1"
        assert "migrated_at" in info

    def test_registry_file_overwritten_with_v2(self, base_dir: Path):
        """After migration, the registry file on disk is v2."""
        _write_v1_registry(
            base_dir,
            {
                "t": {
                    "title": "T",
                    "status": "active",
                    "created_at": "",
                    "updated_at": "",
                }
            },
        )

        migrate_registry(base_dir)

        with open(base_dir / "topic-registry.json") as f:
            on_disk = json.load(f)
        assert on_disk["version"] == "2.0"
        assert "t" in on_disk["topics"]

    def test_idempotent_after_migration(self, base_dir: Path):
        """Running migrate_registry twice is safe."""
        _write_v1_registry(
            base_dir,
            {
                "t": {
                    "title": "T",
                    "status": "active",
                    "created_at": "",
                    "updated_at": "",
                }
            },
        )

        data1, state1 = migrate_registry(base_dir)
        assert state1 == MigrationState.MIGRATED

        # Second call — now it's v2 on disk
        data2, state2 = migrate_registry(base_dir)
        assert state2 == MigrationState.V2_ONLY
        assert data2["topics"]["t"]["label"] == "T"


# ---------------------------------------------------------------------------
# TopicRegistryV2._load_registry auto-migration test
# ---------------------------------------------------------------------------


class TestRegistryAutoMigration:
    """Test that TopicRegistryV2._load_registry detects v1 and auto-migrates."""

    def test_load_registry_auto_migrates_v1(self, base_dir: Path):
        """When TopicRegistryV2 encounters a v1 registry, it auto-migrates."""
        from topic_registry_v2 import TopicRegistryV2

        _write_v1_registry(
            base_dir,
            {
                "auto-topic": {
                    "title": "Auto Migrated",
                    "status": "active",
                    "created_at": "2025-01-01T00:00:00+00:00",
                    "updated_at": "2025-01-02T00:00:00+00:00",
                }
            },
        )

        registry = TopicRegistryV2(base_dir=base_dir)
        # Should have loaded the migrated topic
        entry = registry.get_topic("auto-topic")
        assert entry is not None
        assert entry.label == "Auto Migrated"
        assert entry.state == "active" or (
            hasattr(entry.state, "value") and entry.state.value == "active"
        )

    def test_load_registry_v2_no_migration(self, base_dir: Path):
        """v2 registry loads normally without migration."""
        from topic_registry_v2 import TopicRegistryV2

        _write_v2_registry(
            base_dir,
            {
                "existing": {
                    "topic_id": "existing",
                    "label": "Existing Topic",
                    "state": "active",
                    "description": "",
                    "parent_topic_id": None,
                    "first_seen_at": "2025-01-01T00:00:00+00:00",
                    "last_seen_at": "2025-01-01T00:00:00+00:00",
                    "last_access_message_idx": 0,
                    "message_count": 0,
                    "compactions_since_last_access": 0,
                    "never_consolidate_items": [],
                    "priority_boost": 0.0,
                    "summary": None,
                    "key_decisions": [],
                    "last_raw_exchange": None,
                }
            },
        )

        registry = TopicRegistryV2(base_dir=base_dir)
        entry = registry.get_topic("existing")
        assert entry is not None
        assert entry.label == "Existing Topic"


# ---------------------------------------------------------------------------
# Server fallback on error test
# ---------------------------------------------------------------------------


class TestServerFallbackOnError:
    """Test server.py _handle_get_memory_context fallback behavior."""

    def test_fallback_returns_empty_on_error(self, base_dir: Path):
        """When memory context raises and v1_fallback_on_error is True, returns empty."""
        from server import ContextStateServer
        from feature_flags import FeatureFlags
        from unittest.mock import MagicMock

        os.environ["FISH_TRAIL_BASE_DIR"] = str(base_dir)
        os.environ["FISH_TRAIL_V2_ENABLED"] = "true"
        os.environ["FISH_TRAIL_V2_MEMORY_CONTEXT"] = "true"
        os.environ["FISH_TRAIL_V1_FALLBACK_ON_ERROR"] = "true"

        try:
            server = ContextStateServer(base_dir=str(base_dir))

            # Set up a mock memory_context that raises on get_memory_context
            mock_mc = MagicMock()
            mock_mc.get_memory_context.side_effect = RuntimeError("simulated failure")
            server._memory_context = mock_mc

            server._feature_flags = FeatureFlags(
                v2_enabled=True, v1_fallback_on_error=True
            )

            # Should NOT raise — fallback returns empty result
            result = server._handle_get_memory_context({})
            assert result["context_block"] == ""
            assert result["tokens_used"] == 0
        finally:
            for key in [
                "FISH_TRAIL_BASE_DIR",
                "FISH_TRAIL_V2_ENABLED",
                "FISH_TRAIL_V2_MEMORY_CONTEXT",
                "FISH_TRAIL_V1_FALLBACK_ON_ERROR",
            ]:
                os.environ.pop(key, None)
