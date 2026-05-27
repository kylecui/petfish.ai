<!-- BEGIN pack: opencode-skill-pack-testcases-usage-docs -->
# Test Cases & Usage Docs Skill Pack Rules

This pack provides two complementary skills: generating test cases from real project code, and generating usage documentation from real project capabilities.

## Skill Routing (强制)

### Rules

1. When the user asks to generate **test cases, test strategy, test matrix, or test plan** from a project, **MUST** route to `generate-test-cases`. Do NOT route to `generate-usage-docs`.
2. When the user asks to generate **README, Quick Start, API docs, CLI docs, FAQ, or troubleshooting guides** from a project, **MUST** route to `generate-usage-docs`. Do NOT route to `generate-test-cases`.
3. Both skills require a **project inventory step first**: run `uv run scripts/project_inventory.py .` before generating artifacts. Do not skip this step.
4. When the user asks for both tests and docs in the same request, run `generate-test-cases` and `generate-usage-docs` sequentially (inventory once, then both generation steps). Do not merge them into a single pass.
5. Both skills operate on **real project code and design docs** — do not generate generic/template artifacts without first reading the actual project.

### Conflict Resolution

- "Write tests for this project" = `generate-test-cases`.
- "Document this project" = `generate-usage-docs`.
- "Help me ship this project" (ambiguous) → ask whether the priority is test coverage or user-facing documentation, then route accordingly.
- If the user provides a design doc or spec as input, both skills can use it — but route based on the desired output type (tests vs docs).

## generate-test-cases Workflow

1. Run project inventory: `uv run scripts/project_inventory.py .`
2. Build traceability map: capabilities → test targets
3. Generate layered test artifacts:
   - Test strategy (scope, risk areas, coverage goals)
   - Test matrix (feature × scenario × priority)
   - Test cases (input, expected output, pass/fail criteria)
4. Output to `tests/` or designated output directory

## generate-usage-docs Workflow

1. Run project inventory: `uv run scripts/project_inventory.py .`
2. Identify target audience (end user / developer / operator)
3. Identify project capabilities (CLI, API, config, integrations)
4. Build doc set:
   - README (overview, install, quick start)
   - API / CLI reference
   - FAQ and troubleshooting
5. Output to `docs/` or designated output directory

## Behavioral Rules

- Always run project inventory before generating any artifact. Do not generate from assumptions.
- Test cases must be traceable to specific project capabilities identified in the inventory.
- Usage docs must reflect actual project behavior, not generic boilerplate.
- If the project inventory reveals missing or ambiguous capabilities, flag them before generating — do not silently fill gaps with invented behavior.
- Generated test cases must include: input, expected output, and pass/fail criteria. Vague test descriptions are not acceptable.
- Generated docs must include: at least one working example per capability documented.

## Output Format

**generate-test-cases** outputs:
1. Test strategy document — scope, risk areas, coverage goals
2. Test matrix — feature × scenario × priority table
3. Test case files — structured cases with input/output/criteria

**generate-usage-docs** outputs:
1. README — overview, install, quick start
2. Reference docs — API / CLI / config
3. FAQ / Troubleshooting — common issues and resolutions
<!-- END pack: opencode-skill-pack-testcases-usage-docs -->
