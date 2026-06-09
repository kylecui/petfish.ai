# Online GPT Quality Gate

This quality gate applies to the `online-gpt/` subsystem.

It supplements, but does not replace, the core PEtFiSh skill quality gate.

## Gate 1: Alignment

Required:

- `ALIGNMENT.md` exists;
- `SOURCE-OF-TRUTH.md` exists;
- `knowledge/00-source-of-truth-note.md` is included in GPT Knowledge package;
- `tools/check_alignment.py` passes;
- online-gpt does not invent official pack aliases.

## Gate 2: Behavior contracts

Required:

- main GPT instructions exist;
- safety boundary exists;
- answer contracts exist;
- anti-sycophancy contract exists;
- GPT configuration package names exact files to upload/copy.

## Gate 3: Actions contract

Required:

- `actions/openapi.yaml` imports in GPT Builder;
- operation IDs match `gateway/app.py` dispatcher;
- remote execute is disabled or approval-protected;
- Action policy explains side-effect boundaries.

## Gate 4: Gateway smoke

Required local commands:

```bash
python -m py_compile online-gpt/gateway/app.py online-gpt/gateway/router.py online-gpt/gateway/schemas.py online-gpt/gateway/eval_runner.py online-gpt/gateway/modules/*.py online-gpt/tools/*.py
python online-gpt/gateway/app.py
python online-gpt/gateway/eval_runner.py online-gpt/evals
```

## Gate 5: Security

Required:

- no secrets in Knowledge;
- remote daemon spec requires approval and audit;
- Trust Gate classifies risky actions;
- command rendering does not claim execution;
- publish/release actions require explicit approval.

## Gate 6: Documentation completeness

Required:

- GPT Builder guide;
- local test plan;
- quickstart;
- publish checklist;
- known limitations;
- PR notes;
- work completion summary.

## Decision states

| State | Meaning |
|---|---|
| PASS | all gates pass locally |
| CONDITIONAL | docs/contracts complete, but optional OpenAPI validator unavailable |
| FAIL | syntax, eval, alignment, or safety gate fails |

Do not publish the GPT unless the gate is PASS or the only remaining issue is a documented external validator limitation.
