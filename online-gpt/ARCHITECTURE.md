# PEtFiSh Companion GPT Architecture

## Purpose

PEtFiSh Companion GPT is the GPT version of `petfish.ai`: an independent online companion runtime for PEtFiSh.

It gives ChatGPT a disciplined PEtFiSh-native operating surface without requiring OpenCode, Codex, Antigravity, or any local IDE/CLI runtime.

The architecture is optimized in this order:

```text
P0. Standalone Mode
P1. Gateway Mode
P2. Adapter Mode
```

Adapter Mode exists as a future extension only. It must not block Standalone or Gateway work.

## Mode-first architecture

### P0. Standalone Mode

```text
┌────────────────────────────────────────────┐
│ ChatGPT GPT                                │
└────────────────────────────────────────────┘
                    │
                    ▼
┌────────────────────────────────────────────┐
│ Instructions + Knowledge                   │
│ Identity / Safety / Answer Contracts       │
│ Source-of-Truth Alignment                  │
└────────────────────────────────────────────┘
                    │
                    ▼
┌────────────────────────────────────────────┐
│ Standalone Companion Capabilities          │
│ Explain / Recommend / Design / Review /    │
│ Render Commands / Produce Test Plans       │
└────────────────────────────────────────────┘
```

Standalone Mode has no external runtime dependency.

It must support:

- PEtFiSh concept explanation;
- Companion Gateway explanation;
- profile and pack recommendation;
- skill design;
- trigger and non-trigger design;
- command rendering;
- quality-gate planning;
- source-of-truth checks;
- anti-sycophancy review.

### P1. Gateway Mode

```text
┌────────────────────────────────────────────┐
│ ChatGPT GPT                                │
└────────────────────────────────────────────┘
                    │ GPT Actions
                    ▼
┌────────────────────────────────────────────┐
│ PEtFiSh Online Gateway                     │
│ Catalog / Profile / Install Render /       │
│ Skill Workbench / Trust Gate               │
└────────────────────────────────────────────┘
                    │
                    ▼
┌────────────────────────────────────────────┐
│ Online Server-Side State and Services      │
│ Pack Index / Policy / Eval / Logs          │
└────────────────────────────────────────────┘
```

Gateway Mode depends on online API infrastructure, not local IDE/CLI tools.

Gateway Mode must support:

- catalog search;
- profile suggestion;
- pack resolution;
- install command rendering;
- skill contract rendering;
- Trust Gate classification;
- server-side validation and eval when implemented.

### P2. Adapter Mode, low priority

```text
┌────────────────────────────────────────────┐
│ PEtFiSh Online Gateway                     │
└────────────────────────────────────────────┘
                    │ optional
                    ▼
┌────────────────────────────────────────────┐
│ Local Daemon / Desktop Bridge              │
└────────────────────────────────────────────┘
                    │ optional
                    ▼
┌────────────────────────────────────────────┐
│ OpenCode / Codex / Antigravity / Shell     │
└────────────────────────────────────────────┘
```

Adapter Mode overlaps with 胖鱼遥控器 but is not the same product surface.

For `online-gpt`, Adapter Mode is optional and low priority. It is only an execution extension.

## Layer model

The original five-layer model is still useful, but it must be interpreted through the priority order above:

| Layer | Standalone Mode | Gateway Mode | Adapter Mode |
|---|---|---|---|
| Interface | ChatGPT GPT | ChatGPT GPT | ChatGPT GPT |
| Kernel | instruction-level Companion discipline | server-side router | server-side router |
| Capabilities | explain, recommend, design, render, review | catalog/profile/install/trust/skill APIs | preview/execute local tasks |
| Adapter | none | GPT Actions to online API | local daemon / desktop bridge |
| Substrate | GPT config and Knowledge | online server resources | IDE/CLI/local filesystem |

## Core capability modules

Current high-priority modules:

- `catalog`: pack, skill, MCP, and plugin lookup;
- `installer`: install, upgrade, uninstall command rendering;
- `profiler`: map project intent to profile and pack set;
- `skill_workbench`: design, render, lint, audit, gate, eval workflow;
- `trust_gate`: classify action risk and policy decisions.

Low-priority future module:

- `remote_control`: preview and execute local/remote actions via optional adapters.

## Execution truth rule

The GPT shell must never claim that local state changed unless an adapter returned a verified execution result.

Valid result levels:

```text
advice_only        no side effect
command_rendered   no side effect; user must run locally
dry_run            no side effect; gateway validated shape
previewed          no side effect; preview result only
executed           side effect confirmed by adapter result
audit_logged       executed result has durable trace
```

Standalone and Gateway Mode normally operate at `advice_only`, `command_rendered`, or `dry_run`.

## Module contract rule

Every module must define:

- purpose;
- inputs;
- outputs;
- policy;
- failure modes;
- examples;
- eval cases;
- source-of-truth alignment.

A disabled module is allowed. An undefined module is not.

## Adapter Mode rule

Remote/local execution is not part of the critical path for `online-gpt`.

Adapter Mode should remain documented but de-emphasized until:

- Standalone Mode passes GPT preview tests;
- Gateway Mode APIs are deployed and tested;
- Trust Gate is reliable;
- a separate 胖鱼遥控器 direction is clarified.

## Knowledge versus behavior

- `instructions/` contains behavior and answer contracts.
- `knowledge/` contains reference material for GPT retrieval.
- `actions/` contains Gateway Mode API contracts.
- `gateway/` contains reusable deterministic online logic.
- `remote-daemon/` contains low-priority Adapter Mode contracts.
- `evals/` protects prompt, routing, safety, and source-of-truth behavior.
