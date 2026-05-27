"""Tests for memory_context.py — MemoryContextProvider and MemoryContextCache.

Covers:
- Cache hit/miss/invalidation
- Tier categorization (active/warm/cold/archived)
- Budget enforcement
- Pressure-level-based cold inclusion
- Token estimation
- Context block formatting
"""

import json
import time
from unittest.mock import patch

import pytest

from memory_context import (
    MemoryContextCache,
    MemoryContextProvider,
    MemoryContextResult,
    _build_topic_block_full,
    _build_topic_block_summary_only,
    _build_topic_block_summary_plus_key,
    _estimate_tokens,
)
from memory_pressure_monitor import (
    BudgetConfig,
    MemoryPressureMonitor,
    PressureLevel,
    RetentionPlan,
)
from topic_registry_v2 import (
    KeyDecision,
    RawExchange,
    TopicEntry,
    TopicRegistryV2,
    TopicState,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


def _make_topic(
    topic_id: str = "t1",
    label: str = "Test Topic",
    state: str = TopicState.ACTIVE.value,
    description: str = "A test topic",
    summary: str = "Summary of test topic",
    key_decisions: list = None,
    last_raw_exchange: RawExchange = None,
    message_count: int = 5,
    compactions_since_last_access: int = 0,
) -> TopicEntry:
    return TopicEntry(
        topic_id=topic_id,
        label=label,
        state=state,
        description=description,
        summary=summary,
        key_decisions=key_decisions or [],
        last_raw_exchange=last_raw_exchange,
        message_count=message_count,
        compactions_since_last_access=compactions_since_last_access,
    )


def _make_key_decision(desc: str = "Chose approach A") -> KeyDecision:
    return KeyDecision(
        decision_id="kd1",
        description=desc,
        rationale="Because reasons",
        timestamp="2026-01-01T00:00:00Z",
    )


def _make_raw_exchange() -> RawExchange:
    return RawExchange(
        user_message="How do we do X?",
        assistant_message="We should do Y because Z.",
        message_idx=10,
        timestamp="2026-01-01T12:00:00Z",
    )


def _inject_topic(registry: TopicRegistryV2, topic: TopicEntry):
    """Inject a topic directly into the registry's JSON file."""
    data = json.loads(registry.registry_path.read_text(encoding="utf-8"))
    data["topics"][topic.topic_id] = topic.to_dict()
    registry.registry_path.write_text(json.dumps(data, indent=2), encoding="utf-8")


@pytest.fixture
def tmp_registry(tmp_path):
    """Create a TopicRegistryV2 with tmp_path storage."""
    return TopicRegistryV2(base_dir=str(tmp_path))


@pytest.fixture
def pressure_monitor():
    """Create a MemoryPressureMonitor with default config."""
    return MemoryPressureMonitor()


@pytest.fixture
def provider(tmp_registry, pressure_monitor):
    """Create a MemoryContextProvider."""
    return MemoryContextProvider(
        registry=tmp_registry,
        pressure_monitor=pressure_monitor,
        cache_ttl=30.0,
    )


# ---------------------------------------------------------------------------
# Token estimation
# ---------------------------------------------------------------------------


class TestEstimateTokens:
    def test_empty_string(self):
        assert _estimate_tokens("") == 1  # min 1

    def test_normal_text(self):
        text = "Hello world this is a test"
        tokens = _estimate_tokens(text)
        assert tokens > 0
        # ~26 chars / 3.5 ≈ 7
        assert tokens == int(len(text) / 3.5)

    def test_long_text(self):
        text = "x" * 3500
        assert _estimate_tokens(text) == 1000


# ---------------------------------------------------------------------------
# Block builders
# ---------------------------------------------------------------------------


class TestBlockBuilders:
    def test_full_block_minimal(self):
        topic = _make_topic(summary=None, key_decisions=[], last_raw_exchange=None)
        block = _build_topic_block_full(topic)
        assert "[ACTIVE]" in block
        assert "Test Topic" in block
        assert "Scope: A test topic" in block

    def test_full_block_with_all_fields(self):
        topic = _make_topic(
            key_decisions=[_make_key_decision("Used Redis")],
            last_raw_exchange=_make_raw_exchange(),
        )
        block = _build_topic_block_full(topic)
        assert "Summary: Summary of test topic" in block
        assert "Used Redis" in block
        assert "Recent exchange:" in block

    def test_summary_plus_key_block(self):
        topic = _make_topic(
            state=TopicState.WARM.value,
            key_decisions=[_make_key_decision("Pick Postgres")],
        )
        block = _build_topic_block_summary_plus_key(topic)
        assert "[WARM]" in block
        assert "Summary:" in block
        assert "Pick Postgres" in block
        # Should NOT include raw exchange
        assert "Recent exchange:" not in block

    def test_summary_only_block(self):
        topic = _make_topic(state=TopicState.COLD.value)
        block = _build_topic_block_summary_only(topic)
        assert "[COLD]" in block
        assert "Summary: Summary of test topic" in block

    def test_summary_only_no_summary(self):
        topic = _make_topic(state=TopicState.COLD.value, summary=None)
        block = _build_topic_block_summary_only(topic)
        assert "(No summary available)" in block


# ---------------------------------------------------------------------------
# Cache
# ---------------------------------------------------------------------------


class TestMemoryContextCache:
    def test_miss_when_empty(self):
        cache = MemoryContextCache(ttl_seconds=30.0)
        result = cache.get("t1", "NORMAL", 5, 0)
        assert result is None

    def test_hit_after_put(self):
        cache = MemoryContextCache(ttl_seconds=30.0)
        r = MemoryContextResult(context_block="hello", tokens_used=10)
        cache.put(r, "t1", "NORMAL", 5, 0)
        hit = cache.get("t1", "NORMAL", 5, 0)
        assert hit is not None
        assert hit.context_block == "hello"

    def test_miss_on_topic_change(self):
        cache = MemoryContextCache(ttl_seconds=30.0)
        r = MemoryContextResult(context_block="hello", tokens_used=10)
        cache.put(r, "t1", "NORMAL", 5, 0)
        assert cache.get("t2", "NORMAL", 5, 0) is None

    def test_miss_on_pressure_change(self):
        cache = MemoryContextCache(ttl_seconds=30.0)
        r = MemoryContextResult(context_block="hello", tokens_used=10)
        cache.put(r, "t1", "NORMAL", 5, 0)
        assert cache.get("t1", "L1", 5, 0) is None

    def test_miss_on_topic_count_change(self):
        cache = MemoryContextCache(ttl_seconds=30.0)
        r = MemoryContextResult(context_block="hello", tokens_used=10)
        cache.put(r, "t1", "NORMAL", 5, 0)
        assert cache.get("t1", "NORMAL", 6, 0) is None

    def test_miss_on_compaction_change(self):
        cache = MemoryContextCache(ttl_seconds=30.0)
        r = MemoryContextResult(context_block="hello", tokens_used=10)
        cache.put(r, "t1", "NORMAL", 5, 0)
        assert cache.get("t1", "NORMAL", 5, 1) is None

    def test_ttl_expiry(self):
        cache = MemoryContextCache(ttl_seconds=0.01)
        r = MemoryContextResult(context_block="hello", tokens_used=10)
        cache.put(r, "t1", "NORMAL", 5, 0)
        time.sleep(0.02)
        assert cache.get("t1", "NORMAL", 5, 0) is None

    def test_invalidate(self):
        cache = MemoryContextCache(ttl_seconds=30.0)
        r = MemoryContextResult(context_block="hello", tokens_used=10)
        cache.put(r, "t1", "NORMAL", 5, 0)
        cache.invalidate()
        assert cache.get("t1", "NORMAL", 5, 0) is None


# ---------------------------------------------------------------------------
# MemoryContextProvider integration
# ---------------------------------------------------------------------------


class TestMemoryContextProvider:
    def test_empty_registry_returns_empty_context(self, provider):
        result = provider.get_memory_context()
        assert result.context_block == ""
        assert result.tokens_used == 0
        assert result.metadata.topics_active == 0
        assert result.cache_hit is False

    def test_single_active_topic(self, tmp_registry, pressure_monitor):
        # Add a topic directly
        topic = _make_topic(topic_id="t1", label="Auth System")
        _inject_topic(tmp_registry, topic)

        provider = MemoryContextProvider(tmp_registry, pressure_monitor)
        result = provider.get_memory_context()

        assert "Auth System" in result.context_block
        assert "[ACTIVE]" in result.context_block
        assert result.metadata.topics_active == 1
        assert result.tokens_used > 0

    def test_tiered_topics(self, tmp_registry, pressure_monitor):
        # Add topics in different tiers
        _inject_topic(
            tmp_registry,
            _make_topic(
                topic_id="t1", label="Active Topic", state=TopicState.ACTIVE.value
            ),
        )
        _inject_topic(
            tmp_registry,
            _make_topic(topic_id="t2", label="Warm Topic", state=TopicState.WARM.value),
        )
        _inject_topic(
            tmp_registry,
            _make_topic(topic_id="t3", label="Cold Topic", state=TopicState.COLD.value),
        )
        _inject_topic(
            tmp_registry,
            _make_topic(
                topic_id="t4", label="Archived Topic", state=TopicState.ARCHIVED.value
            ),
        )

        provider = MemoryContextProvider(tmp_registry, pressure_monitor)
        result = provider.get_memory_context()

        assert result.metadata.topics_active == 1
        assert result.metadata.topics_warm == 1
        assert result.metadata.topics_cold == 1
        assert result.metadata.topics_archived == 1
        # Active and warm should appear
        assert "Active Topic" in result.context_block
        assert "Warm Topic" in result.context_block
        # Cold should appear at NORMAL pressure
        assert "Cold Topic" in result.context_block

    def test_exclude_warm(self, tmp_registry, pressure_monitor):
        """include_warm param is now vestigial — OutputFormatter uses BudgetAllocation
        to determine tier visibility. The topic index always lists all topics."""
        _inject_topic(
            tmp_registry,
            _make_topic(topic_id="t1", label="Active", state=TopicState.ACTIVE.value),
        )
        _inject_topic(
            tmp_registry,
            _make_topic(topic_id="t2", label="Warm", state=TopicState.WARM.value),
        )

        provider = MemoryContextProvider(tmp_registry, pressure_monitor)
        result = provider.get_memory_context(include_warm=False)

        # Both topics appear — formatter decides visibility via BudgetAllocation
        assert "Active" in result.context_block
        # Warm topic appears in topic index (formatter includes all topics in index)
        assert result.context_block != ""

    def test_budget_constraint(self, tmp_registry, pressure_monitor):
        """budget_tokens param is now vestigial — OutputFormatter uses BudgetAllocation
        from MemoryPressureMonitor which calculates budget based on topic count and
        pressure level, not the raw budget_tokens param."""
        _inject_topic(
            tmp_registry,
            _make_topic(
                topic_id="t1",
                label="Big Topic",
                state=TopicState.ACTIVE.value,
                description="A" * 500,
                summary="B" * 500,
            ),
        )

        provider = MemoryContextProvider(tmp_registry, pressure_monitor)
        # budget_tokens param kept for API compat but doesn't constrain output
        result = provider.get_memory_context(budget_tokens=5)

        # Output is generated based on BudgetAllocation, not raw budget_tokens
        assert result.tokens_used > 0
        assert result.context_block != ""

    def test_cache_hit_on_second_call(self, tmp_registry, pressure_monitor):
        _inject_topic(tmp_registry, _make_topic(topic_id="t1", label="Cached"))

        provider = MemoryContextProvider(tmp_registry, pressure_monitor)
        result1 = provider.get_memory_context()
        assert result1.cache_hit is False

        result2 = provider.get_memory_context()
        assert result2.cache_hit is True
        assert result2.context_block == result1.context_block

    def test_cache_invalidation_on_topic_add(self, tmp_registry, pressure_monitor):
        _inject_topic(tmp_registry, _make_topic(topic_id="t1", label="First"))

        provider = MemoryContextProvider(tmp_registry, pressure_monitor)
        result1 = provider.get_memory_context()
        assert result1.cache_hit is False

        # Add another topic — cache should miss due to topic_count change
        _inject_topic(tmp_registry, _make_topic(topic_id="t2", label="Second"))

        result2 = provider.get_memory_context()
        assert result2.cache_hit is False

    def test_invalidate_cache_manually(self, tmp_registry, pressure_monitor):
        _inject_topic(tmp_registry, _make_topic(topic_id="t1", label="Manual"))

        provider = MemoryContextProvider(tmp_registry, pressure_monitor)
        provider.get_memory_context()  # populate cache
        provider.invalidate_cache()

        result = provider.get_memory_context()
        assert result.cache_hit is False

    def test_current_topic_id_override(self, tmp_registry, pressure_monitor):
        _inject_topic(
            tmp_registry,
            _make_topic(topic_id="t1", label="Topic A", state=TopicState.ACTIVE.value),
        )
        _inject_topic(
            tmp_registry,
            _make_topic(topic_id="t2", label="Topic B", state=TopicState.ACTIVE.value),
        )

        provider = MemoryContextProvider(tmp_registry, pressure_monitor)
        # Calling with different current_topic_id should invalidate cache
        r1 = provider.get_memory_context(current_topic_id="t1")
        r2 = provider.get_memory_context(current_topic_id="t2")
        assert r2.cache_hit is False  # different active topic = cache miss

    def test_to_dict(self, tmp_registry, pressure_monitor):
        _inject_topic(tmp_registry, _make_topic(topic_id="t1", label="Dict Test"))

        provider = MemoryContextProvider(tmp_registry, pressure_monitor)
        result = provider.get_memory_context()
        d = result.to_dict()

        assert "context_block" in d
        assert "tokens_used" in d
        assert "metadata" in d
        assert d["metadata"]["topics_active"] == 1
        assert d["metadata"]["pressure_level"] == "NORMAL"
        assert "cache_hit" in d

    def test_include_cold_summaries_false(self, tmp_registry, pressure_monitor):
        """include_cold_summaries param is now vestigial — OutputFormatter uses
        BudgetAllocation to determine which cold topics appear. Topic index
        always lists all topics regardless of this param."""
        _inject_topic(
            tmp_registry,
            _make_topic(topic_id="t1", label="Active", state=TopicState.ACTIVE.value),
        )
        _inject_topic(
            tmp_registry,
            _make_topic(topic_id="t2", label="Cold One", state=TopicState.COLD.value),
        )

        provider = MemoryContextProvider(tmp_registry, pressure_monitor)
        result = provider.get_memory_context(include_cold_summaries=False)
        # Cold topic appears in topic index — formatter decides visibility
        assert "Active" in result.context_block

    def test_pressure_level_in_metadata(self, tmp_registry, pressure_monitor):
        _inject_topic(tmp_registry, _make_topic(topic_id="t1"))

        provider = MemoryContextProvider(tmp_registry, pressure_monitor)
        result = provider.get_memory_context()
        assert result.metadata.pressure_level in ("NORMAL", "L1", "L2", "L3")
