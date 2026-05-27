---
name: course-directory-structure
description: Create, reorganize, normalize, or audit a course project directory tree,
  including naming rules, artifact placement, archive cleanup, and scaffold generation.
license: Proprietary
compatibility: Designed for OpenCode. Assumes repo-local `.opencode/skills` discovery
  and standard read/edit/bash tools; optional scripts should run through a repo-local uv environment; requires uv and Python 3.11+.
metadata:
  pack: opencode-course-skills
---

# Purpose

Create and maintain a predictable course project directory structure for OpenCode-based course development.

# When to use

Activate when the user asks to:

- initialize a new course repository
- create a standard course artifact tree
- reorganize messy course files
- normalize naming and placement
- archive old drafts
- check whether a course project is structurally complete

# Default directory model

Use this structure unless the user provides a better existing standard:

```text
.opencode/
  skills/
docs/
  00-project/
  01-outline/
  02-content/
  03-labs/
  04-learner-pack/
  05-instructor-pack/
  06-qa/
  07-qc/
assets/
  images/
  drawio/
  tables/
references/
  external/
  internal/
release/
archive/
```

# Naming rules

- Prefer lowercase kebab-case for file names.
- Prefix ordered directories and ordered lesson files with two digits.
- Keep one primary topic per file.
- Separate learner-facing and instructor-only files.
- Keep generated reports under `docs/06-qa/` or `docs/07-qc/`, not mixed into content.
- Move obsolete or superseded drafts into `archive/`, not random `old/` folders.

# Operating procedure

1. Inspect the current tree.
2. Infer the user's intended course lifecycle.
3. Compare the current tree with the default model.
4. Propose the minimal safe reorganization.
5. If the repository is messy, split the work into three phases: initialize -> audit -> reorganize.
6. Create missing folders and move files only when the target location is unambiguous.
7. When ambiguity exists, generate a dry-run style reorganization proposal instead of guessing.
8. Record structural decisions in a project note if the reorganization is substantial.

# Use the scaffold script when appropriate

Script:
`uv run scripts/bootstrap_course_tree.py --help`

Use it when the user explicitly wants a new scaffold or a normalized tree created on disk.

# Use the audit script when appropriate

Script:
`uv run scripts/check_course_tree.py --help`

Use it when the user asks whether the repository is complete, clean, or ready for the next phase.

# Output expectations

When reviewing a structure, report:

- what exists
- what is missing
- what is misplaced
- what should be archived
- what should be created next

When modifying structure, also produce a concise change summary.
When only proposing changes, produce a reorganization plan with risk notes.

# Gotchas

- Do not rename files that are heavily cross-referenced unless necessary.
- Do not move deliverables into `archive/` just because they are old; archive only superseded or abandoned material.
- Do not put source references inside learner packs.
- Do not create deep nesting unless the course is large enough to justify it.

See:
- `assets/course-tree-template.md`
- `references/structure-policy.md`
- `references/reorganization-checklist.md`
