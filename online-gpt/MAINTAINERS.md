# Maintainer Notes

This file records maintenance rules for `online-gpt/`.

## Do not fork core semantics

Before adding or changing any online-gpt behavior, decide which category it belongs to:

| Category | Example | Rule |
|---|---|---|
| core semantic | pack alias, profile mapping, skill lifecycle | change core first |
| derived reference | Knowledge pack table, platform table | compile or sync from core |
| adapter behavior | Action wrapper, Trust Gate, remote preview | may be online-specific but must wrap core |
| evaluation | regression, alignment, safety checks | should accompany behavior changes |

## When to update alignment docs

Update `ALIGNMENT.md` and `SOURCE-OF-TRUTH.md` when:

- a new authoritative core source is added;
- a pack moves to petfish-market;
- platform metadata changes;
- a module duplicates core facts temporarily;
- remote-control semantics become stable in the main project.

## Commit discipline

A good online-gpt commit usually contains:

- module or instruction change;
- corresponding Knowledge or Action update if needed;
- eval update;
- alignment check if core facts are affected.

## Red flags

Pause and review if a change says or implies:

- online-gpt has its own official pack list;
- GPT behavior replaces Companion Gateway;
- remote execution is safe without Trust Gate;
- generated commands equal executed work;
- publish readiness without quality gate.

## Local checks

Run:

```bash
python online-gpt/tools/check_alignment.py
python online-gpt/gateway/eval_runner.py online-gpt/evals
```

The current eval runner is intentionally simple. It checks deterministic gateway behavior, not full GPT prose.
