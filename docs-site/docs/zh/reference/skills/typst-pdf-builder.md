# typst-pdf-builder

> 所属包: **typst**

>

**兼容性:** Requires pandoc, typst, Python 3.10+, and draw.io CLI for diagrams.

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

*... (完整 SKILL.md 中还有 97 行)*
