---
name: skill-description-optimizer
description: >
  Analyze/optimize SKILL.md frontmatter descriptions for trigger precision.
  Trigger on “optimize description”, “improve trigger”, “fix skill description”,
  “description too broad”, “skill not triggering”. Checks length, trigger phrase
  density, specificity score, activation boundaries, sibling overlap/collision,
  then outputs actionable rewrite suggestions and a replacement description.
metadata:
  author: petfish-team
  version: 0.2.0
---

# skill-description-optimizer

## Purpose

Improve a skill's frontmatter description so matching is more precise, more reliable, and easier to debug.

## Trigger phrases

Use this skill when the request includes ideas like:

- "optimize description"
- "improve trigger"
- "fix skill description"
- "description too broad"
- "skill not triggering"

## Core workflow

1. Read the target skill's `SKILL.md` and extract the frontmatter `description`.
2. Analyze description quality:
   - length check: too short means under-specified; too long means unfocused
   - trigger phrase density: does it contain actionable trigger words?
   - specificity score: how precisely does it define when to activate?
   - overlap analysis: compare against sibling skills to find trigger collisions
   - boundary check: does it say what it does **not** handle?
3. Generate optimization suggestions:
   - add missing trigger phrases
   - remove overly broad language
   - sharpen activation boundary
   - reduce overlap with siblings
4. Output an analysis report plus a suggested new description.

## How to execute

Primary command:

```bash
uv run .opencode/skills/skill-description-optimizer/scripts/optimize_description.py --path <skill-dir> --suggest --verbose
```

For sibling overlap analysis:

```bash
uv run .opencode/skills/skill-description-optimizer/scripts/optimize_description.py --path <skill-dir> --siblings <skills-dir> --suggest
```

Machine-readable output:

```bash
uv run .opencode/skills/skill-description-optimizer/scripts/optimize_description.py --path <skill-dir> --siblings <skills-dir> --json
```

## Output format

Always report:

- target skill name
- current description
- length assessment
- trigger phrase findings
- specificity score (0-100)
- boundary check result
- sibling overlap findings when available
- concrete rewrite suggestions
- suggested replacement description when requested

## Must do

- Read the actual target `SKILL.md` before making any recommendation.
- Focus on description quality, trigger precision, and activation boundaries.
- Compare against siblings when a sibling directory is available.
- Explain why the current description underperforms.
- Keep suggested descriptions concise, explicit, and trigger-oriented.

## Must not do

- Do not rewrite unrelated parts of the skill.
- Do not modify skill files directly; this skill analyzes and suggests only.
- Do not recommend vague catch-all wording such as "help with skills".
- Do not ignore overlap risk when multiple sibling skills compete for similar requests.

## References

- `references/optimization-guide.md`
- `scripts/optimize_description.py`
