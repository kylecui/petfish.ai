---
name: skill-lint
description: >
  Lint/check/validate skill quality and trigger reliability. Trigger on “lint
  skill”, “check skill”, “validate skill”, “is this skill valid”, pre-publish
  QA, or debugging load/match issues. Runs lint_skill.py on single skill or
  recursive roots, reports ERROR/WARN/INFO with rule IDs, score/counts, JSON
  output, and optional dry-run/apply fix workflow.
metadata:
  version: 0.2.0
  author: petfish-team
---

# skill-lint

## Purpose

Validate a skill directory for structure, frontmatter quality, body guidance quality, and basic script safety.

## When to use

Use this skill when the user asks to lint skill, check skill, validate skill, review skill quality, or asks whether a skill is valid.

Typical targets:

- a single skill directory
- a pack's `.opencode/skills/` tree
- a skill that fails to trigger reliably
- a skill that is about to be published or committed

## Workflow

1. Identify the target skill directory or root directory to scan.
2. Run `scripts/lint_skill.py` on the target.
3. If the user wants a machine-readable report, use `--json`.
4. If the user wants batch validation, use `--recursive`.
5. If the user wants low-noise output, use `--severity error` or `--severity warn`.
6. If the user asks for safe auto-fixes, run `--fix` first to show the dry-run plan, then `--fix-apply` only after confirmation.

## Output rules

Report findings with these severities:

- `ERROR`: must fix
- `WARN`: should fix
- `INFO`: suggestion

For every finding, provide:

- rule ID
- severity
- short explanation
- concrete fix suggestion

Always summarize:

- total score
- error count
- warning count
- info count

## Must do

- Run `lint_skill.py` on the requested target instead of manually improvising checks.
- Use the reported rule IDs and severities exactly.
- Give a concrete fix suggestion for each finding.
- Call out whether `--fix` is dry run or applied.

## Must not do

- Do not invent extra blocking rules beyond the linter output.
- Do not treat `INFO` as release-blocking.
- Do not apply fixes silently; use dry run first unless the user explicitly wants changes applied.

## Reference

See `references/lint-rules.md` for the full rule catalog and examples.
