# course-lab-design

> Pack: **course**

Create, modify, review, or operationalize course labs, exercises, demos,

**Compatibility:** Designed for OpenCode. Assumes repo-local `.opencode/skills` discovery

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
