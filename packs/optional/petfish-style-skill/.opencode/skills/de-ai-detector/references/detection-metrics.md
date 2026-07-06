# Detection Metrics Reference

This document defines every quantitative metric emitted by `detect_ai.py`, including how it is calculated, what human and AI writing typically look like, and the thresholds used for flagging.

---

## 1. Burstiness (Coefficient of Variation of Sentence Lengths)

- **What it measures**: Whether sentence lengths vary (a hallmark of human writing) or stay uniform (a hallmark of AI output).
- **Calculation**:
  - Split text into sentences.
  - For Chinese, measure each sentence by non-whitespace character count.
  - For English, measure each sentence by whitespace-separated word count.
  - Compute `CV = stdev(lengths) / mean(lengths)`.
- **Human baseline**: CV > 0.5.
- **AI typical**: CV 0.2–0.4.
- **Thresholds**:
  - OK: CV ≥ 0.5
  - WARN: 0.35 ≤ CV < 0.5
  - FLAG: CV < 0.35 (or fewer than 5 sentences)

> Note: very short texts (< 5 sentences) can produce unstable CV; the metric is then marked INFO rather than FLAG.

---

## 2. Average Sentence Length

- **What it measures**: Central tendency of sentence size.
- **Calculation**:
  - Chinese: mean character count per sentence.
  - English: mean word count per sentence.
- **Human baseline**: Varies by genre; technical prose often 15–35 words (EN) or 25–60 characters (ZH).
- **AI typical**: Often clusters narrowly around the genre mean.
- **Thresholds**: This metric is informational. Extreme values (> 50 words or > 90 characters) are noted but not flagged on their own.

---

## 3. Type-Token Ratio (TTR)

- **What it measures**: Vocabulary diversity. Low TTR can indicate repetitive, templated wording.
- **Calculation**: `unique_tokens / total_tokens`.
  - Chinese: unique CJK characters / total CJK characters (punctuation excluded).
  - English: unique alphabetic words / total alphabetic words (case-insensitive).
- **Human baseline**: > 0.7 for short-to-medium texts.
- **AI typical**: < 0.6 when the same connectors and buzzwords repeat.
- **Thresholds**:
  - OK: TTR ≥ 0.7
  - WARN: 0.5 ≤ TTR < 0.7
  - FLAG: TTR < 0.5

> TTR decreases naturally as text grows. This detector is intended for article-length inputs (roughly 200–2000 tokens). For very long inputs, interpret TTR together with other metrics.

---

## 4. Transition Density

- **What it measures**: The proportion of sentences that begin with or contain explicit templated transitions.
- **Calculation**: `transition_hits / sentence_count`.
  - Chinese transitions: `首先`, `其次`, `最后`, `第一`, `第二`, `第三`, `一方面`, `另一方面`, `同时`, `此外`, `因此`, `所以`, `综上所述`, `总而言之`, `值得注意的是`.
  - English transitions: `Furthermore`, `Moreover`, `Additionally`, `However`, `Therefore`, `Thus`, `Consequently`, `In addition`, `On the other hand`, `For example`, `In conclusion`, `Notably`, `Interestingly`, `Meanwhile`.
- **Human baseline**: < 10% of sentences.
- **AI typical**: 15–40% of sentences.
- **Thresholds**:
  - OK: density < 10%
  - WARN: 10% ≤ density < 15%
  - FLAG: density ≥ 15%

---

## 5. Passive Voice Percentage (English only)

- **What it measures**: How many sentences use a `be + past participle` construction.
- **Calculation**: `passive_hits / sentence_count`.
  - Regex targets common forms: `is/are/was/were/been/being/be + [word ending in -ed]` plus a small list of common irregular participles (`made`, `done`, `seen`, `taken`, `given`, `written`, `built`, `found`).
- **Human baseline**: < 20% in most technical and narrative writing.
- **AI typical**: 30–60% when the actor is hidden.
- **Thresholds**:
  - OK: < 20%
  - WARN: 20%–30%
  - FLAG: > 30%

> For Chinese, passive constructions are not reliably detectable with simple regex, so this metric is reported as `N/A`.

---

## 6. Paragraph Length Variance

- **What it measures**: Whether paragraphs vary in size or are templated to the same length.
- **Calculation**:
  - Split text into paragraphs (blank-line separated).
  - For each paragraph, compute length in characters (ZH) or words (EN).
  - Compute `CV = stdev / mean`.
- **Human baseline**: CV > 0.4.
- **AI typical**: CV < 0.25 when paragraphs are structurally templated.
- **Thresholds**:
  - OK: CV ≥ 0.4
  - WARN: 0.25 ≤ CV < 0.4
  - FLAG: CV < 0.25 (or fewer than 4 paragraphs)

---

## 7. List Density

- **What it measures**: The fraction of non-empty lines that are list items.
- **Calculation**: `list_item_lines / total_non_empty_lines`.
  - List markers: `-`, `*`, `+`, or `1.`, `2.`, etc. at the start of a line.
- **Human baseline**: < 10% of lines.
- **AI typical**: > 20% when prose is over-bulleted.
- **Thresholds**:
  - OK: density < 10%
  - WARN: 10% ≤ density < 20%
  - FLAG: density ≥ 20%

---

## Combining Metrics

No single metric proves AI authorship. The detector combines them into an overall AI probability using weighted heuristics and then lets the LLM stage interpret the pattern cluster. Use the metrics table to identify *where* the text looks mechanical; use the flagged patterns to decide *what* to rewrite.
