---
name: course-content-authoring
description: Create, revise, expand, compress, or review course chapter content, including explanations, examples, transitions, key takeaways, and teaching flow.
license: Proprietary
compatibility: Designed for OpenCode. Assumes repo-local `.opencode/skills` discovery
  and standard read/edit/bash tools; optional scripts should run through a repo-local uv environment; requires uv and Python 3.11+.
metadata:
  pack: opencode-course-skills
---

# Purpose

Write or refine lesson-level course content.

# Default content structure

For each chapter or lesson, cover:

1. teaching objective
2. key terms/concepts
3. explanation path
4. examples or demonstrations
5. common misunderstandings
6. summary
7. optional reflection/exercise

# Authoring behavior

- Write for the target audience's level, not for the source author's level.
- Prefer a teaching progression: definition -> mechanism -> example -> boundary -> takeaway.
- Keep conceptual accuracy and teaching usability aligned.
- Mark places that need diagrams, demos, or labs.

# Review behavior

When reviewing existing content, look for:

- concept gaps
- sequence problems
- weak transitions
- missing examples
- excessive density
- lack of learner checkpoints

# Gotchas

- Do not duplicate the outline file inside every chapter.
- Do not let examples become detached from the core point.
- Do not bury the most important explanation after too much setup.
- Do not assume the chapter is teachable just because it is technically correct.

See:
- `assets/lesson-template.md`
- `references/teaching-flow-patterns.md`
