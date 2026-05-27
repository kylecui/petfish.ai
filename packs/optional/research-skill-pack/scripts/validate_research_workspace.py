#!/usr/bin/env python3
"""Audit a research workspace for required structure and files."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


REQUIRED_DIRS = [
    "00_brief",
    "01_sources",
    "02_notes",
    "03_evidence",
    "04_methods",
    "05_analysis",
    "06_outputs",
    "07_reviews",
    "adr",
]

REQUIRED_FILES = [
    "CONTEXT.md",
    "00_brief/research-brief.md",
    "01_sources/source-index.jsonl",
    "02_notes/excerpt-notes.jsonl",
    "02_notes/insight-log.jsonl",
    "03_evidence/evidence-ledger.jsonl",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate required directories/files in a research workspace."
    )
    parser.add_argument("--root", required=True, help="Workspace root directory.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = Path(args.root).expanduser()

    missing_dirs = [d for d in REQUIRED_DIRS if not (root / d).is_dir()]
    missing_files = [f for f in REQUIRED_FILES if not (root / f).is_file()]
    warnings: list[str] = []

    if not root.exists():
        warnings.append("Root path does not exist.")
    elif not root.is_dir():
        warnings.append("Root path exists but is not a directory.")

    status = "pass" if not missing_dirs and not missing_files else "fail"
    output = {
        "status": status,
        "missing_dirs": missing_dirs,
        "missing_files": missing_files,
        "warnings": warnings,
    }
    print(json.dumps(output, ensure_ascii=False))
    return 0 if status == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
