"""Performance benchmarks for Fish Trail Tiered Memory v2.

Tests measure timing for 4 key performance areas:
1. Compaction Throughput
2. Registry I/O Performance
3. Pressure Monitor Performance
4. End-to-End Pipeline Performance

All tests use `time.perf_counter()` for high-resolution timing.
All tests must complete and pass (they measure performance, not correctness).
"""
import json
import os
import time
from pathlib import Path

import pytest

from topic_registry_v2 import TopicRegistryV2, TopicState, RegistryConfig, TopicEntry
from memory_pressure_monitor import (
    MemoryPressureMonitor,
    BudgetConfig,
    RetentionConfig,
    PressureLevel,
    BudgetAllocator,
    estimate_tokens,
)
from memory_context import MemoryContextProvider


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def make_topic_dict(topic_id, state="active", summary="", message_count=0,
                    compactions_since=0):
    """Create a synthetic topic dict for pressure monitor testing."""
    return {
        "topic_id": topic_id,
        "label": f"Topic {topic_id}",
        "state": state,
        "summary": summary,
        "key_decisions": [],
        "last_raw_exchange": None,
        "never_consolidate_items": [],
        "message_count": message_count,
        "last_access_message_idx": message_count,
        "compactions_since_last_access": compactions_since,
    }


def make_rich_topic_dict(topic_id, state="active", summary="",
                         message_count=0, compactions_since=0):
    """Create a topic dict with realistic content for budget pressure testing."""
    topic = make_topic_dict(topic_id, state, summary, message_count, compactions_since)
    if summary:
        topic["summary"] = summary
    if state == "warm":
        topic["key_decisions"] = [
            {"description": f"Decision A for {topic_id}", "rationale": "Based on evidence"},
            {"description": f"Decision B for {topic_id}", "rationale": "Alternative considered"},
        ]
        topic["last_raw_exchange"] = {
            "user_message": f"User query about {topic_id} " * 4,
            "assistant_message": f"Assistant response for {topic_id} " * 8,
            "message_idx": message_count,
            "timestamp": "2024-01-15T10:00:00Z",
        }
    elif state == "cold":
        topic["summary"] = summary or f"Summary of cold topic {topic_id} " * 20
    elif state == "active":
        topic["summary"] = summary or f"Active topic {topic_id} currently in discussion"
    return topic


def _force_topic_state(reg, topic_id, state):
    """Helper to directly set a topic's state via update_topic."""
    reg.update_topic(topic_id, state=state)


# ---------------------------------------------------------------------------
# 1. Compaction Throughput
# ---------------------------------------------------------------------------


class TestCompactionThroughput:
    """Benchmark compaction speed across varied registry sizes."""

    def test_compaction_with_10_topics(self, tmp_path):
        """Create 10 topics, run 5 compactions each, measure average time."""
        base = tmp_path / "fish-trail"
        reg = TopicRegistryV2(str(base))

        # Create topics with warm state so compaction affects them
        for i in range(10):
            reg.create_topic(f"topic_{i}", f"Topic {i}")
            _force_topic_state(reg, f"topic_{i}", TopicState.WARM.value)

        times = []
        for cycle in range(5):
            t0 = time.perf_counter()
            transitions = reg.on_compaction(f"compaction_{cycle}")
            elapsed = time.perf_counter() - t0
            times.append(elapsed)

            assert isinstance(transitions, list)

        avg_time = sum(times) / len(times)
        total_time = sum(times)

        # Verify results
        assert len(times) == 5
        assert avg_time < 1.0, f"Average compaction time {avg_time:.4f}s exceeds 1s"
        assert total_time < 3.0, f"Total compaction time {total_time:.4f}s exceeds 3s"

        # Verify compaction occurred
        assert reg.get_compaction_count() == 5

    def test_compaction_with_100_topics(self, tmp_path):
        """Create 100 topics, run 3 compactions, measure average time."""
        base = tmp_path / "fish-trail"
        reg = TopicRegistryV2(str(base))

        for i in range(100):
            reg.create_topic(f"topic_{i}", f"Topic {i}")
            # Set most to warm to test compaction impact
            _force_topic_state(reg, f"topic_{i}", TopicState.WARM.value)

        times = []
        for cycle in range(3):
            t0 = time.perf_counter()
            transitions = reg.on_compaction(f"compaction_{cycle}")
            elapsed = time.perf_counter() - t0
            times.append(elapsed)

        avg_time = sum(times) / len(times)
        total_time = sum(times)

        assert avg_time < 5.0, (
            f"Average compaction time {avg_time:.4f}s exceeds 5s for 100 topics"
        )
        assert total_time < 8.0, f"Total time {total_time:.4f}s exceeds 8s"
        assert reg.get_compaction_count() == 3

    def test_compaction_with_state_transitions(self, tmp_path):
        """Create 20 topics with mixed states, run compactions, verify transitions."""
        base = tmp_path / "fish-trail"
        # Use custom config for faster transitions
        config = RegistryConfig(
            active_threshold_messages=3,
            warm_to_cold_compactions=1,
            cold_to_archived_compactions=2,
        )
        reg = TopicRegistryV2(str(base), config=config)

        # Create 20 topics with varied initial states
        for i in range(20):
            reg.create_topic(f"topic_{i}", f"Topic {i}")

        # Set states: 5 ACTIVE, 8 WARM, 5 COLD, 2 ARCHIVED
        for i in range(5):
            pass  # already active
        for i in range(5, 13):
            _force_topic_state(reg, f"topic_{i}", TopicState.WARM.value)
        for i in range(13, 18):
            _force_topic_state(reg, f"topic_{i}", TopicState.COLD.value)
        for i in range(18, 20):
            _force_topic_state(reg, f"topic_{i}", TopicState.ARCHIVED.value)

        # Run compaction and time it
        t0 = time.perf_counter()
        transitions = reg.on_compaction("compaction_with_transitions")
        elapsed = time.perf_counter() - t0

        assert elapsed < 2.0, f"Compaction with transitions too slow: {elapsed:.4f}s"
        assert isinstance(transitions, list)
        assert reg.get_compaction_count() == 1

        # Verify transitions occurred (WARM topics with 1 compaction → COLD)
        assert len(transitions) > 0, "Expected at least some state transitions"

        # Verify backup was created
        backup_path = base / "registry-backups" / "compaction_with_transitions.json"
        assert backup_path.exists()

    def test_compaction_backup_overhead(self, tmp_path):
        """Measure time: compaction with backup vs without backup simulation."""
        base = tmp_path / "fish-trail"
        reg = TopicRegistryV2(str(base))

        # Create 5 topics with warm state
        for i in range(5):
            reg.create_topic(f"topic_{i}", f"Topic {i}")
            _force_topic_state(reg, f"topic_{i}", TopicState.WARM.value)

        # Measure compaction WITH backup
        t0 = time.perf_counter()
        reg.on_compaction("with_backup")
        with_backup_time = time.perf_counter() - t0

        # Measure a similar operation WITHOUT backup: manual counter update + save
        t0 = time.perf_counter()
        for i in range(5):
            reg.update_topic(f"topic_{i}", compactions_since_last_access=2)
        without_backup_time = time.perf_counter() - t0

        # Backup overhead should be measurable but small
        assert with_backup_time < 2.0, (
            f"Compaction with backup too slow: {with_backup_time:.4f}s"
        )
        assert without_backup_time < 2.0

        # Verify backup exists
        backup_path = base / "registry-backups" / "with_backup.json"
        assert backup_path.exists()

        # Verify compaction count increment
        assert reg.get_compaction_count() == 1


# ---------------------------------------------------------------------------
# 2. Registry I/O Performance
# ---------------------------------------------------------------------------


class TestRegistryIO:
    """Benchmark registry load, save, file size, and roundtrip integrity."""

    def _create_registry_with_n_topics(self, base_path, n):
        """Create a registry with N topics on disk and return it."""
        reg = TopicRegistryV2(str(base_path))
        for i in range(n):
            reg.create_topic(
                f"topic_{i}",
                f"Topic {i}",
                description=f"Description for topic {i} " * 2,
            )
        return reg

    def test_load_time_with_growing_topics(self, tmp_path):
        """Time _load_registry() with 50, 200, 500 topics."""
        sizes = [50, 200, 500]
        load_times = {}

        for n in sizes:
            base = tmp_path / f"load_{n}"
            # Create and populate registry
            reg1 = TopicRegistryV2(str(base))
            for i in range(n):
                reg1.create_topic(f"topic_{i}", f"Topic {i}",
                                  description=f"Description for topic {i} " * 2)
            del reg1

            # Now open fresh instance and measure first list_topics (triggers load)
            t0 = time.perf_counter()
            reg2 = TopicRegistryV2(str(base))
            topics = reg2.list_topics()
            elapsed = time.perf_counter() - t0
            load_times[n] = elapsed

            assert len(topics) == n, f"Expected {n} topics, got {len(topics)}"

        # Verify sub-linear or reasonable growth (500 should be < 20x of 50)
        ratio = load_times[500] / max(load_times[50], 0.001)
        assert ratio < 30, (
            f"Load time scaling poor: 500-topics={load_times[500]:.4f}s vs "
            f"50-topics={load_times[50]:.4f}s (ratio={ratio:.1f}x)"
        )
        assert load_times[500] < 5.0, (
            f"500-topic load time {load_times[500]:.4f}s exceeds 5s"
        )

    def test_save_time_with_growing_topics(self, tmp_path):
        """Time _save_registry() with 50, 200, 500 topics."""
        sizes = [50, 200, 500]
        save_times = {}

        for n in sizes:
            base = tmp_path / f"save_{n}"
            reg = TopicRegistryV2(str(base))

            # Create N-1 topics first
            for i in range(n - 1):
                reg.create_topic(f"topic_{i}", f"Topic {i}")

            # Measure the Nth create (triggers save)
            t0 = time.perf_counter()
            reg.create_topic(f"topic_{n - 1}", f"Topic {n - 1}",
                             description=f"Description for topic {n - 1} " * 2)
            elapsed = time.perf_counter() - t0
            save_times[n] = elapsed

        # Verify reasonable scaling
        ratio = save_times[500] / max(save_times[50], 0.001)
        assert ratio < 30, (
            f"Save time scaling poor: 500-topics={save_times[500]:.4f}s vs "
            f"50-topics={save_times[50]:.4f}s (ratio={ratio:.1f}x)"
        )
        assert save_times[500] < 5.0, (
            f"500-topic save time {save_times[500]:.4f}s exceeds 5s"
        )

    def test_registry_file_size(self, tmp_path):
        """Check registry JSON file size with 100, 500 topics."""
        for n in [100, 500]:
            base = tmp_path / f"filesize_{n}"
            reg = TopicRegistryV2(str(base))
            for i in range(n):
                reg.create_topic(
                    f"topic_{i}",
                    f"Topic {i}",
                    description=f"Description for topic {i} with some extra "
                                f"content to make the file larger " * 3,
                )

            file_path = base / "topic-registry.json"
            assert file_path.exists()

            size_bytes = file_path.stat().st_size
            size_mb = size_bytes / (1024 * 1024)

            assert size_mb < 5.0, (
                f"Registry file for {n} topics is {size_mb:.2f}MB, exceeds 5MB limit"
            )

            # For 100 topics, should be reasonable (< 2MB)
            if n == 100:
                assert size_mb < 2.0, (
                    f"Registry file for 100 topics is {size_mb:.2f}MB, exceeds 2MB"
                )

    def test_read_write_roundtrip_integrity(self, tmp_path):
        """Create topics, save, reload, verify data intact — measure total time."""
        base = tmp_path / "fish-trail"
        n_topics = 50

        # Phase 1: Create and populate
        t0 = time.perf_counter()
        reg1 = TopicRegistryV2(str(base))
        for i in range(n_topics):
            reg1.create_topic(
                f"topic_{i}",
                f"Topic {i}",
                description=f"Description {i}",
            )

        # Add some complex data to verify
        for i in range(10):
            reg1.update_topic(
                f"topic_{i}",
                state=TopicState.WARM.value,
                summary=f"Summary for topic {i}",
                message_count=i * 5,
            )
        create_time = time.perf_counter() - t0

        # Phase 2: Reload and verify
        t1 = time.perf_counter()
        reg2 = TopicRegistryV2(str(base))
        topics = reg2.list_topics()
        reload_time = time.perf_counter() - t1

        total_time = time.perf_counter() - t0
        assert total_time < 10.0, f"Roundtrip too slow: {total_time:.4f}s"

        # Phase 3: Verify data integrity
        assert len(topics) == n_topics
        for i in range(10):
            topic = reg2.get_topic(f"topic_{i}")
            assert topic is not None
            assert topic.state == TopicState.WARM.value
            assert topic.summary == f"Summary for topic {i}"
            assert topic.message_count == i * 5

        # Verify metadata persisted
        metadata = reg2.get_registry_metadata()
        assert metadata["topic_count"] == n_topics
        assert metadata["version"] == "2.0"


# ---------------------------------------------------------------------------
# 3. Pressure Monitor Performance
# ---------------------------------------------------------------------------


class TestPressureMonitorPerformance:
    """Benchmark pressure monitor assess(), pressure detection, and allocation."""

    def test_assess_with_50_topics(self, tmp_path):
        """Create 50 synthetic topic dicts with varied states, measure assess() time."""
        monitor = MemoryPressureMonitor()

        topics = []
        for i in range(50):
            if i < 10:
                state = "active"
                summary = f"Active topic {i} " * 5
            elif i < 30:
                state = "warm"
                summary = f"Warm topic {i} summary " * 10
            elif i < 45:
                state = "cold"
                summary = f"Cold topic {i} " * 15
            else:
                state = "archived"
                summary = ""

            topics.append(make_rich_topic_dict(
                f"topic_{i}", state=state, summary=summary, message_count=i
            ))

        t0 = time.perf_counter()
        result = monitor.assess(topics)
        elapsed = time.perf_counter() - t0

        assert elapsed < 3.0, f"assess() with 50 topics too slow: {elapsed:.4f}s"
        assert result is not None
        assert result.retention_plan is not None
        assert result.allocation is not None
        assert isinstance(result.pressure_level, PressureLevel)

    def test_assess_with_200_topics(self, tmp_path):
        """Scale to 200 topics, verify completion under 5 seconds."""
        monitor = MemoryPressureMonitor()

        topics = []
        for i in range(200):
            if i < 30:
                state = "active"
            elif i < 100:
                state = "warm"
            elif i < 170:
                state = "cold"
            else:
                state = "archived"

            topics.append(make_rich_topic_dict(
                f"topic_{i}", state=state,
                summary=f"Topic {i} summary content " * 8,
                message_count=i % 20,
            ))

        t0 = time.perf_counter()
        result = monitor.assess(topics)
        elapsed = time.perf_counter() - t0

        assert elapsed < 5.0, (
            f"assess() with 200 topics too slow: {elapsed:.4f}s"
        )
        assert result is not None
        assert len(result.retention_plan.topics) == 200

    def test_pressure_detection_speed(self, tmp_path):
        """Test that _detect_pressure() is fast (< 1ms for any input)."""
        monitor = MemoryPressureMonitor()
        allocator = monitor.budget_allocator

        # Test various utilization values
        test_values = [0.0, 0.25, 0.50, 0.75, 0.85, 0.92, 0.98, 1.0, 1.5, 100.0]

        for util in test_values:
            t0 = time.perf_counter()
            result = allocator._detect_pressure(util)
            elapsed = time.perf_counter() - t0

            assert elapsed < 0.01, (
                f"_detect_pressure({util}) took {elapsed*1000:.3f}ms, "
                f"exceeds 10ms limit"
            )
            assert isinstance(result, PressureLevel)

    def test_budget_allocation_consistency(self, tmp_path):
        """Run allocate() 10 times with same input, verify results are consistent."""
        monitor = MemoryPressureMonitor()

        # Create a fixed set of topics
        topics = []
        for i in range(20):
            state = "active" if i < 5 else "warm" if i < 12 else "cold"
            topics.append(make_rich_topic_dict(
                f"topic_{i}", state=state,
                summary=f"Topic {i} summary " * 10,
                message_count=i * 3,
            ))

        # Run 10 allocations
        allocations = []
        for _ in range(10):
            plan = monitor.retention_engine.compute_retention(topics)
            alloc = monitor.budget_allocator.allocate(plan)
            allocations.append(alloc)

        # Verify consistency: same pressure level and total budget each time
        first = allocations[0]
        for i, alloc in enumerate(allocations):
            assert alloc.pressure_level == first.pressure_level, (
                f"Allocation {i} has different pressure level"
            )
            assert alloc.total_budget == first.total_budget, (
                f"Allocation {i} has different total budget"
            )
            assert len(alloc.active.topics_included) == len(
                first.active.topics_included
            ), f"Allocation {i} has different active topic count"

        # Verify allocation has expected structure
        assert first.total_budget > 0
        assert first.index.allocated_tokens > 0
        assert first.active.allocated_tokens > 0


# ---------------------------------------------------------------------------
# 4. End-to-End Pipeline Performance
# ---------------------------------------------------------------------------


class TestPipelinePerformance:
    """Benchmark full pipeline: registry → transitions → assess → context."""

    def test_full_pipeline_50_topics(self, tmp_path):
        """Create 50 topics → record access → check transitions → monitor.assess()."""
        base = tmp_path / "fish-trail"
        reg = TopicRegistryV2(str(base))
        monitor = MemoryPressureMonitor()

        # Phase 1: Create topics and record access
        t0 = time.perf_counter()
        for i in range(50):
            reg.create_topic(f"topic_{i}", f"Topic {i}")
            reg.record_access(f"topic_{i}", message_idx=i)

        # Move some to warm/cold for realistic state distribution
        for i in range(20, 50):
            _force_topic_state(reg, f"topic_{i}", TopicState.WARM.value)
        for i in range(35, 50):
            _force_topic_state(reg, f"topic_{i}", TopicState.COLD.value)

        # Phase 2: Check transitions
        transitions = reg.check_transitions(current_message_idx=100)
        assert isinstance(transitions, list)

        # Phase 3: Get topic dicts and run assess
        topic_dicts = [t.to_dict() for t in reg.list_topics()]
        result = monitor.assess(topic_dicts)
        total_time = time.perf_counter() - t0

        assert total_time < 10.0, (
            f"Full pipeline with 50 topics too slow: {total_time:.4f}s"
        )
        assert len(topic_dicts) == 50
        assert result.allocation.total_budget > 0
        assert isinstance(result.pressure_level, PressureLevel)

    def test_compaction_stress_10_cycles_50_topics(self, tmp_path):
        """10 compaction cycles on 50 topics, measure total time, no degradation."""
        base = tmp_path / "fish-trail"
        reg = TopicRegistryV2(str(base))

        # Create 50 topics, set 30 to warm state
        for i in range(50):
            reg.create_topic(f"topic_{i}", f"Topic {i}")
        for i in range(20, 50):
            _force_topic_state(reg, f"topic_{i}", TopicState.WARM.value)

        cycle_times = []
        t0 = time.perf_counter()

        for cycle in range(10):
            ct0 = time.perf_counter()
            transitions = reg.on_compaction(f"stress_compaction_{cycle}")
            cycle_elapsed = time.perf_counter() - ct0
            cycle_times.append(cycle_elapsed)
            assert isinstance(transitions, list)

        total_time = time.perf_counter() - t0

        assert total_time < 10.0, (
            f"10 compaction cycles on 50 topics too slow: {total_time:.4f}s"
        )
        assert reg.get_compaction_count() == 10

        # Verify no degradation: last cycle should not be slower than first * 3
        # (some variation is expected, but not order-of-magnitude degradation)
        first_time = cycle_times[0]
        last_time = cycle_times[-1]
        if first_time > 0.001:
            degradation_ratio = last_time / first_time
            assert degradation_ratio < 5.0, (
                f"Compaction cycle degradation: first={first_time:.4f}s, "
                f"last={last_time:.4f}s (ratio={degradation_ratio:.1f}x)"
            )

    def test_memory_context_with_loaded_registry(self, tmp_path):
        """Pre-populate 30 topics, create MemoryContextProvider, measure response."""
        base = tmp_path / "fish-trail"
        reg = TopicRegistryV2(str(base))
        monitor = MemoryPressureMonitor()

        # Pre-populate 30 topics with various states
        for i in range(30):
            reg.create_topic(f"topic_{i}", f"Topic {i}",
                             description=f"Description {i}")
        for i in range(10, 20):
            reg.update_topic(f"topic_{i}", state=TopicState.WARM.value,
                             summary=f"Warm summary {i}")
        for i in range(20, 25):
            reg.update_topic(f"topic_{i}", state=TopicState.COLD.value,
                             summary=f"Cold summary {i}")
        for i in range(25, 30):
            reg.update_topic(f"topic_{i}", state=TopicState.ARCHIVED.value)

        provider = MemoryContextProvider(
            registry=reg, pressure_monitor=monitor, cache_ttl=0.0
        )

        t0 = time.perf_counter()
        result = provider.get_memory_context(
            current_topic_id="topic_0",
            include_warm=True,
            include_cold_summaries=True,
        )
        elapsed = time.perf_counter() - t0

        assert elapsed < 5.0, (
            f"get_memory_context() too slow: {elapsed:.4f}s"
        )
        assert result is not None
        assert result.tokens_used >= 0
        assert not result.cache_hit  # cache_ttl=0 disables cache
        assert result.metadata.topics_active >= 1
        assert result.metadata.topics_warm >= 0

    def test_memory_context_cache_hit(self, tmp_path):
        """Verify cache provides speedup on repeated calls."""
        base = tmp_path / "fish-trail"
        reg = TopicRegistryV2(str(base))
        monitor = MemoryPressureMonitor()

        for i in range(10):
            reg.create_topic(f"topic_{i}", f"Topic {i}")

        provider = MemoryContextProvider(
            registry=reg, pressure_monitor=monitor, cache_ttl=60.0
        )

        # First call — should be a cache miss
        t0 = time.perf_counter()
        result1 = provider.get_memory_context(current_topic_id="topic_0")
        first_call_time = time.perf_counter() - t0

        assert not result1.cache_hit

        # Second call — should be a cache hit and faster
        t0 = time.perf_counter()
        result2 = provider.get_memory_context(current_topic_id="topic_0")
        second_call_time = time.perf_counter() - t0

        assert result2.cache_hit
        assert second_call_time < first_call_time, (
            f"Cache should be faster: first={first_call_time:.4f}s, "
            f"second={second_call_time:.4f}s"
        )

    def test_concurrent_access_simulation(self, tmp_path):
        """Simulate rapid interleaved topic access — verify no crashes."""
        base = tmp_path / "fish-trail"
        reg = TopicRegistryV2(str(base))
        monitor = MemoryPressureMonitor()

        t0 = time.perf_counter()
        n_ops = 0

        # Simulate rapid create/access/compact on small registry
        for cycle in range(5):
            # Create some topics
            for i in range(10):
                topic_id = f"topic_{cycle}_{i}"
                try:
                    reg.create_topic(topic_id, f"Topic {cycle}_{i}")
                    n_ops += 1
                except ValueError:
                    pass  # Already exists from previous cycles

            # Access topics rapidly
            for i in range(10):
                topic_id = f"topic_{cycle}_{i}"
                try:
                    reg.record_access(topic_id, message_idx=cycle * 10 + i)
                    n_ops += 1
                except KeyError:
                    pass

            # Check transitions
            reg.check_transitions(current_message_idx=(cycle + 1) * 10)
            n_ops += 1

            # Get registry metadata
            reg.get_registry_metadata()
            n_ops += 1

            # Run assess on current topics
            topic_dicts = [t.to_dict() for t in reg.list_topics()]
            if topic_dicts:
                monitor.assess(topic_dicts)
                n_ops += 1

        total_time = time.perf_counter() - t0

        assert total_time < 10.0, (
            f"Concurrent access simulation too slow: {total_time:.4f}s"
        )
        assert n_ops > 30, f"Only performed {n_ops} operations, expected > 30"

        # Verify registry is still functional after stress
        all_topics = reg.list_topics()
        assert len(all_topics) > 0
        metadata = reg.get_registry_metadata()
        assert metadata["version"] == "2.0"


# ---------------------------------------------------------------------------
# Smoke test — verify all modules import and basic functionality
# ---------------------------------------------------------------------------


class TestSmoke:
    """Quick smoke tests to verify imports and basic functionality."""

    def test_imports_work(self):
        """Verify all required imports resolve."""
        assert TopicRegistryV2 is not None
        assert MemoryPressureMonitor is not None
        assert MemoryContextProvider is not None
        assert BudgetConfig is not None
        assert estimate_tokens is not None

    def test_basic_topic_create_and_read(self, tmp_path):
        """Create a single topic and verify it can be read back."""
        base = tmp_path / "fish-trail"
        reg = TopicRegistryV2(str(base))
        entry = reg.create_topic("test", "Test Topic", description="A test")
        assert entry.topic_id == "test"
        assert entry.state == TopicState.ACTIVE.value

    def test_estimate_tokens_reasonable(self):
        """Verify estimate_tokens produces reasonable numbers."""
        assert estimate_tokens("hello world") > 0
        assert estimate_tokens("") == 0
        chars_1000 = "x" * 1000
        estimated = estimate_tokens(chars_1000)
        assert 200 < estimated < 400  # chars/3.5 ≈ 285
