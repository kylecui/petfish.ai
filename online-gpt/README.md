# PEtFiSh Companion GPT

PEtFiSh Companion GPT is the GPT version of `petfish.ai` and an independent online companion runtime for the PEtFiSh ecosystem.

It is not a lightweight chatbot copy of PEtFiSh, and it is not a wrapper around OpenCode, Codex, or Antigravity. It must operate without local IDE/CLI tools.

Its job is to bring PEtFiSh's companion discipline, profiles, packs, skill lifecycle, quality gates, and trust boundaries into a GPT-native online surface while staying aligned with core PEtFiSh semantics.

## Release-candidate entry points

For the current RC, read in this order:

```text
RELEASE-CANDIDATE.md
PRIORITY-GUARDRAIL.md
GPT-BUILDER-RUNBOOK.md
GATEWAY-DEPLOYMENT-RUNBOOK.md
PRODUCTION-READINESS-CHECKLIST.md
```

The first release is scoped to:

```text
P0 Standalone Mode + P1 Gateway-only Actions
```

P2 Adapter Mode remains boundary/regression only.

## Priority

```text
P0. Standalone Mode  GPT Instructions + Knowledge, no external runtime required
P1. Gateway Mode     GPT + PEtFiSh Online Gateway APIs
P2. Adapter Mode     optional local daemon / IDE / CLI execution adapters
```

Adapter Mode is low priority. It overlaps with 胖鱼遥控器 but should not drive this subsystem.

See `OPERATING-MODES.md` for the full mode contract.

## Design stance

PEtFiSh Companion GPT follows a modular assembly model, not a POC -> MVP -> product-growth model.

The complete machine is defined first, but implementation priority is Standalone first, Gateway second, Adapter last:

```text
Standalone Mode:
ChatGPT GPT
        |
        v
Instructions + Knowledge + Answer Contracts
        |
        v
PEtFiSh planning, command rendering, skill design, critical review

Gateway Mode:
ChatGPT GPT
        |
        v
PEtFiSh Online Gateway
        |
        v
Catalog / Profile / Install Render / Trust / Skill Workbench APIs

Adapter Mode, low priority:
Gateway
        |
        v
Optional daemon / OpenCode / Codex / Antigravity adapters
```

A module may start with a mock, read-only, or disabled adapter, but its contract must be complete from day one: inputs, outputs, policy, failures, tests, and replacement path.

## Directory map

```text
online-gpt/
├── README.md
├── RELEASE-CANDIDATE.md
├── PRIORITY-GUARDRAIL.md
├── GPT-BUILDER-RUNBOOK.md
├── GATEWAY-DEPLOYMENT-RUNBOOK.md
├── PRODUCTION-READINESS-CHECKLIST.md
├── OPERATING-MODES.md
├── ARCHITECTURE.md
├── MODULES.md
├── runtime-contract.md    # online runtime contract
├── profiles/              # online project profiles (review-online)
├── project-instructions/  # ChatGPT Project instruction templates
├── instructions/          # GPT behavior contracts for Standalone Mode
├── knowledge/             # compiled GPT Knowledge bundle for Standalone Mode
├── actions/               # GPT Actions OpenAPI and policy for Gateway Mode
├── gateway/               # reference gateway kernel skeleton for Gateway Mode
├── remote-daemon/         # low-priority Adapter Mode contracts
└── evals/                 # routing, safety, knowledge, alignment, regression, online-runtime evals
```

## Non-negotiable boundaries

- Standalone Mode must work without OpenCode, Codex, Antigravity, a local daemon, or local filesystem access.
- Gateway Mode must work with online APIs and still not require IDE/CLI tools.
- Adapter Mode is optional and low priority.
- P2 Adapter tests are boundary/regression tests only.
- The GPT shell may generate local commands, but it must not claim local execution unless a verified adapter result confirms it.
- Secrets must never be echoed back.
- Knowledge files are references; behavioral rules belong in `instructions/`.
- Core PEtFiSh remains the source of truth.

## Assembly order

This is an implementation order, not a reduced product roadmap:

1. Freeze architecture, operating modes, and source-of-truth contracts.
2. Build Standalone Mode: GPT instructions, answer contracts, Knowledge bundle, manual command rendering behavior.
3. Add Standalone evals for pack/profile/skill/anti-sycophancy/source-of-truth behavior.
4. Define Gateway Mode OpenAPI contract.
5. Implement Gateway skeleton for catalog, profile, installer, trust, and skill workbench.
6. Add Gateway evals and local test plan.
7. Configure GPT Builder from `GPT-BUILDER-RUNBOOK.md`.
8. Deploy Gateway from `GATEWAY-DEPLOYMENT-RUNBOOK.md`.
9. Defer Adapter Mode remote preview / local daemon work until Standalone and Gateway are reliable.

## Primary artifact

The GPT Builder should be configured from:

- `instructions/petfish-companion.instructions.md`
- selected files under `knowledge/`
- `actions/openapi.gateway-only.yaml` only when Gateway Mode is enabled
- `actions/action-policy.md` only when Gateway Mode is enabled

Do not import full `actions/openapi.yaml` for the first release.

## Status

This subsystem is an RC-ready skeleton for Standalone and Gateway development. Adapter Mode contracts exist for future compatibility but are not the current priority.
