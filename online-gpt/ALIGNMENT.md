# Alignment with Core PEtFiSh

`online-gpt/` is an online interface adapter for PEtFiSh. It must not fork PEtFiSh semantics.

## Primary rule

The original PEtFiSh system remains the source of truth.

The online GPT subsystem may adapt delivery surfaces, API contracts, and safety boundaries for ChatGPT, but it must not redefine:

- Companion Gateway semantics;
- pack aliases;
- profile-to-pack mapping;
- platform adapter meanings;
- skill lifecycle stages;
- quality gate expectations;
- release discipline;
- PEtFiSh identity and style.

## What online-gpt may do

`online-gpt/` may:

- compile existing docs into GPT Knowledge files;
- convert local commands into Action-rendered plans;
- expose module contracts through OpenAPI;
- add Trust Gate wrappers around remote execution;
- add evals for GPT behavior regression;
- provide a remote-control preview/adapter layer;
- state execution truth labels required by online environments.

These are adaptation mechanisms, not new PEtFiSh product semantics.

## What online-gpt must not do

`online-gpt/` must not:

- invent new official pack aliases that do not exist in core or market;
- silently change profile mappings;
- rename existing core concepts;
- replace `/petfish` command semantics with incompatible online-only semantics;
- make GPT Knowledge override project instructions;
- weaken quality gate requirements;
- enable remote execution without Trust Gate and approval;
- treat ChatGPT as the local execution environment.

## Source-of-truth files

When enriching online-gpt, check against these sources:

```text
README.md
AGENTS.md
docs/companion-gateway.md
docs/agent-install.md
platforms.json
packs/**/pack-manifest.json
packs/**/.opencode/skills/**/SKILL.md
```

Optional packs may be sourced from petfish-market when they are no longer authoritative in this repository.

## Compatibility matrix

| Core PEtFiSh concept | Online GPT representation | Allowed change |
|---|---|---|
| Companion Gateway | lightweight GPT behavior loop + optional gateway route | delivery adaptation only |
| `/petfish install` | install command rendering Action | no semantic change |
| packs | Knowledge and catalog entries | no alias drift |
| skills | Skill Workbench contracts | no lifecycle weakening |
| MCP/tools/plugins | Actions/MCP/adapter references | adapter wrapping only |
| context/trail | online topic boundary hints | no replacement of local state |
| Trust/governance | Trust Gate wrapper | stricter is allowed; weaker is not |

## Drift checks

Before merging online-gpt changes:

- [ ] Does this change introduce a concept not present in core PEtFiSh?
- [ ] If yes, is it clearly an adapter concern rather than a new semantic layer?
- [ ] Does it change pack/profile mapping?
- [ ] Does it weaken local installer, skill lifecycle, or gate behavior?
- [ ] Does it make online GPT sound more authoritative than the local project state?
- [ ] Does it preserve the distinction between generated command and executed action?

## Preferred language

Use:

```text
online adapter
Companion shell
Action wrapper
remote preview
execution proof
source-of-truth alignment
```

Avoid:

```text
new PEtFiSh version
replacement Companion Gateway
GPT-native pack semantics
online-only pack lifecycle
```

## Enforcement

Any future `online-gpt/` module that duplicates core logic should explain why it cannot reuse or compile from the core source.

If duplication is temporary, mark it as:

```text
SYNC_REQUIRED: source=<core file or market entry>
```

and add an eval or checklist item to catch drift.
