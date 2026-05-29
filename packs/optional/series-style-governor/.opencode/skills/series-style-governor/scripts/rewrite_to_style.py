#!/usr/bin/env python3
"""Create conservative rewrite drafts using mechanical style rules.

This script intentionally performs only low-risk transformations. Semantic rewriting
should be done by the agent after reading rewrite boundaries.
"""
from __future__ import annotations

import argparse
import glob
import json
import re
from pathlib import Path

CJK_EN_SPACE_RE = re.compile(r"([\u4e00-\u9fff])[ \t]+([A-Za-z0-9])|([A-Za-z0-9])[ \t]+([\u4e00-\u9fff])")


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(encoding="utf-8-sig")


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


def remove_cjk_english_spaces(text: str) -> str:
    def repl(m: re.Match[str]) -> str:
        groups = m.groups()
        if groups[0] is not None:
            return groups[0] + groups[1]
        return groups[2] + groups[3]
    return CJK_EN_SPACE_RE.sub(repl, text)


def normalize_blank_lines(text: str) -> str:
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"([^\n])\n(#{1,6}\s)", r"\1\n\n\2", text)
    text = re.sub(r"(#{1,6}\s[^\n]+)\n([^\n#])", r"\1\n\n\2", text)
    return text


def main() -> int:
    parser = argparse.ArgumentParser(description="Create conservative rewrite drafts from Markdown files.")
    parser.add_argument("--profile", required=True, help="Path to style-profile.json.")
    parser.add_argument("--targets", nargs="+", required=True, help="Target Markdown files, directories, or globs.")
    parser.add_argument("--output-dir", required=True, help="Directory for rewritten Markdown files.")
    parser.add_argument("--mode", default="conservative", choices=["conservative"], help="Rewrite mode. Only conservative is supported.")
    args = parser.parse_args()

    profile = json.loads(Path(args.profile).read_text(encoding="utf-8"))
    spacing = profile.get("language_profile", {}).get("cjk_english_spacing", "unknown")
    files = expand_targets(args.targets)
    if not files:
        raise SystemExit("Error: no Markdown target files found.")

    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    report = ["# Conservative Rewrite Report", "", f"Profile: `{args.profile}`", ""]

    for path in files:
        text = read_text(path)
        new_text = text
        applied = []
        if spacing == "no-space":
            updated = remove_cjk_english_spaces(new_text)
            if updated != new_text:
                new_text = updated
                applied.append("normalized CJK-English spacing to no-space")
        new_text2 = normalize_blank_lines(new_text)
        if new_text2 != new_text:
            new_text = new_text2
            applied.append("normalized excessive blank lines and heading spacing")

        dest = out_dir / path.name
        dest.write_text(new_text, encoding="utf-8")
        report.append(f"## `{path}`")
        report.append("")
        report.append(f"- Output: `{dest}`")
        if applied:
            for item in applied:
                report.append(f"- Applied: {item}")
        else:
            report.append("- Applied: no mechanical changes")
        report.append("- Review-needed: semantic style rewriting, if desired, should be performed by the agent after preserving facts and citations.")
        report.append("")

    (out_dir / "rewrite-report.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    print(f"Wrote conservative rewrite drafts to: {out_dir}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
