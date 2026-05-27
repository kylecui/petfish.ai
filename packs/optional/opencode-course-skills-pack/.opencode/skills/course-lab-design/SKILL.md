---
name: course-lab-design
description: Create, modify, review, or operationalize course labs, exercises, demos,
  or hands-on projects, including objectives, environment, steps, validation, troubleshooting,
  and answer keys.
license: Proprietary
compatibility: Designed for OpenCode. Assumes repo-local `.opencode/skills` discovery
  and standard read/edit/bash tools; optional scripts should run through a repo-local uv environment; requires uv and Python 3.11+.
metadata:
  pack: opencode-course-skills
---

# Purpose

Design hands-on labs that are teachable, executable, and reviewable.

# Lab design model

Each lab should explicitly define:

1. objective
2. prerequisites
3. environment
4. inputs/files/tools
5. procedure
6. expected result
7. validation method
8. troubleshooting
9. instructor answer/reference path

# Review checks

- Can a learner realistically complete it in the allocated time?
- Are setup steps isolated from learning steps?
- Is success observable?
- Are common failure modes covered?
- Is the answer key separated from the learner guide?

# Output split

Prefer two linked artifacts:

- learner lab guide
- instructor answer key/reference notes

# Gotchas

- Do not turn environment setup into the main learning burden unless that is intentional.
- Do not define a lab objective that cannot be validated.
- Do not hide required files, credentials, or dependencies.
- Do not mix official answers into learner-facing instructions.

See:
- `assets/lab-template.md`
- `references/lab-review-checklist.md`
