---
name: typst-pdf-builder
description: >
  Build PDF from Markdown chapters when the user wants to build PDF, generate PDF,
  typeset, run a PDF pipeline, use typst, convert pandoc to PDF, or produce Chinese
  textbook 教材排版 output. Handles draw.io diagram export, per-chapter figure/table
  numbering, code block escaping, compact Chinese-English typography, and
  thuthesis-compliant formatting.
triggers: build pdf, generate pdf, 排版, 构建pdf, typst, pandoc to pdf, 教材排版, pdf pipeline, typeset
license: MIT
compatibility: Requires pandoc, typst, Python 3.10+, and draw.io CLI for diagrams.
metadata:
  author: sisyphus
  version: 1.0.0
---

# typst-pdf-builder

## Role

Build stable, publication-ready PDF documents from Markdown sources using a
pandoc + Typst pipeline. The skill preserves Chinese-English mixed typography,
per-chapter figure/table numbering, draw.io diagram export, and code-block
escaping that the raw pandoc+Typst combination does not handle automatically.

## When to Use

- User says "build PDF", "generate PDF", "排版", "构建PDF", "typst", "pandoc to PDF", "教材排版", "pdf pipeline", or "typeset".
- User needs a Chinese textbook or technical manual PDF from Markdown chapters.
- User needs per-chapter figure/table numbering, code-block escaping, or draw.io diagram batch export.
- User wants to replicate a battle-tested Markdown-to-PDF workflow in a new project.

## When NOT to Use

- User wants a single-page document or slide deck → use `ppt-writer` or `markdown-course-writing`.
- User wants a non-Chinese, non-textbook layout without thuthesis-style constraints → use plain pandoc or typst directly.
- User only wants to export one draw.io diagram → use `drawio-radar-chart` or draw.io CLI directly.

## Critical Domain Rules

### Rule 1: One source of truth for diagrams

Diagrams live in `diagrams-source/M#/` as editable `.drawio` files.
The PDF build reads PNG exports from `diagrams-export/M#/`.
Do not maintain a third copy inside the content directory; the build script
rewrites Markdown image paths to point at the export directory.

### Rule 2: Tables must carry machine-readable captions

Before building PDF, run `add_table_captions.py` so every table ends with a
`**表N  标题**` line. `build_pdf.py` later rewrites that line into the
per-chapter `表X.Y.` format.

### Rule 3: Code blocks need angle-bracket escaping

Inside code blocks, replace `<=`/`>=` with `≤`/`≥` and standalone `<`/`>` with
full-width `＜`/`＞` before pandoc sees them, or pandoc may truncate lines that
look like HTML tags.

### Rule 4: Per-chapter numbering requires the custom `chapter` counter

Typst's native `heading` counter does not auto-increment inside custom `show`
rules. The template uses a manual `counter("chapter")` and resets the figure
counter on every H1. Captions render as `图X.Y.` and `表X.Y.`.

### Rule 5: First-line indent is inserted by post-processing

`book-template.typ` disables `first-line-indent` and `build_pdf.py` inserts
`#h(2em)` before each paragraph that follows a heading, figure, table, or blank
line. Lists and directive lines are skipped.

## Decision Points

1. **Is this a new project or an existing one?**
   - New project: copy `templates/book-template.typ` and run `scripts/bootstrap.py` (if available) or follow the setup workflow.
   - Existing project: point `--content-dir`, `--output-dir`, and `--template` at existing locations.
2. **Full book or per-chapter pilot?**
   - Full book: omit `--ch` and get a single PDF with title page and outline.
   - Pilot one chapter: `--ch 0`.
   - All chapters individually: `--per-chapter`.
3. **Are diagrams already exported?**
   - If not, run `export_drawio.py` before `build_pdf.py`.
4. **Do tables already have captions?**
   - If not, run `add_table_captions.py` first.

## Execution Modes

- **Interactive / manual**: User runs the scripts in order and inspects output.
- **CI / automated**: A wrapper script calls `add_table_captions.py`, then `export_drawio.py`, then `build_pdf.py --per-chapter`.
- **Agent-driven**: The skill can copy the template, discover chapters, and run the pipeline when the user asks for PDF output.

## Output Contracts

When this skill runs to completion it must produce:

1. **PDF file(s)** in the configured output directory:
   - `{book_title}.pdf` for a full build.
   - `Ch{NN}_pilot.pdf` for a single-chapter build.
   - `per-chapter/Ch{NN}.pdf` for each chapter when `--per-chapter` is used.
2. **Intermediate `.typ` files** in the content directory, one per Markdown chapter, plus `book.typ`.
3. **PNG exports** in `diagrams-export/M#/` if `export_drawio.py` was invoked.
4. **Table caption lines** inserted into the source Markdown by `add_table_captions.py`.

## Workflow

1. **Install prerequisites**: pandoc, typst, Python 3.10+, draw.io CLI.
2. **Prepare directory layout**:
   - `content/Ch*_*.md` — Markdown chapters.
   - `diagrams-source/M#/*.drawio` — editable diagrams.
   - `diagrams-export/M#/*.png` — exported diagram PNGs.
   - `handbook-layout/book-template.typ` — copy from `templates/`.
   - `print-ready/` — PDF output.
3. **Add table captions**:
   ```powershell
   python .opencode/skills/typst-pdf-builder/scripts/add_table_captions.py --dir content
   ```
4. **Export draw.io diagrams**:
   ```powershell
   python .opencode/skills/typst-pdf-builder/scripts/export_drawio.py --source-dir diagrams-source --output-dir diagrams-export
   ```
5. **Configure the build** by editing `book-template.typ` top variables and by passing `--title`/`--subtitle` to `build_pdf.py`.
6. **Build the PDF**:
   ```powershell
   python .opencode/skills/typst-pdf-builder/scripts/build_pdf.py --root . --title "Book Title" --subtitle "Subtitle"
   ```
   Pilot one chapter:
   ```powershell
   python .opencode/skills/typst-pdf-builder/scripts/build_pdf.py --ch 0
   ```
   Build every chapter separately:
   ```powershell
   python .opencode/skills/typst-pdf-builder/scripts/build_pdf.py --per-chapter
   ```
7. **Verify**: open the PDF and check figure/table numbering, fonts, and margins.

## Anti-Patterns

- Running `build_pdf.py` before captions are added → tables render without `表X.Y.` labels.
- Exporting draw.io diagrams to the wrong directory → missing-image placeholders appear in the PDF.
- Writing `---` immediately before a heading without a blank line → pandoc treats `---` as a table delimiter and corrupts the chapter.
- Leaving raw `<`/`>` in code blocks → pandoc truncates lines.
- Editing `book-template.typ` show/set rules without updating `references/typography-spec.md` → style drift.
- Maintaining two copies of diagrams in `content/diagrams/` and `diagrams-export/` → stale images.

## Handoff & Boundaries

**This skill owns**:
- Markdown-to-Typst-to-PDF pipeline execution.
- Chinese-English mixed-text post-processing.
- Per-chapter figure/table numbering.
- draw.io batch export for textbook diagrams.
- thuthesis-style typography parameter reference.

**This skill does NOT own**:
- Writing or editing course content (use `course-content-authoring`).
- Draw.io diagram design beyond batch export (use `drawio-course-diagrams` or `drawio-radar-chart`).
- Generic Markdown linting or content QA (use `course-quality-assurance`).
- Source citation auditing (use `research-citation-auditor`).

**Adjacent skills**:
- `course-content-authoring` — create textbook chapters.
- `drawio-course-diagrams` — design general course diagrams.
- `markdown-course-writing` — polish Markdown before PDF build.
- `course-quality-assurance` — review PDF against delivery criteria.

## Must Do

- Read the source `build_pdf.py`, `book-template.typ`, `add_table_captions.py`, and `排版参数规范.md` before modifying anything.
- Keep all processing logic in `build_pdf.py` identical when generalizing paths.
- Run `add_table_captions.py` before every build if tables may have changed.
- Run `export_drawio.py` after any diagram source changes.
- Add pandoc to PATH on Windows before running the scripts.
- Flush stdout/stderr and call `os._exit(0)` at the end of Windows builds to avoid hangs.

## Must Not Do

- Do not hardcode project paths in the generalized scripts; use `--root` or script-location detection.
- Do not skip the table-caption or draw.io-export steps and expect perfect output.
- Do not change Typst show/set rules when only the title or subtitle needs changing.
- Do not use emojis or decorative characters in build logs or documentation.
- Do not commit PDFs and intermediate `.typ` files to version control.

## References

- `references/typography-spec.md` — authoritative font, spacing, and sizing parameters.
- `references/format-conventions.md` — figure/table numbering, code escaping, compact CN-EN rules.
- `references/pandoc-pitfalls.md` — known pandoc+Typst traps and fixes.
- `references/thuthesis-compliance.md` — mapping to thuthesis v7.7.1 requirements.
- `references/directory-conventions.md` — where source, export, and output files live.
- `templates/book-template.typ` — reusable Typst template.
- `scripts/build_pdf.py` — main build orchestrator.
- `scripts/add_table_captions.py` — table caption generator.
- `scripts/export_drawio.py` — draw.io batch exporter.
