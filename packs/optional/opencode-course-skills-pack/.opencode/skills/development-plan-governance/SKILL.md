---
name: development-plan-governance
description: Create, revise, or review a course development plan, including milestones,
  owners, dependencies, deliverables, risks, acceptance gates, and change control.
license: Proprietary
compatibility: Designed for OpenCode. Assumes repo-local `.opencode/skills` discovery
  and standard read/edit/bash tools; optional scripts should run through a repo-local uv environment; requires uv and Python 3.11+.
metadata:
  pack: opencode-course-skills
---

# Purpose

Define and govern the execution plan for a course project.

# Deliverable types

- project brief
- milestone plan
- WBS-like work breakdown
- risk register
- dependency log
- review gate plan
- change log

# Planning model

Always cover:

1. goal and scope
2. artifacts to be produced
3. sequencing
4. dependencies
5. review gates
6. risks
7. release conditions

# Plan structure

Use this default structure:

1. Project objective
2. Scope in/out
3. Delivery assumptions
4. Workstreams
5. Milestones
6. Deliverables
7. Risks and mitigations
8. Acceptance criteria
9. Change control

# Review behavior

When reviewing an existing plan, check for:

- missing deliverables
- impossible sequencing
- unclear ownership
- missing QA/QC stages
- unbounded scope
- no release gate

# Gotchas

- Do not confuse lesson sequence with production sequence.
- Do not omit review and remediation cycles.
- Do not let plan dates exist without deliverable definitions.
- Do not leave risks unconnected to mitigation actions.

See:
- `assets/development-plan-template.md`
- `references/review-gates.md`
