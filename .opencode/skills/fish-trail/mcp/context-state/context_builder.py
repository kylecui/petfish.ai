"""Build Markdown context packages for the Context Router MCP server."""

import re
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


class ContextBuilder:
    """Generate standard, bridge, export, and frozen context packages."""

    STANDARD_LIMIT = 5 * 1024
    BRIDGE_LIMIT = 3 * 1024
    EXPORT_LIMIT = 8 * 1024
    SIZE_WARNING = "<!-- Warning: package exceeds recommended size -->"

    def __init__(self, base_dir: str):
        self.base_dir = Path(base_dir)
        self.contexts_dir = self.base_dir / "contexts"

    def build(
        self,
        topic: Dict[str, Any],
        related_topics: List[Dict[str, Any]],
        decisions: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        topic_id = self._topic_id(topic)
        topic_path = self.contexts_dir / f"{topic_id}.context.md"
        content = self._render_standard_package(topic, related_topics, decisions)
        return self._write_package(topic_path, content, self.STANDARD_LIMIT)

    def build_bridge(
        self,
        topic_a: Dict[str, Any],
        topic_b: Dict[str, Any],
        shared_keywords: List[str],
        cross_refs: List[str],
    ) -> Dict[str, Any]:
        topic_a_id = self._topic_id(topic_a)
        topic_b_id = self._topic_id(topic_b)
        bridge_id = f"{topic_a_id}_bridge_{topic_b_id}"
        bridge_path = self.contexts_dir / f"{bridge_id}.context.md"

        shared_scope = self._join_items(shared_keywords, "No shared scope identified.")
        generated_at = self._now_iso()
        summary = (
            f"Bridge package connecting {self._topic_title(topic_a)} and "
            f"{self._topic_title(topic_b)}."
        )
        if shared_keywords:
            summary += f" Shared keywords: {', '.join(shared_keywords)}."

        related_topics = [
            {
                "relation": "source",
                "id": topic_a_id,
                "title": self._topic_title(topic_a),
            },
            {
                "relation": "target",
                "id": topic_b_id,
                "title": self._topic_title(topic_b),
            },
        ]

        active_context = self._render_bridge_active_context(
            topic_a,
            topic_b,
            shared_keywords,
        )

        extra_sections = [
            "## Bridge Info",
            "",
            f"- **Source Topic**: {self._topic_title(topic_a)} ({topic_a_id})",
            f"- **Target Topic**: {self._topic_title(topic_b)} ({topic_b_id})",
            f"- **Shared Scope**: {shared_scope}",
            "",
            "## Cross References",
            "",
            self._render_bullets(cross_refs, "No cross references identified."),
        ]

        content = self._compose_package(
            title=f"{self._topic_title(topic_a)} ↔ {self._topic_title(topic_b)}",
            info_lines=[
                f"- **ID**: {bridge_id}",
                "- **Status**: bridge",
                f"- **Scope**: {shared_scope}",
                f"- **Created**: {generated_at}",
                f"- **Updated**: {generated_at}",
                "- **Parent**: none",
            ],
            summary=summary,
            key_decisions="No decisions recorded.",
            active_context=active_context,
            related_topics=self._render_related_topics(related_topics),
            extra_sections=extra_sections,
        )
        return self._write_package(bridge_path, content, self.BRIDGE_LIMIT)

    def export(
        self,
        topic: Dict[str, Any],
        related_topics: List[Dict[str, Any]],
        decisions: List[Dict[str, Any]],
        reason: str = "",
        session_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        topic_id = self._topic_id(topic)
        export_path = self.contexts_dir / f"{topic_id}.export.md"
        topic_decisions = self._decisions_for_topic(topic_id, decisions)

        if session_id is not None:
            topic_decisions = [
                d for d in topic_decisions if d.get("session_id") == session_id
            ]

        extra_sections = [
            "## Handoff Info",
            "",
            f"- **Exported At**: {self._now_iso()}",
            f"- **Export Reason**: {reason.strip() or 'Manual export'}",
            f"- **Session**: {session_id or 'all sessions'}",
            "",
            "## Session History",
            "",
            self._render_decisions(topic_decisions, "No session history."),
            "",
            "## Next Steps",
            "",
            self._extract_next_steps(topic.get("summary")),
        ]

        content = self._compose_package(
            title=self._topic_title(topic),
            info_lines=self._topic_info_lines(topic),
            summary=self._topic_summary(topic),
            key_decisions=self._render_decisions(
                topic_decisions, "No decisions recorded."
            ),
            active_context=self._render_active_context(topic),
            related_topics=self._render_related_topics(related_topics),
            extra_sections=extra_sections,
        )
        return self._write_package(export_path, content, self.EXPORT_LIMIT)

    def build_resume_package(
        self,
        session_context: Dict[str, Any],
        topic: Optional[Dict[str, Any]],
        related_topics: List[Dict[str, Any]],
        decisions: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        session_id = str(session_context.get("session_id") or "unknown-session")
        resume_path = self.contexts_dir / f"{session_id}.resume.md"

        session_summary = session_context.get("summary")
        if session_summary is not None and str(session_summary).strip():
            summary = str(session_summary).strip()
        elif topic is not None:
            topic_summary = topic.get("summary")
            if topic_summary is not None and str(topic_summary).strip():
                summary = str(topic_summary).strip()
            else:
                summary = "No summary."
        else:
            summary = "No summary."

        timeline_lines = []
        for event in session_context.get("timeline_digest") or []:
            if not isinstance(event, dict):
                continue
            timeline_lines.append(
                "- [{}] {} (topic: {})".format(
                    event.get("ts") or "unknown",
                    event.get("type") or "unknown",
                    event.get("topic_id") or "unknown",
                )
            )

        content = self._compose_package(
            title=(
                f"Resume: {self._topic_title(topic)}"
                if topic is not None
                else f"Resume: Session {session_id}"
            ),
            info_lines=[
                f"- **Session ID**: {session_id}",
                (
                    f"- **Inherited From**: "
                    f"{session_context.get('inherited_from') or 'none'}"
                ),
                f"- **Status**: {session_context.get('status') or 'unknown'}",
                (
                    f"- **Last Activity**: "
                    f"{session_context.get('last_activity_at') or 'unknown'}"
                ),
                (
                    f"- **Active Topic ID**: "
                    f"{session_context.get('active_topic_id') or 'none'}"
                ),
            ],
            summary=summary,
            key_decisions=self._render_decisions(decisions, "No decisions recorded."),
            active_context=(
                self._render_active_context(topic)
                if topic is not None
                else "No active topic context."
            ),
            related_topics=self._render_related_topics(related_topics),
            extra_sections=[
                "## Session Timeline",
                "",
                "\n".join(timeline_lines) or "No session timeline.",
            ],
        )
        return self._write_package(resume_path, content, self.EXPORT_LIMIT)

    def freeze(
        self,
        topic: Dict[str, Any],
        related_topics: List[Dict[str, Any]],
        decisions: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        latest = self.build(topic, related_topics, decisions)
        source_path = Path(latest["path"])
        frozen_path = self.contexts_dir / (
            f"{self._topic_id(topic)}.context.frozen.{self._timestamp_for_filename()}.md"
        )
        frozen_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source_path, frozen_path)
        size = frozen_path.stat().st_size
        return {"path": str(frozen_path), "size": size}

    def _write_file(self, path: str, content: str) -> int:
        file_path = Path(path)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        payload = content.encode("utf-8")
        with open(file_path, "wb") as handle:
            handle.write(payload)
        return len(payload)

    def _write_package(
        self, path: Path, content: str, size_limit: int
    ) -> Dict[str, Any]:
        final_content = content
        if len(content.encode("utf-8")) > size_limit:
            final_content = content.rstrip() + "\n\n" + self.SIZE_WARNING + "\n"
        size = self._write_file(str(path), final_content)
        return {"path": str(path), "size": size}

    def _render_standard_package(
        self,
        topic: Dict[str, Any],
        related_topics: List[Dict[str, Any]],
        decisions: List[Dict[str, Any]],
    ) -> str:
        topic_id = self._topic_id(topic)
        topic_decisions = self._decisions_for_topic(topic_id, decisions)
        return self._compose_package(
            title=self._topic_title(topic),
            info_lines=self._topic_info_lines(topic),
            summary=self._topic_summary(topic),
            key_decisions=self._render_decisions(
                topic_decisions, "No decisions recorded."
            ),
            active_context=self._render_active_context(topic),
            related_topics=self._render_related_topics(related_topics),
        )

    def _compose_package(
        self,
        title: str,
        info_lines: List[str],
        summary: str,
        key_decisions: str,
        active_context: str,
        related_topics: str,
        extra_sections: Optional[List[str]] = None,
    ) -> str:
        lines = [
            f"# Context Package: {title}",
            "",
            "## Topic Info",
            "",
        ]
        lines.extend(info_lines)
        lines.extend(
            [
                "",
                "## Summary",
                "",
                summary,
                "",
                "## Key Decisions",
                "",
                key_decisions,
                "",
                "## Active Context",
                "",
                active_context,
                "",
                "## Related Topics",
                "",
                related_topics,
            ]
        )

        if extra_sections:
            lines.extend([""] + extra_sections)

        return "\n".join(lines).rstrip() + "\n"

    def _topic_info_lines(self, topic: Dict[str, Any]) -> List[str]:
        return [
            f"- **ID**: {self._topic_id(topic)}",
            f"- **Status**: {topic.get('status') or 'unknown'}",
            f"- **Scope**: {topic.get('scope') or 'No scope defined.'}",
            f"- **Created**: {topic.get('created_at') or 'unknown'}",
            f"- **Updated**: {topic.get('updated_at') or 'unknown'}",
            f"- **Parent**: {topic.get('parent') or 'none'}",
        ]

    def _topic_id(self, topic: Dict[str, Any]) -> str:
        return str(topic.get("id") or "unknown-topic")

    def _topic_title(self, topic: Dict[str, Any]) -> str:
        return str(topic.get("title") or self._topic_id(topic))

    def _topic_summary(self, topic: Dict[str, Any]) -> str:
        summary = topic.get("summary")
        if summary is None:
            return "No summary yet."
        text = str(summary).strip()
        return text or "No summary yet."

    def _decisions_for_topic(
        self,
        topic_id: str,
        decisions: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        matches = []
        for decision in decisions or []:
            source_topic = str(decision.get("source_topic") or "")
            target_topic = str(decision.get("target_topic") or "")
            if topic_id in {source_topic, target_topic}:
                matches.append(decision)
        matches.sort(key=lambda item: str(item.get("timestamp") or ""))
        return matches

    def _render_decisions(
        self,
        decisions: List[Dict[str, Any]],
        empty_message: str,
    ) -> str:
        if not decisions:
            return empty_message

        lines = []
        for decision in decisions:
            timestamp = decision.get("timestamp") or "unknown"
            action = decision.get("action") or "No action recorded."
            lines.append(f"- [{timestamp}] {action}")
        return "\n".join(lines)

    def _render_active_context(self, topic: Dict[str, Any]) -> str:
        status = str(topic.get("status") or "").lower()
        if status == "archived":
            return "This topic is archived."

        scope = topic.get("scope") or "No scope defined."
        summary = self._topic_summary(topic)
        return f"Current scope: {scope}\n\nRecent summary: {summary}"

    def _render_bridge_active_context(
        self,
        topic_a: Dict[str, Any],
        topic_b: Dict[str, Any],
        shared_keywords: List[str],
    ) -> str:
        status_a = str(topic_a.get("status") or "").lower()
        status_b = str(topic_b.get("status") or "").lower()
        if status_a == "archived" and status_b == "archived":
            return "Both linked topics are archived."

        scope_text = self._join_items(shared_keywords, "No shared scope identified.")
        return (
            f"Shared scope: {scope_text}\n\n"
            f"Source summary: {self._topic_summary(topic_a)}\n\n"
            f"Target summary: {self._topic_summary(topic_b)}"
        )

    def _render_related_topics(self, related_topics: List[Dict[str, Any]]) -> str:
        if not related_topics:
            return "No related topics."

        lines = []
        for item in related_topics:
            relation = item.get("relation") or "related"
            topic_title = (
                item.get("title")
                or item.get("topic_title")
                or item.get("target_title")
                or item.get("source_title")
                or item.get("id")
                or item.get("topic_id")
                or "unknown"
            )
            topic_id = (
                item.get("id")
                or item.get("topic_id")
                or item.get("target_topic")
                or item.get("source_topic")
                or "unknown"
            )
            lines.append(f"- [{relation}] {topic_title} ({topic_id})")
        return "\n".join(lines)

    def _render_bullets(self, items: List[str], empty_message: str) -> str:
        cleaned_items = []
        for item in items or []:
            text = str(item).strip()
            if text:
                cleaned_items.append(f"- {text}")
        if not cleaned_items:
            return empty_message
        return "\n".join(cleaned_items)

    def _extract_next_steps(self, summary: Any) -> str:
        summary_text = ""
        if summary is not None:
            summary_text = str(summary).strip()
        if not summary_text:
            return "No next steps identified."

        markers = [
            "todo",
            "next step",
            "next steps",
            "follow up",
            "follow-up",
            "action item",
            "pending",
            "- [ ]",
            "[ ]",
        ]

        candidates = []
        for line in summary_text.splitlines():
            stripped = line.strip()
            if not stripped:
                continue
            lowered = stripped.lower()
            if any(marker in lowered for marker in markers):
                candidates.append(stripped)

        if not candidates:
            sentence_candidates = re.split(r"(?<=[.!?])\s+", summary_text)
            for sentence in sentence_candidates:
                stripped = sentence.strip()
                if not stripped:
                    continue
                lowered = stripped.lower()
                if any(marker in lowered for marker in markers):
                    candidates.append(stripped)

        cleaned = []
        for item in candidates:
            normalized = re.sub(r"^[-*]\s*", "", item)
            normalized = re.sub(r"^\[\s?\]\s*", "", normalized)
            normalized = normalized.strip()
            if normalized:
                cleaned.append(f"- {normalized}")

        if not cleaned:
            return "No next steps identified."
        return "\n".join(cleaned)

    def _join_items(self, items: List[str], empty_message: str) -> str:
        cleaned = []
        for item in items or []:
            text = str(item).strip()
            if text:
                cleaned.append(text)
        if not cleaned:
            return empty_message
        return ", ".join(cleaned)

    def _now_iso(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def _timestamp_for_filename(self) -> str:
        return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
