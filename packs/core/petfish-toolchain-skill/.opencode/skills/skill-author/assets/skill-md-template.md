---
name: {{SKILL_NAME}}
description: >
  {{WHAT_IT_DOES}}. Trigger on "{{TRIGGER_1}}", "{{TRIGGER_2}}",
  "{{TRIGGER_3}}". Does not handle {{NEAR_MISS_TASK}}.
metadata:
  version: 0.1.0
  author: {{AUTHOR}}
---

# {{SKILL_NAME}}

## Role

{{ONE_SENTENCE_ROLE_DEFINITION}}

## Activation

Use this skill when the user asks to:
- {{TRIGGER_SCENARIO_1}}
- {{TRIGGER_SCENARIO_2}}
- {{TRIGGER_SCENARIO_3}}

Do not use this skill for:
- {{NEAR_MISS_SCENARIO_1}} → {{ADJACENT_SKILL_1}}
- {{NEAR_MISS_SCENARIO_2}} → {{ADJACENT_SKILL_2}}

## Domain Rules

{{RULE_AGENT_WOULD_VIOLATE_IF_IT_DIDNT_KNOW}}
{{RULE_2}}
{{RULE_3}}

## Execution Modes

| Mode | Behavior |
|------|----------|
| interactive | {{INTERACTIVE_DESCRIPTION}} |
| auto | {{AUTO_DESCRIPTION}} |

## Workflow

1. {{STEP_1_INTAKE_OR_DETECTION}}
2. {{STEP_2_CORE_ACTION}}
3. {{DECISION_POINT}}: if {{CONDITION}}, then {{BRANCH_A}}; else {{BRANCH_B}}
4. {{STEP_3_OUTPUT_GENERATION}}
5. {{STEP_4_VALIDATION_OR_REVIEW}}

## Output Contract

| Mode | Required Deliverables |
|------|-----------------------|
| interactive | {{INTERACTIVE_OUTPUTS}} |
| auto | {{AUTO_OUTPUTS}} |

## Anti-patterns

- {{ANTI_PATTERN_1}}: {{WHY_IT_FAILS}}
- {{ANTI_PATTERN_2}}: {{WHY_IT_FAILS}}

## Handoff & Boundaries

This skill owns:
- {{OWNED_RESPONSIBILITY_1}}
- {{OWNED_RESPONSIBILITY_2}}

This skill does not own:
- {{NOT_OWNED_1}} → {{TARGET_SKILL_1}}
- {{NOT_OWNED_2}} → {{TARGET_SKILL_2}}

## Must Do

- {{MUST_DO_1}}
- {{MUST_DO_2}}

## Must Not Do

- {{MUST_NOT_DO_1}}
- {{MUST_NOT_DO_2}}

## References

- `references/{{REFERENCE_FILE_1}}`
- `references/{{REFERENCE_FILE_2}}`
