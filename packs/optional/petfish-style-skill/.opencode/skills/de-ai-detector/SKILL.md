---
name: de-ai-detector
description: Detect AI writing patterns in Chinese or English text. Use when the user asks to 检测AI味 / 检测AI痕迹 / 去AI检测 / AI写作检测, detect AI writing, check for AI patterns, is this AI-generated, AI slop check, or detect_ai. Produces a structured quantitative + qualitative detection report; does not rewrite.
compatibility: opencode
metadata:
  version: "1.0.0"
  author: "Petfish"
  owner: "Petfish"
---

# AI Writing Detector

## Purpose

Detect AI writing patterns in Chinese or English text and produce a structured detection report. This skill does NOT rewrite text — targeted rewriting is the job of `petfish-style-rewriter`.

## Activation

Use this skill when the user says any of the following:

- "检测AI味" / "检测AI痕迹" / "去AI检测" / "AI写作检测" / "AI腔检测"
- "detect AI writing" / "check for AI patterns" / "is this AI-generated" / "AI slop check" / "detect_ai"
- "这段是不是AI写的" / "有没有AI味" / "像不像AI写的"

## Workflow

1. Read the input text and auto-detect language (`zh` if >30% CJK characters, otherwise `en`).
2. Run `scripts/detect_ai.py` to compute quantitative metrics: burstiness, average sentence length, TTR, transition density, passive-voice %, AI buzzword count, and paragraph uniformity.
3. Apply qualitative pattern matching using the catalog in `references/ai-patterns.md`.
4. Produce the detection report below.

## Detection Report Format

```markdown
# AI Writing Detection Report
## Overall Assessment
- AI Probability: [Low/Medium/High] ([0-100]%)
- Confidence: [Low/Medium/High]
## Quantitative Metrics
| Metric | Value | Status | Baseline |
|---|---|---|---|
| Burstiness (CV) | 0.32 | ⚠ FLAG | >0.5 = human |
| Average sentence length | 28.5 | OK | informational |
| TTR | 0.68 | ⚠ WARN | >0.7 = human |
| Transition density | 18% | ⚠ FLAG | <10% = human |
| Passive voice % | 12% | OK | <20% = human |
| AI buzzword count | 7 | ⚠ WARN | ≥3 flagged |
| Paragraph uniformity | 0.23 | ⚠ FLAG | >0.4 = human |
## Flagged Patterns
### [CRITICAL] 空洞总结句
- Location: "综上所述，这一方案具有重要意义。"
- Signal: Empty summary phrase adds no information
- Fix suggestion: Replace with specific conclusion
[etc.]
## Summary
[2-3 sentence overall assessment]
```

## Two-layer Detection

- **Layer 1 (quantitative)**: `scripts/detect_ai.py` computes lexical and syntactic metrics defined in `references/detection-metrics.md`.
- **Layer 2 (qualitative)**: The LLM matches the text against the concrete AI patterns in `references/ai-patterns.md`, using Layer 1 results to focus attention.

## Relationship to petfish-style-rewriter

`de-ai-detector` produces a report; `petfish-style-rewriter` consumes the report to decide which patterns to target during rewriting. Use the detector first when the user only wants diagnosis, and route to the rewriter when the user asks for rewriting.

## Reference Loading

Load these references before qualitative analysis:

- `references/ai-patterns.md` — pattern catalog with severity and examples.
- `references/detection-metrics.md` — metric definitions, baselines, and thresholds.

## Domain Rules

- Do not rewrite. Diagnose only.
- Treat severity and clustering as evidence, not proof.
- For Chinese inputs, passive-voice % is not computed; report `N/A`.
- Metrics are calibrated for article-length inputs (~200–2000 tokens); very short texts may produce unstable CV/TTR.

## Decision Points

- If the user asks for rewriting after detection, hand off to `petfish-style-rewriter`.
- If the user only asks "is this AI?", produce the detection report without rewriting.
- If metrics conflict with qualitative patterns, explain the conflict in the summary rather than overriding one with the other.

## Execution Modes

- **Auto**: run the script and apply the LLM pattern stage without user interaction.
- **Review-only**: output only the quantitative metrics table when the user asks for a "quick check".

## Output Contracts

- A report must contain Overall Assessment, Quantitative Metrics table, Flagged Patterns, and Summary.
- Every flagged pattern must quote the source text and give a concrete fix suggestion.
- Percentages and counts must be numeric, not ranges.

## Anti-patterns

- Flagging a single pattern as proof of AI authorship.
- Reporting metrics without interpreting them.
- Rewriting the text instead of diagnosing it.

## Handoff & Boundaries

- **Owns**: detection, metrics, pattern naming, report generation.
- **Does not own**: rewriting (`petfish-style-rewriter`), formatting/translation (general agent), general writing advice (`petfish-style-rewriter`).

## Must Do

- Run `scripts/detect_ai.py` before producing the qualitative report.
- Load both reference files for the qualitative stage.
- Report confidence and AI probability separately.

## Must Not Do

- Rewrite, paraphrase, or polish the input text.
- Suppress metrics that do not match the qualitative impression.
- Treat any single metric as conclusive evidence.
