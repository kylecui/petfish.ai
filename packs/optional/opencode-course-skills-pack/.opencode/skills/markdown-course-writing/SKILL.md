---
name: markdown-course-writing
description: Polished Markdown artifacts for course plans, outlines, lesson notes, lab guides, learner handouts, instructor guides, QA/QC records, or course reports; also converts PDF/DOCX/images/notes into structured Markdown with normalized terms, explicit assumptions, and verification placeholders.
license: Proprietary
compatibility: Designed for OpenCode. Assumes repo-local `.opencode/skills` discovery
  and standard read/edit/bash tools; optional scripts should run through a repo-local uv environment; requires uv and Python 3.11+.
metadata:
  pack: opencode-course-skills
---

# Purpose

Produce durable Markdown artifacts for course development.

# Writing defaults

Use Markdown as the primary authoring format. Favor:

- stable heading hierarchy
- concise tables only when they help comparison
- ordered lists for procedures
- callouts only when the client supports them
- short sections that can be reorganized later

# Standard artifact shapes

Choose the closest template:

- development plan
- syllabus/outline
- lesson chapter
- lab guide
- learner handout
- instructor guide
- QA checklist
- QC report

# Required writing behavior

1. Start from the user's objective, not from a generic template.
2. Make titles operational and specific.
3. Separate:
   - scope
   - audience
   - prerequisites
   - main body
   - outputs
   - review points
4. Preserve explicit placeholders when facts are missing.
5. Keep references and assumptions visible rather than silently inventing detail.

# Formatting rules

- Use ATX headings (`#`, `##`, `###`).
- Avoid jumping heading levels.
- Prefer fenced code blocks with language tags where relevant.
- Use blockquotes only for source excerpts or mandated wording.
- Do not bury key conclusions in paragraphs longer than necessary.

# Conversion rules

When transforming content from PDF, DOCX, images, or notes:

- normalize terminology
- remove obvious duplication
- mark uncertain text as needing verification
- preserve source structure only when it helps the final artifact

# Gotchas

- Do not force every artifact into the same outline.
- Do not overuse tables for narrative teaching content.
- Do not mix learner-facing text with reviewer notes.
- Do not assume Markdown rendering extensions unless the environment clearly supports them.

See:
- `assets/markdown-style-guide.md`
- `assets/markdown-templates.md`
