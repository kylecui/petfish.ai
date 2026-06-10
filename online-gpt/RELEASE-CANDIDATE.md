# PEtFiSh Companion GPT Release Candidate

This document freezes the current `online-gpt/` release-candidate scope.

## RC identity

```text
Name: PEtFiSh Companion GPT
Branch: dev
Scope: P0 Standalone + P1 Gateway-only
P2 Adapter Mode: boundary/regression only
```

## RC principle

PEtFiSh Companion GPT is an independent online companion runtime for the PEtFiSh ecosystem.

It must be useful without:

- OpenCode;
- Codex;
- Antigravity;
- Cursor;
- GitHub Copilot;
- Windsurf;
- local daemon;
- local filesystem access;
- local execution adapter.

## Included in this RC

### P0 Standalone Mode

Included:

- GPT instructions;
- Knowledge bundle plan;
- pack/profile reasoning;
- skill design workflow;
- install command rendering;
- quality-gate planning;
- anti-sycophancy discipline;
- source-of-truth discipline;
- **ChatGPT Project as first-class online PEtFiSh runtime;**
- **`runtime-contract.md` defining online runtime guarantees;**
- **`review-online` profile for ChatGPT Project code reviews;**
- **`project-instructions/code-review.md` template;**
- **`docs/online-projects.md` user-facing documentation.**

### P1 Gateway Mode

Included:

- gateway-only OpenAPI schema;
- dispatcher skeleton;
- stdlib HTTP server;
- HTTP smoke script;
- route/profile/catalog/install/trust/skill endpoints;
- health and version endpoints;
- module envelope contract.

### P2 Adapter Mode

Included only as boundary/regression material:

- remote-control Knowledge is excluded from first GPT upload;
- remote execution is disabled;
- direct local control is forbidden;
- preview-only behavior is allowed for boundary testing.

## Excluded from first release

- Full `actions/openapi.yaml` import;
- `knowledge/07-remote-control-model.md` upload;
- local daemon connection;
- desktop bridge;
- OpenCode/Codex/Antigravity execution;
- remote execute enablement;
- autonomous local workspace modification.

## Validated by local team

Reported local validation:

```text
P0/P1 primary acceptance: 5/5 PASS
P2 boundary regression: 3/3 PASS
Gateway API smoke: PASS
Gateway-only OpenAPI schema validation: PASS
server.py and gateway-only OpenAPI health/version path alignment: DONE
remote execution: disabled
```

## Required pre-publication checks

Before sharing the GPT outside the core team:

- [ ] `PRIORITY-GUARDRAIL.md` reviewed;
- [ ] `PUBLISH-CHECKLIST.md` completed;
- [ ] P0 Preview prompts pass without Actions;
- [ ] P1 Gateway Actions imported from `actions/openapi.gateway-only.yaml` only;
- [ ] production Gateway URL replaces placeholder;
- [ ] API authentication configured;
- [ ] `remote_execute_enabled=false` verified;
- [ ] no P2 prompt in conversation starters;
- [ ] no P2 Knowledge file uploaded to first GPT.

## RC decision

The current RC is ready for GPT Builder configuration and Gateway staging deployment.

It is not ready for Adapter Mode execution.
