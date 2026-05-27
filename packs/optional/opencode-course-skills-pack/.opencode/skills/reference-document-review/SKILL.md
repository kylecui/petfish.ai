---
name: reference-document-review
description: Read, normalize, compare, extract, or convert reference materials in PDF,
  Markdown, DOC, DOCX, images, slides, or mixed formats into course inputs.
license: Proprietary
compatibility: Designed for OpenCode. Assumes repo-local `.opencode/skills` discovery
  and standard read/edit/bash tools; optional scripts should run through a repo-local uv environment; requires uv and Python 3.11+.
metadata:
  pack: opencode-course-skills
---

# Purpose

Turn heterogeneous reference material into structured course-development inputs.

# Default intake workflow

1. Identify each source and its role:
   - authoritative source
   - rough draft
   - supporting example
   - visual reference
   - conflicting reference
2. Extract the useful material:
   - objectives
   - concepts
   - terminology
   - data points
   - examples
   - diagrams/tables
3. Normalize the extracted content into a course-ready note.
4. Flag uncertainty, OCR risk, or contradiction.
5. Route the cleaned result into the next relevant artifact.

# Review modes

- summary
- structured extraction
- comparison/diff
- lesson-input conversion
- issue spotting
- terminology normalization

# Expected output

When reading references for course work, prefer this structure:

```markdown
# Source Review

## Source inventory
## Key extracted points
## Reusable course material
## Conflicts / uncertainties
## Suggested downstream artifact
```

# Source handling rules

- Keep source facts separate from your suggestions.
- Preserve citations or file attribution when available.
- If a scan or image is ambiguous, mark it instead of guessing.
- When multiple references disagree, present the disagreement explicitly.

# Common source-specific defaults

- PDF: capture title, section structure, tables, and figures.
- DOC/DOCX: preserve editorial structure and tracked-intent where obvious.
- Markdown: preserve heading logic and embedded code blocks.
- Image: extract visible text, diagram meaning, and any labels that influence course design.

# Gotchas

- Do not silently merge conflicting source statements.
- Do not treat a marketing deck as authoritative technical truth.
- Do not rewrite source intent too early; first extract, then reinterpret.
- Do not discard appendices if they contain definitions or lab constraints.

See `assets/source-review-template.md`.
