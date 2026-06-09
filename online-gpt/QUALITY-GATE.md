# Online GPT Quality Gate

This quality gate applies to the `online-gpt/` subsystem.

It supplements, but does not replace, the core PEtFiSh skill quality gate.

## Gate 0: Mode priority

Required:

- P0 Standalone Mode is tested first;
- P1 Gateway Mode is tested only after P0 passes;
- P2 Adapter Mode is treated as optional boundary/regression testing only;
- P2 Adapter tests are not used as primary acceptance evidence;
- local IDE/CLI tools are never required for P0 or P1 acceptance.

## Gate 1: Alignment

Required:

- `PRINCIPLES.md` exists;
- `OPERATING-MODES.md` exists;
- `ALIGNMENT.md` exists;
- `SOURCE-OF-TRUTH.md` exists;
- `knowledge/00-source-of-truth-note.md` is included in GPT Knowledge package;
- `tools/check_alignment.py` passes;
- online-gpt does not invent official pack aliases.

## Gate 2: Behavior contracts

Required:

- main GPT instructions exist;
- instructions state independent online companion runtime identity;
- instructions state IDE/CLI tools are optional execution adapters;
- safety boundary exists;
- answer contracts exist;
- anti-sycophancy contract exists;
- GPT configuration package names exact files to upload/copy.

## Gate 3: P0 Standalone acceptance

Required:

- GPT preview works without Actions;
- PEtFiSh explanation prompt passes;
- pack/profile recommendation prompt passes;
- skill design prompt passes;
- command rendering prompt passes;
- anti-sycophancy prompt passes;
- no answer requires OpenCode/Codex/Antigravity as a dependency.

## Gate 4: P1 Gateway acceptance

Required:

- Gateway-only Actions schema imports in GPT Builder if Gateway Mode is enabled;
- operation IDs match `gateway/app.py` dispatcher;
- `gateway/server.py` starts locally;
- HTTP smoke requests return module envelopes;
- command rendering does not claim execution;
- Trust Gate classifies risky actions.

Required local commands:

```bash
python -m py_compile online-gpt/gateway/app.py online-gpt/gateway/router.py online-gpt/gateway/server.py online-gpt/gateway/schemas.py online-gpt/gateway/eval_runner.py online-gpt/gateway/modules/*.py online-gpt/tools/*.py
python online-gpt/gateway/app.py
python online-gpt/gateway/eval_runner.py online-gpt/evals
```

## Gate 5: P2 Adapter boundary

Required only when Adapter Mode is explicitly tested:

- remote daemon spec requires approval and audit;
- remote execution is disabled by default;
- remote-control prompts are labeled boundary/regression tests;
- preview is side-effect-free;
- execution requires approval, scoped project alias, secret masking, audit trace, and execution proof.

P2 failure should block Adapter Mode claims, but it should not be used to claim that P0/P1 are missing unless the failure leaks into P0/P1 answers.

## Gate 6: Evals

Required:

- Routing evals pass.
- Safety evals pass.
- Knowledge evals pass.
- Priority regression evals pass.
- Anti-sycophancy regression evals pass.
- P2 boundary evals are labeled as P2 and do not dominate P0/P1 acceptance.

## Gate 7: Documentation completeness

Required:

- GPT Builder guide;
- local test plan;
- quickstart;
- publish checklist;
- known limitations;
- PR notes;
- completion summary;
- priority audit report.

## Decision states

| State | Meaning |
|---|---|
| PASS | P0 and P1 gates pass locally; P2 boundary either passes or is explicitly deferred |
| CONDITIONAL | docs/contracts complete, but optional OpenAPI validator unavailable |
| FAIL | syntax, eval, alignment, mode-priority, or safety gate fails |

Do not publish the GPT unless the gate is PASS or the only remaining issue is a documented external validator limitation.
