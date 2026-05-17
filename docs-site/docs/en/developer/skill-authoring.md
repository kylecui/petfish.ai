# Skill Authoring Guide

How to create, structure, and validate PEtFiSh skills from scratch.

---

## What Is a Skill?

A skill is a directory containing a `SKILL.md` file with YAML frontmatter and Markdown instructions. Skills tell AI agents *how* to perform a specific task — they're prompt engineering packaged as reusable modules.

```text
my-skill/
├── SKILL.md              # Required: frontmatter + instructions
├── references/           # Optional: reference docs, examples
├── scripts/              # Optional: Python scripts for automation
├── assets/               # Optional: templates, schemas, images
└── evals/
    └── trigger/          # Optional: trigger evaluation test sets
        └── my-skill.json
```

---

## Quick Start

The fastest way to create a skill:

```bash
# Using the skill-author via /petfish
/petfish create my-new-skill
```

This scaffolds the directory structure and generates a starter `SKILL.md`. You can also create one manually.

---

## SKILL.md Structure

Every skill needs a `SKILL.md` with YAML frontmatter and a Markdown body.

### Frontmatter

```yaml
---
name: my-skill
version: 1.0.0
description: >-
  One-line description with trigger keywords. This is what the agent reads
  to decide whether to load this skill. Keep under 500 characters.
  Include both Chinese and English trigger phrases.
---
```

| Field | Required | Notes |
|---|---|---|
| `name` | Yes | Lowercase kebab-case. Must match directory name. |
| `version` | Yes | Semver format (`1.0.0`). |
| `description` | Yes | Under 500 chars. Must cover ≥80% of body trigger words. |

<a id="activation"></a>

!!! warning "Description is the match surface"
    The agent only reads `description` to decide whether to activate a skill. Trigger phrases in the body are invisible to the matcher. If a keyword isn't in the description, the skill won't fire for that keyword.

### Body

The body contains the actual instructions. Structure it however makes sense for your skill, but follow these conventions:

```markdown
# Role

You are a [role description].

## Activation

Use this skill when: [trigger conditions]

## Workflow

1. Step one
2. Step two
3. Step three

## Boundaries

- MUST: [requirements]
- MUST NOT: [prohibitions]

## Output Format

[Expected output structure]
```

---

## Naming Rules

- **Directory name** = `name` field in frontmatter
- Lowercase `kebab-case` only: `my-skill`, not `mySkill` or `My_Skill`
- No spaces, no underscores in directory names
- Prefer descriptive names: `deployment-executor` over `deploy`

---

## Adding Scripts

Python scripts go in `scripts/`. They extend the skill's capabilities beyond prompt instructions.

```text
my-skill/
└── scripts/
    └── validate.py
```

### Script Requirements

- Use PEP 723 inline metadata for dependencies:

```python
# /// script
# requires-python = ">=3.11"
# dependencies = ["pyyaml>=6.0"]
# ///
```

- Run via `uv run`:

```bash
uv run python .opencode/skills/my-skill/scripts/validate.py --input data.json
```

- Never use `pip install`. Never use bare `python3` for scripts with external dependencies.

---

## Adding References

Reference files provide domain knowledge that the skill instructions can point to:

```text
my-skill/
└── references/
    ├── best-practices.md
    └── examples.md
```

!!! tip "Lazy loading"
    Reference files should be loaded on demand, not all at once. Instruct the skill to read specific reference files only when needed.

---

## Adding Schemas

JSON schemas in `schemas/` define structured output formats:

```text
my-skill/
└── schemas/
    └── output.json
```

!!! warning "Schema–SKILL.md alignment"
    If you have both a schema and SKILL.md field descriptions, they **must** match exactly — same field names, same required/optional markers, same types. Mismatches cause validation failures. See the [Schema alignment discipline](../../technical/index.md) for details.

---

## Trigger Evaluation

Test whether your skill triggers correctly for the right inputs and stays silent for the wrong ones.

### Create Test Set

```text
my-skill/
└── evals/
    └── trigger/
        └── my-skill.json
```

```json
{
  "skill_name": "my-skill",
  "should_trigger": [
    "help me validate the deployment",
    "check if the service is healthy"
  ],
  "should_not_trigger": [
    "write a poem about clouds",
    "fix this CSS bug"
  ]
}
```

### Run Evaluation

```bash
/petfish eval .opencode/skills/my-skill/
```

Or via script:

```bash
uv run python .opencode/skills/skill-trigger-evaluator/scripts/evaluate_triggers.py \
  --path .opencode/skills/my-skill/evals/trigger/my-skill.json
```

---

## Validation

Before publishing, validate your skill:

### Lint

```bash
/petfish lint .opencode/skills/my-skill/
```

Checks:

- Frontmatter completeness (name, version, description)
- Description length (≤500 chars)
- Trigger keyword coverage (description vs. body ≥80%)
- File structure conventions
- Score must be ≥80/100 to pass

### Security Audit

```bash
/petfish audit .opencode/skills/my-skill/
```

Scans for:

- Prompt injection vectors
- Secret access patterns
- Dangerous command usage
- Excessive permissions
- Risk score must be ≤0.5 with no CRITICAL findings

### Full Quality Gate

```bash
/petfish gate .opencode/skills/my-skill/
```

Runs lint → security audit → metadata validation, then outputs a decision:

| Decision | Meaning |
|---|---|
| **PASS** | Ready to publish |
| **CONDITIONAL** | Minor issues; proceed with noted concerns |
| **FAIL** | Blocking issues; must fix before publishing |

---

## Packaging into a Pack

Skills are distributed in **packs** — directories under `packs/` that bundle related skills together.

```text
packs/my-pack/
├── .opencode/
│   └── skills/
│       ├── skill-one/
│       │   └── SKILL.md
│       └── skill-two/
│           └── SKILL.md
├── pack-manifest.json
├── AGENTS.md
└── opencode.example.json
```

### pack-manifest.json

```json
{
  "name": "my-pack",
  "version": "1.0.0",
  "description": "What this pack does",
  "skills": ["skill-one", "skill-two"],
  "commands": [],
  "agents": []
}
```

### New Pack Checklist

Introducing a new pack requires updating **9 touchpoints**. Missing any one causes silent installation failures. See the [Contributing Guide](contributing.md) for the full checklist.

---

## Common Mistakes

| Mistake | Consequence | Fix |
|---|---|---|
| Trigger keywords only in body, not in description | Skill never activates for those keywords | Add keywords to frontmatter description |
| Description only in English | Chinese users can't trigger the skill | Add Chinese trigger phrases |
| Schema field names differ from SKILL.md | Validation failures at runtime | Cross-check and align |
| Using `pip install` in scripts | Breaks uv-managed environments | Use PEP 723 inline metadata |
| Reference files loaded eagerly | Wastes context tokens | Load on demand |
