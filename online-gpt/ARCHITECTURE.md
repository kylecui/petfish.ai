# PEtFiSh Companion GPT Architecture

## Purpose

PEtFiSh Companion GPT is the online companion shell for PEtFiSh. It gives ChatGPT a disciplined interface into PEtFiSh without pretending that ChatGPT itself is the local execution environment.

The architecture keeps the core companion logic reusable across:

- ChatGPT Custom GPT
- future ChatGPT Apps / MCP frontends
- web consoles
- local CLI wrappers
- remote-control surfaces

## Five-layer model

```text
┌────────────────────────────────────────────┐
│ L1. Companion Interface Layer              │
│ ChatGPT GPT / ChatGPT App / Web UI         │
└────────────────────────────────────────────┘
                    │
                    ▼
┌────────────────────────────────────────────┐
│ L2. Companion Kernel                       │
│ Intent Router / Gateway Loop / Policy Core │
└────────────────────────────────────────────┘
                    │
                    ▼
┌────────────────────────────────────────────┐
│ L3. Capability Modules                     │
│ Catalog / Install / Skill / Project /      │
│ Context / Research / Deploy / Trust        │
└────────────────────────────────────────────┘
                    │
                    ▼
┌────────────────────────────────────────────┐
│ L4. Adapter Layer                          │
│ GPT Actions / MCP / CLI / GitHub / Local   │
│ Daemon / Cloud Gateway                     │
└────────────────────────────────────────────┘
                    │
                    ▼
┌────────────────────────────────────────────┐
│ L5. Execution Substrate                    │
│ OpenCode / Codex / Antigravity / Repo /    │
│ File System / petfish-market / CI          │
└────────────────────────────────────────────┘
```

## Layer responsibilities

### L1. Companion Interface Layer

Owns user interaction and presentation. It must not own execution truth.

Responsibilities:

- parse user intent in conversational form;
- present plans, commands, warnings, and results;
- call Actions or Apps/MCP tools when available;
- distinguish advice, generated commands, dry-run plans, and executed actions.

### L2. Companion Kernel

Owns the online version of Companion Gateway.

Responsibilities:

- topic continuity check;
- failure signal detection;
- skill and pack sensing;
- anti-sycophancy gate;
- action risk pre-classification;
- response contract selection.

### L3. Capability Modules

Owns deterministic capability logic.

Initial modules:

- `catalog`: pack, skill, MCP, and plugin lookup;
- `installer`: install, upgrade, uninstall command rendering;
- `profiler`: map project intent to profile and pack set;
- `skill_workbench`: design, render, lint, audit, gate, eval workflow;
- `trust_gate`: classify and restrict action risk;
- `remote_control`: preview and execute local/remote actions via adapters.

### L4. Adapter Layer

Owns integration with outside systems.

Adapters may be:

- `mock`: deterministic test behavior;
- `readonly`: query-only behavior;
- `dry_run`: render commands/plans but do not execute;
- `remote_preview`: preview local execution through relay;
- `remote_execute`: perform approved execution.

### L5. Execution Substrate

Owns real state and side effects:

- repositories;
- local filesystems;
- OpenCode, Codex, Antigravity sessions;
- petfish-market;
- CI;
- remote daemons.

## Execution truth rule

The GPT shell must never claim that local state changed unless an adapter returned a verified execution result.

Valid result levels:

```text
advice_only        no side effect
command_rendered   no side effect; user must run locally
dry_run            no side effect; adapter validated shape
previewed          no side effect; remote daemon returned proposed plan
executed           side effect confirmed by adapter result
audit_logged       executed result has durable trace
```

## Module contract rule

Every module must define:

- purpose;
- inputs;
- outputs;
- policy;
- failure modes;
- examples;
- eval cases;
- replacement path from mock to real adapter.

A disabled module is allowed. An undefined module is not.

## Remote-control rule

Remote control is part of the architecture from day one, but it defaults to preview or disabled mode until a trusted local daemon is connected.

Required flow:

```text
intent compile -> risk classify -> command preview -> approval -> execution -> log capture -> result summary -> rollback hint
```

## Knowledge versus behavior

- `instructions/` contains behavior and answer contracts.
- `knowledge/` contains reference material for GPT retrieval.
- `gateway/` contains reusable deterministic logic.
- `actions/` contains external call contracts.
- `evals/` protects against prompt, routing, and safety regression.
