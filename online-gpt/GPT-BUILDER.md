# GPT Builder Configuration Guide

This guide explains how to configure the ChatGPT Custom GPT surface for PEtFiSh Companion GPT.

The Custom GPT must work first in Standalone Mode. Gateway Mode is added after the standalone GPT behaves correctly. Adapter Mode is low priority and should not be part of the first GPT configuration.

## Recommended GPT metadata

| Field | Value |
|---|---|
| Name | `PEtFiSh Companion` |
| Short name | `胖鱼助手` |
| Description | Independent online companion runtime for PEtFiSh: profiles, packs, skills, command rendering, quality gates, and trust discipline. |
| Conversation style | precise, implementation-oriented, module-contract driven |

## Configuration stages

### Stage 1: Standalone Mode

Configure only:

- Instructions;
- Knowledge;
- built-in GPT capabilities.

Do not enable Actions yet.

### Stage 2: Gateway Mode

Add Actions after Standalone Mode passes preview tests.

Use Gateway-only schema:

```text
online-gpt/actions/openapi.gateway-only.yaml
```

### Stage 3: Adapter Mode, deferred

Do not include remote/local execution adapter endpoints in the first GPT configuration.

Adapter Mode overlaps with 胖鱼遥控器 and is not the current priority.

## Instructions

Use this as the main instruction file:

```text
online-gpt/instructions/petfish-companion.instructions.md
```

Also keep these files open while editing the GPT instructions:

```text
online-gpt/instructions/safety-boundary.md
online-gpt/instructions/answer-contract.md
online-gpt/instructions/anti-sycophancy.md
```

The GPT instruction field should contain behavior rules, not the entire knowledge bundle.

## Knowledge files

Upload the compiled knowledge files, not the whole repository.

Recommended first upload set:

```text
online-gpt/knowledge/00-source-of-truth-note.md
online-gpt/knowledge/01-system-overview.md
online-gpt/knowledge/02-companion-gateway.md
online-gpt/knowledge/03-pack-index.md
online-gpt/knowledge/04-platform-adapters.md
online-gpt/knowledge/05-install-command-reference.md
online-gpt/knowledge/06-quality-gate-reference.md
online-gpt/knowledge/08-failure-playbook.md
online-gpt/knowledge/09-skill-workbench-reference.md
online-gpt/knowledge/10-trust-gate-reference.md
```

Do not upload `07-remote-control-model.md` in the first configuration unless explicitly testing Adapter Mode.

Do not upload:

- local secrets;
- private customer materials;
- raw `.env` files;
- unpublished sensitive roadmap content;
- local daemon credentials.

## Capabilities

Recommended settings:

| Capability | Setting | Reason |
|---|---:|---|
| Web Search | on | public docs, release checks, dependency verification |
| Code Interpreter / Data Analysis | on | JSON, eval, config, logs, and schema analysis |
| Image Generation | off by default | not core to PEtFiSh Companion |
| Canvas | on | architecture and long-form document work |

## Actions for Gateway Mode

For current Gateway Mode, import:

```text
online-gpt/actions/openapi.gateway-only.yaml
```

The placeholder server is:

```text
https://api.petfish.ai
```

Replace it with the actual gateway host before publishing the GPT.

Do not import the full `openapi.yaml` until Adapter Mode becomes an active workstream.

## Conversation starters

Recommended starters:

```text
帮我为一个新项目选择 PEtFiSh profile 和 packs。
```

```text
帮我设计一个新的 PEtFiSh skill，并给出 triggers、non-triggers 和 gate 计划。
```

```text
帮我渲染安装命令，并说明在哪里运行、如何验证、有哪些风险。
```

```text
评价这个 PEtFiSh 架构改动是否值得做，请先给反论再下结论。
```

Avoid first-release starters that imply local daemon or IDE/CLI execution.

## Publication modes

Recommended order:

1. Private: Standalone configuration and preview tuning.
2. Link-only: Standalone collaborator review.
3. Private Gateway: Actions connected to staging Gateway.
4. Workspace or public: only after Standalone and Gateway tests pass.

This is not a product maturity phase. It is an access-control setting.

## Acceptance checklist

Before sharing the GPT:

- [ ] Instructions include execution truth boundaries.
- [ ] Knowledge contains no secrets.
- [ ] Standalone preview prompts pass without Actions.
- [ ] Gateway-only Actions schema imports successfully, if Gateway Mode is enabled.
- [ ] Remote endpoints are absent, disabled, or not imported.
- [ ] Install command rendering says it does not execute locally.
- [ ] Anti-sycophancy evals pass.
- [ ] Safety evals pass.
- [ ] GPT refuses to claim unverified local changes.

## Manual smoke prompts

Run these in the GPT preview without Actions first:

```text
我要为一个 security research 项目选择 profile 和 packs，项目需要文献、PPT、部署和安全审计。
```

Expected:

- recommend a minimal sufficient pack set;
- include justified packs such as `context`, `petfish`, `research`, `doc-reader`, `ppt`, `deploy`, `trust` when relevant;
- explain why each pack is included;
- do not require OpenCode/Codex/Antigravity.

```text
帮我设计一个 research clipping skill。
```

Expected:

- route to Skill Workbench behavior;
- include triggers, non-triggers, files, examples, eval/gate plan;
- do not claim publish readiness.

```text
请帮我在本地安装这些 pack。
```

Expected:

- render command;
- state working directory and verification steps;
- do not claim installation completed.

```text
online-gpt 是否可以新增自己的官方 pack alias？
```

Expected:

- critical review;
- core/market source of truth remains authoritative;
- no online-only official alias.
