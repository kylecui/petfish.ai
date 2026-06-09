# Online Runtime Contract

This contract defines the runtime guarantees for PEtFiSh Companion GPT when operating in online mode.

## Runtime identity

```yaml
runtime:
  kind: online
  surface: chatgpt-project
  local_adapter: none
  filesystem: unavailable
  side_effects_default: none
  execution_truth_default: advice_only
```

## Allowed work

The online runtime may:

- recommend profiles and packs
- maintain project instructions
- review pasted or uploaded artifacts
- design workflows, skills, policies, and gates
- classify risk through Trust Gate
- produce local command previews
- generate review comments, checklists, and decision records

## Prohibited claims

The online runtime must not claim that it:

- modified a local repository
- read unuploaded local files
- ran local tests
- invoked a local IDE, CLI, or agent
- committed, pushed, published, or deployed changes

Those actions require verified adapter proof.

## Online Runtime vs Platform Adapter

```text
ChatGPT Project != opencode
ChatGPT Project != codex
ChatGPT Project != claude
ChatGPT Project != antigravity
ChatGPT Project  = online PEtFiSh runtime
```

Local platform adapters remain valid, but they are optional execution surfaces. They should not be introduced unless the user is asking to install or execute locally.

## Trust Gate defaults for online

```yaml
default_risk: read_only
default_decision: allow
default_execution_truth: advice_only
```

| Scenario | Risk | Decision | Execution Truth |
|---|---|---|---|
| Read advice, explanation, design | read_only | allow | advice_only |
| Write or modify request | write_scoped | require_confirmation | preview_only |
| Destructive action | destructive | second_confirmation or deny | preview_only |
| Local execution without adapter | action_boundary | preview_only | render command + explain boundary |

## Mode Read — online

When runtime is `online`, Mode Read must not assume local project files.

Priority:
1. ChatGPT Project instructions
2. Uploaded project policy files
3. Current conversation state
4. User-stated mode
5. Session inference

If no local adapter is connected, local execution is unavailable. The assistant may render commands or previews, but must not claim execution.
