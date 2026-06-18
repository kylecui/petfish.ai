#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = []
# ///
"""Check text against Petfish-style writing rules.

Usage:
  uv run scripts/style_check.py --text "..."
  uv run scripts/style_check.py --file draft.md
"""

from __future__ import annotations

import argparse
import json
import re
import statistics
from pathlib import Path

CJK = r"\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff"
EN_TOKEN = r"[A-Za-z][A-Za-z0-9_.*+-]*"
BT_TOKEN = r"`[^`]+`"

AI_FLAVOR_PATTERNS = [
    # From V3
    "在当今",
    "高度复杂",
    "全面赋能",
    "能力闭环",
    "普惠",
    "拔高",
    "民主化",
    "极限",
    "银弹式",
    "立体认知",
    "多维协同",
    "重塑",
    "塑造",
    "从看得懂到管得住",
    # From petfish BUZZWORDS (deduplicated)
    "赋能",
    "银弹",
    "能力放大器",
    "蜂群式",
    "语不惊人死不休",
    "打造",
    "抓手",
    "质的飞跃",
    "全面升级",
    "颠覆式",
    # From petfish AI_OPENINGS (deduplicated)
    "随着技术的不断发展",
    "日益严峻",
    "不可忽视",
    "新时代背景下",
    # From petfish WEAK_CLAIMS
    "具有重要意义",
    "具有重大意义",
    "极大提升",
    "全面提升",
    "完整闭环",
    "全链路闭环",
    # V5 — Chinese AI-slop expansion (issue #24)
    # Empty summary phrases
    "综上所述",
    "总而言之",
    "众所周知",
    "不言而喻",
    "毋庸置疑",
    # Rhetorical filler idioms
    "瞬息万变",
    "日新月异",
    "翻天覆地",
    "前所未有",
    "史无前例",
    "方兴未艾",
    # Slogan-style phrases
    "与时俱进",
    "拥抱变化",
    "拥抱未来",
    "引领未来",
    "面向未来",
    "开创未来",
    "开创美好未来",
    # Empty positive action phrases
    "迎接挑战",
    "抓住机遇",
    "乘风破浪",
    "砥砺前行",
    "勇毅前行",
    "奋楫笃行",
    "踔厉奋发",
    # Corporate/AI grandstanding
    "使命",
    "担当",
    "深耕",
    "赋能",
    "携手共创",
    "共同打造",
    "助力",
    "加持",
    "底座",
    "护城河",
    "生态",
    "布局",
    "落地",
    "闭环",
    "链路",
    "矩阵",
    "沉淀",
    "对齐",
    "拉通",
    "透传",
    "打通",
]

EN_AI_HIGH_FREQ_WORDS = [
    "delve",
    "nuanced",
    "robust",
    "seamless",
    "leverage",
    "transformative",
    "foster",
    "encompass",
    "utilize",
    "multifaceted",
    "holistic",
    "synergy",
    "paradigm",
    "empower",
    "harness",
    "pivotal",
    "cutting-edge",
    "game-changer",
    "revolutionize",
    "unlock",
]

LOGICAL_CONNECTORS = [
    # V3 connectors
    "因此",
    "另一方面",
    "具体来说",
    "综上所述",
    "从这个角度看",
    "这意味着",
    "有必要",
    # petfish English connectors
    "However",
    "Therefore",
    "More specifically",
    "From this perspective",
]

_LAST_EXTRA_ISSUES: dict[str, list[str]] = {}


def split_sentences(text: str) -> list[str]:
    parts = re.split(r"(?<=[。！？.!?])\s*", text)
    return [p.strip() for p in parts if p.strip()]


def _is_code_or_heading(line: str) -> bool:
    """Return True for lines that should be skipped in spacing checks."""
    stripped = line.strip()
    return stripped.startswith("```") or line.startswith("    ")


def _iter_non_code_lines(text: str):
    in_code_block = False

    for line in text.split("\n"):
        stripped = line.strip()
        if stripped.startswith("```"):
            in_code_block = not in_code_block
            continue
        if in_code_block:
            continue
        yield line


def find_zh_en_spacing_issues(text: str) -> list[str]:
    """Find Chinese-English spacing violations including slash-separated terms."""
    issues: list[str] = []

    for line in text.split("\n"):
        if _is_code_or_heading(line):
            continue

        # Pattern 1: CJK + space(s) + English token
        issues.extend(re.findall(rf"[{CJK}]\s+{EN_TOKEN}", line))
        # Pattern 2: English token + space(s) + CJK
        issues.extend(re.findall(rf"{EN_TOKEN}\s+[{CJK}]", line))
        # Pattern 3: CJK + space(s) + backtick token
        issues.extend(re.findall(rf"[{CJK}]\s+{BT_TOKEN}", line))
        # Pattern 4: backtick token + space(s) + CJK
        issues.extend(re.findall(rf"{BT_TOKEN}\s+[{CJK}]", line))

    return sorted(set(issues))[:30]


def find_slash_spacing_issues(text: str) -> list[str]:
    """Find slash-separated term spacing violations.

    Detects patterns like:
      "API / CLI / SDK" (spaces around slashes between English tokens)
      "根据 API / CLI" (CJK space before slash group)
      "SDK / 配置文件" (slash group space before CJK)
    """
    issues: list[str] = []

    for line in text.split("\n"):
        if _is_code_or_heading(line):
            continue

        # Detect "EN space / space EN" patterns (spaced slashes between English tokens)
        matches = re.findall(
            rf"({EN_TOKEN}\s+/\s+{EN_TOKEN}(?:\s*/\s*{EN_TOKEN})*)",
            line,
        )
        issues.extend(matches)

        # Detect "/ space CJK" or "CJK space /" adjacent patterns
        issues.extend(re.findall(rf"/\s+[{CJK}]", line))
        issues.extend(re.findall(rf"[{CJK}]\s+/", line))

    return sorted(set(issues))[:20]


def find_en_ai_words(text: str) -> list[str]:
    found: list[str] = []

    for word in EN_AI_HIGH_FREQ_WORDS:
        pattern = re.compile(
            rf"(?<![A-Za-z0-9_]){re.escape(word)}(?![A-Za-z0-9_])",
            re.IGNORECASE,
        )
        if any(pattern.search(line) for line in _iter_non_code_lines(text)):
            found.append(word)

    return found


def find_dash_abuse(text: str) -> list[str]:
    issues: list[str] = []

    for line in _iter_non_code_lines(text):
        if "——" in line:
            issues.append(line.strip())

    return issues


def find_triplet_patterns(text: str) -> list[str]:
    issues: list[str] = []
    # Original: explicit 、和与 separators
    pattern = re.compile(r"[\u4e00-\u9fff]+、[\u4e00-\u9fff]+[、和与][\u4e00-\u9fff]+")
    # Extended: 3+ comma-separated 4-char phrases (e.g., 迎接挑战，抓住机遇，开创未来)
    idiom_chain = re.compile(
        r"[\u4e00-\u9fff]{2,6}[，,][\u4e00-\u9fff]{2,6}[，,][\u4e00-\u9fff]{2,6}"
    )

    for line in _iter_non_code_lines(text):
        stripped = line.lstrip()
        if stripped.startswith("|") or stripped.startswith("-"):
            continue
        issues.extend(pattern.findall(line))
        issues.extend(idiom_chain.findall(line))

    return list(dict.fromkeys(issues))


def find_empty_contrast(text: str) -> list[str]:
    issues: list[str] = []
    patterns = [
        re.compile(r"不是[^。！？.!?\n]{0,80}?而是[^。！？.!?\n]{0,80}"),
        re.compile(r"不仅仅是[^。！？.!?\n]{0,80}?更是[^。！？.!?\n]{0,80}"),
        re.compile(r"不仅是[^。！？.!?\n]{0,80}?更是[^。！？.!?\n]{0,80}"),
        re.compile(r"不仅[^。！？.!?\n]{0,80}?而且[^。！？.!?\n]{0,80}"),
        re.compile(r"不仅[^。！？.!?\n]{0,80}?更[^。！？.!?\n]{0,80}"),
        re.compile(
            r"\bnot\s+just\b[^.!?\n]{0,80}?\bbut\b[^.!?\n]{0,80}", re.IGNORECASE
        ),
        re.compile(
            r"\bnot\s+merely\b[^.!?\n]{0,80}?\bbut\b[^.!?\n]{0,80}", re.IGNORECASE
        ),
    ]

    for line in _iter_non_code_lines(text):
        for pattern in patterns:
            issues.extend(match.group(0) for match in pattern.finditer(line))

    return issues


def find_heading_issues(text: str) -> list[str]:
    """Detect heading format issues in Chinese Markdown."""
    issues: list[str] = []

    for i, line in enumerate(text.split("\n"), 1):
        stripped = line.strip()
        if not stripped.startswith("#"):
            continue
        # Only check H2-H4
        level = len(stripped) - len(stripped.lstrip("#"))
        if level < 2 or level > 4:
            continue

        # Issue: section number + Chinese without space
        if re.search(r'\d+(?:\.\d+)+[\u4e00-\u9fff(（]', stripped):
            issues.append(f"L{i}: missing space after section number in heading: {stripped[:80]}")

        # Issue: Chinese ordinal + text without space
        if re.search(r'第[一二三四五六七八九十百零]+(?:节|部分|章|篇|模块|单元)[\u4e00-\u9fffA-Za-z0-9(（]', stripped):
            issues.append(f"L{i}: missing space after Chinese ordinal in heading: {stripped[:80]}")

        # Issue: fullwidth space in heading
        if '\u3000' in stripped:
            issues.append(f"L{i}: fullwidth space (U+3000) in heading: {stripped[:80]}")

    return issues


# ---------------------------------------------------------------------------
# v4.1.0 — academic-writing humanization detections
# ---------------------------------------------------------------------------


def _sentence_length(sentence: str) -> int:
    """Measure sentence length: characters for CJK text, words for English.

    Heuristic: if the sentence contains any CJK character, count non-whitespace
    characters; otherwise count whitespace-separated words.
    """
    if re.search(f"[{CJK}]", sentence):
        return len(re.sub(r"\s", "", sentence))
    return len(sentence.split())


def _extract_starter(sentence: str) -> str:
    """Extract a sentence starter: first 2 chars for CJK, first word for English."""
    if re.search(f"[{CJK}]", sentence):
        return sentence[:2]
    match = re.match(r"\s*([A-Za-z]+)", sentence)
    if match:
        return match.group(1).lower()
    return sentence[:2]


def compute_burstiness(sentences: list[str]) -> dict:
    """Compute the coefficient of variation (CV) of sentence lengths.

    Low burstiness (CV < 0.4 with >= 5 sentences) indicates AI-like uniform
    sentence lengths.

    Returns a dict with keys: cv, mean, stdev, is_low.
    For fewer than 2 sentences, cv is None and is_low is False.
    """
    if len(sentences) < 2:
        return {"cv": None, "mean": 0.0, "stdev": 0.0, "is_low": False}

    lengths = [_sentence_length(s) for s in sentences]
    mean_val = statistics.mean(lengths)
    if mean_val == 0:
        return {"cv": None, "mean": 0.0, "stdev": 0.0, "is_low": False}
    stdev_val = statistics.stdev(lengths)
    cv = stdev_val / mean_val
    is_low = cv < 0.4 and len(sentences) >= 5
    return {"cv": cv, "mean": mean_val, "stdev": stdev_val, "is_low": is_low}


def find_syntactic_repetition(text: str) -> list[dict]:
    """Detect repeated sentence starters within the same paragraph.

    For each paragraph, extracts the starter of every sentence (first 2 chars
    for CJK or first word for English). If 3+ sentences in the same paragraph
    share the same starter, the paragraph is flagged.

    Returns a list of findings, each with keys: paragraph_index, starter, count.
    """
    findings: list[dict] = []
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]

    for idx, para in enumerate(paragraphs):
        sentences = split_sentences(para)
        if len(sentences) < 3:
            continue

        starters = [_extract_starter(s) for s in sentences]
        # Manual counting to avoid extra imports
        counts: dict[str, int] = {}
        for starter in starters:
            if not starter:
                continue
            counts[starter] = counts.get(starter, 0) + 1

        for starter, count in counts.items():
            if count >= 3:
                findings.append(
                    {
                        "paragraph_index": idx,
                        "starter": starter,
                        "count": count,
                    }
                )

    return findings


def find_paragraph_templating(text: str) -> dict:
    """Detect paragraph templating via near-zero sentence-count variance.

    Splits text into paragraphs (by blank lines) and counts sentences per
    paragraph. If there are 4+ paragraphs and all paragraph sentence counts
    fall within a ±1 band, flag as paragraph templating.

    Returns a dict with keys: paragraph_sentence_counts (list[int]),
    is_templating (bool).
    """
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    counts = [len(split_sentences(p)) for p in paragraphs]

    is_templating = False
    if len(paragraphs) >= 4 and counts:
        if max(counts) - min(counts) <= 1:
            is_templating = True

    return {
        "paragraph_sentence_counts": counts,
        "is_templating": is_templating,
    }


def check(text: str) -> dict:
    global _LAST_EXTRA_ISSUES

    sentences = split_sentences(text)
    long_sentences = [s for s in sentences if len(s) > 80]
    ai_terms = [p for p in AI_FLAVOR_PATTERNS if p in text]
    spacing_issues = find_zh_en_spacing_issues(text)
    slash_issues = find_slash_spacing_issues(text)
    en_ai_words = find_en_ai_words(text)
    dash_abuse = find_dash_abuse(text)
    triplet_patterns = find_triplet_patterns(text)
    empty_contrast = find_empty_contrast(text)
    heading_issues = find_heading_issues(text)

    # v4.1.0 — academic-writing humanization detections
    burstiness = compute_burstiness(sentences)
    syntactic_repetition = find_syntactic_repetition(text)
    paragraph_templating = find_paragraph_templating(text)

    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    has_closure = False
    if paragraphs:
        last = paragraphs[-1]
        has_closure = any(
            k in last
            for k in [
                "因此",
                "综上所述",
                "有必要",
                "下一步",
                "建议",
                "可以",
                "应当",
                "需要",
            ]
        )

    connector_count = sum(text.count(c) for c in LOGICAL_CONNECTORS)

    score = 100
    score -= min(len(ai_terms) * 8, 32)
    score -= min(len(en_ai_words) * 6, 24)
    score -= min(len(long_sentences) * 5, 25)
    score -= min(len(spacing_issues) * 4, 24)
    score -= min(len(slash_issues) * 4, 16)
    score -= min(len(dash_abuse) * 3, 15)
    score -= min(len(triplet_patterns) * 4, 16)
    score -= min(len(empty_contrast) * 5, 15)
    score -= min(len(heading_issues) * 4, 20)
    if connector_count == 0 and len(sentences) >= 3:
        score -= 10
    if not has_closure and len(paragraphs) >= 2:
        score -= 10
    # v4.1.0 penalties
    if burstiness["is_low"]:
        score -= 6
    if syntactic_repetition:
        score -= min(len(syntactic_repetition) * 5, 10)
    if paragraph_templating["is_templating"]:
        score -= 6
    score = max(score, 0)

    _LAST_EXTRA_ISSUES = {
        "en_ai_high_freq_words": en_ai_words,
        "dash_abuse": dash_abuse,
        "triplet_patterns": triplet_patterns,
        "empty_contrast": empty_contrast,
        "heading_issues": heading_issues,
        "syntactic_repetition": syntactic_repetition,
        "paragraph_templating": paragraph_templating,
        "burstiness": burstiness,
    }

    return {
        "score": score,
        "summary": {
            "sentence_count": len(sentences),
            "paragraph_count": len(paragraphs),
            "logical_connector_count": connector_count,
            "has_useful_closure": has_closure,
            "burstiness_cv": burstiness["cv"],
            "sentence_length_mean": round(burstiness["mean"], 2) if burstiness["mean"] else 0.0,
            "paragraph_sentence_counts": paragraph_templating["paragraph_sentence_counts"],
        },
        "issues": {
            "ai_flavor_terms": ai_terms,
            "en_ai_high_freq_words": en_ai_words,
            "long_sentences": long_sentences[:10],
            "zh_en_spacing_issues": spacing_issues,
            "slash_spacing_issues": slash_issues,
            "dash_abuse": dash_abuse,
            "triplet_patterns": triplet_patterns,
            "empty_contrast": empty_contrast,
            "heading_issues": heading_issues,
            "low_burstiness": burstiness,
            "syntactic_repetition": syntactic_repetition,
            "paragraph_templating": paragraph_templating,
        },
        "recommendations": build_recommendations(
            ai_terms,
            long_sentences,
            spacing_issues,
            slash_issues,
            connector_count,
            has_closure,
        ),
    }


def build_recommendations(
    ai_terms, long_sentences, spacing_issues, slash_issues, connector_count, has_closure
):
    recs = []
    en_ai_words = _LAST_EXTRA_ISSUES.get("en_ai_high_freq_words", [])
    dash_abuse = _LAST_EXTRA_ISSUES.get("dash_abuse", [])
    triplet_patterns = _LAST_EXTRA_ISSUES.get("triplet_patterns", [])
    empty_contrast = _LAST_EXTRA_ISSUES.get("empty_contrast", [])
    heading_issues = _LAST_EXTRA_ISSUES.get("heading_issues", [])
    syntactic_repetition = _LAST_EXTRA_ISSUES.get("syntactic_repetition", [])
    paragraph_templating = _LAST_EXTRA_ISSUES.get("paragraph_templating", {})
    burstiness = _LAST_EXTRA_ISSUES.get("burstiness", {})

    if ai_terms:
        recs.append(
            "Remove rhetorical or slogan-like expressions and replace them with concrete technical claims."
        )
    if en_ai_words:
        recs.append(
            "Replace AI-frequent English words (delve, nuanced, robust, etc.) with specific technical terms or concrete descriptions."
        )
    if long_sentences:
        recs.append(
            "Split long sentences so that each sentence carries one logical point."
        )
    if spacing_issues:
        recs.append(
            "Remove unnecessary spaces between Chinese text and English technical terms, for example Git提交 instead of Git 提交."
        )
    if slash_issues:
        recs.append(
            "Remove spaces around slashes in slash-separated English terms adjacent to Chinese, for example API/CLI/SDK instead of API / CLI / SDK."
        )
    if dash_abuse:
        recs.append(
            "Review em-dash (——) usage. Replace with commas, periods, or colons where the dash adds no meaningful pause or contrast."
        )
    if triplet_patterns:
        recs.append(
            "Check triplet parallel structures (A、B和C). Keep only when all three items carry distinct, concrete meaning."
        )
    if empty_contrast:
        recs.append(
            "Review 'not X but Y' structures. Remove or rewrite if the Y-part lacks specific mechanism, object, or outcome."
        )
    if heading_issues:
        recs.append(
            "Fix heading format: add space after section numbers and Chinese ordinals, replace fullwidth spaces with halfwidth."
        )
    if burstiness.get("is_low"):
        recs.append(
            "Vary sentence lengths deliberately. The current text has uniform sentence lengths (low burstiness), which reads as AI-generated; mix short and long sentences."
        )
    if syntactic_repetition:
        starters = sorted({f["starter"] for f in syntactic_repetition})
        recs.append(
            f"Diversify sentence openings. Multiple sentences in the same paragraph start with the same token ({', '.join(starters)}); rewrite to vary syntactic structure."
        )
    if paragraph_templating.get("is_templating"):
        recs.append(
            "Vary paragraph structure. All paragraphs have nearly the same sentence count, which suggests templated writing; let paragraph length follow content rather than a fixed mold."
        )
    if connector_count == 0:
        recs.append(
            "Add explicit logical connectors when the text contains multiple reasoning steps."
        )
    if not has_closure:
        recs.append(
            "Add a restrained closure that converges to necessity, next step, or bounded conclusion."
        )
    if not recs:
        recs.append("No major Petfish-style issues detected.")
    return recs


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check text against Petfish-style writing rules."
    )
    src = parser.add_mutually_exclusive_group(required=True)
    src.add_argument("--text", help="Input text to check")
    src.add_argument("--file", help="Input file path")
    parser.add_argument("--json", action="store_true", help="Print JSON only")
    args = parser.parse_args()

    if args.file:
        text = Path(args.file).read_text(encoding="utf-8")
    else:
        text = args.text

    result = check(text)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"Score: {result['score']}/100")
        print("\nSummary:")
        for k, v in result["summary"].items():
            print(f"  {k}: {v}")
        print("\nIssues:")
        for k, vals in result["issues"].items():
            print(f"  {k}:")
            if not vals:
                print("    (none)")
            elif isinstance(vals, dict):
                for dk, dv in vals.items():
                    print(f"    - {dk}: {dv}")
            elif vals and isinstance(vals[0], dict):
                for item in vals:
                    print(f"    - {item}")
            else:
                for item in vals:
                    print(f"    - {item}")
        print("\nRecommendations:")
        for r in result["recommendations"]:
            print(f"  - {r}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
