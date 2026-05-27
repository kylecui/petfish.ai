#!/usr/bin/env python3
"""Initialize a research workspace directory tree."""

from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path


RESEARCH_TYPES = ("scientific", "product", "planning", "mixed")

# Category aliases group multiple domains under broader labels.
# The mapped value is the workspace --type used for directory scaffolding.
CATEGORY_ALIASES: dict[str, str] = {
    "academic": "scientific",
    "business": "product",
    "experiential": "planning",
    # Direct types pass through unchanged.
    "scientific": "scientific",
    "product": "product",
    "planning": "planning",
    "mixed": "mixed",
    "custom": "mixed",
}

# Which research domains each category covers (for CONTEXT.md).
CATEGORY_DOMAINS: dict[str, list[str]] = {
    "academic": ["scientific"],
    "business": ["product", "decision", "risk-procurement"],
    "planning": ["planning", "learning"],
    "experiential": ["experience-event", "adapters"],
    "mixed": [
        "scientific",
        "product",
        "planning",
        "learning",
        "decision",
        "risk-procurement",
        "experience-event",
        "adapters",
    ],
    "custom": [],  # filled at runtime from --domains
}

ALL_DOMAINS = [
    "scientific",
    "product",
    "planning",
    "learning",
    "decision",
    "risk-procurement",
    "experience-event",
    "adapters",
]


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
    valid_types = list(RESEARCH_TYPES) + [
        k for k in CATEGORY_ALIASES if k not in RESEARCH_TYPES
    ]
    parser.add_argument(
        "--type",
        required=True,
        choices=valid_types,
        dest="rtype",
        help="Research type or category alias.",
    )
    parser.add_argument("--name", required=True, help="Project name.")
    parser.add_argument("--path", required=True, help="Target workspace root path.")
    parser.add_argument(
        "--domains",
        nargs="*",
        default=None,
        help="Specific domains for custom category (e.g. scientific product decision).",
    )
    args = parser.parse_args()

    # Resolve category alias to workspace type.
    args.category = args.rtype
    args.rtype = CATEGORY_ALIASES.get(args.rtype, args.rtype)

    # Resolve active domains.
    if args.category == "custom" and args.domains:
        invalid = [d for d in args.domains if d not in ALL_DOMAINS]
        if invalid:
            parser.error(
                f"Unknown domains: {', '.join(invalid)}. Valid: {', '.join(ALL_DOMAINS)}"
            )
        args.active_domains = args.domains
    elif args.category in CATEGORY_DOMAINS:
        args.active_domains = CATEGORY_DOMAINS[args.category]
    else:
        args.active_domains = CATEGORY_DOMAINS.get("mixed", ALL_DOMAINS)

    return args


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

    domains_lines = "\n".join(f"  - {d}" for d in args.active_domains)
    context_content = (
        f"# Research Context\n\n"
        f"## Project\n\n"
        f"- **Name**: {args.name}\n"
        f"- **Category**: {args.category}\n"
        f"- **Workspace Type**: {args.rtype}\n"
        f"- **Created**: {date.today().isoformat()}\n\n"
        f"## Active Domains\n\n"
        f"{domains_lines}\n\n"
        f"Agents should prioritize skill chains from these domains. "
        f"Other domains remain available but are not the primary focus.\n\n"
        f"## Purpose\n\n"
        f"<!-- Why this research exists. What question are we answering? -->\n\n"
        f"## Scope\n\n"
        f"<!-- What is in scope and out of scope. -->\n\n"
        f"## Key Decisions\n\n"
        f"<!-- Record important decisions and their rationale here. -->\n"
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
        "category": args.category,
        "workspace_type": args.rtype,
        "active_domains": args.active_domains,
        "directories_created": directories_created,
        "files_created": files_created,
    }
    print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
