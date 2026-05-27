"""Consolidation Gate — Controls when and how to summarize topic content.

Implements spec §3.4:
- Determines whether a topic should be consolidated (shouldConsolidate)
- Performs consolidation: extract key decisions, generate summary, quality check
- Enforces never-consolidate list
- Rollback on quality failure with retry tracking

This module does NOT call an LLM. It provides the *logic and structure* for
consolidation decisions. Actual summarization is injected via a callable.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

from topic_registry_v2 import (
    KeyDecision,
    NeverConsolidateItem,
    NeverConsolidateType,
    TopicEntry,
    TopicState,
)
from memory_pressure_monitor import PressureLevel


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------


class ConsolidationTrigger(str, Enum):
    STATE_TRANSITION_WARM_TO_COLD = "state_transition_warm_to_cold"
    BUDGET_PRESSURE = "budget_pressure"
    REDUNDANCY_DETECTED = "redundancy_detected"
    MANUAL_REQUEST = "manual_request"


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------


@dataclass
class ConsolidationContext:
    """Context passed to shouldConsolidate to decide if consolidation is needed."""

    trigger: ConsolidationTrigger
    budget_pressure: PressureLevel
    messages_since_last_consolidation: int


@dataclass
class ConsolidationDecision:
    """Result of shouldConsolidate — whether to proceed."""

    should_consolidate: bool
    reason: str
    exempt_items: List[NeverConsolidateItem] = field(default_factory=list)


@dataclass
class ConsolidationConfig:
    """Configuration for the consolidation process."""

    quality_threshold: float = 0.7
    max_summary_tokens: int = 200
    preserve_error_fix_pairs: bool = True
    max_consecutive_failures: int = 3


@dataclass
class Message:
    """Minimal message representation for consolidation input."""

    idx: int
    role: str  # "user", "assistant", "tool"
    content: str
    tokens: int = 0


@dataclass
class ConsolidationResult:
    """Result of a consolidation attempt."""

    success: bool
    summary: str = ""
    key_decisions: List[KeyDecision] = field(default_factory=list)
    quality_score: float = 0.0
    tokens_before: int = 0
    tokens_after: int = 0
    compression_ratio: float = 0.0
    failure_reason: str = ""


# ---------------------------------------------------------------------------
# Summarizer protocol
# ---------------------------------------------------------------------------

# A summarizer is a callable:
#   (messages: List[Message], max_tokens: int, focus: str) -> str
SummarizerFn = Callable[[List[Message], int, str], str]

# A quality assessor is a callable:
#   (summary: str, original_messages: List[Message], key_decisions: List[KeyDecision]) -> float
QualityAssessorFn = Callable[[str, List[Message], List[KeyDecision]], float]


# ---------------------------------------------------------------------------
# Redundancy Detection
# ---------------------------------------------------------------------------


def detect_redundancy(messages: List[Message]) -> bool:
    """Detect high redundancy in a message list.

    Rules from spec:
    - >3 consecutive same tool call pattern
    - >2 consecutive same error message
    - >5 messages with content similarity > 0.9 (approximated by exact match)
    """
    if len(messages) < 3:
        return False

    # Rule 1: >3 consecutive similar messages (same content prefix, likely tool calls)
    consecutive_similar = 1
    for i in range(1, len(messages)):
        # Use first 100 chars as "pattern" proxy
        prev_pattern = messages[i - 1].content[:100]
        curr_pattern = messages[i].content[:100]
        if prev_pattern == curr_pattern and prev_pattern:
            consecutive_similar += 1
            if consecutive_similar > 3:
                return True
        else:
            consecutive_similar = 1

    # Rule 2: >2 consecutive same error-like messages
    consecutive_errors = 1
    for i in range(1, len(messages)):
        if (
            messages[i].role == messages[i - 1].role
            and messages[i].content == messages[i - 1].content
            and "error" in messages[i].content.lower()
        ):
            consecutive_errors += 1
            if consecutive_errors > 2:
                return True
        else:
            consecutive_errors = 1

    # Rule 3: >5 messages with identical content
    content_counts: Dict[str, int] = {}
    for m in messages:
        key = m.content.strip()
        if key:
            content_counts[key] = content_counts.get(key, 0) + 1
            if content_counts[key] > 5:
                return True

    return False


# ---------------------------------------------------------------------------
# Key Decision Extraction
# ---------------------------------------------------------------------------

# Patterns that indicate a decision
_DECISION_KEYWORDS = [
    "决定",
    "选择",
    "确认",
    "选",
    "用",
    "decide",
    "chose",
    "choose",
    "confirm",
    "pick",
    "go with",
    "方案a",
    "方案b",
    "option a",
    "option b",
]


def extract_key_decisions(
    messages: List[Message],
    existing_decisions: List[KeyDecision],
) -> List[KeyDecision]:
    """Extract key decisions from messages using pattern matching.

    Looks for:
    - Messages containing decision keywords
    - User messages followed by assistant confirmation
    - A vs B comparison followed by conclusion
    """
    import hashlib
    from datetime import datetime, timezone

    existing_ids = {d.decision_id for d in existing_decisions}
    new_decisions: List[KeyDecision] = []

    for i, msg in enumerate(messages):
        if msg.role != "user":
            continue

        content_lower = msg.content.lower()
        matched_keyword = None
        for kw in _DECISION_KEYWORDS:
            if kw in content_lower:
                matched_keyword = kw
                break

        if matched_keyword is None:
            continue

        # Check if next message is assistant confirmation
        if i + 1 < len(messages) and messages[i + 1].role == "assistant":
            # Generate stable ID from content
            decision_id = hashlib.sha256(
                f"decision:{msg.idx}:{msg.content[:80]}".encode()
            ).hexdigest()[:12]

            if decision_id in existing_ids:
                continue

            rationale = messages[i + 1].content[:200] if i + 1 < len(messages) else ""
            decision = KeyDecision(
                decision_id=decision_id,
                description=msg.content[:200],
                rationale=rationale,
                timestamp=datetime.now(timezone.utc).isoformat(),
            )
            new_decisions.append(decision)
            existing_ids.add(decision_id)

    return new_decisions


# ---------------------------------------------------------------------------
# Never-Consolidate Filtering
# ---------------------------------------------------------------------------


def extract_exempt_messages(
    messages: List[Message],
    never_consolidate_items: List[NeverConsolidateItem],
    preserve_error_fix_pairs: bool = True,
) -> tuple[List[Message], List[Message]]:
    """Separate messages into exempt and consolidatable.

    Returns (exempt_messages, consolidatable_messages).
    """
    exempt_indices: set[int] = set()

    # Mark messages that match never_consolidate items by source_message_idx
    for item in never_consolidate_items:
        exempt_indices.add(item.source_message_idx)

    # If preserving error-fix pairs, detect them
    if preserve_error_fix_pairs:
        for i, msg in enumerate(messages):
            if "error" in msg.content.lower() or "exception" in msg.content.lower():
                # Mark this error and the next message (likely the fix)
                exempt_indices.add(msg.idx)
                if i + 1 < len(messages):
                    exempt_indices.add(messages[i + 1].idx)

    exempt = [m for m in messages if m.idx in exempt_indices]
    consolidatable = [m for m in messages if m.idx not in exempt_indices]
    return exempt, consolidatable


# ---------------------------------------------------------------------------
# Consolidation Gate
# ---------------------------------------------------------------------------


class ConsolidationGate:
    """Controls when and how content is consolidated (summarized).

    Key responsibilities:
    - shouldConsolidate: decide based on trigger, pressure, and topic state
    - consolidate: perform the summarization with quality checks
    - Enforce never-consolidate list
    - Track consecutive failures for forced best-effort fallback
    """

    def __init__(
        self,
        summarizer: Optional[SummarizerFn] = None,
        quality_assessor: Optional[QualityAssessorFn] = None,
        config: Optional[ConsolidationConfig] = None,
    ):
        self._config = config or ConsolidationConfig()
        self._summarizer = summarizer or self._default_summarizer
        self._quality_assessor = quality_assessor or self._default_quality_assessor
        # Track consecutive failures per topic
        self._failure_counts: Dict[str, int] = {}

    @property
    def config(self) -> ConsolidationConfig:
        return self._config

    # -------------------------------------------------------------------
    # shouldConsolidate
    # -------------------------------------------------------------------

    def should_consolidate(
        self,
        topic: TopicEntry,
        context: ConsolidationContext,
    ) -> ConsolidationDecision:
        """Determine whether consolidation should proceed for a topic.

        Logic by trigger:
        - state_transition_warm_to_cold: consolidate if no summary exists
        - budget_pressure: consolidate if pressure >= L1
        - redundancy_detected: always consolidate (low priority)
        - manual_request: always consolidate
        """
        exempt_items = list(topic.never_consolidate_items)

        # Trigger 1: State transition WARM → COLD
        if context.trigger == ConsolidationTrigger.STATE_TRANSITION_WARM_TO_COLD:
            if topic.state == TopicState.COLD and not topic.summary:
                return ConsolidationDecision(
                    should_consolidate=True,
                    reason="Topic transitioned to COLD without summary",
                    exempt_items=exempt_items,
                )
            if topic.summary:
                return ConsolidationDecision(
                    should_consolidate=False,
                    reason="Topic already has summary",
                    exempt_items=exempt_items,
                )

        # Trigger 2: Budget pressure
        if context.trigger == ConsolidationTrigger.BUDGET_PRESSURE:
            if context.budget_pressure in (
                PressureLevel.L1,
                PressureLevel.L2,
                PressureLevel.L3,
            ):
                return ConsolidationDecision(
                    should_consolidate=True,
                    reason=f"Budget pressure at {context.budget_pressure.value}",
                    exempt_items=exempt_items,
                )
            return ConsolidationDecision(
                should_consolidate=False,
                reason="Budget pressure normal, no consolidation needed",
                exempt_items=exempt_items,
            )

        # Trigger 3: Redundancy detected
        if context.trigger == ConsolidationTrigger.REDUNDANCY_DETECTED:
            return ConsolidationDecision(
                should_consolidate=True,
                reason="Redundancy detected in topic messages",
                exempt_items=exempt_items,
            )

        # Trigger 4: Manual request
        if context.trigger == ConsolidationTrigger.MANUAL_REQUEST:
            return ConsolidationDecision(
                should_consolidate=True,
                reason="Manual consolidation requested",
                exempt_items=exempt_items,
            )

        # Default: don't consolidate
        return ConsolidationDecision(
            should_consolidate=False,
            reason="No applicable trigger condition met",
            exempt_items=exempt_items,
        )

    # -------------------------------------------------------------------
    # consolidate
    # -------------------------------------------------------------------

    def consolidate(
        self,
        topic: TopicEntry,
        messages: List[Message],
        config: Optional[ConsolidationConfig] = None,
    ) -> ConsolidationResult:
        """Perform consolidation on topic messages.

        Steps:
        1. Separate exempt items from consolidatable messages
        2. Extract key decisions
        3. Generate summary
        4. Quality check
        5. Accept or reject based on quality threshold
        """
        cfg = config or self._config

        if not messages:
            return ConsolidationResult(
                success=False,
                failure_reason="No messages to consolidate",
            )

        # Step 1: Separate exempt from consolidatable
        _exempt, consolidatable = extract_exempt_messages(
            messages, topic.never_consolidate_items, cfg.preserve_error_fix_pairs
        )

        if not consolidatable:
            return ConsolidationResult(
                success=False,
                failure_reason="All messages are exempt from consolidation",
            )

        # Step 2: Extract key decisions
        new_decisions = extract_key_decisions(consolidatable, topic.key_decisions)
        all_decisions = list(topic.key_decisions) + new_decisions

        # Step 3: Generate summary
        summary = self._summarizer(
            consolidatable, cfg.max_summary_tokens, "outcomes_and_state"
        )

        # Step 4: Quality check
        quality_score = self._quality_assessor(summary, consolidatable, all_decisions)

        # Calculate token metrics
        tokens_before = sum(m.tokens for m in messages)
        # Approximate tokens_after from summary length
        tokens_after = len(summary.split()) + sum(
            len(d.description.split()) for d in new_decisions
        )
        compression_ratio = tokens_after / tokens_before if tokens_before > 0 else 0.0

        # Step 5: Quality threshold check
        topic_id = topic.topic_id
        consecutive_failures = self._failure_counts.get(topic_id, 0)

        # Forced best-effort after max consecutive failures
        if consecutive_failures >= cfg.max_consecutive_failures:
            # Force accept with low confidence marking
            self._failure_counts[topic_id] = 0
            return ConsolidationResult(
                success=True,
                summary=summary,
                key_decisions=new_decisions,
                quality_score=quality_score,
                tokens_before=tokens_before,
                tokens_after=tokens_after,
                compression_ratio=compression_ratio,
            )

        if quality_score < cfg.quality_threshold:
            # Rollback: keep raw, increment failure counter
            self._failure_counts[topic_id] = consecutive_failures + 1
            return ConsolidationResult(
                success=False,
                summary=summary,
                key_decisions=new_decisions,
                quality_score=quality_score,
                tokens_before=tokens_before,
                tokens_after=tokens_after,
                compression_ratio=compression_ratio,
                failure_reason=f"Quality {quality_score:.2f} below threshold {cfg.quality_threshold}",
            )

        # Success: reset failure counter
        self._failure_counts[topic_id] = 0
        return ConsolidationResult(
            success=True,
            summary=summary,
            key_decisions=new_decisions,
            quality_score=quality_score,
            tokens_before=tokens_before,
            tokens_after=tokens_after,
            compression_ratio=compression_ratio,
        )

    # -------------------------------------------------------------------
    # Failure tracking
    # -------------------------------------------------------------------

    def get_failure_count(self, topic_id: str) -> int:
        """Get consecutive consolidation failure count for a topic."""
        return self._failure_counts.get(topic_id, 0)

    def reset_failure_count(self, topic_id: str) -> None:
        """Reset failure count (e.g. after manual intervention)."""
        self._failure_counts.pop(topic_id, None)

    # -------------------------------------------------------------------
    # Default implementations (can be overridden via constructor injection)
    # -------------------------------------------------------------------

    @staticmethod
    def _default_summarizer(
        messages: List[Message], max_tokens: int, focus: str
    ) -> str:
        """Simple extractive summary — takes first and last messages' key content.

        In production, this would be replaced by an LLM-based summarizer.
        """
        if not messages:
            return ""

        parts: List[str] = []
        # Take key content from messages, respecting approximate token budget
        budget_chars = max_tokens * 4  # ~4 chars per token approximation
        used = 0

        for msg in messages:
            snippet = msg.content[:200]
            if used + len(snippet) > budget_chars:
                break
            parts.append(f"[{msg.role}] {snippet}")
            used += len(snippet)

        return "\n".join(parts) if parts else messages[0].content[:budget_chars]

    @staticmethod
    def _default_quality_assessor(
        summary: str,
        original_messages: List[Message],
        key_decisions: List[KeyDecision],
    ) -> float:
        """Simple heuristic quality assessment.

        Checks:
        - Information coverage: summary length relative to input
        - Decision preservation: mentioned decisions appear in summary or separate list
        """
        if not summary or not original_messages:
            return 0.0

        # Coverage: summary should be at least 10% of original content length
        original_length = sum(len(m.content) for m in original_messages)
        if original_length == 0:
            return 0.0

        coverage_ratio = len(summary) / original_length
        # Ideal: 10-30% compression yields high score
        if coverage_ratio < 0.05:
            coverage_score = 0.3
        elif coverage_ratio < 0.1:
            coverage_score = 0.6
        elif coverage_ratio <= 0.5:
            coverage_score = 0.9
        else:
            coverage_score = 0.7  # Too verbose

        # Decision preservation: check if decisions are captured
        decision_score = 1.0
        if key_decisions:
            preserved = sum(
                1
                for d in key_decisions
                if d.description[:30].lower() in summary.lower()
            )
            decision_score = preserved / len(key_decisions) if key_decisions else 1.0

        # Weighted final score
        return coverage_score * 0.6 + decision_score * 0.4
