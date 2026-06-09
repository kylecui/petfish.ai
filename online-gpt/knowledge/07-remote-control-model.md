# Remote Control Model

This file is intended for GPT Knowledge upload.

## Positioning

PEtFiSh Companion GPT can become a control surface for local agents, but it must not become an unguarded remote shell.

## Required chain

```text
ChatGPT GPT
    -> GPT Action
    -> PEtFiSh Online Gateway
    -> Trust Gate
    -> Remote preview
    -> User approval
    -> Local daemon
    -> Runtime adapter
    -> OpenCode / Codex / Antigravity
```

## Runtime metadata

Remote-control requests should name or infer:

```json
{
  "host": "windows | linux | macos",
  "runtime": "native | wsl | hyperv | vmware | ssh",
  "agent": "opencode | codex | antigravity | universal",
  "project_alias": "petfish.ai"
}
```

## Preview contract

A preview must include:

- target runtime;
- target project alias;
- proposed task or command;
- files or resources likely affected;
- risk classification;
- approval requirement;
- expected result;
- rollback hint.

## Execute contract

Execution requires:

- connected trusted daemon;
- approval token or equivalent confirmation;
- audit trace;
- log capture;
- result summary;
- explicit statement of what was and was not verified.

## Disabled is valid

A remote execution endpoint may exist but return disabled. This is valid when the module contract is present but the trusted adapter is not connected.
