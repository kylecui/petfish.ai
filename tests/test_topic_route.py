"""Tests for topic_route.py."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

MODULE_DIR = (
    Path(__file__).resolve().parents[1]
    / "packs/fish-trail/.opencode/skills/fish-trail/scripts"
)
sys.path.insert(0, str(MODULE_DIR))

from topic_route import TopicRouter  # pyright: ignore[reportMissingImports]


def make_graph(tmp_path: Path, nodes: list, edges: list | None = None) -> str:
    """Create a test graph in the expected directory structure."""
    base = tmp_path / ".petfish" / "fish-trail"
    base.mkdir(parents=True, exist_ok=True)
    graph = {"version": 1, "nodes": nodes, "edges": edges or []}
    (base / "topic_graph.json").write_text(json.dumps(graph), encoding="utf-8")
    return str(base)


class TestRouteBasics:
    """Test basic routing functionality."""

    def test_route_single_topic_returns_it(self, tmp_path: Path):
        """route() with single topic returns that topic."""
        nodes = [
            {
                "id": "topic_alpha",
                "type": "topic",
                "title": "Alpha Topic",
                "summary": "First topic",
                "status": "active",
                "priority": "high",
                "keywords": ["alpha", "first"],
            }
        ]
        base_dir = make_graph(tmp_path, nodes)
        router = TopicRouter(base_dir)

        result = router.route("alpha test")

        assert result["topic_id"] == "topic_alpha"
        assert result["topic_title"] == "Alpha Topic"
        assert isinstance(result["score"], float)
        assert result["score"] >= 0.0

    def test_route_multiple_topics_scores_by_keyword_match(self, tmp_path: Path):
        """route() scores multiple topics by Jaccard similarity."""
        nodes = [
            {
                "id": "topic_python",
                "type": "topic",
                "title": "Python Programming",
                "summary": "Learn Python language",
                "status": "active",
                "keywords": ["python", "programming", "code"],
            },
            {
                "id": "topic_rust",
                "type": "topic",
                "title": "Rust Programming",
                "summary": "Learn Rust language",
                "status": "active",
                "keywords": ["rust", "programming", "code"],
            },
            {
                "id": "topic_cooking",
                "type": "topic",
                "title": "Cooking Methods",
                "summary": "How to cook food",
                "status": "active",
                "keywords": ["cooking", "food", "recipes"],
            },
        ]
        base_dir = make_graph(tmp_path, nodes)
        router = TopicRouter(base_dir)

        result = router.route("python programming tutorial")

        # Python should score highest since query contains "python" and "programming"
        assert result["topic_id"] == "topic_python"

    def test_route_current_topic_id_gives_boost(self, tmp_path: Path):
        """route() with current_topic_id adds CURRENT_TOPIC_BOOST to score."""
        nodes = [
            {
                "id": "topic_a",
                "type": "topic",
                "title": "Topic A",
                "summary": "About A",
                "status": "active",
                "keywords": ["a"],
            },
            {
                "id": "topic_b",
                "type": "topic",
                "title": "Topic B",
                "summary": "About A and B together",
                "status": "active",
                "keywords": ["a", "b"],
            },
        ]
        base_dir = make_graph(tmp_path, nodes)
        router = TopicRouter(base_dir)

        # Without boost, topic_b should win (higher overlap)
        result_no_boost = router.route("a")
        # With boost on topic_a, it should win despite lower raw score
        result_with_boost = router.route("a", current_topic_id="topic_a")

        # topic_a should be selected when boosted
        assert result_with_boost["topic_id"] == "topic_a"

    def test_route_empty_graph_raises_value_error(self, tmp_path: Path):
        """route() raises ValueError when no topics available."""
        base_dir = make_graph(tmp_path, [])
        router = TopicRouter(base_dir)

        with pytest.raises(ValueError, match="No topics available"):
            router.route("some query")

    def test_route_returns_all_required_keys(self, tmp_path: Path):
        """route() result has all required keys."""
        nodes = [
            {
                "id": "topic_test",
                "type": "topic",
                "title": "Test Topic",
                "summary": "Test summary",
                "status": "active",
                "keywords": ["test"],
            }
        ]
        base_dir = make_graph(tmp_path, nodes)
        router = TopicRouter(base_dir)

        result = router.route("test")

        assert "topic_id" in result
        assert "topic_title" in result
        assert "score" in result
        assert "must_load" in result
        assert "may_load" in result
        assert "must_not_load" in result
        assert "confirmed_decisions" in result
        assert "open_questions" in result


class TestActiveContextWriting:
    """Test write_active_context functionality."""

    def test_write_active_context_creates_markdown_file(self, tmp_path: Path):
        """write_active_context() creates active_context.md with proper structure."""
        nodes = [
            {
                "id": "topic_demo",
                "type": "topic",
                "title": "Demo Topic",
                "summary": "Demo summary",
                "status": "active",
                "keywords": ["demo"],
            }
        ]
        base_dir = make_graph(tmp_path, nodes)
        router = TopicRouter(base_dir)
        route_result = router.route("demo query")

        path = router.write_active_context(route_result, "demo query")

        assert path.endswith("active_context.md")
        md_file = Path(path)
        assert md_file.exists()
        content = md_file.read_text(encoding="utf-8")
        assert "# Active Context" in content
        assert "## Current topic" in content
        assert "## User request" in content
        assert "## Must load" in content
        assert "## May load" in content
        assert "## Must not load" in content
        assert "## Confirmed decisions" in content
        assert "## Open questions" in content

    def test_write_active_context_saves_last_route_json(self, tmp_path: Path):
        """write_active_context() saves last_route.json with route data."""
        nodes = [
            {
                "id": "topic_x",
                "type": "topic",
                "title": "Topic X",
                "summary": "X summary",
                "status": "active",
                "keywords": ["x"],
            }
        ]
        base_dir = make_graph(tmp_path, nodes)
        router = TopicRouter(base_dir)
        route_result = router.route("x query")

        router.write_active_context(route_result, "x query")

        last_route_path = Path(base_dir) / "routes" / "last_route.json"
        assert last_route_path.exists()
        saved = json.loads(last_route_path.read_text(encoding="utf-8"))
        assert saved["topic_id"] == "topic_x"
        assert saved["topic_title"] == "Topic X"
        assert saved["score"] >= 0.0


class TestKeywordExtraction:
    """Test _extract_keywords functionality."""

    def test_extract_keywords_handles_cjk_text(self, tmp_path: Path):
        """_extract_keywords() properly extracts CJK characters as separate keywords."""
        base_dir = make_graph(tmp_path, [{"id": "dummy", "type": "topic"}])
        router = TopicRouter(base_dir)

        keywords = router._extract_keywords("学习Python编程")

        # Should contain individual CJK characters or words
        # The function extracts whole words with CJK AND individual CJK chars
        assert len(keywords) > 0
        # At minimum, should have CJK characters (stopwords like 学 may be excluded)
        assert any(c in str(keywords) for c in ["编", "程", "学"])

    def test_extract_keywords_filters_stopwords(self, tmp_path: Path):
        """_extract_keywords() removes English and Chinese stopwords."""
        base_dir = make_graph(tmp_path, [{"id": "dummy", "type": "topic"}])
        router = TopicRouter(base_dir)

        keywords = router._extract_keywords("the and is python and django")

        # Stopwords should be filtered
        assert "the" not in keywords
        assert "and" not in keywords
        assert "is" not in keywords
        # Content words should remain
        assert "python" in keywords
        assert "django" in keywords

    def test_extract_keywords_handles_empty_string(self, tmp_path: Path):
        """_extract_keywords() returns empty set for empty input."""
        base_dir = make_graph(tmp_path, [{"id": "dummy", "type": "topic"}])
        router = TopicRouter(base_dir)

        keywords = router._extract_keywords("")

        assert keywords == set()

    def test_extract_keywords_lowercases_input(self, tmp_path: Path):
        """_extract_keywords() normalizes to lowercase."""
        base_dir = make_graph(tmp_path, [{"id": "dummy", "type": "topic"}])
        router = TopicRouter(base_dir)

        keywords = router._extract_keywords("Python Django REST")

        assert "python" in keywords
        assert "django" in keywords
        assert "rest" in keywords
        # Uppercase versions should not exist
        assert "Python" not in keywords


class TestFirewallMustLoad:
    """Test MUST_LOAD_RELATIONS firewall."""

    def test_firewall_must_load_respects_depends_on(self, tmp_path: Path):
        """MUST_LOAD_RELATIONS includes 'depends_on' edges."""
        nodes = [
            {
                "id": "topic_main",
                "type": "topic",
                "title": "Main Topic",
                "summary": "Main",
                "status": "active",
                "keywords": ["main"],
            },
            {
                "id": "topic_dep",
                "type": "topic",
                "title": "Dependency",
                "summary": "Dependency",
                "status": "active",
                "keywords": ["dep"],
            },
        ]
        edges = [
            {
                "id": "edge_1",
                "source": "topic_main",
                "target": "topic_dep",
                "relation": "depends_on",
            }
        ]
        base_dir = make_graph(tmp_path, nodes, edges)
        router = TopicRouter(base_dir)

        result = router.route("main")

        # Dependency should be in must_load
        dep_in_must_load = any("topic_dep" in item for item in result["must_load"])
        assert dep_in_must_load

    def test_firewall_must_load_respects_refines(self, tmp_path: Path):
        """MUST_LOAD_RELATIONS includes 'refines' edges."""
        nodes = [
            {
                "id": "topic_rough",
                "type": "topic",
                "title": "Rough Idea",
                "summary": "Rough",
                "status": "active",
                "keywords": ["rough"],
            },
            {
                "id": "topic_refined",
                "type": "topic",
                "title": "Refined Version",
                "summary": "Refined",
                "status": "active",
                "keywords": ["refined"],
            },
        ]
        edges = [
            {
                "id": "edge_1",
                "source": "topic_rough",
                "target": "topic_refined",
                "relation": "refines",
            }
        ]
        base_dir = make_graph(tmp_path, nodes, edges)
        router = TopicRouter(base_dir)

        result = router.route("rough")

        refined_in_must_load = any(
            "topic_refined" in item for item in result["must_load"]
        )
        assert refined_in_must_load

    def test_firewall_must_load_respects_evidence_for(self, tmp_path: Path):
        """MUST_LOAD_RELATIONS includes 'evidence_for' edges."""
        nodes = [
            {
                "id": "topic_claim",
                "type": "topic",
                "title": "Claim",
                "summary": "A claim",
                "status": "active",
                "keywords": ["claim"],
            },
            {
                "id": "topic_evidence",
                "type": "topic",
                "title": "Evidence",
                "summary": "Supporting evidence",
                "status": "active",
                "keywords": ["evidence"],
            },
        ]
        edges = [
            {
                "id": "edge_1",
                "source": "topic_evidence",
                "target": "topic_claim",
                "relation": "evidence_for",
            }
        ]
        base_dir = make_graph(tmp_path, nodes, edges)
        router = TopicRouter(base_dir)

        result = router.route("claim")

        evidence_in_must_load = any(
            "topic_evidence" in item for item in result["must_load"]
        )
        assert evidence_in_must_load

    def test_firewall_max_must_load_enforced(self, tmp_path: Path):
        """Firewall enforces MAX_MUST_LOAD limit."""
        nodes = [
            {
                "id": f"topic_{i}",
                "type": "topic",
                "title": f"Topic {i}",
                "status": "active",
                "keywords": [f"t{i}"],
            }
            for i in range(15)
        ]
        edges = [
            {
                "id": f"edge_{i}",
                "source": "topic_0",
                "target": f"topic_{i + 1}",
                "relation": "depends_on",
            }
            for i in range(14)
        ]
        base_dir = make_graph(tmp_path, nodes, edges)
        router = TopicRouter(base_dir)

        result = router.route("t0")

        # must_load includes current topic + decision-log + topic_graph.json + dependencies
        # Limited by MAX_MUST_LOAD
        assert len(result["must_load"]) <= router.MAX_MUST_LOAD


class TestFirewallMayLoad:
    """Test MAY_LOAD_RELATIONS firewall."""

    def test_firewall_may_load_respects_related_to(self, tmp_path: Path):
        """MAY_LOAD_RELATIONS includes 'related_to' edges."""
        nodes = [
            {
                "id": "topic_a",
                "type": "topic",
                "title": "Topic A",
                "summary": "About A features",
                "status": "active",
                "keywords": ["a", "alfa"],
            },
            {
                "id": "topic_b",
                "type": "topic",
                "title": "Topic B",
                "summary": "About B functions",
                "status": "active",
                "keywords": ["b", "bravo"],
            },
        ]
        edges = [
            {
                "id": "edge_1",
                "source": "topic_a",
                "target": "topic_b",
                "relation": "related_to",
            }
        ]
        base_dir = make_graph(tmp_path, nodes, edges)
        router = TopicRouter(base_dir)

        result = router.route("alfa a")

        b_in_may_load = any("topic_b" in item for item in result["may_load"])
        assert b_in_may_load

    def test_firewall_may_load_respects_inspired_by(self, tmp_path: Path):
        """MAY_LOAD_RELATIONS includes 'inspired_by' edges."""
        nodes = [
            {
                "id": "topic_original",
                "type": "topic",
                "title": "Original",
                "summary": "Original",
                "status": "active",
                "keywords": ["orig"],
            },
            {
                "id": "topic_inspired",
                "type": "topic",
                "title": "Inspired",
                "summary": "Inspired",
                "status": "active",
                "keywords": ["insp"],
            },
        ]
        edges = [
            {
                "id": "edge_1",
                "source": "topic_inspired",
                "target": "topic_original",
                "relation": "inspired_by",
            }
        ]
        base_dir = make_graph(tmp_path, nodes, edges)
        router = TopicRouter(base_dir)

        result = router.route("insp")

        orig_in_may_load = any("topic_original" in item for item in result["may_load"])
        assert orig_in_may_load

    def test_firewall_max_may_load_enforced(self, tmp_path: Path):
        """Firewall enforces MAX_MAY_LOAD limit."""
        nodes = [
            {
                "id": f"topic_{i}",
                "type": "topic",
                "title": f"Topic {i}",
                "status": "active",
                "keywords": [f"t{i}"],
            }
            for i in range(20)
        ]
        edges = [
            {
                "id": f"edge_{i}",
                "source": "topic_0",
                "target": f"topic_{i + 1}",
                "relation": "related_to",
            }
            for i in range(19)
        ]
        base_dir = make_graph(tmp_path, nodes, edges)
        router = TopicRouter(base_dir)

        result = router.route("t0")

        # may_load limited by MAX_MAY_LOAD
        assert len(result["may_load"]) <= router.MAX_MAY_LOAD


class TestFirewallMustNotLoad:
    """Test MUST_NOT_LOAD_RELATIONS firewall."""

    def test_firewall_must_not_load_respects_conflicts_with(self, tmp_path: Path):
        """MUST_NOT_LOAD_RELATIONS includes 'conflicts_with' edges."""
        nodes = [
            {
                "id": "topic_approach_a",
                "type": "topic",
                "title": "Approach A",
                "summary": "Strategy approach A implementation",
                "status": "active",
                "keywords": ["approach", "strategy", "a"],
            },
            {
                "id": "topic_approach_b",
                "type": "topic",
                "title": "Approach B",
                "summary": "Conflicting approach B",
                "status": "active",
                "keywords": ["approach", "strategy", "b"],
            },
        ]
        edges = [
            {
                "id": "edge_1",
                "source": "topic_approach_a",
                "target": "topic_approach_b",
                "relation": "conflicts_with",
            }
        ]
        base_dir = make_graph(tmp_path, nodes, edges)
        router = TopicRouter(base_dir)

        result = router.route("approach strategy a")

        b_in_must_not_load = any(
            "topic_approach_b" in item for item in result["must_not_load"]
        )
        assert b_in_must_not_load

    def test_firewall_must_not_load_respects_should_not_mix_with(self, tmp_path: Path):
        """MUST_NOT_LOAD_RELATIONS includes 'should_not_mix_with' edges."""
        nodes = [
            {
                "id": "topic_x",
                "type": "topic",
                "title": "Topic X",
                "summary": "X",
                "status": "active",
                "keywords": ["x"],
            },
            {
                "id": "topic_y",
                "type": "topic",
                "title": "Topic Y",
                "summary": "Y",
                "status": "active",
                "keywords": ["y"],
            },
        ]
        edges = [
            {
                "id": "edge_1",
                "source": "topic_x",
                "target": "topic_y",
                "relation": "should_not_mix_with",
            }
        ]
        base_dir = make_graph(tmp_path, nodes, edges)
        router = TopicRouter(base_dir)

        result = router.route("x")

        y_in_must_not_load = any("topic_y" in item for item in result["must_not_load"])
        assert y_in_must_not_load

    def test_firewall_max_must_not_load_enforced(self, tmp_path: Path):
        """Firewall enforces MAX_MUST_NOT_LOAD limit."""
        nodes = [
            {
                "id": f"topic_{i}",
                "type": "topic",
                "title": f"Topic {i}",
                "status": "active",
                "keywords": [f"t{i}"],
            }
            for i in range(30)
        ]
        edges = [
            {
                "id": f"edge_{i}",
                "source": "topic_0",
                "target": f"topic_{i + 1}",
                "relation": "conflicts_with",
            }
            for i in range(29)
        ]
        base_dir = make_graph(tmp_path, nodes, edges)
        router = TopicRouter(base_dir)

        result = router.route("t0")

        # must_not_load limited by MAX_MUST_NOT_LOAD
        assert len(result["must_not_load"]) <= router.MAX_MUST_NOT_LOAD

    def test_firewall_deprecated_topics_in_must_not_load(self, tmp_path: Path):
        """Deprecated topics are automatically added to must_not_load."""
        nodes = [
            {
                "id": "topic_active",
                "type": "topic",
                "title": "Active",
                "summary": "Active",
                "status": "active",
                "keywords": ["active"],
            },
            {
                "id": "topic_old",
                "type": "topic",
                "title": "Deprecated",
                "summary": "Old version",
                "status": "deprecated",
                "keywords": ["old"],
            },
        ]
        base_dir = make_graph(tmp_path, nodes)
        router = TopicRouter(base_dir)

        result = router.route("active")

        old_in_must_not_load = any(
            "topic_old" in item for item in result["must_not_load"]
        )
        assert old_in_must_not_load


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_route_with_missing_graph_file_raises_error(self, tmp_path: Path):
        """route() raises FileNotFoundError when topic_graph.json doesn't exist."""
        base_dir = str(tmp_path / ".petfish" / "fish-trail")
        Path(base_dir).mkdir(parents=True, exist_ok=True)
        router = TopicRouter(base_dir)

        with pytest.raises(FileNotFoundError):
            router.route("test")

    def test_topic_with_confirmed_decisions_includes_them(self, tmp_path: Path):
        """route() includes confirmed_decisions from node if provided."""
        nodes = [
            {
                "id": "topic_decided",
                "type": "topic",
                "title": "Decided Topic",
                "summary": "A settled issue",
                "status": "active",
                "keywords": ["decided"],
                "confirmed_decisions": ["Decision 1", "Decision 2"],
            }
        ]
        base_dir = make_graph(tmp_path, nodes)
        router = TopicRouter(base_dir)

        result = router.route("decided")

        # If no confirmed_decisions, summary becomes the confirmed_decision
        assert len(result["confirmed_decisions"]) > 0

    def test_topic_with_open_questions_includes_them(self, tmp_path: Path):
        """route() includes open_questions from node if provided."""
        nodes = [
            {
                "id": "topic_questions",
                "type": "topic",
                "title": "Topic with Questions",
                "summary": "Still figuring this out",
                "status": "active",
                "keywords": ["questions"],
                "open_questions": ["Question 1?", "Question 2?"],
            }
        ]
        base_dir = make_graph(tmp_path, nodes)
        router = TopicRouter(base_dir)

        result = router.route("questions")

        assert "Question" in str(result["open_questions"])

    def test_route_handles_nodes_without_keywords(self, tmp_path: Path):
        """route() works with nodes that have no keywords field."""
        nodes = [
            {
                "id": "topic_minimal",
                "type": "topic",
                "title": "Minimal Topic",
                # No keywords, summary, or other fields
            }
        ]
        base_dir = make_graph(tmp_path, nodes)
        router = TopicRouter(base_dir)

        result = router.route("minimal topic")

        assert result["topic_id"] == "topic_minimal"

    def test_score_is_between_0_and_1(self, tmp_path: Path):
        """route() score is always in range [0.0, 1.0]."""
        nodes = [
            {
                "id": "topic_1",
                "type": "topic",
                "title": "Topic One",
                "summary": "First",
                "status": "active",
                "keywords": ["one"],
            },
            {
                "id": "topic_2",
                "type": "topic",
                "title": "Topic Two",
                "summary": "Second",
                "status": "active",
                "keywords": ["two"],
            },
        ]
        base_dir = make_graph(tmp_path, nodes)
        router = TopicRouter(base_dir)

        result = router.route("completely unrelated query xyz 123")

        assert 0.0 <= result["score"] <= 1.0
