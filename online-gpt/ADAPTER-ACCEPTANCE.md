# Adapter Mode Acceptance Criteria

Adapter Mode is optional for PEtFiSh Companion GPT.

It must not be required for the GPT version to be useful.

## Required inputs

Adapter Mode uses:

```text
GPT Instructions
GPT Knowledge
PEtFiSh Online Gateway API
Trust Gate
petfish_remote daemon or equivalent bridge
optional execution adapter
```

Optional execution adapters may include:

- OpenCode;
- Codex;
- Antigravity;
- Cursor;
- GitHub Copilot;
- Windsurf;
- shell-readonly;
- shell-scoped.

## Required capabilities

Adapter Mode may support:

- runtime registration;
- project alias lookup;
- side-effect-free local preview;
- approved scoped execution;
- log summarization;
- audit trace;
- rollback hints.

## Required safety controls

Adapter Mode requires:

- Trust Gate classification;
- explicit approval for side effects;
- second confirmation for high-risk operations;
- scoped project alias;
- secret masking;
- audit trace;
- execution proof;
- central disable switch.

## Required degradation

If no daemon or adapter is connected, the GPT must degrade to Gateway Mode or Standalone Mode.

It should provide:

- command plan;
- expected effects;
- manual verification;
- explanation that local execution is unavailable.

## Pass condition

Adapter Mode passes only when approved execution returns verified adapter results and durable audit traces.

Until then, remote execution should remain disabled.
