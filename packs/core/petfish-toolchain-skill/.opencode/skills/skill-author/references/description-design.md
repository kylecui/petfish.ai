# Description Design

How to write precise, high-signal descriptions that trigger correctly.

## Description Anatomy

A production description has four parts in under 1024 characters:

1. **What**: core capability in one clause
2. **When**: activation scenarios with concrete trigger phrases
3. **Boundary**: what it does NOT do (near-miss exclusion)
4. **Output hint**: what it produces

Example:
> Run structured code review with severity classification. Trigger on "review
> code", "code review", "quality check", "PR review", "review my changes".
> Does not handle deployment or testing. Returns findings with evidence and
> severity ratings.

## Near-Miss Design

Near-misses are requests that sound similar but belong to another skill.

Common near-miss patterns:

| Skill | Near-miss | Why it's different |
|-------|-----------|-------------------|
| code-review | "refactor this code" | Review assesses; refactor modifies |
| writing-style | "translate this" | Translation is not style rewrite |
| research-brief | "find me a source" | Brief frames questions; discovery finds sources |
| skill-author | "write me a script" | Script writing ≠ skill packaging |

For each skill, list 2-3 near-misses in the description.

## Trigger Phrase Rules

- Include both English and Chinese triggers when the skill is bilingual
- Use the exact phrasing a user would type, not abstract categories
- Cover at least 5 distinct trigger phrases
- Each phrase should be 2-6 words
- Avoid generic triggers like "help with X" — use specific actions

## Trigger Coverage Check

After writing the description, verify:

1. Every trigger phrase in the SKILL.md body appears (or is paraphrased) in the
   description
2. The description does NOT trigger for adjacent tasks
3. A user typing only the description's trigger phrases would correctly activate

Target: ≥80% body trigger coverage in description. Below 50% is a blocking defect.
