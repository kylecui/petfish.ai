#!/usr/bin/env python3
"""Extract a lightweight style profile from a Markdown baseline file."""
from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from datetime import date
from pathlib import Path

HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
CJK_EN_SPACE_RE = re.compile(r"[\u4e00-\u9fff][ \t]+[A-Za-z0-9]|[A-Za-z0-9][ \t]+[\u4e00-\u9fff]")
CJK_EN_NOSPACE_RE = re.compile(r"[\u4e00-\u9fff][A-Za-z0-9]|[A-Za-z0-9][\u4e00-\u9fff]")
TERM_RE = re.compile(r"[A-Za-z][A-Za-z0-9_+/#.-]{1,}|[\u4e00-\u9fff]{2,12}")
FIGURE_RE = re.compile(r"^\s*(图\s*\d+|Figure\s+\d+)[\.:：、]?\s*(.*)$", re.I)
TABLE_RE = re.compile(r"^\s*(表\s*\d+|Table\s+\d+)[\.:：、]?\s*(.*)$", re.I)


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(encoding="utf-8-sig")


def detect_heading_numbering(headings: list[str]) -> str:
    numbered = 0
    chinese_numbered = 0
    for h in headings:
        if re.match(r"^\d+(\.\d+)*[\.、\s]", h):
            numbered += 1
        if re.match(r"^第[一二三四五六七八九十0-9]+[章节篇]", h):
            chinese_numbered += 1
    if chinese_numbered:
        return "chinese-chapter"
    if numbered:
        return "arabic-dot"
    return "none"


def infer_tone(text: str) -> list[str]:
    tone = []
    if any(w in text for w in ["研究", "文献", "模型", "方法", "实验", "参考文献"]):
        tone.append("academic-technical")
    if any(w in text for w in ["建议", "方案", "路径", "实施", "治理"]):
        tone.append("consulting-analytical")
    if any(w in text for w in ["课程", "学习", "实践", "小结", "本章"]):
        tone.append("course-material")
    if not tone:
        tone.append("general-longform")
    return tone


def main() -> int:
    parser = argparse.ArgumentParser(description="Extract a style profile from a Markdown baseline file.")
    parser.add_argument("--baseline", required=True, help="Path to the baseline Markdown file.")
    parser.add_argument("--output", required=True, help="Output path for style-profile.json.")
    parser.add_argument("--mode", default="fixed", choices=["fixed", "first-file", "evolving"], help="Baseline mode.")
    args = parser.parse_args()

    baseline = Path(args.baseline)
    if not baseline.exists():
        raise SystemExit(f"Error: baseline file not found: {baseline}")

    text = read_text(baseline)
    lines = text.splitlines()

    headings_by_level: dict[str, list[str]] = {}
    heading_titles = []
    for line in lines:
        m = HEADING_RE.match(line)
        if m:
            level = str(len(m.group(1)))
            title = m.group(2).strip()
            headings_by_level.setdefault(level, []).append(title)
            heading_titles.append(title)

    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip() and not p.lstrip().startswith("#")]
    para_lengths = [len(p) for p in paragraphs]
    avg_para_len = round(sum(para_lengths) / len(para_lengths), 1) if para_lengths else 0

    cjk_space_count = len(CJK_EN_SPACE_RE.findall(text))
    cjk_nospace_count = len(CJK_EN_NOSPACE_RE.findall(text))
    if cjk_space_count > cjk_nospace_count:
        spacing = "space"
    elif cjk_nospace_count > 0:
        spacing = "no-space"
    else:
        spacing = "unknown"

    list_markers = Counter()
    for line in lines:
        if re.match(r"^\s*-\s+", line):
            list_markers["-"] += 1
        elif re.match(r"^\s*\*\s+", line):
            list_markers["*"] += 1
        elif re.match(r"^\s*\+\s+", line):
            list_markers["+"] += 1
    list_marker = list_markers.most_common(1)[0][0] if list_markers else "-"

    term_counts = Counter(t for t in TERM_RE.findall(text) if len(t) >= 2)
    common_terms = [term for term, _ in term_counts.most_common(80)]

    summary_patterns = [h for h in heading_titles if any(k in h for k in ["小结", "总结", "结语", "展望"])]
    figure_pattern = "图 N. 标题" if any(FIGURE_RE.match(l) for l in lines) else "unknown"
    table_pattern = "表 N. 标题" if any(TABLE_RE.match(l) for l in lines) else "unknown"

    profile = {
        "profile_version": "0.1.0",
        "baseline": {
            "path": str(baseline),
            "mode": args.mode,
            "created_at": date.today().isoformat(),
        },
        "language_profile": {
            "primary_language": "zh-CN" if re.search(r"[\u4e00-\u9fff]", text) else "en",
            "secondary_language": "en" if re.search(r"[A-Za-z]", text) else "none",
            "tone": infer_tone(text),
            "cjk_english_spacing": spacing,
            "punctuation": "zh-full-width-for-chinese",
            "preferred_sentence_density": "medium" if avg_para_len < 500 else "dense",
            "average_paragraph_length_chars": avg_para_len,
        },
        "structure_profile": {
            "heading_numbering": detect_heading_numbering(heading_titles),
            "max_heading_depth": max([int(k) for k in headings_by_level.keys()], default=0),
            "heading_counts": {k: len(v) for k, v in headings_by_level.items()},
            "intro_required": any("引言" in h or "Introduction" in h for h in heading_titles),
            "summary_section_pattern": summary_patterns,
            "common_section_sequence": heading_titles[:12],
            "figure_caption_pattern": figure_pattern,
            "table_caption_pattern": table_pattern,
        },
        "terminology_profile": {
            "candidate_terms": common_terms,
            "preferred_terms": {},
            "forbidden_terms": {},
            "abbreviation_rules": {
                "first_use": "中文全称（English Full Name, ACRONYM）",
                "later_use": "follow-baseline",
            },
        },
        "markdown_layout_profile": {
            "blank_line_after_heading": True,
            "blank_line_before_heading": True,
            "list_marker": list_marker,
            "ordered_list_marker": "1.",
            "code_fence_style": "triple-backtick-with-language-when-known",
            "table_alignment": "github-flavored-markdown",
            "image_syntax": "markdown-image",
        },
        "rewrite_policy": {
            "default_mode": "conservative",
            "preserve_citations": True,
            "preserve_claims": True,
            "preserve_examples": True,
            "auto_fix_allowed": [
                "heading-numbering",
                "term-alias-unambiguous",
                "cjk-english-spacing",
                "blank-lines",
                "list-marker",
            ],
            "review_required": [
                "paragraph-move",
                "definition-rewrite",
                "claim-emphasis-change",
            ],
        },
    }

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(profile, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote style profile: {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
