# PR Notes for `online-gpt/`

## Summary

This change adds the `online-gpt/` subsystem as an online adapter layer for core PEtFiSh.

It does not redefine PEtFiSh semantics. Core PEtFiSh remains the source of truth for Companion Gateway behavior, pack aliases, profile mapping, platform adapters, skill lifecycle, and quality gates.

## Added

- GPT Builder configuration guide.
- GPT instruction contracts.
- GPT Knowledge bundle.
- Actions OpenAPI contract.
- Stdlib-only gateway skeleton.
- Trust Gate and remote-preview contracts.
- Remote daemon specification.
- Alignment and source-of-truth policies.
- Eval harness and sample evals.
- Local test plan and quickstart.

## Safety stance

Remote execution is represented as a contract but remains disabled unless a trusted local daemon, approval flow, and audit trace are implemented.

Install behavior renders commands only. It does not claim local execution.

## Local validation required

Before merge or publication, run:

```bash
python -m py_compile online-gpt/gateway/app.py online-gpt/gateway/router.py online-gpt/gateway/schemas.py online-gpt/gateway/eval_runner.py online-gpt/gateway/modules/*.py online-gpt/tools/*.py
python online-gpt/gateway/app.py
python online-gpt/gateway/eval_runner.py online-gpt/evals
python online-gpt/tools/check_alignment.py
python online-gpt/tools/compile_knowledge.py
```

See `online-gpt/LOCAL-TEST-PLAN.md` for the complete workflow.

## Review focus

- Does online-gpt preserve core PEtFiSh semantics?
- Are pack/profile/platform facts aligned with core sources?
- Does the router prioritize install/skill/catalog semantics before remote preview?
- Does Trust Gate prevent unsafe execution claims?
- Are GPT Builder artifacts ready for configuration after local tests pass?
