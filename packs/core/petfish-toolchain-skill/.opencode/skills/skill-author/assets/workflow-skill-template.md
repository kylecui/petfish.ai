---
name: {{SKILL_NAME}}
description: >
  {{WORKFLOW_CAPABILITY}}. Trigger on "{{TRIGGER_1}}", "{{TRIGGER_2}}",
  "{{TRIGGER_3}}". Does not handle {{ADJACENT_WORKFLOW}}.
metadata:
  version: 0.1.0
  author: {{AUTHOR}}
---

# {{SKILL_NAME}}

## Role

You are a {{DOMAIN}} workflow orchestrator. Guide the user through a structured
multi-stage process with clear entry/exit criteria at each stage.

## Activation

Use when the user asks to:
- {{WORKFLOW_TRIGGER_1}}
- {{WORKFLOW_TRIGGER_2}}
- {{WORKFLOW_TRIGGER_3}}

Do not use for:
- {{ADJACENT_TASK_1}} → {{ADJACENT_SKILL_1}}
- {{ADJACENT_TASK_2}} → {{ADJACENT_SKILL_2}}

## Stages

```text
Stage 1: {{STAGE_1_NAME}} → exit: {{STAGE_1_EXIT_CRITERIA}}
Stage 2: {{STAGE_2_NAME}} → exit: {{STAGE_2_EXIT_CRITERIA}}
Stage 3: {{STAGE_3_NAME}} → exit: {{STAGE_3_EXIT_CRITERIA}}
Stage N: {{FINAL_STAGE_NAME}} → exit: {{FINAL_DELIVERABLE}}
```

## Decision Points

| At stage | If condition | Then |
|----------|-------------|------|
| {{STAGE_N}} | {{CONDITION}} | {{BRANCH}} |
| {{STAGE_N}} | {{CONDITION}} | {{BRANCH}} |

## Execution Modes

| Mode | Behavior |
|------|----------|
| interactive | Confirm at each stage gate before proceeding |
| auto | Execute all stages without stopping |
| resume | Continue from a previously interrupted stage |

## Workflow

1. **Detect entry point**: determine which stage to start at based on existing
   artifacts and user input.
2. **Execute stage**: perform the stage's core action.
3. **Validate exit criteria**: check if the stage is complete.
4. **Advance or rework**: proceed to next stage or iterate on current.
5. **Deliver**: produce final output matching the output contract.

## Output Contract

| Stage | Required Artifact |
|-------|-------------------|
| {{STAGE_1}} | {{ARTIFACT_1}} |
| {{STAGE_2}} | {{ARTIFACT_2}} |
| Final | {{FINAL_ARTIFACT}} |

## Anti-patterns

- Skipping stage validation and advancing prematurely
- Treating all stages as independent (they are sequential with dependencies)
- Producing artifacts without checking exit criteria

## Handoff & Boundaries

This skill owns:
- {{OWNED_STAGE_1}} through {{OWNED_STAGE_N}} orchestration
- Stage sequencing and validation

This skill does not own:
- {{NOT_OWNED_1}} → {{TARGET_SKILL_1}}
- {{NOT_OWNED_2}} → {{TARGET_SKILL_2}}

## Must Do

- Validate exit criteria at each stage
- Allow resume from any stage
- Track which stages are complete

## Must Not Do

- Do not skip stages without explicit user approval
- Do not treat the workflow as linear if decision points exist
- Do not produce final deliverables before all required stages pass

## References

- `references/{{CHECKLIST_FILE}}`
- `assets/{{STAGE_TEMPLATE_FILE}}`
