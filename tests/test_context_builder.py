# pyright: reportMissingImports=false

from pathlib import Path
import sys


MODULE_DIR = (
    Path(__file__).resolve().parents[1]
    / "packs"
    / "context-router-skill"
    / ".opencode"
    / "skills"
    / "context-router"
    / "mcp"
    / "context-state"
)
sys.path.insert(0, str(MODULE_DIR))

from context_builder import ContextBuilder


def make_builder(tmp_path):
    base_dir = tmp_path / "workspace"
    contexts_dir = base_dir / "contexts"
    contexts_dir.mkdir(parents=True)
    return ContextBuilder(str(base_dir)), contexts_dir


def test_build_generates_context_package_with_required_sections(tmp_path):
    builder, contexts_dir = make_builder(tmp_path)
    topic = {
        "id": "topic-alpha",
        "title": "Topic Alpha",
        "status": "active",
        "scope": "Context routing and package generation",
        "created_at": "2026-05-03T08:00:00Z",
        "updated_at": "2026-05-03T09:00:00Z",
        "parent": "root-topic",
        "summary": "Build tests for context packages.",
    }
    related_topics = [
        {"relation": "related", "id": "topic-beta", "title": "Topic Beta"}
    ]

    result = builder.build(topic, related_topics, [])

    package_path = Path(result["path"])
    assert package_path == contexts_dir / "topic-alpha.context.md"
    assert package_path.exists()
    assert result["size"] == package_path.stat().st_size

    content = package_path.read_text(encoding="utf-8")
    for section in [
        "# Context Package: Topic Alpha",
        "## Topic Info",
        "## Summary",
        "## Key Decisions",
        "## Active Context",
        "## Related Topics",
    ]:
        assert section in content


def test_build_with_no_decisions_uses_empty_message(tmp_path):
    builder, contexts_dir = make_builder(tmp_path)
    topic = {
        "id": "topic-empty-decisions",
        "title": "Empty Decisions",
        "status": "active",
        "scope": "Verify empty decision rendering",
        "created_at": "2026-05-03T08:00:00Z",
        "updated_at": "2026-05-03T09:00:00Z",
        "summary": "No decisions yet.",
    }

    builder.build(topic, [], [])

    content = (contexts_dir / "topic-empty-decisions.context.md").read_text(
        encoding="utf-8"
    )
    assert "No decisions recorded." in content


def test_build_includes_only_related_decisions(tmp_path):
    builder, contexts_dir = make_builder(tmp_path)
    topic = {
        "id": "topic-decisions",
        "title": "Decision Topic",
        "status": "active",
        "scope": "Track related decisions",
        "created_at": "2026-05-03T08:00:00Z",
        "updated_at": "2026-05-03T09:00:00Z",
        "summary": "Collect decisions tied to this topic.",
    }
    decisions = [
        {
            "timestamp": "2026-05-03T10:00:00Z",
            "action": "Chose bridge mode",
            "source_topic": "topic-decisions",
            "target_topic": "topic-bridge",
        },
        {
            "timestamp": "2026-05-03T08:30:00Z",
            "action": "Defined initial scope",
            "source_topic": "topic-decisions",
            "target_topic": "",
        },
        {
            "timestamp": "2026-05-03T09:00:00Z",
            "action": "Archived stale notes",
            "source_topic": "topic-other",
            "target_topic": "topic-else",
        },
    ]

    builder.build(topic, [], decisions)

    content = (contexts_dir / "topic-decisions.context.md").read_text(encoding="utf-8")
    assert "- [2026-05-03T08:30:00Z] Defined initial scope" in content
    assert "- [2026-05-03T10:00:00Z] Chose bridge mode" in content
    assert "Archived stale notes" not in content


def test_build_bridge_generates_bridge_info_section(tmp_path):
    builder, contexts_dir = make_builder(tmp_path)
    topic_a = {
        "id": "topic-source",
        "title": "Source Topic",
        "status": "active",
        "scope": "Install workflow",
        "summary": "Covers installer behavior.",
    }
    topic_b = {
        "id": "topic-target",
        "title": "Target Topic",
        "status": "active",
        "scope": "Release workflow",
        "summary": "Covers release behavior.",
    }

    result = builder.build_bridge(
        topic_a,
        topic_b,
        ["release tag", "latest version"],
        ["remote-install.sh", "GitHub Releases"],
    )

    bridge_path = Path(result["path"])
    assert bridge_path == contexts_dir / "topic-source_bridge_topic-target.context.md"
    assert bridge_path.exists()

    content = bridge_path.read_text(encoding="utf-8")
    assert "## Bridge Info" in content
    assert "## Cross References" in content
    assert "Source Topic" in content
    assert "Target Topic" in content


def test_export_generates_export_file_with_handoff_sections(tmp_path):
    builder, contexts_dir = make_builder(tmp_path)
    topic = {
        "id": "topic-export",
        "title": "Export Topic",
        "status": "active",
        "scope": "Prepare handoff package",
        "created_at": "2026-05-03T08:00:00Z",
        "updated_at": "2026-05-03T09:00:00Z",
        "summary": "TODO: Verify session history before handoff.",
    }
    decisions = [
        {
            "timestamp": "2026-05-03T10:15:00Z",
            "action": "Prepared export draft",
            "source_topic": "topic-export",
            "target_topic": "review-topic",
        }
    ]

    result = builder.export(topic, [], decisions)

    export_path = Path(result["path"])
    assert export_path == contexts_dir / "topic-export.export.md"
    assert export_path.exists()

    content = export_path.read_text(encoding="utf-8")
    assert "## Handoff Info" in content
    assert "## Session History" in content
    assert "Prepared export draft" in content


def test_export_includes_custom_reason(tmp_path):
    builder, contexts_dir = make_builder(tmp_path)
    topic = {
        "id": "topic-export-reason",
        "title": "Export Reason Topic",
        "status": "active",
        "scope": "Check export reason rendering",
        "created_at": "2026-05-03T08:00:00Z",
        "updated_at": "2026-05-03T09:00:00Z",
        "summary": "Capture why the export happened.",
    }

    builder.export(topic, [], [], reason="Hand off to QA for trigger review")

    content = (contexts_dir / "topic-export-reason.export.md").read_text(
        encoding="utf-8"
    )
    assert "Hand off to QA for trigger review" in content


def test_freeze_creates_snapshot_and_keeps_original_package(tmp_path):
    builder, contexts_dir = make_builder(tmp_path)
    topic = {
        "id": "topic-freeze",
        "title": "Freeze Topic",
        "status": "active",
        "scope": "Snapshot generated context",
        "created_at": "2026-05-03T08:00:00Z",
        "updated_at": "2026-05-03T09:00:00Z",
        "summary": "Freeze the current package state.",
    }

    result = builder.freeze(topic, [], [])

    frozen_path = Path(result["path"])
    original_path = contexts_dir / "topic-freeze.context.md"
    assert original_path.exists()
    assert frozen_path.exists()
    assert frozen_path != original_path
    assert ".context.frozen." in frozen_path.name
    assert result["size"] == frozen_path.stat().st_size


def test_build_appends_size_warning_for_large_package(tmp_path):
    builder, contexts_dir = make_builder(tmp_path)
    topic = {
        "id": "topic-large",
        "title": "Large Topic",
        "status": "active",
        "scope": "Generate oversized package",
        "created_at": "2026-05-03T08:00:00Z",
        "updated_at": "2026-05-03T09:00:00Z",
        "summary": "Large context block. " * 400,
    }

    builder.build(topic, [], [])

    content = (contexts_dir / "topic-large.context.md").read_text(encoding="utf-8")
    assert builder.SIZE_WARNING in content
