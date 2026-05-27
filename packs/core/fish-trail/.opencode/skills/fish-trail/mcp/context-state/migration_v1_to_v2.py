"""V1 → V2 Topic Registry Migration.

Handles detection, migration, and state tracking for upgrading from
TopicStore (v1) registry format to TopicRegistryV2 (v2) format.

Migration is idempotent: running on an already-v2 registry is a no-op.
"""

import json
import os
import shutil
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


class MigrationState(str, Enum):
    """Tracks the overall migration lifecycle."""

    V1_ONLY = "v1_only"  # No v2 registry exists; v1 is authoritative
    MIGRATED = "migrated"  # Successfully migrated from v1 to v2
    V2_ONLY = "v2_only"  # Clean v2 installation (no v1 history)


class MigrationError(Exception):
    """Raised when migration encounters an unrecoverable problem."""


def detect_registry_version(registry_path: Path) -> Optional[str]:
    """Detect registry format version from file.

    Returns:
        "1" for v1 format, "2.0" for v2 format, None if file doesn't exist.

    Raises:
        MigrationError: If file exists but format is unrecognizable.
    """
    if not registry_path.exists():
        return None

    with open(registry_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, dict):
        raise MigrationError("Registry file is not a JSON object")

    version = data.get("version")

    if version == 1 or version == "1":
        return "1"
    elif version == "2.0":
        return "2.0"
    elif version is None:
        # No version field — assume v1 (legacy files before version was added)
        return "1"
    else:
        raise MigrationError(f"Unknown registry version: {version!r}")


def detect_migration_state(base_dir: Path) -> MigrationState:
    """Determine current migration state from filesystem.

    Args:
        base_dir: The .petfish/fish-trail/ directory.
    """
    registry_path = base_dir / "topic-registry.json"
    version = detect_registry_version(registry_path)

    if version is None:
        return MigrationState.V2_ONLY  # No registry yet, will create as v2
    elif version == "1":
        return MigrationState.V1_ONLY
    else:
        # Check if migration marker exists
        marker_path = base_dir / ".migration-v1-to-v2.json"
        if marker_path.exists():
            return MigrationState.MIGRATED
        return MigrationState.V2_ONLY


def _load_v1_topic_file(topics_dir: Path, topic_id: str) -> Optional[Dict[str, Any]]:
    """Load an individual v1 topic file.

    V1 stores full topic data in topics/{topic_id}.json with fields:
    id, title, scope, status, parent, summary, created_at, updated_at, tags, metadata.
    """
    topic_path = topics_dir / f"{topic_id}.json"
    if not topic_path.exists():
        return None

    with open(topic_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, dict):
        return None
    return data


def _map_v1_status_to_v2_state(v1_status: str) -> str:
    """Map v1 status string to v2 TopicState value."""
    mapping = {
        "active": "active",
        "paused": "warm",
        "archived": "archived",
    }
    return mapping.get(v1_status, "active")


def _migrate_topic_entry(
    topic_id: str,
    registry_entry: Dict[str, Any],
    topic_file_data: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    """Convert a v1 topic to v2 TopicEntry dict format.

    Args:
        topic_id: The topic ID.
        registry_entry: The minimal entry from v1 registry (title, status, created_at, updated_at).
        topic_file_data: Full topic data from topics/{id}.json (may be None if file missing).
    """
    # Prefer topic file data over registry entry (more complete)
    source = topic_file_data or registry_entry

    title = source.get("title", registry_entry.get("title", topic_id))
    status = source.get("status", registry_entry.get("status", "active"))
    created_at = source.get("created_at", registry_entry.get("created_at", ""))
    updated_at = source.get("updated_at", registry_entry.get("updated_at", ""))

    # Fields only available from topic file
    scope = source.get("scope", "") if topic_file_data else ""
    parent = source.get("parent") if topic_file_data else None
    summary = source.get("summary", "") if topic_file_data else None
    tags = source.get("tags", []) if topic_file_data else []

    return {
        "topic_id": topic_id,
        "label": title,
        "state": _map_v1_status_to_v2_state(status),
        "description": scope,
        "parent_topic_id": parent,
        "first_seen_at": created_at,
        "last_seen_at": updated_at,
        "last_access_message_idx": 0,
        "message_count": 0,
        "compactions_since_last_access": 0,
        "never_consolidate_items": [],
        "priority_boost": 0.0,
        "summary": summary if summary else None,
        "key_decisions": [],
        "last_raw_exchange": None,
    }


def migrate_registry(
    base_dir: Path,
    backup: bool = True,
) -> Tuple[Dict[str, Any], MigrationState]:
    """Migrate a v1 registry to v2 format.

    Args:
        base_dir: The .petfish/fish-trail/ directory.
        backup: If True, create a backup of v1 registry before overwriting.

    Returns:
        Tuple of (v2_registry_dict, resulting_migration_state).

    Raises:
        MigrationError: If migration fails.
    """
    registry_path = base_dir / "topic-registry.json"
    topics_dir = base_dir / "topics"

    # Detect current version
    version = detect_registry_version(registry_path)

    if version is None:
        # No registry — return empty v2
        now = datetime.now(timezone.utc).isoformat()
        return {
            "version": "2.0",
            "topics": {},
            "session_id": None,
            "last_compaction_id": None,
            "compaction_count": 0,
            "created_at": now,
            "updated_at": now,
            "config_hash": "",
        }, MigrationState.V2_ONLY

    if version == "2.0":
        # Already v2 — load and return as-is
        with open(registry_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data, MigrationState.V2_ONLY

    # === V1 → V2 Migration ===

    # Load v1 registry
    with open(registry_path, "r", encoding="utf-8") as f:
        v1_registry = json.load(f)

    v1_topics = v1_registry.get("topics", {})

    # Backup v1 registry
    if backup:
        backup_path = base_dir / "topic-registry.v1.backup.json"
        shutil.copy2(registry_path, backup_path)

    # Migrate each topic
    now = datetime.now(timezone.utc).isoformat()
    v2_topics: Dict[str, Any] = {}

    for topic_id, registry_entry in v1_topics.items():
        # Load full topic data from individual file
        topic_file_data = _load_v1_topic_file(topics_dir, topic_id)
        v2_topics[topic_id] = _migrate_topic_entry(
            topic_id, registry_entry, topic_file_data
        )

    # Build v2 registry
    v2_registry: Dict[str, Any] = {
        "version": "2.0",
        "topics": v2_topics,
        "session_id": None,
        "last_compaction_id": None,
        "compaction_count": 0,
        "created_at": v1_registry.get(
            "created_at", now
        ),  # v1 doesn't have this, fallback
        "updated_at": now,
        "config_hash": "",
    }

    # Write migration marker
    marker_path = base_dir / ".migration-v1-to-v2.json"
    marker = {
        "migrated_at": now,
        "v1_topic_count": len(v1_topics),
        "v2_topic_count": len(v2_topics),
        "v1_active_topic": v1_registry.get("active_topic"),
        "v1_links_count": len(v1_registry.get("links", [])),
        "backup_path": str(backup_path) if backup else None,
    }

    # Atomic write marker
    marker_tmp = Path(str(marker_path) + ".tmp")
    with open(marker_tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f, ensure_ascii=False, indent=2)
        f.write("\n")
    os.replace(marker_tmp, marker_path)

    # Atomic write v2 registry
    registry_tmp = Path(str(registry_path) + ".tmp")
    with open(registry_tmp, "w", encoding="utf-8") as f:
        json.dump(v2_registry, f, ensure_ascii=False, indent=2)
        f.write("\n")
    os.replace(registry_tmp, registry_path)

    return v2_registry, MigrationState.MIGRATED


def get_migration_info(base_dir: Path) -> Optional[Dict[str, Any]]:
    """Read migration marker if it exists."""
    marker_path = base_dir / ".migration-v1-to-v2.json"
    if not marker_path.exists():
        return None
    with open(marker_path, "r", encoding="utf-8") as f:
        return json.load(f)
