#!/usr/bin/env python3
"""Detect and optionally normalize terminology aliases in Markdown files."""
from __future__ import annotations

import argparse
import glob
import re
from pathlib import Path


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(encoding="utf-8-sig")


def parse_simple_termbase(path: Path) -> dict[str, list[str]]:
    """Parse the simple YAML termbase format without external dependencies."""
    text = read_text(path)
    terms: dict[str, list[str]] = {}
    current: str | None = None
    in_aliases = False
    for raw in text.splitlines():
        line = raw.rstrip()
        m = re.match(r"^\s{2}([^:#][^:]*):\s*$", line)
        if m:
            current = m.group(1).strip()
            terms.setdefault(current, [])
            in_aliases = False
            continue
        if current and re.match(r"^\s{4}aliases:\s*$", line):
            in_aliases = True
            continue
        if current and in_aliases:
            a = re.match(r"^\s{6}-\s+(.+?)\s*$", line)
            if a:
                alias = a.group(1).strip().strip('"\'')
                terms[current].append(alias)
            elif line and not line.startswith("      "):
                in_aliases = False
    return terms


def expand_targets(patterns: list[str]) -> list[Path]:
    files: list[Path] = []
    for pattern in patterns:
        matched = glob.glob(pattern, recursive=True)
        if matched:
            files.extend(Path(p) for p in matched if Path(p).is_file() and Path(p).suffix.lower() == ".md")
        else:
            p = Path(pattern)
            if p.is_dir():
                files.extend(sorted(p.rglob("*.md")))
            elif p.is_file() and p.suffix.lower() == ".md":
                files.append(p)
    return sorted(set(files))


def main() -> int:
    parser = argparse.ArgumentParser(description="Detect and optionally normalize terminology aliases.")
    parser.add_argument("--termbase", required=True, help="Path to termbase.yaml.")
    parser.add_argument("--targets", nargs="+", required=True, help="Target Markdown files, directories, or globs.")
    parser.add_argument("--output", required=True, help="Output report Markdown path.")
    parser.add_argument("--apply", action="store_true", help="Apply unambiguous replacements in place. Default is report-only.")
    args = parser.parse_args()

    terms = parse_simple_termbase(Path(args.termbase))
    files = expand_targets(args.targets)
    if not files:
        raise SystemExit("Error: no Markdown target files found.")

    lines = ["# Term Drift Report", "", f"Termbase: `{args.termbase}`", ""]
    changed_files = []
    for path in files:
        text = read_text(path)
        file_findings = []
        new_text = text
        for preferred, aliases in terms.items():
            for alias in aliases:
                if alias and alias in text:
                    count = text.count(alias)
                    file_findings.append((preferred, alias, count))
                    if args.apply:
                        new_text = new_text.replace(alias, preferred)
        if file_findings:
            lines.append(f"## `{path}`")
            lines.append("")
            for preferred, alias, count in file_findings:
                lines.append(f"- `{alias}` → `{preferred}`: {count} occurrence(s)")
            lines.append("")
        if args.apply and new_text != text:
            path.write_text(new_text, encoding="utf-8")
            changed_files.append(str(path))

    if not any(line.startswith("## `") for line in lines):
        lines.append("No alias drift detected.")
    if args.apply:
        lines.extend(["", "## Applied changes", ""])
        if changed_files:
            for f in changed_files:
                lines.append(f"- `{f}`")
        else:
            lines.append("No files changed.")

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote term drift report: {output}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
