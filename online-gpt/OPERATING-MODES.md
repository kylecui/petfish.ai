# Operating Modes and Priority

`online-gpt/` is the GPT version of `petfish.ai`.

It is an independent online companion runtime for the PEtFiSh ecosystem. IDE/CLI agents are optional execution adapters, not required dependencies.

## Priority order

```text
P0. Standalone Mode
P1. Gateway Mode
P2. Adapter Mode
```

This priority order is a product and architecture constraint.

Standalone Mode and Gateway Mode must remain useful even if Adapter Mode never ships.

## P0: Standalone Mode

Standalone Mode must work without:

- OpenCode;
- Codex;
- Antigravity;
- Cursor;
- GitHub Copilot;
- Windsurf;
- local daemon;
- local filesystem access;
- remote execution adapter;
- online API gateway.

Standalone Mode uses:

- GPT Instructions;
- GPT Knowledge;
- reasoning over PEtFiSh source-of-truth references;
- generated commands;
- design contracts;
- manual user execution steps.

Standalone Mode must support:

- explaining PEtFiSh;
- explaining Companion Gateway;
- recommending profiles and packs;
- designing skills;
- designing triggers and non-triggers;
- producing install/upgrade/uninstall commands;
- producing test plans;
- producing quality-gate plans;
- doing critical review and anti-sycophancy;
- preserving source-of-truth alignment.

Standalone Mode must not claim:

- local files were changed;
- local packs were installed;
- local tests were run;
- local IDE/CLI tools were invoked;
- online gateway APIs were called unless Actions actually returned results.

Allowed result levels:

- `advice_only`;
- `command_rendered`.

## P1: Gateway Mode

Gateway Mode adds online APIs but still does not require local IDE/CLI tools.

Gateway Mode uses:

- GPT Instructions;
- GPT Knowledge;
- GPT Actions;
- PEtFiSh Online Gateway API;
- server-side catalog/profile/trust/command-rendering logic.

Gateway Mode must support:

- deterministic routing;
- catalog search;
- profile suggestion;
- pack resolution;
- command rendering;
- Trust Gate classification;
- skill contract rendering;
- server-side eval or policy checks when implemented;
- side-effect-free preview where available.

Gateway Mode does not require:

- OpenCode;
- Codex;
- Antigravity;
- Cursor;
- GitHub Copilot;
- Windsurf;
- local daemon;
- desktop client.

Gateway Mode must not claim local execution. Local execution is Adapter Mode.

Allowed result levels:

- `advice_only`;
- `command_rendered`;
- `dry_run`;
- `previewed`.

Gateway Mode is the second implementation target after Standalone Mode.

## P2: Adapter Mode

Adapter Mode connects online-gpt to local execution environments through adapters.

Adapter Mode may involve:

- local daemon;
- OpenCode;
- Codex;
- Antigravity;
- Cursor;
- GitHub Copilot;
- Windsurf;
- desktop bridge;
- remote preview;
- approved local execution.

Adapter Mode is optional for `online-gpt`.

It overlaps with, but is not identical to, 胖鱼遥控器:

- `online-gpt` Adapter Mode is an optional extension of the GPT version;
- 胖鱼遥控器 is closer to the relationship between Codex's GPT and a desktop client;
- 胖鱼遥控器 should be designed as a dedicated remote-control product surface;
- `online-gpt` should not become blocked on Adapter Mode.

Adapter Mode requires:

- Trust Gate;
- explicit approval for side effects;
- scoped project alias;
- secret masking;
- audit trace;
- execution proof.

Allowed result levels:

- `previewed`;
- `executed` only after adapter proof;
- `audit_logged` only after durable audit logging exists.

## Dependency rule

```text
Standalone Mode depends on GPT configuration only.
Gateway Mode depends on online API infrastructure.
Adapter Mode depends on Gateway + daemon + optional execution targets.
```

OpenCode, Codex, Antigravity, Cursor, GitHub Copilot, and Windsurf are execution targets, not runtime dependencies of the GPT version.

## Capability matrix

| Capability | Standalone | Gateway | Adapter |
|---|---:|---:|---:|
| Explain PEtFiSh | yes | yes | yes |
| Recommend packs | yes | yes | yes |
| Design skills | yes | yes | yes |
| Render install commands | yes | yes | yes |
| Deterministic routing API | no | yes | yes |
| Live catalog search | no | yes | yes |
| Trust classification API | no | yes | yes |
| Local workspace preview | no | no | yes |
| Local execution | no | no | optional |
| Requires IDE/CLI agent | no | no | only selected adapter |

## Alignment rule

Even in Standalone Mode, online-gpt must remain aligned with core PEtFiSh semantics:

- no new official pack aliases unless core/market defines them;
- no replacement Companion Gateway semantics;
- no incompatible profile mappings;
- no weakened skill lifecycle;
- no bypass of quality gate or trust boundaries.

## Naming rule

Preferred phrase:

```text
independent online companion runtime with optional execution adapters
```

Avoid:

```text
remote controller for OpenCode
Codex-dependent GPT
Antigravity wrapper
IDE-bound PEtFiSh
```
