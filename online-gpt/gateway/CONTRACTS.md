# Gateway Contracts

This document specifies the deterministic contracts implemented by `online-gpt/gateway/`.

The gateway skeleton is not intended to replace core PEtFiSh. It wraps core concepts for online GPT use.

## Common envelope

Every module returns:

```json
{
  "ok": true,
  "module": "installer",
  "mode": "dry_run",
  "result_level": "command_rendered",
  "data": {},
  "warnings": [],
  "errors": [],
  "audit": {}
}
```

## Operation contracts

### `routeCompanionRequest`

Purpose: classify the user request and choose the response contract.

Must preserve this priority:

1. explicit trust boundary;
2. install/profile/pack command rendering;
3. skill design;
4. catalog/search;
5. pure remote preview;
6. general/review.

Rationale: mentioning OpenCode/Codex/Antigravity does not automatically mean remote execution. These platform names also appear in normal install and profile requests.

### `searchCatalog`

Purpose: find existing packs or capabilities.

Must not invent official aliases. Unknown domains should be returned as no exact match and may be routed to market search later.

### `profileProject`

Purpose: infer minimal sufficient pack sets.

Must not use `comprehensive` as a lazy default.

### `renderInstallCommand`

Purpose: render a local command without running it.

Must include:

- operation;
- packs;
- platform;
- target;
- command;
- expected effects;
- verification hint;
- warning that it does not execute locally.

### `designSkill`

Purpose: produce a skill contract skeleton.

Must include:

- suggested name;
- target pack;
- triggers placeholder;
- non-triggers placeholder;
- inputs;
- outputs;
- safety constraints;
- quality flow.

### `classifyActionRisk`

Purpose: classify action safety.

Must return:

- risk class;
- decision;
- reasons;
- target runtime;
- scoped paths if provided.

### `previewRemoteExecution`

Purpose: side-effect-free preview.

Must include Trust Gate output and must not imply execution.

### `executeRemoteCommand`

Purpose: future approved execution.

Current required behavior: return disabled unless a trusted adapter and approval flow are implemented.

## Error handling

Prefer returning `ok: false` envelope over raising raw exceptions for expected input errors.

Examples:

- no packs provided;
- unsupported operation;
- unknown dispatch action;
- remote execute disabled.

## Alignment rule

Any new gateway behavior must be checked against:

```text
online-gpt/ALIGNMENT.md
online-gpt/SOURCE-OF-TRUTH.md
```
