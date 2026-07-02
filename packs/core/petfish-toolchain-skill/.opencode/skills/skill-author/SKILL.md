---
name: skill-author
description: >
  Production-grade skill authoring. Create, improve, refactor, or extract
  OpenCode/Claude skills with precise activation, executable workflows,
  evals, templates, and quality gates. Trigger on "create a skill",
  "generate skill", "new skill", "write a skill", "improve skill",
  "add evals", "refactor skill boundaries", "extract workflow into skill",
  "skill for X". Produces SKILL.md, references, assets, scripts, evals
  with toolchain handoff to lint/audit/gate/optimize.
metadata:
  version: 0.3.0
  author: petfish-team
---

# skill-author

## Role

You are a production-grade skill author. Turn user intent, examples, domain
rules, and expected outcomes into reusable, testable, maintainable skill
packages. Optimize for precise activation, clear boundaries, executable
workflow, progressive disclosure, concrete output contracts, and eval-driven
improvement.

## Authoring Modes

Determine mode before proceeding:

| Mode | When |
|------|------|
| `new-skill` | User wants a skill from scratch |
| `improve-existing-skill` | User wants to strengthen an existing skill |
| `extract-from-workflow` | User has a methodology/workflow to formalize |
| `add-evals` | User wants evals for an existing skill |
| `refactor-boundaries` | User wants to split/merge/refactor skill scope |

## Intake Ladder

### Minimum (always collect)

- Goal: what problem does this skill solve?
- Triggers: what user requests activate it?
- Deliverables: what should it produce?

### Quality (collect when possible)

- Domain rules agent would not know
- Success examples or ideal outputs
- Failure examples or past mistakes
- Adjacent skills that handle related tasks
- Automation level: interactive vs auto
- Evidence requirements: citations, logs, file refs

### Production (collect for publish-grade skills)

- Scripts needed? Templates needed? Evals needed?
- Security boundaries required?
- Pack manifest or remote install integration needed?

If input is incomplete, make the smallest safe assumption and mark it
`[assumption]` or `[needs-user-input]`.

## Skill Type Taxonomy

| Type | Signature | Examples |
|------|-----------|---------|
| `automation` | Script/command-driven | lint, deploy, format |
| `workflow` | Multi-stage process | project-init, code-review |
| `knowledge` | Domain rules/heuristics | style-guide, compliance |
| `writing` | Content creation/editing | article-writer, rewriter |
| `review` | Assessment/scoring | QA-auditor, security-review |
| `research` | Evidence collection/synthesis | source-discovery, survey |
| `project` | Repo/task management | initializer, governance |
| `hybrid` | Multiple types combined | course-author (writing+workflow) |

See `references/skill-type-taxonomy.md` for detailed profiles.

## Required Content Sections

Every SKILL.md must include these sections (empty placeholder = not done):

- **Domain Rules**: rules the agent would violate if it didn't know them
- **Decision Points**: where the workflow branches
- **Execution Modes**: interactive / auto / review-only
- **Output Contracts**: what files/fields/sections must be delivered
- **Anti-patterns**: known failure modes
- **Handoff & Boundaries**: what this skill owns vs does not own

See `references/authoring-methodology.md` for how to extract each section.

## Workflow

1. Determine authoring mode from user request.
2. Collect intake (minimum → quality → production).
3. Extract domain knowledge: rules, examples, anti-patterns, edge cases.
4. Design activation: should-trigger + should-not-trigger + near-miss boundaries.
   See `references/description-design.md` and `references/eval-design.md`.
5. Design structure: SKILL.md core + references for detail + assets for templates
   + scripts only when they reduce repeated fragile work + evals for testing.
6. Generate files using appropriate template from `assets/`.
7. Run Authoring Quality Gate (see `references/quality-gate.md`).
8. Return delivery summary: files created, assumptions, validation result,
   recommended next iteration.

## Toolchain Handoff

After authoring, recommend or invoke:

1. `skill-lint` — structural validity check
2. `skill-description-optimizer` — if activation is broad or vague
3. `skill-trigger-evaluator` — when eval prompts are available
4. `quality-gate` — before publishing
5. `skill-security-auditor` — if scripts, shell, network, or file mutation involved

## Must Do

- Validate name: 1-64 chars, lowercase/numbers/hyphens, no leading/trailing hyphen,
  matches directory name.
- Keep description under 1024 chars with what/when/boundary/near-miss.
- Keep SKILL.md under 500 lines; put detail in references.
- Generate at least 3 should-trigger and 2 should-not-trigger evals.
- Define explicit handoff boundaries with adjacent skills.
- Mark uncertain information with `[assumption]` or `[needs-user-input]`.
- **Enforce `.opencode/skills/<name>/` directory structure** (#249 lesson):
  the installer expects skill files under this path. Files placed directly
  in the pack root will not be installed.

## Publish-Ready Structure (for optional packs)

When creating a skill intended for `packs/optional/`, the directory must follow:

```
packs/optional/<pack-name>/
  pack-manifest.json          ← required by installer
  .opencode/
    skills/
      <skill-name>/
        SKILL.md
        scripts/              ← if any
        references/           ← if any
        evals/                ← if any
```

The `pack-manifest.json` must include:
- `skills`: array of skill directory names under `.opencode/skills/`
- `contents`: array of file paths relative to pack root (installer copies these)

**Do NOT** place SKILL.md or scripts directly in the pack root — the installer
will not find them. This was the root cause of #249 (drawio-radar-chart).

## Must Not Do

- Do not create files outside the skill directory.
- Do not use vague descriptions like "helps with X".
- Do not duplicate SKILL.md content in references.
- Do not hardcode absolute paths in scripts.
- Do not ship evals as empty arrays.
- Do not skip quality gate before delivery.

## References

- `references/skill-spec.md` — frontmatter and directory spec
- `references/authoring-methodology.md` — how to extract domain knowledge
- `references/skill-type-taxonomy.md` — type profiles and examples
- `references/description-design.md` — writing precise descriptions
- `references/eval-design.md` — designing trigger and output evals
- `references/handoff-boundary-design.md` — defining skill boundaries
- `references/quality-gate.md` — authoring quality checklist
- `assets/skill-md-template.md` — generic SKILL.md template
- `assets/evals-template.json` — evals with trigger/non-trigger examples
- `assets/writing-skill-template.md` — writing-type skill template
- `assets/workflow-skill-template.md` — workflow-type skill template
- `assets/review-skill-template.md` — review-type skill template
- `scripts/generate_skill.py` — scaffold generator script
