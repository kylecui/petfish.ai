# Trust Gate Reference

This file is intended for GPT Knowledge upload.

## Purpose

Trust Gate is the online-gpt action firewall. It decides whether a proposed action is safe to allow, should be previewed, needs confirmation, needs second confirmation, or should be denied.

## Risk classes

| Risk | Meaning | Default decision |
|---|---|---|
| `read_only` | query, inspect, summarize | allow |
| `write_scoped` | create or modify known files | require confirmation |
| `networked` | download, call service, external API | preview or confirmation |
| `destructive` | delete, reset, uninstall, overwrite broad state | second confirmation or deny |
| `secret_sensitive` | credentials, tokens, private keys | mask and restrict |
| `publish_release` | tag, release, publish, push external state | require release discipline |

## Decisions

| Decision | Meaning |
|---|---|
| `allow` | safe to proceed without extra approval |
| `preview_only` | side-effect-free preview allowed |
| `require_confirmation` | user must confirm before execution |
| `require_second_confirmation` | high-risk action needs explicit double confirmation |
| `deny` | do not execute |

## Required fields for risky actions

For write, destructive, publish, or remote execution actions, the GPT should collect or infer:

- target runtime;
- project alias;
- affected paths;
- proposed command or task;
- expected side effects;
- rollback hint;
- approval status.

## Deny cases

Deny when:

- deletion or reset scope is ambiguous;
- user asks to bypass logging or approval;
- secrets would be printed back;
- remote execution adapter is missing but the request requires execution;
- publish/release action lacks explicit target and release discipline.

## Output contract

Trust Gate output should include:

```json
{
  "risk": "destructive",
  "decision": "deny",
  "reasons": ["Destructive action has no explicit scoped path list."],
  "paths": [],
  "target_runtime": "opencode"
}
```

## GPT Companion behavior

The GPT should not make Trust Gate invisible. For risky actions, it should summarize the risk class and decision before giving next steps.
