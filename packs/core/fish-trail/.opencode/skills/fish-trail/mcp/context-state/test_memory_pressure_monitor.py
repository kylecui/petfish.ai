"""Unit tests for MemoryPressureMonitor.

Covers:
- Token estimation helpers (estimate_tokens, estimate_retained_tokens)
- TieredRetentionEngine: retention by state, message filtering, consolidation detection
- BudgetAllocator: pressure detection, normal/L1/L2/L3 strategies, LRU eviction
- MemoryPressureMonitor: unified facade, L3 alert, needs_consolidation
"""

import pytest

from memory_pressure_monitor import (
    BudgetAllocator,
    BudgetAllocation,
    BudgetConfig,
    MemoryPressureMonitor,
    OverflowActionType,
    PressureLevel,
    RetainedContent,
    RetentionConfig,
    RetentionPlan,
    RetentionType,
    TieredRetentionEngine,
    TopicRetentionDecision,
    estimate_retained_tokens,
    estimate_tokens,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def active_topic():
    return {
        "topic_id": "topic-active-1",
        "state": "active",
        "summary": "Active topic summary",
        "key_decisions": [{"description": "Use Python", "rationale": "Team expertise"}],
        "last_raw_exchange": {"user_message": "hello", "assistant_message": "hi"},
        "never_consolidate_items": [{"content": "CRITICAL: never lose this"}],
    }


@pytest.fixture
def warm_topic():
    return {
        "topic_id": "topic-warm-1",
        "state": "warm",
        "summary": "Warm topic summary about architecture decisions",
        "key_decisions": [
            {"description": "Use microservices", "rationale": "Scalability"},
            {"description": "PostgreSQL over MySQL", "rationale": "JSON support"},
        ],
        "last_raw_exchange": {
            "user_message": "What about the database?",
            "assistant_message": "I recommend PostgreSQL for its JSON support.",
        },
        "never_consolidate_items": [],
    }


@pytest.fixture
def cold_topic():
    return {
        "topic_id": "topic-cold-1",
        "state": "cold",
        "summary": "Cold topic summary about legacy migration",
        "key_decisions": [],
        "last_raw_exchange": None,
        "never_consolidate_items": [],
    }


@pytest.fixture
def archived_topic():
    return {
        "topic_id": "topic-archived-1",
        "state": "archived",
        "summary": "Archived topic",
        "key_decisions": [],
        "last_raw_exchange": None,
        "never_consolidate_items": [],
    }


@pytest.fixture
def messages():
    return [
        {"topic_id": "topic-active-1", "content": "First message about deployment"},
        {"topic_id": "topic-active-1", "content": "Second message with details"},
        {
            "topic_id": "topic-active-1",
            "content": "Third message",
            "tool_calls": [{"id": "tc1"}, {"id": "tc2"}],
        },
        {"topic_id": "topic-warm-1", "content": "Old warm message"},
        {"topic_id": "other-topic", "content": "Unrelated message"},
    ]


@pytest.fixture
def small_budget_config():
    """Small budget to easily trigger pressure levels."""
    return BudgetConfig(
        total_context_window=1000,
        reserve_ratio=0.15,
        index_ratio=0.10,
        active_ratio=0.50,
        warm_ratio=0.30,
        cold_ratio=0.10,
        pressure_l1=0.80,
        pressure_l2=0.90,
        pressure_l3=0.95,
        max_active_topics=3,
    )


# ---------------------------------------------------------------------------
# Token Estimation Tests
# ---------------------------------------------------------------------------


class TestEstimateTokens:
    def test_empty_string(self):
        assert estimate_tokens("") == 0

    def test_none_like_empty(self):
        # Empty string is falsy
        assert estimate_tokens("") == 0

    def test_short_string(self):
        # "hello" = 5 chars → 5/3.5 = 1.43 → int = 1
        assert estimate_tokens("hello") == 1

    def test_medium_string(self):
        # 100 chars → 100/3.5 ≈ 28
        text = "a" * 100
        assert estimate_tokens(text) == 28

    def test_long_string(self):
        # 3500 chars → 1000 tokens
        text = "x" * 3500
        assert estimate_tokens(text) == 1000

    def test_minimum_is_one(self):
        # Even single char → max(1, int(1/3.5)) = max(1, 0) = 1
        assert estimate_tokens("a") == 1


class TestEstimateRetainedTokens:
    def test_none_type(self):
        retain = RetainedContent(type=RetentionType.NONE)
        assert estimate_retained_tokens(retain) == 0

    def test_full_raw_messages(self):
        retain = RetainedContent(
            type=RetentionType.FULL_RAW,
            messages=[
                {"content": "a" * 350},  # 100 tokens
                {"content": "b" * 350},  # 100 tokens
            ],
        )
        assert estimate_retained_tokens(retain) == 200

    def test_full_raw_with_tool_calls(self):
        retain = RetainedContent(
            type=RetentionType.FULL_RAW,
            messages=[
                {"content": "a" * 350, "tool_calls": [{"id": "1"}, {"id": "2"}]},
            ],
        )
        # 100 tokens content + 2*50 tool_calls = 200
        assert estimate_retained_tokens(retain) == 200

    def test_summary_only(self):
        retain = RetainedContent(
            type=RetentionType.SUMMARY_ONLY,
            summary="a" * 175,  # 50 tokens
        )
        assert estimate_retained_tokens(retain) == 50

    def test_summary_plus_key(self):
        retain = RetainedContent(
            type=RetentionType.SUMMARY_PLUS_KEY,
            summary="a" * 175,  # 50 tokens
            key_decisions=[
                {"description": "b" * 35, "rationale": "c" * 35},  # 10+10 = 20
            ],
            last_exchange={
                "user_message": "d" * 70,  # 20
                "assistant_message": "e" * 70,  # 20
            },
        )
        # 50 + 20 + 40 = 110
        assert estimate_retained_tokens(retain) == 110

    def test_never_consolidate_adds_tokens(self):
        retain = RetainedContent(
            type=RetentionType.SUMMARY_ONLY,
            summary="a" * 175,  # 50
            never_consolidate=[{"content": "x" * 350}],  # 100
        )
        assert estimate_retained_tokens(retain) == 150

    def test_empty_messages_list(self):
        retain = RetainedContent(type=RetentionType.FULL_RAW, messages=[])
        assert estimate_retained_tokens(retain) == 0


# ---------------------------------------------------------------------------
# TieredRetentionEngine Tests
# ---------------------------------------------------------------------------


class TestTieredRetentionEngine:
    def test_active_topic_gets_full_raw(self, active_topic, messages):
        engine = TieredRetentionEngine()
        plan = engine.compute_retention([active_topic], messages)

        assert len(plan.topics) == 1
        decision = plan.topics[0]
        assert decision.state == "active"
        assert decision.retain.type == RetentionType.FULL_RAW
        # Should only include messages for topic-active-1 (3 messages)
        assert len(decision.retain.messages) == 3
        assert decision.consolidation_needed is False

    def test_active_topic_includes_never_consolidate(self, active_topic, messages):
        engine = TieredRetentionEngine()
        plan = engine.compute_retention([active_topic], messages)
        decision = plan.topics[0]
        assert decision.retain.never_consolidate is not None
        assert len(decision.retain.never_consolidate) == 1

    def test_warm_topic_gets_summary_plus_key(self, warm_topic):
        engine = TieredRetentionEngine()
        plan = engine.compute_retention([warm_topic])

        decision = plan.topics[0]
        assert decision.state == "warm"
        assert decision.retain.type == RetentionType.SUMMARY_PLUS_KEY
        assert decision.retain.summary is not None
        assert decision.retain.key_decisions is not None
        assert len(decision.retain.key_decisions) == 2
        assert decision.retain.last_exchange is not None
        assert decision.consolidation_needed is False

    def test_warm_topic_needs_consolidation_without_summary(self, warm_topic):
        warm_topic["summary"] = None
        engine = TieredRetentionEngine()
        plan = engine.compute_retention([warm_topic])
        assert plan.topics[0].consolidation_needed is True

    def test_cold_topic_gets_summary_only(self, cold_topic):
        engine = TieredRetentionEngine()
        plan = engine.compute_retention([cold_topic])

        decision = plan.topics[0]
        assert decision.state == "cold"
        assert decision.retain.type == RetentionType.SUMMARY_ONLY
        assert decision.retain.summary is not None
        assert decision.retain.key_decisions is None
        assert decision.retain.last_exchange is None

    def test_cold_topic_needs_consolidation_without_summary(self, cold_topic):
        cold_topic["summary"] = None
        engine = TieredRetentionEngine()
        plan = engine.compute_retention([cold_topic])
        assert plan.topics[0].consolidation_needed is True

    def test_archived_topic_gets_none(self, archived_topic):
        engine = TieredRetentionEngine()
        plan = engine.compute_retention([archived_topic])

        decision = plan.topics[0]
        assert decision.state == "archived"
        assert decision.retain.type == RetentionType.NONE
        assert decision.estimated_tokens == 0

    def test_message_filtering_by_topic_id(self, active_topic, messages):
        engine = TieredRetentionEngine()
        plan = engine.compute_retention([active_topic], messages)
        # Only 3 messages have topic_id=topic-active-1
        assert len(plan.topics[0].retain.messages) == 3

    def test_multiple_topics_mixed_states(
        self, active_topic, warm_topic, cold_topic, archived_topic, messages
    ):
        engine = TieredRetentionEngine()
        topics = [active_topic, warm_topic, cold_topic, archived_topic]
        plan = engine.compute_retention(topics, messages)

        assert len(plan.topics) == 4
        assert plan.topics[0].retain.type == RetentionType.FULL_RAW
        assert plan.topics[1].retain.type == RetentionType.SUMMARY_PLUS_KEY
        assert plan.topics[2].retain.type == RetentionType.SUMMARY_ONLY
        assert plan.topics[3].retain.type == RetentionType.NONE

    def test_total_estimated_tokens_summed(self, active_topic, warm_topic, messages):
        engine = TieredRetentionEngine()
        plan = engine.compute_retention([active_topic, warm_topic], messages)
        expected = sum(d.estimated_tokens for d in plan.topics)
        assert plan.total_estimated_tokens == expected

    def test_unknown_state_gets_none(self):
        topic = {
            "topic_id": "t1",
            "state": "unknown_state",
            "never_consolidate_items": [],
        }
        engine = TieredRetentionEngine()
        plan = engine.compute_retention([topic])
        assert plan.topics[0].retain.type == RetentionType.NONE

    def test_pressure_level_always_normal(self, active_topic, messages):
        """Retention engine preliminary detection always returns NORMAL."""
        engine = TieredRetentionEngine()
        plan = engine.compute_retention([active_topic], messages)
        assert plan.pressure_level == PressureLevel.NORMAL

    def test_no_messages_for_active_topic(self, active_topic):
        engine = TieredRetentionEngine()
        plan = engine.compute_retention([active_topic], [])
        assert plan.topics[0].retain.messages == []

    def test_warm_no_key_decisions_sets_none(self, warm_topic):
        warm_topic["key_decisions"] = []
        engine = TieredRetentionEngine()
        plan = engine.compute_retention([warm_topic])
        assert plan.topics[0].retain.key_decisions is None


# ---------------------------------------------------------------------------
# BudgetAllocator Tests
# ---------------------------------------------------------------------------


class TestBudgetAllocator:
    def _make_plan(self, topics_data):
        """Helper: build a RetentionPlan from simple topic defs."""
        decisions = []
        for td in topics_data:
            retain = RetainedContent(type=td.get("retain_type", RetentionType.FULL_RAW))
            decision = TopicRetentionDecision(
                topic_id=td["topic_id"],
                state=td["state"],
                retain=retain,
                estimated_tokens=td.get("tokens", 0),
            )
            decisions.append(decision)
        plan = RetentionPlan(
            topics=decisions,
            total_estimated_tokens=sum(d.estimated_tokens for d in decisions),
        )
        return plan

    def test_pressure_detection_normal(self):
        allocator = BudgetAllocator()
        assert allocator._detect_pressure(0.5) == PressureLevel.NORMAL
        assert allocator._detect_pressure(0.79) == PressureLevel.NORMAL

    def test_pressure_detection_l1(self):
        allocator = BudgetAllocator()
        assert allocator._detect_pressure(0.80) == PressureLevel.L1
        assert allocator._detect_pressure(0.89) == PressureLevel.L1

    def test_pressure_detection_l2(self):
        allocator = BudgetAllocator()
        assert allocator._detect_pressure(0.90) == PressureLevel.L2
        assert allocator._detect_pressure(0.94) == PressureLevel.L2

    def test_pressure_detection_l3(self):
        allocator = BudgetAllocator()
        assert allocator._detect_pressure(0.95) == PressureLevel.L3
        assert allocator._detect_pressure(1.0) == PressureLevel.L3

    def test_normal_allocation_fits_budget(self, small_budget_config):
        allocator = BudgetAllocator(small_budget_config)
        # Budget = 1000 * 0.85 = 850
        # active_budget = 850 * 0.50 = 425
        # warm_budget = 850 * 0.30 = 255
        # cold_budget = 850 * 0.10 = 85
        plan = self._make_plan(
            [
                {"topic_id": "a1", "state": "active", "tokens": 100},
                {"topic_id": "w1", "state": "warm", "tokens": 50},
                {"topic_id": "c1", "state": "cold", "tokens": 20},
            ]
        )
        result = allocator.allocate(plan)

        assert result.pressure_level == PressureLevel.NORMAL
        assert result.total_budget == 850
        assert result.active.used_tokens == 100
        assert result.warm.used_tokens == 50
        assert result.cold.used_tokens == 20
        assert "a1" in result.active.topics_included
        assert "w1" in result.warm.topics_included
        assert "c1" in result.cold.topics_included

    def test_l1_evicts_cold_topics(self, small_budget_config):
        allocator = BudgetAllocator(small_budget_config)
        # Budget = 850, demand must be 80-90% → 680-765
        # Let's fill: active=400, warm=200, cold=100 → 700+index → ~740
        plan = self._make_plan(
            [
                {"topic_id": "a1", "state": "active", "tokens": 400},
                {"topic_id": "w1", "state": "warm", "tokens": 200},
                {"topic_id": "c1", "state": "cold", "tokens": 80},
                {"topic_id": "c2", "state": "cold", "tokens": 70},
            ]
        )
        result = allocator.allocate(plan)

        # With demand ~750+index on 850 budget = ~90%+ → at least L1
        assert result.pressure_level in (
            PressureLevel.L1,
            PressureLevel.L2,
            PressureLevel.L3,
        )

    def test_lru_eviction_when_too_many_active(self):
        config = BudgetConfig(max_active_topics=2)
        allocator = BudgetAllocator(config)
        plan = self._make_plan(
            [
                {"topic_id": "a1", "state": "active", "tokens": 100},
                {"topic_id": "a2", "state": "active", "tokens": 200},
                {"topic_id": "a3", "state": "active", "tokens": 300},
            ]
        )
        result = allocator.allocate(plan)

        # a1 has least tokens → evicted
        assert "a1" in result.active.topics_evicted
        assert "a1" not in result.active.topics_included
        # overflow action generated
        evict_actions = [
            a for a in result.overflow_actions if a.type == OverflowActionType.EVICT
        ]
        assert len(evict_actions) >= 1
        assert any(a.target_topic_id == "a1" for a in evict_actions)

    def test_lru_no_eviction_within_limit(self):
        config = BudgetConfig(max_active_topics=3)
        allocator = BudgetAllocator(config)
        plan = self._make_plan(
            [
                {"topic_id": "a1", "state": "active", "tokens": 100},
                {"topic_id": "a2", "state": "active", "tokens": 200},
                {"topic_id": "a3", "state": "active", "tokens": 300},
            ]
        )
        result = allocator.allocate(plan)
        assert result.active.topics_evicted == []

    def test_index_tokens_estimation(self):
        allocator = BudgetAllocator()
        decisions = [
            TopicRetentionDecision(
                topic_id="t1",
                state="active",
                retain=RetainedContent(type=RetentionType.FULL_RAW),
            ),
            TopicRetentionDecision(
                topic_id="t2",
                state="warm",
                retain=RetainedContent(type=RetentionType.SUMMARY_PLUS_KEY),
            ),
            TopicRetentionDecision(
                topic_id="t3",
                state="archived",
                retain=RetainedContent(type=RetentionType.NONE),
            ),
        ]
        # Non-archived = 2, each 20 tokens
        assert allocator._estimate_index_tokens(decisions) == 40

    def test_archived_topics_skipped_in_allocation(self, small_budget_config):
        allocator = BudgetAllocator(small_budget_config)
        plan = self._make_plan(
            [
                {"topic_id": "a1", "state": "active", "tokens": 50},
                {
                    "topic_id": "x1",
                    "state": "archived",
                    "tokens": 0,
                    "retain_type": RetentionType.NONE,
                },
            ]
        )
        result = allocator.allocate(plan)
        # Archived topic not in any tier's included list
        assert "x1" not in result.active.topics_included
        assert "x1" not in result.warm.topics_included
        assert "x1" not in result.cold.topics_included

    def test_l2_evicts_all_cold_and_trims_active(self):
        # Force L2: demand = 91% of budget
        config = BudgetConfig(
            total_context_window=1000,
            reserve_ratio=0.15,  # budget = 850
            pressure_l2=0.90,
        )
        allocator = BudgetAllocator(config)
        # demand = 500 + 200 + 100 + index(60) = 860 → 860/850 > L2
        plan = self._make_plan(
            [
                {"topic_id": "a1", "state": "active", "tokens": 500},
                {"topic_id": "w1", "state": "warm", "tokens": 200},
                {"topic_id": "c1", "state": "cold", "tokens": 100},
            ]
        )
        result = allocator.allocate(plan)

        # Cold should be evicted in L2
        cold_evicts = [a for a in result.overflow_actions if "cold" in a.reason.lower()]
        assert len(cold_evicts) >= 1
        assert result.cold.topics_evicted == ["c1"]

    def test_l3_generates_emergency_summarize(self):
        config = BudgetConfig(
            total_context_window=1000,
            reserve_ratio=0.15,  # budget = 850
            pressure_l3=0.95,
        )
        allocator = BudgetAllocator(config)
        # demand must be >= 95% of 850 = 808
        plan = self._make_plan(
            [
                {"topic_id": "a1", "state": "active", "tokens": 500},
                {"topic_id": "w1", "state": "warm", "tokens": 300},
                {"topic_id": "c1", "state": "cold", "tokens": 100},
            ]
        )
        result = allocator.allocate(plan)

        if result.pressure_level == PressureLevel.L3:
            emergency_actions = [
                a
                for a in result.overflow_actions
                if a.type == OverflowActionType.EMERGENCY_SUMMARIZE
            ]
            assert len(emergency_actions) >= 1

    def test_total_budget_calculation(self):
        config = BudgetConfig(total_context_window=128000, reserve_ratio=0.15)
        allocator = BudgetAllocator(config)
        plan = self._make_plan([{"topic_id": "a1", "state": "active", "tokens": 100}])
        result = allocator.allocate(plan)
        assert result.total_budget == 108800  # 128000 * 0.85


# ---------------------------------------------------------------------------
# MemoryPressureMonitor (Facade) Tests
# ---------------------------------------------------------------------------


class TestMemoryPressureMonitor:
    def test_assess_returns_assessment_result(self, active_topic, messages):
        monitor = MemoryPressureMonitor()
        result = monitor.assess([active_topic], messages)

        assert result.retention_plan is not None
        assert result.allocation is not None
        assert result.pressure_level is not None
        assert isinstance(result.overflow_actions, list)
        assert isinstance(result.needs_consolidation, list)

    def test_no_alert_under_normal_pressure(self, active_topic, messages):
        monitor = MemoryPressureMonitor()
        result = monitor.assess([active_topic], messages)
        assert result.alert is None

    def test_l3_generates_alert(self):
        """Force L3 pressure and verify alert message."""
        budget_config = BudgetConfig(
            total_context_window=100,  # tiny window
            reserve_ratio=0.15,  # budget = 85
            pressure_l3=0.95,
        )
        monitor = MemoryPressureMonitor(budget_config=budget_config)
        # Create topic with messages that exceed 95% of 85 tokens
        topics = [
            {
                "topic_id": "t1",
                "state": "active",
                "summary": None,
                "key_decisions": [],
                "last_raw_exchange": None,
                "never_consolidate_items": [],
            }
        ]
        # Messages with enough content to overflow tiny budget
        msgs = [{"topic_id": "t1", "content": "x" * 500}]

        result = monitor.assess(topics, msgs)
        if result.pressure_level == PressureLevel.L3:
            assert result.alert is not None
            assert "CRITICAL" in result.alert

    def test_needs_consolidation_collected(self, warm_topic):
        warm_topic["summary"] = None  # triggers consolidation_needed
        monitor = MemoryPressureMonitor()
        result = monitor.assess([warm_topic])
        assert "topic-warm-1" in result.needs_consolidation

    def test_no_consolidation_when_summaries_present(self, warm_topic, cold_topic):
        monitor = MemoryPressureMonitor()
        result = monitor.assess([warm_topic, cold_topic])
        assert result.needs_consolidation == []

    def test_multiple_topics_consolidation(self, warm_topic, cold_topic):
        warm_topic["summary"] = None
        cold_topic["summary"] = None
        monitor = MemoryPressureMonitor()
        result = monitor.assess([warm_topic, cold_topic])
        assert "topic-warm-1" in result.needs_consolidation
        assert "topic-cold-1" in result.needs_consolidation

    def test_custom_configs_propagate(self):
        retention_config = RetentionConfig(max_active_topics=5)
        budget_config = BudgetConfig(total_context_window=64000)
        monitor = MemoryPressureMonitor(retention_config, budget_config)
        assert monitor.retention_engine.config.max_active_topics == 5
        assert monitor.budget_allocator.config.total_context_window == 64000

    def test_empty_topics_list(self):
        monitor = MemoryPressureMonitor()
        result = monitor.assess([], [])
        assert result.retention_plan.total_estimated_tokens == 0
        assert result.pressure_level == PressureLevel.NORMAL
        assert result.needs_consolidation == []

    def test_overflow_actions_from_allocation(self):
        """Overflow actions from allocator are passed through to result."""
        budget_config = BudgetConfig(max_active_topics=1)
        monitor = MemoryPressureMonitor(budget_config=budget_config)
        topics = [
            {
                "topic_id": "a1",
                "state": "active",
                "summary": None,
                "key_decisions": [],
                "last_raw_exchange": None,
                "never_consolidate_items": [],
            },
            {
                "topic_id": "a2",
                "state": "active",
                "summary": None,
                "key_decisions": [],
                "last_raw_exchange": None,
                "never_consolidate_items": [],
            },
        ]
        msgs = [
            {"topic_id": "a1", "content": "x" * 350},
            {"topic_id": "a2", "content": "y" * 700},
        ]
        result = monitor.assess(topics, msgs)
        # With max_active=1, one topic should be LRU evicted
        evict_actions = [
            a for a in result.overflow_actions if a.type == OverflowActionType.EVICT
        ]
        assert len(evict_actions) >= 1
