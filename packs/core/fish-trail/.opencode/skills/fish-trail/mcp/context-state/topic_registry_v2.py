"""V2 Topic Registry — Tiered Memory lifecycle state management.

This module implements the TopicRegistry v2.0 spec (§3.2) with:
- 4-tier state machine: active → warm → cold → archived
- Per-topic compaction tracking
- NeverConsolidate items, KeyDecisions, RawExchange
- Atomic persistence with backup-before-compaction
- Backward-compatible migration from v1

The registry is the sole persistent state that survives compaction.
It does NOT store full message content — only lifecycle metadata.
"""

import hashlib
import json
import os
import shutil
import threading
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------


class TopicState(str, Enum):
    ACTIVE = "active"
    WARM = "warm"
    COLD = "cold"
    ARCHIVED = "archived"


class NeverConsolidateType(str, Enum):
    DECISION = "decision"
    ERROR_FIX = "error_fix"
    CONFIG = "config"
    INSTRUCTION = "instruction"
    CONSTRAINT = "constraint"


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------


@dataclass
class NeverConsolidateItem:
    item_id: str
    type: str  # NeverConsolidateType value
    content: str
    source_message_idx: int
    added_at: str  # ISO8601
    reason: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "NeverConsolidateItem":
        return cls(
            item_id=data["item_id"],
            type=data["type"],
            content=data["content"],
            source_message_idx=data.get("source_message_idx", 0),
            added_at=data.get("added_at", ""),
            reason=data.get("reason", ""),
        )


@dataclass
class KeyDecision:
    decision_id: str
    description: str
    rationale: str
    timestamp: str  # ISO8601
    alternatives_considered: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "KeyDecision":
        return cls(
            decision_id=data["decision_id"],
            description=data["description"],
            rationale=data.get("rationale", ""),
            timestamp=data.get("timestamp", ""),
            alternatives_considered=data.get("alternatives_considered", []),
        )


@dataclass
class RawExchange:
    user_message: str
    assistant_message: str
    message_idx: int
    timestamp: str  # ISO8601

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RawExchange":
        return cls(
            user_message=data["user_message"],
            assistant_message=data["assistant_message"],
            message_idx=data.get("message_idx", 0),
            timestamp=data.get("timestamp", ""),
        )


@dataclass
class TopicEntry:
    topic_id: str
    label: str
    state: str = TopicState.ACTIVE.value  # stored as string for JSON compat
    description: str = ""
    parent_topic_id: Optional[str] = None

    # Temporal
    first_seen_at: str = ""  # ISO8601
    last_seen_at: str = ""  # ISO8601
    last_access_message_idx: int = 0

    # Statistics
    message_count: int = 0
    compactions_since_last_access: int = 0

    # Retention control
    never_consolidate_items: List[NeverConsolidateItem] = field(default_factory=list)
    priority_boost: float = 0.0

    # Consolidation products
    summary: Optional[str] = None
    key_decisions: List[KeyDecision] = field(default_factory=list)
    last_raw_exchange: Optional[RawExchange] = None

    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {
            "topic_id": self.topic_id,
            "label": self.label,
            "state": self.state,
            "description": self.description,
            "parent_topic_id": self.parent_topic_id,
            "first_seen_at": self.first_seen_at,
            "last_seen_at": self.last_seen_at,
            "last_access_message_idx": self.last_access_message_idx,
            "message_count": self.message_count,
            "compactions_since_last_access": self.compactions_since_last_access,
            "never_consolidate_items": [
                item.to_dict() for item in self.never_consolidate_items
            ],
            "priority_boost": self.priority_boost,
            "summary": self.summary,
            "key_decisions": [kd.to_dict() for kd in self.key_decisions],
            "last_raw_exchange": (
                self.last_raw_exchange.to_dict() if self.last_raw_exchange else None
            ),
        }
        return d

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TopicEntry":
        nci = [
            NeverConsolidateItem.from_dict(item)
            for item in data.get("never_consolidate_items", [])
        ]
        kd = [KeyDecision.from_dict(item) for item in data.get("key_decisions", [])]
        raw = None
        if data.get("last_raw_exchange"):
            raw = RawExchange.from_dict(data["last_raw_exchange"])

        return cls(
            topic_id=data["topic_id"],
            label=data.get("label", data.get("title", data["topic_id"])),
            state=data.get("state", TopicState.ACTIVE.value),
            description=data.get("description", ""),
            parent_topic_id=data.get("parent_topic_id"),
            first_seen_at=data.get("first_seen_at", ""),
            last_seen_at=data.get("last_seen_at", ""),
            last_access_message_idx=data.get("last_access_message_idx", 0),
            message_count=data.get("message_count", 0),
            compactions_since_last_access=data.get("compactions_since_last_access", 0),
            never_consolidate_items=nci,
            priority_boost=data.get("priority_boost", 0.0),
            summary=data.get("summary"),
            key_decisions=kd,
            last_raw_exchange=raw,
        )


# ---------------------------------------------------------------------------
# Registry Configuration
# ---------------------------------------------------------------------------


@dataclass
class RegistryConfig:
    """Tunable thresholds for state transitions."""

    active_threshold_messages: int = 5
    warm_to_cold_compactions: int = 1
    cold_to_archived_compactions: int = 3

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RegistryConfig":
        return cls(
            active_threshold_messages=data.get("active_threshold_messages", 5),
            warm_to_cold_compactions=data.get("warm_to_cold_compactions", 1),
            cold_to_archived_compactions=data.get("cold_to_archived_compactions", 3),
        )

    def config_hash(self) -> str:
        """Deterministic hash to detect config changes."""
        payload = json.dumps(self.to_dict(), sort_keys=True)
        return hashlib.sha256(payload.encode()).hexdigest()[:16]


# ---------------------------------------------------------------------------
# Topic Registry v2
# ---------------------------------------------------------------------------


class TopicRegistryV2:
    """Persistent registry managing topic lifecycle across compactions.

    Storage layout:
        .petfish/fish-trail/topic-registry.json  (main registry)
        .petfish/fish-trail/registry-backups/     (pre-compaction backups)
    """

    VERSION = "2.0"

    def __init__(self, base_dir: str, config: Optional[RegistryConfig] = None):
        self.base_dir = Path(base_dir)
        self.registry_path = self.base_dir / "topic-registry.json"
        self.backups_dir = self.base_dir / "registry-backups"
        self.config = config or RegistryConfig()

        self._lock = threading.Lock()
        self._lock_owner: Optional[int] = None
        self._lock_depth = 0

        # Ensure directories exist
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.backups_dir.mkdir(parents=True, exist_ok=True)

        # Initialize or load registry
        if not self.registry_path.exists():
            self._save_registry(self._empty_registry())

    # ------------------------------------------------------------------
    # Public API: Topic CRUD
    # ------------------------------------------------------------------

    def create_topic(
        self,
        topic_id: str,
        label: str,
        description: str = "",
        parent_topic_id: Optional[str] = None,
    ) -> TopicEntry:
        """Create a new topic in ACTIVE state."""
        self._enter_lock()
        try:
            registry = self._load_registry()
            if topic_id in registry["topics"]:
                raise ValueError(f"Topic already exists: {topic_id}")

            now = self._now()
            entry = TopicEntry(
                topic_id=topic_id,
                label=label,
                state=TopicState.ACTIVE.value,
                description=description,
                parent_topic_id=parent_topic_id,
                first_seen_at=now,
                last_seen_at=now,
                last_access_message_idx=0,
                message_count=0,
                compactions_since_last_access=0,
            )

            registry["topics"][topic_id] = entry.to_dict()
            registry["updated_at"] = now
            self._save_registry(registry)
            return entry
        finally:
            self._exit_lock()

    def get_topic(self, topic_id: str) -> Optional[TopicEntry]:
        """Get a topic entry by ID."""
        registry = self._load_registry()
        data = registry["topics"].get(topic_id)
        if data is None:
            return None
        return TopicEntry.from_dict(data)

    def list_topics(self, state: Optional[TopicState] = None) -> List[TopicEntry]:
        """List all topics, optionally filtered by state."""
        registry = self._load_registry()
        entries = []
        for data in registry["topics"].values():
            entry = TopicEntry.from_dict(data)
            if state is None or entry.state == state.value:
                entries.append(entry)
        # Sort by last_seen_at descending
        entries.sort(key=lambda e: e.last_seen_at, reverse=True)
        return entries

    def update_topic(self, topic_id: str, **fields: Any) -> TopicEntry:
        """Update arbitrary fields on a topic entry."""
        self._enter_lock()
        try:
            registry = self._load_registry()
            data = registry["topics"].get(topic_id)
            if data is None:
                raise KeyError(f"Topic not found: {topic_id}")

            # Apply updates
            for key, value in fields.items():
                if key in {"topic_id", "first_seen_at"}:
                    continue  # immutable fields
                if key == "never_consolidate_items" and isinstance(value, list):
                    data[key] = [
                        item.to_dict() if hasattr(item, "to_dict") else item
                        for item in value
                    ]
                elif key == "key_decisions" and isinstance(value, list):
                    data[key] = [
                        item.to_dict() if hasattr(item, "to_dict") else item
                        for item in value
                    ]
                elif key == "last_raw_exchange" and value is not None:
                    data[key] = value.to_dict() if hasattr(value, "to_dict") else value
                else:
                    data[key] = value

            data["last_seen_at"] = self._now()
            registry["topics"][topic_id] = data
            registry["updated_at"] = self._now()
            self._save_registry(registry)
            return TopicEntry.from_dict(data)
        finally:
            self._exit_lock()

    def record_access(self, topic_id: str, message_idx: int) -> TopicEntry:
        """Record that a topic was accessed at a given message index.

        This may trigger re-activation if the topic is WARM/COLD.
        """
        self._enter_lock()
        try:
            registry = self._load_registry()
            data = registry["topics"].get(topic_id)
            if data is None:
                raise KeyError(f"Topic not found: {topic_id}")

            entry = TopicEntry.from_dict(data)
            entry.last_seen_at = self._now()
            entry.last_access_message_idx = message_idx
            entry.message_count += 1
            entry.compactions_since_last_access = 0

            # Re-activation: WARM/COLD → ACTIVE
            if entry.state in (TopicState.WARM.value, TopicState.COLD.value):
                entry.state = TopicState.ACTIVE.value

            registry["topics"][topic_id] = entry.to_dict()
            registry["updated_at"] = self._now()
            self._save_registry(registry)
            return entry
        finally:
            self._exit_lock()

    # ------------------------------------------------------------------
    # Public API: State Transitions
    # ------------------------------------------------------------------

    def check_transitions(self, current_message_idx: int) -> List[Dict[str, Any]]:
        """Check and execute state transitions for all topics.

        Returns a list of transitions that occurred:
        [{"topic_id": ..., "from": ..., "to": ..., "reason": ...}]
        """
        self._enter_lock()
        try:
            registry = self._load_registry()
            transitions: List[Dict[str, Any]] = []

            active_topics = [
                tid
                for tid, data in registry["topics"].items()
                if data.get("state") == TopicState.ACTIVE.value
            ]
            has_multiple_active = len(active_topics) > 1

            for topic_id, data in list(registry["topics"].items()):
                entry = TopicEntry.from_dict(data)
                new_state = self._compute_transition(
                    entry, current_message_idx, has_multiple_active
                )

                if new_state and new_state != entry.state:
                    old_state = entry.state
                    entry.state = new_state

                    # WARM→COLD: discard last_raw_exchange
                    if new_state == TopicState.COLD.value:
                        entry.last_raw_exchange = None

                    registry["topics"][topic_id] = entry.to_dict()
                    transitions.append(
                        {
                            "topic_id": topic_id,
                            "from": old_state,
                            "to": new_state,
                            "reason": self._transition_reason(
                                old_state, new_state, entry
                            ),
                        }
                    )

            if transitions:
                registry["updated_at"] = self._now()
                self._save_registry(registry)

            return transitions
        finally:
            self._exit_lock()

    def on_compaction(self, compaction_id: str) -> List[Dict[str, Any]]:
        """Handle a compaction event.

        1. Backup registry
        2. Increment compaction counters
        3. Check and execute state transitions
        Returns transitions that occurred.
        """
        self._enter_lock()
        try:
            # 1. Backup
            self._backup_registry(compaction_id)

            # 2. Update compaction metadata
            registry = self._load_registry()
            registry["last_compaction_id"] = compaction_id
            registry["compaction_count"] = registry.get("compaction_count", 0) + 1

            # 3. Increment compactions_since_last_access for non-active topics
            for topic_id, data in registry["topics"].items():
                if data.get("state") != TopicState.ACTIVE.value:
                    data["compactions_since_last_access"] = (
                        data.get("compactions_since_last_access", 0) + 1
                    )

            registry["updated_at"] = self._now()
            self._save_registry(registry)

            # 4. Check transitions (using message_idx=0 as we don't have it here)
            # Transitions after compaction are based on compaction counts, not message gap
            return self._check_compaction_transitions()
        finally:
            self._exit_lock()

    # ------------------------------------------------------------------
    # Public API: Re-expand (ARCHIVED → COLD)
    # ------------------------------------------------------------------

    def reexpand_topic(self, topic_id: str) -> TopicEntry:
        """Re-expand an archived topic to COLD state (v2.0: summary only)."""
        self._enter_lock()
        try:
            registry = self._load_registry()
            data = registry["topics"].get(topic_id)
            if data is None:
                raise KeyError(f"Topic not found: {topic_id}")

            entry = TopicEntry.from_dict(data)
            if entry.state != TopicState.ARCHIVED.value:
                raise ValueError(
                    f"Only archived topics can be re-expanded, got: {entry.state}"
                )

            entry.state = TopicState.COLD.value
            entry.compactions_since_last_access = 0
            entry.last_seen_at = self._now()

            registry["topics"][topic_id] = entry.to_dict()
            registry["updated_at"] = self._now()
            self._save_registry(registry)
            return entry
        finally:
            self._exit_lock()

    # ------------------------------------------------------------------
    # Public API: Registry metadata
    # ------------------------------------------------------------------

    def get_session_id(self) -> Optional[str]:
        registry = self._load_registry()
        return registry.get("session_id")

    def set_session_id(self, session_id: str) -> None:
        self._enter_lock()
        try:
            registry = self._load_registry()
            registry["session_id"] = session_id
            registry["updated_at"] = self._now()
            self._save_registry(registry)
        finally:
            self._exit_lock()

    def get_compaction_count(self) -> int:
        registry = self._load_registry()
        return registry.get("compaction_count", 0)

    def get_registry_metadata(self) -> Dict[str, Any]:
        """Return registry-level metadata (version, counts, timestamps)."""
        registry = self._load_registry()
        return {
            "version": registry.get("version", self.VERSION),
            "session_id": registry.get("session_id"),
            "compaction_count": registry.get("compaction_count", 0),
            "last_compaction_id": registry.get("last_compaction_id"),
            "topic_count": len(registry.get("topics", {})),
            "config_hash": registry.get("config_hash", ""),
            "created_at": registry.get("created_at", ""),
            "updated_at": registry.get("updated_at", ""),
        }

    # ------------------------------------------------------------------
    # Public API: Migration from v1
    # ------------------------------------------------------------------

    def migrate_from_v1(self, v1_registry_data: Dict[str, Any]) -> int:
        """Migrate v1 registry data into v2 format.

        v1 format: {"version": 1, "active_topic": str|null, "topics": {id: {title, status, ...}}, "links": [...]}
        Returns the number of topics migrated.
        """
        self._enter_lock()
        try:
            registry = self._load_registry()
            now = self._now()
            migrated = 0

            v1_active = v1_registry_data.get("active_topic")
            v1_topics = v1_registry_data.get("topics", {})

            for topic_id, v1_entry in v1_topics.items():
                if topic_id in registry["topics"]:
                    continue  # already exists in v2

                # Map v1 status to v2 state
                v1_status = v1_entry.get("status", "active")
                if v1_status == "archived":
                    state = TopicState.ARCHIVED.value
                elif topic_id == v1_active:
                    state = TopicState.ACTIVE.value
                else:
                    state = TopicState.WARM.value

                entry = TopicEntry(
                    topic_id=topic_id,
                    label=v1_entry.get("title", topic_id),
                    state=state,
                    description="",
                    first_seen_at=v1_entry.get("created_at", now),
                    last_seen_at=v1_entry.get("updated_at", now),
                    last_access_message_idx=0,
                    message_count=0,
                    compactions_since_last_access=0,
                )

                registry["topics"][topic_id] = entry.to_dict()
                migrated += 1

            registry["updated_at"] = now
            self._save_registry(registry)
            return migrated
        finally:
            self._exit_lock()

    # ------------------------------------------------------------------
    # Internal: State transition logic
    # ------------------------------------------------------------------

    def _compute_transition(
        self,
        entry: TopicEntry,
        current_message_idx: int,
        has_multiple_active: bool,
    ) -> Optional[str]:
        """Determine if a topic should transition. Returns new state or None."""

        if entry.state == TopicState.ACTIVE.value:
            # ACTIVE → WARM: message gap exceeded AND other active topics exist
            msg_gap = current_message_idx - entry.last_access_message_idx
            if msg_gap > self.config.active_threshold_messages and has_multiple_active:
                return TopicState.WARM.value

        elif entry.state == TopicState.WARM.value:
            # WARM → COLD: compactions_since >= threshold
            if (
                entry.compactions_since_last_access
                >= self.config.warm_to_cold_compactions
            ):
                return TopicState.COLD.value

        elif entry.state == TopicState.COLD.value:
            # COLD → ARCHIVED: compactions_since >= threshold
            if (
                entry.compactions_since_last_access
                >= self.config.cold_to_archived_compactions
            ):
                return TopicState.ARCHIVED.value

        return None

    def _check_compaction_transitions(self) -> List[Dict[str, Any]]:
        """Check transitions that depend on compaction counts (WARM→COLD, COLD→ARCHIVED)."""
        registry = self._load_registry()
        transitions: List[Dict[str, Any]] = []

        for topic_id, data in list(registry["topics"].items()):
            entry = TopicEntry.from_dict(data)

            if entry.state == TopicState.WARM.value:
                if (
                    entry.compactions_since_last_access
                    >= self.config.warm_to_cold_compactions
                ):
                    entry.state = TopicState.COLD.value
                    entry.last_raw_exchange = None
                    registry["topics"][topic_id] = entry.to_dict()
                    transitions.append(
                        {
                            "topic_id": topic_id,
                            "from": TopicState.WARM.value,
                            "to": TopicState.COLD.value,
                            "reason": f"compactions_since={entry.compactions_since_last_access} >= {self.config.warm_to_cold_compactions}",
                        }
                    )

            elif entry.state == TopicState.COLD.value:
                if (
                    entry.compactions_since_last_access
                    >= self.config.cold_to_archived_compactions
                ):
                    entry.state = TopicState.ARCHIVED.value
                    registry["topics"][topic_id] = entry.to_dict()
                    transitions.append(
                        {
                            "topic_id": topic_id,
                            "from": TopicState.COLD.value,
                            "to": TopicState.ARCHIVED.value,
                            "reason": f"compactions_since={entry.compactions_since_last_access} >= {self.config.cold_to_archived_compactions}",
                        }
                    )

        if transitions:
            registry["updated_at"] = self._now()
            self._save_registry(registry)

        return transitions

    def _transition_reason(
        self, from_state: str, to_state: str, entry: TopicEntry
    ) -> str:
        if from_state == TopicState.ACTIVE.value and to_state == TopicState.WARM.value:
            return f"message_gap exceeded active_threshold ({self.config.active_threshold_messages})"
        if from_state == TopicState.WARM.value and to_state == TopicState.COLD.value:
            return f"compactions_since={entry.compactions_since_last_access}"
        if (
            from_state == TopicState.COLD.value
            and to_state == TopicState.ARCHIVED.value
        ):
            return f"compactions_since={entry.compactions_since_last_access}"
        return f"{from_state} → {to_state}"

    # ------------------------------------------------------------------
    # Internal: Persistence
    # ------------------------------------------------------------------

    def _empty_registry(self) -> Dict[str, Any]:
        now = self._now()
        return {
            "version": self.VERSION,
            "topics": {},
            "session_id": None,
            "last_compaction_id": None,
            "compaction_count": 0,
            "created_at": now,
            "updated_at": now,
            "config_hash": self.config.config_hash(),
        }

    def _load_registry(self) -> Dict[str, Any]:
        if not self.registry_path.exists():
            return self._empty_registry()

        with open(self.registry_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        if not isinstance(data, dict):
            raise ValueError("Invalid registry payload")

        # Detect v1 format and auto-migrate
        version = data.get("version")
        if version is None or (isinstance(version, int) and version == 1):
            from migration_v1_to_v2 import migrate_registry

            data, _state = migrate_registry(self.base_dir)

        # Ensure required fields
        data.setdefault("version", self.VERSION)
        data.setdefault("topics", {})
        data.setdefault("session_id", None)
        data.setdefault("last_compaction_id", None)
        data.setdefault("compaction_count", 0)
        data.setdefault("created_at", self._now())
        data.setdefault("updated_at", self._now())
        data.setdefault("config_hash", "")

        return data

    def _save_registry(self, data: Dict[str, Any]) -> None:
        """Atomic write: write to .tmp then rename."""
        self.base_dir.mkdir(parents=True, exist_ok=True)
        tmp_path = Path(str(self.registry_path) + ".tmp")
        with open(tmp_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            f.write("\n")
        os.replace(tmp_path, self.registry_path)

    def _backup_registry(self, compaction_id: str) -> None:
        """Backup current registry before compaction."""
        if not self.registry_path.exists():
            return
        self.backups_dir.mkdir(parents=True, exist_ok=True)
        backup_path = self.backups_dir / f"{compaction_id}.json"
        shutil.copy2(self.registry_path, backup_path)

    # ------------------------------------------------------------------
    # Internal: Utilities
    # ------------------------------------------------------------------

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def _enter_lock(self) -> None:
        thread_id = threading.get_ident()
        if self._lock_owner == thread_id:
            self._lock_depth += 1
            return
        self._lock.acquire()
        self._lock_owner = thread_id
        self._lock_depth = 1

    def _exit_lock(self) -> None:
        thread_id = threading.get_ident()
        if self._lock_owner != thread_id:
            raise RuntimeError("Lock owned by another thread")
        self._lock_depth -= 1
        if self._lock_depth == 0:
            self._lock_owner = None
            self._lock.release()
