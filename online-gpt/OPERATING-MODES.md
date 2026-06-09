# Operating Modes and Priority

`online-gpt/` is the GPT version of `petfish.ai`.

Its first responsibility is to operate independently as a GPT-native online companion. IDE/CLI adapters are optional and low priority.

## Priority order

```text
P0. Standalone Mode
P1. Gateway Mode
P2. Adapter Mode
```

This priority order is a product and architecture constraint.

## P0: Standalone Mode

Standalone Mode must work without:

- OpenCode;
- Codex;
- Antigravity;
- local daemon;
- local filesystem access;
- remote execution adapter.

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
- local IDE/CLI tools were invoked.

## P1: Gateway Mode

Gateway Mode adds online APIs but still does not require local IDE/CLI tools.

Gateway Mode uses:

- GPT Instructions;
- GPT Knowledge;
- GPT Actions;
- PEtFiSh Online Gateway API;
- server-side catalog/profile/trust/command-rendering logic.

Gateway Mode must support:

- catalog search;
- profile suggestion;
- pack resolution;
- command rendering;
- Trust Gate classification;
- skill contract rendering;
- server-side eval or policy checks when implemented.

Gateway Mode does not require:

- OpenCode;
- Codex;
- Antigravity;
- local daemon;
- desktop client.

Gateway Mode is the second implementation target after Standalone Mode.

## P2: Adapter Mode

Adapter Mode connects online-gpt to local execution environments through adapters.

Adapter Mode may involve:

- local daemon;
- OpenCode;
- Codex;
- Antigravity;
- desktop bridge;
- remote preview;
- approved local execution.

Adapter Mode is low priority for `online-gpt`.

It overlaps with, but is not identical to, 胖鱼遥控器:

- `online-gpt` Adapter Mode is an optional extension of the GPT version;
- 胖鱼遥控器 is closer to the relationship between Codex's GPT and a desktop client;
- 胖鱼遥控器 should be designed as a dedicated remote-control product surface;
- `online-gpt` should not become blocked on Adapter Mode.

## Non-negotiable rule

Standalone Mode and Gateway Mode must remain useful even if Adapter Mode never ships.

## Dependency rule

```text
Standalone Mode depends on GPT configuration only.
Gateway Mode depends on online API infrastructure.
Adapter Mode depends on Gateway + daemon + execution targets.
```

OpenCode, Codex, and Antigravity are execution targets, not runtime dependencies of the GPT version.

## Alignment rule

Even in Standalone Mode, online-gpt must remain aligned with core PEtFiSh semantics:

- no new official pack aliases unless core/market defines them;
- no replacement Companion Gateway semantics;
- no incompatible profile mappings;
- no weakened skill lifecycle;
- no bypass of quality gate or trust boundaries.
