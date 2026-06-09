# PEtFiSh Companion GPT Module Contracts

This document defines the modules of the online GPT subsystem. It is not a roadmap. It is the module contract registry.

A module may be implemented by a mock, read-only, dry-run, remote-preview, or real adapter. The contract remains stable.

## Common module response

Every module returns this envelope:

```json
{
  "ok": true,
  "module": "catalog",
  "mode": "dry_run",
  "result_level": "command_rendered",
  "data": {},
  "warnings": [],
  "errors": [],
  "audit": {
    "trace_id": "optional",
    "policy": "optional"
  }
}
```

`result_level` values:

- `advice_only`
- `command_rendered`
- `dry_run`
- `previewed`
- `executed`
- `audit_logged`

## Module A: Companion Identity

Purpose: keep the GPT shell aligned with PEtFiSh behavior.

Inputs:

- user message;
- active conversation context;
- available Actions;
- user-provided project facts.

Outputs:

- response contract;
- execution boundary;
- refusal or warning when needed.

Policy:

- never claim local execution without adapter proof;
- prefer precise commands over vague advice;
- use anti-sycophancy on evaluation requests.

Files:

- `instructions/petfish-companion.instructions.md`
- `instructions/answer-contract.md`
- `instructions/safety-boundary.md`
- `instructions/anti-sycophancy.md`

## Module B: Knowledge Compiler

Purpose: convert PEtFiSh repository knowledge into GPT-uploadable reference files.

Inputs:

- README;
- docs;
- pack manifests;
- platform registry;
- quality-gate docs;
- selected architecture notes.

Outputs:

- compact Markdown files under `knowledge/`;
- no secrets;
- no raw local state;
- no behavior rules that belong in instructions.

Policy:

- knowledge is reference only;
- instructions override knowledge;
- stale generated files must be regenerated before GPT publication.

## Module C: Companion Kernel

Purpose: route user intent through the online Companion Gateway.

Inputs:

```json
{
  "user_message": "...",
  "active_context": "...",
  "installed_packs": ["context", "petfish"],
  "platform": "opencode",
  "project_profile": "security",
  "mode": {
    "depth": "balanced",
    "rigor": false
  }
}
```

Outputs:

```json
{
  "intent": "install_plan",
  "topic_risk": "low",
  "required_modules": ["catalog", "installer"],
  "recommended_packs": ["deploy", "testdocs", "trust"],
  "action_policy": "dry_run",
  "response_contract": "plan_plus_command"
}
```

Policy:

- default to dry-run for side-effectful actions;
- trigger Trust Gate before write/destructive remote execution;
- ask less, infer more, but do not fake unavailable state.

## Module D: Capability Router

Purpose: map request categories to capability modules.

Routes:

| Intent | Modules |
|---|---|
| project initialization | profiler, catalog, installer |
| pack recommendation | profiler, catalog |
| install/upgrade/uninstall | installer, trust_gate |
| skill authoring | skill_workbench |
| skill lint/audit/gate | skill_workbench, trust_gate |
| remote execution | remote_control, trust_gate |
| evaluation/review | companion kernel, anti-sycophancy |
| platform question | catalog, platform adapter reference |

Failure mode:

- unknown intent returns `advice_only` plus nearest module candidates.

## Module E: Catalog / Market Brain

Purpose: know packs, skills, aliases, platforms, and install resolution.

Inputs:

- keyword;
- project profile;
- platform;
- installed pack list;
- market metadata.

Outputs:

- matching packs;
- matching skills;
- install aliases;
- recommendation reason;
- command-render request.

Policy:

- core packs resolve from petfish.ai;
- optional packs may resolve through petfish-market;
- explain why a pack is included or excluded.

## Module F: Project Profiler

Purpose: infer profile and pack set from project intent.

Inputs:

- project description;
- platform;
- OS/runtime constraints;
- requested domains;
- risk sensitivity.

Outputs:

- recommended profile;
- pack set;
- exclusions;
- assumptions;
- install-render request.

Policy:

- do not blindly map all complex projects to `comprehensive`;
- prefer minimal sufficient pack set;
- include `context` for multi-topic or long-running projects;
- include `trust` for security-sensitive or remote-control projects.

## Module G: Skill Workbench

Purpose: design and validate PEtFiSh skills.

Workflow:

```text
idea -> contract -> SKILL.md -> triggers -> examples -> scripts -> lint -> audit -> eval -> gate
```

Inputs:

- skill goal;
- target pack;
- platform;
- trigger examples;
- safety constraints.

Outputs:

- skill contract;
- file tree;
- SKILL.md draft;
- script skeletons;
- trigger eval cases;
- lint/audit/gate result.

Policy:

- define non-triggers as well as triggers;
- every generated skill needs at least one success example and one misuse example;
- any script that touches files must declare write scope.

## Module H: Remote Control / Local Bridge

Purpose: allow GPT to coordinate local OpenCode, Codex, Antigravity, and compatible agents through a trusted bridge.

Inputs:

- action intent;
- target runtime;
- repository path alias;
- command or task payload;
- approval token when required.

Outputs:

- preview;
- risk classification;
- execution status;
- logs;
- summarized result;
- rollback hint.

Policy:

- remote execution defaults to disabled or preview-only;
- write and destructive actions require approval;
- secrets are masked;
- every execution receives an audit trace.

## Module I: Trust Gate / Action Firewall

Purpose: classify and constrain actions before they reach local or remote execution.

Risk levels:

- `read_only`
- `write_scoped`
- `networked`
- `destructive`
- `secret_sensitive`
- `publish_release`

Decisions:

- `allow`
- `preview_only`
- `require_confirmation`
- `require_second_confirmation`
- `deny`

Policy:

- destructive unscoped commands are denied;
- secret-bearing payloads must be masked;
- release/publish actions require release discipline check;
- local shell access is never implicit.

## Module J: Evaluation Harness

Purpose: protect routing, safety, knowledge, and regression behavior.

Eval families:

- routing;
- safety;
- knowledge;
- regression.

Each eval case should define:

```json
{
  "input": "...",
  "expected_route": "install_plan",
  "must_include": [],
  "must_not_include": [],
  "risk_level": "low"
}
```

Policy:

- evals must test behavior and boundaries, not only answer content;
- any prompt/instruction update should run the relevant eval subset;
- failed evals produce a fix note before prompt changes are accepted.
