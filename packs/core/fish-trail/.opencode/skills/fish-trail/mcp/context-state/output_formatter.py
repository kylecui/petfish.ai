"""Output Formatter — Transforms budget allocation into structured context text.

Implements spec §3.6:
- Converts BudgetAllocation + TopicRegistry into formatted Markdown
- Topic Index table → ACTIVE (raw) → WARM (summary+key+exchange+NCI) → COLD (summary+NCI)
- Emergency Mode (L3): simplified single-line topic list
- Sorting: within each tier by last_access_message_idx descending
- ARCHIVED topics only appear in the index table
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List, Optional

from memory_pressure_monitor import (
    BudgetAllocation,
    PressureLevel,
    estimate_tokens,
)
from topic_registry_v2 import (
    TopicEntry,
    TopicState,
)


# ---------------------------------------------------------------------------
# Output data classes
# ---------------------------------------------------------------------------


@dataclass
class OutputSection:
    """Metadata for a single section in the formatted output."""

    type: str  # 'index' | 'active' | 'warm' | 'cold'
    topic_id: str
    token_count: int = 0
    content_type: str = ""  # e.g. 'raw_messages', 'summary', 'emergency'


@dataclass
class FormattedOutput:
    """Final formatted context text with metadata."""

    text: str = ""
    total_tokens: int = 0
    sections: List[OutputSection] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _relative_time(iso_str: str) -> str:
    """Convert ISO8601 timestamp to relative time string."""
    if not iso_str:
        return "unknown"
    try:
        dt = datetime.fromisoformat(iso_str.replace("Z", "+00:00"))
        now = datetime.now(timezone.utc)
        delta = now - dt
        seconds = int(delta.total_seconds())
        if seconds < 0:
            return "just now"
        if seconds < 60:
            return "just now"
        if seconds < 3600:
            mins = seconds // 60
            return f"{mins}m ago"
        if seconds < 86400:
            hours = seconds // 3600
            return f"{hours}h ago"
        days = seconds // 86400
        return f"{days}d ago"
    except (ValueError, TypeError):
        return "unknown"


def _sort_topics_by_access(topics: List[TopicEntry]) -> List[TopicEntry]:
    """Sort topics by last_access_message_idx descending (most recent first)."""
    return sorted(topics, key=lambda t: t.last_access_message_idx, reverse=True)


# ---------------------------------------------------------------------------
# Output Formatter
# ---------------------------------------------------------------------------


class OutputFormatter:
    """Transforms BudgetAllocation + TopicRegistry into structured context text.

    §3.6: The formatter produces Markdown output with:
    - Topic Index table (all topics)
    - ACTIVE sections (raw messages)
    - WARM sections (summary + key decisions + last exchange + NCI)
    - COLD sections (2-3 sentence summary + NCI)
    - Emergency Mode for L3 pressure
    """

    def format(
        self,
        allocation: BudgetAllocation,
        topics: List[TopicEntry],
    ) -> FormattedOutput:
        """Format allocation and topics into structured context text.

        Args:
            allocation: Budget allocation from BudgetAllocator
            topics: All topic entries from TopicRegistry

        Returns:
            FormattedOutput with text, token count, and section metadata
        """
        if allocation.pressure_level == PressureLevel.L3:
            return self._format_emergency(allocation, topics)
        return self._format_normal(allocation, topics)

    # -------------------------------------------------------------------
    # Normal mode
    # -------------------------------------------------------------------

    def _format_normal(
        self,
        allocation: BudgetAllocation,
        topics: List[TopicEntry],
    ) -> FormattedOutput:
        """Standard multi-tier format."""
        sections: List[OutputSection] = []
        parts: List[str] = []

        # Categorize topics by state
        active_topics = [t for t in topics if t.state == TopicState.ACTIVE.value]
        warm_topics = [t for t in topics if t.state == TopicState.WARM.value]
        cold_topics = [t for t in topics if t.state == TopicState.COLD.value]
        archived_topics = [t for t in topics if t.state == TopicState.ARCHIVED.value]

        # Filter to only included topics (from allocation)
        active_included = self._filter_included(
            active_topics, allocation.active.topics_included
        )
        warm_included = self._filter_included(
            warm_topics, allocation.warm.topics_included
        )
        cold_included = self._filter_included(
            cold_topics, allocation.cold.topics_included
        )

        # Sort within each tier
        active_included = _sort_topics_by_access(active_included)
        warm_included = _sort_topics_by_access(warm_included)
        cold_included = _sort_topics_by_access(cold_included)

        # 1. Topic Index
        index_text = self._build_index(
            active_included, warm_included, cold_included, archived_topics
        )
        index_tokens = estimate_tokens(index_text)
        sections.append(
            OutputSection(
                type="index",
                topic_id="__index__",
                token_count=index_tokens,
                content_type="table",
            )
        )
        parts.append(index_text)

        # 2. ACTIVE sections
        for topic in active_included:
            section_text = self._build_active_section(topic)
            section_tokens = estimate_tokens(section_text)
            sections.append(
                OutputSection(
                    type="active",
                    topic_id=topic.topic_id,
                    token_count=section_tokens,
                    content_type="raw_messages",
                )
            )
            parts.append(section_text)

        # 3. WARM sections
        for topic in warm_included:
            section_text = self._build_warm_section(topic)
            section_tokens = estimate_tokens(section_text)
            sections.append(
                OutputSection(
                    type="warm",
                    topic_id=topic.topic_id,
                    token_count=section_tokens,
                    content_type="summary",
                )
            )
            parts.append(section_text)

        # 4. COLD sections
        for topic in cold_included:
            section_text = self._build_cold_section(topic)
            section_tokens = estimate_tokens(section_text)
            sections.append(
                OutputSection(
                    type="cold",
                    topic_id=topic.topic_id,
                    token_count=section_tokens,
                    content_type="summary",
                )
            )
            parts.append(section_text)

        text = "\n".join(parts)
        total_tokens = sum(s.token_count for s in sections)

        return FormattedOutput(text=text, total_tokens=total_tokens, sections=sections)

    # -------------------------------------------------------------------
    # Emergency mode (L3)
    # -------------------------------------------------------------------

    def _format_emergency(
        self,
        allocation: BudgetAllocation,
        topics: List[TopicEntry],
    ) -> FormattedOutput:
        """Emergency mode: minimal output for extreme pressure."""
        sections: List[OutputSection] = []
        parts: List[str] = []

        active_topics = [t for t in topics if t.state == TopicState.ACTIVE.value]
        warm_topics = [t for t in topics if t.state == TopicState.WARM.value]
        cold_topics = [t for t in topics if t.state == TopicState.COLD.value]

        # Filter to included
        active_included = self._filter_included(
            active_topics, allocation.active.topics_included
        )
        active_included = _sort_topics_by_access(active_included)

        # Header line
        active_labels = ", ".join(t.label for t in active_included) or "none"
        warm_count = len(
            [t for t in warm_topics if t.topic_id in allocation.warm.topics_included]
        )
        cold_count = len(
            [t for t in cold_topics if t.topic_id in allocation.cold.topics_included]
        )

        header = f"## Topics (Emergency Mode)\nActive: {active_labels} | Warm: {warm_count} topics | Cold: {cold_count} topics"
        header_tokens = estimate_tokens(header)
        sections.append(
            OutputSection(
                type="index",
                topic_id="__index__",
                token_count=header_tokens,
                content_type="emergency",
            )
        )
        parts.append(header)

        # Active topic: last message only
        for topic in active_included[:1]:  # Only first active topic in emergency
            section_text = self._build_emergency_active(topic)
            section_tokens = estimate_tokens(section_text)
            sections.append(
                OutputSection(
                    type="active",
                    topic_id=topic.topic_id,
                    token_count=section_tokens,
                    content_type="emergency",
                )
            )
            parts.append(section_text)

        # All NCI items merged
        all_nci = self._collect_all_nci(topics)
        if all_nci:
            nci_text = "\n## Important Items (cross-topic)\n" + "\n".join(
                f"- {item}" for item in all_nci
            )
            nci_tokens = estimate_tokens(nci_text)
            sections.append(
                OutputSection(
                    type="cold",
                    topic_id="__nci__",
                    token_count=nci_tokens,
                    content_type="never_consolidate",
                )
            )
            parts.append(nci_text)

        text = "\n\n".join(parts)
        total_tokens = sum(s.token_count for s in sections)

        return FormattedOutput(text=text, total_tokens=total_tokens, sections=sections)

    # -------------------------------------------------------------------
    # Section builders
    # -------------------------------------------------------------------

    def _build_index(
        self,
        active: List[TopicEntry],
        warm: List[TopicEntry],
        cold: List[TopicEntry],
        archived: List[TopicEntry],
    ) -> str:
        """Build Topic Index table."""
        lines = [
            "## Topic Index",
            "| Topic | State | Last Active | Messages |",
            "|-------|-------|-------------|----------|",
        ]

        for topic in active:
            rel_time = _relative_time(topic.last_seen_at)
            lines.append(
                f"| {topic.label} | ACTIVE | {rel_time} | {topic.message_count} |"
            )

        for topic in warm:
            rel_time = _relative_time(topic.last_seen_at)
            lines.append(
                f"| {topic.label} | warm | {rel_time} | {topic.message_count} |"
            )

        for topic in cold:
            rel_time = _relative_time(topic.last_seen_at)
            lines.append(
                f"| {topic.label} | cold | {rel_time} | {topic.message_count} |"
            )

        for topic in archived:
            rel_time = _relative_time(topic.last_seen_at)
            lines.append(f"| {topic.label} | archived | {rel_time} | - |")

        lines.append("")
        lines.append("---")

        return "\n".join(lines)

    def _build_active_section(self, topic: TopicEntry) -> str:
        """Build ACTIVE section — raw messages preserved.

        Note: In v2, raw messages are stored externally. The formatter
        renders what's available in the TopicEntry (last_raw_exchange).
        Full raw message injection happens at the integration layer.
        """
        lines = [f"\n## [ACTIVE] {topic.label}\n"]

        # Raw exchange (if available)
        if topic.last_raw_exchange:
            lines.append(f"> User: {topic.last_raw_exchange.user_message}")
            lines.append(f"> Assistant: {topic.last_raw_exchange.assistant_message}")
            lines.append("")

        # NCI items
        if topic.never_consolidate_items:
            lines.append("**Preserved Items**:")
            for item in topic.never_consolidate_items:
                lines.append(f"- [{item.type}] {item.content}")
            lines.append("")

        lines.append("---")
        return "\n".join(lines)

    def _build_warm_section(self, topic: TopicEntry) -> str:
        """Build WARM section — summary + key decisions + last exchange + NCI."""
        lines = [f"\n## [WARM] {topic.label}\n"]

        # Summary
        if topic.summary:
            lines.append(f"**Summary**: {topic.summary}")
            lines.append("")

        # Key decisions
        if topic.key_decisions:
            lines.append("**Key Decisions**:")
            for kd in topic.key_decisions:
                lines.append(f"- {kd.description}")
            lines.append("")

        # Last exchange
        if topic.last_raw_exchange:
            lines.append("**Last Exchange**:")
            lines.append(f"> User: {topic.last_raw_exchange.user_message}")
            lines.append(f"> Assistant: {topic.last_raw_exchange.assistant_message}")
            lines.append("")

        # NCI items
        if topic.never_consolidate_items:
            lines.append("**Preserved Items**:")
            for item in topic.never_consolidate_items:
                lines.append(f"- [{item.type}] {item.content}")
            lines.append("")

        lines.append("---")
        return "\n".join(lines)

    def _build_cold_section(self, topic: TopicEntry) -> str:
        """Build COLD section — brief summary + NCI only."""
        lines = [f"\n## [COLD] {topic.label}\n"]

        # Summary (2-3 sentences)
        if topic.summary:
            lines.append(topic.summary)
            lines.append("")

        # NCI items
        if topic.never_consolidate_items:
            for item in topic.never_consolidate_items:
                lines.append(f"- [{item.type}] {item.content}")
            lines.append("")

        lines.append("---")
        return "\n".join(lines)

    def _build_emergency_active(self, topic: TopicEntry) -> str:
        """Emergency mode: just the topic label and last message."""
        lines = [f"## {topic.label}"]

        if topic.last_raw_exchange:
            # Last message only
            lines.append(topic.last_raw_exchange.assistant_message)
        elif topic.summary:
            lines.append(topic.summary)
        else:
            lines.append("(no content available)")

        return "\n".join(lines)

    # -------------------------------------------------------------------
    # Utilities
    # -------------------------------------------------------------------

    def _filter_included(
        self,
        topics: List[TopicEntry],
        included_ids: List[str],
    ) -> List[TopicEntry]:
        """Filter topics to only those in the included list."""
        if not included_ids:
            return topics  # If no filter, include all
        id_set = set(included_ids)
        return [t for t in topics if t.topic_id in id_set]

    def _collect_all_nci(self, topics: List[TopicEntry]) -> List[str]:
        """Collect all NCI items across all topics for emergency mode."""
        items: List[str] = []
        for topic in topics:
            for item in topic.never_consolidate_items:
                items.append(f"[{item.type}] {item.content}")
        return items
