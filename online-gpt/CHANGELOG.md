# Online GPT Changelog

## Unreleased

Initial `online-gpt/` subsystem skeleton and enrichment.

### Added

- Architecture and module contract documents:
  - `README.md`
  - `ARCHITECTURE.md`
  - `MODULES.md`
  - `IMPLEMENTATION.md`
  - `SECURITY.md`
  - `PUBLISH-CHECKLIST.md`
- GPT Builder configuration guide:
  - `GPT-BUILDER.md`
- GPT instruction contracts:
  - `instructions/petfish-companion.instructions.md`
  - `instructions/safety-boundary.md`
  - `instructions/answer-contract.md`
  - `instructions/anti-sycophancy.md`
- GPT Knowledge bundle:
  - system overview
  - companion gateway
  - pack index
  - platform adapters
  - install command reference
  - quality gate reference
  - remote control model
  - failure playbook
  - skill workbench reference
  - trust gate reference
- GPT Actions contract:
  - `actions/openapi.yaml`
  - `actions/action-policy.md`
  - request examples
- Stdlib-only gateway skeleton:
  - dispatcher
  - schemas
  - router
  - catalog module
  - installer module
  - profiler module
  - skill workbench module
  - trust gate module
  - remote control module
- Eval harness:
  - routing evals
  - safety evals
  - knowledge evals
  - anti-sycophancy regression evals
  - lightweight eval runner
- Remote daemon specification:
  - `remote-daemon/SPEC.md`

### Design decisions

- The subsystem follows modular assembly, not POC/MVP staging.
- Remote execution is represented in the contract from day one but disabled by default.
- Knowledge is reference material; behavior belongs in instructions.
- Gateway modules return a common envelope.
- Actions use operation IDs that match the local smoke dispatcher.
