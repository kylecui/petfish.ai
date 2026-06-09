# Local Test Plan V2: Standalone First, Gateway Second

This test plan supersedes the older Adapter-heavy interpretation.

Priority:

```text
P0. Standalone Mode
P1. Gateway Mode
P2. Adapter Mode, deferred
```

The purpose is to verify that PEtFiSh Companion GPT can operate independently before any IDE/CLI or remote-control adapter is considered.

## 0. Checkout

```bash
git clone https://github.com/kylecui/petfish.ai.git
cd petfish.ai
git checkout dev
git pull
```

## 1. Static file checks

```bash
test -f online-gpt/README.md
test -f online-gpt/OPERATING-MODES.md
test -f online-gpt/STANDALONE-ACCEPTANCE.md
test -f online-gpt/GATEWAY-DEPLOYMENT.md
test -f online-gpt/ALIGNMENT.md
test -f online-gpt/SOURCE-OF-TRUTH.md
test -f online-gpt/GPT-BUILDER.md
test -f online-gpt/GPT-CONFIG-PACKAGE.md
test -f online-gpt/actions/openapi.gateway-only.yaml
test -f online-gpt/actions/openapi.yaml
test -f online-gpt/gateway/app.py
test -f online-gpt/tools/check_alignment.py
```

Expected: all commands exit with status `0`.

## 2. Standalone Mode documentation review

Read:

```bash
cat online-gpt/OPERATING-MODES.md
cat online-gpt/STANDALONE-ACCEPTANCE.md
cat online-gpt/GPT-CONFIG-PACKAGE.md
```

Expected:

- Standalone Mode is P0;
- Gateway Mode is P1;
- Adapter Mode is P2 and low priority;
- OpenCode/Codex/Antigravity are not required dependencies;
- remote-control model is not in the first Knowledge upload set.

## 3. Python syntax check

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

Expected: no output and exit status `0`.

## 4. Gateway skeleton smoke test

```bash
python online-gpt/gateway/app.py
```

Expected:

- dispatcher runs;
- install command rendering works;
- profile recommendation works;
- trust classification works;
- any remote preview sample is treated as optional and side-effect-free.

## 5. Evals

```bash
python online-gpt/gateway/eval_runner.py online-gpt/evals
```

Expected:

```text
Total: <N> | Passed: <N> | Failed: 0
```

Failures should be fixed in this order:

1. source-of-truth/alignment failures;
2. Standalone pack/profile/skill behavior failures;
3. Gateway route failures;
4. Adapter-related failures.

## 6. Alignment check

```bash
python online-gpt/tools/check_alignment.py
```

Expected:

```text
online-gpt alignment check passed
```

## 7. Knowledge compiler scaffold

```bash
python online-gpt/tools/compile_knowledge.py
cat online-gpt/knowledge/04-platform-adapters.generated.md
```

Expected:

- generated file is created;
- output is inspected before replacing curated Knowledge.

## 8. Gateway-only OpenAPI validation

Prefer validating the Gateway-only schema first:

```bash
uvx openapi-spec-validator online-gpt/actions/openapi.gateway-only.yaml
```

Optional full contract validation:

```bash
uvx openapi-spec-validator online-gpt/actions/openapi.yaml
```

Expected:

- Gateway-only schema validates before any GPT Actions publication;
- full schema may remain future-facing for Adapter Mode.

## 9. GPT Builder Standalone preview

Configure GPT with:

```text
instructions/petfish-companion.instructions.md
knowledge/00-source-of-truth-note.md
knowledge/01-system-overview.md
knowledge/02-companion-gateway.md
knowledge/03-pack-index.md
knowledge/04-platform-adapters.md
knowledge/05-install-command-reference.md
knowledge/06-quality-gate-reference.md
knowledge/08-failure-playbook.md
knowledge/09-skill-workbench-reference.md
knowledge/10-trust-gate-reference.md
```

Do not enable Actions for this test.

Prompts:

```text
什么是 PEtFiSh Companion Gateway？
```

```text
我要做一个 AI security research 项目，需要文献、PPT、部署和安全审计，应该装哪些 packs？
```

```text
帮我设计一个 research clipping skill。
```

```text
请帮我在本地安装这些 pack。
```

Expected:

- GPT works without Actions;
- GPT does not require IDE/CLI tools;
- GPT renders commands but does not claim local execution;
- GPT preserves source-of-truth boundaries.

## 10. GPT Builder Gateway preview

After Standalone passes, enable Actions with:

```text
online-gpt/actions/openapi.gateway-only.yaml
```

Prompts:

```text
通过 Gateway 推荐 security research 项目的 packs。
```

```text
通过 Gateway 渲染 OpenCode security profile 的安装命令。
```

Expected:

- Gateway APIs are called;
- OpenCode is treated as target platform metadata, not a required runtime;
- no local execution claim;
- remote endpoints are absent from the Gateway-only schema.

## 11. Adapter Mode check, deferred

Do not test Adapter Mode unless explicitly starting 胖鱼遥控器 or remote execution work.

For now, verify only:

- Adapter documents are present;
- remote execution is absent from Gateway-only schema;
- full schema documents remote endpoints as disabled or approval-protected.

## Pass condition

`online-gpt` is ready for first GPT configuration when:

- Standalone preview passes;
- Gateway-only OpenAPI validates;
- Gateway skeleton tests pass;
- alignment check passes;
- online-runtime evals pass (ChatGPT Project treated as online PEtFiSh runtime);
- remote/Adapter Mode remains out of the first public configuration.
