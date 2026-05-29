# Eval Design

How to design evals that test trigger accuracy and output quality.

## Eval Structure

Each eval has:

- `id`: descriptive kebab-case identifier
- `prompt`: what the user would type (realistic, 10-40 chars)
- `should_trigger`: boolean
- `expected_output`: what the skill should do (1-2 sentences)
- `assertions`: 2-4 verifiable checks on the response

## Should-Trigger Evals (minimum 3)

Cover these categories:

1. **Primary trigger**: the most obvious use case
2. **Secondary trigger**: a less common but valid use case
3. **Edge case trigger**: unusual but correct activation

Example:
```json
{
  "id": "trigger-primary-review",
  "prompt": "帮我review一下这个PR",
  "should_trigger": true,
  "expected_output": "Runs structured review with severity classification.",
  "assertions": [
    "Response classifies findings by severity.",
    "Each finding includes file and line reference.",
    "Response does not modify any files."
  ]
}
```

## Should-Not-Trigger Evals (minimum 2)

Cover these categories:

1. **Adjacent task**: similar domain, different skill
2. **Generic request**: too vague to match

Example:
```json
{
  "id": "no-trigger-adjacent-refactor",
  "prompt": "帮我重构这个模块",
  "should_trigger": false,
  "expected_output": "Does not activate review workflow.",
  "assertions": [
    "Response does not run review stages.",
    "Response does not classify findings by severity."
  ]
}
```

## Output Quality Assertions

For writing/review/research skills, add quality assertions:

- Writing: "No unresolved placeholders in final output"
- Review: "Each finding has evidence citation"
- Research: "Each claim maps to a source_id"

## Boundary Evals

Include at least one eval that tests the boundary between this skill and an
adjacent skill. The assertion should verify correct handoff, not just non-trigger.

## Evals File Location

Place evals at `evals/evals.json` with this structure:

```json
{
  "skill_name": "skill-name",
  "version": "0.1.0",
  "evals": [...]
}
```
