# Skill Specification Reference

This is a condensed working reference for authoring valid Agent Skills.

## 1. Required frontmatter

Every skill needs a `SKILL.md` with YAML frontmatter plus a Markdown body.

- `name`: required, 1-64 chars, lowercase letters/numbers/hyphens only
- `description`: required, 1-1024 chars, must explain **what** the skill does
  and **when** it should activate

Practical name rules:

- directory name and `name` must match exactly
- do not start or end with `-`
- avoid consecutive hyphens

## 2. Optional frontmatter

Use only when helpful:

- `license`: skill license or bundled license reference
- `compatibility`: environment requirements, runtime, or network constraints
- `metadata`: extra key/value metadata such as author or version
- `allowed-tools`: pre-approved tools if your runtime supports it

## 3. Progressive disclosure budget

Design the skill so agents load detail in layers:

1. `name` + `description`: roughly 100 tokens at startup
2. `SKILL.md` body: keep under 5000 tokens; concise instructions win
3. `references/`, `scripts/`, `assets/`: load on demand only

Keep the main skill focused. Move deep examples, long specs, and helper material
into separate files.

## 4. Directory conventions

Typical layout:

```text
skill-name/
├── SKILL.md
├── references/
├── scripts/
├── assets/
└── evals/
```

Guidelines:

- `references/`: reusable knowledge, domain rules, checklists, templates
- `scripts/`: executable helpers with clear errors and `--help`
- `assets/`: static templates, schemas, diagrams, sample files
- `evals/`: prompt examples and assertions for behavior checks

## 5. Authoring checklist

Before you finish:

- verify `name` matches the folder
- verify description states both what + when
- keep activation conditions concrete
- keep the body action-oriented, not essay-like
- avoid duplicating reference material inside `SKILL.md`
- prefer relative file references such as `references/guide.md`

## 6. Validation

If validation tooling exists, run it before handing off. A common pattern is:

```bash
skill-lint ./skill-name
```

If no validator is available, say so explicitly and do a manual frontmatter,
structure, and path check.
