# Format Conventions

This document describes the Markdown and Typst formatting conventions enforced
by the `typst-pdf-builder` pipeline.

---

## 1. Figure Numbering

Format: `图X.Y.` where `X` is the chapter number and `Y` is the figure index
inside that chapter.

### How it works

- The Typst template defines a custom `counter("chapter")`.
- On every H1 heading the template increments the chapter counter and resets
  the image figure counter:
  ```typst
  counter("chapter").update(c => c + 1)
  counter(figure.where(kind: image)).update(0)
  ```
- The caption show rule builds the label:
  ```typst
  let ch = counter("chapter").get().first() - 1
  let fig = counter(figure.where(kind: image)).get().at(0)
  align(center)[图#ch.#fig. #it.caption]
  ```
- The `-1` on the chapter counter is required because the counter is
  incremented before the H1 content is rendered.

### Markdown source

```markdown
![Figure caption text](diagrams/m0/fig0_1_overview.png)

Description paragraph that is merged into the caption block.
```

Do not write manual `**图X.Y**` labels; the pipeline generates them.

---

## 2. Table Numbering

Format: `表X.Y.` where `X` is the chapter number and `Y` is the table index
inside that chapter.

### How it works

1. `add_table_captions.py` scans each chapter for table blocks and appends a
   caption line after each table:
   ```markdown
   **表1  列1与列2对照**
   ```
2. `build_pdf.py` step 7 rewrites the caption line to a centered 9pt
   FangSong label with per-chapter numbering:
   ```typst
   #align(center)[#text(size: 9pt, font: ("Times New Roman", "FangSong"))[表X.Y. 列1与列2对照]]
   ```

Run `add_table_captions.py` before every build if tables may have changed.

---

## 3. Code Block Escaping

Inside fenced code blocks, the following character substitutions are applied
by `preprocess_md()` before pandoc sees the content:

| Original | Replacement | Reason |
|----------|-------------|--------|
| `<=` | `≤` | Avoid Typst/Unicode issues. |
| `>=` | `≥` | Avoid Typst/Unicode issues. |
| `<` | `＜` (full-width) | Prevent pandoc from parsing `<` as an HTML tag start, which truncates the line. |
| `>` | `＞` (full-width) | Prevent pandoc from parsing `>` as an HTML tag end. |

The same full-width substitution is applied to table rows.

---

## 4. List Indent Handling

Typst lists do not need a first-line indent. The `book-template.typ` show rules
for `list` and `enum` set `first-line-indent: 0em`.

`build_pdf.py` post-processing inserts `#h(2em)` at paragraph starts, but it
skips lines that begin with a list marker:

```regex
^[-*+]\s   # unordered list
^\d+[.)]\s # ordered list
```

This prevents list items from receiving an unwanted extra indent.

---

## 5. Compact Chinese-English Spacing

The `compact_cn_en()` function removes extra spaces between CJK characters and
Latin letters/digits while preserving the space after figure/table/section
numbering labels.

### Rules

- `AI模型`, `Token预算`, `Prompt技巧` — compact, no space.
- `图0.0 绪论`, `表4.1 工具`, `§0.1 概述` — keep the space after the number.
- Heading lines (`# ...`) are skipped so that section numbers keep their
  spacing.

### Implementation

A placeholder (`\x00`) temporarily protects the label-space before the
regexes run:

```python
PLACEHOLDER = "\x00"
text = re.sub(r'([图表§]\d+\.?\d*)\s+', lambda m: m.group(1) + PLACEHOLDER, text)
# ... remove spaces between CJK and Latin ...
text = text.replace('\x00', ' ')
```

---

## 6. Figure Caption Layout

A figure may have a short caption (from the image `alt` text) and a longer
description paragraph in the Markdown source. The pipeline merges the
description into the figure's `caption` block and separates the two with a
forced line break.

### Before post-processing

```typst
#figure(image("path", alt: "Caption title"),
  caption: [
    Caption title
  ]
)

#h(2em) Longer description text.
```

### After post-processing

```typst
#figure(image("path", alt: "Caption title"),
  caption: [
    Caption title
    #linebreak() Longer description text.
  ]
)
```

The `#linebreak()` keeps the title and description visually grouped while
allowing different runs of text inside the same caption block.

---

## 7. Table Column Auto-Sizing

Pandoc emits `columns: N` for Markdown tables. The pipeline rewrites this so
that the first column is `auto` and the remaining columns share the available
space with `1fr`.

### Rewrite rule

```typst
// Input from pandoc
columns: 4

// Output from build_pdf.py
columns: (auto, 1fr, 1fr, 1fr)
```

The first column is typically a header/narrow label column; the remaining
columns hold body content.

If pandoc emits explicit percentage widths, the pipeline also converts them
using the same `(auto, 1fr, ...)` pattern based on the number of `%` tokens.

---

## 8. Table Font Auto-Shrink

Wide tables with six or more columns are automatically rendered in a smaller
font to avoid overflowing the page.

### Rule

```typst
let n = if it.columns == auto { 2 } else { it.columns.len() }
let sz = if n > 5 { 8pt } else { 10.5pt }
let ld = if n > 5 { 12pt } else { 16pt }
```

- `n <= 5`: 10.5pt font, 16pt leading.
- `n > 5`: 8pt font, 12pt leading.

The font remains FangSong for Chinese and Times New Roman for Western text.

---

## 9. Table Breaking

Typst wraps table blocks in a `figure` by default, and that figure cannot
break across pages. The template unwraps table figures so long tables can
split naturally:

```typst
show figure.where(kind: table): it => {
    set par(first-line-indent: 0em)
    it.body
}
```

This keeps the table caption above the table but allows the table body to
span multiple pages.
