# PEtFiSh Online Projects

PEtFiSh supports two project modes:

1. **Local project mode** — install packs, skills, and agents into IDE/CLI environments
2. **Online project mode** — use a ChatGPT Project as a first-class PEtFiSh runtime

## Local project mode

Local project mode installs packs, skills, commands, MCP servers, plugins,
and instruction fragments into local agent environments.

Examples: OpenCode, Codex, Claude Code, Cursor, Copilot, Windsurf,
Antigravity, and Universal adapters.

```bash
uv run https://raw.githubusercontent.com/kylecui/petfish.ai/master/install.py --pack context,petfish --platform opencode --target .
```

## Online project mode

Online project mode treats a hosted chat surface, such as a ChatGPT Project,
as the project runtime. It does not require a local adapter.

```yaml
runtime:
  kind: online
  surface: chatgpt-project
  local_adapter: none
```

No installation is needed. Packs are referenced semantically — the GPT
applies their discipline through Instructions, Knowledge, and Gateway Actions.

## What online projects can do

- maintain project instructions
- review uploaded or pasted artifacts
- apply Companion Gateway discipline
- recommend profiles and packs
- run Trust Gate classification
- generate local command previews
- produce review policies, comments, and decision records

## What online projects cannot do by default

- read local files that were not uploaded
- run local tests
- modify repositories
- invoke local IDE or CLI agents
- commit, push, deploy, or publish

Those require a verified adapter result.

## Profile example: review-online

```yaml
profile: review-online
packs:
  core:
    - companion
    - context
    - petfish
    - testdocs
    - trust
  optional:
    - calibrate
    - deploy
```

## When to use which mode

| Scenario | Mode |
|---|---|
| I want to install PEtFiSh in my IDE | Local |
| I want to review code in a ChatGPT Project | Online |
| I want to run a quality gate on a skill | Local (or Online + Gateway) |
| I want to deploy a service | Local |
| I want to design a skill contract | Either |
| I want to classify risk of a change | Either |

Online mode is not "simpler local." It is a separate runtime with its own
contracts, boundaries, and execution truth defaults.
