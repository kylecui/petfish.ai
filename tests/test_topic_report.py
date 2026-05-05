#!/usr/bin/env python3
"""
Test suite for TopicReporter class.
Tests core functionality including graph loading, report generation, and file output.
"""

import json
import sys
from pathlib import Path
from datetime import datetime, timedelta

# Import TopicReporter using required pattern
MODULE_DIR = (
    Path(__file__).resolve().parents[1]
    / "packs/fish-trail/.opencode/skills/fish-trail/scripts"
)
sys.path.insert(0, str(MODULE_DIR))
from topic_report import TopicReporter

import pytest


# ==================== Fixtures ====================


def make_graph(tmp_path, nodes, edges=None):
    """Helper to create test data structure with topic_graph.json."""
    base = tmp_path / ".petfish" / "fish-trail"
    base.mkdir(parents=True, exist_ok=True)
    graph = {"version": 1, "nodes": nodes, "edges": edges or []}
    (base / "topic_graph.json").write_text(json.dumps(graph), encoding="utf-8")
    return str(base)


def make_topic_card(base_dir, topic_id, content):
    """Helper to create a topic card (.md file)."""
    cards_dir = Path(base_dir) / "topic_cards"
    cards_dir.mkdir(parents=True, exist_ok=True)
    card_path = cards_dir / f"{topic_id}.md"
    card_path.write_text(content, encoding="utf-8")


@pytest.fixture
def empty_graph(tmp_path):
    """Fixture: empty graph with no nodes or edges."""
    return make_graph(tmp_path, nodes=[], edges=[])


@pytest.fixture
def simple_graph(tmp_path):
    """Fixture: simple graph with 3 nodes and 2 edges."""
    nodes = [
        {
            "id": "topic-a",
            "title": "Topic A",
            "status": "active",
            "updated_at": "2026-05-05T10:00:00+00:00",
        },
        {
            "id": "topic-b",
            "title": "Topic B",
            "status": "active",
            "updated_at": "2026-05-04T10:00:00+00:00",
        },
        {
            "id": "topic-c",
            "title": "Topic C",
            "status": "paused",
            "updated_at": "2026-03-01T10:00:00+00:00",
        },
    ]
    edges = [
        {"source": "topic-a", "target": "topic-b", "relation": "depends_on"},
        {"source": "topic-b", "target": "topic-c", "relation": "related_to"},
    ]
    return make_graph(tmp_path, nodes, edges)


@pytest.fixture
def hub_graph(tmp_path):
    """Fixture: graph with a hub topic (topic-hub has 5 edges)."""
    nodes = [
        {
            "id": "topic-hub",
            "title": "Hub Topic",
            "status": "active",
            "updated_at": "2026-05-05T10:00:00+00:00",
        },
        {"id": "topic-1", "title": "Topic 1", "status": "active"},
        {"id": "topic-2", "title": "Topic 2", "status": "active"},
        {"id": "topic-3", "title": "Topic 3", "status": "active"},
        {"id": "topic-4", "title": "Topic 4", "status": "active"},
        {"id": "topic-5", "title": "Topic 5", "status": "active"},
    ]
    edges = [
        {"source": "topic-hub", "target": "topic-1", "relation": "depends_on"},
        {"source": "topic-hub", "target": "topic-2", "relation": "depends_on"},
        {"source": "topic-hub", "target": "topic-3", "relation": "depends_on"},
        {"source": "topic-hub", "target": "topic-4", "relation": "depends_on"},
        {"source": "topic-hub", "target": "topic-5", "relation": "depends_on"},
    ]
    return make_graph(tmp_path, nodes, edges)


@pytest.fixture
def pollution_graph(tmp_path):
    """Fixture: graph with explicit conflict edges."""
    nodes = [
        {
            "id": "topic-x",
            "title": "Topic X",
            "status": "active",
            "updated_at": "2026-05-05T10:00:00+00:00",
        },
        {
            "id": "topic-y",
            "title": "Topic Y",
            "status": "active",
            "updated_at": "2026-05-05T10:00:00+00:00",
        },
    ]
    edges = [
        {"source": "topic-x", "target": "topic-y", "relation": "should_not_mix_with"}
    ]
    return make_graph(tmp_path, nodes, edges)


@pytest.fixture
def stale_graph(tmp_path):
    """Fixture: graph with stale topics."""
    nodes = [
        {
            "id": "stale-1",
            "title": "Stale Topic 1",
            "status": "stale",
            "updated_at": "2025-01-01T10:00:00+00:00",
        },
        {
            "id": "old-2",
            "title": "Old Topic 2",
            "status": "paused",
            "updated_at": "2025-01-15T10:00:00+00:00",
        },
    ]
    return make_graph(tmp_path, nodes, [])


@pytest.fixture
def complex_graph(tmp_path):
    """Fixture: complex graph with multiple features for comprehensive testing."""
    nodes = [
        {
            "id": "topic-core",
            "title": "Core Topic",
            "status": "active",
            "updated_at": "2026-05-05T10:00:00+00:00",
            "keywords": "api, design, architecture",
        },
        {
            "id": "topic-feature",
            "title": "Feature Topic",
            "status": "active",
            "updated_at": "2026-05-04T15:00:00+00:00",
            "keywords": "api, implementation, testing",
        },
        {
            "id": "topic-old",
            "title": "Old Topic",
            "status": "stale",
            "updated_at": "2025-02-01T10:00:00+00:00",
            "evidence_level": "ambiguous",
        },
        {
            "id": "topic-deprecated",
            "title": "Deprecated Topic",
            "status": "archived",
        },
        {
            "id": "topic-unused",
            "title": "Unused Topic",
            "status": "paused",
        },
    ]
    edges = [
        {"source": "topic-core", "target": "topic-feature", "relation": "depends_on"},
        {
            "source": "topic-feature",
            "target": "topic-old",
            "relation": "should_not_mix_with",
        },
        {"source": "topic-core", "target": "topic-old", "relation": "conflicts_with"},
        {
            "source": "topic-deprecated",
            "target": "topic-feature",
            "relation": "depends_on",
            "evidence_level": "deprecated",
        },
    ]
    return make_graph(tmp_path, nodes, edges)


# ==================== Tests ====================


class TestTopicReporterInitialization:
    """Test TopicReporter initialization and basic properties."""

    def test_init_sets_paths(self, tmp_path):
        """Test that __init__ correctly sets up path attributes."""
        base = make_graph(tmp_path, [], [])
        reporter = TopicReporter(base)

        assert reporter.base_dir == Path(base)
        assert reporter.graph_path == Path(base) / "topic_graph.json"
        assert reporter.cards_dir == Path(base) / "topic_cards"
        assert reporter.report_path == Path(base) / "TOPIC_REPORT.md"

    def test_init_empty_graph_structures(self, tmp_path):
        """Test that __init__ initializes empty data structures."""
        base = make_graph(tmp_path, [], [])
        reporter = TopicReporter(base)

        assert reporter.graph == {}
        assert reporter.cards == {}
        assert reporter.nodes_by_id == {}
        assert reporter.edges == []


class TestGenerateReportStructure:
    """Test report generation and structure."""

    def test_generate_empty_graph_returns_valid_structure(self, empty_graph):
        """Test generate() with empty graph returns valid report structure."""
        reporter = TopicReporter(empty_graph)
        report = reporter.generate()

        assert isinstance(report, dict)
        assert "timestamp" in report
        assert "overview" in report
        assert "hub_topics" in report
        assert "recently_active" in report
        assert "pollution_risks" in report
        assert "stale_topics" in report
        assert "suggested_maintenance" in report

    def test_overview_section_structure(self, simple_graph):
        """Test overview section has correct keys and types."""
        reporter = TopicReporter(simple_graph)
        report = reporter.generate()
        overview = report["overview"]

        assert "total_topics" in overview
        assert "status_counts" in overview
        assert "stale_count" in overview
        assert isinstance(overview["total_topics"], int)
        assert isinstance(overview["status_counts"], dict)
        assert isinstance(overview["stale_count"], int)

    def test_overview_counts_correct(self, simple_graph):
        """Test that overview correctly counts topics."""
        reporter = TopicReporter(simple_graph)
        report = reporter.generate()
        overview = report["overview"]

        assert overview["total_topics"] == 3
        assert overview["status_counts"]["active"] == 2
        assert overview["status_counts"]["paused"] == 1


class TestHubTopicDetection:
    """Test hub topic identification."""

    def test_identifies_hub_topics(self, hub_graph):
        """Test generate() identifies hub topics (>= 3 edges)."""
        reporter = TopicReporter(hub_graph)
        report = reporter.generate()
        hubs = report["hub_topics"]

        assert len(hubs) > 0
        assert any(hub["topic_id"] == "topic-hub" for hub in hubs)

    def test_hub_topic_structure(self, hub_graph):
        """Test hub topics have correct structure."""
        reporter = TopicReporter(hub_graph)
        report = reporter.generate()
        hubs = report["hub_topics"]

        assert len(hubs) > 0
        hub = hubs[0]
        assert "topic_id" in hub
        assert "title" in hub
        assert "edges" in hub
        assert "status" in hub
        assert isinstance(hub["edges"], int)

    def test_hub_topics_sorted_by_edge_count(self, hub_graph):
        """Test hub topics are sorted by edge count descending."""
        reporter = TopicReporter(hub_graph)
        report = reporter.generate()
        hubs = report["hub_topics"]

        if len(hubs) > 1:
            for i in range(len(hubs) - 1):
                assert hubs[i]["edges"] >= hubs[i + 1]["edges"]

    def test_non_hub_topics_excluded(self, simple_graph):
        """Test that topics with < 3 edges are not identified as hubs."""
        reporter = TopicReporter(simple_graph)
        report = reporter.generate()
        hubs = report["hub_topics"]

        # simple_graph has max 2 edges per topic
        assert len(hubs) == 0


class TestStaleTopicDetection:
    """Test stale topic identification."""

    def test_detects_stale_topics(self, stale_graph):
        """Test generate() identifies stale topics."""
        reporter = TopicReporter(stale_graph)
        report = reporter.generate()
        stale = report["stale_topics"]

        assert len(stale) > 0
        assert any(t["topic_id"] == "stale-1" for t in stale)

    def test_stale_topic_structure(self, stale_graph):
        """Test stale topics have correct structure."""
        reporter = TopicReporter(stale_graph)
        report = reporter.generate()
        stale = report["stale_topics"]

        assert len(stale) > 0
        topic = stale[0]
        assert "topic_id" in topic
        assert "title" in topic
        assert "last_updated" in topic
        assert "reason" in topic
        assert "status" in topic

    def test_overview_counts_stale_topics(self, stale_graph):
        """Test overview stale_count matches stale_topics count."""
        reporter = TopicReporter(stale_graph)
        report = reporter.generate()
        overview = report["overview"]
        stale = report["stale_topics"]

        assert overview["stale_count"] == len(stale)


class TestPollutionRiskDetection:
    """Test pollution risk detection."""

    def test_detects_explicit_conflicts(self, pollution_graph):
        """Test generate() detects explicit should_not_mix_with edges."""
        reporter = TopicReporter(pollution_graph)
        report = reporter.generate()
        risks = report["pollution_risks"]

        assert len(risks) > 0
        assert any(r["risk"] == "explicit_conflict" for r in risks)

    def test_pollution_risk_structure(self, pollution_graph):
        """Test pollution risks have correct structure."""
        reporter = TopicReporter(pollution_graph)
        report = reporter.generate()
        risks = report["pollution_risks"]

        assert len(risks) > 0
        risk = risks[0]
        assert "topic_a" in risk
        assert "topic_b" in risk
        assert "risk" in risk
        assert "reason" in risk

    def test_pollution_risk_includes_reason(self, pollution_graph):
        """Test pollution risks include explanation."""
        reporter = TopicReporter(pollution_graph)
        report = reporter.generate()
        risks = report["pollution_risks"]

        assert len(risks) > 0
        for risk in risks:
            assert len(risk["reason"]) > 0


class TestRecentlyActiveDetection:
    """Test recently active topic detection."""

    def test_identifies_fresh_topics(self, simple_graph):
        """Test generate() identifies fresh topics."""
        reporter = TopicReporter(simple_graph)
        report = reporter.generate()
        active = report["recently_active"]

        assert len(active) > 0
        assert all(t["status"] == "active" for t in active)

    def test_recently_active_structure(self, simple_graph):
        """Test recently active topics have correct structure."""
        reporter = TopicReporter(simple_graph)
        report = reporter.generate()
        active = report["recently_active"]

        assert len(active) > 0
        topic = active[0]
        assert "topic_id" in topic
        assert "title" in topic
        assert "last_updated" in topic
        assert "status" in topic

    def test_recently_active_sorted_by_date(self, simple_graph):
        """Test recently active topics are sorted by date descending."""
        reporter = TopicReporter(simple_graph)
        report = reporter.generate()
        active = report["recently_active"]

        if len(active) > 1:
            for i in range(len(active) - 1):
                date_i = datetime.fromisoformat(
                    active[i]["last_updated"].replace("Z", "+00:00")
                )
                date_next = datetime.fromisoformat(
                    active[i + 1]["last_updated"].replace("Z", "+00:00")
                )
                assert date_i >= date_next


class TestSuggestedMaintenance:
    """Test maintenance suggestion generation."""

    def test_suggests_deprecated_edge_removal(self, complex_graph):
        """Test suggestions include deprecated edge removal."""
        reporter = TopicReporter(complex_graph)
        report = reporter.generate()
        suggestions = report["suggested_maintenance"]

        assert any("deprecated" in s.lower() for s in suggestions)

    def test_suggests_ambiguous_clarification(self, complex_graph):
        """Test suggestions include ambiguous evidence clarification."""
        reporter = TopicReporter(complex_graph)
        report = reporter.generate()
        suggestions = report["suggested_maintenance"]

        assert any("ambiguous" in s.lower() for s in suggestions)

    def test_suggests_hub_review(self, hub_graph):
        """Test suggestions include hub topic review (>= 5 edges)."""
        reporter = TopicReporter(hub_graph)
        report = reporter.generate()
        suggestions = report["suggested_maintenance"]

        assert any("hub" in s.lower() for s in suggestions)

    def test_suggests_unused_archiving(self, complex_graph):
        """Test suggestions include archiving unused topics."""
        reporter = TopicReporter(complex_graph)
        report = reporter.generate()
        suggestions = report["suggested_maintenance"]

        assert any("archiv" in s.lower() for s in suggestions)

    def test_maintenance_suggestions_list_format(self, complex_graph):
        """Test maintenance suggestions are a list of strings."""
        reporter = TopicReporter(complex_graph)
        report = reporter.generate()
        suggestions = report["suggested_maintenance"]

        assert isinstance(suggestions, list)
        for suggestion in suggestions:
            assert isinstance(suggestion, str)
            assert len(suggestion) > 0


class TestWriteReport:
    """Test report file writing."""

    def test_write_report_creates_file(self, simple_graph):
        """Test write_report() generates TOPIC_REPORT.md."""
        reporter = TopicReporter(simple_graph)
        report = reporter.generate()
        report_path = reporter.write_report(report)

        assert Path(report_path).exists()
        assert report_path.endswith("TOPIC_REPORT.md")

    def test_write_report_returns_path(self, simple_graph):
        """Test write_report() returns the report file path."""
        reporter = TopicReporter(simple_graph)
        report = reporter.generate()
        report_path = reporter.write_report(report)

        assert isinstance(report_path, str)
        assert len(report_path) > 0

    def test_report_contains_header(self, simple_graph):
        """Test report file contains expected header."""
        reporter = TopicReporter(simple_graph)
        report = reporter.generate()
        report_path = reporter.write_report(report)

        content = Path(report_path).read_text(encoding="utf-8")
        assert "# Fish Trail Topic Report" in content

    def test_report_contains_timestamp(self, simple_graph):
        """Test report file contains timestamp."""
        reporter = TopicReporter(simple_graph)
        report = reporter.generate()
        report_path = reporter.write_report(report)

        content = Path(report_path).read_text(encoding="utf-8")
        assert "Generated:" in content

    def test_report_contains_overview_section(self, simple_graph):
        """Test report file contains Overview section."""
        reporter = TopicReporter(simple_graph)
        report = reporter.generate()
        report_path = reporter.write_report(report)

        content = Path(report_path).read_text(encoding="utf-8")
        assert "## Overview" in content

    def test_report_contains_hub_section_when_hubs_exist(self, hub_graph):
        """Test report file contains Hub Topics section when hubs exist."""
        reporter = TopicReporter(hub_graph)
        report = reporter.generate()
        report_path = reporter.write_report(report)

        content = Path(report_path).read_text(encoding="utf-8")
        if report["hub_topics"]:
            assert "## Hub Topics" in content

    def test_report_contains_active_section_when_active_exist(self, simple_graph):
        """Test report file contains Recently Active section when topics exist."""
        reporter = TopicReporter(simple_graph)
        report = reporter.generate()
        report_path = reporter.write_report(report)

        content = Path(report_path).read_text(encoding="utf-8")
        if report["recently_active"]:
            assert "## Recently Active" in content

    def test_report_contains_stale_section_when_stale_exist(self, stale_graph):
        """Test report file contains Stale Topics section when stale topics exist."""
        reporter = TopicReporter(stale_graph)
        report = reporter.generate()
        report_path = reporter.write_report(report)

        content = Path(report_path).read_text(encoding="utf-8")
        if report["stale_topics"]:
            assert "## Stale Topics" in content

    def test_report_contains_maintenance_section_when_suggestions_exist(
        self, complex_graph
    ):
        """Test report file contains Suggested Maintenance section."""
        reporter = TopicReporter(complex_graph)
        report = reporter.generate()
        report_path = reporter.write_report(report)

        content = Path(report_path).read_text(encoding="utf-8")
        if report["suggested_maintenance"]:
            assert "## Suggested Maintenance" in content

    def test_report_file_is_valid_markdown(self, simple_graph):
        """Test report file is valid Markdown with proper structure."""
        reporter = TopicReporter(simple_graph)
        report = reporter.generate()
        report_path = reporter.write_report(report)

        content = Path(report_path).read_text(encoding="utf-8")
        # Check for Markdown headers
        assert "# " in content or "## " in content
        # Check for line breaks (proper formatting)
        assert "\n" in content


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_empty_graph_generates_without_error(self, empty_graph):
        """Test that empty graph doesn't cause errors."""
        reporter = TopicReporter(empty_graph)
        report = reporter.generate()

        assert report is not None
        assert report["overview"]["total_topics"] == 0

    def test_single_node_no_edges(self, tmp_path):
        """Test graph with single node and no edges."""
        nodes = [
            {
                "id": "single",
                "title": "Single Node",
                "status": "active",
                "updated_at": "2026-05-05T10:00:00+00:00",
            }
        ]
        base = make_graph(tmp_path, nodes, [])
        reporter = TopicReporter(base)
        report = reporter.generate()

        assert report["overview"]["total_topics"] == 1
        assert len(report["hub_topics"]) == 0
        assert len(report["pollution_risks"]) == 0

    def test_self_referential_edge(self, tmp_path):
        """Test handling of self-referential edges."""
        nodes = [{"id": "self-ref", "title": "Self-Ref", "status": "active"}]
        edges = [{"source": "self-ref", "target": "self-ref", "relation": "depends_on"}]
        base = make_graph(tmp_path, nodes, edges)
        reporter = TopicReporter(base)
        report = reporter.generate()

        # Self-ref edge counts, so 1 node with 1 edge doesn't become hub
        assert report["overview"]["total_topics"] == 1

    def test_missing_optional_fields(self, tmp_path):
        """Test handling nodes with missing optional fields."""
        nodes = [
            {"id": "minimal", "status": "active"},  # No title, freshness
        ]
        base = make_graph(tmp_path, nodes, [])
        reporter = TopicReporter(base)
        report = reporter.generate()

        assert report["overview"]["total_topics"] == 1
        # Reporter should use id as fallback for title
        assert len(report["overview"]["status_counts"]) > 0

    def test_malformed_date_handling(self, tmp_path):
        """Test handling of malformed date strings."""
        nodes = [
            {
                "id": "bad-date",
                "title": "Bad Date",
                "status": "active",
                "updated_at": "not-a-date",
            }
        ]
        base = make_graph(tmp_path, nodes, [])
        reporter = TopicReporter(base)
        report = reporter.generate()

        # Should not crash, treat as epoch
        assert report is not None


# ==================== Integration Tests ====================


class TestIntegration:
    """Integration tests combining multiple features."""

    def test_full_workflow_generate_and_write(self, complex_graph):
        """Test complete workflow: generate report and write to file."""
        reporter = TopicReporter(complex_graph)
        report = reporter.generate()
        report_path = reporter.write_report(report)

        # Verify file was created and is readable
        content = Path(report_path).read_text(encoding="utf-8")
        assert len(content) > 0
        assert "Fish Trail Topic Report" in content

    def test_report_consistency(self, complex_graph):
        """Test that generate() produces consistent results across calls."""
        reporter = TopicReporter(complex_graph)
        report1 = reporter.generate()
        report2 = reporter.generate()

        assert (
            report1["overview"]["total_topics"] == report2["overview"]["total_topics"]
        )
        assert len(report1["hub_topics"]) == len(report2["hub_topics"])
        assert len(report1["stale_topics"]) == len(report2["stale_topics"])


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
