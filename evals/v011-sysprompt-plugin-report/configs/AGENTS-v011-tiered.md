# Project Agent Guide

## Project Goal

We are testers for 胖鱼 PEtFiSh. Our goal is to mock every possible usage scenario of PEtFiSh skills, commands, agents, and installation workflows — verify they work correctly, and raise issues via GitHub when problems are found.

## Project Type

comprehensive (PEtFiSh QA & testing)

## Working Principles

- Test every skill pack systematically: install, invoke, verify output, check edge cases.
- When a bug or UX issue is found, file a GitHub issue at `kylecui/SKILL_builder` with reproduction steps.
- Keep test evidence (logs, outputs, screenshots) in `experiments/` or `outputs/`.
- Do not overwrite existing files unless explicitly confirmed.
- Leave notes for important findings.
- Prefer real-world usage scenarios over synthetic tests.

## Directory Map

```text
.
├── .opencode/          # Skills, commands, agents, templates
├── course/             # Course development testing
├── deploy/             # Deployment testing
├── docs/               # Documentation
├── experiments/        # Test evidence and experiments
├── mcp/                # MCP configuration
├── ops/                # Operations testing
├── outputs/            # Generated outputs
├── product/            # Product artifacts
├── qa/                 # QA checklists and reports
├── references/         # Reference materials
├── src/                # Source code
├── tasks/              # Backlog and roadmap
└── tests/              # Automated tests
```

## Quality Gates

- Every bug filed must include reproduction steps.
- Test evidence should be saved before reporting.
- Generated outputs are separated from sources.

## Do Not

- Do not write secrets or API keys into repository files.
- Do not overwrite user files silently.
- Do not mix temporary outputs into formal materials.

---

<!-- Pack rules are injected into system prompt by plugin — no manual Read needed -->

---

