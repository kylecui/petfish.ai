#!/usr/bin/env python3
"""Create a standard course project tree."""

import argparse
import json
from pathlib import Path

FULL_DIRS = [
    ".opencode/skills",
    "docs/00-project",
    "docs/01-outline",
    "docs/02-content",
    "docs/03-labs",
    "docs/04-learner-pack",
    "docs/05-instructor-pack",
    "docs/06-qa",
    "docs/07-qc",
    "assets/drawio",
    "assets/images",
    "assets/tables",
    "references/external",
    "references/internal",
    "release",
    "archive",
]

MINIMAL_DIRS = [
    ".opencode/skills",
    "docs/00-project",
    "docs/01-outline",
    "docs/02-content",
    "docs/03-labs",
    "release",
]

PLACEHOLDERS = {
    "docs/00-project/project-brief.md": "# Project Brief\n",
    "docs/00-project/milestone-plan.md": "# Milestone Plan\n",
    "docs/01-outline/course-overview.md": "# Course Overview\n",
    "docs/01-outline/syllabus.md": "# Syllabus\n",
    "docs/02-content/01-introduction.md": "# Lesson 01\n",
    "docs/03-labs/environment-notes.md": "# Lab Environment Notes\n",
}

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create a standard course project directory tree.",
    )
    parser.add_argument("--root", required=True, help="Target project root directory.")
    parser.add_argument(
        "--mode",
        choices=["minimal", "full"],
        default="full",
        help="Scaffold size to create.",
    )
    parser.add_argument(
        "--with-placeholders",
        action="store_true",
        help="Create starter markdown files.",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing placeholder files when present.",
    )
    parser.add_argument(
        "--emit",
        choices=["json", "text"],
        default="json",
        help="Output format for the creation summary.",
    )
    return parser.parse_args()

def main() -> int:
    args = parse_args()
    root = Path(args.root).expanduser().resolve()
    root.mkdir(parents=True, exist_ok=True)

    dirs = FULL_DIRS if args.mode == "full" else MINIMAL_DIRS
    created_dirs = []
    created_files = []
    skipped_files = []

    for rel in dirs:
        target = root / rel
        if not target.exists():
            target.mkdir(parents=True, exist_ok=True)
            created_dirs.append(rel)

    if args.with_placeholders:
        for rel, content in PLACEHOLDERS.items():
            file_path = root / rel
            file_path.parent.mkdir(parents=True, exist_ok=True)
            if file_path.exists() and not args.overwrite:
                skipped_files.append(rel)
                continue
            file_path.write_text(content, encoding="utf-8")
            created_files.append(rel)

    payload = {
        "root": str(root),
        "mode": args.mode,
        "created_dirs": created_dirs,
        "created_files": created_files,
        "skipped_files": skipped_files,
    }

    if args.emit == "json":
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(f"root: {root}")
        print(f"mode: {args.mode}")
        print("created dirs:")
        for item in created_dirs:
            print(f"  - {item}")
        print("created files:")
        for item in created_files:
            print(f"  - {item}")
        if skipped_files:
            print("skipped files:")
            for item in skipped_files:
                print(f"  - {item}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
