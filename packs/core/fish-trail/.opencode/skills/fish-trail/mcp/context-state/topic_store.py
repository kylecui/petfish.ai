"""JSON-backed topic persistence for the Context Router MCP server."""

import json
import os
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


class TopicStore:
    """Persist topics, topic links, and routing decisions under .petfish/fish-trail/."""

    VALID_RELATIONS = {
        # Detection relations (from topic_detect)
        "continue",
        "fork",
        "switch",
        "merge",
        "archive",
        "reset",
        "bridge",
        # Semantic relations (user-defined)
        "related",
        "depends_on",
        "blocks",
        "parent",
        "child",
    }

    def __init__(self, base_dir: str):
        self.base_dir = Path(base_dir)
        self.topics_dir = self.base_dir / "topics"
        self.contexts_dir = self.base_dir / "contexts"
        self.decisions_dir = self.base_dir / "decisions"
        self.registry_path = self.base_dir / "topic-registry.json"
        self.decision_log_path = self.decisions_dir / "decision-log.json"

        self._lock = threading.Lock()
        self._lock_owner = None
        self._lock_depth = 0

        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.topics_dir.mkdir(parents=True, exist_ok=True)
        self.contexts_dir.mkdir(parents=True, exist_ok=True)
        self.decisions_dir.mkdir(parents=True, exist_ok=True)

        if not self.registry_path.exists():
            self._atomic_write(self.registry_path, self._empty_registry())
        if not self.decision_log_path.exists():
            self._atomic_write(self.decision_log_path, [])

    def create(
        self,
        title: str,
        scope: str,
        parent: Optional[str] = None,
        tags: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        self._enter_lock()
        try:
            registry = self._load_registry()

            if parent is not None and self.get(parent) is None:
                raise KeyError("topic not found: {0}".format(parent))

            topic_id = self._generate_topic_id(registry)
            timestamp = self._now()
            topic = {
                "id": topic_id,
                "title": title,
                "scope": scope,
                "status": "active",
                "parent": parent,
                "summary": "",
                "created_at": timestamp,
                "updated_at": timestamp,
                "tags": list(tags or []),
                "metadata": {},
            }

            self._atomic_write(self._topic_path(topic_id), topic)
            registry["topics"][topic_id] = self._registry_entry(topic)
            if registry.get("active_topic") is None:
                registry["active_topic"] = topic_id
            self._atomic_write(self.registry_path, registry)
            return topic
        finally:
            self._exit_lock()

    def get(self, topic_id: str) -> Optional[Dict[str, Any]]:
        path = self._topic_path(topic_id)
        if not path.exists():
            return None
        data = self._read_json(path)
        if not isinstance(data, dict):
            raise ValueError("invalid topic payload: {0}".format(topic_id))
        return data

    def list_topics(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        registry = self._load_registry()
        items = []

        for topic_id, entry in registry.get("topics", {}).items():
            if not isinstance(entry, dict):
                continue
            if status is not None and entry.get("status") != status:
                continue

            item = {"id": topic_id}
            item.update(entry)
            items.append(item)

        return sorted(items, key=lambda item: item.get("updated_at", ""), reverse=True)

    def update(self, topic_id: str, **fields: Any) -> Dict[str, Any]:
        self._enter_lock()
        try:
            topic = self.get(topic_id)
            if topic is None:
                raise KeyError("topic not found: {0}".format(topic_id))

            for key, value in fields.items():
                if key in {"id", "created_at"}:
                    continue
                topic[key] = value

            topic["updated_at"] = self._now()
            self._atomic_write(self._topic_path(topic_id), topic)

            registry = self._load_registry()
            registry["topics"][topic_id] = self._registry_entry(topic)
            if (
                topic.get("status") == "archived"
                and registry.get("active_topic") == topic_id
            ):
                registry["active_topic"] = None
            self._atomic_write(self.registry_path, registry)
            return topic
        finally:
            self._exit_lock()

    def archive(self, topic_id: str) -> Dict[str, Any]:
        return self.update(topic_id, status="archived")

    def search(self, query: str) -> List[Dict[str, Any]]:
        needle = query.strip().lower()
        matches = []

        for item in self.list_topics():
            topic = self.get(item["id"])
            if topic is None:
                continue

            if not needle:
                matches.append(topic)
                continue

            fields = [
                topic.get("title", ""),
                topic.get("scope", ""),
                topic.get("summary", ""),
                " ".join(str(tag) for tag in topic.get("tags", []) or []),
            ]
            haystack = "\n".join(str(value).lower() for value in fields)
            if needle in haystack:
                matches.append(topic)

        return sorted(
            matches, key=lambda item: item.get("updated_at", ""), reverse=True
        )

    def link(self, source: str, target: str, relation: str) -> Dict[str, Any]:
        if relation not in self.VALID_RELATIONS:
            raise ValueError("invalid relation: {0}".format(relation))
        if self.get(source) is None:
            raise KeyError("topic not found: {0}".format(source))
        if self.get(target) is None:
            raise KeyError("topic not found: {0}".format(target))

        self._enter_lock()
        try:
            registry = self._load_registry()
            created_at = self._now()
            link_entry = {
                "source": source,
                "target": target,
                "relation": relation,
                "created_at": created_at,
            }

            links = []
            replaced = False
            for existing in registry.get("links", []):
                if (
                    existing.get("source") == source
                    and existing.get("target") == target
                ):
                    if not replaced:
                        links.append(link_entry)
                        replaced = True
                    continue
                links.append(existing)

            if not replaced:
                links.append(link_entry)

            registry["links"] = links
            self._atomic_write(self.registry_path, registry)
            return link_entry
        finally:
            self._exit_lock()

    def unlink(self, source: str, target: str) -> bool:
        self._enter_lock()
        try:
            registry = self._load_registry()
            original_links = registry.get("links", [])
            filtered_links = [
                link
                for link in original_links
                if not (link.get("source") == source and link.get("target") == target)
            ]

            found = len(filtered_links) != len(original_links)
            if found:
                registry["links"] = filtered_links
                self._atomic_write(self.registry_path, registry)
            return found
        finally:
            self._exit_lock()

    def graph(self) -> Dict[str, Any]:
        registry = self._load_registry()
        nodes = []

        for topic_id, entry in registry.get("topics", {}).items():
            if not isinstance(entry, dict):
                continue
            node = {"id": topic_id}
            node.update(entry)
            nodes.append(node)

        nodes.sort(key=lambda item: item.get("updated_at", ""), reverse=True)
        return {
            "version": registry.get("version", 1),
            "nodes": nodes,
            "edges": list(registry.get("links", [])),
        }

    def get_active(self) -> Optional[Dict[str, Any]]:
        registry = self._load_registry()
        topic_id = registry.get("active_topic")
        if not topic_id:
            return None
        return self.get(topic_id)

    def set_active(self, topic_id: str) -> None:
        if self.get(topic_id) is None:
            raise KeyError("topic not found: {0}".format(topic_id))

        self._enter_lock()
        try:
            registry = self._load_registry()
            registry["active_topic"] = topic_id
            self._atomic_write(self.registry_path, registry)
        finally:
            self._exit_lock()

    def recommend_related(self, topic_id: str, max_depth: int = 2) -> Dict[str, Any]:
        """Walk the topic graph from topic_id up to max_depth hops.

        Returns related topics ranked by proximity (closer = higher rank),
        with relation paths and topic summaries.
        """
        graph = self.graph()
        edges = graph.get("edges", [])

        # BFS from topic_id
        visited = {topic_id}
        queue = [(topic_id, 0)]  # (id, depth)
        results = []  # (other_id, depth, relation, via_id)

        while queue:
            current_id, depth = queue.pop(0)
            if depth >= max_depth:
                continue
            for edge in edges:
                source = edge.get("source")
                target = edge.get("target")
                relation = edge.get("relation", "related")
                other_id = None
                if source == current_id and target not in visited:
                    other_id = target
                elif target == current_id and source not in visited:
                    other_id = source
                if other_id:
                    visited.add(other_id)
                    results.append((other_id, depth + 1, relation, current_id))
                    queue.append((other_id, depth + 1))

        # Enrich with topic data
        recommendations = []
        for other_id, depth, relation, via_id in results:
            topic = self.get(other_id)
            if topic is None:
                continue
            recommendations.append(
                {
                    "topic_id": other_id,
                    "title": topic.get("title", other_id),
                    "status": topic.get("status"),
                    "relation": relation,
                    "depth": depth,
                    "via": via_id if via_id != topic_id else None,
                    "summary": topic.get("summary", ""),
                    "tags": topic.get("tags", []),
                }
            )

        # Sort by depth (closer first), then by title
        recommendations.sort(key=lambda r: (r["depth"], r.get("title", "")))

        return {
            "source_topic_id": topic_id,
            "recommendations": recommendations,
            "total": len(recommendations),
        }

    def log_decision(self, entry: Dict[str, Any]) -> Dict[str, Any]:
        self._enter_lock()
        try:
            decisions = self._load_decisions()
            record = dict(entry)
            record["timestamp"] = self._now()
            decisions.append(record)
            self._atomic_write(self.decision_log_path, decisions)
            return record
        finally:
            self._exit_lock()

    def get_decisions(
        self,
        topic_id: Optional[str] = None,
        session_id: Optional[str] = None,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        decisions = self._load_decisions()
        if topic_id is not None:
            decisions = [
                entry
                for entry in decisions
                if entry.get("source_topic") == topic_id
                or entry.get("target_topic") == topic_id
            ]

        if session_id is not None:
            decisions = [
                entry for entry in decisions if entry.get("session_id") == session_id
            ]

        if limit <= 0:
            return []
        return decisions[-limit:]

    def _atomic_write(self, path: Path, data: Any) -> None:
        self._enter_lock()
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            tmp_path = Path(str(path) + ".tmp")
            with open(tmp_path, "w", encoding="utf-8") as handle:
                json.dump(data, handle, ensure_ascii=False, indent=2)
                handle.write("\n")
            os.replace(tmp_path, path)
        finally:
            self._exit_lock()

    def _read_json(self, path: Path, default: Any = None) -> Any:
        if not path.exists():
            return default
        with open(path, "r", encoding="utf-8") as handle:
            return json.load(handle)

    def _load_registry(self) -> Dict[str, Any]:
        registry = self._read_json(self.registry_path, self._empty_registry())
        if not isinstance(registry, dict):
            raise ValueError("invalid registry payload")

        registry.setdefault("version", 1)
        registry.setdefault("active_topic", None)
        registry.setdefault("topics", {})
        registry.setdefault("links", [])

        # v1→v2 migration: topics was array, convert to dict keyed by id (#175)
        if isinstance(registry["topics"], list):
            registry["topics"] = {
                t["id"]: t for t in registry["topics"]
                if isinstance(t, dict) and "id" in t
            }

        if not isinstance(registry["topics"], dict):
            raise ValueError("invalid registry topics payload")
        if not isinstance(registry["links"], list):
            raise ValueError("invalid registry links payload")

        return registry

    def _load_decisions(self) -> List[Dict[str, Any]]:
        decisions = self._read_json(self.decision_log_path, [])
        if not isinstance(decisions, list):
            raise ValueError("invalid decision log payload")
        return decisions

    def _topic_path(self, topic_id: str) -> Path:
        self._validate_topic_id(topic_id)
        return self.topics_dir / "{0}.json".format(topic_id)

    def _generate_topic_id(self, registry: Dict[str, Any]) -> str:
        prefix = datetime.now(timezone.utc).strftime("%Y%m%d")
        while True:
            topic_id = "topic_{0}_{1}".format(prefix, os.urandom(2).hex())
            if (
                topic_id not in registry.get("topics", {})
                and not self._topic_path(topic_id).exists()
            ):
                return topic_id

    def _registry_entry(self, topic: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "title": topic.get("title", ""),
            "status": topic.get("status", "active"),
            "created_at": topic.get("created_at", ""),
            "updated_at": topic.get("updated_at", ""),
        }

    def _empty_registry(self) -> Dict[str, Any]:
        return {
            "version": 1,
            "active_topic": None,
            "topics": {},
            "links": [],
        }

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def _validate_topic_id(self, topic_id: str) -> None:
        if not topic_id:
            raise ValueError("topic_id is required")

        separators = [os.sep]
        if os.altsep:
            separators.append(os.altsep)

        if any(separator in topic_id for separator in separators):
            raise ValueError("invalid topic_id: {0}".format(topic_id))
        if ".." in topic_id:
            raise ValueError("invalid topic_id: {0}".format(topic_id))

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
            raise RuntimeError("lock owned by another thread")

        self._lock_depth -= 1
        if self._lock_depth == 0:
            self._lock_owner = None
            self._lock.release()
