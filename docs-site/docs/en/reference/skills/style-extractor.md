# style-extractor

> Pack: **petfish**

Extract personal writing style from samples to create a style profile. Analyzes sentence patterns, vocabulary preferences, argumentation structure, punctuation habits, tone markers, and AI-distinguishability signals across Chinese and English. Use when "提炼我的写作风格", "extract my style", "create style profile", "analyze my writing", "风格画像", "个性化风格提取", or when setting up petfish-style-rewriter for the first time.

**Compatibility:** opencode

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

*... (146 more lines in full SKILL.md)*
