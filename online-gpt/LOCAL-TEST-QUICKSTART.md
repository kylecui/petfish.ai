# Local Test Quickstart

For the full plan, read:

```text
online-gpt/LOCAL-TEST-PLAN.md
```

This is the short command sequence.

## Priority rule

Run tests in this order:

```text
P0. Standalone Mode first
P1. Gateway Mode second
P2. Adapter Mode boundary/regression only
```

Do not use P2 remote-control prompts as primary acceptance evidence for the GPT version.

## 1. Checkout

```bash
git checkout dev
git pull
```

## 2. P0 Standalone review

Inspect the mode and GPT configuration docs:

```bash
cat online-gpt/PRINCIPLES.md
cat online-gpt/OPERATING-MODES.md
cat online-gpt/STANDALONE-ACCEPTANCE.md
cat online-gpt/GPT-CONFIG-PACKAGE.md
```

Expected:

- GPT version is independently operable;
- IDE/CLI tools are optional adapters;
- Standalone Mode does not require Actions;
- no local execution claim is allowed.

## 3. Compile Python files

```bash
python -m py_compile \
  online-gpt/gateway/app.py \
  online-gpt/gateway/router.py \
  online-gpt/gateway/server.py \
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

## 4. Run P1 Gateway dispatcher smoke demo

```bash
python online-gpt/gateway/app.py
```

## 5. Run P1 HTTP gateway smoke test

Terminal 1:

```bash
python online-gpt/gateway/server.py --host 127.0.0.1 --port 8787
```

Terminal 2:

```bash
bash online-gpt/gateway/http-smoke.sh
```

## 6. Run evals

```bash
python online-gpt/gateway/eval_runner.py online-gpt/evals
```

P2 remote-control evals, if present, are boundary/regression tests only.

Online-runtime evals (`online-gpt/evals/online-runtime/`) verify that ChatGPT Project requests are treated as online PEtFiSh runtime, not local platform adapters.

## 7. Run alignment check

```bash
python online-gpt/tools/check_alignment.py
```

## 8. Try knowledge compiler scaffold

```bash
python online-gpt/tools/compile_knowledge.py
cat online-gpt/knowledge/04-platform-adapters.generated.md
```

## 9. Optional OpenAPI validation

```bash
uvx openapi-spec-validator online-gpt/actions/openapi.yaml
```

Expected before GPT Builder publication:

- P0 standalone review passes;
- compile passes;
- dispatcher smoke demo runs;
- HTTP gateway smoke runs;
- evals pass;
- alignment check passes;
- OpenAPI validates or validator issue is documented;
- remote execute remains disabled or approval-protected.
