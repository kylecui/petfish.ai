#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = []
# ///
"""Quantitative writing-style analyzer.

Reads Markdown files (or a directory of Markdown files) and emits JSON metrics
for each file plus aggregated cross-document metrics. The output is consumed by
the style-extractor skill to produce a qualitative style profile.

Usage:
  uv run analyze_style.py --samples ./samples/ --output style-metrics.json
  uv run analyze_style.py --samples a.md b.md c.md --output style-metrics.json
"""

from __future__ import annotations

import argparse
import json
import math
import re
from collections import Counter
from collections.abc import Sequence
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Static word lists (stdlib only)
# ---------------------------------------------------------------------------

EN_STOPWORDS = {
    "the", "a", "an", "is", "are", "was", "were", "be", "been", "being",
    "have", "has", "had", "do", "does", "did", "will", "would", "shall",
    "should", "can", "could", "may", "might", "must", "ought", "to", "of",
    "in", "on", "at", "by", "for", "with", "about", "against", "between",
    "into", "through", "during", "before", "after", "above", "below", "from",
    "up", "down", "out", "off", "over", "under", "again", "further", "then",
    "once", "here", "there", "when", "where", "why", "how", "all", "each",
    "every", "both", "few", "more", "most", "other", "some", "such", "no",
    "nor", "not", "only", "own", "same", "so", "than", "too", "very", "just",
    "and", "but", "if", "or", "because", "as", "until", "while", "this",
    "that", "these", "those", "i", "we", "you", "he", "she", "it", "they",
    "them", "their", "what", "which", "who", "whom", "whose", "my", "our",
    "your", "his", "her", "its",
}

ZH_STOPWORDS = {
    "的", "了", "在", "是", "我", "有", "和", "就", "不", "人", "都", "一",
    "一个", "上", "也", "很", "到", "说", "要", "去", "你", "会", "着", "没有",
    "看", "好", "自己", "这", "那", "这些", "那些", "之", "与", "及", "等",
    "或", "但", "而", "如果", "因为", "所以", "可以", "这个", "那个", "我们",
    "咱们", "他", "她", "它", "们", "为", "以", "被", "把", "让", "给", "对",
    "将", "还", "只", "最", "更", "太", "非常", "已经", "正在", "曾经",
    "进行", "作出", "成为", "需要", "表示", "认为", "觉得", "出现", "具有",
    "通过", "根据", "关于", "由于", "随着", "为了", "作为", "对于", "以及",
    "其中", "其", "所", "而", "且", "并", "且", "但是", "然而", "因此",
}

EN_TRANSITIONS = {
    "however", "therefore", "thus", "moreover", "furthermore", "nevertheless",
    "nonetheless", "consequently", "accordingly", "hence", "meanwhile",
    "alternatively", "otherwise", "instead", "similarly", "likewise",
    "in contrast", "on the other hand", "for example", "for instance",
    "in particular", "specifically", "indeed", "in fact", "as a result",
    "because", "since", "although", "though", "while", "whereas", "unless",
    "if", "then", "finally", "in conclusion", "to summarize", "overall",
    "additionally", "besides", "also", "yet", "still", "regardless",
}

ZH_TRANSITIONS = {
    "然而", "但是", "不过", "因此", "所以", "于是", "因而", "从而", "此外",
    "另外", "而且", "并且", "同时", "相反", "反之", "另一方面", "例如",
    "比如", "譬如", "具体来说", "具体而言", "事实上", "实际上", "确实",
    "诚然", "虽然", "尽管", "即使", "由于", "因为", "所以", "综上所述",
    "总之", "总而言之", "最后", "最终", "首先", "其次", "再次", "第一",
    "第二", "第三", "一方面", "与此同时", "紧接着", "随后", "然后", "接着",
    "除此以外", "除此之外", "何况", "况且", "除非", "只要", "只有",
    "换言之", "换句话说", "也就是说", "这意味着", "由此可见", "不难看出",
}

EN_PRONOUNS = {
    "i", "we", "us", "our", "my", "mine", "this paper", "this article",
    "this study", "this work", "the author", "authors",
}

ZH_PRONOUNS = {
    "我", "我们", "笔者", "本人", "本文", "本研究", "本论文", "笔者们",
    "作者", "本篇文章",
}

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def mean(values: Sequence[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def median(values: Sequence[float]) -> float:
    if not values:
        return 0.0
    s = sorted(values)
    n = len(s)
    if n % 2 == 1:
        return s[n // 2]
    return (s[n // 2 - 1] + s[n // 2]) / 2.0


def stdev(values: Sequence[float]) -> float:
    if len(values) < 2:
        return 0.0
    m = mean(values)
    variance = sum((x - m) ** 2 for x in values) / (len(values) - 1)
    return math.sqrt(variance)


def coefficient_of_variation(values: Sequence[float]) -> float:
    m = mean(values)
    if m == 0:
        return 0.0
    return stdev(values) / m


def classify_language(text: str) -> str:
    """Classify text as zh, en, or mixed based on character ranges."""
    cjk = len(re.findall(r"[\u4e00-\u9fff\u3000-\u303f\uff00-\uffef]", text))
    latin = len(re.findall(r"[a-zA-Z]", text))
    total = len(text)
    if total == 0:
        return "en"
    cjk_ratio = cjk / total
    latin_ratio = latin / total
    if cjk_ratio > 0.05 and latin_ratio > 0.05:
        return "mixed"
    if cjk_ratio > 0.05:
        return "zh"
    return "en"


def split_sentences(text: str, lang: str) -> list[str]:
    """Split text into sentences."""
    if lang == "zh":
        # Split on Chinese sentence-ending punctuation
        parts = re.split(r"([。！？；…]+)", text)
    else:
        # English-aware split
        parts = re.split(r"([.!?]+)\s+", text)

    sentences = []
    i = 0
    while i < len(parts):
        sent = parts[i].strip()
        if i + 1 < len(parts):
            sent += parts[i + 1]
            i += 2
        else:
            i += 1
        sent = sent.strip()
        if sent:
            sentences.append(sent)
    return sentences


def sentence_length(sentence: str, lang: str) -> int:
    if lang == "zh":
        return len(re.findall(r"[\u4e00-\u9fff]", sentence))
    return len(re.findall(r"[a-zA-Z]+", sentence))


def extract_words(text: str, lang: str) -> list[str]:
    """Extract content words, lowercased."""
    words: list[str] = []
    if lang in ("zh", "mixed"):
        # Treat each CJK character as a token for stopword filtering
        chars = re.findall(r"[\u4e00-\u9fff]", text)
        words.extend(chars)
    if lang in ("en", "mixed"):
        en = re.findall(r"[a-zA-Z]+(?:[-'][a-zA-Z]+)?", text)
        words.extend(w.lower() for w in en)
    return words


def extract_en_words(text: str) -> list[str]:
    return [w.lower() for w in re.findall(r"[a-zA-Z]+(?:[-'][a-zA-Z]+)?", text)]


def extract_zh_chars(text: str) -> list[str]:
    return re.findall(r"[\u4e00-\u9fff]", text)


def top_non_stopwords(words: list[str], lang: str, n: int = 50) -> list[tuple[str, int]]:
    if lang == "zh":
        stop = ZH_STOPWORDS
    elif lang == "en":
        stop = EN_STOPWORDS
    else:
        stop = ZH_STOPWORDS | EN_STOPWORDS
    filtered = [w for w in words if w not in stop and len(w) > 1]
    return Counter(filtered).most_common(n)


def split_paragraphs(text: str) -> list[str]:
    # Remove Markdown headings/code fences but keep paragraph breaks
    return [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]


def paragraph_length_chars(paragraph: str, lang: str) -> int:
    if lang == "zh":
        return len(re.findall(r"[\u4e00-\u9fff]", paragraph))
    return len(extract_en_words(paragraph))


def transition_frequency(text: str, lang: str) -> dict[str, int]:
    text_lower = text.lower()
    if lang == "zh":
        return {t: len(re.findall(re.escape(t), text)) for t in ZH_TRANSITIONS}
    return {t: len(re.findall(r"\b" + re.escape(t) + r"\b", text_lower)) for t in EN_TRANSITIONS}


def pronoun_frequency(text: str, lang: str) -> dict[str, int]:
    text_lower = text.lower()
    if lang == "zh":
        return {p: len(re.findall(re.escape(p), text)) for p in ZH_PRONOUNS}
    result: dict[str, int] = {}
    for p in EN_PRONOUNS:
        if " " in p:
            result[p] = len(re.findall(re.escape(p), text_lower))
        else:
            result[p] = len(re.findall(r"\b" + re.escape(p) + r"\b", text_lower))
    return result


def question_mark_density(text: str) -> float:
    return text.count("?") + text.count("？")


def list_line_percentage(text: str) -> float:
    lines = [ln for ln in text.splitlines() if ln.strip()]
    if not lines:
        return 0.0
    list_lines = [ln for ln in lines if re.match(r"^\s*[-*+\d]", ln)]
    return len(list_lines) / len(lines)


def average_clause_depth(text: str, lang: str) -> float:
    """Approximate clause depth via punctuation density."""
    sentences = split_sentences(text, lang)
    if not sentences:
        return 0.0
    total = 0.0
    for sent in sentences:
        marks = len(re.findall(r"[、,;，；]", sent))
        total += marks
    return total / len(sentences)


def type_token_ratio(words: list[str]) -> float:
    if not words:
        return 0.0
    return len(set(words)) / len(words)


def analyze_file(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8", errors="ignore")
    lang = classify_language(text)
    sentences = split_sentences(text, lang)
    sent_lengths = [sentence_length(s, lang) for s in sentences if sentence_length(s, lang) > 0]
    paragraphs = split_paragraphs(text)
    para_lengths = [paragraph_length_chars(p, lang) for p in paragraphs]
    words = extract_words(text, lang)
    ttr = type_token_ratio(words)
    top_words = top_non_stopwords(words, lang, n=50)
    transitions = transition_frequency(text, lang)
    pronouns = pronoun_frequency(text, lang)
    q_density = question_mark_density(text)
    list_pct = list_line_percentage(text)
    clause_depth = average_clause_depth(text, lang)

    # Heading analysis
    headings = re.findall(r"^#{1,6}\s+(.+)$", text, re.MULTILINE)
    heading_levels = []
    for line in text.splitlines():
        m = re.match(r"^(#{1,6})\s+", line)
        if m:
            heading_levels.append(len(m.group(1)))

    # Opening / closing fragments (first/last 200 chars or 50 words)
    opening = text[:200].strip().replace("\n", " ")
    closing = text[-200:].strip().replace("\n", " ")

    return {
        "path": str(path),
        "language": lang,
        "char_count": len(text),
        "sentence_count": len(sentences),
        "sentence_lengths": {
            "values": sent_lengths,
            "mean": round(mean(sent_lengths), 2),
            "median": round(median(sent_lengths), 2),
            "std": round(stdev(sent_lengths), 2),
            "cv": round(coefficient_of_variation(sent_lengths), 3),
            "min": min(sent_lengths) if sent_lengths else 0,
            "max": max(sent_lengths) if sent_lengths else 0,
        },
        "paragraph_count": len(paragraphs),
        "paragraph_lengths": {
            "values": para_lengths,
            "mean": round(mean(para_lengths), 2),
            "median": round(median(para_lengths), 2),
            "std": round(stdev(para_lengths), 2),
            "cv": round(coefficient_of_variation(para_lengths), 3),
            "min": min(para_lengths) if para_lengths else 0,
            "max": max(para_lengths) if para_lengths else 0,
        },
        "type_token_ratio": round(ttr, 3),
        "unique_word_count": len(set(words)),
        "total_word_count": len(words),
        "top_words": top_words,
        "transition_frequency": {k: v for k, v in transitions.items() if v > 0},
        "transition_total": sum(transitions.values()),
        "pronoun_frequency": {k: v for k, v in pronouns.items() if v > 0},
        "pronoun_total": sum(pronouns.values()),
        "question_marks": q_density,
        "list_line_percentage": round(list_pct, 3),
        "average_clause_depth": round(clause_depth, 3),
        "headings": {
            "count": len(headings),
            "levels": heading_levels,
            "titles": headings[:20],
        },
        "opening_snippet": opening,
        "closing_snippet": closing,
    }


def weighted_average(values: list[float], weights: list[float]) -> float:
    if sum(weights) == 0:
        return 0.0
    return sum(v * w for v, w in zip(values, weights)) / sum(weights)


def aggregate_metrics(file_results: list[dict[str, Any]]) -> dict[str, Any]:
    if not file_results:
        return {}

    # Separate by language
    by_lang: dict[str, list[dict[str, Any]]] = {"zh": [], "en": [], "mixed": []}
    for r in file_results:
        by_lang.setdefault(r["language"], []).append(r)

    def agg_lang(results: list[dict[str, Any]]) -> dict[str, Any]:
        weights = [r["char_count"] for r in results]
        sent_cvs = [r["sentence_lengths"]["cv"] for r in results]
        sent_means = [r["sentence_lengths"]["mean"] for r in results]
        para_cvs = [r["paragraph_lengths"]["cv"] for r in results]
        para_means = [r["paragraph_lengths"]["mean"] for r in results]
        ttrs = [r["type_token_ratio"] for r in results]
        clause_depths = [r["average_clause_depth"] for r in results]
        list_pcts = [r["list_line_percentage"] for r in results]
        qms = [r["question_marks"] for r in results]

        # Aggregate top words by weighted sum of frequencies
        word_counter: Counter = Counter()
        for r in results:
            for word, count in r["top_words"]:
                word_counter[word] += count

        # Aggregate transitions
        transition_counter: Counter = Counter()
        pronoun_counter: Counter = Counter()
        for r in results:
            for k, v in r.get("transition_frequency", {}).items():
                transition_counter[k] += v
            for k, v in r.get("pronoun_frequency", {}).items():
                pronoun_counter[k] += v

        return {
            "file_count": len(results),
            "total_char_count": sum(weights),
            "sentence": {
                "mean_length": round(weighted_average(sent_means, weights), 2),
                "burstiness_cv": round(weighted_average(sent_cvs, weights), 3),
                "mean_clause_depth": round(weighted_average(clause_depths, weights), 3),
            },
            "paragraph": {
                "mean_length": round(weighted_average(para_means, weights), 2),
                "burstiness_cv": round(weighted_average(para_cvs, weights), 3),
            },
            "vocabulary": {
                "type_token_ratio": round(weighted_average(ttrs, weights), 3),
                "top_words": word_counter.most_common(30),
            },
            "transitions": dict(transition_counter.most_common(20)),
            "pronouns": dict(pronoun_counter.most_common(10)),
            "question_marks": sum(qms),
            "list_line_percentage": round(weighted_average(list_pcts, weights), 3),
        }

    aggregated = {lang: agg_lang(results) for lang, results in by_lang.items() if results}

    # Cross-lingual summary
    lang_weights = {
        lang: sum(r["char_count"] for r in results)
        for lang, results in by_lang.items()
        if results
    }

    cross_lingual = {
        "detected_languages": list(aggregated.keys()),
        "language_char_weights": lang_weights,
        "dominant_language": max(lang_weights.items(), key=lambda kv: kv[1])[0] if lang_weights else "en",
        "sample_count": len(file_results),
    }

    return {
        "by_language": aggregated,
        "cross_lingual": cross_lingual,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Quantitative writing-style analyzer.")
    parser.add_argument("--samples", nargs="+", required=True, help="Markdown files or directories to analyze")
    parser.add_argument("--output", required=True, help="Output JSON file path")
    args = parser.parse_args()

    paths: list[Path] = []
    for sample in args.samples:
        p = Path(sample)
        if p.is_dir():
            paths.extend(sorted(p.glob("**/*.md")))
        else:
            paths.append(p)

    paths = [p for p in paths if p.suffix.lower() == ".md" and p.is_file()]
    if not paths:
        print("No Markdown files found.", file=sys.stderr)
        return 1

    file_results = [analyze_file(p) for p in paths]
    aggregated = aggregate_metrics(file_results)

    output = {
        "files": file_results,
        "aggregated": aggregated,
        "cross_lingual": aggregated.get("cross_lingual", {}),
    }

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Metrics written to {out_path}")
    return 0


if __name__ == "__main__":
    import sys
    raise SystemExit(main())
