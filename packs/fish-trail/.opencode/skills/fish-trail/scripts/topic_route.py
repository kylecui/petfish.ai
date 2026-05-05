#!/usr/bin/env python3
"""
Topic Router - Builds active_context.md with a context firewall.
Pure stdlib implementation.
"""

import argparse
import json
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List


class TopicRouter:
    """Route a query to the best topic and generate context firewall lists."""

    MUST_LOAD_RELATIONS = {"refines", "depends_on", "evidence_for"}
    MAY_LOAD_RELATIONS = {"inspired_by", "related_to", "produces"}
    MUST_NOT_LOAD_RELATIONS = {"should_not_mix_with", "conflicts_with"}

    MAX_MUST_LOAD = 8
    MAX_MAY_LOAD = 10
    MAX_MUST_NOT_LOAD = 20
    CURRENT_TOPIC_BOOST = 0.15

    STOPWORDS = {
        "a",
        "an",
        "and",
        "are",
        "as",
        "at",
        "be",
        "been",
        "but",
        "by",
        "for",
        "from",
        "how",
        "i",
        "in",
        "into",
        "is",
        "it",
        "its",
        "me",
        "my",
        "of",
        "on",
        "or",
        "our",
        "please",
        "that",
        "the",
        "their",
        "them",
        "then",
        "there",
        "these",
        "they",
        "this",
        "those",
        "to",
        "us",
        "we",
        "with",
        "you",
        "your",
        "do",
        "does",
        "did",
        "task",
        "create",
        "make",
        "build",
        "add",
        "the",
        "的",
        "了",
        "和",
        "与",
        "并",
        "是",
        "在",
        "把",
        "将",
        "对",
        "为",
        "用",
        "到",
        "从",
        "上",
        "下",
        "中",
        "这",
        "那",
        "一个",
        "一些",
        "这个",
        "那个",
        "我们",
        "你们",
        "他们",
        "以及",
        "然后",
        "现在",
        "请",
        "帮",
        "需要",
        "生成",
        "写",
    }

    def __init__(self, base_dir: str):
        self.base_dir = Path(base_dir).expanduser()
        self.graph_path = self.base_dir / "topic_graph.json"
        self.cards_dir = self.base_dir / "topic_cards"
        self.routes_dir = self.base_dir / "routes"
        self.active_context_path = self.base_dir / "active_context.md"

    def route(self, query: str, current_topic_id: str | None = None) -> dict:
        graph = self._load_graph()
        cards = self._load_cards()
        topics = self._build_topics(graph.get("nodes", []), cards)

        if not topics:
            raise ValueError("No topics available in topic_graph.json or topic_cards/.")

        query_keywords = self._extract_keywords(query)
        scored_topics = []

        for topic in topics.values():
            topic_terms = self._topic_terms(topic)
            score = self._jaccard_similarity(query_keywords, topic_terms)
            if current_topic_id and topic["id"] == current_topic_id:
                score = min(1.0, score + self.CURRENT_TOPIC_BOOST)
            scored_topics.append((topic, round(score, 6)))

        scored_topics.sort(
            key=lambda item: (
                item[1],
                self._status_rank(item[0]),
                self._priority_rank(item[0]),
                self._timestamp_value(item[0].get("last_updated", "")),
                item[0].get("title", ""),
            ),
            reverse=True,
        )

        current_topic = scored_topics[0][0]
        current_score = scored_topics[0][1]

        must_load, may_load, must_not_load = self._build_firewall(
            current_topic=current_topic,
            topics=topics,
            edges=graph.get("edges", []),
        )

        confirmed_decisions = list(current_topic.get("confirmed_decisions") or [])
        if not confirmed_decisions and current_topic.get("summary"):
            confirmed_decisions = [str(current_topic["summary"]).strip()]

        open_questions = list(current_topic.get("open_questions") or [])

        return {
            "topic_id": current_topic["id"],
            "topic_title": current_topic.get("title") or current_topic["id"],
            "score": current_score,
            "must_load": must_load,
            "may_load": may_load,
            "must_not_load": must_not_load,
            "confirmed_decisions": confirmed_decisions,
            "open_questions": open_questions,
        }

    def write_active_context(self, route_result: dict, query: str) -> str:
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.routes_dir.mkdir(parents=True, exist_ok=True)

        markdown = "\n".join(
            [
                "# Active Context",
                "",
                "## Current topic",
                route_result.get("topic_title")
                or route_result.get("topic_id")
                or "Unknown topic",
                "",
                "## User request",
                query.strip(),
                "",
                "## Must load",
                self._render_markdown_list(route_result.get("must_load", [])),
                "",
                "## May load",
                self._render_markdown_list(route_result.get("may_load", [])),
                "",
                "## Must not load",
                self._render_markdown_list(route_result.get("must_not_load", [])),
                "",
                "## Confirmed decisions",
                self._render_markdown_list(route_result.get("confirmed_decisions", [])),
                "",
                "## Open questions",
                self._render_markdown_list(route_result.get("open_questions", [])),
                "",
            ]
        )

        self.active_context_path.write_text(markdown, encoding="utf-8")

        last_route_path = self.routes_dir / "last_route.json"
        last_route_path.write_text(
            json.dumps(route_result, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

        return str(self.active_context_path)

    def _load_graph(self) -> Dict[str, Any]:
        if not self.graph_path.exists():
            raise FileNotFoundError(f"topic_graph.json not found: {self.graph_path}")

        with open(self.graph_path, "r", encoding="utf-8") as handle:
            graph = json.load(handle)

        if not isinstance(graph, dict):
            raise ValueError("topic_graph.json must contain a JSON object.")

        nodes = graph.get("nodes", [])
        edges = graph.get("edges", [])
        if not isinstance(nodes, list) or not isinstance(edges, list):
            raise ValueError(
                "topic_graph.json must contain list fields 'nodes' and 'edges'."
            )

        return graph

    def _load_cards(self) -> Dict[str, Dict[str, Any]]:
        cards: Dict[str, Dict[str, Any]] = {}
        if not self.cards_dir.exists():
            return cards

        for card_path in sorted(self.cards_dir.glob("*.md")):
            content = card_path.read_text(encoding="utf-8")
            frontmatter, body = self._split_frontmatter(content)
            sections = self._extract_sections(body)

            topic_id = str(frontmatter.get("topic_id") or card_path.stem).strip()
            cards[topic_id] = {
                "topic_id": topic_id,
                "title": self._clean_text(frontmatter.get("title") or ""),
                "status": self._clean_text(frontmatter.get("status") or ""),
                "priority": self._clean_text(frontmatter.get("priority") or ""),
                "last_updated": self._clean_text(frontmatter.get("last_updated") or ""),
                "evidence_level": self._clean_text(
                    frontmatter.get("evidence_level") or ""
                ),
                "keywords": self._as_list(frontmatter.get("keywords")),
                "summary": self._extract_section_text(sections.get("一句话定位", [])),
                "confirmed_decisions": self._extract_section_items(
                    sections.get("当前结论", [])
                ),
                "open_questions": self._extract_section_items(
                    sections.get("开放问题", [])
                ),
                "path": self._relative_resource_path(card_path),
            }

        return cards

    def _build_topics(
        self, nodes: List[Dict[str, Any]], cards: Dict[str, Dict[str, Any]]
    ) -> Dict[str, Dict[str, Any]]:
        topics: Dict[str, Dict[str, Any]] = {}

        for node in nodes:
            if not isinstance(node, dict):
                continue

            topic_id = str(node.get("id") or "").strip()
            if not topic_id:
                continue

            card = cards.get(topic_id, {})
            freshness = node.get("freshness") or {}
            if not isinstance(freshness, dict):
                freshness = {}

            topic = {
                "id": topic_id,
                "title": self._clean_text(
                    card.get("title") or node.get("title") or topic_id
                ),
                "summary": self._clean_text(
                    card.get("summary") or node.get("summary") or ""
                ),
                "status": self._clean_text(
                    card.get("status") or node.get("status") or "unknown"
                ),
                "priority": self._clean_text(
                    card.get("priority") or node.get("priority") or "medium"
                ),
                "last_updated": self._clean_text(
                    card.get("last_updated")
                    or freshness.get("last_updated")
                    or node.get("last_updated")
                    or ""
                ),
                "freshness_status": self._clean_text(freshness.get("status") or ""),
                "evidence_level": self._clean_text(
                    card.get("evidence_level") or node.get("evidence_level") or ""
                ),
                "keywords": self._merge_lists(
                    node.get("keywords"), card.get("keywords")
                ),
                "confirmed_decisions": list(card.get("confirmed_decisions") or []),
                "open_questions": list(
                    card.get("open_questions")
                    or self._as_list(node.get("open_questions"))
                ),
                "card_path": card.get("path") or f"topic:{topic_id}",
            }
            topics[topic_id] = topic

        for topic_id, card in cards.items():
            if topic_id in topics:
                continue

            topics[topic_id] = {
                "id": topic_id,
                "title": self._clean_text(card.get("title") or topic_id),
                "summary": self._clean_text(card.get("summary") or ""),
                "status": self._clean_text(card.get("status") or "unknown"),
                "priority": self._clean_text(card.get("priority") or "medium"),
                "last_updated": self._clean_text(card.get("last_updated") or ""),
                "freshness_status": "",
                "evidence_level": self._clean_text(card.get("evidence_level") or ""),
                "keywords": self._as_list(card.get("keywords")),
                "confirmed_decisions": list(card.get("confirmed_decisions") or []),
                "open_questions": list(card.get("open_questions") or []),
                "card_path": card.get("path") or f"topic:{topic_id}",
            }

        return topics

    def _build_firewall(
        self,
        current_topic: Dict[str, Any],
        topics: Dict[str, Dict[str, Any]],
        edges: List[Dict[str, Any]],
    ) -> tuple[List[str], List[str], List[str]]:
        current_id = current_topic["id"]

        must_ids: List[str] = []
        may_ids: List[str] = []
        must_not_ids: List[str] = []

        for edge in edges:
            if not isinstance(edge, dict):
                continue

            relation = str(edge.get("relation") or "").strip()
            source = str(edge.get("source") or "").strip()
            target = str(edge.get("target") or "").strip()

            if current_id != source and current_id != target:
                continue

            other_topic_id = target if current_id == source else source
            if (
                not other_topic_id
                or other_topic_id == current_id
                or other_topic_id not in topics
            ):
                continue

            if relation in self.MUST_LOAD_RELATIONS:
                must_ids.append(other_topic_id)
            elif relation in self.MAY_LOAD_RELATIONS:
                may_ids.append(other_topic_id)
            elif relation in self.MUST_NOT_LOAD_RELATIONS:
                must_not_ids.append(other_topic_id)
            elif relation == "supersedes" and current_id == source:
                must_not_ids.append(target)

        for topic_id, topic in topics.items():
            if topic_id == current_id:
                continue
            if self._is_deprecated(topic):
                must_not_ids.append(topic_id)

        recent_topic_ids = self._recent_topic_ids(topics, exclude_topic_id=current_id)
        may_ids.extend(recent_topic_ids)

        must_not_ids = self._dedupe_topic_ids(must_not_ids)
        must_not_set = set(must_not_ids)

        must_ids = [
            topic_id
            for topic_id in self._dedupe_topic_ids(must_ids)
            if topic_id not in must_not_set
        ]
        must_set = set(must_ids)

        may_ids = [
            topic_id
            for topic_id in self._dedupe_topic_ids(may_ids)
            if topic_id not in must_not_set and topic_id not in must_set
        ]

        must_load = [
            current_topic.get("card_path") or f"topic:{current_id}",
            self._decision_log_resource(),
            "topic_graph.json",
        ]
        must_load.extend(
            self._topic_resource(topics[topic_id]) for topic_id in must_ids
        )

        may_load = [self._topic_resource(topics[topic_id]) for topic_id in may_ids]
        must_not_load = [
            self._topic_resource(topics[topic_id]) for topic_id in must_not_ids
        ]

        must_load = self._dedupe_strings(must_load)[: self.MAX_MUST_LOAD]
        may_load = self._dedupe_strings(may_load)[: self.MAX_MAY_LOAD]
        must_not_load = self._dedupe_strings(must_not_load)[: self.MAX_MUST_NOT_LOAD]

        return must_load, may_load, must_not_load

    def _split_frontmatter(self, content: str) -> tuple[Dict[str, Any], str]:
        lines = content.splitlines()
        if not lines or lines[0].strip() != "---":
            return {}, content

        frontmatter_lines = []
        body_start = None
        for index in range(1, len(lines)):
            if lines[index].strip() == "---":
                body_start = index + 1
                break
            frontmatter_lines.append(lines[index])

        if body_start is None:
            return {}, content

        frontmatter = self._parse_frontmatter_lines(frontmatter_lines)
        body = "\n".join(lines[body_start:])
        return frontmatter, body

    def _parse_frontmatter_lines(self, lines: List[str]) -> Dict[str, Any]:
        data: Dict[str, Any] = {}
        current_key = ""

        for raw_line in lines:
            line = raw_line.rstrip()
            if not line.strip() or line.lstrip().startswith("#"):
                continue

            if re.match(r"^[A-Za-z0-9_-]+\s*:", line):
                key, raw_value = line.split(":", 1)
                current_key = key.strip()
                value = raw_value.strip()
                if value:
                    data[current_key] = self._parse_frontmatter_value(value)
                    current_key = ""
                else:
                    data[current_key] = []
                continue

            stripped = line.strip()
            if current_key and stripped.startswith("- "):
                if not isinstance(data.get(current_key), list):
                    data[current_key] = []
                data[current_key].append(self._strip_quotes(stripped[2:].strip()))

        return data

    def _parse_frontmatter_value(self, value: str) -> Any:
        value = value.strip()
        if value.startswith("[") and value.endswith("]"):
            inner = value[1:-1].strip()
            if not inner:
                return []
            return [
                self._strip_quotes(part.strip())
                for part in inner.split(",")
                if part.strip()
            ]
        return self._strip_quotes(value)

    def _extract_sections(self, body: str) -> Dict[str, List[str]]:
        sections: Dict[str, List[str]] = {}
        current_section = ""

        for raw_line in body.splitlines():
            heading_match = re.match(r"^##\s+(.+?)\s*$", raw_line.strip())
            if heading_match:
                current_section = heading_match.group(1).strip()
                sections.setdefault(current_section, [])
                continue

            if current_section:
                sections[current_section].append(raw_line.rstrip())

        return sections

    def _extract_section_items(self, lines: List[str]) -> List[str]:
        items: List[str] = []
        current_item: List[str] = []
        free_text: List[str] = []

        for raw_line in lines:
            stripped = raw_line.strip()
            if not stripped:
                continue

            bullet_match = re.match(r"^(?:[-*+]|\d+\.)\s+(.*)$", stripped)
            if bullet_match:
                if current_item:
                    items.append(" ".join(current_item).strip())
                current_item = [bullet_match.group(1).strip()]
                continue

            if current_item:
                current_item.append(stripped)
            else:
                free_text.append(stripped)

        if current_item:
            items.append(" ".join(current_item).strip())
        elif free_text:
            items.append(" ".join(free_text).strip())

        return [item for item in items if item]

    def _extract_section_text(self, lines: List[str]) -> str:
        items = self._extract_section_items(lines)
        if items:
            return " ".join(items).strip()
        return " ".join(line.strip() for line in lines if line.strip()).strip()

    def _topic_terms(self, topic: Dict[str, Any]) -> set[str]:
        text_parts = []
        text_parts.extend(self._as_list(topic.get("keywords")))
        text_parts.append(topic.get("title") or "")
        text_parts.append(topic.get("summary") or "")
        text_parts.extend(topic.get("confirmed_decisions") or [])
        text_parts.extend(topic.get("open_questions") or [])
        return self._extract_keywords(" ".join(part for part in text_parts if part))

    def _extract_keywords(self, text: str) -> set[str]:
        if not text:
            return set()

        lowered = text.lower()
        keywords: set[str] = set()

        word_tokens = re.split(r"[^0-9a-zA-Z_\u3400-\u4dbf\u4e00-\u9fff]+", lowered)
        for token in word_tokens:
            token = token.strip("_")
            if not token:
                continue

            if self._contains_cjk(token):
                if token not in self.STOPWORDS:
                    keywords.add(token)
                for char in token:
                    if self._is_cjk_char(char) and char not in self.STOPWORDS:
                        keywords.add(char)
            else:
                if token not in self.STOPWORDS:
                    keywords.add(token)

        return keywords

    def _jaccard_similarity(self, left: set[str], right: set[str]) -> float:
        if not left or not right:
            return 0.0
        union = left | right
        if not union:
            return 0.0
        return len(left & right) / len(union)

    def _recent_topic_ids(
        self, topics: Dict[str, Dict[str, Any]], exclude_topic_id: str
    ) -> List[str]:
        recent_topics = []
        now = datetime.now(timezone.utc)

        for topic_id, topic in topics.items():
            if topic_id == exclude_topic_id:
                continue
            if self._is_deprecated(topic):
                continue

            freshness_status = topic.get("freshness_status") or ""
            last_updated = self._parse_date(topic.get("last_updated") or "")
            is_recent = freshness_status in {"fresh", "recent"}

            if not is_recent and last_updated is not None:
                is_recent = now - last_updated <= timedelta(days=30)

            if is_recent:
                recent_topics.append(topic)

        recent_topics.sort(
            key=lambda topic: (
                self._timestamp_value(topic.get("last_updated", "")),
                self._status_rank(topic),
                self._priority_rank(topic),
            ),
            reverse=True,
        )
        return [topic["id"] for topic in recent_topics]

    def _decision_log_resource(self) -> str:
        candidates = [
            self.base_dir / "decisions" / "decision-log.json",
            self.base_dir / "decision-log.json",
            self.base_dir / "decisions" / "decision_log.json",
        ]
        for candidate in candidates:
            if candidate.exists():
                return self._relative_resource_path(candidate)
        return "decisions/decision-log.json"

    def _topic_resource(self, topic: Dict[str, Any]) -> str:
        return str(topic.get("card_path") or f"topic:{topic['id']}")

    def _relative_resource_path(self, path: Path) -> str:
        try:
            return path.relative_to(self.base_dir).as_posix()
        except ValueError:
            return path.as_posix()

    def _as_list(self, value: Any) -> List[str]:
        if value is None:
            return []
        if isinstance(value, list):
            return [self._clean_text(item) for item in value if self._clean_text(item)]
        if isinstance(value, str):
            if not value.strip():
                return []
            if "," in value:
                return [
                    self._clean_text(part)
                    for part in value.split(",")
                    if self._clean_text(part)
                ]
            return [self._clean_text(value)]
        return [self._clean_text(str(value))] if self._clean_text(str(value)) else []

    def _merge_lists(self, *values: Any) -> List[str]:
        merged: List[str] = []
        seen = set()
        for value in values:
            for item in self._as_list(value):
                lowered = item.lower()
                if lowered in seen:
                    continue
                seen.add(lowered)
                merged.append(item)
        return merged

    def _dedupe_topic_ids(self, topic_ids: List[str]) -> List[str]:
        deduped: List[str] = []
        seen = set()
        for topic_id in topic_ids:
            if not topic_id or topic_id in seen:
                continue
            seen.add(topic_id)
            deduped.append(topic_id)
        return deduped

    def _dedupe_strings(self, items: List[str]) -> List[str]:
        deduped: List[str] = []
        seen = set()
        for item in items:
            normalized = item.strip()
            if not normalized or normalized in seen:
                continue
            seen.add(normalized)
            deduped.append(normalized)
        return deduped

    def _render_markdown_list(self, items: List[str]) -> str:
        cleaned = [str(item).strip() for item in items if str(item).strip()]
        if not cleaned:
            return "- (none)"
        return "\n".join(f"- {item}" for item in cleaned)

    def _status_rank(self, topic: Dict[str, Any]) -> int:
        status = (topic.get("status") or "").lower()
        ranking = {"active": 4, "paused": 3, "archived": 2, "deprecated": 1}
        return ranking.get(status, 0)

    def _priority_rank(self, topic: Dict[str, Any]) -> int:
        priority = (topic.get("priority") or "").lower()
        ranking = {"high": 3, "medium": 2, "low": 1}
        return ranking.get(priority, 0)

    def _is_deprecated(self, topic: Dict[str, Any]) -> bool:
        status = (topic.get("status") or "").lower()
        evidence_level = (topic.get("evidence_level") or "").lower()
        return status == "deprecated" or evidence_level == "deprecated"

    def _parse_date(self, value: str) -> datetime | None:
        if not value:
            return None

        candidate = value.strip()
        if not candidate:
            return None

        try:
            candidate = candidate.replace("Z", "+00:00")
            parsed = datetime.fromisoformat(candidate)
        except ValueError:
            return None

        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        else:
            parsed = parsed.astimezone(timezone.utc)
        return parsed

    def _timestamp_value(self, value: str) -> float:
        parsed = self._parse_date(value)
        if parsed is None:
            return 0.0
        return parsed.timestamp()

    def _clean_text(self, value: Any) -> str:
        if value is None:
            return ""
        return str(value).strip()

    def _strip_quotes(self, value: str) -> str:
        return value.strip().strip("\"'")

    def _contains_cjk(self, token: str) -> bool:
        return any(self._is_cjk_char(char) for char in token)

    def _is_cjk_char(self, char: str) -> bool:
        return bool(re.match(r"[\u3400-\u4dbf\u4e00-\u9fff]", char))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--query", required=True)
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--write-active-context", action="store_true")
    args = parser.parse_args()

    try:
        base_dir = Path(args.project_root).expanduser() / ".petfish" / "fish-trail"
        router = TopicRouter(str(base_dir))
        route_result = router.route(args.query)

        output = dict(route_result)
        if args.write_active_context:
            output["active_context_path"] = router.write_active_context(
                route_result, args.query
            )

        json.dump(output, sys.stdout, ensure_ascii=False, indent=2)
        sys.stdout.write("\n")
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(1)
