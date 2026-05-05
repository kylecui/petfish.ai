"""Tests for topic_store.py."""

from __future__ import annotations

import json
import sys
import threading
import time
from pathlib import Path

import pytest

MODULE_DIR = (
    Path(__file__).resolve().parents[1]
    / "packs/fish-trail/.opencode/skills/fish-trail/mcp/context-state"
)
sys.path.insert(0, str(MODULE_DIR))

from topic_store import TopicStore  # pyright: ignore[reportMissingImports]


def make_store(tmp_path: Path) -> TopicStore:
    return TopicStore(str(tmp_path / ".ai-context"))


def test_create_basic_create(tmp_path: Path):
    store = make_store(tmp_path)

    topic = store.create(title="Topic A", scope="Scope A")

    assert topic["id"].startswith("topic_")
    assert topic["title"] == "Topic A"
    assert topic["scope"] == "Scope A"
    assert topic["status"] == "active"
    assert topic["parent"] is None
    assert topic["summary"] == ""
    assert topic["tags"] == []
    assert topic["metadata"] == {}
    assert topic["created_at"] == topic["updated_at"]
    assert (tmp_path / ".ai-context/topics" / f"{topic['id']}.json").exists()


def test_create_with_parent(tmp_path: Path):
    store = make_store(tmp_path)
    parent = store.create(title="Parent", scope="Root scope")

    child = store.create(title="Child", scope="Nested scope", parent=parent["id"])

    assert child["parent"] == parent["id"]


def test_create_with_tags(tmp_path: Path):
    store = make_store(tmp_path)

    topic = store.create(title="Tagged", scope="Scope", tags=["alpha", "beta"])

    assert topic["tags"] == ["alpha", "beta"]


def test_create_generates_duplicate_safe_ids(tmp_path: Path):
    store = make_store(tmp_path)

    ids = {store.create(title=f"Topic {i}", scope="Scope")["id"] for i in range(25)}

    assert len(ids) == 25


def test_get_existing_topic(tmp_path: Path):
    store = make_store(tmp_path)
    created = store.create(title="Existing", scope="Scope")

    fetched = store.get(created["id"])

    assert fetched == created


def test_get_nonexistent_returns_none(tmp_path: Path):
    store = make_store(tmp_path)

    assert store.get("topic_missing") is None


def test_list_topics_returns_all_topics(tmp_path: Path):
    store = make_store(tmp_path)
    first = store.create(title="First", scope="Scope")
    second = store.create(title="Second", scope="Scope")

    listed = store.list_topics()

    assert {item["id"] for item in listed} == {first["id"], second["id"]}


def test_list_topics_filters_by_status(tmp_path: Path):
    store = make_store(tmp_path)
    active = store.create(title="Active", scope="Scope")
    archived = store.create(title="Archived", scope="Scope")
    store.archive(archived["id"])

    listed = store.list_topics(status="archived")

    assert [item["id"] for item in listed] == [archived["id"]]
    assert active["id"] not in {item["id"] for item in listed}


def test_update_changes_fields_and_bumps_updated_at(tmp_path: Path):
    store = make_store(tmp_path)
    topic = store.create(title="Original", scope="Scope")
    time.sleep(0.01)

    updated = store.update(topic["id"], title="Renamed", summary="New summary")

    assert updated["title"] == "Renamed"
    assert updated["summary"] == "New summary"
    assert updated["updated_at"] > topic["updated_at"]


def test_update_rejects_id_and_created_at_changes(tmp_path: Path):
    store = make_store(tmp_path)
    topic = store.create(title="Original", scope="Scope")

    updated = store.update(
        topic["id"],
        id="topic_changed",
        created_at="1999-01-01T00:00:00+00:00",
        summary="Still allowed",
    )

    assert updated["id"] == topic["id"]
    assert updated["created_at"] == topic["created_at"]
    assert updated["summary"] == "Still allowed"


def test_archive_sets_status_archived(tmp_path: Path):
    store = make_store(tmp_path)
    topic = store.create(title="To archive", scope="Scope")

    archived = store.archive(topic["id"])

    assert archived["status"] == "archived"
    assert store.get(topic["id"])["status"] == "archived"
    assert store.get_active() is None


def test_search_matches_title_case_insensitive(tmp_path: Path):
    store = make_store(tmp_path)
    topic = store.create(title="Alpha Planning", scope="Scope")

    matches = store.search("alpHA")

    assert [item["id"] for item in matches] == [topic["id"]]


def test_search_matches_scope(tmp_path: Path):
    store = make_store(tmp_path)
    topic = store.create(title="Topic", scope="Webhook routing and retry policy")

    matches = store.search("routing")

    assert [item["id"] for item in matches] == [topic["id"]]


def test_search_matches_summary(tmp_path: Path):
    store = make_store(tmp_path)
    topic = store.create(title="Topic", scope="Scope")
    store.update(topic["id"], summary="Tracks checkout rollback decisions")

    matches = store.search("rollback")

    assert [item["id"] for item in matches] == [topic["id"]]


def test_search_matches_tags(tmp_path: Path):
    store = make_store(tmp_path)
    topic = store.create(title="Topic", scope="Scope", tags=["Critical", "Router"])

    matches = store.search("critical")

    assert [item["id"] for item in matches] == [topic["id"]]


def test_link_creates_link_and_graph_edge(tmp_path: Path):
    store = make_store(tmp_path)
    source = store.create(title="Source", scope="Scope")
    target = store.create(title="Target", scope="Scope")

    link = store.link(source["id"], target["id"], "fork")
    graph = store.graph()

    assert link["source"] == source["id"]
    assert link["target"] == target["id"]
    assert link["relation"] == "fork"
    assert graph["edges"] == [link]


def test_link_validates_relation(tmp_path: Path):
    store = make_store(tmp_path)
    source = store.create(title="Source", scope="Scope")
    target = store.create(title="Target", scope="Scope")

    with pytest.raises(ValueError):
        store.link(source["id"], target["id"], "invalid")


def test_unlink_returns_true_when_link_removed(tmp_path: Path):
    store = make_store(tmp_path)
    source = store.create(title="Source", scope="Scope")
    target = store.create(title="Target", scope="Scope")
    store.link(source["id"], target["id"], "bridge")

    removed = store.unlink(source["id"], target["id"])

    assert removed is True
    assert store.graph()["edges"] == []


def test_unlink_returns_false_when_link_missing(tmp_path: Path):
    store = make_store(tmp_path)
    source = store.create(title="Source", scope="Scope")
    target = store.create(title="Target", scope="Scope")

    assert store.unlink(source["id"], target["id"]) is False


def test_graph_returns_nodes_and_edges_structure(tmp_path: Path):
    store = make_store(tmp_path)
    first = store.create(title="First", scope="Scope")
    second = store.create(title="Second", scope="Scope")
    edge = store.link(first["id"], second["id"], "continue")

    graph = store.graph()

    assert set(graph.keys()) == {"nodes", "edges"}
    assert {node["id"] for node in graph["nodes"]} == {first["id"], second["id"]}
    assert graph["edges"] == [edge]


def test_get_active_returns_initial_active_topic(tmp_path: Path):
    store = make_store(tmp_path)
    first = store.create(title="First", scope="Scope")
    store.create(title="Second", scope="Scope")

    active = store.get_active()

    assert active["id"] == first["id"]


def test_set_active_switches_active_topic(tmp_path: Path):
    store = make_store(tmp_path)
    first = store.create(title="First", scope="Scope")
    second = store.create(title="Second", scope="Scope")

    store.set_active(second["id"])

    assert store.get_active()["id"] == second["id"]
    assert store.get_active()["id"] != first["id"]


def test_log_decision_and_get_decisions(tmp_path: Path):
    store = make_store(tmp_path)
    source = store.create(title="Source", scope="Scope")
    target = store.create(title="Target", scope="Scope")

    record = store.log_decision(
        {
            "source_topic": source["id"],
            "target_topic": target["id"],
            "relation": "switch",
            "reason": "User changed task",
        }
    )
    decisions = store.get_decisions()

    assert record["timestamp"]
    assert decisions[-1] == record


def test_get_decisions_filters_by_topic_id(tmp_path: Path):
    store = make_store(tmp_path)
    first = store.create(title="First", scope="Scope")
    second = store.create(title="Second", scope="Scope")
    third = store.create(title="Third", scope="Scope")
    match = store.log_decision(
        {
            "source_topic": first["id"],
            "target_topic": second["id"],
            "relation": "continue",
        }
    )
    store.log_decision(
        {
            "source_topic": third["id"],
            "target_topic": second["id"],
            "relation": "fork",
        }
    )

    filtered = store.get_decisions(topic_id=first["id"])

    assert filtered == [match]


def test_get_decisions_respects_limit(tmp_path: Path):
    store = make_store(tmp_path)
    first = store.create(title="First", scope="Scope")
    second = store.create(title="Second", scope="Scope")

    store.log_decision({"source_topic": first["id"], "target_topic": second["id"]})
    second_record = store.log_decision(
        {"source_topic": second["id"], "target_topic": first["id"]}
    )

    assert store.get_decisions(limit=1) == [second_record]
    assert store.get_decisions(limit=0) == []


def test_atomic_write_handles_simple_concurrent_access(tmp_path: Path):
    store = make_store(tmp_path)
    ids: list[str] = []
    errors: list[Exception] = []

    def worker(index: int) -> None:
        try:
            topic = store.create(title=f"Topic {index}", scope="Concurrent scope")
            ids.append(topic["id"])
        except Exception as exc:  # pragma: no cover - failure capture path
            errors.append(exc)

    threads = [threading.Thread(target=worker, args=(index,)) for index in range(20)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    registry = json.loads((tmp_path / ".ai-context/topic-registry.json").read_text())

    assert errors == []
    assert len(ids) == 20
    assert len(set(ids)) == 20
    assert len(registry["topics"]) == 20
    assert len(store.list_topics()) == 20
