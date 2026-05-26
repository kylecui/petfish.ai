#!/usr/bin/env python3
"""
TopicValidator - Validates topic_graph.json structure and consistency.
Detects structural errors, dangling references, and inconsistencies.
"""

import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional


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
        # Legacy/extended relations
        "refines",
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
        "title",
        "status",
    }
    OPTIONAL_NODE_FIELDS = {
        "type",
        "summary",
        "keywords",
        "evidence_level",
        "confidence",
        "freshness",
        "created_at",
        "updated_at",
        "scope",
        "parent",
        "tags",
        "metadata",
    }
    REQUIRED_EDGE_FIELDS = {
        "source",
        "target",
        "relation",
    }
    OPTIONAL_EDGE_FIELDS = {
        "id",
        "evidence_level",
        "confidence",
        "created_at",
    }

    def __init__(self, base_dir: str):
        """
        Initialize validator.

        Args:
            base_dir: Path to .petfish/fish-trail directory
        """
        self.base_dir = Path(base_dir)
        self.graph_file: Optional[Path] = None  # resolved in _load_graph
        self.topic_cards_dir = self.base_dir / "topic_cards"
        self.topics_dir = self.base_dir / "topics"
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

    # ------------------------------------------------------------------
    # Loading & normalization
    # ------------------------------------------------------------------

    def _load_graph(self) -> bool:
        """Load and normalize graph/registry data from topic_graph.json or topic-registry.json."""
        # Try topic_graph.json first, then topic-registry.json
        candidates = [
            self.base_dir / "topic_graph.json",
            self.base_dir / "topic-registry.json",
        ]
        self.graph_file = None
        for candidate in candidates:
            if candidate.exists():
                self.graph_file = candidate
                break

        if self.graph_file is None:
            self.errors.append(
                {
                    "code": "MISSING_GRAPH_FILE",
                    "message": (
                        "Neither topic_graph.json nor topic-registry.json found in "
                        f"{self.base_dir}"
                    ),
                }
            )
            return False

        try:
            with open(self.graph_file, "r", encoding="utf-8") as f:
                raw = json.load(f)
        except json.JSONDecodeError as e:
            self.errors.append(
                {
                    "code": "INVALID_JSON",
                    "message": f"Invalid JSON in {self.graph_file.name}: {str(e)}",
                }
            )
            return False
        except Exception as e:
            self.errors.append(
                {
                    "code": "INVALID_JSON",
                    "message": f"Error reading {self.graph_file.name}: {str(e)}",
                }
            )
            return False

        if not isinstance(raw, dict):
            self.errors.append(
                {"code": "INVALID_JSON", "message": "Data file must be a JSON object."}
            )
            return False

        self.graph = self._normalize(raw)
        return True

    def _normalize(self, raw: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize any supported format to {version, nodes: [...], edges: [...]}.

        Supported formats:
          1. graph() output:        {"version":N, "nodes":[...],   "edges":[...]}
          2. v1 registry:           {"version":1, "topics":{...},  "links":[...]}
          3. v2 registry:           {"version":"2.0","topics":{...}}
          4. Legacy v1 list:        {"version":1, "topics":[...],  "links":[...]}
        """
        version = raw.get("version", 1)
        edges = raw.get("edges", raw.get("links", []))

        # Format 1: already has nodes/edges arrays
        if "nodes" in raw and isinstance(raw["nodes"], list):
            nodes = raw["nodes"]
            return {"version": str(version), "nodes": nodes, "edges": edges}

        # Format 2 / 3 / 4: registry with topics
        topics_src = raw.get("topics", {})
        nodes: List[Dict[str, Any]] = []

        if isinstance(topics_src, dict):
            self._normalize_dict_topics(topics_src, nodes)
        elif isinstance(topics_src, list):
            # Legacy v1 format: topics as a list of dicts (pre-migration)
            self.warnings.append(
                {
                    "code": "LEGACY_TOPICS_FORMAT",
                    "message": (
                        "topics is a list (pre-migration v1 format). "
                        "Consider migrating to dict-keyed topics."
                    ),
                }
            )
            self._normalize_list_topics(topics_src, nodes)

        return {"version": str(version), "nodes": nodes, "edges": edges}

    def _normalize_dict_topics(
        self, topics_src: Dict[str, Any], nodes: List[Dict[str, Any]]
    ) -> None:
        """Normalize dict-keyed topics (v1 or v2 registry format)."""
        for topic_id, entry in topics_src.items():
            if not isinstance(entry, dict):
                continue
            # Prefer full topic file for richer data
            node = self._read_topic_file(topic_id)
            if node is not None:
                # Merge: registry entry metadata (status, timestamps) wins
                node.update(entry)
            else:
                node = self._entry_to_node(topic_id, entry)
            nodes.append(node)

    def _normalize_list_topics(
        self, topics_src: List[Dict[str, Any]], nodes: List[Dict[str, Any]]
    ) -> None:
        """Normalize list-format topics (legacy v1 pre-migration)."""
        for entry in topics_src:
            if not isinstance(entry, dict):
                continue
            topic_id = entry.get("id")
            if not topic_id:
                continue
            # Prefer full topic file for richer data
            node = self._read_topic_file(topic_id)
            if node is not None:
                # Merge: registry entry metadata wins
                node.update(entry)
            else:
                node = dict(entry)
                # Ensure canonical fields
                node.setdefault("id", topic_id)
                node.setdefault("title", topic_id)
                node.setdefault("status", "active")
            nodes.append(node)

    def _entry_to_node(self, topic_id: str, entry: Dict[str, Any]) -> Dict[str, Any]:
        """Convert a registry entry to the canonical node format ({id, title, status, ...}).

        Handles:
          - v1 registry entries: {title, status, created_at, updated_at, ...}
          - v2 TopicEntry dicts:  {topic_id, label, state, description, ...}
        """
        node: Dict[str, Any] = {"id": topic_id}

        # Title: v1="title", v2="label" → canonical "title"
        node["title"] = entry.get("title", entry.get("label", topic_id))
        # Status: v1="status", v2="state" → canonical "status"
        node["status"] = entry.get("status", entry.get("state", "active"))

        # Carry through optional fields with canonical names
        for key in (
            "created_at",
            "updated_at",
            "summary",
            "tags",
            "scope",
            "parent",
            "confidence",
            "evidence_level",
            "keywords",
            "freshness",
            "metadata",
            "type",
        ):
            if key in entry:
                node[key] = entry[key]

        # v2 description → scope
        if "description" in entry and "scope" not in node:
            node["scope"] = entry["description"]

        return node

    def _read_topic_file(self, topic_id: str) -> Optional[Dict[str, Any]]:
        """Read individual topic file from topics/ directory if it exists."""
        topic_path = self.topics_dir / f"{topic_id}.json"
        if not topic_path.exists():
            return None
        try:
            with open(topic_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, dict):
                return data
        except (json.JSONDecodeError, OSError):
            pass
        return None

    # ------------------------------------------------------------------
    # Validation steps
    # ------------------------------------------------------------------

    def _validate_top_level(self) -> None:
        """Validate top-level structure (post-normalization)."""
        # After _normalize(), nodes and edges are always present as lists
        # Version is optional — if missing, it's just a data quirk, not an error
        if "version" not in self.graph:
            self.warnings.append(
                {
                    "code": "MISSING_TOP_LEVEL_KEY",
                    "message": "Missing top-level key 'version' (treated as v1)",
                }
            )

        if "nodes" not in self.graph:
            self.errors.append(
                {
                    "code": "MISSING_TOP_LEVEL_KEY",
                    "message": "Missing required top-level key: nodes",
                }
            )
        elif not isinstance(self.graph["nodes"], list):
            self.errors.append(
                {
                    "code": "MISSING_TOP_LEVEL_KEY",
                    "message": "Top-level 'nodes' must be a list",
                }
            )

        if "edges" not in self.graph:
            self.errors.append(
                {
                    "code": "MISSING_TOP_LEVEL_KEY",
                    "message": "Missing required top-level key: edges",
                }
            )
        elif not isinstance(self.graph["edges"], list):
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

            # Validate evidence_level (only if present — it's optional)
            evidence_level = node.get("evidence_level")
            if (
                evidence_level is not None
                and evidence_level not in self.VALID_EVIDENCE_LEVELS
            ):
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

            # Validate confidence (only if present)
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

            # Warn on stale active topic (only if freshness present)
            status = node.get("status")
            freshness = node.get("freshness")
            if isinstance(freshness, dict):
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

            edge_id = edge.get("id", f"{edge.get('source')}->{edge.get('target')}")
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

            # Validate evidence_level (only if present — it's optional)
            if (
                evidence_level is not None
                and evidence_level not in self.VALID_EVIDENCE_LEVELS
            ):
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

            # Validate confidence (only if present)
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
            if relation and relation not in self.VALID_RELATIONS:
                self.warnings.append(
                    {
                        "code": "UNKNOWN_RELATION",
                        "message": f"Edge '{edge_id}' has unrecognized relation: {relation}",
                    }
                )

    def _validate_topic_cards(self) -> None:
        """Validate that every node has a corresponding topic file (topics/ or topic_cards/)."""
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

            # Check topics/ directory (individual topic JSON files — canonical)
            topic_file = self.topics_dir / f"{node_id}.json"
            # Check topic_cards/ directory (Markdown cards — legacy)
            card_file = self.topic_cards_dir / f"{slug}.md"

            has_topic_file = topic_file.exists()
            has_card_file = card_file.exists()

            if not has_topic_file and not has_card_file:
                self.warnings.append(
                    {
                        "code": "MISSING_TOPIC_CARD",
                        "message": (
                            f"No topic file for node '{node_id}'. "
                            f"Checked: {topic_file} and {card_file}"
                        ),
                    }
                )
            elif has_card_file:
                # Validate card frontmatter topic_id for Markdown cards
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
