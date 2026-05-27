"""Memory Pressure Monitor — Tiered Retention Engine + Budget Allocator.

Implements spec §3.3 (Tiered Retention Engine) and §3.5 (Budget Allocator):
- Computes per-topic retention decisions based on tier state
- Allocates token budget across tiers with priority weighting
- Detects pressure levels and suggests overflow actions
- Graceful degradation through L1/L2/L3 strategies

This module does NOT perform actual consolidation (that's ConsolidationGate §3.4).
It only decides *what* to retain and *how much budget* each tier gets.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------


class PressureLevel(str, Enum):
    NORMAL = "normal"
    L1 = "l1"  # >80% utilization
    L2 = "l2"  # >90% utilization
    L3 = "l3"  # >95% utilization


class RetentionType(str, Enum):
    FULL_RAW = "full_raw"
    SUMMARY_PLUS_KEY = "summary_plus_key"
    SUMMARY_ONLY = "summary_only"
    NONE = "none"


class OverflowActionType(str, Enum):
    EVICT = "evict"
    COMPRESS = "compress"
    TRIM = "trim"
    EMERGENCY_SUMMARIZE = "emergency_summarize"


# ---------------------------------------------------------------------------
# Data classes — Retention Engine
# ---------------------------------------------------------------------------


@dataclass
class RetainedContent:
    """What to retain for a topic in context."""

    type: RetentionType
    messages: Optional[List[Dict[str, Any]]] = None  # full_raw mode
    summary: Optional[str] = None  # summary modes
    key_decisions: Optional[List[Dict[str, Any]]] = None  # summary_plus_key
    last_exchange: Optional[Dict[str, Any]] = None  # summary_plus_key
    never_consolidate: Optional[List[Dict[str, Any]]] = None  # always kept


@dataclass
class DiscardedContent:
    """What was discarded and why."""

    message_ids: List[str] = field(default_factory=list)
    reason: str = ""


@dataclass
class TopicRetentionDecision:
    """Retention decision for a single topic."""

    topic_id: str
    state: str  # TopicState value
    retain: RetainedContent
    discard: DiscardedContent = field(default_factory=DiscardedContent)
    consolidation_needed: bool = False
    estimated_tokens: int = 0


@dataclass
class RetentionPlan:
    """Full retention plan across all topics."""

    topics: List[TopicRetentionDecision] = field(default_factory=list)
    total_estimated_tokens: int = 0
    pressure_level: PressureLevel = PressureLevel.NORMAL


# ---------------------------------------------------------------------------
# Data classes — Budget Allocator
# ---------------------------------------------------------------------------


@dataclass
class TokenBudget:
    """Budget allocation for a single tier."""

    allocated_tokens: int = 0
    used_tokens: int = 0
    topics_included: List[str] = field(default_factory=list)
    topics_evicted: List[str] = field(default_factory=list)


@dataclass
class OverflowAction:
    """An action to take when budget is exceeded."""

    type: OverflowActionType
    target_topic_id: str
    reason: str
    tokens_freed: int = 0


@dataclass
class BudgetAllocation:
    """Final budget allocation result."""

    total_budget: int = 0
    index: TokenBudget = field(default_factory=TokenBudget)
    active: TokenBudget = field(default_factory=TokenBudget)
    warm: TokenBudget = field(default_factory=TokenBudget)
    cold: TokenBudget = field(default_factory=TokenBudget)
    pressure_level: PressureLevel = PressureLevel.NORMAL
    overflow_actions: List[OverflowAction] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------


@dataclass
class RetentionConfig:
    """Configuration for the retention engine."""

    # Pressure thresholds (fraction of total budget)
    pressure_l1: float = 0.80
    pressure_l2: float = 0.90
    pressure_l3: float = 0.95

    # Max active topics before LRU eviction
    max_active_topics: int = 3


@dataclass
class BudgetConfig:
    """Configuration for budget allocation."""

    total_context_window: int = 128000  # tokens
    reserve_ratio: float = 0.15  # reserved for new messages

    # Tier ratios (must sum to 1.0)
    index_ratio: float = 0.10
    active_ratio: float = 0.50
    warm_ratio: float = 0.30
    cold_ratio: float = 0.10

    # Pressure thresholds
    pressure_l1: float = 0.80
    pressure_l2: float = 0.90
    pressure_l3: float = 0.95

    # Max active topics
    max_active_topics: int = 3


# ---------------------------------------------------------------------------
# Token estimation
# ---------------------------------------------------------------------------


def estimate_tokens(content: str) -> int:
    """Estimate token count using chars/3.5 heuristic for mixed CJK/Latin text."""
    if not content:
        return 0
    return max(1, int(len(content) / 3.5))


def estimate_retained_tokens(retain: RetainedContent) -> int:
    """Estimate total tokens for a RetainedContent."""
    total = 0

    if retain.type == RetentionType.FULL_RAW and retain.messages:
        for msg in retain.messages:
            content = msg.get("content", "")
            if isinstance(content, str):
                total += estimate_tokens(content)
            # tool calls add ~50 tokens overhead each
            tool_calls = msg.get("tool_calls", [])
            total += len(tool_calls) * 50

    if retain.summary:
        total += estimate_tokens(retain.summary)

    if retain.key_decisions:
        for kd in retain.key_decisions:
            desc = kd.get("description", "")
            rationale = kd.get("rationale", "")
            total += estimate_tokens(desc) + estimate_tokens(rationale)

    if retain.last_exchange:
        user_msg = retain.last_exchange.get("user_message", "")
        asst_msg = retain.last_exchange.get("assistant_message", "")
        total += estimate_tokens(user_msg) + estimate_tokens(asst_msg)

    if retain.never_consolidate:
        for item in retain.never_consolidate:
            content = item.get("content", "")
            total += estimate_tokens(content)

    return total


# ---------------------------------------------------------------------------
# Tiered Retention Engine
# ---------------------------------------------------------------------------


class TieredRetentionEngine:
    """Computes per-topic retention decisions based on tier state.

    §3.3: Given the registry and current messages, decides what each topic
    should retain in context. Does NOT manipulate content — only decides.
    """

    def __init__(self, config: Optional[RetentionConfig] = None):
        self.config = config or RetentionConfig()

    def compute_retention(
        self,
        topics: List[Dict[str, Any]],
        messages: Optional[List[Dict[str, Any]]] = None,
    ) -> RetentionPlan:
        """Compute retention plan for all topics.

        Args:
            topics: List of topic entries from registry (as dicts).
                    Each must have: topic_id, state, summary, key_decisions,
                    last_raw_exchange, never_consolidate_items
            messages: Current context messages (optional, for full_raw mode).

        Returns:
            RetentionPlan with per-topic decisions and pressure level.
        """
        plan = RetentionPlan()
        messages = messages or []

        for topic in topics:
            state = topic.get("state", "active")

            # Skip archived — they get nothing in context
            if state == "archived":
                decision = TopicRetentionDecision(
                    topic_id=topic["topic_id"],
                    state=state,
                    retain=RetainedContent(type=RetentionType.NONE),
                    estimated_tokens=0,
                )
                plan.topics.append(decision)
                continue

            decision = self._compute_topic_retention(topic, state, messages)
            plan.topics.append(decision)

        # Compute total and pressure
        plan.total_estimated_tokens = sum(d.estimated_tokens for d in plan.topics)
        plan.pressure_level = self._detect_pressure(plan.total_estimated_tokens)

        return plan

    def _compute_topic_retention(
        self,
        topic: Dict[str, Any],
        state: str,
        messages: List[Dict[str, Any]],
    ) -> TopicRetentionDecision:
        """Compute retention for a single topic based on its state."""
        topic_id = topic["topic_id"]
        never_consolidate = topic.get("never_consolidate_items", [])

        if state == "active":
            # ACTIVE: full episodic retention
            topic_messages = self._get_messages_for_topic(messages, topic_id)
            retain = RetainedContent(
                type=RetentionType.FULL_RAW,
                messages=topic_messages,
                never_consolidate=never_consolidate if never_consolidate else None,
            )
            decision = TopicRetentionDecision(
                topic_id=topic_id,
                state=state,
                retain=retain,
                consolidation_needed=False,
            )

        elif state == "warm":
            # WARM: summary + key decisions + last exchange
            summary = topic.get("summary")
            key_decisions = topic.get("key_decisions", [])
            last_exchange = topic.get("last_raw_exchange")

            retain = RetainedContent(
                type=RetentionType.SUMMARY_PLUS_KEY,
                summary=summary,
                key_decisions=key_decisions if key_decisions else None,
                last_exchange=last_exchange,
                never_consolidate=never_consolidate if never_consolidate else None,
            )
            # Need consolidation if no summary yet
            decision = TopicRetentionDecision(
                topic_id=topic_id,
                state=state,
                retain=retain,
                consolidation_needed=(summary is None),
            )

        elif state == "cold":
            # COLD: summary only
            summary = topic.get("summary")
            retain = RetainedContent(
                type=RetentionType.SUMMARY_ONLY,
                summary=summary,
                never_consolidate=never_consolidate if never_consolidate else None,
            )
            decision = TopicRetentionDecision(
                topic_id=topic_id,
                state=state,
                retain=retain,
                consolidation_needed=(summary is None),
            )

        else:
            # Unknown state — treat as none
            retain = RetainedContent(type=RetentionType.NONE)
            decision = TopicRetentionDecision(
                topic_id=topic_id,
                state=state,
                retain=retain,
            )

        decision.estimated_tokens = estimate_retained_tokens(decision.retain)
        return decision

    def _get_messages_for_topic(
        self, messages: List[Dict[str, Any]], topic_id: str
    ) -> List[Dict[str, Any]]:
        """Filter messages belonging to a specific topic.

        Messages are associated with topics via a 'topic_id' field.
        If no topic_id field exists, messages are not associated.
        """
        return [m for m in messages if m.get("topic_id") == topic_id]

    def _detect_pressure(self, total_tokens: int) -> PressureLevel:
        """Detect pressure level based on total estimated tokens.

        Note: This is a preliminary detection. The Budget Allocator
        does the definitive pressure calculation against actual budget.
        """
        # Use a reasonable default budget for preliminary detection
        # The Budget Allocator will recalculate with actual config
        return PressureLevel.NORMAL


# ---------------------------------------------------------------------------
# Budget Allocator
# ---------------------------------------------------------------------------


class BudgetAllocator:
    """Allocates token budget across tiers with graceful degradation.

    §3.5: Given a retention plan and budget config, fits content into
    the available context window. Generates overflow actions when needed.
    """

    def __init__(self, config: Optional[BudgetConfig] = None):
        self.config = config or BudgetConfig()

    def allocate(self, retention_plan: RetentionPlan) -> BudgetAllocation:
        """Allocate budget based on retention plan.

        Args:
            retention_plan: Output from TieredRetentionEngine.

        Returns:
            BudgetAllocation with per-tier budgets and overflow actions.
        """
        cfg = self.config
        total_budget = int(cfg.total_context_window * (1 - cfg.reserve_ratio))

        # Step 1: Calculate per-tier base budgets
        index_budget = int(total_budget * cfg.index_ratio)
        active_budget = int(total_budget * cfg.active_ratio)
        warm_budget = int(total_budget * cfg.warm_ratio)
        cold_budget = int(total_budget * cfg.cold_ratio)

        # Step 2: Categorize topics by state and compute demand
        active_topics = []
        warm_topics = []
        cold_topics = []

        for decision in retention_plan.topics:
            if decision.state == "active":
                active_topics.append(decision)
            elif decision.state == "warm":
                warm_topics.append(decision)
            elif decision.state == "cold":
                cold_topics.append(decision)
            # archived topics have 0 tokens, skip

        active_demand = sum(t.estimated_tokens for t in active_topics)
        warm_demand = sum(t.estimated_tokens for t in warm_topics)
        cold_demand = sum(t.estimated_tokens for t in cold_topics)
        index_demand = self._estimate_index_tokens(retention_plan.topics)

        total_demand = active_demand + warm_demand + cold_demand + index_demand

        # Step 3: Detect pressure
        utilization = total_demand / total_budget if total_budget > 0 else 1.0
        pressure = self._detect_pressure(utilization)

        # Step 4: Build allocation based on pressure level
        allocation = BudgetAllocation(
            total_budget=total_budget,
            pressure_level=pressure,
        )

        if pressure == PressureLevel.NORMAL:
            allocation = self._normal_allocation(
                allocation,
                active_topics,
                warm_topics,
                cold_topics,
                active_budget,
                warm_budget,
                cold_budget,
                index_budget,
                index_demand,
            )
        elif pressure == PressureLevel.L1:
            allocation = self._l1_degradation(
                allocation,
                active_topics,
                warm_topics,
                cold_topics,
                active_budget,
                warm_budget,
                cold_budget,
                index_budget,
                index_demand,
            )
        elif pressure == PressureLevel.L2:
            allocation = self._l2_degradation(
                allocation,
                active_topics,
                warm_topics,
                cold_topics,
                active_budget,
                warm_budget,
                cold_budget,
                index_budget,
                index_demand,
            )
        else:  # L3
            allocation = self._l3_emergency(
                allocation,
                active_topics,
                warm_topics,
                cold_topics,
                active_budget,
                warm_budget,
                cold_budget,
                index_budget,
                index_demand,
            )

        return allocation

    def _detect_pressure(self, utilization: float) -> PressureLevel:
        """Detect pressure level from utilization ratio."""
        cfg = self.config
        if utilization >= cfg.pressure_l3:
            return PressureLevel.L3
        elif utilization >= cfg.pressure_l2:
            return PressureLevel.L2
        elif utilization >= cfg.pressure_l1:
            return PressureLevel.L1
        return PressureLevel.NORMAL

    def _estimate_index_tokens(self, topics: List[TopicRetentionDecision]) -> int:
        """Estimate tokens needed for the Topic Index section.

        Topic Index shows one line per non-archived topic (~20 tokens each).
        """
        non_archived = [t for t in topics if t.state != "archived"]
        return len(non_archived) * 20

    def _normal_allocation(
        self,
        allocation,
        active_topics,
        warm_topics,
        cold_topics,
        active_budget,
        warm_budget,
        cold_budget,
        index_budget,
        index_demand,
    ) -> BudgetAllocation:
        """Normal allocation — fit within budgets, redistribute surplus."""
        # Index
        allocation.index = TokenBudget(
            allocated_tokens=index_budget,
            used_tokens=index_demand,
            topics_included=[
                t.topic_id for t in active_topics + warm_topics + cold_topics
            ],
        )

        # Active — include all, use actual demand up to budget
        active_demand = sum(t.estimated_tokens for t in active_topics)
        allocation.active = TokenBudget(
            allocated_tokens=active_budget,
            used_tokens=min(active_demand, active_budget),
            topics_included=[t.topic_id for t in active_topics],
        )

        # LRU eviction if too many active topics
        if len(active_topics) > self.config.max_active_topics:
            self._evict_active_lru(allocation, active_topics)

        # Warm
        warm_demand = sum(t.estimated_tokens for t in warm_topics)
        allocation.warm = TokenBudget(
            allocated_tokens=warm_budget,
            used_tokens=min(warm_demand, warm_budget),
            topics_included=[t.topic_id for t in warm_topics],
        )

        # Cold
        cold_demand = sum(t.estimated_tokens for t in cold_topics)
        allocation.cold = TokenBudget(
            allocated_tokens=cold_budget,
            used_tokens=min(cold_demand, cold_budget),
            topics_included=[t.topic_id for t in cold_topics],
        )

        return allocation

    def _l1_degradation(
        self,
        allocation,
        active_topics,
        warm_topics,
        cold_topics,
        active_budget,
        warm_budget,
        cold_budget,
        index_budget,
        index_demand,
    ) -> BudgetAllocation:
        """L1: Compress cold tier, give freed space to active.

        Actions:
        1. Cold topics sorted by compactions_since_last_access
        2. Most stale cold topics → archived (evict from context)
        3. Freed space → active tier
        """
        overflow_actions = []

        # Sort cold topics by staleness (higher compactions = more stale)
        cold_sorted = sorted(
            cold_topics,
            key=lambda t: t.estimated_tokens,  # evict largest first for space
            reverse=True,
        )

        # Evict cold topics until demand fits
        cold_demand = sum(t.estimated_tokens for t in cold_topics)
        cold_included = []
        cold_evicted = []
        tokens_freed = 0

        for topic in cold_sorted:
            if cold_demand - tokens_freed <= cold_budget:
                cold_included.append(topic)
            else:
                tokens_freed += topic.estimated_tokens
                cold_evicted.append(topic)
                overflow_actions.append(
                    OverflowAction(
                        type=OverflowActionType.EVICT,
                        target_topic_id=topic.topic_id,
                        reason="L1 pressure: evict stale cold topic",
                        tokens_freed=topic.estimated_tokens,
                    )
                )

        # Remaining cold that still exceed budget
        for topic in cold_sorted:
            if topic not in cold_evicted and topic not in cold_included:
                cold_included.append(topic)

        # Build allocation
        allocation.index = TokenBudget(
            allocated_tokens=index_budget,
            used_tokens=index_demand,
            topics_included=[
                t.topic_id for t in active_topics + warm_topics + cold_included
            ],
        )

        # Active gets extra from freed cold space
        boosted_active_budget = active_budget + tokens_freed
        active_demand = sum(t.estimated_tokens for t in active_topics)
        allocation.active = TokenBudget(
            allocated_tokens=boosted_active_budget,
            used_tokens=min(active_demand, boosted_active_budget),
            topics_included=[t.topic_id for t in active_topics],
        )

        if len(active_topics) > self.config.max_active_topics:
            self._evict_active_lru(allocation, active_topics)

        warm_demand = sum(t.estimated_tokens for t in warm_topics)
        allocation.warm = TokenBudget(
            allocated_tokens=warm_budget,
            used_tokens=min(warm_demand, warm_budget),
            topics_included=[t.topic_id for t in warm_topics],
        )

        cold_used = sum(t.estimated_tokens for t in cold_included)
        allocation.cold = TokenBudget(
            allocated_tokens=cold_budget,
            used_tokens=min(cold_used, cold_budget),
            topics_included=[t.topic_id for t in cold_included],
            topics_evicted=[t.topic_id for t in cold_evicted],
        )

        allocation.overflow_actions = overflow_actions
        return allocation

    def _l2_degradation(
        self,
        allocation,
        active_topics,
        warm_topics,
        cold_topics,
        active_budget,
        warm_budget,
        cold_budget,
        index_budget,
        index_demand,
    ) -> BudgetAllocation:
        """L2: Compress warm + trim active.

        Actions:
        1. All L1 actions
        2. Warm topics: drop last_exchange (keep summary+key_decisions only)
        3. Active topics: limit to 3 most recent messages each
        4. LRU evict active if > max_active_topics
        """
        overflow_actions = []

        # Evict all cold topics
        for topic in cold_topics:
            overflow_actions.append(
                OverflowAction(
                    type=OverflowActionType.EVICT,
                    target_topic_id=topic.topic_id,
                    reason="L2 pressure: evict all cold topics",
                    tokens_freed=topic.estimated_tokens,
                )
            )

        # Compress warm: estimate without last_exchange
        warm_compressed_tokens = 0
        for topic in warm_topics:
            # Re-estimate without last_exchange
            compressed = estimate_tokens(topic.retain.summary or "")
            if topic.retain.key_decisions:
                for kd in topic.retain.key_decisions:
                    compressed += estimate_tokens(kd.get("description", ""))
            if topic.retain.never_consolidate:
                for item in topic.retain.never_consolidate:
                    compressed += estimate_tokens(item.get("content", ""))
            warm_compressed_tokens += compressed
            overflow_actions.append(
                OverflowAction(
                    type=OverflowActionType.COMPRESS,
                    target_topic_id=topic.topic_id,
                    reason="L2 pressure: drop last_exchange from warm topic",
                    tokens_freed=max(0, topic.estimated_tokens - compressed),
                )
            )

        # Trim active: cap at ~3 messages each (estimate ~500 tokens per msg)
        active_trimmed_tokens = 0
        for topic in active_topics:
            trimmed_estimate = min(topic.estimated_tokens, 1500)  # ~3 msgs
            if topic.estimated_tokens > trimmed_estimate:
                overflow_actions.append(
                    OverflowAction(
                        type=OverflowActionType.TRIM,
                        target_topic_id=topic.topic_id,
                        reason="L2 pressure: trim active to last 3 messages",
                        tokens_freed=topic.estimated_tokens - trimmed_estimate,
                    )
                )
            active_trimmed_tokens += trimmed_estimate

        # Build allocation
        total_freed = sum(t.estimated_tokens for t in cold_topics)
        boosted_active = active_budget + total_freed

        allocation.index = TokenBudget(
            allocated_tokens=index_budget,
            used_tokens=index_demand,
            topics_included=[t.topic_id for t in active_topics + warm_topics],
        )
        allocation.active = TokenBudget(
            allocated_tokens=boosted_active,
            used_tokens=min(active_trimmed_tokens, boosted_active),
            topics_included=[t.topic_id for t in active_topics],
        )
        allocation.warm = TokenBudget(
            allocated_tokens=warm_budget,
            used_tokens=min(warm_compressed_tokens, warm_budget),
            topics_included=[t.topic_id for t in warm_topics],
        )
        allocation.cold = TokenBudget(
            allocated_tokens=0,
            used_tokens=0,
            topics_evicted=[t.topic_id for t in cold_topics],
        )

        if len(active_topics) > self.config.max_active_topics:
            self._evict_active_lru(allocation, active_topics)

        allocation.overflow_actions = overflow_actions
        return allocation

    def _l3_emergency(
        self,
        allocation,
        active_topics,
        warm_topics,
        cold_topics,
        active_budget,
        warm_budget,
        cold_budget,
        index_budget,
        index_demand,
    ) -> BudgetAllocation:
        """L3 Emergency: Extreme compression.

        Actions:
        1. All cold → archived (0 tokens)
        2. All warm → single sentence summary only
        3. Active → last 1 message + never-consolidate only
        4. Topic Index → active topics only
        5. Suggest new session
        """
        overflow_actions = []

        # Evict all cold
        for topic in cold_topics:
            overflow_actions.append(
                OverflowAction(
                    type=OverflowActionType.EVICT,
                    target_topic_id=topic.topic_id,
                    reason="L3 emergency: evict all cold",
                    tokens_freed=topic.estimated_tokens,
                )
            )

        # Emergency summarize all warm (estimate ~30 tokens each)
        warm_emergency_tokens = 0
        for topic in warm_topics:
            emergency_estimate = 30  # single sentence
            if topic.retain.never_consolidate:
                for item in topic.retain.never_consolidate:
                    emergency_estimate += estimate_tokens(item.get("content", ""))
            overflow_actions.append(
                OverflowAction(
                    type=OverflowActionType.EMERGENCY_SUMMARIZE,
                    target_topic_id=topic.topic_id,
                    reason="L3 emergency: compress warm to single sentence",
                    tokens_freed=max(0, topic.estimated_tokens - emergency_estimate),
                )
            )
            warm_emergency_tokens += emergency_estimate

        # Trim active to last 1 message + never-consolidate
        active_emergency_tokens = 0
        for topic in active_topics:
            emergency_estimate = 500  # ~1 message
            if topic.retain.never_consolidate:
                for item in topic.retain.never_consolidate:
                    emergency_estimate += estimate_tokens(item.get("content", ""))
            overflow_actions.append(
                OverflowAction(
                    type=OverflowActionType.TRIM,
                    target_topic_id=topic.topic_id,
                    reason="L3 emergency: trim active to last 1 message",
                    tokens_freed=max(0, topic.estimated_tokens - emergency_estimate),
                )
            )
            active_emergency_tokens += emergency_estimate

        # Index only shows active topics in L3
        index_emergency = len(active_topics) * 20

        allocation.index = TokenBudget(
            allocated_tokens=index_budget,
            used_tokens=index_emergency,
            topics_included=[t.topic_id for t in active_topics],
        )
        allocation.active = TokenBudget(
            allocated_tokens=active_budget + cold_budget,  # reclaim cold space
            used_tokens=active_emergency_tokens,
            topics_included=[t.topic_id for t in active_topics],
        )
        allocation.warm = TokenBudget(
            allocated_tokens=warm_budget,
            used_tokens=warm_emergency_tokens,
            topics_included=[t.topic_id for t in warm_topics],
        )
        allocation.cold = TokenBudget(
            allocated_tokens=0,
            used_tokens=0,
            topics_evicted=[t.topic_id for t in cold_topics],
        )

        allocation.overflow_actions = overflow_actions
        return allocation

    def _evict_active_lru(
        self,
        allocation: BudgetAllocation,
        active_topics: List[TopicRetentionDecision],
    ) -> None:
        """LRU-evict active topics exceeding max_active_topics.

        Moves least-recently-accessed active topics to warm tier conceptually.
        Adds overflow actions for the evicted topics.
        """
        max_count = self.config.max_active_topics
        if len(active_topics) <= max_count:
            return

        # Sort by estimated_tokens ascending (proxy for recency — smaller = older/less active)
        # In real usage, we'd sort by last_access_message_idx from the registry
        sorted_topics = sorted(active_topics, key=lambda t: t.estimated_tokens)
        to_evict = sorted_topics[: len(active_topics) - max_count]

        for topic in to_evict:
            allocation.overflow_actions.append(
                OverflowAction(
                    type=OverflowActionType.EVICT,
                    target_topic_id=topic.topic_id,
                    reason="LRU eviction: too many active topics",
                    tokens_freed=topic.estimated_tokens,
                )
            )
            # Move from active included to evicted
            if topic.topic_id in allocation.active.topics_included:
                allocation.active.topics_included.remove(topic.topic_id)
                allocation.active.topics_evicted.append(topic.topic_id)


# ---------------------------------------------------------------------------
# Unified API — MemoryPressureMonitor
# ---------------------------------------------------------------------------


class MemoryPressureMonitor:
    """Unified facade combining TieredRetentionEngine + BudgetAllocator.

    Usage:
        monitor = MemoryPressureMonitor()
        result = monitor.assess(topics, messages)
        # result.retention_plan — what each topic should retain
        # result.allocation — how budget is distributed
        # result.pressure_level — current pressure
        # result.overflow_actions — suggested actions
    """

    def __init__(
        self,
        retention_config: Optional[RetentionConfig] = None,
        budget_config: Optional[BudgetConfig] = None,
    ):
        self.retention_engine = TieredRetentionEngine(retention_config)
        self.budget_allocator = BudgetAllocator(budget_config)

    @dataclass
    class AssessmentResult:
        """Combined result from retention + budget allocation."""

        retention_plan: RetentionPlan
        allocation: BudgetAllocation
        pressure_level: PressureLevel
        overflow_actions: List[OverflowAction]
        needs_consolidation: List[str]  # topic_ids needing consolidation
        alert: Optional[str] = None  # human-readable alert if L3

    def assess(
        self,
        topics: List[Dict[str, Any]],
        messages: Optional[List[Dict[str, Any]]] = None,
    ) -> "MemoryPressureMonitor.AssessmentResult":
        """Run full assessment: retention plan → budget allocation.

        Args:
            topics: Topic entries from registry (as dicts).
            messages: Current context messages (optional).

        Returns:
            AssessmentResult with plan, allocation, and actions.
        """
        # Step 1: Compute retention plan
        retention_plan = self.retention_engine.compute_retention(topics, messages)

        # Step 2: Allocate budget
        allocation = self.budget_allocator.allocate(retention_plan)

        # Step 3: Collect topics needing consolidation
        needs_consolidation = [
            d.topic_id for d in retention_plan.topics if d.consolidation_needed
        ]

        # Step 4: Generate alert for L3
        alert = None
        if allocation.pressure_level == PressureLevel.L3:
            alert = (
                "⚠️ Memory pressure CRITICAL (L3). Context severely trimmed. "
                "Consider starting a new session or archiving inactive topics."
            )

        return MemoryPressureMonitor.AssessmentResult(
            retention_plan=retention_plan,
            allocation=allocation,
            pressure_level=allocation.pressure_level,
            overflow_actions=allocation.overflow_actions,
            needs_consolidation=needs_consolidation,
            alert=alert,
        )
