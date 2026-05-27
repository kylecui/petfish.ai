# SKILL.md Templates

Use these as starting points. Replace placeholders with concrete task language.

## 1. automation

Best for script-backed skills such as linters, formatters, deployers, sync jobs,
or report generators.

### Frontmatter example

```yaml
---
name: repo-linter
description: Run repository lint checks and summarize failures. Use when the user asks to lint the repo, validate style rules, or troubleshoot CI lint errors.
metadata:
  version: 0.1.0
  author: your-team
---
```

### Body outline

```md
# repo-linter

## Role
You are the repo linting specialist.

## When to use
- Lint the repository
- Investigate CI lint failures
- Run formatting or static checks before commit/release

## Workflow
1. Inspect the repo and detect the lint command.
2. Run the script or command.
3. Summarize failures by file and rule.
4. Suggest the smallest safe fix.

## Tool usage
- Read config files before running commands.
- Use scripts/run_lint.py or project-native commands.

## Output
- command run
- result
- failing files
- next action

## Must do / Must not do
- must verify command target
- must not edit unrelated files
```

### Customize

- replace the command and validation steps
- define exact failure reporting format
- add `scripts/` helpers only when they reduce repeated work

## 2. workflow

Best for multi-step operational or review flows such as project init, code
review, release readiness, or migration planning.

### Frontmatter example

```yaml
---
name: code-reviewer
description: Run a structured code review and return findings by severity. Use when the user asks for review, risk analysis, quality checks, or release readiness feedback.
metadata:
  version: 0.1.0
  author: your-team
---
```

### Body outline

```md
# code-reviewer

## Role
You are a structured review facilitator.

## Intake
- scope
- risk focus
- expected output format

## Workflow
1. Identify review scope.
2. Inspect relevant files.
3. Classify findings by severity.
4. Return evidence and recommended next steps.

## Tool usage
- Read implementation and config files first.
- Use search/navigation tools to trace impact.

## Output
- summary
- findings
- risks
- recommendation

## Boundaries
- must cite evidence
- must not invent issues without proof
```

### Customize

- define the exact phases and exit criteria
- add checklists in `references/` instead of expanding the main body
- include eval prompts when the workflow has clear expected behavior

## 3. knowledge

Best for domain expertise skills such as style guides, architecture heuristics,
security baselines, or compliance notes.

### Frontmatter example

```yaml
---
name: api-style-guide
description: Apply the team's API design rules and explain tradeoffs. Use when the user asks for endpoint design, naming consistency, request/response conventions, or API review guidance.
metadata:
  version: 0.1.0
  author: your-team
---
```

### Body outline

```md
# api-style-guide

## Role
You are the team's API design reference.

## When to use
- design a new endpoint
- review API naming
- check request/response consistency

## Workflow
1. Identify the API problem.
2. Apply the relevant rules.
3. Explain tradeoffs and give a recommendation.

## Tool usage
- Read local API specs before advising.
- Use references for detailed naming or payload rules.

## Output
- recommendation
- reasoning
- relevant rules applied

## Boundaries
- must align with local conventions
- must not override explicit project rules
```

### Customize

- move detailed standards into `references/`
- add examples and anti-patterns there instead of bloating `SKILL.md`
- keep the main skill focused on decision flow, not encyclopedic content
