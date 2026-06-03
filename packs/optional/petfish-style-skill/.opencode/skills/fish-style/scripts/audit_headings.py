#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = []
# ///

"""Audit heading format in Markdown files.

Enumerate-first-fix-second-verify-remaining workflow:
  1. Run audit -> list all heading variants
  2. Run with --fix -> fix issues in place
  3. Run audit again -> confirm zero remaining

Usage:
  uv run scripts/audit_headings.py --files *.md
  uv run scripts/audit_headings.py --files *.md --fix
  uv run scripts/audit_headings.py --files *.md --json report.json
"""

from __future__ import annotations

import argparse
import glob
import json
import re
import sys
from pathlib import Path

CJK = r"\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff"
ORDINAL_SUFFIXES = r"(?:节|部分|章|篇|模块|单元)"
ORDINAL_CHARS = r"[一二三四五六七八九十百零]+"


def classify_heading(line: str) -> str:
    """Classify a heading line into a category."""
    stripped = line.strip()
    if not stripped.startswith("#"):
        return ""
    level = len(stripped) - len(stripped.lstrip("#"))
    if level < 2 or level > 4:
        return ""

    # Fullwidth space
    if "\u3000" in stripped:
        return "fullwidth_space"

    # Section number + Chinese/paren without space
    if re.search(r"\d+(?:\.\d+)+[\u4e00-\u9fff(（]", stripped):
        return "number_cn_no_space"

    # Chinese ordinal + text without space
    if re.search(
        rf"第{ORDINAL_CHARS}{ORDINAL_SUFFIXES}[\u4e00-\u9fffA-Za-z0-9(（]", stripped
    ):
        return "ordinal_cn_no_space"

    return "ok"


def fix_heading(line: str) -> str:
    """Apply heading fixes to a single line."""

    # Fix: section number + Chinese/paren without space
    line = re.sub(
        rf"^(#{{2,4}}\s+\d+(?:\.\d+)+)([\u4e00-\u9fff(（])",
        r"\1 \2",
        line,
        flags=re.MULTILINE,
    )

    # Fix: Chinese ordinal + text without space
    line = re.sub(
        rf"^(#{{2,4}}\s+(?:第{ORDINAL_CHARS}{ORDINAL_SUFFIXES}))([\u4e00-\u9fffA-Za-z0-9(（])",
        r"\1 \2",
        line,
        flags=re.MULTILINE,
    )

    # Fix: fullwidth space -> halfwidth in headings
    def replace_fullwidth(match: re.Match) -> str:
        return match.group(0).replace("\u3000", " ")

    line = re.sub(r"^#{1,6}\s+.*", replace_fullwidth, line, flags=re.MULTILINE)
    return line


def scan_file(filepath: str) -> dict:
    """Scan one file and return heading classification results."""
    text = Path(filepath).read_text(encoding="utf-8")
    results: dict[str, list[str]] = {
        "number_cn_no_space": [],
        "ordinal_cn_no_space": [],
        "fullwidth_space": [],
        "ok": [],
    }

    for i, line in enumerate(text.split("\n"), 1):
        stripped = line.strip()
        if not stripped.startswith("#"):
            continue
        level = len(stripped) - len(stripped.lstrip("#"))
        if level < 2 or level > 4:
            continue

        cat = classify_heading(stripped)
        if cat:
            results[cat].append(f"L{i}: {stripped[:80]}")

    return results


def fix_file(filepath: str) -> int:
    """Fix heading issues in a file. Returns number of lines changed."""
    text = Path(filepath).read_text(encoding="utf-8")
    lines = text.split("\n")
    changed = 0
    new_lines = []

    for line in lines:
        stripped = line.strip()
        if not stripped.startswith("#"):
            new_lines.append(line)
            continue
        level = len(stripped) - len(stripped.lstrip("#"))
        if level < 2 or level > 4:
            new_lines.append(line)
            continue

        fixed = fix_heading(line)
        if fixed != line:
            changed += 1
        new_lines.append(fixed)

    if changed > 0:
        Path(filepath).write_text("\n".join(new_lines), encoding="utf-8")

    return changed


def print_report(file_results: dict[str, dict]) -> None:
    """Print human-readable summary."""
    total_issues = 0

    for filepath, results in file_results.items():
        issues = sum(
            len(v) for k, v in results.items() if k != "ok"
        )
        if issues == 0:
            print(f"\n{filepath}: OK (all headings formatted correctly)")
            continue

        total_issues += issues
        print(f"\n{filepath}: {issues} issue(s)")
        for cat in ("number_cn_no_space", "ordinal_cn_no_space", "fullwidth_space"):
            items = results[cat]
            if items:
                label = cat.replace("_", " ").title()
                print(f"  {label} ({len(items)}):")
                for item in items[:5]:
                    print(f"    {item}")
                if len(items) > 5:
                    print(f"    ... and {len(items) - 5} more")

    print(f"\n--- Total: {total_issues} issue(s) across {len(file_results)} file(s) ---")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Audit heading format in Markdown files."
    )
    parser.add_argument(
        "--files",
        nargs="+",
        required=True,
        help="File paths or glob patterns to scan",
    )
    parser.add_argument(
        "--fix",
        action="store_true",
        help="Fix issues in place",
    )
    parser.add_argument(
        "--json",
        metavar="OUTPUT",
        help="Write structured JSON report to file",
    )
    args = parser.parse_args()

    # Expand glob patterns
    all_files: list[str] = []
    for pattern in args.files:
        matches = glob.glob(pattern, recursive=True)
        if matches:
            all_files.extend(matches)
        else:
            all_files.append(pattern)

    # Deduplicate while preserving order
    seen = set()
    unique_files: list[str] = []
    for f in all_files:
        if f not in seen:
            seen.add(f)
            unique_files.append(f)

    if args.fix:
        total_fixed = 0
        for filepath in unique_files:
            if not Path(filepath).exists():
                print(f"SKIP: {filepath} not found", file=sys.stderr)
                continue
            n = fix_file(filepath)
            if n > 0:
                print(f"FIXED: {filepath} ({n} heading(s))")
            total_fixed += n
        print(f"\n--- Fixed {total_fixed} heading(s) across {len(unique_files)} file(s) ---")

    # Always scan (after fix if --fix was passed)
    file_results: dict[str, dict] = {}
    for filepath in unique_files:
        if not Path(filepath).exists():
            continue
        file_results[filepath] = scan_file(filepath)

    if args.json:
        Path(args.json).write_text(
            json.dumps(file_results, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        print(f"JSON report written to {args.json}")

    print_report(file_results)

    total_issues = sum(
        sum(len(v) for k, v in r.items() if k != "ok")
        for r in file_results.values()
    )
    return 1 if total_issues > 0 else 0


if __name__ == "__main__":
    raise SystemExit(main())
