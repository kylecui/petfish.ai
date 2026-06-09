# Companion Gateway Reference

This file summarizes Companion Gateway for GPT Knowledge.

## Gateway flow

```text
User message
    -> Mode Read
    -> Topic Check
    -> Failure Signal Detection
    -> Skill Sense
    -> Anti-Sycophancy Check
    -> Proceed
```

## Mode Read

Reads project mode when available.

Mode dimensions:

- `depth`: urgent, balanced, thorough;
- `rigor`: false or true.

Online GPT cannot always read local `.opencode/project-mode.yaml`. It should infer session-only mode from user wording and ask less when enough context exists.

## Topic Check

Determines whether the user continues the current topic, shifts within a related topic, or switches to a new domain.

Online GPT should keep this lightweight:

- low risk: continue silently;
- medium risk: state inherited context briefly;
- high risk: flag possible topic switch and isolate assumptions.

## Failure Signal Detection

Detects previous failure patterns and recommends a pack or module that handles that failure.

Examples:

- document parsing failure -> doc-reader or ppt;
- deployment failure -> deploy;
- test document difficulty -> testdocs;
- weak research evidence -> research;
- context drift -> context.

## Skill Sense

Maps capability gaps to packs, skills, MCP servers, or Actions.

Examples:

- Docker, CI/CD, rollback -> deploy;
- course, teaching, lab -> course;
- slides, presentation -> ppt;
- testing, test case -> testdocs;
- research, literature, evidence -> research;
- context, topic, contamination -> context;
- trust, policy, audit, dangerous command -> trust.

## Anti-Sycophancy Check

For evaluation requests, the assistant must define criteria, identify counterarguments, and then conclude.

## Online adaptation

In local PEtFiSh, Gateway is injected into project instructions and can rely on local files or MCP. In Companion GPT, Gateway becomes a behavior contract plus optional Actions calls into the PEtFiSh Online Gateway.
