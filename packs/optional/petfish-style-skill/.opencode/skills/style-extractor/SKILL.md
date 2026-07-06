---
name: style-extractor
description: Extract personal writing style from samples to create a style profile. Analyzes sentence patterns, vocabulary preferences, argumentation structure, punctuation habits, tone markers, and AI-distinguishability signals across Chinese and English. Use when "提炼我的写作风格", "extract my style", "create style profile", "analyze my writing", "风格画像", "个性化风格提取", or when setting up petfish-style-rewriter for the first time.
compatibility: opencode
metadata:
  version: "1.0.0"
  author: "Petfish"
---

# Style Extractor

## Purpose

Transform a user's writing samples into a structured, actionable style profile. The profile captures the user's recognizably-human voice across sentence-level, paragraph-level, vocabulary-level, and argumentation-level signals. The output is consumed by `petfish-style-rewriter` so that rewrites match the user's style rather than a generic target.

This skill is **extraction only**. It does not detect AI-generated text and it does not rewrite content.

## Triggers / Activation

Use this skill when the user asks for any of the following:

- 提炼我的写作风格 / 提炼写作风格
- extract my style / extract my writing style
- create style profile / build a style profile
- analyze my writing / analyze my style
- 风格画像 / 我的风格画像
- 个性化风格提取 / 个性化设置
- 第一次设置 petfish-style-rewriter
- first-time setup for style-rewriter

Do not use this skill for:

- Direct rewriting or polishing → route to `petfish-style-rewriter`
- Generic AI-text detection → not supported
- Document conversion only → route to `doc-reader`

## Prerequisites

1. The user must provide **3 or more** writing samples.
2. More samples produce a better extraction.
3. Minimum bilingual requirement: if the user writes in both Chinese and English, provide at least **1 Chinese + 1 English** sample.
4. Accepted formats: Markdown (`.md`), DOCX (`.docx`), PDF (`.pdf`).
   - DOCX and PDF must first be converted to Markdown via `doc-reader` (`scripts/doc_to_markdown.py`) before analysis.

## Domain Rules

- This skill never writes, edits, or rewrites the user's text. It only reads and measures.
- The final style profile is written to `.petfish/style-profile.md` in the active project, not inside the skill pack. Style profiles are private user data.
- Quantitative metrics are produced by a stdlib-only Python script (`scripts/analyze_style.py`). Qualitative synthesis is performed by the LLM using those metrics as evidence.
- Chinese and English are analyzed separately and then cross-compared. Do not collapse them into one undifferentiated profile.
- Signature phrases, pronoun preferences, and register patterns must be derived from the data, not invented.
- "AI-distinguishability signals" are positive human markers (burstiness, idiosyncrasy, imperfection) that should be preserved, not eliminated.

## Extraction Dimensions

Based on nuwa-skill's multi-dimensional extraction methodology:

1. **Sentence statistics** — length, variance, complexity, burstiness (coefficient of variation).
2. **Vocabulary profile** — density, formality tier, signature phrases, technical density.
3. **Argumentation pattern** — how the user builds and closes arguments.
4. **Transition style** — connector preferences and logical-flow markers.
5. **Paragraph organization** — length, structure, topic-sentence position.
6. **Punctuation habits** — comma-heavy vs period-heavy, semicolon/colon/dash usage.
7. **Title/heading conventions** — heading depth, numbering style, capitalization.
8. **Opening/closing patterns** — how pieces begin and end.
9. **Person pronoun usage** — 笔者/我们/本文/我 for Chinese; we/I/this paper for English.
10. **Register awareness** — formal vs casual, code-switching, domain tone.
11. **AI distinguishability** — what makes the writing recognizably human and should be preserved.

See `references/extraction-dimensions.md` for detailed definitions, interpretation guidance, and example profiles.

## Two-Stage Workflow

### Stage 0: Convert non-Markdown samples

For each PDF or DOCX sample, run:

```bash
uv run scripts/doc_to_markdown.py sample.docx --output sample.md
uv run scripts/doc_to_markdown.py sample.pdf --output sample.md
```

### Stage 1: Quantitative analysis

Run the analyzer on the directory of Markdown samples:

```bash
uv run .opencode/skills/style-extractor/scripts/analyze_style.py --samples ./my-samples/ --output style-metrics.json
```

This produces `style-metrics.json` with per-file and aggregated metrics.

### Stage 2: Qualitative synthesis

The agent reads `style-metrics.json` and each converted Markdown sample, then generates `.petfish/style-profile.md` using the template at `references/style-profile-template.md`. The synthesis must:

- Cite concrete metrics from Stage 1.
- Quote representative short passages from the samples.
- Keep each section short and actionable for the rewriter.
- Flag uncertainty when sample size is small.

## Decision Points

1. **Enough samples?** If fewer than 3 samples are provided, stop and ask for more. If the user is bilingual but supplies only one language, note the limitation in the profile.
2. **Language split**: Classify each sample as `zh`, `en`, or `mixed`. Chinese-only, English-only, and bilingual sample sets are all supported; the output structure adapts accordingly.
3. **Metrics outlier handling**: If one sample is very different from the others, report it as a possible register switch or outlier rather than averaging it away.
4. **Profile confidence**: Label the profile as `high`, `medium`, or `low` confidence based on sample count, consistency, and language coverage.

## Execution Modes

| Mode | Behavior |
|------|----------|
| interactive | Ask the user for sample files/locations, confirm language coverage, explain the output location, and show a preview of the metrics before writing the final profile. |
| auto | Accept the provided sample paths, run Stage 0–2, and write `.petfish/style-profile.md` with minimal explanation. |

Default to `interactive` when the user only says "extract my style" without providing paths. Default to `auto` when paths are explicit.

## Output Contract

Required deliverables:

1. `style-metrics.json` — structured quantitative metrics (per-file + aggregated + cross-lingual).
2. `.petfish/style-profile.md` — qualitative style profile following `references/style-profile-template.md`.

The profile must contain:

- Extracted date and sample count
- Chinese fingerprint (if applicable)
- English fingerprint (if applicable)
- Cross-lingual consistency notes
- AI-distinguishability signals to preserve
- Rewriting guidelines for `petfish-style-rewriter`

## Output Location

The qualitative profile is written to:

```text
.petfish/style-profile.md
```

This file is project-local and private to the user. It is the contract between `style-extractor` and `petfish-style-rewriter`.

## Integration with petfish-style-rewriter

`petfish-style-rewriter` loads `.petfish/style-profile.md` at runtime when available. If the profile exists, the rewriter:

- Uses the user's preferred sentence-length target and burstiness level.
- Preserves signature phrases and pronoun choices.
- Mirrors the user's argumentation structure and transition style.
- Respects the register map.
- Avoids adding patterns listed in the profile's `DON'T add` section.

If no profile exists, `petfish-style-rewriter` falls back to the default Petfish style.

## Anti-patterns

- **Inventing style features without evidence**: claiming the user prefers a phrase that does not appear in the samples.
- **Averaging away register variation**: collapsing formal and casual samples into one undifferentiated profile.
- **Treating human imperfection as a bug**: burstiness, minor asymmetry, and idiosyncratic connectors are human signals to preserve.
- **Omitting the rewriting guidelines section**: the profile is useless to the rewriter without explicit DO/DON'T rules.
- **Hardcoding a persona**: the template must remain generic; only values derived from the samples are filled in.
- **Skipping Stage 1**: relying only on LLM impression without quantitative anchors produces inconsistent profiles.

## Handoff & Boundaries

### This skill owns

- Collecting or confirming writing sample paths.
- Converting PDF/DOCX samples to Markdown via `doc-reader`.
- Computing quantitative style metrics.
- Synthesizing metrics and sample evidence into `.petfish/style-profile.md`.
- Updating an existing profile when new samples are provided.

### This skill does not own

- Rewriting the user's text → `petfish-style-rewriter`
- Detecting AI-generated text → not supported
- General document conversion without style analysis → `doc-reader`
- Cross-document series-style governance → `series-style-governor`

## Must Do

- Verify at least 3 samples before extraction.
- Convert PDF/DOCX to Markdown before analysis.
- Run `scripts/analyze_style.py` and include its metrics in the final profile.
- Write the profile to `.petfish/style-profile.md`.
- Keep the profile generic in structure but specific in values.
- Preserve human imperfections as positive signals.

## Must Not Do

- Do not rewrite, edit, or polish the samples.
- Do not hardcode a specific user's style into the template.
- Do not produce detection or rewriting capabilities inside this skill.
- Do not place the generated profile inside the skill pack directory.
- Do not skip the quantitative stage.

## References

- `references/extraction-dimensions.md` — dimension definitions and interpretation
- `references/style-profile-template.md` — output contract template
- `scripts/analyze_style.py` — stdlib-only quantitative analyzer
