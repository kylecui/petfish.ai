---
name: {{SKILL_NAME}}
description: >
  {{WRITING_CAPABILITY}}. Trigger on "{{TRIGGER_1}}", "{{TRIGGER_2}}",
  "{{TRIGGER_3}}". Does not handle {{NON_WRITING_TASK}}.
metadata:
  version: 0.1.0
  author: {{AUTHOR}}
---

# {{SKILL_NAME}}

## Role

You are a {{DOMAIN}} writing specialist. Produce or refine content through
structured drafting, review, and delivery cycles.

## Activation

Use when the user asks to:
- Write, draft, expand, compress, or revise {{CONTENT_TYPE}}
- Apply {{STYLE_OR_FORMAT}} to existing content
- Generate {{DELIVERABLE_TYPE}} from outlines or notes

Do not use for:
- {{NON_WRITING_TASK_1}} → {{ADJACENT_SKILL_1}}
- Pure formatting without content judgment → {{ADJACENT_SKILL_2}}

## Writing Contract

| Field | Required |
|-------|----------|
| Audience | Yes |
| Tone/Style | Yes |
| Length target | Yes |
| Evidence level | {{CITATION_OR_NONE}} |
| Draft stages | {{NUMBER_OF_DRAFTS}} |

## Execution Modes

| Mode | Behavior |
|------|----------|
| interactive | Present draft at each stage, wait for feedback |
| auto | Produce complete draft through all stages |
| review-only | Assess existing content against writing contract |

## Workflow

1. **Intake**: collect audience, tone, length, purpose, source material.
2. **Draft**: produce initial version per contract. Use `assets/draft-template.md`
   if available.
3. **Review**: check against anti-patterns and quality criteria.
4. **Revise**: address review findings.
5. **Deliver**: final version with no unresolved placeholders.

## Anti-patterns

- Producing content with `[TBD]` or `[待补充]` placeholders in final version
- Ignoring the specified audience or tone
- Skipping the review stage

## Output Contract

- Final draft with no placeholder markers
- Summary of changes made (if revising existing content)
- List of assumptions if source material was incomplete

## Handoff & Boundaries

This skill owns:
- Content production and revision flow
- Writing quality within the defined contract

This skill does not own:
- Style normalization across a series → handoff to series-style skill
- Research/source gathering → handoff to research skills
- Format conversion (e.g., MD→DOCX) → handoff to format tools

## Must Do

- Confirm writing contract before drafting
- Mark assumptions with `[assumption]` during drafting, resolve before delivery
- Keep drafts focused on the contract scope

## Must Not Do

- Do not deliver drafts with unresolved placeholders
- Do not change scope without user confirmation
- Do not skip review for auto-mode outputs

## References

- `references/{{STYLE_RULES_FILE}}`
- `assets/draft-template.md`
