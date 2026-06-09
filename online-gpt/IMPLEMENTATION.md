# Implementation Assembly Plan

This is not a POC/MVP roadmap. It is the assembly plan for the complete PEtFiSh Companion GPT subsystem.

The system shape is fixed first. Each module is then implemented against its contract.

## Assembly principle

A module can be:

- `contract_only`: documented but not implemented;
- `mock`: deterministic placeholder;
- `dry_run`: validates and renders without side effects;
- `readonly`: queries external state without mutation;
- `preview`: asks a trusted adapter for a side-effect-free plan;
- `execute`: performs approved side effects.

The module contract must not change when moving between these modes.

## Assembly 1: Contract freeze

Files:

```text
online-gpt/README.md
online-gpt/ARCHITECTURE.md
online-gpt/MODULES.md
online-gpt/actions/openapi.yaml
```

Acceptance:

- every module has purpose, input, output, policy, and failure modes;
- every Action endpoint maps to a module;
- remote execution endpoint exists but may be disabled;
- module response envelope is stable.

## Assembly 2: GPT behavior layer

Files:

```text
online-gpt/instructions/petfish-companion.instructions.md
online-gpt/instructions/safety-boundary.md
online-gpt/instructions/answer-contract.md
online-gpt/instructions/anti-sycophancy.md
```

Acceptance:

- GPT distinguishes command rendering from execution;
- answer contracts are explicit;
- evaluation requests trigger anti-sycophancy;
- remote execution requires preview and trust classification.

## Assembly 3: Knowledge compiler output

Files:

```text
online-gpt/knowledge/*.md
```

Acceptance:

- knowledge is reference only;
- no secrets;
- pack/profile/platform/install facts are compact and searchable;
- behavior rules remain in instructions.

## Assembly 4: Deterministic gateway skeleton

Files:

```text
online-gpt/gateway/*.py
online-gpt/gateway/modules/*.py
```

Acceptance:

- `python online-gpt/gateway/app.py` runs as a smoke demo;
- all OpenAPI operation IDs map to dispatcher actions;
- remote execute returns disabled unless adapter is connected;
- Trust Gate can classify common write, publish, secret, and destructive classes.

## Assembly 5: Eval harness

Files:

```text
online-gpt/evals/**/*.jsonl
online-gpt/gateway/eval_runner.py
```

Acceptance:

- eval runner loads JSONL cases;
- routing cases assert expected route;
- safety cases assert forbidden claims are absent;
- regression cases protect anti-sycophancy.

## Assembly 6: HTTP runtime wrapper

Candidate wrappers:

- FastAPI;
- Cloudflare Workers;
- lightweight serverless function;
- MCP server bridge.

Acceptance:

- exposes the OpenAPI contract;
- validates payloads;
- returns module envelope;
- logs trace IDs without storing secrets.

## Assembly 7: Catalog and market integration

Acceptance:

- reads local pack index or petfish-market index;
- resolves core versus optional packs;
- renders branch-aware install commands;
- supports community pack lookup.

## Assembly 8: Skill Workbench real rendering

Acceptance:

- creates full skill file trees in dry-run;
- can render scoped patches;
- can run lint/audit/gate adapters;
- never publishes without gate result.

## Assembly 9: Remote preview adapter

Acceptance:

- local daemon registers runtime metadata;
- remote preview returns proposed task plan;
- Trust Gate classification is attached;
- approval requirement is explicit.

## Assembly 10: Remote execution adapter

Acceptance:

- disabled by default;
- requires approval token;
- masks secrets;
- captures logs;
- emits audit trace;
- returns partial failure honestly.

## Definition of done

The subsystem is ready to wire into GPT Builder when:

- GPT instructions are configured;
- knowledge bundle is uploaded;
- Actions schema imports;
- gateway endpoint responds to all defined operations;
- eval runner passes routing, safety, knowledge, and regression suites;
- remote execute is either disabled or fully approval-protected.
