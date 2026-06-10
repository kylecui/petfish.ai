# Skill Workbench Reference

This file is intended for GPT Knowledge upload.

## Purpose

Skill Workbench is the online-gpt module for designing and validating PEtFiSh skills.

It should not merely write a `SKILL.md`. It should produce a skill contract and prepare the skill for lint, audit, trigger eval, and quality gate.

## Required workflow

```text
idea
  -> skill contract
  -> trigger and non-trigger design
  -> file tree
  -> SKILL.md draft
  -> examples
  -> optional scripts
  -> safety boundary
  -> trigger eval cases
  -> lint/audit/gate plan
```

## Skill contract fields

| Field | Purpose |
|---|---|
| `name` | stable kebab-case skill name |
| `pack` | target pack or project-local location |
| `purpose` | the job this skill performs |
| `triggers` | positive activation examples |
| `non_triggers` | near-miss examples that should not activate |
| `inputs` | expected context or files |
| `outputs` | produced artifacts, reviews, commands, or patches |
| `side_effects` | whether the skill reads, writes, executes, or publishes |
| `safety` | constraints and prohibited behavior |
| `evals` | behavior tests and trigger tests |

## Good trigger design

Good triggers are specific enough to avoid accidental activation.

Example:

```text
Good: "Design a PEtFiSh skill with triggers, non-triggers, examples, and evals."
Weak: "Help me with a skill."
```

## Non-trigger design

Every skill should define cases that are close but should not activate the skill.

Example:

```text
Trigger: "Create a skill for deployment rollback runbooks."
Non-trigger: "Explain what rollback means in CI/CD."
```

## Side-effect declaration

Skills with scripts must declare one of:

- read-only;
- scoped write;
- network access;
- command execution;
- publish/release.

Any side effect beyond read-only should be routed through Trust Gate when exposed through the online GPT.

## GPT Companion response rule

When asked to create a skill, the GPT should produce:

1. skill contract;
2. suggested file tree;
3. trigger and non-trigger examples;
4. safety constraints;
5. eval cases;
6. gate plan.

It should not claim the skill is installed or published unless an adapter result confirms that.
