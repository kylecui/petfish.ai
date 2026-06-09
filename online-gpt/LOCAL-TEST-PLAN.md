# Local Test Plan for `online-gpt/`

This plan covers work that requires a local clone of `kylecui/petfish.ai` and cannot be fully verified through remote GitHub file edits alone.

The goal is to verify that the online GPT subsystem is aligned with core PEtFiSh, that deterministic gateway modules run, and that the GPT Builder artifacts are ready to configure.

## 0. Preconditions

Required tools:

```bash
python --version   # Python 3.10+ recommended
uv --version       # recommended for broader PEtFiSh workflows
git --version
```

Recommended environment:

- Windows + WSL, Linux, or macOS;
- clean working tree before tests;
- branch: `dev`.

Clone and enter the repository:

```bash
git clone https://github.com/kylecui/petfish.ai.git
cd petfish.ai
git checkout dev
git pull
```

Confirm the subsystem exists:

```bash
find online-gpt -maxdepth 3 -type f | sort
```

Expected: files under `instructions/`, `knowledge/`, `actions/`, `gateway/`, `remote-daemon/`, `tools/`, and `evals/`.

## 1. Static file presence check

Run:

```bash
test -f online-gpt/README.md
test -f online-gpt/ARCHITECTURE.md
test -f online-gpt/MODULES.md
test -f online-gpt/ALIGNMENT.md
test -f online-gpt/SOURCE-OF-TRUTH.md
test -f online-gpt/GPT-BUILDER.md
test -f online-gpt/IMPLEMENTATION.md
test -f online-gpt/SECURITY.md
test -f online-gpt/PUBLISH-CHECKLIST.md
test -f online-gpt/actions/openapi.yaml
test -f online-gpt/gateway/app.py
test -f online-gpt/gateway/eval_runner.py
test -f online-gpt/tools/check_alignment.py
test -f online-gpt/tools/compile_knowledge.py
```

Expected: all commands exit with status `0`.

## 2. Python syntax check

Run:

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

If this fails:

1. fix syntax/import issues first;
2. do not proceed to evals until syntax passes.

## 3. Gateway smoke demo

Run:

```bash
python online-gpt/gateway/app.py
```

Expected output sections:

```text
## routeCompanionRequest
## profileProject
## renderInstallCommand
## classifyActionRisk
## previewRemoteExecution
```

Expected properties:

- `renderInstallCommand` returns `result_level: command_rendered`;
- install command uses `uv run https://raw.githubusercontent.com/kylecui/petfish.ai/master/install.py`;
- remote preview returns `result_level: previewed`;
- remote execution is not performed.

## 4. Deterministic eval runner

Run:

```bash
python online-gpt/gateway/eval_runner.py online-gpt/evals
```

Expected:

```text
Total: <N> | Passed: <N> | Failed: 0
```

If failures occur:

- routing failures usually mean `gateway/router.py` priority needs adjustment;
- `must_include` failures may mean the deterministic envelope lacks expected metadata;
- `must_not_include` failures indicate unsafe or misleading wording;
- alignment failures may mean online-gpt drifted from core PEtFiSh semantics.

## 5. Alignment checker

Run:

```bash
python online-gpt/tools/check_alignment.py
```

Expected:

```text
online-gpt alignment check passed
```

If this fails:

- unknown aliases: update `knowledge/03-pack-index.md` or confirm the alias exists in core/market;
- missing platform: update `knowledge/04-platform-adapters.md` from `platforms.json`;
- drift term: inspect whether a document implies online-gpt replaces core PEtFiSh semantics.

## 6. Knowledge compiler scaffold

Run:

```bash
python online-gpt/tools/compile_knowledge.py
```

Expected:

```text
wrote online-gpt/knowledge/04-platform-adapters.generated.md
```

Then inspect:

```bash
cat online-gpt/knowledge/04-platform-adapters.generated.md
```

Expected:

- file is generated from `platforms.json` when possible;
- if platform metadata format differs, output may be incomplete and compiler should be improved.

Do not replace the hand-curated `04-platform-adapters.md` until generated output is accurate.

## 7. OpenAPI schema validation

Optional but recommended.

With Python package:

```bash
uvx openapi-spec-validator online-gpt/actions/openapi.yaml
```

Alternative with Node:

```bash
npx @redocly/cli lint online-gpt/actions/openapi.yaml
```

Expected:

- schema parses;
- operation IDs are unique;
- `$ref` values resolve;
- no syntax errors.

If validators complain about OpenAPI 3.1 compatibility, record validator version and error message.

## 8. Action example sanity check

Manually compare these example operation IDs with `actions/openapi.yaml` and `gateway/app.py` dispatcher:

```bash
cat online-gpt/actions/examples/*.json
```

Expected operation IDs:

- `renderInstallCommand`
- `profileProject`
- `previewRemoteExecution`

Each should exist in both:

```text
online-gpt/actions/openapi.yaml
online-gpt/gateway/app.py
```

## 9. GPT Builder dry configuration review

No online publishing yet. Locally inspect:

```bash
cat online-gpt/GPT-BUILDER.md
cat online-gpt/instructions/petfish-companion.instructions.md
cat online-gpt/knowledge/README.md
cat online-gpt/actions/openapi.yaml
```

Expected:

- instructions tell GPT it is an online adapter, not a replacement;
- Knowledge upload set includes source-of-truth note;
- Actions point to placeholder `https://api.petfish.ai`, which must be replaced before real GPT deployment;
- remote execute endpoint is documented as disabled or approval-protected.

## 10. Manual prompt simulation

Use the gateway route function indirectly through evals, then manually inspect likely GPT answers.

Test prompts:

```text
我要在 Codex 项目里安装 security profile，给我命令和验证方式。
```

Expected:

- install plan route;
- packs include `context`, `deploy`, `petfish`, `testdocs`, `trust`;
- Codex verification references `.agents/skills/` and `AGENTS.md`;
- no claim that installation completed.

```text
帮我设计一个用于研究摘录和引用整理的 skill。
```

Expected:

- Skill Workbench route;
- triggers and non-triggers;
- file tree;
- eval/gate plan;
- no publish claim.

```text
预览让本地 OpenCode 执行一次 online-gpt gate。
```

Expected:

- remote preview route;
- Trust Gate included;
- no side effects;
- execute remains separate.

```text
online-gpt 是否可以定义自己的官方 pack alias？
```

Expected:

- critical review;
- core PEtFiSh remains source of truth;
- no new official alias unless core/market defines it.

## 11. Regression acceptance criteria

Before considering local validation complete:

- [ ] all Python files compile;
- [ ] gateway smoke demo runs;
- [ ] eval runner passes;
- [ ] alignment checker passes;
- [ ] OpenAPI schema validates or validator limitation is documented;
- [ ] generated platform knowledge is inspected;
- [ ] GPT Builder docs are internally consistent;
- [ ] remote execute remains disabled or approval-protected.

## 12. If tests fail

Create a local notes file, not committed by default:

```bash
mkdir -p .petfish-local-test
cat > .petfish-local-test/online-gpt-test-notes.md <<'EOF'
# online-gpt local test notes

## Environment

## Failed command

## Error output

## Suspected cause

## Proposed fix
EOF
```

Then fix in this order:

1. syntax/import errors;
2. router priority errors;
3. alignment checker drift;
4. eval expected text mismatch;
5. OpenAPI validation;
6. documentation consistency.
