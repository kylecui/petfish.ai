# series-style-governor

> Pack: **style-governor**

系列文档风格一致性治理。跨文档统一术语、命名、排版和叙事结构。从参考文件提取风格画像，审计目标文档，检测术语漂移和排版漂移，生成保守改写草稿。Use when writing a series of books, chapters, course materials, whitepapers and want consistent style, terminology, naming, layout. Triggers: 系列风格, 跨文档一致性, 风格画像, 术语漂移, 排版漂移, style profile, terminology drift, layout drift, series consistency, style audit.

**Compatibility:** opencode; requires Python 3.10+ for bundled scripts; uv is recommended but python3 also works.

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


*... (187 more lines in full SKILL.md)*
