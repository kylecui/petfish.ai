---
name: skill-trigger-evaluator
description: >
  Evaluate whether a skill triggers correctly using positive should_trigger and
  negative should_not_trigger query sets. Trigger on “evaluate triggers”, “test
  skill trigger”, “trigger accuracy”, “false positive rate”, “is my skill
  triggering correctly”. Reports pass rate, false positive/negative rates,
  per-query decisions, and sibling cross-trigger conflicts when requested.
metadata:
  author: petfish-team
  version: 0.2.0
---

# skill-trigger-evaluator

## Purpose

Evaluate whether a skill's description and trigger phrasing are specific enough to activate on the right requests and avoid unrelated ones.

## Trigger phrases

- evaluate triggers
- test skill trigger
- trigger accuracy
- false positive rate
- is my skill triggering correctly

## When to use

Use this skill when the user wants to test whether a skill fires on the right prompts, compare positive and negative query sets, or diagnose overlap with sibling skills.

Typical targets:

- a newly authored skill before publishing
- a skill with vague or noisy trigger phrasing
- a pack with multiple related skills that may overlap
- a skill that passes lint but still matches the wrong requests

## Core workflow

1. Load the target skill's `SKILL.md` and extract the description plus any explicit trigger phrases.
2. Load a test file or generate a basic test set with:
   - positive queries that **should trigger** the skill
   - negative queries that **should not trigger** the skill
3. For each query, compute similarity to the skill description using keyword matching.
4. Calculate aggregate metrics:
   - `trigger_pass_rate`
   - `false_positive_rate`
   - `false_negative_rate`
5. Output an evaluation report with per-query pass/fail results and aggregate metrics.

## Recommended execution

Run the evaluator script instead of improvising manual checks:

```bash
uv run .opencode/skills/skill-trigger-evaluator/scripts/evaluate_triggers.py --path <skill-directory>
```

Useful options:

- `--test-file <file>` to supply curated test queries
- `--siblings <skills-dir>` to detect sibling overlap
- `--json` for machine-readable output
- `--verbose` to show per-query decisions
- `--threshold 0.80` to set the minimum acceptable positive pass rate

## Output rules

Always report:

- skill name
- total positive and negative counts
- passed positive count
- failed negative count
- `trigger_pass_rate`
- `false_positive_rate`
- `false_negative_rate`
- any `cross_trigger_conflicts`
- final `verdict`

If verbose output is requested, include each query with:

- expected behavior
- actual behavior
- overlap score
- matched keywords

## Must do

- Use both positive and negative query sets.
- Keep the heuristic explicit: keyword overlap against the skill description.
- Report sibling conflicts when `--siblings` is provided.
- Call out whether tests came from a provided JSON file or auto-generation.

## Must not do

- Do not claim this heuristic is equivalent to production embedding-based routing.
- Do not evaluate only positive queries and ignore false positives.
- Do not modify sibling skills during cross-trigger testing.
- Do not hardcode project-specific paths into the script.

## References

- `references/evaluation-methodology.md`
- `scripts/evaluate_triggers.py`
