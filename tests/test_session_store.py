"""Tests for session_store.py."""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import pytest

MODULE_DIR = (
    Path(__file__).resolve().parents[1]
    / "packs/context-router-skill/.opencode/skills/context-router/mcp/context-state"
)
sys.path.insert(0, str(MODULE_DIR))

from session_store import SessionStore  # pyright: ignore[reportMissingImports]


def make_store(tmp_path: Path) -> SessionStore:
    return SessionStore(str(tmp_path / ".ai-context"))


def read_index(tmp_path: Path) -> dict:
    return json.loads(
        (tmp_path / ".ai-context" / "sessions" / "index.json").read_text(
            encoding="utf-8"
        )
    )


def read_session(tmp_path: Path, session_id: str) -> dict:
    return json.loads(
        (tmp_path / ".ai-context" / "sessions" / f"{session_id}.json").read_text(
            encoding="utf-8"
        )
    )


def test_init_creates_sessions_dir_and_index_json(tmp_path: Path):
    make_store(tmp_path)

    sessions_dir = tmp_path / ".ai-context" / "sessions"

    assert sessions_dir.is_dir()
    assert read_index(tmp_path) == {"version": 1, "sessions": {}}


def test_init_preserves_valid_existing_index_json(tmp_path: Path):
    base_dir = tmp_path / ".ai-context"
    sessions_dir = base_dir / "sessions"
    sessions_dir.mkdir(parents=True)
    existing_index = {
        "version": 1,
        "sessions": {
            "oc_existing": {
                "status": "active",
                "source": "external",
                "started_at": "2026-01-01T00:00:00+00:00",
                "last_activity_at": "2026-01-01T00:00:00+00:00",
                "active_topic_id": None,
                "event_count": 0,
            }
        },
    }
    (sessions_dir / "index.json").write_text(
        json.dumps(existing_index), encoding="utf-8"
    )

    store = SessionStore(str(base_dir))

    assert read_index(tmp_path) == existing_index
    assert store.list_sessions(limit=None)[0]["id"] == "oc_existing"


def test_init_repairs_invalid_existing_index_json_structure(tmp_path: Path):
    base_dir = tmp_path / ".ai-context"
    sessions_dir = base_dir / "sessions"
    sessions_dir.mkdir(parents=True)
    (sessions_dir / "index.json").write_text(
        json.dumps({"version": 0, "sessions": []}), encoding="utf-8"
    )

    make_store(tmp_path)

    assert read_index(tmp_path) == {"version": 1, "sessions": {}}


def test_bind_external_creates_external_session_with_oc_prefix(tmp_path: Path):
    store = make_store(tmp_path)

    session = store.bind(external_session_id="ext-123")

    assert session["id"] == "oc_ext-123"
    assert session["external_id"] == "ext-123"
    assert session["source"] == "external"
    assert session["status"] == "active"
    assert session["timeline"] == []
    assert session["topic_refs"] == []
    assert session["metadata"] == {}
    assert (tmp_path / ".ai-context" / "sessions" / "oc_ext-123.json").exists()


def test_bind_inferred_creates_inferred_session_with_inf_prefix(tmp_path: Path):
    store = make_store(tmp_path)

    session = store.bind()

    assert session["id"].startswith("inf_")
    assert session["external_id"] is None
    assert session["source"] == "inferred"
    assert session["status"] == "active"


def test_bind_existing_external_session_returns_existing_without_duplicate(
    tmp_path: Path,
):
    store = make_store(tmp_path)
    first = store.bind(external_session_id="shared")

    second = store.bind(external_session_id="shared")

    assert second == first
    assert len(store.list_sessions(limit=None)) == 1
    assert set(read_index(tmp_path)["sessions"].keys()) == {first["id"]}


def test_bind_with_topic_id_sets_active_topic_and_topic_refs(tmp_path: Path):
    store = make_store(tmp_path)

    session = store.bind(external_session_id="topic-bound", topic_id="topic_alpha")

    assert session["active_topic_id"] == "topic_alpha"
    assert session["topic_refs"] == [
        {
            "topic_id": "topic_alpha",
            "first_seen_at": session["started_at"],
            "last_seen_at": session["started_at"],
            "transition_count": 0,
        }
    ]


def test_bind_with_metadata_stores_metadata(tmp_path: Path):
    store = make_store(tmp_path)

    session = store.bind(metadata={"owner": "petfish", "attempt": 1})

    assert session["metadata"] == {"owner": "petfish", "attempt": 1}


def test_bind_existing_external_session_merges_metadata_and_updates_last_activity(
    tmp_path: Path,
):
    store = make_store(tmp_path)
    first = store.bind(external_session_id="meta", metadata={"alpha": 1})
    time.sleep(0.01)

    second = store.bind(external_session_id="meta", metadata={"beta": 2})

    assert second["metadata"] == {"alpha": 1, "beta": 2}
    assert second["last_activity_at"] > first["last_activity_at"]


def test_get_returns_session_for_valid_id(tmp_path: Path):
    store = make_store(tmp_path)
    created = store.bind(external_session_id="fetch-me")

    fetched = store.get(created["id"])

    assert fetched == created


def test_get_returns_none_for_missing_id(tmp_path: Path):
    store = make_store(tmp_path)

    assert store.get("oc_missing") is None


def test_list_sessions_returns_all_sessions_sorted_by_last_activity_desc(
    tmp_path: Path,
):
    store = make_store(tmp_path)
    first = store.bind(external_session_id="first")
    time.sleep(0.01)
    second = store.bind(external_session_id="second")
    time.sleep(0.01)
    store.add_event(first["id"], "touch")

    listed = store.list_sessions(limit=None)

    assert [item["id"] for item in listed] == [first["id"], second["id"]]


def test_list_sessions_filters_by_status(tmp_path: Path):
    store = make_store(tmp_path)
    active = store.bind(external_session_id="active")
    closed = store.bind(external_session_id="closed")
    store.close(closed["id"])

    listed = store.list_sessions(status="closed", limit=None)

    assert [item["id"] for item in listed] == [closed["id"]]
    assert active["id"] not in {item["id"] for item in listed}


def test_list_sessions_filters_by_topic_id_across_topic_refs(tmp_path: Path):
    store = make_store(tmp_path)
    first = store.bind(external_session_id="first", topic_id="topic_alpha")
    second = store.bind(external_session_id="second", topic_id="topic_beta")
    time.sleep(0.01)
    store.add_event(second["id"], "switch", topic_id="topic_alpha")
    time.sleep(0.01)
    store.add_event(second["id"], "switch", topic_id="topic_gamma")

    listed = store.list_sessions(topic_id="topic_alpha", limit=None)

    assert {item["id"] for item in listed} == {first["id"], second["id"]}


def test_list_sessions_filters_by_since_iso8601_timestamp(tmp_path: Path):
    store = make_store(tmp_path)
    store.bind(external_session_id="older")
    time.sleep(0.01)
    newer = store.bind(external_session_id="newer")

    listed = store.list_sessions(since=newer["last_activity_at"], limit=None)

    assert [item["id"] for item in listed] == [newer["id"]]


def test_list_sessions_returns_empty_for_non_positive_limit(tmp_path: Path):
    store = make_store(tmp_path)
    store.bind(external_session_id="only")

    assert store.list_sessions(limit=0) == []


def test_resume_by_session_id_returns_session_and_active_topic(tmp_path: Path):
    store = make_store(tmp_path)
    session = store.bind(external_session_id="resume-id", topic_id="topic_alpha")

    resumed = store.resume(session_id=session["id"])

    assert resumed["session"]["id"] == session["id"]
    assert resumed["topic_id"] == "topic_alpha"


def test_resume_by_topic_id_returns_most_recent_matching_session(tmp_path: Path):
    store = make_store(tmp_path)
    first = store.bind(external_session_id="first", topic_id="topic_alpha")
    second = store.bind(external_session_id="second", topic_id="topic_beta")
    time.sleep(0.01)
    store.add_event(second["id"], "visit", topic_id="topic_alpha")
    time.sleep(0.01)
    store.add_event(second["id"], "leave", topic_id="topic_gamma")

    resumed = store.resume(topic_id="topic_alpha")

    assert resumed["session"]["id"] == second["id"]
    assert resumed["topic_id"] == "topic_alpha"
    assert resumed["session"]["id"] != first["id"]


def test_resume_raises_key_error_when_nothing_found(tmp_path: Path):
    store = make_store(tmp_path)

    with pytest.raises(KeyError):
        store.resume(topic_id="missing-topic")


def test_resume_without_arguments_prefers_most_recent_active_session(tmp_path: Path):
    store = make_store(tmp_path)
    active = store.bind(external_session_id="active")
    later = store.bind(external_session_id="later")
    store.close(later["id"])

    resumed = store.resume()

    assert resumed["session"]["id"] == active["id"]
    assert resumed["topic_id"] is None


def test_add_event_appends_timeline_and_updates_last_activity(tmp_path: Path):
    store = make_store(tmp_path)
    session = store.bind(external_session_id="events")
    before = session["last_activity_at"]
    time.sleep(0.01)

    event = store.add_event(session["id"], "message", content="hello")
    persisted = store.get(session["id"])

    assert event["type"] == "message"
    assert event["content"] == "hello"
    assert persisted["timeline"] == [event]
    assert persisted["last_activity_at"] > before


def test_add_event_with_topic_id_updates_active_topic_and_topic_refs(tmp_path: Path):
    store = make_store(tmp_path)
    session = store.bind(external_session_id="topic-events")

    event = store.add_event(session["id"], "switch", topic_id="topic_alpha")
    persisted = store.get(session["id"])

    assert event["topic_id"] == "topic_alpha"
    assert persisted["active_topic_id"] == "topic_alpha"
    assert persisted["topic_refs"] == [
        {
            "topic_id": "topic_alpha",
            "first_seen_at": event["ts"],
            "last_seen_at": event["ts"],
            "transition_count": 1,
        }
    ]


def test_add_event_multiple_events_accumulate_and_reserved_fields_are_ignored(
    tmp_path: Path,
):
    store = make_store(tmp_path)
    session = store.bind(external_session_id="multi-events", topic_id="topic_alpha")

    first = store.add_event(session["id"], "step", detail="one")
    second = store.add_event(
        session["id"],
        "step",
        **{"type": "ignored", "ts": "ignored", "detail": "two"},
    )
    persisted = read_session(tmp_path, session["id"])

    assert [event["detail"] for event in persisted["timeline"]] == ["one", "two"]
    assert persisted["timeline"][0] == first
    assert persisted["timeline"][1]["type"] == "step"
    assert persisted["timeline"][1]["ts"] != "ignored"
    assert persisted["timeline"][1]["detail"] == second["detail"]


def test_close_sets_status_ended_at_and_optional_summary(tmp_path: Path):
    store = make_store(tmp_path)
    session = store.bind(external_session_id="close-me")

    closed = store.close(session["id"], summary="finished cleanly")

    assert closed["status"] == "closed"
    assert closed["summary"] == "finished cleanly"
    assert closed["ended_at"] is not None
    assert closed["last_activity_at"] == closed["ended_at"]


def test_close_updates_index(tmp_path: Path):
    store = make_store(tmp_path)
    session = store.bind(external_session_id="close-index")

    store.close(session["id"])

    assert read_index(tmp_path)["sessions"][session["id"]]["status"] == "closed"


def test_update_updates_arbitrary_fields(tmp_path: Path):
    store = make_store(tmp_path)
    session = store.bind(external_session_id="update-fields")
    time.sleep(0.01)

    updated = store.update(
        session["id"], summary="revised", inherited_from="seed-session"
    )

    assert updated["summary"] == "revised"
    assert updated["inherited_from"] == "seed-session"
    assert updated["last_activity_at"] > session["last_activity_at"]


def test_update_metadata_merges_instead_of_replacing(tmp_path: Path):
    store = make_store(tmp_path)
    session = store.bind(external_session_id="update-meta", metadata={"alpha": 1})

    updated = store.update(session["id"], metadata={"beta": 2})

    assert updated["metadata"] == {"alpha": 1, "beta": 2}


def test_update_metadata_none_clears_existing_metadata(tmp_path: Path):
    store = make_store(tmp_path)
    session = store.bind(external_session_id="clear-meta", metadata={"alpha": 1})

    updated = store.update(session["id"], metadata=None)

    assert updated["metadata"] == {}


def test_get_path_traversal_in_session_id_raises_value_error(tmp_path: Path):
    store = make_store(tmp_path)

    with pytest.raises(ValueError):
        store.get("../escape")
