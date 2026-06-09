# Local Test Quickstart

For the full plan, read:

```text
online-gpt/LOCAL-TEST-PLAN.md
```

This is the short command sequence.

## 1. Checkout

```bash
git checkout dev
git pull
```

## 2. Compile Python files

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

## 3. Run smoke demo

```bash
python online-gpt/gateway/app.py
```

## 4. Run evals

```bash
python online-gpt/gateway/eval_runner.py online-gpt/evals
```

## 5. Run alignment check

```bash
python online-gpt/tools/check_alignment.py
```

## 6. Try knowledge compiler scaffold

```bash
python online-gpt/tools/compile_knowledge.py
cat online-gpt/knowledge/04-platform-adapters.generated.md
```

## 7. Optional OpenAPI validation

```bash
uvx openapi-spec-validator online-gpt/actions/openapi.yaml
```

Expected before GPT Builder publication:

- compile passes;
- smoke demo runs;
- evals pass;
- alignment check passes;
- OpenAPI validates or validator issue is documented;
- remote execute remains disabled or approval-protected.
