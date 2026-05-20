"""get_memory_context() implementation for Fish Trail Tiered Memory v2.

Provides the primary MCP integration point that assembles a context block
from topics across tiers (active/warm/cold/archived), respecting token budgets
and pressure levels.

Spec reference: §6.1 of 03-product-spec-tiered-memory.md
"""

import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from topic_registry_v2 import TopicEntry, TopicRegistryV2, TopicState
from memory_pressure_monitor import (
    MemoryPressureMonitor,
    PressureLevel,
)


# ---------------------------------------------------------------------------
# Data types
# ---------------------------------------------------------------------------


@dataclass
class MemoryContextMetadata:
    """Metadata about the assembled context."""

    topics_active: int = 0
    topics_warm: int = 0
    topics_cold: int = 0
    topics_archived: int = 0
    pressure_level: str = "NORMAL"


@dataclass
class MemoryContextResult:
    """Result of get_memory_context() call."""

    context_block: str
    tokens_used: int
    metadata: MemoryContextMetadata = field(default_factory=MemoryContextMetadata)
    cache_hit: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "context_block": self.context_block,
            "tokens_used": self.tokens_used,
            "metadata": {
                "topics_active": self.metadata.topics_active,
                "topics_warm": self.metadata.topics_warm,
                "topics_cold": self.metadata.topics_cold,
                "topics_archived": self.metadata.topics_archived,
                "pressure_level": self.metadata.pressure_level,
            },
            "cache_hit": self.cache_hit,
        }


# ---------------------------------------------------------------------------
# Cache
# ---------------------------------------------------------------------------


@dataclass
class _CacheEntry:
    """Session-scoped cache entry."""

    result: MemoryContextResult
    created_at: float
    # Invalidation keys
    active_topic_id: Optional[str]
    pressure_level: str
    topic_count: int
    last_compaction_counter: int


class MemoryContextCache:
    """Simple session-scoped cache with invalidation on state change.

    Invalidation triggers:
    - Topic switch (active_topic_id changed)
    - Compaction event (compaction_counter changed)
    - Pressure level change
    - Topic count change (topic created/archived)
    - TTL expiry (default 30s)
    """

    def __init__(self, ttl_seconds: float = 30.0):
        self._entry: Optional[_CacheEntry] = None
        self._ttl = ttl_seconds

    def get(
        self,
        active_topic_id: Optional[str],
        pressure_level: str,
        topic_count: int,
        last_compaction_counter: int,
    ) -> Optional[MemoryContextResult]:
        """Return cached result if still valid, else None."""
        if self._entry is None:
            return None

        e = self._entry

        # TTL check
        if (time.time() - e.created_at) > self._ttl:
            self._entry = None
            return None

        # Invalidation checks
        if e.active_topic_id != active_topic_id:
            self._entry = None
            return None
        if e.pressure_level != pressure_level:
            self._entry = None
            return None
        if e.topic_count != topic_count:
            self._entry = None
            return None
        if e.last_compaction_counter != last_compaction_counter:
            self._entry = None
            return None

        return e.result

    def put(
        self,
        result: MemoryContextResult,
        active_topic_id: Optional[str],
        pressure_level: str,
        topic_count: int,
        last_compaction_counter: int,
    ) -> None:
        """Store a result in the cache."""
        self._entry = _CacheEntry(
            result=result,
            created_at=time.time(),
            active_topic_id=active_topic_id,
            pressure_level=pressure_level,
            topic_count=topic_count,
            last_compaction_counter=last_compaction_counter,
        )

    def invalidate(self) -> None:
        """Force-clear the cache."""
        self._entry = None


# ---------------------------------------------------------------------------
# Context block builder
# ---------------------------------------------------------------------------


def _estimate_tokens(text: str) -> int:
    """Quick token estimate: ~3.5 chars per token."""
    return max(1, int(len(text) / 3.5))


def _build_topic_block_full(topic: TopicEntry) -> str:
    """Build full context block for an ACTIVE topic."""
    lines: List[str] = []
    lines.append(f"## [{topic.state.upper()}] {topic.label}")
    if topic.description:
        lines.append(f"Scope: {topic.description}")
    if topic.summary:
        lines.append(f"Summary: {topic.summary}")
    if topic.key_decisions:
        lines.append("Key decisions:")
        for kd in topic.key_decisions:
            lines.append(f"  - {kd.description}")
    if topic.last_raw_exchange:
        lines.append("Recent exchange:")
        ex = topic.last_raw_exchange
        content = ex.content if hasattr(ex, "content") else str(ex.to_dict())
        lines.append(f"  > {content[:200]}")
    lines.append("")
    return "\n".join(lines)


def _build_topic_block_summary_plus_key(topic: TopicEntry) -> str:
    """Build summary + key decisions block for a WARM topic."""
    lines: List[str] = []
    lines.append(f"## [{topic.state.upper()}] {topic.label}")
    if topic.summary:
        lines.append(f"Summary: {topic.summary}")
    if topic.key_decisions:
        lines.append("Key decisions:")
        for kd in topic.key_decisions:
            lines.append(f"  - {kd.description}")
    lines.append("")
    return "\n".join(lines)


def _build_topic_block_summary_only(topic: TopicEntry) -> str:
    """Build summary-only block for a COLD topic."""
    lines: List[str] = []
    lines.append(f"## [{topic.state.upper()}] {topic.label}")
    if topic.summary:
        lines.append(f"Summary: {topic.summary}")
    else:
        lines.append("(No summary available)")
    lines.append("")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main implementation
# ---------------------------------------------------------------------------


class MemoryContextProvider:
    """Assembles memory context blocks from tiered topic state.

    This is the primary integration point for the MCP get_memory_context tool.
    """

    def __init__(
        self,
        registry: TopicRegistryV2,
        pressure_monitor: MemoryPressureMonitor,
        cache_ttl: float = 30.0,
    ):
        self._registry = registry
        self._monitor = pressure_monitor
        self._cache = MemoryContextCache(ttl_seconds=cache_ttl)

    def get_memory_context(
        self,
        current_topic_id: Optional[str] = None,
        budget_tokens: Optional[int] = None,
        include_warm: bool = True,
        include_cold_summaries: Optional[bool] = None,
    ) -> MemoryContextResult:
        """Assemble a context block for injection into system prompt.

        Args:
            current_topic_id: Active topic ID. If None, uses first ACTIVE topic.
            budget_tokens: Token budget override. If None, derived from pressure level.
            include_warm: Whether to include WARM tier content.
            include_cold_summaries: Whether to include COLD summaries.
                                   If None, auto-decided based on pressure level.

        Returns:
            MemoryContextResult with context_block, tokens_used, metadata, cache_hit.
        """
        all_topics = self._registry.list_topics()

        # Resolve active topic
        active_topic_id = current_topic_id
        if active_topic_id is None:
            for t in all_topics:
                if t.state == TopicState.ACTIVE.value:
                    active_topic_id = t.topic_id
                    break

        # Assess pressure — monitor.assess() expects List[Dict]
        topic_dicts = [t.to_dict() for t in all_topics]
        assessment = self._monitor.assess(topic_dicts)
        pressure_level = assessment.pressure_level

        # Compute compaction counter sum for cache invalidation
        compaction_sum = sum(t.compactions_since_last_access for t in all_topics)

        # Check cache
        cached = self._cache.get(
            active_topic_id=active_topic_id,
            pressure_level=pressure_level.name,
            topic_count=len(all_topics),
            last_compaction_counter=compaction_sum,
        )
        if cached is not None:
            cached.cache_hit = True
            return cached

        # Determine include_cold_summaries based on pressure
        if include_cold_summaries is None:
            # Include cold summaries only at NORMAL or L1 pressure
            include_cold_summaries = pressure_level in (
                PressureLevel.NORMAL,
                PressureLevel.L1,
            )

        # Determine effective budget
        if budget_tokens is None:
            # Default budget based on pressure level
            config = self._monitor.budget_allocator.config
            total_window = config.total_context_window
            reserve = config.reserve_ratio
            available = int(total_window * (1.0 - reserve))
            # Scale by pressure
            budget_map = {
                PressureLevel.NORMAL: 0.6,  # 60% of available for context
                PressureLevel.L1: 0.4,
                PressureLevel.L2: 0.25,
                PressureLevel.L3: 0.15,
            }
            budget_tokens = int(available * budget_map.get(pressure_level, 0.4))

        # Categorize topics by state
        active_topics: List[TopicEntry] = []
        warm_topics: List[TopicEntry] = []
        cold_topics: List[TopicEntry] = []
        archived_topics: List[TopicEntry] = []

        for t in all_topics:
            if t.state == TopicState.ACTIVE.value:
                active_topics.append(t)
            elif t.state == TopicState.WARM.value:
                warm_topics.append(t)
            elif t.state == TopicState.COLD.value:
                cold_topics.append(t)
            elif t.state == TopicState.ARCHIVED.value:
                archived_topics.append(t)

        # Build context block respecting budget
        blocks: List[str] = []
        tokens_remaining = budget_tokens

        # 1. Active topics (full)
        for t in active_topics:
            block = _build_topic_block_full(t)
            block_tokens = _estimate_tokens(block)
            if block_tokens <= tokens_remaining:
                blocks.append(block)
                tokens_remaining -= block_tokens
            else:
                # Fallback to summary for active if budget is tight
                fallback = _build_topic_block_summary_plus_key(t)
                fb_tokens = _estimate_tokens(fallback)
                if fb_tokens <= tokens_remaining:
                    blocks.append(fallback)
                    tokens_remaining -= fb_tokens

        # 2. Warm topics (summary + key decisions)
        if include_warm:
            for t in warm_topics:
                block = _build_topic_block_summary_plus_key(t)
                block_tokens = _estimate_tokens(block)
                if block_tokens <= tokens_remaining:
                    blocks.append(block)
                    tokens_remaining -= block_tokens
                else:
                    break  # Budget exhausted

        # 3. Cold topics (summary only)
        if include_cold_summaries:
            for t in cold_topics:
                block = _build_topic_block_summary_only(t)
                block_tokens = _estimate_tokens(block)
                if block_tokens <= tokens_remaining:
                    blocks.append(block)
                    tokens_remaining -= block_tokens
                else:
                    break

        # Assemble final context block
        header = "# Memory Context (Fish Trail v2)\n\n"
        context_block = header + "\n".join(blocks) if blocks else ""
        tokens_used = budget_tokens - tokens_remaining

        # Build metadata
        metadata = MemoryContextMetadata(
            topics_active=len(active_topics),
            topics_warm=len(warm_topics),
            topics_cold=len(cold_topics),
            topics_archived=len(archived_topics),
            pressure_level=pressure_level.name,
        )

        result = MemoryContextResult(
            context_block=context_block,
            tokens_used=tokens_used,
            metadata=metadata,
            cache_hit=False,
        )

        # Store in cache
        self._cache.put(
            result=result,
            active_topic_id=active_topic_id,
            pressure_level=pressure_level.name,
            topic_count=len(all_topics),
            last_compaction_counter=compaction_sum,
        )

        return result

    def invalidate_cache(self) -> None:
        """Force cache invalidation (e.g., after manual topic mutation)."""
        self._cache.invalidate()
