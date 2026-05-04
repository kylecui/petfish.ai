"""JSON-backed session persistence for the Context Router MCP server."""

import json
import os
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


class SessionStore:
    def __init__(self, base_dir: str):
        self.base_dir = Path(base_dir)
        self.sessions_dir = self.base_dir / "sessions"
        self.sessions_dir.mkdir(parents=True, exist_ok=True)
        self.index_path = self.sessions_dir / "index.json"

        self._lock = threading.Lock()
        self._lock_owner = None
        self._lock_depth = 0
        self._sessions_dir_resolved = self.sessions_dir.resolve()

        if self.index_path.exists():
            index = self._read_json(self.index_path)
            needs_write = False
            if not isinstance(index, dict):
                index = self._empty_index()
                needs_write = True
            if not isinstance(index.get("sessions"), dict):
                index["sessions"] = {}
                needs_write = True
            if index.get("version") != 1:
                index["version"] = 1
                needs_write = True
            self._index = index
            if needs_write:
                self._atomic_write(self.index_path, self._index)
        else:
            self._index = self._empty_index()
            self._atomic_write(self.index_path, self._index)

    def bind(self, external_session_id=None, topic_id=None, metadata=None) -> dict:
        self._enter_lock()
        try:
            if external_session_id is not None:
                session_id = "oc_{}".format(external_session_id)
                session = self._load_session(session_id)
                if session is not None:
                    changed = False
                    now = self._now()
                    if topic_id is not None:
                        session["active_topic_id"] = topic_id
                        self._ensure_topic_ref(session, topic_id, now, increment=False)
                        changed = True
                    if metadata is not None:
                        session["metadata"] = self._merge_metadata(
                            session.get("metadata"), metadata
                        )
                        changed = True
                    if changed:
                        session["last_activity_at"] = now
                        self._persist_session(session)
                    return session
            else:
                session_id = self._new_inferred_session_id()

            now = self._now()
            if external_session_id is not None:
                session_id = "oc_{}".format(external_session_id)

            session = {
                "id": session_id,
                "external_id": external_session_id,
                "source": "external" if external_session_id is not None else "inferred",
                "status": "active",
                "started_at": now,
                "last_activity_at": now,
                "ended_at": None,
                "active_topic_id": None,
                "topic_refs": [],
                "timeline": [],
                "summary": "",
                "inherited_from": None,
                "metadata": dict(metadata or {}),
            }

            if topic_id is not None:
                session["active_topic_id"] = topic_id
                self._ensure_topic_ref(session, topic_id, now, increment=False)

            self._persist_session(session)
            return session
        finally:
            self._exit_lock()

    def get(self, session_id: str) -> Optional[dict]:
        session = self._load_session(session_id)
        if isinstance(session, dict):
            return session
        return None

    def list_sessions(
        self, topic_id=None, since=None, status=None, limit: Optional[int] = 50
    ) -> list:
        items = []
        sessions = self._index.get("sessions", {})

        for session_id, entry in sessions.items():
            if status is not None and entry.get("status") != status:
                continue

            last_activity_at = entry.get("last_activity_at") or ""
            if since is not None and last_activity_at < since:
                continue

            if topic_id is not None:
                matches_topic = entry.get("active_topic_id") == topic_id
                if not matches_topic:
                    session = self._load_session(session_id)
                    if session is None:
                        continue
                    for topic_ref in session.get("topic_refs", []):
                        if topic_ref.get("topic_id") == topic_id:
                            matches_topic = True
                            break
                if not matches_topic:
                    continue

            item = dict(entry)
            item["id"] = session_id
            items.append(item)

        items.sort(key=lambda value: value.get("last_activity_at") or "", reverse=True)

        if limit is None:
            return items
        if limit <= 0:
            return []
        return items[:limit]

    def resume(self, topic_id=None, session_id=None) -> dict:
        if session_id is not None:
            session = self.get(session_id)
            if session is None:
                raise KeyError(session_id)
            return {
                "session": session,
                "topic_id": session.get("active_topic_id"),
            }

        if topic_id is not None:
            for item in self.list_sessions(topic_id=topic_id, limit=None):
                session = self.get(item.get("id"))
                if session is None:
                    continue
                for topic_ref in session.get("topic_refs", []):
                    if topic_ref.get("topic_id") == topic_id:
                        return {
                            "session": session,
                            "topic_id": topic_id,
                        }
                if session.get("active_topic_id") == topic_id:
                    return {
                        "session": session,
                        "topic_id": topic_id,
                    }
            raise KeyError(topic_id)

        items = self.list_sessions(status="active", limit=None)
        if not items:
            items = self.list_sessions(limit=None)
        if not items:
            raise KeyError("session")

        session = self.get(items[0].get("id"))
        if session is None:
            raise KeyError(items[0].get("id"))

        return {
            "session": session,
            "topic_id": session.get("active_topic_id"),
        }

    def add_event(
        self, session_id: str, event_type: str, topic_id=None, **fields
    ) -> dict:
        self._enter_lock()
        try:
            session = self._require_session(session_id)
            now = self._now()

            event = {
                "ts": now,
                "type": event_type,
            }
            if topic_id is not None:
                event["topic_id"] = topic_id

            for key, value in fields.items():
                if key in ("ts", "type", "topic_id"):
                    continue
                event[key] = value

            timeline = session.get("timeline")
            if not isinstance(timeline, list):
                timeline = []
                session["timeline"] = timeline
            timeline.append(event)

            session["last_activity_at"] = now
            if topic_id is not None:
                session["active_topic_id"] = topic_id
                self._ensure_topic_ref(session, topic_id, now, increment=True)

            self._persist_session(session)
            return event
        finally:
            self._exit_lock()

    def close(self, session_id: str, summary=None) -> dict:
        self._enter_lock()
        try:
            session = self._require_session(session_id)
            now = self._now()

            session["status"] = "closed"
            session["ended_at"] = now
            session["last_activity_at"] = now
            if summary is not None:
                session["summary"] = summary

            self._persist_session(session)
            return session
        finally:
            self._exit_lock()

    def update(self, session_id: str, **fields) -> dict:
        self._enter_lock()
        try:
            session = self._require_session(session_id)
            now = self._now()

            for key, value in fields.items():
                if key == "metadata":
                    if value is None:
                        session["metadata"] = {}
                    else:
                        session["metadata"] = self._merge_metadata(
                            session.get("metadata"), value
                        )
                    continue
                session[key] = value

            active_topic_id = session.get("active_topic_id")
            if active_topic_id is not None:
                self._ensure_topic_ref(session, active_topic_id, now, increment=False)

            session["last_activity_at"] = now
            self._persist_session(session)
            return session
        finally:
            self._exit_lock()

    def _empty_index(self) -> Dict[str, Any]:
        return {
            "version": 1,
            "sessions": {},
        }

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def _new_inferred_session_id(self) -> str:
        stamp = datetime.now(timezone.utc).strftime("%Y%m%d")
        while True:
            session_id = "inf_{}_{}".format(stamp, os.urandom(2).hex())
            if session_id not in self._index.get("sessions", {}):
                if not self._session_path(session_id).exists():
                    return session_id

    def _index_entry(self, session: Dict[str, Any]) -> Dict[str, Any]:
        timeline = session.get("timeline")
        if not isinstance(timeline, list):
            timeline = []
        return {
            "status": session.get("status"),
            "source": session.get("source"),
            "started_at": session.get("started_at"),
            "last_activity_at": session.get("last_activity_at"),
            "active_topic_id": session.get("active_topic_id"),
            "event_count": len(timeline),
        }

    def _session_path(self, session_id):
        session_id = self._validate_session_id(session_id)
        return self.sessions_dir / "{}.json".format(session_id)

    def _validate_session_id(self, session_id):
        if not isinstance(session_id, str) or not session_id:
            raise ValueError("session_id must be a non-empty string")
        if session_id in (".", ".."):
            raise ValueError("invalid session_id")
        if os.path.sep and os.path.sep in session_id:
            raise ValueError("invalid session_id")
        if os.path.altsep and os.path.altsep in session_id:
            raise ValueError("invalid session_id")
        if ".." in session_id:
            raise ValueError("invalid session_id")

        candidate = (self.sessions_dir / "{}.json".format(session_id)).resolve()
        if candidate.parent != self._sessions_dir_resolved:
            raise ValueError("invalid session_id")
        return session_id

    def _enter_lock(self):
        thread_id = threading.get_ident()
        if self._lock_owner == thread_id:
            self._lock_depth += 1
            return

        self._lock.acquire()
        self._lock_owner = thread_id
        self._lock_depth = 1

    def _exit_lock(self):
        thread_id = threading.get_ident()
        if self._lock_owner != thread_id or self._lock_depth == 0:
            raise RuntimeError("lock not owned by current thread")

        self._lock_depth -= 1
        if self._lock_depth == 0:
            self._lock_owner = None
            self._lock.release()

    def _read_json(self, path):
        with Path(path).open("r", encoding="utf-8") as handle:
            return json.load(handle)

    def _atomic_write(self, path, data):
        path = Path(path)
        tmp_path = Path("{}.tmp".format(path))
        with tmp_path.open("w", encoding="utf-8") as handle:
            json.dump(data, handle, ensure_ascii=False, indent=2, sort_keys=True)
            handle.write("\n")
        os.replace(str(tmp_path), str(path))

    def _load_session(self, session_id):
        path = self._session_path(session_id)
        if not path.exists():
            return None
        data = self._read_json(path)
        if isinstance(data, dict):
            return data
        return None

    def _require_session(self, session_id):
        session = self._load_session(session_id)
        if session is None:
            raise KeyError(session_id)
        return session

    def _persist_session(self, session):
        session_id = session.get("id")
        if not session_id:
            raise ValueError("session is missing id")

        self._atomic_write(self._session_path(session_id), session)
        self._index["sessions"][session_id] = self._index_entry(session)
        self._atomic_write(self.index_path, self._index)

    def _ensure_topic_ref(self, session, topic_id, seen_at, increment=False):
        topic_refs = session.get("topic_refs")
        if not isinstance(topic_refs, list):
            topic_refs = []
            session["topic_refs"] = topic_refs

        for topic_ref in topic_refs:
            if topic_ref.get("topic_id") == topic_id:
                if not topic_ref.get("first_seen_at"):
                    topic_ref["first_seen_at"] = seen_at
                topic_ref["last_seen_at"] = seen_at
                count = topic_ref.get("transition_count", 0)
                if increment:
                    topic_ref["transition_count"] = int(count) + 1
                else:
                    topic_ref["transition_count"] = int(count)
                return topic_ref

        topic_ref = {
            "topic_id": topic_id,
            "first_seen_at": seen_at,
            "last_seen_at": seen_at,
            "transition_count": 1 if increment else 0,
        }
        topic_refs.append(topic_ref)
        return topic_ref

    def _merge_metadata(self, current, incoming):
        base = {}
        if isinstance(current, dict):
            base.update(current)
        if incoming is not None:
            base.update(dict(incoming))
        return base
