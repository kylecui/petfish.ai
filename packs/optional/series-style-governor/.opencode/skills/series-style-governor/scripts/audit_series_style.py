#!/usr/bin/env python3
"""Audit Markdown files against a series style profile."""
from __future__ import annotations

import argparse
import glob
import json
import re
from pathlib import Path

HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
CJK_EN_SPACE_RE = re.compile(r"([\u4e00-\u9fff])[ \t]+([A-Za-z0-9])|([A-Za-z0-9])[ \t]+([\u4e00-\u9fff])")
CJK_EN_NOSPACE_RE = re.compile(r"[\u4e00-\u9fff][A-Za-z0-9]|[A-Za-z0-9][\u4e00-\u9fff]")

def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(encoding="utf-8-sig")


def load_profile(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


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


def detect_heading_numbering(headings: list[str]) -> str:
    if any(re.match(r"^第[一二三四五六七八九十0-9]+[章节篇]", h) for h in headings):
        return "chinese-chapter"
    if any(re.match(r"^\d+(\.\d+)*[\.、\s]", h) for h in headings):
        return "arabic-dot"
    return "none"


def audit_file(path: Path, profile: dict) -> dict:
    text = read_text(path)
    lines = text.splitlines()
    headings = []
    max_depth = 0
    for line in lines:
        m = HEADING_RE.match(line)
        if m:
            max_depth = max(max_depth, len(m.group(1)))
            headings.append(m.group(2).strip())

    issues = []
    expected_spacing = profile.get("language_profile", {}).get("cjk_english_spacing", "unknown")
    cjk_space = len(CJK_EN_SPACE_RE.findall(text))
    cjk_nospace = len(CJK_EN_NOSPACE_RE.findall(text))
    if expected_spacing == "no-space" and cjk_space:
        issues.append(("Chinese-English typography", "Warning", f"Found {cjk_space} CJK-English spaces; profile prefers no-space."))
    elif expected_spacing == "space" and cjk_nospace:
        issues.append(("Chinese-English typography", "Warning", f"Found {cjk_nospace} adjacent CJK-English pairs; profile prefers spaces."))

    expected_depth = profile.get("structure_profile", {}).get("max_heading_depth", 0)
    if expected_depth and max_depth > expected_depth:
        issues.append(("Structure", "Warning", f"Max heading depth {max_depth} exceeds baseline depth {expected_depth}."))

    expected_numbering = profile.get("structure_profile", {}).get("heading_numbering", "unknown")
    actual_numbering = detect_heading_numbering(headings)
    if expected_numbering not in ["unknown", actual_numbering] and headings:
        issues.append(("Structure", "Warning", f"Heading numbering is {actual_numbering}, baseline is {expected_numbering}."))

    summary_patterns = profile.get("structure_profile", {}).get("summary_section_pattern", [])
    if summary_patterns and not any(any(token in h for token in summary_patterns) for h in headings):
        issues.append(("Structure", "Warning", "Baseline has summary sections but this file has no matching summary heading."))

    preferred_terms = profile.get("terminology_profile", {}).get("preferred_terms", {})
    for preferred, spec in preferred_terms.items():
        aliases = spec.get("aliases", []) if isinstance(spec, dict) else []
        for alias in aliases:
            if alias and alias in text and preferred not in text:
                issues.append(("Terminology", "Warning", f"Alias `{alias}` appears but preferred term `{preferred}` does not."))

    forbidden_terms = profile.get("terminology_profile", {}).get("forbidden_terms", {})
    for term in forbidden_terms:
        if term in text:
            issues.append(("Terminology", "Review", f"Forbidden or discouraged term appears: `{term}`."))

    return {
        "path": str(path),
        "heading_count": len(headings),
        "max_heading_depth": max_depth,
        "heading_numbering": actual_numbering,
        "cjk_space_count": cjk_space,
        "cjk_nospace_count": cjk_nospace,
        "issues": issues,
    }


def status_for(results: list[dict], dimension: str) -> tuple[str, str]:
    count = sum(1 for r in results for i in r["issues"] if i[0] == dimension)
    if count == 0:
        return "Pass", "No major drift detected."
    if count <= 3:
        return "Warning", f"{count} issue(s) detected."
    return "Fail", f"{count} issue(s) detected across files."


def write_report(results: list[dict], profile: dict, output: Path) -> None:
    dims = ["Structure", "Terminology", "Naming", "Markdown layout", "Chinese-English typography", "Rewrite risk"]
    lines = [
        "# Series Style Audit Report",
        "",
        "## Executive summary",
        "",
        f"Audited {len(results)} Markdown file(s) against baseline `{profile.get('baseline', {}).get('path', '')}`.",
        "",
        "## Baseline",
        "",
        f"- Baseline file: `{profile.get('baseline', {}).get('path', '')}`",
        f"- Baseline mode: `{profile.get('baseline', {}).get('mode', '')}`",
        "",
        "## Overall findings",
        "",
        "| Dimension | Status | Notes |",
        "|---|---:|---|",
    ]
    for dim in dims:
        status, note = status_for(results, dim)
        lines.append(f"| {dim} | {status} | {note} |")
    lines.extend(["", "## File-level findings", ""])
    for r in results:
        lines.append(f"### `{r['path']}`")
        lines.append("")
        lines.append(f"- Heading count: {r['heading_count']}")
        lines.append(f"- Max heading depth: {r['max_heading_depth']}")
        lines.append(f"- Heading numbering: {r['heading_numbering']}")
        lines.append(f"- CJK-English spaces: {r['cjk_space_count']}")
        if not r["issues"]:
            lines.append("- Issues: none detected")
        else:
            lines.append("- Issues:")
            for dim, severity, msg in r["issues"]:
                lines.append(f"  - **{severity} / {dim}**: {msg}")
        lines.append("")
    lines.extend([
        "## Safe automatic fixes",
        "",
        "- CJK-English spacing normalization when profile is clear.",
        "- Heading/list/blank-line normalization when unambiguous.",
        "",
        "## Review-needed changes",
        "",
        "- Terminology replacements involving conceptual ambiguity.",
        "- Structural changes that move or delete content.",
        "",
        "## Blocked changes",
        "",
        "- Any change that may alter facts, claims, citations, or authorial stance.",
        "",
        "## Suggested style decisions",
        "",
        "- Confirm whether the baseline should remain fixed or evolve with later chapters.",
    ])
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit Markdown files against a series style profile.")
    parser.add_argument("--profile", required=True, help="Path to style-profile.json.")
    parser.add_argument("--targets", nargs="+", required=True, help="Target Markdown files, directories, or glob patterns.")
    parser.add_argument("--output", required=True, help="Output Markdown audit report.")
    args = parser.parse_args()

    profile = load_profile(Path(args.profile))
    files = expand_targets(args.targets)
    if not files:
        raise SystemExit("Error: no Markdown target files found.")
    results = [audit_file(p, profile) for p in files]
    write_report(results, profile, Path(args.output))
    print(f"Wrote audit report: {args.output}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
