#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = []
# ///
"""Compute quantitative AI-writing detection metrics for Chinese or English text.

Usage:
    uv run detect_ai.py input.txt
    uv run detect_ai.py input.txt --lang zh
    uv run detect_ai.py input.txt --json

The script always prints JSON. Use --json to make the flag explicit.
"""

from __future__ import annotations

import argparse
import json
import re
import statistics
import sys
from pathlib import Path

CHINESE_TRANSITIONS = [
    "首先",
    "其次",
    "最后",
    "第一",
    "第二",
    "第三",
    "一方面",
    "另一方面",
    "同时",
    "此外",
    "因此",
    "所以",
    "综上所述",
    "总而言之",
    "值得注意的是",
]

ENGLISH_TRANSITIONS = [
    "furthermore",
    "moreover",
    "additionally",
    "however",
    "therefore",
    "thus",
    "consequently",
    "in addition",
    "on the other hand",
    "for example",
    "in conclusion",
    "notably",
    "interestingly",
    "meanwhile",
]

CHINESE_BUZZWORDS = [
    "综上所述",
    "总而言之",
    "值得注意的是",
    "不言而喻",
    "毋庸置疑",
    "赋能",
    "打造闭环",
    "完整能力闭环",
    "持续沉淀",
    "最佳实践",
    "立体认知",
    "全面提升",
    "极大地",
    "显著地",
    "全面地",
    "深刻地",
    "有效地",
    "旨在",
    "重塑",
    "革命",
]

ENGLISH_BUZZWORDS = [
    "delve",
    "nuanced",
    "robust",
    "leverage",
    "paradigm",
    "foster",
    "seamlessly",
    "transformative",
    "holistic",
    "groundbreaking",
    "cutting-edge",
    "pivotal",
    "crucial",
    "vital",
    "significant",
    "it is worth noting",
    "it should be mentioned",
    "it is important to",
    "this demonstrates",
    "this highlights",
    "this underscores",
    "not only",
    "but also",
]

BE_VERBS = {"am", "is", "are", "was", "were", "been", "being", "be"}
IRREGULAR_PARTICIPLES = {
    "made",
    "done",
    "seen",
    "taken",
    "given",
    "written",
    "built",
    "found",
    "shown",
    "known",
    "begun",
    "chosen",
    "driven",
    "eaten",
    "fallen",
    "felt",
    "flown",
    "forgotten",
    "gotten",
    "grown",
    "hidden",
    "hit",
    "held",
    "kept",
    "laid",
    "led",
    "left",
    "lent",
    "let",
    "lost",
    "met",
    "paid",
    "put",
    "read",
    "ridden",
    "rung",
    "run",
    "said",
    "sold",
    "sent",
    "set",
    "shaken",
    "shot",
    "shut",
    "sung",
    "sunk",
    "sat",
    "slept",
    "spoken",
    "spent",
    "stood",
    "stolen",
    "struck",
    "sworn",
    "swept",
    "swum",
    "taught",
    "told",
    "thought",
    "thrown",
    "understood",
    "woken",
    "worn",
    "won",
    "wound",
}


def detect_language(text: str) -> str:
    """Return 'zh' if >30% of meaningful characters are CJK, else 'en'."""
    meaningful = re.sub(r"\s+", "", text)
    meaningful = re.sub(r"[^\w\u4e00-\u9fff]", "", meaningful)
    if not meaningful:
        return "en"
    cjk = len(re.findall(r"[\u4e00-\u9fff]", meaningful))
    total = len(re.findall(r"[a-zA-Z0-9\u4e00-\u9fff]", meaningful))
    return "zh" if total and cjk / total > 0.30 else "en"


def split_sentences_zh(text: str) -> list[str]:
    text = re.sub(r"\s+", " ", text).strip()
    parts = re.split(r"([。！？]+)", text)
    sentences: list[str] = []
    current = ""
    for part in parts:
        current += part
        if re.fullmatch(r"\s*[。！？]+\s*", part):
            stripped = current.strip()
            if stripped:
                sentences.append(stripped)
            current = ""
    if current.strip():
        sentences.append(current.strip())
    return sentences


def split_sentences_en(text: str) -> list[str]:
    text = re.sub(r"\s+", " ", text).strip()
    placeholders = {
        "e.g.": "\x00EG\x00",
        "i.e.": "\x00IE\x00",
        "etc.": "\x00ETC\x00",
        "vs.": "\x00VS\x00",
        "Dr.": "\x00DR\x00",
        "Mr.": "\x00MR\x00",
        "Mrs.": "\x00MRS\x00",
        "Ms.": "\x00MS\x00",
        "Prof.": "\x00PROF\x00",
        "Sr.": "\x00SR\x00",
        "Jr.": "\x00JR\x00",
        "Inc.": "\x00INC\x00",
        "Ltd.": "\x00LTD\x00",
        "Corp.": "\x00CORP\x00",
        "Fig.": "\x00FIG\x00",
        "fig.": "\x00fig\x00",
    }
    protected = text
    for abbr, placeholder in placeholders.items():
        protected = protected.replace(abbr, placeholder)

    parts = re.split(r"(\s*[.!?]+\s*)", protected)
    sentences: list[str] = []
    current = ""
    for part in parts:
        if re.fullmatch(r"\s*[.!?]+\s*", part):
            current += part
            stripped = current.strip()
            if stripped:
                for abbr, placeholder in placeholders.items():
                    stripped = stripped.replace(placeholder, abbr)
                sentences.append(stripped)
            current = ""
        else:
            current += part
    if current.strip():
        stripped = current.strip()
        for abbr, placeholder in placeholders.items():
            stripped = stripped.replace(placeholder, abbr)
        sentences.append(stripped)
    return sentences


def split_sentences(text: str, lang: str) -> list[str]:
    if lang == "zh":
        return split_sentences_zh(text)
    return split_sentences_en(text)


def sentence_length(sentence: str, lang: str) -> int:
    if lang == "zh":
        return len(re.sub(r"\s+", "", sentence))
    return len(re.findall(r"[a-zA-Z]+(?:['’-][a-zA-Z]+)*", sentence))


def compute_burstiness(sentences: list[str], lang: str) -> tuple[float, list[int]]:
    lengths = [sentence_length(s, lang) for s in sentences]
    if len(lengths) < 2:
        return 0.0, lengths
    mean = statistics.mean(lengths)
    if mean == 0:
        return 0.0, lengths
    return statistics.stdev(lengths) / mean, lengths


def compute_ttr(text: str, lang: str) -> tuple[float, int]:
    if lang == "zh":
        chars = re.findall(r"[\u4e00-\u9fff]", text)
        total = len(chars)
        unique = len(set(chars))
    else:
        words = re.findall(r"[a-zA-Z]+(?:['’-][a-zA-Z]+)*", text.lower())
        total = len(words)
        unique = len(set(words))
    return (unique / total) if total else 0.0, total


def compute_transition_density(sentences: list[str], lang: str) -> tuple[float, list[str]]:
    transitions = CHINESE_TRANSITIONS if lang == "zh" else ENGLISH_TRANSITIONS
    hits = 0
    matched: list[str] = []
    for sentence in sentences:
        start = re.sub(r"^[^\w\u4e00-\u9fff]+", "", sentence).lower()
        for trans in transitions:
            trans_lower = trans.lower()
            if start.startswith(trans_lower):
                hits += 1
                matched.append(trans)
                break
    density = hits / len(sentences) if sentences else 0.0
    return density, matched


def compute_passive_voice(sentences: list[str]) -> tuple[float, list[str]]:
    hits = 0
    matched: list[str] = []
    for sentence in sentences:
        words = re.findall(r"[a-zA-Z]+(?:['’-][a-zA-Z]+)*", sentence.lower())
        for i in range(len(words) - 1):
            if words[i] in BE_VERBS:
                next_word = words[i + 1]
                if next_word.endswith("ed") or next_word in IRREGULAR_PARTICIPLES:
                    hits += 1
                    matched.append(f"{words[i]} {next_word}")
                    break
    pct = hits / len(sentences) if sentences else 0.0
    return pct, matched


def compute_ai_buzzwords(text: str, lang: str) -> tuple[int, list[str]]:
    buzzwords = CHINESE_BUZZWORDS if lang == "zh" else ENGLISH_BUZZWORDS
    found: list[str] = []
    text_lower = text.lower()
    for phrase in buzzwords:
        count = len(re.findall(re.escape(phrase.lower()), text_lower))
        if count:
            found.extend([phrase] * min(count, 3))  # cap repeats for reporting
    total = len(found)
    unique = sorted(set(found))
    return total, unique


def split_paragraphs(text: str) -> list[str]:
    return [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]


def compute_paragraph_uniformity(text: str) -> tuple[float, list[int]]:
    paragraphs = split_paragraphs(text)
    counts = [len(split_sentences_zh(p)) + len(split_sentences_en(p)) for p in paragraphs]
    if len(counts) < 2:
        return 0.0, counts
    mean = statistics.mean(counts)
    if mean == 0:
        return 0.0, counts
    return statistics.stdev(counts) / mean, counts


def classify_cv(value: float, n: int, min_n: int) -> str:
    if n < min_n:
        return "INFO"
    if value >= 0.5:
        return "OK"
    if value >= 0.35:
        return "WARN"
    return "FLAG"


def classify_transition_density(value: float) -> str:
    if value < 0.10:
        return "OK"
    if value < 0.15:
        return "WARN"
    return "FLAG"


def classify_ttr(value: float, total: int) -> str:
    if total < 20:
        return "INFO"
    if value >= 0.7:
        return "OK"
    if value >= 0.5:
        return "WARN"
    return "FLAG"


def classify_passive_voice(value: float) -> str:
    if value < 0.20:
        return "OK"
    if value <= 0.30:
        return "WARN"
    return "FLAG"


def classify_buzzwords(value: int) -> str:
    if value == 0:
        return "OK"
    if value >= 3:
        return "WARN"
    return "INFO"


def classify_paragraph_uniformity(value: float, n: int) -> str:
    if n < 4:
        return "INFO"
    if value >= 0.4:
        return "OK"
    if value >= 0.25:
        return "WARN"
    return "FLAG"


def overall_ai_probability(metrics: dict) -> tuple[str, str]:
    score = 0
    for status in metrics.values():
        if status == "FLAG":
            score += 25
        elif status == "WARN":
            score += 10
        elif status == "INFO":
            score += 3
    score = min(score, 100)
    if score <= 30:
        prob = "Low"
    elif score <= 60:
        prob = "Medium"
    else:
        prob = "High"
    return prob, f"{score}%"


def overall_confidence(sentence_count: int) -> str:
    if sentence_count < 5:
        return "Low"
    if sentence_count < 20:
        return "Medium"
    return "High"


def analyze(text: str, lang: str | None) -> dict:
    if lang is None:
        lang = detect_language(text)

    sentences = split_sentences(text, lang)
    sentence_count = len(sentences)

    burstiness_cv, _ = compute_burstiness(sentences, lang)
    avg_length = statistics.mean([sentence_length(s, lang) for s in sentences]) if sentences else 0.0
    ttr, token_total = compute_ttr(text, lang)
    transition_density, _ = compute_transition_density(sentences, lang)
    paragraph_cv, _ = compute_paragraph_uniformity(text)
    buzzword_count, buzzword_patterns = compute_ai_buzzwords(text, lang)

    metrics: dict = {
        "burstiness_cv": {
            "value": round(burstiness_cv, 2),
            "status": classify_cv(burstiness_cv, sentence_count, 5),
            "baseline": ">0.5",
        },
        "avg_sentence_length": {
            "value": round(avg_length, 1),
            "status": "OK",
            "baseline": "informational",
        },
        "ttr": {
            "value": round(ttr, 2),
            "status": classify_ttr(ttr, token_total),
            "baseline": ">0.7",
        },
        "transition_density": {
            "value": round(transition_density, 2),
            "status": classify_transition_density(transition_density),
            "baseline": "<0.10",
        },
        "paragraph_uniformity": {
            "value": round(paragraph_cv, 2),
            "status": classify_paragraph_uniformity(paragraph_cv, len(split_paragraphs(text))),
            "baseline": ">0.4",
        },
        "ai_buzzword_count": {
            "value": buzzword_count,
            "status": classify_buzzwords(buzzword_count),
            "baseline": "≥3 flagged",
            "patterns": buzzword_patterns,
        },
    }

    if lang == "zh":
        metrics["passive_voice_pct"] = {
            "value": None,
            "status": "N/A",
            "baseline": "<20%",
            "note": "Chinese text",
        }
    else:
        passive_pct, _ = compute_passive_voice(sentences)
        metrics["passive_voice_pct"] = {
            "value": round(passive_pct, 2),
            "status": classify_passive_voice(passive_pct),
            "baseline": "<20%",
        }

    statuses = {k: v["status"] for k, v in metrics.items()}
    prob, pct = overall_ai_probability(statuses)

    return {
        "language": lang,
        "sentence_count": sentence_count,
        "metrics": metrics,
        "overall_ai_probability": f"{prob} ({pct})",
        "confidence": overall_confidence(sentence_count),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Quantitative AI-writing detection metrics (JSON output)."
    )
    parser.add_argument("input", help="Path to text file")
    parser.add_argument("--lang", choices=["zh", "en"], help="Force language (default: auto)")
    parser.add_argument("--json", action="store_true", help="Output JSON (default behavior)")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    path = Path(args.input)
    if not path.is_file():
        print(f"File not found: {path}", file=sys.stderr)
        return 2

    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        print(f"Could not read {path}: {exc}", file=sys.stderr)
        return 2

    result = analyze(text, args.lang)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
