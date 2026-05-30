---
name: series-style-governor
description: 系列文档风格一致性治理。当用户要求跨文档统一风格、术语、命名和排版时激活。Use when the user is writing a series of books, chapters, long-form articles, course materials, whitepapers, or Markdown documents and wants to keep style, terminology, naming conventions, section structure, and Markdown layout consistent. Triggers on: 系列风格, 跨文档一致性, 风格画像, 术语漂移, 排版漂移, 风格归一化, style profile, terminology drift, layout drift, style audit, series consistency, reference style, naming rules. Extract a style profile from a reference file or the first document. Audit, report, and optionally rewrite targets to match the baseline while preserving facts and author intent.
license: MIT
compatibility: opencode; requires Python 3.10+ for bundled scripts; uv is recommended but python3 also works.
metadata:
  version: "0.1.0"
  audience: writers, researchers, course authors, technical authors
  maintainer: petfish-skills
---

# Series Style Governor

## Purpose

Use this skill to govern consistency across a series of Markdown documents, such as books, chapters, course materials, technical manuals, research notes, long-form essays, and whitepapers.

This skill does not merely polish prose. It builds and applies a series-level style contract covering:

- narrative structure
- terminology and aliases
- naming conventions
- heading hierarchy
- Markdown layout
- citation and reference style
- Chinese-English typography
- rewrite safety boundaries

The central principle is: **unify without flattening**. Preserve the author's concepts, claims, factual meaning, and argumentative intent while reducing style drift across the series.

## When to activate

Activate this skill when the user asks to:

- unify style across a book series or chapter collection
- use one Markdown file as a reference style for others
- make several articles look like the same series
- check terminology drift, naming inconsistency, or layout inconsistency
- rewrite a Markdown chapter to match another chapter's style
- build or update a style guide from existing Markdown
- maintain series-level consistency in course, research, strategy, or whitepaper projects

Do not activate this skill for one-off copy editing unless the user explicitly mentions series consistency, reference style, naming rules, or Markdown layout governance.

## Baseline selection

1. If the user specifies a reference Markdown file, use that file as the baseline.
2. If the user specifies a reference directory, infer the main Markdown file from `README.md`, `index.md`, or the first numbered file.
3. If the user does not specify a baseline, use the first Markdown file in the target series by filename ordering.
4. Never overwrite the baseline file unless the user explicitly requests it.
5. If later chapters appear structurally more mature than the baseline, report this and suggest a baseline upgrade instead of silently changing the baseline.

Supported baseline modes:

- `fixed`: always use the specified baseline.
- `first-file`: use the first Markdown file as the default baseline.
- `evolving`: recommend style-profile updates when later files establish better conventions; require user confirmation before changing the profile.

## Standard workflow

1. Identify baseline and target files.
2. Create or update `.series-style/style-profile.json` from the baseline.
3. Create or update `.series-style/termbase.yaml` when terminology can be inferred or supplied.
4. Audit target files against the style profile.
5. Produce an audit report before large-scale rewriting.
6. If the user requested rewriting, produce a conservative rewrite plan and apply only safe transformations.
7. Save rewritten files separately unless the user explicitly asks to overwrite originals.
8. Produce a diff-oriented change report and unresolved issues list.

## Output modes

### Audit only

Use this when the user asks to inspect, compare, check, review, or report style differences.

Produce:

- `outputs/style-audit-report.md`
- `outputs/term-drift-report.md` when terminology drift exists
- `outputs/layout-drift-report.md` when layout drift is significant

### Rewrite plan

Use this before substantial rewriting or when the user wants control over changes.

Produce:

- `outputs/rewrite-plan.md`
- per-file risk notes
- changes grouped by safe, review-needed, and blocked

### Apply rewrite

Use this when the user explicitly asks to rewrite or normalize target files.

Produce:

- rewritten Markdown files under `outputs/rewritten/` by default
- `outputs/diff-report.md`
- `outputs/unresolved-issues.md`

## Non-negotiable rules

- Do not introduce new facts.
- Do not remove citations, footnotes, links, or reference entries.
- Do not alter technical claims unless the user asks for technical correction.
- Do not turn the author's voice into generic AI prose.
- Do not collapse distinct concepts merely because their terms look similar.
- Preserve original argument intent, stance, and conclusion.
- Preserve Markdown heading hierarchy unless it clearly violates the baseline structure.
- For Chinese technical writing, default to no spaces between Chinese text and English terms, e.g. `Webhook挂载`, `Git提交`, `AI安全`, unless the baseline consistently uses another convention.
- If a target document has a better structure than the baseline, report it instead of downgrading it.
- If a rewrite might change meaning, mark it as `review-needed` instead of applying it silently.

## Required analysis dimensions

When auditing or rewriting, evaluate these dimensions:

1. **Structure consistency**: heading depth, section sequence, numbered sections, intro and conclusion pattern.
2. **Narrative consistency**: whether the document follows the same exposition pattern, such as background → problem → analysis → proposal → summary.
3. **Terminology consistency**: preferred terms, aliases, forbidden terms, abbreviation definitions.
4. **Naming consistency**: file names, chapter titles, figure/table names, module names, concept names.
5. **Markdown layout**: blank lines, lists, tables, fenced code blocks, blockquotes, images, references.
6. **Citation style**: link placement, footnote style, reference list format.
7. **Chinese-English typography**: CJK-English spacing, full-width/half-width punctuation, acronym casing.
8. **Style drift**: sudden changes in formality, marketing tone, casual tone, academic tone, or sentence density.
9. **Rewrite risk**: places where style correction may affect facts, claims, or author intent.

## Tool and script defaults

Prefer the bundled scripts for mechanical checks, then use agent judgment for semantic assessment and rewriting.

Available scripts:

- `scripts/extract_style_profile.py`: extract a baseline style profile from Markdown.
- `scripts/audit_series_style.py`: audit Markdown files against the style profile.
- `scripts/normalize_terms.py`: detect and optionally normalize terminology aliases.
- `scripts/rewrite_to_style.py`: create conservative rewrite drafts from audit findings.
- `scripts/diff_report.py`: generate a Markdown diff report between source and rewritten files.

Run with `uv` when available:

```bash
uv run scripts/extract_style_profile.py --baseline chapters/01-intro.md --output .series-style/style-profile.json
```

Fallback:

```bash
python3 scripts/extract_style_profile.py --baseline chapters/01-intro.md --output .series-style/style-profile.json
```

## Reference loading policy

Load references only when needed:

- Read `references/style-profile-schema.md` when generating or editing `.series-style/style-profile.json`.
- Read `references/series-style-rules.md` when deciding what counts as style drift.
- Read `references/markdown-layout-rules.md` when checking Markdown formatting.
- Read `references/naming-convention-rules.md` when resolving terminology, filenames, module names, or chapter names.
- Read `references/rewrite-boundaries.md` before rewriting user content.

## Recommended project files

Create these files in the user's project when running the skill:

```text
.series-style/
├── style-profile.json
├── termbase.yaml
├── baseline.md
└── decisions.md
outputs/
├── style-audit-report.md
├── rewrite-plan.md
├── diff-report.md
└── unresolved-issues.md
```

`decisions.md` records confirmed style decisions, especially when the user overrides the baseline.

## Conservative rewrite policy

Apply automatically safe changes only:

- heading numbering format
- terminology alias replacement when unambiguous
- CJK-English spacing normalization
- Markdown blank-line normalization
- list marker consistency
- table title and figure title consistency
- repeated phrase cleanup when meaning is unchanged

Require review for:

- sentence restructuring that changes emphasis
- replacing a conceptual term with a near-synonym
- moving paragraphs across sections
- changing conclusions or recommendations
- deleting examples
- changing citations
- rewriting technical definitions

Block changes when:

- the source meaning is unclear
- the target style conflicts with factual precision
- the baseline appears internally inconsistent
- the user asks for global overwrite but target files include uncommitted or unknown changes

## Report template

When producing an audit report, use this structure:

```markdown
# Series Style Audit Report

## Executive summary
[Short summary of overall consistency and major risks.]

## Baseline
- Baseline file: `[path]`
- Baseline mode: `[fixed | first-file | evolving]`
- Style profile: `[path]`

## Overall findings
| Dimension | Status | Notes |
|---|---:|---|
| Structure | Pass/Warning/Fail | ... |
| Terminology | Pass/Warning/Fail | ... |
| Naming | Pass/Warning/Fail | ... |
| Markdown layout | Pass/Warning/Fail | ... |
| Chinese-English typography | Pass/Warning/Fail | ... |
| Rewrite risk | Low/Medium/High | ... |

## File-level findings

### `[file]`
- Structure drift:
- Term drift:
- Layout drift:
- Recommended action:

## Safe automatic fixes

## Review-needed changes

## Blocked changes

## Suggested style decisions
```

## Gotchas

- Do not confuse “style consistency” with “same wording.” Similar structure is desirable; identical phrasing is not.
- A later file may be a better style source than the first file. Recommend baseline evolution when appropriate.
- Technical series often require term precision over prose elegance. Do not sacrifice conceptual accuracy for stylistic smoothness.
- In Chinese technical writing, avoid adding spaces around English acronyms unless the baseline consistently requires it.
- Detect and preserve deliberate variation, such as chapter-specific methods, examples, or audience level.

## Handoff & Boundaries

This skill owns:
- Cross-document style consistency auditing
- Style profile extraction and management
- Conservative mechanical rewriting for style normalization
- Terminology drift detection and normalization

This skill does not own:
- Single-document copy editing → handoff to petfish-style-rewriter
- Long-form writing workflow (fat/slim) → handoff to fat-slim-writer
- Research note capture or citation management → handoff to research-note-capture
- Course content structure → handoff to course-content-authoring
- Markdown format-only fixes without series context → handoff to markdown-course-writing

Composition rules:
- Can be composed with petfish-style-rewriter for post-normalization polish
- Should run before fat-slim-writer when both are needed (normalize first, then write)
