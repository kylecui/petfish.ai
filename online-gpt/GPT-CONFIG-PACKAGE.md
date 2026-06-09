# GPT Configuration Package

This document defines the exact package of files used to configure PEtFiSh Companion GPT.

It is a packaging guide, not a new capability definition.

## Configuration priority

Configure in this order:

```text
P0. Standalone Mode: Instructions + Knowledge only
P1. Gateway Mode: add GPT Actions against PEtFiSh Online Gateway
P2. Adapter Mode: defer remote/local execution adapters
```

Standalone Mode must be useful before any Actions are enabled.

## Instructions package

Primary instruction source:

```text
online-gpt/instructions/petfish-companion.instructions.md
```

Supporting instruction contracts:

```text
online-gpt/instructions/safety-boundary.md
online-gpt/instructions/answer-contract.md
online-gpt/instructions/anti-sycophancy.md
```

When copying into GPT Builder, merge the supporting contracts into the main instruction field in compressed form. Do not rely on Knowledge retrieval for behavior-critical rules.

## Knowledge package

Upload these files:

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

Optional, only when discussing future Adapter Mode:

```text
online-gpt/knowledge/07-remote-control-model.md
```

Do not upload `gateway/`, `tools/`, local test notes, raw logs, secrets, or private runtime configuration.

## Actions package for Gateway Mode

For current Gateway Mode, import:

```text
online-gpt/actions/openapi.gateway-only.yaml
```

This schema intentionally excludes Adapter Mode remote endpoints.

Read before enabling:

```text
online-gpt/actions/action-policy.md
online-gpt/actions/README.md
```

Replace the placeholder server URL with the deployed gateway URL.

## Full contract schema, not default

The full schema remains available as:

```text
online-gpt/actions/openapi.yaml
```

Use it only when Adapter Mode becomes an active workstream. Do not import it into the first public GPT configuration.

## Manual GPT preview checklist

After Standalone configuration, test these prompts without Actions:

```text
什么是 PEtFiSh Companion Gateway？
```

```text
我要做一个 AI security research 项目，需要文献、PPT、部署和安全审计，应该装哪些 packs？
```

```text
帮我设计一个新的 PEtFiSh skill。
```

```text
请帮我在本地安装这些 pack。
```

Expected behavior:

- preserves core PEtFiSh semantics;
- command rendering does not claim execution;
- skill design includes triggers, non-triggers, evals, and gate plan;
- new pack aliases require core or market source of truth;
- evaluative prompts use critical review.

After Gateway Actions are enabled, test:

```text
通过 Gateway 帮我推荐 security research 项目的 packs。
```

```text
通过 Gateway 渲染 OpenCode security profile 的安装命令。
```

Expected behavior:

- calls Gateway APIs where appropriate;
- still does not claim local execution;
- does not require OpenCode/Codex/Antigravity to be installed.
