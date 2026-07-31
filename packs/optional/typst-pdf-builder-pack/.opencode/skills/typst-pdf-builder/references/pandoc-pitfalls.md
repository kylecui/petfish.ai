# Pandoc Pitfalls

This document lists the pandoc+Typst failure modes that the
`typst-pdf-builder` pipeline works around. Each pitfall includes the symptom,
the root cause, and the fix applied by the scripts.

---

## 1. `---` Immediately Before a Heading Becomes a False Table

### Symptom

A horizontal rule followed directly by a heading causes pandoc to treat the
`---` as a single-column table separator. The rest of the chapter may be
rendered as a Typst table or mangled.

### Root cause

Pandoc's `simple_tables` extension allows a table like:

```markdown
---
Content
```

When `---` appears immediately before `## Heading`, pandoc interprets it as a
table delimiter line rather than a horizontal rule.

### Fix

Always place a blank line between `---` and the next heading:

```markdown
---

## 1.6 Title
```

`build_pdf.py` does not rewrite this case; the source must be correct.

---

## 2. `<` in Code Blocks Truncates Lines

### Symptom

Code that contains `<` (for example, `if x < 30`) is truncated or rendered
incorrectly because pandoc treats `<` as the start of an inline HTML tag.

### Root cause

Pandoc parses markdown with the `raw_html` extension enabled by default. In
fenced code blocks it usually leaves HTML alone, but angle brackets can still
leak into the Typst output in unexpected ways.

### Fix

`preprocess_md()` replaces the characters before pandoc sees them:

```python
line = line.replace("<=", "≤").replace(">=", "≥")
line = line.replace("<", "＜").replace(">", "＞")
```

The full-width angle brackets render correctly and are not interpreted as
HTML.

---

## 3. Code Block Fence Imbalance Leaks Content

### Symptom

A code block with mismatched opening and closing fences causes pandoc to
emit a Typst `raw` block that never closes. Subsequent paragraphs may be
swallowed into the code block.

### Root cause

Typst expects balanced triple-backtick fences. Pandoc sometimes emits an
opening fence for a new block without a closing fence for the previous one.

### Fix

`fix_typst_paths()` parses fence lines and inserts missing closing fences:

```python
if in_raw:
    lang = stripped[3:].strip()
    if lang:
        result.append("```")  # close the previous block
        result.append(line)    # then open the new block
```

A trailing closing fence is also appended if the file ends while still inside
a raw block.

---

## 4. Pandoc Span Tag Residuals

### Symptom

The Typst output contains fragments like `<span class="smallcaps">` or other
raw HTML tags that Typst does not understand.

### Root cause

Pandoc occasionally emits inline HTML span wrappers for formatting that has
no direct Typst equivalent.

### Fix

`fix_typst_paths()` strips any remaining HTML-like tags:

```python
content = re.sub(r"<[^>]+>", "", content)
```

This is safe because any intentional content has already been converted to
Typst syntax.

---

## 5. `#horizontalrule` Is Not Valid Typst

### Symptom

Pandoc emits `#horizontalrule` for Markdown `---`, but Typst has no such
function. The compiler fails or emits an error.

### Root cause

Pandoc's Typst writer uses a function name that does not exist in current
Typst versions.

### Fix

`fix_typst_paths()` replaces the directive with an equivalent visual
centered line:

```python
content = content.replace(
    "#horizontalrule",
    "#v(0.5em)\n#align(center)[#line(length: 30%, stroke: 0.5pt + gray)]\n#v(0.5em)",
)
```

---

## 6. Default Figure Caption Format Adds an Unwanted Prefix

### Symptom

Image captions render as `图 1 — title` instead of the desired `图X.Y. title`
format.

### Root cause

Typst's default `figure.caption` show rule prefixes the label with the
figure counter and an em dash.

### Fix

The template overrides the default caption renderer and builds the label
manually:

```typst
show figure.caption: it => it.body

show figure.where(kind: image): it => {
  // ...
  context {
    let ch = counter("chapter").get().first() - 1
    let fig = counter(figure.where(kind: image)).get().at(0)
    align(center)[图#ch.#fig. #it.caption]
  }
}
```

---

## 7. Heading Counter Does Not Auto-Increment in Custom Show Rules

### Symptom

All figures are numbered as `图0.Y.` or the chapter number never advances,
even though headings render correctly.

### Root cause

When a custom `show heading.where(level: 1)` rule is installed, Typst's
native `heading` counter stops auto-incrementing inside that rule.

### Fix

Maintain a separate `chapter` counter and update it explicitly in the H1
show rule:

```typst
show heading.where(level: 1): it => {
  counter("chapter").update(c => c + 1)
  counter(figure.where(kind: image)).update(0)
  // ... render heading ...
}
```

The figure numbering code then reads this counter instead of the native
heading counter.
