# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""
Setup script for Topic-Aware Compaction A/B Test.

Creates two test directories:
  - test-baseline/  (OpenCode project, fish-trail data, NO plugin)
  - test-plugin/    (OpenCode project, fish-trail data, WITH Phase 2 plugin)

Both directories get:
  - opencode.json with low context_limit to trigger compaction quickly
  - .petfish/fish-trail/ with synthetic topic data matching the test conversation
  - .opencode/ directory for OpenCode recognition

Run from the repo root:
  uv run research/topic-aware-compaction/06_outputs/setup_ab_test.py

Then start the servers in separate terminals:
  cd test-baseline && OPENCODE_SERVER_PASSWORD=test opencode serve --port 3100
  cd test-plugin   && OPENCODE_SERVER_PASSWORD=test opencode serve --port 3200

Then run the test:
  uv run research/topic-aware-compaction/06_outputs/ab_test_harness.py
"""

from __future__ import annotations

import json
import os
import shutil
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
PLUGIN_SOURCE = REPO_ROOT / ".opencode" / "plugin" / "fish-trail-compaction.ts"

# Where to create test directories
TEST_BASELINE = REPO_ROOT / "test-baseline"
TEST_PLUGIN = REPO_ROOT / "test-plugin"

# ---------------------------------------------------------------------------
# Synthetic fish-trail data matching test harness conversation topics
# ---------------------------------------------------------------------------

TOPIC_REGISTRY = {
    "version": 1,
    "active_topic": "topic_ab_python",
    "topics": {
        "topic_ab_python": {
            "title": "Python project setup",
            "status": "active",
            "created_at": "2026-05-10T00:00:00+00:00",
            "updated_at": "2026-05-10T00:00:00+00:00",
        },
        "topic_ab_database": {
            "title": "Database schema design",
            "status": "active",
            "created_at": "2026-05-10T00:00:00+00:00",
            "updated_at": "2026-05-10T00:00:00+00:00",
        },
        "topic_ab_cicd": {
            "title": "CI/CD pipeline setup",
            "status": "active",
            "created_at": "2026-05-10T00:00:00+00:00",
            "updated_at": "2026-05-10T00:00:00+00:00",
        },
    },
    "links": [],
}

TOPIC_FILES = {
    "topic_ab_python": {
        "id": "topic_ab_python",
        "title": "Python project setup",
        "scope": "Set up a new Python project 'data-pipeline' with uv, src layout, pytest, CLI",
        "status": "active",
        "parent": None,
        "summary": "",
        "created_at": "2026-05-10T00:00:00+00:00",
        "updated_at": "2026-05-10T00:00:00+00:00",
        "tags": ["python", "uv", "project-setup"],
        "metadata": {},
    },
    "topic_ab_database": {
        "id": "topic_ab_database",
        "title": "Database schema design",
        "scope": "Design PostgreSQL schema for multi-tenant SaaS with audit logging and RLS",
        "status": "active",
        "parent": None,
        "summary": "",
        "created_at": "2026-05-10T00:00:00+00:00",
        "updated_at": "2026-05-10T00:00:00+00:00",
        "tags": ["postgresql", "multi-tenant", "schema"],
        "metadata": {},
    },
    "topic_ab_cicd": {
        "id": "topic_ab_cicd",
        "title": "CI/CD pipeline setup",
        "scope": "Create GitHub Actions CI/CD for data-pipeline: lint, test, build, deploy to K8s",
        "status": "active",
        "parent": None,
        "summary": "",
        "created_at": "2026-05-10T00:00:00+00:00",
        "updated_at": "2026-05-10T00:00:00+00:00",
        "tags": ["github-actions", "cicd", "kubernetes"],
        "metadata": {},
    },
}

FISH_TRAIL_CONFIG = """companion_gateway:
  debug: false
"""

# Minimal opencode.json — low context limit to trigger compaction quickly
OPENCODE_JSON = {
    "provider": "anthropic",
}


def setup_directory(target: Path, *, with_plugin: bool) -> None:
    """Create a test directory with OpenCode config and fish-trail data."""
    label = "plugin" if with_plugin else "baseline"
    print(f"Setting up {label} directory: {target}")

    # Clean and create
    if target.exists():
        shutil.rmtree(target)
    target.mkdir(parents=True)

    # .opencode/ directory (required for OpenCode to recognize the project)
    opencode_dir = target / ".opencode"
    opencode_dir.mkdir()

    # opencode.json
    (target / "opencode.json").write_text(
        json.dumps(OPENCODE_JSON, indent=2), encoding="utf-8"
    )

    # Plugin (only for plugin variant)
    if with_plugin:
        plugin_dir = opencode_dir / "plugin"
        plugin_dir.mkdir()
        if PLUGIN_SOURCE.exists():
            shutil.copy2(PLUGIN_SOURCE, plugin_dir / "fish-trail-compaction.ts")
            print(f"  ✓ Copied plugin from {PLUGIN_SOURCE}")
        else:
            print(f"  ✗ Plugin source not found: {PLUGIN_SOURCE}")
            return

    # .petfish/fish-trail/ data
    fish_trail_dir = target / ".petfish" / "fish-trail"
    topics_dir = fish_trail_dir / "topics"
    contexts_dir = fish_trail_dir / "contexts"
    sessions_dir = fish_trail_dir / "sessions"
    decisions_dir = fish_trail_dir / "decisions"

    for d in [topics_dir, contexts_dir, sessions_dir, decisions_dir]:
        d.mkdir(parents=True)

    # Topic registry
    (fish_trail_dir / "topic-registry.json").write_text(
        json.dumps(TOPIC_REGISTRY, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    # Topic data files
    for topic_id, data in TOPIC_FILES.items():
        (topics_dir / f"{topic_id}.json").write_text(
            json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8"
        )

    # Config
    (fish_trail_dir / "config.yaml").write_text(FISH_TRAIL_CONFIG, encoding="utf-8")

    # Git init (OpenCode may need a git repo)
    os.system(
        f'cd /d "{target}" && git init -q && git add -A && git commit -q -m "init" --allow-empty'
    )

    file_count = sum(1 for _ in target.rglob("*") if _.is_file())
    print(f"  ✓ Created {file_count} files")


def main() -> None:
    print("=" * 60)
    print("  A/B Test Environment Setup")
    print("=" * 60)
    print(f"Repo root: {REPO_ROOT}")
    print()

    setup_directory(TEST_BASELINE, with_plugin=False)
    print()
    setup_directory(TEST_PLUGIN, with_plugin=True)

    print()
    print("=" * 60)
    print("  Setup complete!")
    print("=" * 60)
    print()
    print("Next steps:")
    print()
    print("1. Start baseline server (Terminal 1):")
    print(f'   cd "{TEST_BASELINE}"')
    print("   $env:OPENCODE_SERVER_PASSWORD='test'; opencode serve --port 3100")
    print()
    print("2. Start plugin server (Terminal 2):")
    print(f'   cd "{TEST_PLUGIN}"')
    print("   $env:OPENCODE_SERVER_PASSWORD='test'; opencode serve --port 3200")
    print()
    print("3. Run the test (Terminal 3):")
    print(f'   cd "{REPO_ROOT}"')
    print("   uv run research/topic-aware-compaction/06_outputs/ab_test_harness.py")
    print()
    print("4. Cleanup after test:")
    print(f'   Remove-Item -Recurse -Force "{TEST_BASELINE}", "{TEST_PLUGIN}"')


if __name__ == "__main__":
    main()
