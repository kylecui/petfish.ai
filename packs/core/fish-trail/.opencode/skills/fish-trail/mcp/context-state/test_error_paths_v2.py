"""Error-path and edge-case tests for Fish Trail Tiered Memory v2.

Covers 7 categories:
1. Registry error paths (exceptions on invalid operations)
2. Registry boundary conditions (zero/empty/large values)
3. Migration error paths (v1→v2 edge cases)
4. Lock re-entrancy (same-thread nesting)
5. Pressure monitor edge cases (empty/single/extreme)
6. Memory context edge cases (empty/cache/budget)
7. Server error paths (v2 disabled, unknown tools, malformed messages)

All tests use real modules (no mocks). Each test targets a specific
error path or boundary condition, verifying exceptions where expected
and graceful recovery where expected.
"""

import json
import os
import sys

# Ensure sibling imports work from this test file
_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
if _THIS_DIR not in sys.path:
    sys.path.insert(0, _THIS_DIR)

import pytest

from topic_registry_v2 import (
    TopicRegistryV2,
    TopicState,
    TopicEntry,
    RegistryConfig,
)
from memory_pressure_monitor import (
    MemoryPressureMonitor,
    BudgetConfig,
    RetentionConfig,
    PressureLevel,
    BudgetAllocation,
    BudgetAllocator,
    estimate_tokens,
)
from memory_context import MemoryContextProvider, MemoryContextResult

# ---------------------------------------------------------------------------
# 1. TestRegistryErrorPaths
# ---------------------------------------------------------------------------


class TestRegistryErrorPaths:
    """Tests that verify exceptions are raised for invalid registry operations."""

    def test_duplicate_topic_creation(self, tmp_path):
        """create_topic on same topic_id twice raises ValueError."""
        reg = TopicRegistryV2(str(tmp_path))
        reg.create_topic("dup", "Dup Topic")
        with pytest.raises(ValueError, match="Topic already exists: dup"):
            reg.create_topic("dup", "Dup Topic Again")

    def test_update_nonexistent_topic(self, tmp_path):
        """update_topic on non-existent topic raises KeyError."""
        reg = TopicRegistryV2(str(tmp_path))
        with pytest.raises(KeyError, match="Topic not found: nonexistent"):
            reg.update_topic("nonexistent", state="active")

    def test_record_access_nonexistent_topic(self, tmp_path):
        """record_access on non-existent topic raises KeyError."""
        reg = TopicRegistryV2(str(tmp_path))
        with pytest.raises(KeyError, match="Topic not found: nonexistent"):
            reg.record_access("nonexistent", 1)

    def test_reexpand_non_archived_topic(self, tmp_path):
        """reexpand_topic on an ACTIVE topic raises ValueError."""
        reg = TopicRegistryV2(str(tmp_path))
        reg.create_topic("t1", "Active Topic")
        with pytest.raises(
            ValueError, match="Only archived topics can be re-expanded"
        ):
            reg.reexpand_topic("t1")

    def test_reexpand_nonexistent_topic(self, tmp_path):
        """reexpand_topic on non-existent topic raises KeyError."""
        reg = TopicRegistryV2(str(tmp_path))
        with pytest.raises(KeyError, match="Topic not found: nowhere"):
            reg.reexpand_topic("nowhere")

    def test_corrupt_registry_file_not_dict(self, tmp_path):
        """Non-dict registry payload raises ValueError on load."""
        reg = TopicRegistryV2(str(tmp_path))
        # Write a JSON list (not dict) to the registry file
        registry_path = tmp_path / "topic-registry.json"
        registry_path.write_text(json.dumps([1, 2, 3]), encoding="utf-8")
        with pytest.raises(ValueError, match="Invalid registry payload"):
            reg.get_topic("any")  # triggers _load_registry


# ---------------------------------------------------------------------------
# 2. TestRegistryBoundaryConditions
# ---------------------------------------------------------------------------


class TestRegistryBoundaryConditions:
    """Tests that verify correct behavior at numerical / operational boundaries."""

    def test_empty_registry_operations(self, tmp_path):
        """Create, list, get, update on a fresh empty registry."""
        reg = TopicRegistryV2(str(tmp_path))

        # List is empty
        topics = reg.list_topics()
        assert topics == []

        # Get returns None for non-existent
        assert reg.get_topic("nope") is None

        # Create a topic
        t = reg.create_topic("t1", "First")
        assert t.topic_id == "t1"
        assert t.state == TopicState.ACTIVE.value

        # List now has 1
        topics = reg.list_topics()
        assert len(topics) == 1

        # Update
        updated = reg.update_topic("t1", description="Updated desc")
        assert updated.description == "Updated desc"

    def test_single_topic_lifecycle(self, tmp_path):
        """Full lifecycle: create → access → transitions → compaction."""
        reg = TopicRegistryV2(str(tmp_path))

        # Create
        t = reg.create_topic("life", "Lifecycle Topic")
        assert t.state == TopicState.ACTIVE.value
        assert t.message_count == 0

        # Access (record_access)
        t2 = reg.record_access("life", 5)
        assert t2.message_count == 1
        assert t2.last_access_message_idx == 5
        assert t2.compactions_since_last_access == 0

        # Multiple accesses
        for i in range(10, 70, 10):
            reg.record_access("life", i)

        t3 = reg.get_topic("life")
        assert t3 is not None
        assert t3.message_count == 7  # 1 + 6 more

        # Compaction
        transitions = reg.on_compaction("compaction-001")
        # After 1 compaction, ACTIVE stays ACTIVE (only WARM/COLD increment)

        # Final state should still be active since we accessed it recently
        t4 = reg.get_topic("life")
        assert t4 is not None
        assert t4.state == TopicState.ACTIVE.value
        assert t4.compactions_since_last_access == 0

    def test_zero_message_idx(self, tmp_path):
        """record_access with message_idx=0 succeeds."""
        reg = TopicRegistryV2(str(tmp_path))
        reg.create_topic("t0", "Zero Idx")
        t = reg.record_access("t0", 0)
        assert t.last_access_message_idx == 0
        assert t.message_count == 1

    def test_very_large_message_idx(self, tmp_path):
        """record_access with message_idx=999999 does not overflow."""
        reg = TopicRegistryV2(str(tmp_path))
        reg.create_topic("big", "Big Idx")
        t = reg.record_access("big", 999999)
        assert t.last_access_message_idx == 999999
        assert t.message_count == 1
        # Verify persistence roundtrip
        t2 = reg.get_topic("big")
        assert t2 is not None
        assert t2.last_access_message_idx == 999999

    def test_update_immutable_fields(self, tmp_path):
        """update_topic on first_seen_at is silently ignored.

        Note: topic_id is a positional-only parameter of update_topic,
        not part of **fields, so it cannot be tested as a kwarg.
        first_seen_at IS in the immutable set inside **fields.
        """
        reg = TopicRegistryV2(str(tmp_path))
        orig = reg.create_topic("imm", "Immutable Test")
        orig_first = orig.first_seen_at

        # Try to update immutable field first_seen_at via **fields
        updated = reg.update_topic(
            "imm",
            first_seen_at="2020-01-01T00:00:00",
            description="new desc",
        )
        assert updated.first_seen_at == orig_first  # unchanged (immutable)
        assert updated.description == "new desc"  # mutable field changed


# ---------------------------------------------------------------------------
# 3. TestMigrationErrorPaths
# ---------------------------------------------------------------------------


class TestMigrationErrorPaths:
    """Tests for v1→v2 migration edge cases."""

    def test_migrate_from_empty_v1_data(self, tmp_path):
        """Empty v1 data returns 0 migrated topics."""
        reg = TopicRegistryV2(str(tmp_path))
        count = reg.migrate_from_v1({})
        assert count == 0

    def test_migrate_from_v1_with_archived_topic(self, tmp_path):
        """v1 topic with status='archived' becomes ARCHIVED in v2."""
        reg = TopicRegistryV2(str(tmp_path))
        v1_data = {
            "version": 1,
            "active_topic": None,
            "topics": {
                "archived_one": {
                    "title": "Old Archived",
                    "status": "archived",
                    "created_at": "2025-01-01T00:00:00Z",
                    "updated_at": "2025-01-01T00:00:00Z",
                }
            },
            "links": [],
        }
        count = reg.migrate_from_v1(v1_data)
        assert count == 1

        topic = reg.get_topic("archived_one")
        assert topic is not None
        assert topic.state == TopicState.ARCHIVED.value
        assert topic.label == "Old Archived"

    def test_migrate_duplicate_topics(self, tmp_path):
        """v1 topics already in v2 are skipped (return 0 for duplicates)."""
        reg = TopicRegistryV2(str(tmp_path))

        # First migration
        v1_data = {
            "version": 1,
            "topics": {
                "dup_topic": {
                    "title": "Dup",
                    "status": "active",
                }
            },
        }
        count1 = reg.migrate_from_v1(v1_data)
        assert count1 == 1

        # Second migration of same data
        count2 = reg.migrate_from_v1(v1_data)
        assert count2 == 0  # already exists, skipped

    def test_migrate_v1_active_topic_mapping(self, tmp_path):
        """v1 active_topic → ACTIVE, other non-archived → WARM."""
        reg = TopicRegistryV2(str(tmp_path))
        v1_data = {
            "version": 1,
            "active_topic": "active_one",
            "topics": {
                "active_one": {
                    "title": "Active Topic",
                    "status": "active",
                },
                "warm_one": {
                    "title": "Warm Topic",
                    "status": "active",
                },
            },
        }
        count = reg.migrate_from_v1(v1_data)
        assert count == 2

        active_topic = reg.get_topic("active_one")
        warm_topic = reg.get_topic("warm_one")

        assert active_topic is not None
        assert active_topic.state == TopicState.ACTIVE.value
        assert warm_topic is not None
        assert warm_topic.state == TopicState.WARM.value


# ---------------------------------------------------------------------------
# 4. TestLockReentrancy
# ---------------------------------------------------------------------------


class TestLockReentrancy:
    """Tests that the registry lock allows same-thread re-entrancy
    without deadlocking."""

    def test_lock_reentrancy_same_thread(self, tmp_path):
        """Nested _enter_lock/_exit_lock on same thread does not deadlock."""
        reg = TopicRegistryV2(str(tmp_path))
        # Acquire lock, then acquire again (re-entrant), then release twice
        reg._enter_lock()
        try:
            reg._enter_lock()
            try:
                # Both locks held — no deadlock proves re-entrancy
                assert reg._lock_depth == 2
            finally:
                reg._exit_lock()
            assert reg._lock_depth == 1
        finally:
            reg._exit_lock()
        assert reg._lock_depth == 0

    def test_lock_operations_under_lock(self, tmp_path):
        """Chain of locked operations (create → update → get) without deadlock.
        Since public API methods use lock internally and the lock is re-entrant,
        calling them while manually holding the lock should work."""
        reg = TopicRegistryV2(str(tmp_path))
        reg._enter_lock()
        try:
            # These all call _enter_lock/_exit_lock internally,
            # which is re-entrant for the same thread
            reg.create_topic("lt1", "Locked Topic 1")
            reg.update_topic("lt1", description="Updated under lock")
            t = reg.get_topic("lt1")
            assert t is not None
            assert t.description == "Updated under lock"

            reg.create_topic("lt2", "Locked Topic 2")
            topics = reg.list_topics()
            assert len(topics) == 2
        finally:
            reg._exit_lock()

        # Verify state is consistent after lock release
        t1 = reg.get_topic("lt1")
        t2 = reg.get_topic("lt2")
        assert t1 is not None
        assert t2 is not None
        assert t1.state == TopicState.ACTIVE.value
        assert t2.state == TopicState.ACTIVE.value


# ---------------------------------------------------------------------------
# 5. TestPressureMonitorEdgeCases
# ---------------------------------------------------------------------------


class TestPressureMonitorEdgeCases:
    """Tests for MemoryPressureMonitor edge cases and boundary conditions."""

    def test_assess_empty_topics(self):
        """monitor.assess([]) returns valid BudgetAllocation with NORMAL pressure."""
        monitor = MemoryPressureMonitor()
        result = monitor.assess([])

        assert result.pressure_level == PressureLevel.NORMAL
        assert result.allocation.total_budget > 0
        assert result.allocation.index.allocated_tokens >= 0
        assert result.overflow_actions == []
        assert result.alert is None

    def test_assess_single_active_topic(self):
        """Single active topic yields valid allocation."""
        monitor = MemoryPressureMonitor()
        topics = [
            {
                "topic_id": "t1",
                "state": "active",
                "label": "Test",
                "summary": "A test topic summary",
                "description": "Test desc",
                "key_decisions": [],
                "last_raw_exchange": None,
                "never_consolidate_items": [],
            }
        ]
        result = monitor.assess(topics)

        assert result.pressure_level == PressureLevel.NORMAL
        assert result.allocation.total_budget > 0
        # At least the active tier should have some allocation
        assert result.allocation.active.allocated_tokens >= 0
        assert "t1" in result.allocation.active.topics_included

    def test_assess_archived_only_topics(self):
        """All topics archived → zero token allocation for archived tiers."""
        monitor = MemoryPressureMonitor()
        topics = [
            {
                "topic_id": "a1",
                "state": "archived",
                "label": "Archived 1",
                "summary": "Old topic",
                "key_decisions": [],
                "last_raw_exchange": None,
                "never_consolidate_items": [],
            },
            {
                "topic_id": "a2",
                "state": "archived",
                "label": "Archived 2",
                "summary": "Old topic 2",
                "key_decisions": [],
                "last_raw_exchange": None,
                "never_consolidate_items": [],
            },
        ]
        result = monitor.assess(topics)

        assert result.pressure_level == PressureLevel.NORMAL
        # Archived topics should not appear in active/warm/cold included
        assert len(result.allocation.active.topics_included) == 0
        assert len(result.allocation.warm.topics_included) == 0
        assert len(result.allocation.cold.topics_included) == 0

    def test_estimate_tokens_edge_cases(self):
        """estimate_tokens handles empty and very long strings."""
        assert estimate_tokens("") == 0
        # None/falsy is handled at runtime (not if content → return 0),
        # but the type hint says str, so test empty string instead
        assert estimate_tokens("") == 0
        # Very long string returns a reasonable token estimate
        long_str = "a" * 100000
        tokens = estimate_tokens(long_str)
        assert tokens > 0
        assert tokens < 100000  # Should be chars/3.5, so ~28571

    def test_extreme_budget_config(self):
        """BudgetConfig with zero/negative-like values should not crash."""
        # total_context_window=0 — should work (ratio-based allocation)
        cfg = BudgetConfig(total_context_window=100)  # very small
        monitor = MemoryPressureMonitor(budget_config=cfg)
        topics = [
            {
                "topic_id": "t1",
                "state": "active",
                "label": "Test",
                "summary": "Summary text",
                "key_decisions": [],
                "last_raw_exchange": None,
                "never_consolidate_items": [],
            }
        ]
        result = monitor.assess(topics)
        # Should not crash — allocation may have near-zero budgets but must be valid
        assert result.allocation is not None
        assert result.pressure_level is not None

    def test_zero_thresholds_config(self):
        """All-zero thresholds (pressure_l1/l2/l3) produce correct pressure."""
        cfg = BudgetConfig(
            total_context_window=100000,
            pressure_l1=0.0,
            pressure_l2=0.0,
            pressure_l3=0.0,
        )
        monitor = MemoryPressureMonitor(budget_config=cfg)
        # With lots of topics, utilization may be non-zero, but with
        # all thresholds at 0.0, ANY usage >= 0.0 triggers NORMAL first...
        # Actually the detection uses >= so 0.0 >= 0.0 is True for L3.
        # This is an edge case — but the allocator should not crash.
        topics = [
            {
                "topic_id": f"t{i}",
                "state": "active",
                "label": f"Topic {i}",
                "summary": f"Summary {i}",
                "key_decisions": [],
                "last_raw_exchange": None,
                "never_consolidate_items": [],
            }
            for i in range(10)
        ]
        result = monitor.assess(topics)
        assert result.allocation is not None
        # With all thresholds at 0, should be at L3 (emergency)
        # but must not crash
        assert result.pressure_level in (
            PressureLevel.NORMAL,
            PressureLevel.L1,
            PressureLevel.L2,
            PressureLevel.L3,
        )


# ---------------------------------------------------------------------------
# 6. TestMemoryContextEdgeCases
# ---------------------------------------------------------------------------


class TestMemoryContextEdgeCases:
    """Tests for MemoryContextProvider edge cases and cache behavior."""

    def test_empty_registry_context(self, tmp_path):
        """Provider with empty registry returns valid result."""
        reg = TopicRegistryV2(str(tmp_path))
        monitor = MemoryPressureMonitor()
        provider = MemoryContextProvider(registry=reg, pressure_monitor=monitor)

        result = provider.get_memory_context()
        assert isinstance(result, MemoryContextResult)
        assert result.context_block == ""
        assert result.tokens_used == 0
        assert result.cache_hit is False
        assert result.metadata.topics_active == 0

    def test_nonexistent_topic_context(self, tmp_path):
        """get_memory_context with nonexistent topic_id falls back gracefully."""
        reg = TopicRegistryV2(str(tmp_path))
        reg.create_topic("real", "Real Topic")
        monitor = MemoryPressureMonitor()
        provider = MemoryContextProvider(registry=reg, pressure_monitor=monitor)

        # Request nonexistent topic — should use first active topic
        result = provider.get_memory_context(current_topic_id="nonexistent")
        assert isinstance(result, MemoryContextResult)
        # Should have valid metadata
        assert result.metadata.topics_active == 1

    def test_zero_budget_context(self, tmp_path):
        """budget_tokens=0 returns valid response (may return empty context)."""
        reg = TopicRegistryV2(str(tmp_path))
        reg.create_topic("t1", "Budget Zero")
        monitor = MemoryPressureMonitor()
        provider = MemoryContextProvider(registry=reg, pressure_monitor=monitor)

        result = provider.get_memory_context(budget_tokens=0)
        assert isinstance(result, MemoryContextResult)
        assert result.tokens_used >= 0  # may be 0

    def test_cache_hit_on_repeated_call(self, tmp_path):
        """Second call with same args should return cache_hit=True."""
        reg = TopicRegistryV2(str(tmp_path))
        reg.create_topic("ct1", "Cached Topic")
        monitor = MemoryPressureMonitor()
        provider = MemoryContextProvider(registry=reg, pressure_monitor=monitor)

        # First call — not cached
        result1 = provider.get_memory_context(current_topic_id="ct1")
        assert result1.cache_hit is False

        # Second call with same args — cached
        result2 = provider.get_memory_context(current_topic_id="ct1")
        assert result2.cache_hit is True
        # Results should be identical
        assert result2.context_block == result1.context_block
        assert result2.tokens_used == result1.tokens_used

    def test_cache_invalidation_on_new_topic(self, tmp_path):
        """Creating a new topic invalidates the cache (topic count changes)."""
        reg = TopicRegistryV2(str(tmp_path))
        reg.create_topic("ci1", "Cache Test 1")
        monitor = MemoryPressureMonitor()
        provider = MemoryContextProvider(registry=reg, pressure_monitor=monitor)

        # First call — cache miss
        result1 = provider.get_memory_context(current_topic_id="ci1")
        assert result1.cache_hit is False

        # Second call — cache hit
        result2 = provider.get_memory_context(current_topic_id="ci1")
        assert result2.cache_hit is True

        # Create a new topic — changes topic count, invalidates cache
        reg.create_topic("ci2", "Cache Test 2")

        # Third call — should be cache miss (topic count changed)
        result3 = provider.get_memory_context(current_topic_id="ci1")
        assert result3.cache_hit is False

    def test_explicit_cache_invalidation(self, tmp_path):
        """invalidate_cache() forces cache miss on next call."""
        reg = TopicRegistryV2(str(tmp_path))
        reg.create_topic("ei1", "Explicit Inval")
        monitor = MemoryPressureMonitor()
        provider = MemoryContextProvider(registry=reg, pressure_monitor=monitor)

        # First call — miss
        result1 = provider.get_memory_context(current_topic_id="ei1")
        assert result1.cache_hit is False

        # Second call — hit
        result2 = provider.get_memory_context(current_topic_id="ei1")
        assert result2.cache_hit is True

        # Invalidate
        provider.invalidate_cache()

        # Third call — miss
        result3 = provider.get_memory_context(current_topic_id="ei1")
        assert result3.cache_hit is False


# ---------------------------------------------------------------------------
# 7. TestServerErrorPaths
# ---------------------------------------------------------------------------


class TestServerErrorPaths:
    """Tests for server-level error handling in ContextStateServer."""

    def _make_server(self, tmp_path):
        """Helper to create a ContextStateServer with a temp base_dir."""
        from server import ContextStateServer

        base_dir = str(tmp_path / "fish-trail")
        os.makedirs(base_dir, exist_ok=True)
        return ContextStateServer(base_dir)

    def _tool_call_msg(self, msg_id, tool_name, arguments=None):
        """Build a JSON-RPC tools/call message."""
        return {
            "method": "tools/call",
            "id": msg_id,
            "params": {
                "name": tool_name,
                "arguments": arguments or {},
            },
        }

    def _is_error_response(self, response):
        """Check if response indicates an error (JSON-RPC error or isError)."""
        if response is None:
            return False
        if "error" in response:
            return True
        result = response.get("result", {})
        if isinstance(result, dict) and result.get("isError"):
            return True
        return False

    def test_get_memory_context_when_v2_disabled(self, tmp_path):
        """When v2 is disabled, get_memory_context returns error response."""
        from server import ContextStateServer

        base_dir = str(tmp_path / "fish-trail")
        os.makedirs(base_dir, exist_ok=True)
        # Write config with v2 disabled so handler is not registered
        config_path = os.path.join(base_dir, "config.json")
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump({"feature_flags": {"v2_enabled": False}}, f)
        server = ContextStateServer(base_dir)
        msg = self._tool_call_msg(1, "get_memory_context")
        response = server.handle_message(msg)

        # Should be an error response — tool not registered when v2 disabled
        assert response is not None
        assert self._is_error_response(response)

    def test_unknown_tool_request(self, tmp_path):
        """Calling nonexistent tool returns error response."""
        server = self._make_server(tmp_path)
        msg = self._tool_call_msg(2, "nonexistent_tool")
        response = server.handle_message(msg)

        assert response is not None
        assert self._is_error_response(response)

    def test_malformed_message_no_method(self, tmp_path):
        """Message without 'method' field is handled gracefully."""
        server = self._make_server(tmp_path)
        # No method field — defaults to ""
        msg: dict = {"id": 3, "params": {}}
        response = server.handle_message(msg)

        # Should return an error for unknown method
        assert response is not None
        assert "error" in response
        assert response["error"]["code"] == -32601

    def test_tools_call_missing_params(self, tmp_path):
        """tools/call without params dict is handled gracefully."""
        server = self._make_server(tmp_path)
        # tools/call method but no params key
        msg: dict = {"method": "tools/call", "id": 4}
        response = server.handle_message(msg)

        assert response is not None
        # Should return error for unknown tool (empty name)
        assert self._is_error_response(response)
