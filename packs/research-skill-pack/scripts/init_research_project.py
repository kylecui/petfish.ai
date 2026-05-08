#!/usr/bin/env python3
"""Initialize a research workspace directory tree."""

from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path


RESEARCH_TYPES = ("scientific", "product", "planning", "mixed")


def md_title_from_filename(file_path: Path) -> str:
    stem = file_path.stem.replace("-", " ").replace("_", " ").strip()
    return stem.title() if stem else "Untitled"


def write_if_missing(path: Path, content: str) -> bool:
    if path.exists():
        return False
    path.write_text(content, encoding="utf-8")
    return True


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Initialize a standard research workspace tree."
    )
    parser.add_argument("--type", required=True, choices=RESEARCH_TYPES, dest="rtype")
    parser.add_argument("--name", required=True, help="Project name.")
    parser.add_argument("--path", required=True, help="Target workspace root path.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = Path(args.path).expanduser()

    directories = [
        root / "00_brief",
        root / "01_sources",
        root / "01_sources" / "source-notes",
        root / "02_notes",
        root / "02_notes" / "reading-notes",
        root / "03_evidence",
        root / "04_methods",
        root / "05_analysis",
        root / "06_outputs",
        root / "07_reviews",
        root / "adr",
    ]

    files = [
        root / "CONTEXT.md",
        root / "00_brief" / "research-brief.md",
        root / "00_brief" / "research-questions.md",
        root / "00_brief" / "scope-boundaries.md",
        root / "01_sources" / "source-index.jsonl",
        root / "01_sources" / "bibliography.bib",
        root / "01_sources" / "literature-access.json",
        root / "01_sources" / "access-attempts.jsonl",
        root / "02_notes" / "excerpt-notes.jsonl",
        root / "02_notes" / "insight-log.jsonl",
        root / "02_notes" / "idea-inbox.md",
        root / "02_notes" / "quote-bank.md",
        root / "03_evidence" / "evidence-ledger.jsonl",
        root / "03_evidence" / "claim-map.md",
        root / "03_evidence" / "contradiction-log.md",
        root / "03_evidence" / "uncertainty-log.md",
        root / "04_methods" / "research-design.md",
        root / "05_analysis" / "synthesis-matrix.md",
        root / "06_outputs" / "report.md",
        root / "06_outputs" / "executive-summary.md",
        root / "07_reviews" / "quality-review.md",
    ]

    directories_created = 0
    files_created = 0

    if not root.exists():
        root.mkdir(parents=True, exist_ok=True)
        directories_created += 1

    for d in directories:
        if not d.exists():
            d.mkdir(parents=True, exist_ok=True)
            directories_created += 1

    context_content = (
        f"# Context\n\n"
        f"- Project Name: {args.name}\n"
        f"- Research Type: {args.rtype}\n"
        f"- Created At: {date.today().isoformat()}\n"
    )
    if write_if_missing(root / "CONTEXT.md", context_content):
        files_created += 1

    for file_path in files:
        if file_path.name == "CONTEXT.md":
            continue
        if file_path.suffix in {".jsonl", ".bib"}:
            if write_if_missing(file_path, ""):
                files_created += 1
        elif file_path.name == "literature-access.json":
            payload = {"version": "1.0", "free_first": True, "providers": []}
            if write_if_missing(
                file_path, json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
            ):
                files_created += 1
        elif file_path.suffix == ".md":
            title = md_title_from_filename(file_path)
            if write_if_missing(file_path, f"# {title}\n"):
                files_created += 1
        else:
            if write_if_missing(file_path, ""):
                files_created += 1

    result = {
        "status": "ok",
        "path": str(root.resolve()),
        "directories_created": directories_created,
        "files_created": files_created,
    }
    print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
