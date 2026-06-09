# GPT Configuration Package

This document defines the exact package of files used to configure PEtFiSh Companion GPT.

It is a packaging guide, not a new capability definition.

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
online-gpt/knowledge/07-remote-control-model.md
online-gpt/knowledge/08-failure-playbook.md
online-gpt/knowledge/09-skill-workbench-reference.md
online-gpt/knowledge/10-trust-gate-reference.md
```

Do not upload `gateway/`, `tools/`, local test notes, raw logs, secrets, or private runtime configuration.

## Actions package

Import:

```text
online-gpt/actions/openapi.yaml
```

Read before enabling:

```text
online-gpt/actions/action-policy.md
online-gpt/actions/README.md
```

Replace the placeholder server URL with the deployed gateway URL.

## Manual GPT preview checklist

After configuration, test these prompts:

```text
我要在 OpenCode 项目里安装 security profile。
```

```text
帮我设计一个新的 PEtFiSh skill。
```

```text
预览让本地 OpenCode 执行一次 gate，但不要真正执行。
```

```text
online-gpt 是否可以新增自己的官方 pack alias？
```

Expected behavior:

- preserves core PEtFiSh semantics;
- command rendering does not claim execution;
- remote preview does not execute;
- new pack aliases require core or market source of truth;
- evaluative prompts use critical review.
