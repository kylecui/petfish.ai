"""Rule-based topic change detection for the Context Router MCP server."""

import re
from typing import List, Optional, Set


class TopicDetector:
    """Detect topic changes and relation types from user messages."""

    def __init__(self, embedding_manager=None):
        self._embedding = embedding_manager
        self.bilingual_map = {
            "测试": "test",
            "验证": "verification",
            "验收": "acceptance",
            "升级": "upgrade",
            "部署": "deploy",
            "安装": "install",
            "开发": "development",
            "发布": "release",
            "修复": "fix",
            "问题": "issue",
            "功能": "feature",
            "配置": "config",
            "脚本": "script",
            "文档": "documentation",
            "检查": "check",
            "审计": "audit",
            "质量": "quality",
            "门禁": "gate",
            "评分": "score",
            "风险": "risk",
            "话题": "topic",
            "上下文": "context",
            "污染": "contamination",
            "隔离": "isolation",
            "感知": "detection",
            "能力": "capability",
            "技能": "skill",
            "伙伴": "companion",
            "课程": "course",
            "实验": "lab",
            "提纲": "outline",
            "正文": "content",
            "平台": "platform",
            "命令": "command",
            "服务": "service",
            "重启": "restart",
            "改动": "change",
            "生效": "effective",
            "回归": "regression",
            "覆盖": "coverage",
            "断言": "assertion",
            "用例": "test case",
            "冒烟": "smoke test",
        }
        # Synonyms/aliases that should be considered equivalent in drift checks
        self.synonym_groups = [
            {
                "test",
                "testing",
                "qa",
                "verification",
                "check",
                "validate",
                "acceptance",
                "regression",
                "smoke test",
                "assertion",
                "test case",
                "coverage",
            },
            {"companion", "petfish", "gateway"},
            {"topic", "context", "fish-trail", "drift", "detection"},
            {"deploy", "deployment", "ci", "cd"},
            {"skill", "pack", "capability"},
            {"mcp", "server", "service", "tool"},
            {"install", "setup", "init"},
            {"upgrade", "update", "migration", "change", "effective"},
        ]
        self.reset_signals = [
            "重新开始",
            "忘掉前面",
            "清空上下文",
            "从头来",
            "全部重来",
            "start over",
            "fresh start",
            "reset context",
            "forget everything",
            "clean slate",
        ]
        self.archive_signals = [
            "做完了",
            "可以关了",
            "结束这个",
            "这个话题完成",
            "归档",
            "done with this",
            "close this",
            "archive",
            "finished",
            "wrap up",
        ]
        self.switch_signals = [
            "回到",
            "继续之前的",
            "切换到",
            "转到",
            "go back to",
            "switch to",
            "return to",
            "continue with",
        ]
        self.merge_signals = [
            "合并",
            "合到一起",
            "合在一起",
            "整合",
            "merge",
            "combine",
            "consolidate",
            "bring together",
        ]
        self.fork_signals = [
            "另外",
            "顺便",
            "额外",
            "分出来",
            "单独处理",
            "岔开一下",
            "分叉",
            "子话题",
            "by the way",
            "also",
            "separately",
            "side task",
            "branch off",
            "quick tangent",
            "fork",
            "split off",
            "spin off",
            "subtopic",
        ]
        self.bridge_signals = [
            "关联",
            "桥接",
            "交叉引用",
            "这两个有关系",
            "relate",
            "bridge",
            "cross-reference",
            "these are related",
        ]
        self.stopwords = {
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
        }
        self.risk_profile = {
            "continue": (0, "low"),
            "fork": (30, "low"),
            "switch": (40, "medium"),
            "merge": (50, "medium"),
            "archive": (10, "low"),
            "reset": (40, "medium"),
            "bridge": (35, "medium"),
        }
        self.min_fuzzy_switch_overlap = 0.4

    def detect(
        self,
        text: str,
        current_topic: Optional[dict],
        all_topics: List[dict],
    ) -> dict:
        """Detect the relation between a new message and existing topics."""
        normalized_text = (text or "").strip()
        lowered_text = normalized_text.lower()
        keywords = self._extract_keywords(normalized_text)
        current_topic_id = None
        if current_topic:
            current_topic_id = current_topic.get("id")

        if self._contains_any(lowered_text, self.reset_signals):
            return self._build_result(
                relation="reset",
                confidence=0.95,
                target_topic=None,
                suggestion="Start a fresh topic with empty context and do not inherit earlier discussion.",
            )

        if self._contains_any(lowered_text, self.archive_signals):
            return self._build_result(
                relation="archive",
                confidence=0.80,
                target_topic=None,
                suggestion=self._archive_suggestion(current_topic),
            )

        switch_target = self._find_best_switch_target(
            normalized_text,
            keywords,
            all_topics or [],
            current_topic_id,
        )
        explicit_switch = self._contains_any(lowered_text, self.switch_signals)

        if switch_target and (
            explicit_switch
            or self._topic_explicitly_referenced(lowered_text, keywords, switch_target)
        ):
            return self._build_result(
                relation="switch",
                confidence=0.85,
                target_topic=switch_target.get("id"),
                suggestion=self._switch_suggestion(switch_target, fuzzy=False),
            )

        if switch_target:
            overlap = self._calculate_topic_overlap(keywords, switch_target)
            if overlap >= self.min_fuzzy_switch_overlap:
                return self._build_result(
                    relation="switch",
                    confidence=0.60,
                    target_topic=switch_target.get("id"),
                    suggestion=self._switch_suggestion(switch_target, fuzzy=True),
                )

        if self._contains_any(lowered_text, self.merge_signals):
            return self._build_result(
                relation="merge",
                confidence=0.70,
                target_topic=None,
                suggestion="This may require merging topics. Confirm before combining contexts.",
            )

        if self._contains_any(lowered_text, self.fork_signals):
            return self._build_result(
                relation="fork",
                confidence=0.80,
                target_topic=None,
                suggestion=self._fork_suggestion(current_topic),
            )

        if self._contains_any(lowered_text, self.bridge_signals):
            return self._build_result(
                relation="bridge",
                confidence=0.60,
                target_topic=None,
                suggestion="These topics seem related. Confirm whether to create a bridge instead of merging them.",
            )

        # Semantic drift detection: check keyword overlap with current topic.
        # If the message has meaningful content but zero/near-zero overlap
        # with the current topic's title+scope+tags, flag as potential drift.
        if current_topic and keywords:
            drift_result = self._check_semantic_drift(
                normalized_text, keywords, current_topic
            )
            if drift_result:
                return drift_result

        return self._build_result(
            relation="continue",
            confidence=0.90,
            target_topic=None,
            suggestion=self._continue_suggestion(current_topic),
        )

    def _extract_keywords(self, text: str) -> Set[str]:
        """Split text into lowercase keywords and remove stopwords."""
        normalized = (text or "").lower()
        normalized = re.sub(r"([a-z0-9])([\u4e00-\u9fff])", r"\1 \2", normalized)
        normalized = re.sub(r"([\u4e00-\u9fff])([a-z0-9])", r"\1 \2", normalized)
        tokens = re.split(r"[^\w\u4e00-\u9fff]+", normalized)

        keywords = set()
        for token in tokens:
            token = token.strip("_")
            if not token:
                continue
            if token in self.stopwords:
                continue
            if token.isdigit():
                continue
            if len(token) == 1 and token.isascii():
                continue
            keywords.add(token)

        for keyword in list(keywords):
            if any(self._is_cjk(char) for char in keyword):
                self._add_cjk_keywords(keyword, keywords)

        return keywords

    def _add_cjk_keywords(self, token: str, keywords: Set[str]) -> None:
        cjk_only = "".join(char for char in token if self._is_cjk(char))
        if not cjk_only:
            return

        for char in cjk_only:
            if char not in self.stopwords:
                keywords.add(char)

        if len(cjk_only) >= 2:
            for index in range(len(cjk_only) - 1):
                bigram = cjk_only[index : index + 2]
                if bigram not in self.stopwords:
                    keywords.add(bigram)

    def _is_cjk(self, char: str) -> bool:
        return "\u4e00" <= char <= "\u9fff"

    def _calculate_topic_overlap(self, keywords: Set[str], topic: dict) -> float:
        """Calculate Jaccard similarity between message and topic keywords."""
        topic_text = "{} {}".format(
            topic.get("title", "") or "",
            topic.get("scope", "") or "",
        )
        topic_keywords = self._extract_keywords(topic_text)

        if not keywords or not topic_keywords:
            return 0.0

        union = keywords | topic_keywords
        if not union:
            return 0.0

        intersection = keywords & topic_keywords
        return len(intersection) / len(union)

    def _find_best_switch_target(
        self,
        text: str,
        keywords: Set[str],
        all_topics: List[dict],
        current_topic_id: Optional[str],
    ) -> Optional[dict]:
        """Find the best existing topic candidate for a switch."""
        lowered_text = (text or "").lower()
        best_topic = None
        best_score = 0.0

        for topic in all_topics or []:
            topic_id = topic.get("id")
            if current_topic_id is not None and topic_id == current_topic_id:
                continue

            overlap = self._calculate_topic_overlap(keywords, topic)
            score = overlap
            if self._topic_explicitly_referenced(lowered_text, keywords, topic):
                score = max(score, 1.0)

            if score > best_score:
                best_score = score
                best_topic = topic

        if best_score <= 0.0:
            return None

        return best_topic

    def _build_result(
        self,
        relation: str,
        confidence: float,
        target_topic: Optional[str],
        suggestion: str,
    ) -> dict:
        risk, risk_level = self.risk_profile[relation]
        return {
            "relation": relation,
            "confidence": confidence,
            "risk": risk,
            "risk_level": risk_level,
            "target_topic": target_topic,
            "suggestion": suggestion,
        }

    def _contains_any(self, text: str, phrases: List[str]) -> bool:
        """Check whether text contains any signal phrase."""
        lowered_text = (text or "").lower()
        raw_tokens = set(
            token for token in re.split(r"[^\w\u4e00-\u9fff]+", lowered_text) if token
        )

        for phrase in phrases:
            phrase_lower = phrase.lower()
            if " " in phrase_lower or self._contains_cjk(phrase_lower):
                if phrase_lower in lowered_text:
                    return True
                continue

            if phrase_lower in raw_tokens:
                return True

        return False

    def _contains_cjk(self, text: str) -> bool:
        for char in text:
            if "\u4e00" <= char <= "\u9fff":
                return True
        return False

    def _topic_explicitly_referenced(
        self,
        lowered_text: str,
        keywords: Set[str],
        topic: dict,
    ) -> bool:
        title = str(topic.get("title", "") or "").strip()
        scope = str(topic.get("scope", "") or "").strip()

        if title:
            title_lower = title.lower()
            if self._contains_cjk(title_lower) and title_lower in lowered_text:
                return True
            if " " in title_lower and title_lower in lowered_text:
                return True

            title_keywords = self._extract_keywords(title)
            if title_keywords and title_keywords.issubset(keywords):
                return True

        if scope:
            scope_lower = scope.lower()
            if self._contains_cjk(scope_lower) and scope_lower in lowered_text:
                return True

        return False

    def _expand_bilingual(self, keywords: Set[str]) -> Set[str]:
        """Expand keyword set with bilingual equivalents, synonyms, and stemming."""
        expanded = set(keywords)
        for kw in list(keywords):
            # Chinese → English mapping
            if kw in self.bilingual_map:
                expanded.add(self.bilingual_map[kw])
            # Reverse lookup: English → add Chinese equivalent
            for zh, en in self.bilingual_map.items():
                if kw == en or kw == en + "s" or kw + "s" == en:
                    expanded.add(zh)
                    expanded.add(en)
            # Simple English plural stemming
            if kw.endswith("s") and len(kw) > 3:
                expanded.add(kw[:-1])
            if not kw.endswith("s") and len(kw) > 2:
                expanded.add(kw + "s")
            # Synonym group expansion
            for group in self.synonym_groups:
                if kw in group:
                    expanded.update(group)
                    break
        return expanded

    def _check_semantic_drift(
        self, text: str, keywords: Set[str], current_topic: dict
    ) -> Optional[dict]:
        """Detect semantic drift by comparing message keywords to current topic.

        Uses bilingual keyword expansion and meaningful-token filtering to
        handle cross-language scenarios (Chinese message vs English topic).

        Tier 1: Keyword Jaccard (fast, <1ms)
        Tier 2: Embedding cosine similarity (optional, ~30ms) — only in ambiguous zone

        Returns a fork result if drift is detected, or None to fall through
        to the default continue path.
        """
        # Build topic keyword set from title + scope + tags
        topic_text = "{} {} {}".format(
            current_topic.get("title", "") or "",
            current_topic.get("scope", "") or "",
            " ".join(current_topic.get("tags", []) or []),
        )
        topic_keywords = self._extract_keywords(topic_text)

        # If current topic has no keywords (no title/scope/tags), skip drift check
        if not topic_keywords:
            return None

        # Expand both sets with bilingual equivalents
        expanded_keywords = self._expand_bilingual(keywords)
        expanded_topic = self._expand_bilingual(topic_keywords)

        # Meaningful-token filter: only count tokens with len >= 2
        # This prevents CJK single-character inflation of the denominator
        meaningful_input = {k for k in expanded_keywords if len(k) >= 2}
        meaningful_topic = {k for k in expanded_topic if len(k) >= 2}

        # Need enough meaningful input tokens for comparison
        if len(meaningful_input) < 3:
            return None

        # Calculate relevance: intersection of meaningful tokens / input count
        intersection = meaningful_input & meaningful_topic
        relevance = len(intersection) / len(meaningful_input)

        # High relevance — clearly on-topic
        if relevance >= 0.10:
            return None

        # Ambiguous zone: consult embedding Tier 2 if available
        if relevance > 0.0 and self._embedding and self._embedding.available:
            sim = self._embedding.similarity(text, topic_text)
            if sim is not None:
                if sim > 0.5:
                    return None  # on-topic per embedding
                elif sim < 0.3:
                    return {
                        "relation": "fork",
                        "confidence": 0.65,
                        "risk": 45,
                        "risk_level": "medium",
                        "target_topic": None,
                        "suggestion": (
                            'This message appears unrelated to "{}". '
                            "Consider forking a new topic or confirming you want to continue."
                        ).format(self._topic_title(current_topic) or "current topic"),
                    }
                else:
                    return {
                        "relation": "fork",
                        "confidence": 0.55,
                        "risk": 35,
                        "risk_level": "medium",
                        "target_topic": None,
                        "suggestion": (
                            'This message may be drifting from "{}". '
                            "Consider forking a new topic if changing direction."
                        ).format(self._topic_title(current_topic) or "current topic"),
                    }

        # Zero or near-zero relevance with meaningful keywords — likely drift
        risk = 45 if relevance == 0.0 else 35
        confidence = 0.65 if relevance == 0.0 else 0.55

        title = self._topic_title(current_topic) or "current topic"
        return {
            "relation": "fork",
            "confidence": confidence,
            "risk": risk,
            "risk_level": "medium",
            "target_topic": None,
            "suggestion": (
                'This message appears unrelated to "{}". '
                "Consider forking a new topic or confirming you want to continue."
            ).format(title),
        }

    def _continue_suggestion(self, current_topic: Optional[dict]) -> str:
        title = self._topic_title(current_topic)
        if title:
            return 'Continue current topic "{}".'.format(title)
        return "Continue in the current context."

    def _fork_suggestion(self, current_topic: Optional[dict]) -> str:
        title = self._topic_title(current_topic)
        if title:
            return (
                'Create a child topic from "{}" and handle this as a side task.'.format(
                    title
                )
            )
        return "Create a separate topic for this side task."

    def _archive_suggestion(self, current_topic: Optional[dict]) -> str:
        title = self._topic_title(current_topic)
        if title:
            return 'This sounds complete. Confirm archiving topic "{}".'.format(title)
        return "This sounds complete. Confirm archiving the current topic."

    def _switch_suggestion(self, target_topic: dict, fuzzy: bool) -> str:
        title = (
            self._topic_title(target_topic) or target_topic.get("id") or "target topic"
        )
        if fuzzy:
            return 'This looks closer to existing topic "{}"; consider switching to it.'.format(
                title
            )
        return 'Switch to existing topic "{}" and load its context.'.format(title)

    def _topic_title(self, topic: Optional[dict]) -> Optional[str]:
        if not topic:
            return None

        title = topic.get("title")
        if title is None:
            return None

        title = str(title).strip()
        return title or None
