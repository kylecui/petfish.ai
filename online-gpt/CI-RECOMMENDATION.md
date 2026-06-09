# CI Recommendation for `online-gpt/`

This document describes the recommended CI checks for the online GPT subsystem.

The checks are intentionally lightweight and should not require external services.

## Recommended CI job

Trigger on changes under:

```text
online-gpt/**
README.md
AGENTS.md
docs/companion-gateway.md
platforms.json
packs/**
```

## Steps

```bash
python -m py_compile \
  online-gpt/gateway/app.py \
  online-gpt/gateway/router.py \
  online-gpt/gateway/schemas.py \
  online-gpt/gateway/eval_runner.py \
  online-gpt/gateway/modules/catalog.py \
  online-gpt/gateway/modules/installer.py \
  online-gpt/gateway/modules/profiler.py \
  online-gpt/gateway/modules/remote_control.py \
  online-gpt/gateway/modules/skill_workbench.py \
  online-gpt/gateway/modules/trust_gate.py \
  online-gpt/tools/check_alignment.py \
  online-gpt/tools/compile_knowledge.py
```

```bash
python online-gpt/gateway/app.py
```

```bash
python online-gpt/gateway/eval_runner.py online-gpt/evals
```

```bash
python online-gpt/tools/check_alignment.py
```

## Optional OpenAPI check

If CI may use external packages:

```bash
uvx openapi-spec-validator online-gpt/actions/openapi.yaml
```

If not, keep OpenAPI validation as a local release check.

## Failure policy

- Python compile failure blocks merge.
- Gateway eval failure blocks merge unless the eval is intentionally updated in the same PR.
- Alignment checker failure blocks merge unless core source-of-truth files changed and online-gpt was updated accordingly.
- OpenAPI validation failure blocks GPT publishing, even if it does not block development merge.

## Future workflow file

A future GitHub Actions workflow can be added at:

```text
.github/workflows/online-gpt.yml
```

Do not add a workflow until local commands pass at least once.
