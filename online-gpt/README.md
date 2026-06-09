# PEtFiSh Companion GPT

PEtFiSh Companion GPT is the online companion shell for the PEtFiSh ecosystem.

It is not a lightweight chatbot copy of PEtFiSh. It is a first-class online interface adapter for the same companion architecture: packs, skills, MCP servers, plugins, project conventions, action policies, and local/remote execution boundaries.

## Design stance

PEtFiSh Companion GPT follows a modular assembly model, not a POC -> MVP -> product-growth model.

The complete machine is defined first:

```text
ChatGPT Custom GPT / ChatGPT App
        |
        v
Companion Kernel
        |
        v
Capability Modules
        |
        v
Actions / MCP / CLI / Local Daemon Adapters
        |
        v
OpenCode / Codex / Antigravity / Repos / petfish-market
```

A module may start with a mock, read-only, or disabled adapter, but its contract must be complete from day one: inputs, outputs, policy, failures, tests, and replacement path.

## Directory map

```text
online-gpt/
├── README.md
├── ARCHITECTURE.md
├── MODULES.md
├── instructions/          # GPT behavior contracts
├── knowledge/             # compiled GPT Knowledge bundle
├── actions/               # GPT Actions OpenAPI and policy
├── gateway/               # reference gateway kernel skeleton
└── evals/                 # routing, safety, knowledge, regression evals
```

## Non-negotiable boundaries

- The GPT shell may generate local commands, but it must not claim local execution unless a verified adapter result confirms it.
- Local write/destructive execution must pass through Trust Gate.
- Secrets must never be echoed back.
- Remote execution must be previewed, classified, approved, logged, and summarized.
- Knowledge files are references; behavioral rules belong in `instructions/`.

## Assembly order

This is an implementation order, not a reduced product roadmap:

1. Freeze architecture and module contracts.
2. Build the GPT instructions and answer contracts.
3. Compile the Knowledge bundle.
4. Define the Actions OpenAPI contract.
5. Add the gateway skeleton with all planned endpoints represented.
6. Wire deterministic modules: catalog, installer, profiler, trust gate.
7. Add Skill Workbench and quality-gate integration.
8. Add remote preview and local daemon adapters.
9. Run evals and update prompts, schemas, and modules together.

## Primary artifact

The GPT Builder should be configured from:

- `instructions/petfish-companion.instructions.md`
- selected files under `knowledge/`
- `actions/openapi.yaml`
- `actions/action-policy.md`

## Status

This subsystem is a full skeleton. Endpoint implementations may be deterministic, mock, disabled, or adapter-backed, but the shape of the system should not change when a module becomes real.
