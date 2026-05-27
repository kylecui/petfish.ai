"""Tests for OutputFormatter — spec §3.6."""

import pytest
from datetime import datetime, timezone, timedelta

from output_formatter import (
    OutputFormatter,
    FormattedOutput,
    OutputSection,
    _relative_time,
    _sort_topics_by_access,
)
from memory_pressure_monitor import (
    BudgetAllocation,
    TokenBudget,
    PressureLevel,
)
from topic_registry_v2 import (
    TopicEntry,
    TopicState,
    NeverConsolidateItem,
    KeyDecision,
    RawExchange,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _minutes_ago(n: int) -> str:
    dt = datetime.now(timezone.utc) - timedelta(minutes=n)
    return dt.isoformat()


def _make_topic(
    topic_id: str,
    label: str,
    state: str = TopicState.ACTIVE.value,
    last_access_message_idx: int = 10,
    summary: str | None = None,
    key_decisions: list | None = None,
    last_raw_exchange: RawExchange | None = None,
    never_consolidate_items: list | None = None,
    message_count: int = 5,
    last_seen_at: str | None = None,
) -> TopicEntry:
    return TopicEntry(
        topic_id=topic_id,
        label=label,
        state=state,
        last_access_message_idx=last_access_message_idx,
        summary=summary,
        key_decisions=key_decisions or [],
        last_raw_exchange=last_raw_exchange,
        never_consolidate_items=never_consolidate_items or [],
        message_count=message_count,
        last_seen_at=last_seen_at or _now_iso(),
    )


def _make_allocation(
    pressure: PressureLevel = PressureLevel.NORMAL,
    active_ids: list | None = None,
    warm_ids: list | None = None,
    cold_ids: list | None = None,
) -> BudgetAllocation:
    return BudgetAllocation(
        total_budget=10000,
        active=TokenBudget(
            allocated_tokens=5000,
            topics_included=active_ids or [],
        ),
        warm=TokenBudget(
            allocated_tokens=3000,
            topics_included=warm_ids or [],
        ),
        cold=TokenBudget(
            allocated_tokens=2000,
            topics_included=cold_ids or [],
        ),
        pressure_level=pressure,
    )


def _make_nci(content: str, nci_type: str = "decision") -> NeverConsolidateItem:
    return NeverConsolidateItem(
        item_id=f"nci-{content[:8]}",
        type=nci_type,
        content=content,
        source_message_idx=5,
        added_at=_now_iso(),
        reason="test",
    )


def _make_exchange(user: str = "hello", assistant: str = "hi") -> RawExchange:
    return RawExchange(
        user_message=user,
        assistant_message=assistant,
        message_idx=10,
        timestamp=_now_iso(),
    )


def _make_key_decision(desc: str = "Use PostgreSQL") -> KeyDecision:
    return KeyDecision(
        decision_id="kd-1",
        description=desc,
        rationale="Best fit",
        timestamp=_now_iso(),
    )


# ---------------------------------------------------------------------------
# Tests: _relative_time helper
# ---------------------------------------------------------------------------


class TestRelativeTime:
    def test_empty_string(self):
        assert _relative_time("") == "unknown"

    def test_invalid_string(self):
        assert _relative_time("not-a-date") == "unknown"

    def test_just_now(self):
        result = _relative_time(_now_iso())
        assert result == "just now"

    def test_minutes_ago(self):
        ts = (datetime.now(timezone.utc) - timedelta(minutes=5)).isoformat()
        result = _relative_time(ts)
        assert "m ago" in result

    def test_hours_ago(self):
        ts = (datetime.now(timezone.utc) - timedelta(hours=3)).isoformat()
        result = _relative_time(ts)
        assert "h ago" in result

    def test_days_ago(self):
        ts = (datetime.now(timezone.utc) - timedelta(days=2)).isoformat()
        result = _relative_time(ts)
        assert "d ago" in result


# ---------------------------------------------------------------------------
# Tests: _sort_topics_by_access
# ---------------------------------------------------------------------------


class TestSortTopics:
    def test_sorts_descending(self):
        t1 = _make_topic("a", "A", last_access_message_idx=5)
        t2 = _make_topic("b", "B", last_access_message_idx=20)
        t3 = _make_topic("c", "C", last_access_message_idx=10)
        result = _sort_topics_by_access([t1, t2, t3])
        assert [t.topic_id for t in result] == ["b", "c", "a"]

    def test_empty_list(self):
        assert _sort_topics_by_access([]) == []


# ---------------------------------------------------------------------------
# Tests: Normal Mode
# ---------------------------------------------------------------------------


class TestNormalMode:
    def setup_method(self):
        self.fmt = OutputFormatter()

    def test_empty_topics(self):
        alloc = _make_allocation()
        result = self.fmt.format(alloc, [])
        assert isinstance(result, FormattedOutput)
        assert "Topic Index" in result.text
        assert result.total_tokens > 0
        # Only index section
        assert len(result.sections) == 1
        assert result.sections[0].type == "index"

    def test_active_topic_rendered(self):
        exchange = _make_exchange("What is X?", "X is a tool.")
        topic = _make_topic(
            "t1",
            "My Topic",
            state=TopicState.ACTIVE.value,
            last_raw_exchange=exchange,
        )
        alloc = _make_allocation(active_ids=["t1"])
        result = self.fmt.format(alloc, [topic])

        assert "[ACTIVE] My Topic" in result.text
        assert "What is X?" in result.text
        assert "X is a tool." in result.text
        # index + 1 active section
        assert len(result.sections) == 2
        assert result.sections[1].type == "active"
        assert result.sections[1].topic_id == "t1"

    def test_warm_topic_rendered(self):
        topic = _make_topic(
            "t2",
            "Warm Topic",
            state=TopicState.WARM.value,
            summary="This is about databases.",
            key_decisions=[_make_key_decision("Use PostgreSQL")],
            last_raw_exchange=_make_exchange("db?", "use postgres"),
        )
        alloc = _make_allocation(warm_ids=["t2"])
        result = self.fmt.format(alloc, [topic])

        assert "[WARM] Warm Topic" in result.text
        assert "This is about databases." in result.text
        assert "Use PostgreSQL" in result.text
        assert "Last Exchange" in result.text
        assert result.sections[1].type == "warm"

    def test_cold_topic_rendered(self):
        nci = _make_nci("Never forget this config")
        topic = _make_topic(
            "t3",
            "Cold Topic",
            state=TopicState.COLD.value,
            summary="Brief summary of old work.",
            never_consolidate_items=[nci],
        )
        alloc = _make_allocation(cold_ids=["t3"])
        result = self.fmt.format(alloc, [topic])

        assert "[COLD] Cold Topic" in result.text
        assert "Brief summary of old work." in result.text
        assert "Never forget this config" in result.text
        assert result.sections[1].type == "cold"

    def test_archived_only_in_index(self):
        topic = _make_topic(
            "t4",
            "Archived Topic",
            state=TopicState.ARCHIVED.value,
            summary="Old stuff.",
        )
        alloc = _make_allocation()
        result = self.fmt.format(alloc, [topic])

        assert "Archived Topic" in result.text
        assert "archived" in result.text
        # No dedicated section for archived, only index
        assert len(result.sections) == 1

    def test_nci_in_active_section(self):
        nci = _make_nci("Critical constraint")
        topic = _make_topic(
            "t1",
            "Active NCI",
            state=TopicState.ACTIVE.value,
            never_consolidate_items=[nci],
        )
        alloc = _make_allocation(active_ids=["t1"])
        result = self.fmt.format(alloc, [topic])

        assert "Preserved Items" in result.text
        assert "Critical constraint" in result.text

    def test_multi_tier_output(self):
        active = _make_topic(
            "a1",
            "Active1",
            state=TopicState.ACTIVE.value,
            last_access_message_idx=20,
            last_raw_exchange=_make_exchange(),
        )
        warm = _make_topic(
            "w1",
            "Warm1",
            state=TopicState.WARM.value,
            last_access_message_idx=10,
            summary="Warm summary.",
        )
        cold = _make_topic(
            "c1",
            "Cold1",
            state=TopicState.COLD.value,
            last_access_message_idx=5,
            summary="Cold summary.",
        )
        alloc = _make_allocation(active_ids=["a1"], warm_ids=["w1"], cold_ids=["c1"])
        result = self.fmt.format(alloc, [active, warm, cold])

        assert "[ACTIVE] Active1" in result.text
        assert "[WARM] Warm1" in result.text
        assert "[COLD] Cold1" in result.text
        # index + active + warm + cold = 4 sections
        assert len(result.sections) == 4

    def test_sorting_within_tier(self):
        t1 = _make_topic(
            "a1",
            "Older",
            state=TopicState.ACTIVE.value,
            last_access_message_idx=5,
            last_raw_exchange=_make_exchange("old", "old resp"),
        )
        t2 = _make_topic(
            "a2",
            "Newer",
            state=TopicState.ACTIVE.value,
            last_access_message_idx=20,
            last_raw_exchange=_make_exchange("new", "new resp"),
        )
        alloc = _make_allocation(active_ids=["a1", "a2"])
        result = self.fmt.format(alloc, [t1, t2])

        # Newer (idx=20) should appear before Older (idx=5)
        newer_pos = result.text.index("[ACTIVE] Newer")
        older_pos = result.text.index("[ACTIVE] Older")
        assert newer_pos < older_pos

    def test_total_tokens_is_sum_of_sections(self):
        topic = _make_topic(
            "t1",
            "Test",
            state=TopicState.ACTIVE.value,
            last_raw_exchange=_make_exchange(),
        )
        alloc = _make_allocation(active_ids=["t1"])
        result = self.fmt.format(alloc, [topic])
        assert result.total_tokens == sum(s.token_count for s in result.sections)


# ---------------------------------------------------------------------------
# Tests: _filter_included
# ---------------------------------------------------------------------------


class TestFilterIncluded:
    def setup_method(self):
        self.fmt = OutputFormatter()

    def test_empty_included_returns_all(self):
        topics = [
            _make_topic("a", "A"),
            _make_topic("b", "B"),
        ]
        result = self.fmt._filter_included(topics, [])
        assert len(result) == 2

    def test_filters_to_included_only(self):
        topics = [
            _make_topic("a", "A"),
            _make_topic("b", "B"),
            _make_topic("c", "C"),
        ]
        result = self.fmt._filter_included(topics, ["a", "c"])
        assert [t.topic_id for t in result] == ["a", "c"]

    def test_no_match_returns_empty(self):
        topics = [_make_topic("a", "A")]
        result = self.fmt._filter_included(topics, ["x", "y"])
        assert result == []


# ---------------------------------------------------------------------------
# Tests: Emergency Mode (L3)
# ---------------------------------------------------------------------------


class TestEmergencyMode:
    def setup_method(self):
        self.fmt = OutputFormatter()

    def test_emergency_header(self):
        topic = _make_topic(
            "t1",
            "Urgent",
            state=TopicState.ACTIVE.value,
            last_raw_exchange=_make_exchange("help", "helping"),
        )
        alloc = _make_allocation(
            pressure=PressureLevel.L3,
            active_ids=["t1"],
        )
        result = self.fmt.format(alloc, [topic])

        assert "Emergency Mode" in result.text
        assert "Urgent" in result.text

    def test_emergency_only_first_active(self):
        t1 = _make_topic(
            "t1",
            "First",
            state=TopicState.ACTIVE.value,
            last_access_message_idx=20,
            last_raw_exchange=_make_exchange("q1", "a1"),
        )
        t2 = _make_topic(
            "t2",
            "Second",
            state=TopicState.ACTIVE.value,
            last_access_message_idx=10,
            last_raw_exchange=_make_exchange("q2", "a2"),
        )
        alloc = _make_allocation(
            pressure=PressureLevel.L3,
            active_ids=["t1", "t2"],
        )
        result = self.fmt.format(alloc, [t1, t2])

        # Only first active topic gets a section (after sort, t1 has higher idx)
        active_sections = [s for s in result.sections if s.type == "active"]
        assert len(active_sections) == 1
        assert active_sections[0].topic_id == "t1"

    def test_emergency_shows_last_message(self):
        topic = _make_topic(
            "t1",
            "Topic",
            state=TopicState.ACTIVE.value,
            last_raw_exchange=_make_exchange("question", "answer here"),
        )
        alloc = _make_allocation(
            pressure=PressureLevel.L3,
            active_ids=["t1"],
        )
        result = self.fmt.format(alloc, [topic])
        assert "answer here" in result.text

    def test_emergency_falls_back_to_summary(self):
        topic = _make_topic(
            "t1",
            "Topic",
            state=TopicState.ACTIVE.value,
            summary="Fallback summary content.",
            last_raw_exchange=None,
        )
        alloc = _make_allocation(
            pressure=PressureLevel.L3,
            active_ids=["t1"],
        )
        result = self.fmt.format(alloc, [topic])
        assert "Fallback summary content." in result.text

    def test_emergency_no_content(self):
        topic = _make_topic(
            "t1",
            "Empty",
            state=TopicState.ACTIVE.value,
        )
        alloc = _make_allocation(
            pressure=PressureLevel.L3,
            active_ids=["t1"],
        )
        result = self.fmt.format(alloc, [topic])
        assert "(no content available)" in result.text

    def test_emergency_cross_topic_nci(self):
        nci1 = _make_nci("Config A")
        nci2 = _make_nci("Config B")
        t1 = _make_topic(
            "t1",
            "Active",
            state=TopicState.ACTIVE.value,
            never_consolidate_items=[nci1],
            last_raw_exchange=_make_exchange(),
        )
        t2 = _make_topic(
            "t2",
            "Warm",
            state=TopicState.WARM.value,
            never_consolidate_items=[nci2],
        )
        alloc = _make_allocation(
            pressure=PressureLevel.L3,
            active_ids=["t1"],
            warm_ids=["t2"],
        )
        result = self.fmt.format(alloc, [t1, t2])

        assert "Important Items (cross-topic)" in result.text
        assert "Config A" in result.text
        assert "Config B" in result.text

    def test_emergency_no_nci_no_section(self):
        topic = _make_topic(
            "t1",
            "Clean",
            state=TopicState.ACTIVE.value,
            last_raw_exchange=_make_exchange(),
        )
        alloc = _make_allocation(
            pressure=PressureLevel.L3,
            active_ids=["t1"],
        )
        result = self.fmt.format(alloc, [topic])
        assert "Important Items" not in result.text

    def test_emergency_warm_cold_counts(self):
        active = _make_topic(
            "a1",
            "Active",
            state=TopicState.ACTIVE.value,
            last_raw_exchange=_make_exchange(),
        )
        warm1 = _make_topic("w1", "W1", state=TopicState.WARM.value)
        warm2 = _make_topic("w2", "W2", state=TopicState.WARM.value)
        cold1 = _make_topic("c1", "C1", state=TopicState.COLD.value)
        alloc = _make_allocation(
            pressure=PressureLevel.L3,
            active_ids=["a1"],
            warm_ids=["w1", "w2"],
            cold_ids=["c1"],
        )
        result = self.fmt.format(alloc, [active, warm1, warm2, cold1])
        assert "Warm: 2 topics" in result.text
        assert "Cold: 1 topics" in result.text


# ---------------------------------------------------------------------------
# Tests: Edge cases
# ---------------------------------------------------------------------------


class TestEdgeCases:
    def setup_method(self):
        self.fmt = OutputFormatter()

    def test_topic_with_no_summary_warm(self):
        """Warm topic without summary still renders."""
        topic = _make_topic(
            "t1",
            "No Summary",
            state=TopicState.WARM.value,
            summary=None,
            last_raw_exchange=_make_exchange(),
        )
        alloc = _make_allocation(warm_ids=["t1"])
        result = self.fmt.format(alloc, [topic])
        assert "[WARM] No Summary" in result.text

    def test_topic_with_no_summary_cold(self):
        """Cold topic without summary still renders."""
        topic = _make_topic(
            "t1",
            "No Summary Cold",
            state=TopicState.COLD.value,
            summary=None,
        )
        alloc = _make_allocation(cold_ids=["t1"])
        result = self.fmt.format(alloc, [topic])
        assert "[COLD] No Summary Cold" in result.text

    def test_active_topic_not_in_allocation_excluded(self):
        """Active topic not listed in allocation.active.topics_included gets excluded."""
        topic = _make_topic("t1", "Excluded", state=TopicState.ACTIVE.value)
        alloc = _make_allocation(active_ids=["other_id"])
        result = self.fmt.format(alloc, [topic])
        assert "[ACTIVE]" not in result.text

    def test_large_number_of_topics(self):
        """Smoke test with many topics."""
        topics = []
        for i in range(20):
            state = [
                TopicState.ACTIVE.value,
                TopicState.WARM.value,
                TopicState.COLD.value,
            ][i % 3]
            topics.append(
                _make_topic(
                    f"t{i}",
                    f"Topic {i}",
                    state=state,
                    last_access_message_idx=i,
                    summary=f"Summary {i}",
                )
            )
        active_ids = [f"t{i}" for i in range(20) if i % 3 == 0]
        warm_ids = [f"t{i}" for i in range(20) if i % 3 == 1]
        cold_ids = [f"t{i}" for i in range(20) if i % 3 == 2]
        alloc = _make_allocation(
            active_ids=active_ids,
            warm_ids=warm_ids,
            cold_ids=cold_ids,
        )
        result = self.fmt.format(alloc, topics)
        assert result.total_tokens > 0
        assert len(result.sections) > 1
