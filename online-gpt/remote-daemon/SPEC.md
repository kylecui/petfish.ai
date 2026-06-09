# PEtFiSh Remote Daemon Specification

This document defines the local daemon contract for future PEtFiSh Companion GPT remote-control integration.

The daemon is not required for command rendering, catalog search, or skill design. It is required only when the online GPT needs verified local preview or execution.

## Position in architecture

```text
ChatGPT GPT
  -> PEtFiSh Online Gateway
  -> Trust Gate
  -> Relay / Auth Layer
  -> petfish_remote daemon
  -> Runtime adapter
  -> OpenCode / Codex / Antigravity / local filesystem
```

## Runtime registration

The daemon should register runtime metadata:

```json
{
  "daemon_id": "host-uuid-or-generated-id",
  "host_os": "windows",
  "runtime": "wsl",
  "agents": ["opencode", "codex"],
  "projects": [
    {
      "alias": "petfish.ai",
      "path_hint": "masked-or-local-only",
      "allowed_operations": ["preview", "read", "scoped_write"]
    }
  ]
}
```

`path_hint` should avoid exposing sensitive absolute paths unless the user opts in.

## Preview endpoint

Preview must be side-effect-free.

Request:

```json
{
  "project_alias": "petfish.ai",
  "agent": "opencode",
  "task": "run quality gate for online-gpt",
  "mode": "preview"
}
```

Response:

```json
{
  "ok": true,
  "result_level": "previewed",
  "proposed_commands": [],
  "affected_paths": [],
  "risk": "read_only",
  "approval_required": false,
  "notes": []
}
```

## Execute endpoint

Execution requires:

- trusted daemon identity;
- user approval;
- Trust Gate decision;
- scoped project alias;
- audit trace.

Request:

```json
{
  "project_alias": "petfish.ai",
  "agent": "opencode",
  "task": "run quality gate for online-gpt",
  "approval_token": "opaque-token",
  "mode": "execute"
}
```

Response:

```json
{
  "ok": true,
  "result_level": "audit_logged",
  "trace_id": "trace-id",
  "status": "success | partial | failed",
  "logs_summary": "...",
  "changed_resources": [],
  "verification": [],
  "rollback_hint": null
}
```

## Secret handling

The daemon must:

- mask environment variables by default;
- never send raw credentials to the online GPT;
- redact common token, key, password, and cookie patterns;
- allow user-controlled explicit reveal only outside the GPT channel.

## Adapter classes

| Adapter | Purpose |
|---|---|
| `opencode` | interact with OpenCode sessions or project commands |
| `codex` | interact with Codex-compatible project layout |
| `antigravity` | interact with Antigravity-compatible project layout |
| `shell-readonly` | inspect files and state without mutation |
| `shell-scoped` | execute approved scoped commands |

## Disabled-by-default rule

A daemon implementation should ship with execution disabled until:

- authentication is configured;
- project aliases are registered;
- approval policy is configured;
- audit logging is enabled;
- a preview succeeds.
