#!/usr/bin/env python3
"""
TopicValidator - Validates topic_graph.json structure and consistency.
Detects structural errors, dangling references, and inconsistencies.
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Any


class TopicValidator:
    """Validates topic_graph.json against schema and consistency rules."""

    VALID_EVIDENCE_LEVELS = {
        "extracted",
        "inferred",
        "ambiguous",
        "proposed",
        "deprecated",
    }
    VALID_RELATIONS = {
        "refines",
        "depends_on",
        "inspired_by",
        "supersedes",
        "conflicts_with",
        "related_to",
        "produces",
        "uses_skill",
        "belongs_to_project",
        "should_not_mix_with",
        "evidence_for",
    }
    REQUIRED_NODE_FIELDS = {
        "id",
        "type",
        "title",
        "summary",
        "status",
        "keywords",
        "evidence_level",
        "confidence",
        "freshness",
    }
    REQUIRED_EDGE_FIELDS = {
        "id",
        "source",
        "target",
        "relation",
        "evidence_level",
        "confidence",
    }

    def __init__(self, base_dir: str):
        """
        Initialize validator.

        Args:
            base_dir: Path to .petfish/fish-trail directory
        """
        self.base_dir = Path(base_dir)
        self.graph_file = self.base_dir / "topic_graph.json"
        self.topic_cards_dir = self.base_dir / "topic_cards"
        self.errors: List[Dict[str, str]] = []
        self.warnings: List[Dict[str, str]] = []
        self.graph: Dict[str, Any] = {}

    def validate(self) -> Dict[str, Any]:
        """
        Run full validation suite.

        Returns:
            Dict with keys: status ("pass"|"fail"), errors (list), warnings (list)
        """
        self.errors = []
        self.warnings = []
        self.graph = {}

        # Step 1: Load and parse graph
        if not self._load_graph():
            return {"status": "fail", "errors": self.errors, "warnings": self.warnings}

        # Step 2: Validate top-level structure
        self._validate_top_level()
        if self.errors:
            return {"status": "fail", "errors": self.errors, "warnings": self.warnings}

        # Step 3: Validate nodes
        self._validate_nodes()

        # Step 4: Validate edges
        self._validate_edges()

        # Step 5: Validate cross-references (topic cards)
        self._validate_topic_cards()

        # Step 6: Validate consistency rules
        self._validate_consistency()

        status = "fail" if self.errors else "pass"
        return {"status": status, "errors": self.errors, "warnings": self.warnings}

    def _load_graph(self) -> bool:
        """Load and parse topic_graph.json."""
        if not self.graph_file.exists():
            self.errors.append(
                {
                    "code": "MISSING_GRAPH_FILE",
                    "message": f"topic_graph.json not found at {self.graph_file}",
                }
            )
            return False

        try:
            with open(self.graph_file, "r", encoding="utf-8") as f:
                self.graph = json.load(f)
        except json.JSONDecodeError as e:
            self.errors.append(
                {
                    "code": "INVALID_JSON",
                    "message": f"Invalid JSON in topic_graph.json: {str(e)}",
                }
            )
            return False
        except Exception as e:
            self.errors.append(
                {
                    "code": "INVALID_JSON",
                    "message": f"Error reading topic_graph.json: {str(e)}",
                }
            )
            return False

        return True

    def _validate_top_level(self) -> None:
        """Validate top-level structure."""
        required_keys = {"version", "nodes", "edges"}
        missing = required_keys - set(self.graph.keys())

        for key in missing:
            self.errors.append(
                {
                    "code": "MISSING_TOP_LEVEL_KEY",
                    "message": f"Missing required top-level key: {key}",
                }
            )

        # Ensure nodes and edges are lists
        if "nodes" in self.graph and not isinstance(self.graph["nodes"], list):
            self.errors.append(
                {
                    "code": "MISSING_TOP_LEVEL_KEY",
                    "message": "Top-level 'nodes' must be a list",
                }
            )

        if "edges" in self.graph and not isinstance(self.graph["edges"], list):
            self.errors.append(
                {
                    "code": "MISSING_TOP_LEVEL_KEY",
                    "message": "Top-level 'edges' must be a list",
                }
            )

    def _validate_nodes(self) -> None:
        """Validate all nodes."""
        nodes = self.graph.get("nodes", [])
        node_ids = set()

        for node in nodes:
            if not isinstance(node, dict):
                self.errors.append(
                    {
                        "code": "INVALID_NODE_STRUCTURE",
                        "message": f"Node is not a dict: {type(node)}",
                    }
                )
                continue

            node_id = node.get("id")

            # Check for duplicate IDs
            if node_id in node_ids:
                self.errors.append(
                    {
                        "code": "DUPLICATE_NODE_ID",
                        "message": f"Node ID '{node_id}' appears multiple times",
                    }
                )
            else:
                node_ids.add(node_id)

            # Check required fields
            missing_fields = self.REQUIRED_NODE_FIELDS - set(node.keys())
            for field in missing_fields:
                self.errors.append(
                    {
                        "code": "MISSING_REQUIRED_FIELD",
                        "message": f"Node '{node_id}' missing required field: {field}",
                    }
                )

            # Validate evidence_level
            evidence_level = node.get("evidence_level")
            if evidence_level not in self.VALID_EVIDENCE_LEVELS:
                self.errors.append(
                    {
                        "code": "INVALID_EVIDENCE_LEVEL",
                        "message": f"Node '{node_id}' has invalid evidence_level: {evidence_level}",
                    }
                )

            # Warn on ambiguous evidence
            if evidence_level == "ambiguous":
                self.warnings.append(
                    {
                        "code": "AMBIGUOUS_TOPIC",
                        "message": f"Node '{node_id}' has evidence_level 'ambiguous' — should be confirmed",
                    }
                )

            # Validate confidence
            confidence = node.get("confidence")
            if confidence is not None:
                if not isinstance(confidence, (int, float)) or not (
                    0.0 <= confidence <= 1.0
                ):
                    self.errors.append(
                        {
                            "code": "INVALID_CONFIDENCE",
                            "message": f"Node '{node_id}' has invalid confidence: {confidence} (must be 0.0-1.0)",
                        }
                    )

            # Warn on stale active topic
            status = node.get("status")
            freshness = node.get("freshness", {})
            freshness_status = freshness.get("status")
            if status == "active" and freshness_status == "stale":
                self.warnings.append(
                    {
                        "code": "STALE_ACTIVE_TOPIC",
                        "message": f"Node '{node_id}' is active but marked stale",
                    }
                )

    def _validate_edges(self) -> None:
        """Validate all edges."""
        edges = self.graph.get("edges", [])
        nodes = self.graph.get("nodes", [])
        node_ids = {n.get("id") for n in nodes if isinstance(n, dict)}

        for edge in edges:
            if not isinstance(edge, dict):
                self.errors.append(
                    {
                        "code": "INVALID_EDGE_STRUCTURE",
                        "message": f"Edge is not a dict: {type(edge)}",
                    }
                )
                continue

            edge_id = edge.get("id", "unknown")
            source = edge.get("source")
            target = edge.get("target")
            relation = edge.get("relation")
            evidence_level = edge.get("evidence_level")

            # Check required fields
            missing_fields = self.REQUIRED_EDGE_FIELDS - set(edge.keys())
            for field in missing_fields:
                self.errors.append(
                    {
                        "code": "MISSING_REQUIRED_FIELD",
                        "message": f"Edge '{edge_id}' missing required field: {field}",
                    }
                )

            # Check dangling references
            if source and source not in node_ids:
                self.errors.append(
                    {
                        "code": "DANGLING_EDGE",
                        "message": f"Edge '{edge_id}' references non-existent source node: {source}",
                    }
                )

            if target and target not in node_ids:
                self.errors.append(
                    {
                        "code": "DANGLING_EDGE",
                        "message": f"Edge '{edge_id}' references non-existent target node: {target}",
                    }
                )

            # Validate evidence_level
            if evidence_level not in self.VALID_EVIDENCE_LEVELS:
                self.errors.append(
                    {
                        "code": "INVALID_EVIDENCE_LEVEL",
                        "message": f"Edge '{edge_id}' has invalid evidence_level: {evidence_level}",
                    }
                )

            # Warn on deprecated edge
            if evidence_level == "deprecated":
                self.warnings.append(
                    {
                        "code": "DEPRECATED_EDGE",
                        "message": f"Edge '{edge_id}' ({source} -> {target}) is deprecated",
                    }
                )

            # Validate confidence
            confidence = edge.get("confidence")
            if confidence is not None:
                if not isinstance(confidence, (int, float)) or not (
                    0.0 <= confidence <= 1.0
                ):
                    self.errors.append(
                        {
                            "code": "INVALID_CONFIDENCE",
                            "message": f"Edge '{edge_id}' has invalid confidence: {confidence}",
                        }
                    )

            # Validate relation
            if relation not in self.VALID_RELATIONS:
                self.errors.append(
                    {
                        "code": "INVALID_RELATION",
                        "message": f"Edge '{edge_id}' has invalid relation: {relation}",
                    }
                )

    def _validate_topic_cards(self) -> None:
        """Validate topic card cross-references."""
        nodes = self.graph.get("nodes", [])

        for node in nodes:
            if not isinstance(node, dict):
                continue

            node_id = node.get("id")
            if not node_id:
                continue

            # Extract slug from node ID (remove "topic-" prefix)
            slug = (
                node_id.replace("topic-", "")
                if node_id.startswith("topic-")
                else node_id
            )
            card_file = self.topic_cards_dir / f"{slug}.md"

            # Check if card exists
            if not card_file.exists():
                self.warnings.append(
                    {
                        "code": "MISSING_TOPIC_CARD",
                        "message": f"Topic card missing for node '{node_id}' at {card_file}",
                    }
                )
            else:
                # Validate card frontmatter topic_id
                self._validate_card_frontmatter(card_file, node_id)

    def _validate_card_frontmatter(
        self, card_file: Path, expected_node_id: str
    ) -> None:
        """Validate topic card frontmatter."""
        try:
            with open(card_file, "r", encoding="utf-8") as f:
                content = f.read()

            # Simple YAML frontmatter extraction
            if content.startswith("---"):
                parts = content.split("---", 2)
                if len(parts) >= 2:
                    frontmatter = parts[1]
                    # Look for topic_id field
                    for line in frontmatter.split("\n"):
                        if line.startswith("topic_id:"):
                            topic_id = line.split(":", 1)[1].strip().strip("'\"")
                            if topic_id != expected_node_id:
                                self.warnings.append(
                                    {
                                        "code": "CARD_ID_MISMATCH",
                                        "message": f"Card {card_file.name} has topic_id '{topic_id}' but node is '{expected_node_id}'",
                                    }
                                )
                            return
        except Exception as e:
            self.warnings.append(
                {
                    "code": "CARD_READ_ERROR",
                    "message": f"Could not read card {card_file}: {str(e)}",
                }
            )

    def _validate_consistency(self) -> None:
        """Validate consistency rules across graph."""
        edges = self.graph.get("edges", [])

        # Build edge maps for quick lookup
        edge_map = {}  # (source, target, relation) -> edge
        for edge in edges:
            if isinstance(edge, dict):
                source = edge.get("source")
                target = edge.get("target")
                relation = edge.get("relation")
                if source and target and relation:
                    edge_map[(source, target, relation)] = edge

        # Check for contradictory edges
        conflicting_relations = {
            "must_load": {"refines", "depends_on", "produces"},
            "should_not_mix": {"should_not_mix_with", "conflicts_with"},
        }

        for (src, tgt, rel), edge in edge_map.items():
            # If there's a must_load edge, there shouldn't be conflict edges
            if rel in conflicting_relations["must_load"]:
                for conflict_rel in conflicting_relations["should_not_mix"]:
                    if (src, tgt, conflict_rel) in edge_map:
                        self.warnings.append(
                            {
                                "code": "CONTRADICTORY_EDGES",
                                "message": f"Node pair ({src}, {tgt}) has both '{rel}' (must_load) and '{conflict_rel}' (should_not_mix)",
                            }
                        )


def main():
    """CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Validate topic_graph.json structure and consistency"
    )
    parser.add_argument(
        "--project-root",
        default=".",
        help="Project root directory (default: current directory)",
    )
    args = parser.parse_args()

    # Construct path to fish-trail base directory
    project_root = Path(args.project_root)
    fish_trail_dir = project_root / ".petfish" / "fish-trail"

    # Run validation
    validator = TopicValidator(str(fish_trail_dir))
    result = validator.validate()

    # Output result as JSON
    print(json.dumps(result, indent=2))

    # Exit with appropriate code
    sys.exit(0 if result["status"] == "pass" else 1)


if __name__ == "__main__":
    main()
