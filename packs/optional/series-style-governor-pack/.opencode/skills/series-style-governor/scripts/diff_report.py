#!/usr/bin/env python3
"""Generate a Markdown unified diff report for original and rewritten files."""
from __future__ import annotations

import argparse
import difflib
from pathlib import Path


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(encoding="utf-8-sig")


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate a Markdown diff report between two directories or files.")
    parser.add_argument("--before", required=True, help="Original file or directory.")
    parser.add_argument("--after", required=True, help="Rewritten file or directory.")
    parser.add_argument("--output", required=True, help="Output Markdown report path.")
    args = parser.parse_args()

    before = Path(args.before)
    after = Path(args.after)
    pairs: list[tuple[Path, Path]] = []

    if before.is_file() and after.is_file():
        pairs.append((before, after))
    elif before.is_dir() and after.is_dir():
        for b in sorted(before.rglob("*.md")):
            a = after / b.name
            if a.exists():
                pairs.append((b, a))
    else:
        raise SystemExit("Error: before and after must both be files or both be directories.")

    lines = ["# Diff Report", ""]
    if not pairs:
        lines.append("No matching Markdown file pairs found.")
    for b, a in pairs:
        before_lines = read_text(b).splitlines(keepends=True)
        after_lines = read_text(a).splitlines(keepends=True)
        diff = list(difflib.unified_diff(before_lines, after_lines, fromfile=str(b), tofile=str(a)))
        lines.append(f"## `{b}` → `{a}`")
        lines.append("")
        if diff:
            lines.append("```diff")
            lines.extend(line.rstrip("\n") for line in diff[:400])
            if len(diff) > 400:
                lines.append("... diff truncated at 400 lines ...")
            lines.append("```")
        else:
            lines.append("No differences.")
        lines.append("")

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote diff report: {output}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
