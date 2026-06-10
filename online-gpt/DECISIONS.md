# Architecture Decisions

## ADR-001: Standalone first, Gateway second, Adapter deferred

Status: accepted

Date: 2026-06-09

## Context

`online-gpt/` is being built as the GPT version of `petfish.ai`.

The GPT version must operate independently. It must not require OpenCode, Codex, Antigravity, local IDE/CLI tools, desktop clients, or local daemons.

Adapter Mode overlaps with 胖鱼遥控器 but is not identical. 胖鱼遥控器 is closer to the relationship between Codex's GPT and a desktop/client execution surface. That product direction should not dominate the current `online-gpt` work.

Server resources for Gateway Mode are available, so Gateway APIs are a practical second priority after Standalone Mode.

## Decision

Priority is fixed as:

```text
P0. Standalone Mode
P1. Gateway Mode
P2. Adapter Mode
```

## Consequences

### Standalone Mode must work first

The first GPT configuration uses:

- Instructions;
- Knowledge;
- built-in GPT capabilities.

It must support explanation, pack/profile recommendation, skill design, command rendering, test planning, critical review, and source-of-truth discipline.

### Gateway Mode is second

Gateway Mode uses GPT Actions and server-side APIs for catalog, profile, install rendering, skill design, and Trust Gate classification.

Gateway Mode does not require IDE/CLI tools.

### Adapter Mode is deferred

Adapter Mode remains documented only for future compatibility.

The first GPT configuration should not import remote execution endpoints.

Use:

```text
online-gpt/actions/openapi.gateway-only.yaml
```

not the full:

```text
online-gpt/actions/openapi.yaml
```

unless Adapter Mode becomes an explicit workstream.

## Guardrails

- Do not make remote daemon work part of Standalone acceptance.
- Do not make OpenCode/Codex/Antigravity required for Gateway acceptance.
- Do not upload remote-control Knowledge in the first GPT configuration unless specifically testing Adapter Mode.
- Do not expose `/v1/remote/execute` in the first public GPT Action schema.
- Do not let online-gpt become a semantic fork of PEtFiSh.
