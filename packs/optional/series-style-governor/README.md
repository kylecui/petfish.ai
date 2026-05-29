# series-style-governor

`series-style-governor` is an OpenCode-compatible skill for governing style consistency across a series of Markdown documents.

It extracts a baseline style profile, audits target Markdown files, detects terminology and layout drift, and creates conservative rewrite drafts while preserving facts, claims, citations, and authorial intent.

## Install

Project-level install:

```bash
mkdir -p .opencode/skills
cp -r series-style-governor .opencode/skills/series-style-governor
```

Global install:

```bash
mkdir -p ~/.config/opencode/skills
cp -r series-style-governor ~/.config/opencode/skills/series-style-governor
```

## Basic usage

Extract a style profile:

```bash
python3 scripts/extract_style_profile.py \
  --baseline chapters/01-intro.md \
  --output .series-style/style-profile.json
```

Audit a series:

```bash
python3 scripts/audit_series_style.py \
  --profile .series-style/style-profile.json \
  --targets "chapters/*.md" \
  --output outputs/style-audit-report.md
```

Detect term drift:

```bash
python3 scripts/normalize_terms.py \
  --termbase .series-style/termbase.yaml \
  --targets "chapters/*.md" \
  --output outputs/term-drift-report.md
```

Create conservative rewrite drafts:

```bash
python3 scripts/rewrite_to_style.py \
  --profile .series-style/style-profile.json \
  --targets "chapters/*.md" \
  --output-dir outputs/rewritten
```

Generate a diff report:

```bash
python3 scripts/diff_report.py \
  --before chapters \
  --after outputs/rewritten \
  --output outputs/diff-report.md
```

## Design notes

- The baseline file is not overwritten.
- Rewritten files are saved separately by default.
- Mechanical fixes are intentionally conservative.
- Semantic rewriting should be performed by the agent after reading `references/rewrite-boundaries.md`.
- Default Chinese technical typography uses no spaces between Chinese and English terms, e.g. `Webhook挂载`, `Git提交`, `AI安全`.
