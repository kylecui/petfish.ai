---
name: course-development-orchestrator
description: Drive course projects end to end — plans, outlines, content, labs, learner/instructor materials, QA, QC, and release decisions. Also triggers for broad course development or curriculum requests.
license: Proprietary
compatibility: Designed for OpenCode. Assumes repo-local `.opencode/skills` discovery
  and standard read/edit/bash tools; optional scripts should run through a repo-local uv environment; requires uv and Python 3.11+.
metadata:
  pack: opencode-course-skills
---

# Purpose

Coordinate course development work across the other course skills in this pack. Use this as the default entry skill when the user asks for broad course design, course revision, course production, or course project management.

# When to activate

Activate when the user asks for any of the following in a broad or mixed way:

- build or revise a training course
- design a curriculum, syllabus, or teaching plan
- prepare course content, labs, learner handouts, or teacher notes
- review course quality, readiness, consistency, or delivery risk
- organize a course project repository or artifact set

If the request is narrow and clearly belongs to one specialized skill, let that skill lead. This skill should then act as a coordinator only.

# Default workflow

1. Determine the workstream:
   - planning
   - outline/syllabus
   - lesson content
   - labs/exercises
   - learner materials
   - instructor materials
   - QA review
   - QC remediation and reporting
   - repository/directory organization

2. Decide whether the request is:
   - create from scratch
   - modify existing material
   - review/critique
   - normalize/restructure
   - generate deliverable package

3. Produce or update a minimal execution frame before drafting:
   - target audience
   - training objective
   - delivery format
   - expected duration/lesson count
   - prerequisite knowledge
   - required outputs
   - quality bar
   - explicit constraints from the user

4. Route to the most relevant specialized skill:
   - `development-plan-governance`
   - `course-outline-design`
   - `course-content-authoring`
   - `course-lab-design`
   - `learner-materials`
   - `instructor-reference-materials`
   - `course-quality-assurance`
   - `course-quality-control-reporting`
   - `course-directory-structure`
   - `reference-document-review`
   - `markdown-course-writing`
   - `drawio-course-diagrams`

5. Keep outputs aligned:
   - naming
   - chapter numbering
   - terminology
   - difficulty progression
   - artifact locations
   - QA status

# Output rules

- Prefer Markdown unless the user explicitly asks for another format.
- Keep a stable hierarchy: project -> module -> lesson -> artifact.
- Separate **objective**, **content**, **activity**, **deliverable**, and **quality gate**.
- When reviewing, distinguish clearly between:
  - factual issue
  - structural issue
  - pedagogical issue
  - execution issue
  - formatting issue

# Coordination checklist

- [ ] Defined scope of the current task
- [ ] Identified target artifact(s)
- [ ] Applied the most relevant specialized skill
- [ ] Preserved consistency with existing course assets
- [ ] Added or updated QA/QC implications when relevant
- [ ] Left the project structure cleaner than before

# Gotchas

- Do not merge planning notes, teaching content, and QA findings into one undifferentiated document.
- Do not let labs drift away from lesson objectives.
- Do not let learner-facing material reveal instructor-only answer keys unless the user asks.
- Do not overproduce artifacts when the user only requested review.

See `references/workflow-map.md` for the cross-skill routing model and artifact map.
