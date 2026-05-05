#!/usr/bin/env python3
"""
Topic Report Generator — Produces TOPIC_REPORT.md health report for fish-trail.
Pure stdlib implementation.
"""

import json
import sys
import os
from pathlib import Path
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Any, Optional, Set, Tuple
import re


class TopicReporter:
    """Generate topic health reports from graph and card metadata."""

    def __init__(self, base_dir: str):
        """
        Initialize reporter.

        Args:
            base_dir: Path to .petfish/fish-trail directory
        """
        self.base_dir = Path(base_dir)
        self.graph_path = self.base_dir / "topic_graph.json"
        self.cards_dir = self.base_dir / "topic_cards"
        self.report_path = self.base_dir / "TOPIC_REPORT.md"

        self.graph = {}
        self.cards = {}
        self.nodes_by_id = {}
        self.edges = []

    def _load_graph(self) -> None:
        """Load topic_graph.json."""
        if not self.graph_path.exists():
            raise FileNotFoundError(f"topic_graph.json not found: {self.graph_path}")

        with open(self.graph_path, "r", encoding="utf-8") as f:
            self.graph = json.load(f)

        # Index nodes by ID
        for node in self.graph.get("nodes", []):
            self.nodes_by_id[node.get("id")] = node

        # Store edges
        self.edges = self.graph.get("edges", [])

    def _load_cards(self) -> None:
        """Load topic cards from topic_cards/*.md files."""
        if not self.cards_dir.exists():
            return

        for card_path in self.cards_dir.glob("*.md"):
            with open(card_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Parse YAML frontmatter
            frontmatter = self._parse_frontmatter(content)
            if frontmatter:
                topic_id = frontmatter.get("topic_id", card_path.stem)
                self.cards[topic_id] = frontmatter

    def _parse_frontmatter(self, content: str) -> Dict[str, Any]:
        """Extract YAML frontmatter from Markdown."""
        lines = content.split("\n")

        if not lines or lines[0].strip() != "---":
            return {}

        fm_lines = []
        for i in range(1, len(lines)):
            if lines[i].strip() == "---":
                # Parse collected frontmatter lines
                fm_dict = {}
                for line in fm_lines:
                    if ":" in line:
                        key, val = line.split(":", 1)
                        fm_dict[key.strip()] = val.strip().strip("'\"")
                return fm_dict
            fm_lines.append(lines[i])

        return {}

    def _get_edges_for_node(self, node_id: str) -> int:
        """Count all edges (incoming + outgoing) for a node."""
        count = 0
        for edge in self.edges:
            if edge.get("source") == node_id or edge.get("target") == node_id:
                count += 1
        return count

    def _parse_date(self, date_str: str) -> Optional[datetime]:
        """Parse ISO date string, return tz-aware datetime or None if invalid/empty."""
        if not date_str:
            return None
        try:
            dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt
        except (ValueError, TypeError):
            return None

    def _is_stale(self, last_updated_str: str) -> bool:
        """Check if topic is stale (last updated > 30 days ago). Unknown dates are not stale."""
        last_updated = self._parse_date(last_updated_str)
        if last_updated is None:
            return False
        age = datetime.now(timezone.utc) - last_updated
        return age > timedelta(days=30)

    def _extract_keywords(self, node: Dict[str, Any]) -> Set[str]:
        """Extract keywords from node."""
        keywords = node.get("keywords", [])
        if isinstance(keywords, str):
            return set(w.lower().strip() for w in keywords.split(","))
        elif isinstance(keywords, list):
            return set(w.lower().strip() for w in keywords)
        return set()

    def generate(self) -> Dict[str, Any]:
        """
        Generate report data.

        Returns:
            Dictionary with report sections
        """
        self._load_graph()
        self._load_cards()

        report = {
            "timestamp": datetime.now().isoformat(),
            "overview": self._compute_overview(),
            "hub_topics": self._compute_hub_topics(),
            "recently_active": self._compute_recently_active(),
            "pollution_risks": self._compute_pollution_risks(),
            "stale_topics": self._compute_stale_topics(),
            "suggested_maintenance": self._compute_suggested_maintenance(),
        }

        return report

    def _compute_overview(self) -> Dict[str, Any]:
        """Compute overview statistics."""
        total = len(self.nodes_by_id)

        status_counts = {}
        stale_count = 0

        for node in self.nodes_by_id.values():
            status = node.get("status", "unknown")
            status_counts[status] = status_counts.get(status, 0) + 1

            last_updated = node.get("updated_at", "")
            if self._is_stale(last_updated):
                stale_count += 1

        return {
            "total_topics": total,
            "status_counts": status_counts,
            "stale_count": stale_count,
        }

    def _compute_hub_topics(self) -> List[Dict[str, Any]]:
        """Find hub topics (>= 3 edges), sorted by edge count desc."""
        hubs = []

        for node_id, node in self.nodes_by_id.items():
            edge_count = self._get_edges_for_node(node_id)
            if edge_count >= 3:
                hubs.append(
                    {
                        "topic_id": node_id,
                        "title": node.get("title", node_id),
                        "edges": edge_count,
                        "status": node.get("status", "unknown"),
                    }
                )

        hubs.sort(key=lambda x: x["edges"], reverse=True)
        return hubs

    def _compute_recently_active(self) -> List[Dict[str, Any]]:
        """Find recently active topics (status == 'active'), sorted by updated_at desc."""
        active = []

        for node in self.nodes_by_id.values():
            if node.get("status") == "active":
                last_updated = node.get("updated_at", "")
                active.append(
                    {
                        "topic_id": node.get("id"),
                        "title": node.get("title", node.get("id")),
                        "last_updated": last_updated,
                        "status": node.get("status", "unknown"),
                    }
                )

        active.sort(
            key=lambda x: self._parse_date(x.get("last_updated", ""))
            or datetime.min.replace(tzinfo=timezone.utc),
            reverse=True,
        )
        return active

    def _compute_pollution_risks(self) -> List[Dict[str, Any]]:
        """Find topic pairs with should_not_mix_with, conflicts_with, or conflicting keywords."""
        risks = []
        seen_pairs = set()

        # Check explicit conflict edges
        for edge in self.edges:
            relation = edge.get("relation", "")
            if relation in ["should_not_mix_with", "conflicts_with"]:
                source = edge.get("source")
                target = edge.get("target")
                pair_key = tuple(sorted([source, target]))

                if pair_key not in seen_pairs:
                    seen_pairs.add(pair_key)
                    risks.append(
                        {
                            "topic_a": source,
                            "topic_b": target,
                            "risk": "explicit_conflict",
                            "reason": f"Edge: {relation}",
                        }
                    )

        # Check implicit conflicts: both active, shared keywords but different intents
        active_nodes = [
            n for n in self.nodes_by_id.values() if n.get("status") == "active"
        ]

        for i, node_a in enumerate(active_nodes):
            for node_b in active_nodes[i + 1 :]:
                node_a_id = node_a.get("id")
                node_b_id = node_b.get("id")
                pair_key = tuple(sorted([node_a_id, node_b_id]))

                if pair_key in seen_pairs:
                    continue

                keywords_a = self._extract_keywords(node_a)
                keywords_b = self._extract_keywords(node_b)

                # Check for shared keywords
                shared = keywords_a & keywords_b
                if shared and len(shared) > 0:
                    intent_a = node_a.get("intent", "")
                    intent_b = node_b.get("intent", "")

                    # Simple check: different intents
                    if intent_a and intent_b and intent_a.lower() != intent_b.lower():
                        seen_pairs.add(pair_key)
                        risks.append(
                            {
                                "topic_a": node_a_id,
                                "topic_b": node_b_id,
                                "risk": "shared_keywords_different_intent",
                                "reason": f"Shared keywords: {', '.join(sorted(shared)[:3])}",
                            }
                        )

        return risks

    def _compute_stale_topics(self) -> List[Dict[str, Any]]:
        """Find stale topics (status == 'stale' or updated_at > 30 days)."""
        stale = []

        for node in self.nodes_by_id.values():
            node_status = node.get("status", "")
            last_updated = node.get("updated_at", "")

            is_stale_by_status = node_status == "stale"
            is_stale_by_age = self._is_stale(last_updated)

            if is_stale_by_status or is_stale_by_age:
                reason = ""
                if is_stale_by_status:
                    reason = "marked stale"
                elif is_stale_by_age:
                    reason = "not updated for > 30 days"

                stale.append(
                    {
                        "topic_id": node.get("id"),
                        "title": node.get("title", node.get("id")),
                        "last_updated": last_updated,
                        "reason": reason,
                        "status": node_status,
                    }
                )

        stale.sort(
            key=lambda x: self._parse_date(x.get("last_updated", ""))
            or datetime.min.replace(tzinfo=timezone.utc)
        )
        return stale

    def _compute_suggested_maintenance(self) -> List[str]:
        """Suggest maintenance actions."""
        suggestions = []

        # 1. Deprecated edges still in graph
        deprecated_edges = [
            e for e in self.edges if e.get("evidence_level") == "deprecated"
        ]
        if deprecated_edges:
            suggestions.append(
                f"Remove {len(deprecated_edges)} deprecated edges from graph"
            )

        # 2. Ambiguous evidence topics
        ambiguous_topics = [
            n
            for n in self.nodes_by_id.values()
            if n.get("evidence_level") == "ambiguous"
        ]
        if ambiguous_topics:
            suggestions.append(
                f"Confirm or clarify {len(ambiguous_topics)} topic(s) with ambiguous evidence: "
                f"{', '.join([t.get('id') for t in ambiguous_topics[:3]])}"
            )

        # 3. Hub topics with too many edges (>= 5)
        very_high_hubs = [
            n
            for n in self.nodes_by_id.values()
            if self._get_edges_for_node(n.get("id", "")) >= 5
        ]
        if very_high_hubs:
            suggestions.append(
                f"Review {len(very_high_hubs)} hub topic(s) with >= 5 edges for consolidation: "
                f"{', '.join([n.get('id') for n in very_high_hubs[:3]])}"
            )

        # 4. Unused topics (no edges, not active)
        unused = [
            n
            for n in self.nodes_by_id.values()
            if self._get_edges_for_node(n.get("id", "")) == 0
            and n.get("status") != "active"
        ]
        if unused:
            suggestions.append(
                f"Consider archiving {len(unused)} unused topic(s): "
                f"{', '.join([n.get('id') for n in unused[:3]])}"
            )

        return suggestions

    def write_report(self, report: Dict[str, Any]) -> str:
        """
        Write report to TOPIC_REPORT.md.

        Args:
            report: Report data from generate()

        Returns:
            Path to generated report file
        """
        lines = []

        lines.append("# Fish Trail Topic Report")
        lines.append("")
        lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}")
        lines.append("")

        # Overview
        lines.append("## Overview")
        lines.append("")
        overview = report.get("overview", {})
        total = overview.get("total_topics", 0)
        stale_count = overview.get("stale_count", 0)
        status_counts = overview.get("status_counts", {})

        active_count = status_counts.get("active", 0)
        paused_count = status_counts.get("paused", 0)
        archived_count = status_counts.get("archived", 0)

        lines.append(
            f"当前项目共有 **{total}** 个topics，其中 {active_count} 个active、"
            f"{paused_count} 个paused、{archived_count} 个archived。"
        )
        lines.append(f"其中 **{stale_count}** 个topics显示为stale（未更新超过30天）。")
        lines.append("")

        # Hub topics
        hub_topics = report.get("hub_topics", [])
        if hub_topics:
            lines.append("## Hub Topics")
            lines.append("")
            lines.append("| Topic | Edges | Status |")
            lines.append("|-------|-------|--------|")
            for hub in hub_topics:
                topic_id = hub.get("topic_id", "")
                title = hub.get("title", topic_id)
                edges = hub.get("edges", 0)
                status = hub.get("status", "unknown")
                lines.append(f"| {title} ({topic_id}) | {edges} | {status} |")
            lines.append("")

        # Recently active
        recently_active = report.get("recently_active", [])
        if recently_active:
            lines.append("## Recently Active")
            lines.append("")
            for topic in recently_active:
                topic_id = topic.get("topic_id", "")
                title = topic.get("title", topic_id)
                last_updated = topic.get("last_updated", "unknown")
                lines.append(
                    f"- **{title}** ({topic_id}) — last updated: {last_updated}"
                )
            lines.append("")

        # Pollution risks
        pollution_risks = report.get("pollution_risks", [])
        if pollution_risks:
            lines.append("## Possible Pollution Risks")
            lines.append("")
            lines.append("| Topic A | Topic B | Risk | Reason |")
            lines.append("|---------|---------|------|--------|")
            for risk in pollution_risks:
                topic_a = risk.get("topic_a", "")
                topic_b = risk.get("topic_b", "")
                risk_type = risk.get("risk", "unknown")
                reason = risk.get("reason", "")
                lines.append(f"| {topic_a} | {topic_b} | {risk_type} | {reason} |")
            lines.append("")

        # Stale topics
        stale_topics = report.get("stale_topics", [])
        if stale_topics:
            lines.append("## Stale Topics")
            lines.append("")
            lines.append("| Topic | Last Updated | Reason | Status |")
            lines.append("|-------|-------------|--------|--------|")
            for topic in stale_topics:
                topic_id = topic.get("topic_id", "")
                title = topic.get("title", topic_id)
                last_updated = topic.get("last_updated", "unknown")
                reason = topic.get("reason", "")
                status = topic.get("status", "unknown")
                lines.append(
                    f"| {title} ({topic_id}) | {last_updated} | {reason} | {status} |"
                )
            lines.append("")

        # Suggested maintenance
        suggestions = report.get("suggested_maintenance", [])
        if suggestions:
            lines.append("## Suggested Maintenance")
            lines.append("")
            for i, suggestion in enumerate(suggestions, 1):
                lines.append(f"{i}. {suggestion}")
            lines.append("")

        # Write to file
        self.report_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.report_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

        return str(self.report_path)


def main():
    """CLI interface."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Generate fish-trail topic health report"
    )
    parser.add_argument(
        "--project-root",
        default=".",
        help="Project root directory (default: current directory)",
    )
    parser.add_argument(
        "--json", action="store_true", help="Output JSON instead of writing Markdown"
    )

    args = parser.parse_args()

    # Construct path to fish-trail directory
    project_root = Path(args.project_root)
    base_dir = project_root / ".petfish" / "fish-trail"

    try:
        reporter = TopicReporter(str(base_dir))
        report = reporter.generate()

        if args.json:
            print(json.dumps(report, indent=2, default=str))
        else:
            report_path = reporter.write_report(report)
            print(f"Report written to: {report_path}")

    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
