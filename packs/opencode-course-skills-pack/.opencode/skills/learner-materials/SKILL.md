---
name: learner-materials
description: Learner-facing course assets such as handouts, reading packs, worksheets,
  pre-class guides, post-class exercises, glossaries, or concise recap notes.
license: Proprietary
compatibility: Designed for OpenCode. Assumes repo-local `.opencode/skills` discovery
  and standard read/edit/bash tools; optional scripts should run through a repo-local uv environment; requires uv and Python 3.11+.
metadata:
  pack: opencode-course-skills
---

# Purpose

Produce materials that help learners prepare, follow, and review the course.

# Learner-facing principles

- clarity over completeness
- guidance over internal commentary
- progressive difficulty
- visible takeaways
- no instructor-only information

# Common deliverables

- pre-read
- class handout
- worksheet
- glossary
- recap sheet
- exercise sheet
- FAQ

# Review checks

- Is the language accessible to the target learner?
- Are objectives and expected actions clear?
- Are references to unavailable teacher materials removed?
- Is the material useful outside the live lecture moment?

# Gotchas

- Do not leak answer keys.
- Do not dump raw source notes on the learner.
- Do not assume prior context that was never introduced.
- Do not overload one handout with multiple unrelated purposes.

See `assets/learner-pack-template.md`.
