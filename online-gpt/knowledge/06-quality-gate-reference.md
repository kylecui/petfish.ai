# Quality Gate Reference

This file is intended for GPT Knowledge upload.

## Purpose

PEtFiSh treats skill quality as an engineering lifecycle, not as prompt writing.

A skill should pass through:

```text
idea -> contract -> author -> lint -> audit -> trigger eval -> quality gate -> publish decision
```

## Gate dimensions

| Dimension | Meaning |
|---|---|
| metadata | name, version, description, trigger clarity |
| instruction quality | precise scope, non-triggers, examples |
| script safety | scoped file access, no hidden side effects |
| trigger coverage | description and body align with trigger examples |
| security risk | no critical unsafe behavior |
| eval readiness | expected behavior has test cases |

## GPT Companion behavior

When asked to create or review a skill, GPT should not stop at a draft. It should produce or request:

- skill purpose;
- triggers;
- non-triggers;
- file tree;
- examples;
- safety constraints;
- lint/audit/gate plan;
- eval cases.

## Publication discipline

Do not claim a skill is publishable unless a gate result exists or the statement is clearly a recommendation.

Valid language:

- "This is a draft skill contract."
- "This should be run through lint/audit/gate."
- "The gate has not been executed."

Invalid language:

- "This skill is ready to publish" without a gate result.
