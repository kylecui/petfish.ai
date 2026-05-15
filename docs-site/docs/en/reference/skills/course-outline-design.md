# course-outline-design

> Pack: **course**

Create, modify, or review a course outline, syllabus, chapter tree, hour

**Compatibility:** Designed for OpenCode. Assumes repo-local `.opencode/skills` discovery

---

# Purpose

Design the course architecture before detailed content authoring.

# Outline design method

1. Define training objective.
2. Define target audience and prerequisite baseline.
3. Split the course into modules that each carry a distinct teaching purpose.
4. Attach learning objectives to each module.
5. Allocate hours or lesson counts.
6. Define transitions between modules.
7. Identify what requires labs, demos, discussion, or reading.

# Review questions

- Does each module have a clear pedagogical job?
- Is the progression from basic to advanced coherent?
- Are prerequisites realistic?
- Is time allocation proportional to difficulty and value?
- Are labs attached to the right modules?

# Standard output

Use this structure unless the user already has a required format:

```markdown
# [Course Title]

## Positioning
## Audience
## Prerequisites
## Learning objectives
## Module map
## Hour allocation
## Assessment / lab mapping
## Risks and adjustment notes
```

# Gotchas

- Do not turn an outline into full lesson content.
- Do not let module titles become vague marketing slogans.
- Do not compress advanced modules without adjusting prerequisites.
- Do not ignore assessment and lab placement while outlining.

See `assets/syllabus-template.md`.
