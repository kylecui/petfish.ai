# Thuthesis v7.7.1 Compliance Mapping

This document maps the `typst-pdf-builder` implementation to the
formatting requirements in thuthesis v7.7.1 (Tsinghua University graduate
thesis style). The goal is to stay close to the thuthesis specification
while keeping the pipeline simple enough for a textbook rather than a formal
thesis.

---

## Parameter Comparison

| Parameter | Thuthesis v7.7.1 | Our Implementation | Status |
|---|---|---|---|
| Page | A4, margin = 3cm | A4, margin = 3.0cm | Match |
| Body font | SimSun 12bp, leading 20bp | SimSun 12pt, leading 20pt | Match |
| H1 | sanhao (16bp) centered, beforeskip = 27bp, afterskip = 27bp | 16pt SimHei centered, v(24pt) / v(18pt) | Close (24 vs 27) |
| H2 | sihao (14bp), beforeskip = 24bp, afterskip = 6bp | 14pt SimHei, v(24pt) / v(6pt) | Match |
| H3 | 13bp, beforeskip = 12bp, afterskip = 6bp | 13pt SimHei, v(12pt) / v(6pt) | Match |
| H4 | 12bp, beforeskip = 12bp, afterskip = 6bp | 12pt SimHei, v(12pt) / v(6pt) | Match |
| Caption | 11bp / 14.3bp, labelsep = quad, skip = 6bp | 9pt FangSong, v(2pt) | Smaller font |
| Table | 11bp / 14.3bp, arraystretch = 1.42 | 10.5pt FangSong, leading = 16pt | Close |
| Code | — | Consolas 10pt, leading = 14pt | N/A (no code spec in thuthesis) |
| Math | abovedisplayskip = 6bp, below = 6bp | v(6pt) / v(6pt) | Match |
| Indent | autoindent = 2 (2 chars) | #h(2em) | Match |
| Headrule | 0.75bp on chapter pages | None | Simplified |

---

## Notes on Deviations

### H1 spacing (Close)

Thuthesis uses 27bp before and after the chapter heading. The template uses
24pt before and 18pt after because:

- 24pt keeps the heading visually centered without adding excessive white
  space on a textbook page.
- 18pt after the heading gives a tighter transition into the first paragraph.

Projects that need strict thuthesis spacing can change the `v(24pt)` and
`v(18pt)` values in `book-template.typ`.

### Caption font size (Deviation)

Thuthesis specifies 11bp (small 4) for captions. The pipeline uses 9pt
(small 5) because the textbook contains many figures with long captions and
small 5 keeps the caption block compact while still readable.

If strict compliance is required, change the caption `size` from `9pt` to
`11pt` in both `book-template.typ` and the table-caption rewrite rule in
`build_pdf.py`.

### Table font size (Close)

The implementation uses 10.5pt (size 5) instead of 11bp. The difference is
negligible in print and matches the textbook's more compact table style.
Wide tables automatically shrink to 8pt to avoid overflow.

### Headrule (Simplified)

Thuthesis places a thin horizontal rule in the page header of chapter-start
pages. The pipeline omits this rule because the textbook style uses a
minimal header with only the book title. Add a `#line` to the H1 show rule
if the rule is required.

### Code blocks

Thuthesis does not define a code block style. The pipeline uses Consolas
10pt with a light gray block, which is a common choice for technical
textbooks.

### Indent

`#h(2em)` approximates the thuthesis `autoindent = 2` (two characters). It is
inserted by post-processing rather than by Typst's built-in first-line
indent because Typst's built-in indent does not take effect after custom
headings and figures.

---

## When to Treat This as Compliant

For internal course materials and technical textbooks, the implementation is
sufficiently close to thuthesis v7.7.1 that most readers will not notice the
differences.

For formal thesis submission, manually adjust:

- H1 beforeskip to `v(27pt)`.
- Caption font size to `11pt`.
- Add chapter-page headrules.
