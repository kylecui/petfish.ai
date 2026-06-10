# Principles

This document is the top-level product and architecture principle set for `online-gpt/`.

## Principle 1: GPT version is independently operable

`online-gpt/` is the GPT version of `petfish.ai`.

It must be useful without:

- Codex;
- Antigravity;
- OpenCode;
- Cursor;
- GitHub Copilot;
- Windsurf;
- any local IDE/CLI agent;
- any local daemon;
- any local filesystem access.

The GPT version must independently support:

- PEtFiSh explanation;
- Companion Gateway explanation;
- profile and pack recommendation;
- skill design;
- trigger and non-trigger design;
- install/upgrade/uninstall command rendering;
- quality-gate planning;
- critical review and anti-sycophancy;
- source-of-truth alignment;
- local-test planning;
- GPT Builder configuration guidance.

## Principle 2: IDE/CLI tools are optional execution adapters

Codex, Antigravity, OpenCode, Cursor, GitHub Copilot, Windsurf, and similar tools are optional execution targets.

They are not required dependencies of the GPT version.

Correct dependency model:

```text
PEtFiSh Companion GPT
  can run independently
  may use Online Gateway
  may use optional execution adapters
```

Incorrect dependency model:

```text
PEtFiSh Companion GPT
  requires OpenCode/Codex/Antigravity to be useful
```

## Principle 3: Core PEtFiSh remains source of truth

Independent operation does not mean semantic fork.

The GPT version may independently operate, but it must remain aligned with core PEtFiSh semantics.

It must not redefine:

- official pack aliases;
- profile-to-pack mapping;
- Companion Gateway semantics;
- platform adapter meanings;
- skill lifecycle;
- quality gate requirements;
- installer semantics;
- release discipline.

## Principle 4: Three operating modes

`online-gpt/` has three ordered modes:

```text
P0. Standalone Mode
P1. Gateway Mode
P2. Adapter Mode
```

Priority is intentional.

Standalone Mode and Gateway Mode must remain useful even if Adapter Mode never ships.

## Principle 5: Gateway Mode is online API mode, not local execution mode

Gateway Mode may provide:

- deterministic routing;
- catalog search;
- profile suggestion;
- command rendering;
- skill contract rendering;
- Trust Gate classification;
- side-effect-free previews.

Gateway Mode must not claim local execution unless an Adapter Mode proof exists.

## Principle 6: Adapter Mode is optional and controlled

Adapter Mode connects GPT to local or remote execution environments.

Adapter Mode requires:

- Trust Gate;
- approval flow;
- scoped project alias;
- secret masking;
- audit trace;
- execution proof.

Remote execution is disabled by default.

## Principle 7: Generated commands are not executed actions

The GPT version may render commands independently.

It must not claim that rendered commands were executed.

Use execution truth labels:

- `advice_only`;
- `command_rendered`;
- `dry_run`;
- `previewed`;
- `executed`;
- `audit_logged`.

Only Adapter Mode with verified result may produce `executed` or `audit_logged`.

## Principle 8: Degrade gracefully

Every feature must declare its mode.

If an Adapter Mode dependency is unavailable, the GPT should degrade to Gateway Mode or Standalone Mode rather than fail generically.

Example:

```text
User asks to execute local OpenCode task.
No daemon is connected.
GPT returns preview/command plan and says execution is unavailable.
```

## Principle 9: Do not optimize for remote control first

Remote control is useful, but it is not the core value of the GPT version.

The first product value is:

```text
PEtFiSh knowledge + pack/profile reasoning + skill design + safe command rendering + quality-gate discipline
```

Remote execution is a later optional extension.

## Principle 10: Publish only after baseline independence is proven

Before publication, verify:

- Standalone Mode works in GPT Builder without Actions;
- Gateway Mode works through OpenAPI if Actions are enabled;
- Adapter Mode remains optional and disabled unless configured;
- source-of-truth alignment checks pass;
- local tests pass.
