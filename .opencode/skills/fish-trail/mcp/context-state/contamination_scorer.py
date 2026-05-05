"""Contamination risk scoring for Context Router MCP topics."""

import re
from datetime import datetime, timezone
from typing import Dict, List, Optional, Set, Tuple


class ContaminationScorer:
    """Scores contamination risk between two topic contexts."""

    def __init__(self):
        self.conflict_keyword_pairs = [
            ("增", "减"),
            ("添加", "删除"),
            ("扩展", "收缩"),
            ("复杂", "简化"),
            ("创建", "移除"),
            ("add", "remove"),
            ("expand", "reduce"),
            ("create", "delete"),
            ("build", "teardown"),
            ("increase", "decrease"),
        ]

        self.format_type_mappings = {
            "code": {
                "python",
                "javascript",
                "typescript",
                "java",
                "rust",
                "go",
                "function",
                "class",
                "implement",
                "代码",
                "实现",
                "编程",
            },
            "config": {
                "yaml",
                "json",
                "toml",
                "nginx",
                "docker",
                "配置",
                "config",
            },
            "doc": {
                "document",
                "文档",
                "markdown",
                "写作",
                "writing",
                "报告",
                "report",
            },
            "design": {
                "ui",
                "ux",
                "css",
                "figma",
                "设计",
                "layout",
                "样式",
                "animation",
            },
            "data": {
                "sql",
                "database",
                "数据",
                "schema",
                "migration",
                "query",
            },
            "ops": {
                "deploy",
                "server",
                "部署",
                "运维",
                "container",
                "kubernetes",
            },
            "review": {
                "review",
                "audit",
                "审查",
                "评审",
                "qa",
                "qc",
            },
        }

        self.related_format_pairs = {frozenset(("code", "config"))}
        self.compatible_format_pairs = {
            frozenset(("code", "doc")),
            frozenset(("code", "design")),
            frozenset(("code", "data")),
            frozenset(("code", "ops")),
            frozenset(("code", "review")),
            frozenset(("config", "doc")),
            frozenset(("config", "data")),
            frozenset(("config", "ops")),
            frozenset(("config", "review")),
            frozenset(("doc", "design")),
            frozenset(("doc", "review")),
            frozenset(("doc", "ops")),
            frozenset(("doc", "data")),
            frozenset(("design", "review")),
            frozenset(("data", "ops")),
            frozenset(("data", "review")),
            frozenset(("ops", "review")),
        }

        self.stopwords = {
            "a",
            "an",
            "and",
            "are",
            "as",
            "at",
            "be",
            "by",
            "for",
            "from",
            "in",
            "into",
            "is",
            "it",
            "of",
            "on",
            "or",
            "that",
            "the",
            "this",
            "to",
            "with",
            "we",
            "you",
            "your",
            "our",
            "about",
            "after",
            "before",
            "over",
            "under",
            "using",
            "use",
            "used",
            "will",
            "can",
            "may",
            "should",
            "must",
            "do",
            "does",
            "did",
            "not",
            "no",
            "yes",
            "的",
            "了",
            "和",
            "与",
            "及",
            "或",
            "是",
            "在",
            "对",
            "将",
            "把",
            "按",
            "让",
            "使",
            "为",
            "中",
            "内",
            "外",
            "上",
            "下",
            "前",
            "后",
            "再",
            "并",
            "被",
            "向",
            "从",
            "到",
            "等",
            "一个",
            "一种",
            "一些",
            "以及",
            "进行",
            "相关",
            "需要",
            "当前",
            "用于",
            "通过",
            "如果",
            "因为",
            "所以",
            "但是",
            "然后",
            "已经",
            "可以",
            "可能",
            "要求",
        }

        self.strong_opinion_words = {
            "决定",
            "must",
            "should",
            "必须",
            "reject",
            "拒绝",
            "结论",
        }

        self._english_pattern = re.compile(r"[a-z0-9_]+")
        self._split_pattern = re.compile(
            r"[\s,，。；;：:！!？?、/\\|()\[\]{}<>\-\n\r\t]+"
        )

    def score(self, topic_a: Dict, topic_b: Dict) -> Dict:
        dimensions = {
            "topic_distance": self._score_topic_distance(topic_a, topic_b),
            "goal_conflict": self._score_goal_conflict(topic_a, topic_b),
            "term_overloading": self._score_term_overloading(topic_a, topic_b),
            "output_format_divergence": self._score_format_divergence(topic_a, topic_b),
            "history_bias": self._score_history_bias(topic_a),
        }

        total = min(sum(dimensions.values()), 100)

        return {
            "total": total,
            "level": self._classify_level(total),
            "dimensions": dimensions,
        }

    def explain(self, topic_a: Dict, topic_b: Dict) -> Dict:
        topic_distance_score, topic_distance_reason = self._analyze_topic_distance(
            topic_a, topic_b
        )
        goal_conflict_score, goal_conflict_reason = self._analyze_goal_conflict(
            topic_a, topic_b
        )
        term_overloading_score, term_overloading_reason = (
            self._analyze_term_overloading(topic_a, topic_b)
        )
        format_score, format_reason = self._analyze_format_divergence(topic_a, topic_b)
        history_score, history_reason = self._analyze_history_bias(topic_a)

        dimensions = {
            "topic_distance": topic_distance_score,
            "goal_conflict": goal_conflict_score,
            "term_overloading": term_overloading_score,
            "output_format_divergence": format_score,
            "history_bias": history_score,
        }
        total = min(sum(dimensions.values()), 100)

        return {
            "total": total,
            "level": self._classify_level(total),
            "dimensions": dimensions,
            "reasons": {
                "topic_distance": topic_distance_reason,
                "goal_conflict": goal_conflict_reason,
                "term_overloading": term_overloading_reason,
                "output_format_divergence": format_reason,
                "history_bias": history_reason,
            },
        }

    def _score_topic_distance(self, topic_a: Dict, topic_b: Dict) -> int:
        return self._analyze_topic_distance(topic_a, topic_b)[0]

    def _score_goal_conflict(self, topic_a: Dict, topic_b: Dict) -> int:
        return self._analyze_goal_conflict(topic_a, topic_b)[0]

    def _score_term_overloading(self, topic_a: Dict, topic_b: Dict) -> int:
        return self._analyze_term_overloading(topic_a, topic_b)[0]

    def _score_format_divergence(self, topic_a: Dict, topic_b: Dict) -> int:
        return self._analyze_format_divergence(topic_a, topic_b)[0]

    def _score_history_bias(self, topic_a: Dict) -> int:
        return self._analyze_history_bias(topic_a)[0]

    def _extract_keywords(self, text: str) -> Set[str]:
        if not text:
            return set()

        normalized = str(text).lower()
        keywords = set()

        for token in self._english_pattern.findall(normalized):
            if token and token not in self.stopwords:
                keywords.add(token)

        for fragment in self._split_pattern.split(normalized):
            if not fragment:
                continue

            if self._contains_cjk(fragment):
                self._add_chinese_keywords(fragment, keywords)

        return keywords

    def _analyze_topic_distance(self, topic_a: Dict, topic_b: Dict) -> Tuple[int, str]:
        keywords_a = self._extract_keywords(self._topic_text(topic_a, ["scope"]))
        keywords_b = self._extract_keywords(self._topic_text(topic_b, ["scope"]))

        union = keywords_a | keywords_b
        intersection = keywords_a & keywords_b
        jaccard = float(len(intersection)) / float(len(union)) if union else 0.0
        score = int(round((1.0 - jaccard) * 20.0))

        if not union:
            reason = "No usable scope keywords were found in either topic, so similarity defaults to 0.00."
        else:
            reason = (
                "Scope keyword overlap is {overlap}/{union_count} "
                "(Jaccard {jaccard:.2f})."
            ).format(
                overlap=len(intersection),
                union_count=len(union),
                jaccard=jaccard,
            )

        return score, reason

    def _analyze_goal_conflict(self, topic_a: Dict, topic_b: Dict) -> Tuple[int, str]:
        keywords_a = self._extract_keywords(
            self._topic_text(topic_a, ["scope", "summary"])
        )
        keywords_b = self._extract_keywords(
            self._topic_text(topic_b, ["scope", "summary"])
        )

        matched_pairs = []
        for left, right in self.conflict_keyword_pairs:
            if (left in keywords_a and right in keywords_b) or (
                right in keywords_a and left in keywords_b
            ):
                matched_pairs.append("{0}/{1}".format(left, right))

        conflict_count = len(matched_pairs)
        if conflict_count == 0:
            score = 0
        elif conflict_count == 1:
            score = 10
        elif conflict_count == 2:
            score = 15
        else:
            score = 20

        if matched_pairs:
            reason = "Detected {count} goal-conflict pair(s): {pairs}.".format(
                count=conflict_count,
                pairs=", ".join(matched_pairs),
            )
        else:
            reason = "No defined goal-conflict keyword pairs were found across the two topics."

        return score, reason

    def _analyze_term_overloading(
        self, topic_a: Dict, topic_b: Dict
    ) -> Tuple[int, str]:
        signature_a = self._extract_keywords(
            self._topic_text(topic_a, ["title", "scope", "tags"])
        )
        signature_b = self._extract_keywords(
            self._topic_text(topic_b, ["title", "scope", "tags"])
        )
        shared_keywords = {
            keyword
            for keyword in (signature_a & signature_b)
            if self._is_meaningful_keyword(keyword)
        }

        summary_keywords_a = self._extract_keywords(
            self._topic_text(topic_a, ["summary"])
        )
        summary_keywords_b = self._extract_keywords(
            self._topic_text(topic_b, ["summary"])
        )
        summary_union = summary_keywords_a | summary_keywords_b
        summary_overlap = (
            float(len(summary_keywords_a & summary_keywords_b))
            / float(len(summary_union))
            if summary_union
            else 0.0
        )

        overloaded_keywords = []
        if summary_overlap < 0.3:
            for keyword in sorted(shared_keywords):
                if keyword in summary_keywords_a and keyword in summary_keywords_b:
                    overloaded_keywords.append(keyword)

        score = min(len(overloaded_keywords) * 5, 20)

        if overloaded_keywords:
            reason = (
                "Shared terms {keywords} appear in both summaries, but summary overlap is low "
                "(Jaccard {overlap:.2f})."
            ).format(
                keywords=", ".join(overloaded_keywords[:6]),
                overlap=summary_overlap,
            )
        elif shared_keywords:
            reason = (
                "Shared signature keywords exist, but summary overlap is {overlap:.2f}, "
                "so overloading was not flagged."
            ).format(overlap=summary_overlap)
        else:
            reason = "No meaningful shared keywords were found across title, scope, and tags."

        return score, reason

    def _analyze_format_divergence(
        self, topic_a: Dict, topic_b: Dict
    ) -> Tuple[int, str]:
        types_a, cues_a = self._detect_format_types(topic_a)
        types_b, cues_b = self._detect_format_types(topic_b)

        if types_a & types_b:
            score = 0
            relation = "same format family"
        elif self._has_format_relation(types_a, types_b, self.related_format_pairs):
            score = 5
            relation = "closely related format families"
        elif not types_a or not types_b:
            score = 10
            relation = (
                "format signal is incomplete, so divergence is treated as moderate"
            )
        elif self._has_format_relation(types_a, types_b, self.compatible_format_pairs):
            score = 10
            relation = "different but compatible format families"
        else:
            score = 20
            relation = "clearly different format families"

        reason = (
            "Topic A formats: {types_a} ({cues_a}); Topic B formats: {types_b} ({cues_b}); "
            "relation: {relation}."
        ).format(
            types_a=", ".join(sorted(types_a)) if types_a else "unknown",
            cues_a=", ".join(cues_a[:5]) if cues_a else "no strong cues",
            types_b=", ".join(sorted(types_b)) if types_b else "unknown",
            cues_b=", ".join(cues_b[:5]) if cues_b else "no strong cues",
            relation=relation,
        )

        return score, reason

    def _analyze_history_bias(self, topic_a: Dict) -> Tuple[int, str]:
        score = 0
        reasons = []

        summary = self._topic_text(topic_a, ["summary"])
        if len(summary) > 500:
            score += 5
            reasons.append("summary is longer than 500 characters")

        created_at = self._parse_datetime(topic_a.get("created_at"))
        updated_at = self._parse_datetime(topic_a.get("updated_at"))
        if created_at and updated_at and updated_at > created_at:
            elapsed_seconds = (updated_at - created_at).total_seconds()
            if elapsed_seconds > 7200:
                score += 5
                reasons.append("topic was updated more than 2 hours after creation")

        strong_words = self._find_strong_opinion_words(summary)
        if strong_words:
            score += 5
            reasons.append(
                "summary contains strong opinion words: {0}".format(
                    ", ".join(strong_words)
                )
            )

        tags = self._normalize_tags(topic_a.get("tags"))
        if len(tags) > 5:
            score += 5
            reasons.append("topic has more than 5 tags")

        score = min(score, 20)

        if not reasons:
            reason = "No history-bias signals were triggered for the previous topic."
        else:
            reason = "; ".join(reasons) + "."

        return score, reason

    def _topic_text(self, topic: Dict, fields: List[str]) -> str:
        topic = topic or {}
        parts = []
        for field in fields:
            value = topic.get(field)
            if field == "tags":
                parts.extend(self._normalize_tags(value))
            elif value is not None:
                parts.append(str(value))
        return " ".join(part for part in parts if part)

    def _normalize_tags(self, tags) -> List[str]:
        if tags is None:
            return []
        if isinstance(tags, (list, tuple, set)):
            return [str(tag) for tag in tags if tag is not None and str(tag).strip()]
        text = str(tags).strip()
        return [text] if text else []

    def _add_chinese_keywords(self, fragment: str, keywords: Set[str]) -> None:
        chinese_only = "".join(char for char in fragment if self._is_cjk(char))
        if not chinese_only:
            return

        if chinese_only not in self.stopwords and len(chinese_only) > 1:
            keywords.add(chinese_only)

        for char in chinese_only:
            if char not in self.stopwords:
                keywords.add(char)

        if len(chinese_only) >= 2:
            for index in range(len(chinese_only) - 1):
                bigram = chinese_only[index : index + 2]
                if bigram not in self.stopwords:
                    keywords.add(bigram)

    def _contains_cjk(self, text: str) -> bool:
        return any(self._is_cjk(char) for char in text)

    def _is_cjk(self, char: str) -> bool:
        return "\u4e00" <= char <= "\u9fff"

    def _is_meaningful_keyword(self, keyword: str) -> bool:
        if not keyword:
            return False
        if self._contains_cjk(keyword):
            return len(keyword) > 1
        return len(keyword) > 2

    def _detect_format_types(self, topic: Dict) -> Tuple[Set[str], List[str]]:
        text = self._topic_text(topic, ["scope", "tags", "summary"])
        normalized_text = text.lower()
        keywords = self._extract_keywords(normalized_text)

        detected_types = set()
        matched_cues = []
        for format_type, cue_words in self.format_type_mappings.items():
            current_matches = []
            for cue in cue_words:
                if self._cue_matches(cue, normalized_text, keywords):
                    current_matches.append(cue)

            if current_matches:
                detected_types.add(format_type)
                matched_cues.extend(current_matches)

        return detected_types, sorted(set(matched_cues))

    def _cue_matches(self, cue: str, text: str, keywords: Set[str]) -> bool:
        if cue in keywords:
            return True
        if self._contains_cjk(cue):
            return cue in text
        return cue in keywords

    def _has_format_relation(
        self, types_a: Set[str], types_b: Set[str], relations: Set[frozenset]
    ) -> bool:
        for left in types_a:
            for right in types_b:
                if frozenset((left, right)) in relations:
                    return True
        return False

    def _find_strong_opinion_words(self, text: str) -> List[str]:
        normalized_text = (text or "").lower()
        keywords = self._extract_keywords(normalized_text)
        found = []

        for word in sorted(self.strong_opinion_words):
            if self._contains_cjk(word):
                if word in normalized_text:
                    found.append(word)
            elif word in keywords:
                found.append(word)

        return found

    def _parse_datetime(self, value) -> Optional[datetime]:
        if not value:
            return None

        if isinstance(value, datetime):
            return self._normalize_datetime(value)

        text = str(value).strip()
        if not text:
            return None

        if text.endswith("Z"):
            text = text[:-1] + "+00:00"

        candidates = [text]
        if "T" in text:
            candidates.append(text.replace("T", " "))

        for candidate in candidates:
            try:
                return self._normalize_datetime(datetime.fromisoformat(candidate))
            except ValueError:
                continue

        for fmt in (
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%d %H:%M",
            "%Y-%m-%d",
        ):
            try:
                return datetime.strptime(text, fmt)
            except ValueError:
                continue

        return None

    def _normalize_datetime(self, value: datetime) -> datetime:
        if value.tzinfo is None:
            return value
        return value.astimezone(timezone.utc).replace(tzinfo=None)

    def _classify_level(self, total: int) -> str:
        if total <= 30:
            return "low"
        if total <= 60:
            return "medium"
        return "high"
