"""Tests for TopicStore.recommend_related."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

MODULE_DIR = (
    Path(__file__).resolve().parents[1]
    / "packs/fish-trail/.opencode/skills/fish-trail/mcp/context-state"
)
sys.path.insert(0, str(MODULE_DIR))

from topic_store import TopicStore  # pyright: ignore[reportMissingImports]


@pytest.fixture
def store(tmp_path: Path) -> TopicStore:
    return TopicStore(str(tmp_path / ".petfish" / "fish-trail"))


def create_linked_topics(store: TopicStore) -> tuple[dict, dict, dict]:
    topic_a = store.create(title="Topic A", scope="Scope A", tags=["alpha"])
    topic_b = store.create(title="Topic B", scope="Scope B", tags=["beta"])
    topic_c = store.create(title="Topic C", scope="Scope C", tags=["gamma"])
    store.update(topic_b["id"], summary="Branch from topic A")
    store.update(topic_c["id"], summary="Continues from topic B")
    store.link(topic_a["id"], topic_b["id"], "fork")
    store.link(topic_b["id"], topic_c["id"], "continue")
    return topic_a, topic_b, topic_c


def test_recommend_related_returns_empty_when_no_links(store: TopicStore):
    topic = store.create(title="Solo", scope="Standalone")

    result = store.recommend_related(topic["id"])

    assert result == {
        "source_topic_id": topic["id"],
        "recommendations": [],
        "total": 0,
    }


def test_recommend_related_returns_direct_link_at_depth_one(store: TopicStore):
    topic_a, topic_b, _ = create_linked_topics(store)

    result = store.recommend_related(topic_a["id"], max_depth=1)

    assert result["source_topic_id"] == topic_a["id"]
    assert result["total"] == 1
    assert result["recommendations"] == [
        {
            "topic_id": topic_b["id"],
            "title": "Topic B",
            "status": "active",
            "relation": "fork",
            "depth": 1,
            "via": None,
            "summary": "Branch from topic A",
            "tags": ["beta"],
        }
    ]


def test_recommend_related_returns_two_hops_in_depth_order(store: TopicStore):
    topic_a, topic_b, topic_c = create_linked_topics(store)

    result = store.recommend_related(topic_a["id"])

    assert result["total"] == 2
    assert [item["topic_id"] for item in result["recommendations"]] == [
        topic_b["id"],
        topic_c["id"],
    ]
    assert [item["depth"] for item in result["recommendations"]] == [1, 2]


def test_recommend_related_max_depth_one_excludes_two_hop_topics(store: TopicStore):
    topic_a, topic_b, topic_c = create_linked_topics(store)

    result = store.recommend_related(topic_a["id"], max_depth=1)

    assert [item["topic_id"] for item in result["recommendations"]] == [topic_b["id"]]
    assert topic_c["id"] not in {item["topic_id"] for item in result["recommendations"]}


def test_recommend_related_includes_expected_fields(store: TopicStore):
    topic_a, topic_b, _ = create_linked_topics(store)
    store.update(topic_b["id"], summary="Detailed summary", tags=["beta", "linked"])

    result = store.recommend_related(topic_a["id"], max_depth=1)
    recommendation = result["recommendations"][0]

    assert recommendation["title"] == "Topic B"
    assert recommendation["status"] == "active"
    assert recommendation["relation"] == "fork"
    assert recommendation["depth"] == 1
    assert recommendation["summary"] == "Detailed summary"
    assert recommendation["tags"] == ["beta", "linked"]


def test_recommend_related_sorts_by_depth_then_title(store: TopicStore):
    source = store.create(title="Source", scope="Root")
    gamma = store.create(title="Gamma", scope="Scope")
    alpha = store.create(title="Alpha", scope="Scope")
    omega = store.create(title="Omega", scope="Scope")
    store.link(source["id"], gamma["id"], "fork")
    store.link(source["id"], alpha["id"], "fork")
    store.link(gamma["id"], omega["id"], "continue")

    result = store.recommend_related(source["id"], max_depth=2)

    assert [item["title"] for item in result["recommendations"]] == [
        "Alpha",
        "Gamma",
        "Omega",
    ]
    assert [item["depth"] for item in result["recommendations"]] == [1, 1, 2]
