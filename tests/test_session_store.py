"""Tests for session_store.py."""

from __future__ import annotations

import json
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

MODULE_DIR = (
    Path(__file__).resolve().parents[1]
    / "packs/fish-trail/.opencode/skills/fish-trail/mcp/context-state"
)
sys.path.insert(0, str(MODULE_DIR))

from context_builder import ContextBuilder  # pyright: ignore[reportMissingImports]
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


def set_last_activity_at(
    store: SessionStore,
    session_id: str,
    last_activity_at: datetime,
) -> None:
    session_path = store._session_path(session_id)
    session = json.loads(session_path.read_text(encoding="utf-8"))
    timestamp = last_activity_at.isoformat()
    session["last_activity_at"] = timestamp
    session_path.write_text(json.dumps(session), encoding="utf-8")

    store._index["sessions"][session_id]["last_activity_at"] = timestamp
    store.index_path.write_text(json.dumps(store._index), encoding="utf-8")


def test_auto_close_inactive_closes_only_stale_active_sessions_and_returns_ids(
    tmp_path: Path,
):
    store = make_store(tmp_path)
    stale = store.bind(external_session_id="stale")
    recent = store.bind(external_session_id="recent")
    already_closed = store.bind(external_session_id="already-closed")
    store.close(already_closed["id"], summary="manually closed")

    now = datetime.now(timezone.utc)
    set_last_activity_at(store, stale["id"], now - timedelta(hours=25))
    set_last_activity_at(store, recent["id"], now - timedelta(hours=23))
    set_last_activity_at(store, already_closed["id"], now - timedelta(hours=72))

    closed_session_ids = store.auto_close_inactive()

    assert closed_session_ids == [stale["id"]]

    stale_session = store.get(stale["id"])
    recent_session = store.get(recent["id"])
    already_closed_session = store.get(already_closed["id"])

    assert stale_session is not None
    assert stale_session["status"] == "closed"
    assert stale_session["summary"] == "Auto-closed: inactive for 24h"
    assert stale_session["ended_at"] is not None

    assert recent_session is not None
    assert recent_session["status"] == "active"
    assert recent_session["ended_at"] is None

    assert already_closed_session is not None
    assert already_closed_session["status"] == "closed"
    assert already_closed_session["summary"] == "manually closed"


def test_auto_close_inactive_respects_custom_threshold_hours(tmp_path: Path):
    store = make_store(tmp_path)
    session = store.bind(external_session_id="custom-threshold")

    set_last_activity_at(
        store,
        session["id"],
        datetime.now(timezone.utc) - timedelta(hours=2),
    )

    assert store.auto_close_inactive(threshold_hours=3.0) == []
    assert store.get(session["id"])["status"] == "active"

    closed_session_ids = store.auto_close_inactive(threshold_hours=1.5)

    assert closed_session_ids == [session["id"]]
    assert store.get(session["id"])["summary"] == "Auto-closed: inactive for 1.5h"


def test_get_timeline_summary_returns_expected_structure_and_recent_tail(
    tmp_path: Path,
):
    store = make_store(tmp_path)
    session = store.bind(external_session_id="timeline", topic_id="topic_alpha")

    first = store.add_event(session["id"], "message", content="one")
    second = store.add_event(session["id"], "switch", topic_id="topic_beta")
    third = store.add_event(session["id"], "message", content="three")
    updated = store.update(session["id"], summary="Timeline summary")

    summary = store.get_timeline_summary(session["id"], max_events=2)

    assert summary == {
        "session_id": session["id"],
        "status": updated["status"],
        "started_at": updated["started_at"],
        "ended_at": updated["ended_at"],
        "active_topic_id": updated["active_topic_id"],
        "topic_refs": updated["topic_refs"],
        "summary": "Timeline summary",
        "recent_events": [second, third],
        "total_events": 3,
    }
    assert first not in summary["recent_events"]


def test_get_timeline_summary_returns_empty_recent_events_for_empty_timeline(
    tmp_path: Path,
):
    store = make_store(tmp_path)
    session = store.bind(external_session_id="empty-timeline")

    summary = store.get_timeline_summary(session["id"])

    assert summary["recent_events"] == []
    assert summary["total_events"] == 0


def test_get_timeline_summary_raises_key_error_for_missing_session(tmp_path: Path):
    store = make_store(tmp_path)

    with pytest.raises(KeyError):
        store.get_timeline_summary("oc_missing")


def test_get_resume_context_returns_expected_structure_and_last_ten_events(
    tmp_path: Path,
):
    store = make_store(tmp_path)
    session = store.bind(external_session_id="resume", topic_id="topic_alpha")
    store.update(session["id"], summary="Resume summary")

    for index in range(12):
        store.add_event(
            session["id"],
            f"step_{index}",
            topic_id=f"topic_{index}",
            detail=f"detail-{index}",
        )

    persisted = store.get(session["id"])
    resume_context = store.get_resume_context(session["id"])

    assert persisted is not None
    assert resume_context["session_id"] == session["id"]
    assert resume_context["inherited_from"] == session["id"]
    assert resume_context["status"] == persisted["status"]
    assert resume_context["active_topic_id"] == persisted["active_topic_id"]
    assert resume_context["topic_refs"] == persisted["topic_refs"]
    assert resume_context["summary"] == "Resume summary"
    assert resume_context["last_activity_at"] == persisted["last_activity_at"]

    timeline_digest = resume_context["timeline_digest"]

    assert len(timeline_digest) == 10
    assert [event["type"] for event in timeline_digest] == [
        f"step_{index}" for index in range(2, 12)
    ]
    assert all(
        set(event.keys()) == {"ts", "type", "topic_id"} for event in timeline_digest
    )


def test_get_resume_context_raises_key_error_for_missing_session(tmp_path: Path):
    store = make_store(tmp_path)

    with pytest.raises(KeyError):
        store.get_resume_context("oc_missing")


def test_build_resume_package_uses_topic_title_and_writes_resume_file(
    tmp_path: Path,
):
    base_dir = tmp_path / ".ai-context"
    builder = ContextBuilder(str(base_dir))
    session_context = {
        "session_id": "oc_resume_topic",
        "inherited_from": "oc_seed",
        "status": "active",
        "active_topic_id": "topic_alpha",
        "summary": "Session summary",
        "last_activity_at": "2026-01-01T00:00:00+00:00",
        "timeline_digest": [
            {
                "ts": "2026-01-01T00:00:00+00:00",
                "type": "switch",
                "topic_id": "topic_alpha",
            }
        ],
    }
    topic = {
        "id": "topic_alpha",
        "title": "Topic Alpha",
        "status": "active",
        "scope": "Routing",
        "summary": "Topic summary",
    }

    result = builder.build_resume_package(session_context, topic, [], [])

    expected_path = base_dir / "contexts" / "oc_resume_topic.resume.md"
    content = expected_path.read_text(encoding="utf-8")

    assert expected_path.exists()
    assert result == {"path": str(expected_path), "size": expected_path.stat().st_size}
    assert "# Context Package: Resume: Topic Alpha" in content


def test_build_resume_package_uses_session_id_when_topic_is_none(tmp_path: Path):
    base_dir = tmp_path / ".ai-context"
    builder = ContextBuilder(str(base_dir))
    session_context = {
        "session_id": "oc_resume_session",
        "inherited_from": "none",
        "status": "closed",
        "active_topic_id": None,
        "summary": "Session-only summary",
        "last_activity_at": "2026-01-02T00:00:00+00:00",
        "timeline_digest": [],
    }

    result = builder.build_resume_package(session_context, None, [], [])

    expected_path = base_dir / "contexts" / "oc_resume_session.resume.md"
    content = expected_path.read_text(encoding="utf-8")

    assert expected_path.exists()
    assert result == {"path": str(expected_path), "size": expected_path.stat().st_size}
    assert "# Context Package: Resume: Session oc_resume_session" in content


def test_query_activity_returns_expected_structure(tmp_path: Path):
    store = make_store(tmp_path)
    session = store.bind(external_session_id="activity-structure")

    first = store.add_event(
        session["id"],
        "message",
        topic_id="topic_alpha",
        agent_id="agent_a",
        content="first",
    )
    second = store.add_event(
        session["id"],
        "message",
        topic_id="topic_beta",
        agent_id="agent_b",
        content="second",
    )

    result = store.query_activity()

    assert result == {
        "sessions_scanned": 1,
        "sessions_matched": 1,
        "topics_active": ["topic_alpha", "topic_beta"],
        "agents_active": ["agent_a", "agent_b"],
        "events": [first, second],
        "total_events": 2,
    }


def test_query_activity_filters_by_since_and_until(tmp_path: Path):
    store = make_store(tmp_path)
    first_session = store.bind(external_session_id="activity-older")
    first = store.add_event(first_session["id"], "message", topic_id="topic_alpha")
    time.sleep(0.01)

    second_session = store.bind(external_session_id="activity-middle")
    second = store.add_event(second_session["id"], "message", topic_id="topic_beta")
    time.sleep(0.01)

    third_session = store.bind(external_session_id="activity-newer")
    store.add_event(third_session["id"], "message", topic_id="topic_gamma")

    result = store.query_activity(since=second["ts"], until=second["ts"])

    assert result["sessions_scanned"] == 3
    assert result["sessions_matched"] == 1
    assert result["topics_active"] == ["topic_beta"]
    assert result["agents_active"] == []
    assert result["events"] == [second]
    assert result["total_events"] == 1
    assert first not in result["events"]


def test_query_activity_filters_by_topic_id(tmp_path: Path):
    store = make_store(tmp_path)
    first_session = store.bind(external_session_id="activity-topic-1")
    matching_first = store.add_event(
        first_session["id"], "message", topic_id="topic_alpha", agent_id="agent_a"
    )

    second_session = store.bind(external_session_id="activity-topic-2")
    store.add_event(
        second_session["id"], "message", topic_id="topic_beta", agent_id="agent_b"
    )
    matching_second = store.add_event(
        second_session["id"], "message", topic_id="topic_alpha", agent_id="agent_c"
    )

    result = store.query_activity(topic_id="topic_alpha")

    assert result["sessions_scanned"] == 2
    assert result["sessions_matched"] == 2
    assert result["topics_active"] == ["topic_alpha"]
    assert result["agents_active"] == ["agent_a", "agent_c"]
    assert result["events"] == [matching_first, matching_second]
    assert result["total_events"] == 2


def test_query_activity_filters_by_agent_id(tmp_path: Path):
    store = make_store(tmp_path)
    first_session = store.bind(external_session_id="activity-agent-1")
    matching_first = store.add_event(
        first_session["id"], "message", topic_id="topic_alpha", agent_id="agent_shared"
    )

    second_session = store.bind(external_session_id="activity-agent-2")
    store.add_event(
        second_session["id"], "message", topic_id="topic_beta", agent_id="agent_other"
    )
    matching_second = store.add_event(
        second_session["id"],
        "message",
        topic_id="topic_gamma",
        agent_id="agent_shared",
    )

    result = store.query_activity(agent_id="agent_shared")

    assert result["sessions_scanned"] == 2
    assert result["sessions_matched"] == 2
    assert result["topics_active"] == ["topic_alpha", "topic_gamma"]
    assert result["agents_active"] == ["agent_shared"]
    assert result["events"] == [matching_first, matching_second]
    assert result["total_events"] == 2


def test_query_activity_limit_returns_capped_events_but_preserves_total(tmp_path: Path):
    store = make_store(tmp_path)
    session = store.bind(external_session_id="activity-limit")

    first = store.add_event(session["id"], "message", topic_id="topic_alpha")
    second = store.add_event(session["id"], "message", topic_id="topic_beta")
    store.add_event(session["id"], "message", topic_id="topic_gamma")

    result = store.query_activity(limit=2)

    assert result["events"] == [first, second]
    assert result["total_events"] == 3


def test_query_activity_returns_empty_results_with_no_sessions(tmp_path: Path):
    store = make_store(tmp_path)

    assert store.query_activity() == {
        "sessions_scanned": 0,
        "sessions_matched": 0,
        "topics_active": [],
        "agents_active": [],
        "events": [],
        "total_events": 0,
    }


def test_get_agent_attribution_returns_expected_structure(tmp_path: Path):
    store = make_store(tmp_path)
    session = store.bind(external_session_id="agent-structure")
    store.add_event(
        session["id"], "message", topic_id="topic_alpha", agent_id="agent_a"
    )
    store.add_event(session["id"], "message", topic_id="topic_beta", agent_id="agent_b")

    result = store.get_agent_attribution()

    assert result == {
        "by_agent": {
            "agent_a": ["topic_alpha"],
            "agent_b": ["topic_beta"],
        },
        "by_topic": {
            "topic_alpha": ["agent_a"],
            "topic_beta": ["agent_b"],
        },
        "sessions_scanned": 1,
    }


def test_get_agent_attribution_groups_multiple_topics_per_agent(tmp_path: Path):
    store = make_store(tmp_path)
    session = store.bind(external_session_id="agent-groups")
    store.add_event(
        session["id"], "message", topic_id="topic_alpha", agent_id="agent_a"
    )
    store.add_event(session["id"], "message", topic_id="topic_beta", agent_id="agent_a")
    store.add_event(session["id"], "message", topic_id="topic_beta", agent_id="agent_b")

    result = store.get_agent_attribution()

    assert result["by_agent"] == {
        "agent_a": ["topic_alpha", "topic_beta"],
        "agent_b": ["topic_beta"],
    }
    assert result["by_topic"] == {
        "topic_alpha": ["agent_a"],
        "topic_beta": ["agent_a", "agent_b"],
    }


def test_get_agent_attribution_filters_by_session_id(tmp_path: Path):
    store = make_store(tmp_path)
    first_session = store.bind(external_session_id="agent-session-1")
    second_session = store.bind(external_session_id="agent-session-2")
    store.add_event(
        first_session["id"], "message", topic_id="topic_alpha", agent_id="agent_a"
    )
    store.add_event(
        second_session["id"], "message", topic_id="topic_beta", agent_id="agent_b"
    )

    result = store.get_agent_attribution(session_id=second_session["id"])

    assert result == {
        "by_agent": {"agent_b": ["topic_beta"]},
        "by_topic": {"topic_beta": ["agent_b"]},
        "sessions_scanned": 1,
    }


def test_get_agent_attribution_filters_by_topic_id(tmp_path: Path):
    store = make_store(tmp_path)
    first_session = store.bind(external_session_id="agent-topic-1")
    second_session = store.bind(external_session_id="agent-topic-2")
    store.add_event(
        first_session["id"], "message", topic_id="topic_alpha", agent_id="agent_a"
    )
    store.add_event(
        first_session["id"], "message", topic_id="topic_beta", agent_id="agent_a"
    )
    store.add_event(
        second_session["id"], "message", topic_id="topic_beta", agent_id="agent_b"
    )

    result = store.get_agent_attribution(topic_id="topic_beta")

    assert result["sessions_scanned"] == 2
    assert result["by_agent"] == {
        "agent_a": ["topic_beta"],
        "agent_b": ["topic_beta"],
    }
    assert result["by_topic"] == {"topic_beta": ["agent_a", "agent_b"]}


def test_get_agent_attribution_skips_events_without_agent_id(tmp_path: Path):
    store = make_store(tmp_path)
    session = store.bind(external_session_id="agent-skip")
    store.add_event(session["id"], "message", topic_id="topic_alpha")
    store.add_event(session["id"], "message", topic_id="topic_beta", agent_id="")
    store.add_event(
        session["id"], "message", topic_id="topic_gamma", agent_id="agent_c"
    )

    result = store.get_agent_attribution()

    assert result["by_agent"] == {"agent_c": ["topic_gamma"]}
    assert result["by_topic"] == {"topic_gamma": ["agent_c"]}
