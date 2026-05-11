---
name: instructor-reference-materials
description: Instructor-only assets such as teaching notes, speaking points, timing
  guidance, answer keys, discussion prompts, demo cues, or delivery risk reminders.
license: Proprietary
compatibility: Designed for OpenCode. Assumes repo-local `.opencode/skills` discovery
  and standard read/edit/bash tools; optional scripts should run through a repo-local uv environment; requires uv and Python 3.11+.
metadata:
  pack: opencode-course-skills
---

# Purpose

Create materials that help instructors deliver the course consistently and confidently.

# Typical content

- chapter teaching notes
- talk tracks/speaking points
- timing suggestions
- emphasis cues
- demo reminders
- likely learner questions
- answer keys
- fallback paths when time runs short

# Required behavior

Always keep instructor-only content separate from learner-facing material.

For each teaching unit, cover:

1. objective
2. what to emphasize
3. where learners struggle
4. how to explain it
5. how to pace it
6. what to skip if needed
7. answers or evaluation criteria if relevant

# Gotchas

- Do not write a teleprompter unless the user explicitly wants that style.
- Do not mix confidential instructor notes into learner handouts.
- Do not ignore pacing; teaching notes without timing are often incomplete.
- Do not provide answer keys without mapping them to the associated activity.

See `assets/instructor-guide-template.md`.
