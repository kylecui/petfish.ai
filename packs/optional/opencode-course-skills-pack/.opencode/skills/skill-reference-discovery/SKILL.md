---
name: skill-reference-discovery
description: Search GitHub/public sources for high-quality agent skills, run skill reference scans, compare candidate repositories, evaluate credibility/maintenance/relevance/portability, extract reusable patterns, identify cautions or mismatches, and recommend adaptations for the current OpenCode skill pack.
license: Proprietary
compatibility: Designed for OpenCode. Assumes repo-local `.opencode/skills` discovery
  and standard read/edit/bash tools; optional scripts should run through a repo-local uv environment; requires uv and Python 3.11+.
metadata:
  pack: opencode-course-skills
---

# Purpose

Look outward for reusable public skill patterns that are worth adapting into this pack.

# Search targets

Prefer:

- official repositories
- well-maintained example repositories
- curated collections
- projects that explicitly support Agent Skills or OpenCode

# Evaluation criteria

For each candidate, check:

- credibility
- maintenance
- relevance
- structural quality
- portability to OpenCode
- whether it contains reusable patterns instead of only domain-specific content

# Output structure

```markdown
# Skill Reference Scan

## Search scope
## Candidate repositories
## Strong patterns worth borrowing
## Cautions / mismatches
## Recommendation for this pack
```

# Gotchas

- Do not copy public skills blindly into a private methodology pack.
- Do not treat star count as a substitute for relevance.
- Do not lift vendor-specific workflows that conflict with the user's operating model.
- Do not cite a repository as authoritative if it is only a topic page or discussion thread.

See `references/reference-scan-template.md`.
