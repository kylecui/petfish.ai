"""Unit tests for TopicRegistryV2.

Covers:
- Topic CRUD (create, get, list, update)
- State transitions (ACTIVE→WARM→COLD→ARCHIVED)
- Re-activation (WARM/COLD→ACTIVE)
- Re-expand (ARCHIVED→COLD)
- Compaction handler (backup, counter increment, transitions)
- Migration from v1 format
- NeverConsolidateItem, KeyDecision, RawExchange handling
- Persistence (atomic write, reload correctness)
- Edge cases (duplicate create, missing topic, immutable fields)
"""

import json
import os
import tempfile
from pathlib import Path

import pytest

from topic_registry_v2 import (
    KeyDecision,
    NeverConsolidateItem,
    RawExchange,
    RegistryConfig,
    TopicEntry,
    TopicRegistryV2,
    TopicState,
)


@pytest.fixture
def tmp_dir():
    with tempfile.TemporaryDirectory() as d:
        yield d


@pytest.fixture
def registry(tmp_dir):
    return TopicRegistryV2(tmp_dir)


@pytest.fixture
def registry_fast(tmp_dir):
    """Registry with low thresholds for faster transition testing."""
    config = RegistryConfig(
        active_threshold_messages=2,
        warm_to_cold_compactions=1,
        cold_to_archived_compactions=2,
    )
    return TopicRegistryV2(tmp_dir, config=config)


# ---------------------------------------------------------------------------
# Topic CRUD
# ---------------------------------------------------------------------------


class TestTopicCRUD:
    def test_create_topic(self, registry):
        entry = registry.create_topic("t1", "Topic One", description="desc")
        assert entry.topic_id == "t1"
        assert entry.label == "Topic One"
        assert entry.state == TopicState.ACTIVE.value
        assert entry.description == "desc"
        assert entry.message_count == 0
        assert entry.first_seen_at != ""

    def test_create_duplicate_raises(self, registry):
        registry.create_topic("t1", "Topic One")
        with pytest.raises(ValueError, match="already exists"):
            registry.create_topic("t1", "Topic One Again")

    def test_get_topic(self, registry):
        registry.create_topic("t1", "Topic One")
        entry = registry.get_topic("t1")
        assert entry is not None
        assert entry.label == "Topic One"

    def test_get_nonexistent_returns_none(self, registry):
        assert registry.get_topic("nope") is None

    def test_list_topics_all(self, registry):
        registry.create_topic("t1", "One")
        registry.create_topic("t2", "Two")
        topics = registry.list_topics()
        assert len(topics) == 2

    def test_list_topics_by_state(self, registry):
        registry.create_topic("t1", "One")
        registry.create_topic("t2", "Two")
        # All are active
        active = registry.list_topics(state=TopicState.ACTIVE)
        assert len(active) == 2
        warm = registry.list_topics(state=TopicState.WARM)
        assert len(warm) == 0

    def test_update_topic(self, registry):
        registry.create_topic("t1", "One")
        updated = registry.update_topic("t1", label="Updated", description="new desc")
        assert updated.label == "Updated"
        assert updated.description == "new desc"

    def test_update_nonexistent_raises(self, registry):
        with pytest.raises(KeyError, match="not found"):
            registry.update_topic("nope", label="X")

    def test_update_immutable_fields_ignored(self, registry):
        registry.create_topic("t1", "One")
        entry = registry.get_topic("t1")
        original_first_seen = entry.first_seen_at
        registry.update_topic("t1", first_seen_at="2000-01-01")
        reloaded = registry.get_topic("t1")
        assert reloaded.topic_id == "t1"
        assert reloaded.first_seen_at == original_first_seen

    def test_create_with_parent(self, registry):
        registry.create_topic("parent", "Parent")
        entry = registry.create_topic("child", "Child", parent_topic_id="parent")
        assert entry.parent_topic_id == "parent"


# ---------------------------------------------------------------------------
# Record Access & Re-activation
# ---------------------------------------------------------------------------


class TestRecordAccess:
    def test_record_access_increments_count(self, registry):
        registry.create_topic("t1", "One")
        entry = registry.record_access("t1", message_idx=5)
        assert entry.message_count == 1
        assert entry.last_access_message_idx == 5

    def test_record_access_resets_compaction_counter(self, registry):
        registry.create_topic("t1", "One")
        # Manually set compactions_since_last_access
        registry.update_topic(
            "t1", compactions_since_last_access=3, state=TopicState.WARM.value
        )
        entry = registry.record_access("t1", message_idx=10)
        assert entry.compactions_since_last_access == 0
        # WARM → ACTIVE re-activation
        assert entry.state == TopicState.ACTIVE.value

    def test_reactivation_from_cold(self, registry):
        registry.create_topic("t1", "One")
        registry.update_topic("t1", state=TopicState.COLD.value)
        entry = registry.record_access("t1", message_idx=20)
        assert entry.state == TopicState.ACTIVE.value

    def test_no_reactivation_from_archived(self, registry):
        """Archived topics are NOT re-activated by record_access (use reexpand instead)."""
        registry.create_topic("t1", "One")
        registry.update_topic("t1", state=TopicState.ARCHIVED.value)
        entry = registry.record_access("t1", message_idx=30)
        # Archived stays archived via record_access
        assert entry.state == TopicState.ARCHIVED.value

    def test_record_access_nonexistent_raises(self, registry):
        with pytest.raises(KeyError, match="not found"):
            registry.record_access("nope", message_idx=1)


# ---------------------------------------------------------------------------
# State Transitions
# ---------------------------------------------------------------------------


class TestStateTransitions:
    def test_active_to_warm(self, registry_fast):
        """ACTIVE→WARM when msg_gap > threshold AND multiple active topics exist."""
        reg = registry_fast
        reg.create_topic("t1", "One")
        reg.record_access("t1", message_idx=0)
        reg.create_topic("t2", "Two")
        reg.record_access("t2", message_idx=5)

        # t1 last accessed at idx=0, current=5, gap=5 > threshold=2, multiple active
        transitions = reg.check_transitions(current_message_idx=5)
        assert len(transitions) == 1
        assert transitions[0]["topic_id"] == "t1"
        assert transitions[0]["from"] == "active"
        assert transitions[0]["to"] == "warm"

    def test_no_transition_single_active(self, registry_fast):
        """No ACTIVE→WARM if only one active topic."""
        reg = registry_fast
        reg.create_topic("t1", "One")
        reg.record_access("t1", message_idx=0)
        transitions = reg.check_transitions(current_message_idx=100)
        assert transitions == []

    def test_warm_to_cold_on_compaction(self, registry_fast):
        """WARM→COLD when compactions_since >= warm_to_cold_compactions."""
        reg = registry_fast
        reg.create_topic("t1", "One")
        reg.update_topic("t1", state=TopicState.WARM.value)

        transitions = reg.on_compaction("compact-001")
        # After compaction, t1 (warm) gets compactions_since=1 >= threshold=1
        assert any(t["topic_id"] == "t1" and t["to"] == "cold" for t in transitions)

    def test_cold_to_archived_on_compaction(self, registry_fast):
        """COLD→ARCHIVED when compactions_since >= cold_to_archived_compactions (2)."""
        reg = registry_fast
        reg.create_topic("t1", "One")
        reg.update_topic(
            "t1", state=TopicState.COLD.value, compactions_since_last_access=1
        )

        # First compaction: compactions_since becomes 2 >= threshold 2
        transitions = reg.on_compaction("compact-002")
        assert any(t["topic_id"] == "t1" and t["to"] == "archived" for t in transitions)

    def test_warm_to_cold_discards_raw_exchange(self, registry_fast):
        """When transitioning WARM→COLD, last_raw_exchange is cleared."""
        reg = registry_fast
        reg.create_topic("t1", "One")
        raw = RawExchange(
            user_message="hello",
            assistant_message="hi",
            message_idx=1,
            timestamp="2026-01-01T00:00:00Z",
        )
        reg.update_topic("t1", state=TopicState.WARM.value, last_raw_exchange=raw)

        reg.on_compaction("compact-003")
        entry = reg.get_topic("t1")
        assert entry.state == TopicState.COLD.value
        assert entry.last_raw_exchange is None


# ---------------------------------------------------------------------------
# Re-expand
# ---------------------------------------------------------------------------


class TestReexpand:
    def test_reexpand_archived_to_cold(self, registry):
        registry.create_topic("t1", "One")
        registry.update_topic("t1", state=TopicState.ARCHIVED.value)
        entry = registry.reexpand_topic("t1")
        assert entry.state == TopicState.COLD.value
        assert entry.compactions_since_last_access == 0

    def test_reexpand_non_archived_raises(self, registry):
        registry.create_topic("t1", "One")
        with pytest.raises(ValueError, match="Only archived"):
            registry.reexpand_topic("t1")

    def test_reexpand_nonexistent_raises(self, registry):
        with pytest.raises(KeyError, match="not found"):
            registry.reexpand_topic("nope")


# ---------------------------------------------------------------------------
# Compaction Handler
# ---------------------------------------------------------------------------


class TestCompaction:
    def test_compaction_creates_backup(self, tmp_dir):
        reg = TopicRegistryV2(tmp_dir)
        reg.create_topic("t1", "One")
        reg.on_compaction("backup-001")

        backup_path = Path(tmp_dir) / "registry-backups" / "backup-001.json"
        assert backup_path.exists()

    def test_compaction_increments_counter(self, registry):
        registry.create_topic("t1", "One")
        assert registry.get_compaction_count() == 0
        registry.on_compaction("c1")
        assert registry.get_compaction_count() == 1
        registry.on_compaction("c2")
        assert registry.get_compaction_count() == 2

    def test_compaction_does_not_increment_active_topics(self, registry):
        """Active topics don't get compactions_since incremented."""
        registry.create_topic("t1", "One")  # active
        registry.on_compaction("c1")
        entry = registry.get_topic("t1")
        assert entry.compactions_since_last_access == 0

    def test_compaction_increments_non_active(self, registry):
        registry.create_topic("t1", "One")
        registry.update_topic("t1", state=TopicState.WARM.value)
        registry.on_compaction("c1")
        entry = registry.get_topic("t1")
        assert entry.compactions_since_last_access == 1


# ---------------------------------------------------------------------------
# Migration from v1
# ---------------------------------------------------------------------------


class TestMigration:
    def test_migrate_basic(self, registry):
        v1_data = {
            "version": 1,
            "active_topic": "topic-a",
            "topics": {
                "topic-a": {
                    "title": "Topic A",
                    "status": "active",
                    "created_at": "2026-01-01T00:00:00Z",
                    "updated_at": "2026-01-02T00:00:00Z",
                },
                "topic-b": {
                    "title": "Topic B",
                    "status": "paused",
                    "created_at": "2026-01-01T00:00:00Z",
                    "updated_at": "2026-01-02T00:00:00Z",
                },
                "topic-c": {
                    "title": "Topic C",
                    "status": "archived",
                    "created_at": "2026-01-01T00:00:00Z",
                    "updated_at": "2026-01-02T00:00:00Z",
                },
            },
            "links": [],
        }

        count = registry.migrate_from_v1(v1_data)
        assert count == 3

        a = registry.get_topic("topic-a")
        assert a.state == TopicState.ACTIVE.value
        assert a.label == "Topic A"

        b = registry.get_topic("topic-b")
        assert b.state == TopicState.WARM.value  # non-active, non-archived → WARM

        c = registry.get_topic("topic-c")
        assert c.state == TopicState.ARCHIVED.value

    def test_migrate_skips_existing(self, registry):
        registry.create_topic("topic-a", "Already Here")
        v1_data = {
            "version": 1,
            "active_topic": "topic-a",
            "topics": {"topic-a": {"title": "From V1", "status": "active"}},
            "links": [],
        }
        count = registry.migrate_from_v1(v1_data)
        assert count == 0
        # Original label preserved
        assert registry.get_topic("topic-a").label == "Already Here"


# ---------------------------------------------------------------------------
# NeverConsolidateItem, KeyDecision, RawExchange
# ---------------------------------------------------------------------------


class TestDataClasses:
    def test_never_consolidate_roundtrip(self, registry):
        registry.create_topic("t1", "One")
        items = [
            NeverConsolidateItem(
                item_id="nci-1",
                type="decision",
                content="Always use uv",
                source_message_idx=3,
                added_at="2026-01-01T00:00:00Z",
                reason="Project policy",
            )
        ]
        registry.update_topic("t1", never_consolidate_items=items)
        entry = registry.get_topic("t1")
        assert len(entry.never_consolidate_items) == 1
        assert entry.never_consolidate_items[0].item_id == "nci-1"
        assert entry.never_consolidate_items[0].content == "Always use uv"

    def test_key_decision_roundtrip(self, registry):
        registry.create_topic("t1", "One")
        decisions = [
            KeyDecision(
                decision_id="kd-1",
                description="Use MCP as primary",
                rationale="Lower coupling",
                timestamp="2026-01-01T00:00:00Z",
                alternatives_considered=["Plugin API", "Direct import"],
            )
        ]
        registry.update_topic("t1", key_decisions=decisions)
        entry = registry.get_topic("t1")
        assert len(entry.key_decisions) == 1
        assert entry.key_decisions[0].alternatives_considered == [
            "Plugin API",
            "Direct import",
        ]

    def test_raw_exchange_roundtrip(self, registry):
        registry.create_topic("t1", "One")
        raw = RawExchange(
            user_message="What's the plan?",
            assistant_message="We're implementing v2.",
            message_idx=7,
            timestamp="2026-01-01T00:00:00Z",
        )
        registry.update_topic("t1", last_raw_exchange=raw)
        entry = registry.get_topic("t1")
        assert entry.last_raw_exchange is not None
        assert entry.last_raw_exchange.user_message == "What's the plan?"


# ---------------------------------------------------------------------------
# Persistence
# ---------------------------------------------------------------------------


class TestPersistence:
    def test_survives_reload(self, tmp_dir):
        reg1 = TopicRegistryV2(tmp_dir)
        reg1.create_topic("t1", "Persistent")
        reg1.set_session_id("session-xyz")

        # New instance loads from same file
        reg2 = TopicRegistryV2(tmp_dir)
        entry = reg2.get_topic("t1")
        assert entry is not None
        assert entry.label == "Persistent"
        assert reg2.get_session_id() == "session-xyz"

    def test_registry_file_is_valid_json(self, tmp_dir):
        reg = TopicRegistryV2(tmp_dir)
        reg.create_topic("t1", "One")

        path = Path(tmp_dir) / "topic-registry.json"
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        assert data["version"] == "2.0"
        assert "t1" in data["topics"]


# ---------------------------------------------------------------------------
# Registry Metadata
# ---------------------------------------------------------------------------


class TestMetadata:
    def test_session_id(self, registry):
        assert registry.get_session_id() is None
        registry.set_session_id("sess-1")
        assert registry.get_session_id() == "sess-1"

    def test_get_registry_metadata(self, registry):
        registry.create_topic("t1", "One")
        registry.create_topic("t2", "Two")
        meta = registry.get_registry_metadata()
        assert meta["version"] == "2.0"
        assert meta["topic_count"] == 2
        assert meta["compaction_count"] == 0

    def test_config_hash_changes_with_config(self, tmp_dir):
        c1 = RegistryConfig(active_threshold_messages=5)
        c2 = RegistryConfig(active_threshold_messages=10)
        assert c1.config_hash() != c2.config_hash()


# ---------------------------------------------------------------------------
# Entry point for direct execution
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
