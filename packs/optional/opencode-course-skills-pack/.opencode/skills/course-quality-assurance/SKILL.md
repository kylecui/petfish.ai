---
name: course-quality-assurance
description: 'Structured course QA: completeness checks, consistency review, pedagogical
  review, lab readiness checks, artifact coverage, issue logging, or release readiness
  assessment.'
license: Proprietary
compatibility: Designed for OpenCode. Assumes repo-local `.opencode/skills` discovery
  and standard read/edit/bash tools; optional scripts should run through a repo-local uv environment; requires uv and Python 3.11+.
metadata:
  pack: opencode-course-skills
---

# Purpose

Audit the quality of a course project before release or before the next production stage.

# QA dimensions

Review along these axes:

- scope completeness
- structural consistency
- learning-objective alignment
- content clarity
- lab executability
- learner/instructor material separation
- formatting and naming consistency
- release readiness

# Issue classification

Tag issues as one or more of:

- blocker
- major
- minor
- suggestion

And also by class:

- factual
- structural
- pedagogical
- operational
- formatting

# QA output structure

```markdown
# QA Review

## Scope reviewed
## Findings summary
## Detailed issues
## Risk assessment
## Release recommendation
```

# Review behavior

- Cite the artifact or section where each issue appears.
- Prefer evidence-based findings over vague quality opinions.
- Distinguish between “not ideal” and “not releasable”.

# Gotchas

- Do not convert QA into silent editing.
- Do not file cosmetic nits as blockers.
- Do not approve release if critical labs are unverified.
- Do not overlook cross-file inconsistency.

See:
- `assets/qa-checklist.md`
- `references/severity-model.md`
