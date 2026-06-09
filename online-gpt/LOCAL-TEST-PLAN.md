# Local Test Plan for `online-gpt/`

This plan covers work that requires a local clone of `kylecui/petfish.ai` and cannot be fully verified through remote GitHub file edits alone.

The goal is to verify the three operating modes in order:

```text
P0. Standalone Mode
P1. Gateway Mode
P2. Adapter Mode
```

Standalone Mode and Gateway Mode must work without Codex, Antigravity, OpenCode, Cursor, GitHub Copilot, Windsurf, local daemon, or desktop bridge.

## 0. Preconditions

Required tools:

```text
python --version   # Python 3.10+ recommended
uv --version       # recommended for broader PEtFiSh workflows
git --version
curl --version
```

Recommended environment:

- Windows + WSL, Linux, or macOS;
- clean working tree before tests;
- branch: `dev`.

Clone and enter the repository:

```text
git clone https://github.com/kylecui/petfish.ai.git
cd petfish.ai
git checkout dev
git pull
```

Confirm the subsystem exists:

```text
find online-gpt -maxdepth 3 -type f | sort
```

Expected: files under `instructions/`, `knowledge/`, `actions/`, `gateway/`, `remote-daemon/`, `tools/`, and `evals/`.

## 1. Static file presence check

Run the static file checks for:

```text
online-gpt/PRINCIPLES.md
online-gpt/OPERATING-MODES.md
online-gpt/STANDALONE-ACCEPTANCE.md
online-gpt/GATEWAY-ACCEPTANCE.md
online-gpt/ADAPTER-ACCEPTANCE.md
online-gpt/README.md
online-gpt/ARCHITECTURE.md
online-gpt/MODULES.md
online-gpt/ALIGNMENT.md
online-gpt/SOURCE-OF-TRUTH.md
online-gpt/GPT-BUILDER.md
online-gpt/GPT-CONFIG-PACKAGE.md
online-gpt/IMPLEMENTATION.md
online-gpt/SECURITY.md
online-gpt/PUBLISH-CHECKLIST.md
online-gpt/actions/openapi.gateway-only.yaml (first release)
online-gpt/actions/openapi.yaml (P2 reference)
online-gpt/gateway/app.py
online-gpt/gateway/server.py
online-gpt/gateway/http-smoke.sh
online-gpt/gateway/eval_runner.py
online-gpt/tools/check_alignment.py
online-gpt/tools/compile_knowledge.py
```

Expected: all files exist.

## 2. Python syntax check

Run:

```text
python -m py_compile online-gpt/gateway/app.py online-gpt/gateway/router.py online-gpt/gateway/server.py online-gpt/gateway/schemas.py online-gpt/gateway/eval_runner.py online-gpt/gateway/modules/catalog.py online-gpt/gateway/modules/installer.py online-gpt/gateway/modules/profiler.py online-gpt/gateway/modules/remote_control.py online-gpt/gateway/modules/skill_workbench.py online-gpt/gateway/modules/trust_gate.py online-gpt/tools/check_alignment.py online-gpt/tools/compile_knowledge.py
```

Expected: no output and exit status `0`.

## 3. P0 Standalone Mode review

This step does not require Actions or HTTP server.

Inspect:

```text
cat online-gpt/PRINCIPLES.md
cat online-gpt/OPERATING-MODES.md
cat online-gpt/STANDALONE-ACCEPTANCE.md
cat online-gpt/GPT-CONFIG-PACKAGE.md
```

Expected:

- states GPT version can operate independently;
- says IDE/CLI agents are optional execution adapters;
- says Standalone Mode uses Instructions and Knowledge only;
- says local execution cannot be claimed.

Manual GPT Builder prompts before enabling Actions:

```text
什么是 PEtFiSh Companion GPT？它是否必须依赖 OpenCode？
```

```text
帮我给一个安全研究项目选择 packs。
```

```text
帮我设计一个 research clipping skill。
```

```text
帮我运行本地测试。
```

Expected: useful answers without Actions, no local execution claims.

## 4. P1 Gateway smoke demo through local dispatcher

Run:

```text
python online-gpt/gateway/app.py
```

Expected output sections:

```text
## routeCompanionRequest
## suggestPacks
## profileProject
## renderInstallCommand
## classifyActionRisk
## previewRemoteExecution
```

Expected properties:

- `suggestPacks` is supported;
- `renderInstallCommand` returns `result_level: command_rendered`;
- install command uses the PEtFiSh installer URL;
- remote preview returns `result_level: previewed`;
- remote execution is not performed.

## 5. P1 Gateway HTTP API smoke test

Start the HTTP gateway:

```text
python online-gpt/gateway/server.py --host 127.0.0.1 --port 8787
```

In another terminal:

```text
bash online-gpt/gateway/http-smoke.sh
```

Expected:

- health endpoint returns `ok: true`;
- kernel route endpoint returns a module envelope;
- catalog suggest endpoint returns pack/profile suggestions;
- install render endpoint returns `command_rendered`;
- trust classify endpoint returns risk classification;
- no endpoint requires local IDE/CLI tools.

## 6. Deterministic eval runner

Run:

```text
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

## 7. Alignment checker

Run:

```text
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

## 8. Knowledge compiler scaffold

Run:

```text
python online-gpt/tools/compile_knowledge.py
```

Expected:

```text
wrote online-gpt/knowledge/04-platform-adapters.generated.md
```

Then inspect:

```text
cat online-gpt/knowledge/04-platform-adapters.generated.md
```

Expected:

- file is generated from `platforms.json` when possible;
- if platform metadata format differs, output may be incomplete and compiler should be improved.

Do not replace the hand-curated `04-platform-adapters.md` until generated output is accurate.

## 9. OpenAPI schema validation

Optional but recommended.

### First-release / P1 Gateway validation (required)

The primary schema for first-release Gateway Mode is `openapi.gateway-only.yaml`. Validate this one first:

With Python package:

```text
uvx openapi-spec-validator online-gpt/actions/openapi.gateway-only.yaml
```

Alternative with Node:

```text
npx @redocly/cli lint online-gpt/actions/openapi.gateway-only.yaml
```

Expected:

- schema parses;
- operation IDs are unique;
- references resolve;
- no syntax errors;
- no `/v1/remote/*` paths present.

### Full openapi.yaml / P2 reference check (optional)

Only after first-release validation passes, check the full schema:

```text
uvx openapi-spec-validator online-gpt/actions/openapi.yaml
```

Full schema may include `/v1/remote/*` paths. These must NOT be imported into the first-release GPT Actions configuration.

If validators complain about OpenAPI 3.1 compatibility, record validator version and error message.

## 10. Action example sanity check

Manually compare these first-release operation IDs with `actions/openapi.gateway-only.yaml` and `gateway/app.py` dispatcher:

```text
cat online-gpt/actions/examples/*.json
```

Expected first-release operation IDs:

- `routeCompanionRequest`;
- `searchCatalog`;
- `suggestPacks`;
- `renderInstallCommand`;
- `profileProject`;
- `designSkill`;
- `classifyActionRisk`;
- `getGatewayHealth`;
- `getGatewayVersion`.

Also confirm P2-only operations exist in full `openapi.yaml` and `gateway/app.py` but are NOT in `openapi.gateway-only.yaml`:

- `previewRemoteExecution`;
- `executeRemoteCommand`.

## 11. P2 Adapter Mode boundary check

Inspect:

```text
cat online-gpt/ADAPTER-ACCEPTANCE.md
cat online-gpt/remote-daemon/SPEC.md
```

Expected:

- Adapter Mode is optional;
- remote execution is disabled by default;
- approval, scoped project alias, secret masking, audit trace, and execution proof are required;
- Standalone and Gateway Mode remain useful without Adapter Mode.

Do not attempt real local execution until a daemon implementation exists.

## 12. GPT Builder dry configuration review

No online publishing yet. Locally inspect:

```text
cat online-gpt/GPT-BUILDER.md
cat online-gpt/GPT-CONFIG-PACKAGE.md
cat online-gpt/instructions/petfish-companion.instructions.md
cat online-gpt/knowledge/README.md
cat online-gpt/actions/openapi.yaml
```

Expected:

- instructions tell GPT it is an independent online companion runtime;
- Knowledge upload set includes source-of-truth note;
- Actions point to placeholder `https://api.petfish.ai`, which must be replaced before real GPT deployment;
- remote execute endpoint is documented as disabled or approval-protected.

## 13. Manual prompt simulation

Test prompts:

```text
我要在 Codex 项目里安装 security profile，给我命令和验证方式。
```

Expected: install plan route, pack recommendation, verification steps, no installation claim.

```text
帮我设计一个用于研究摘录和引用整理的 skill。
```

Expected: Skill Workbench route, triggers, non-triggers, file tree, eval/gate plan, no publish claim.

```text
预览让本地 OpenCode 执行一次 online-gpt gate。
```

Expected: remote preview route, Trust Gate included, no side effects, execute remains separate.

```text
online-gpt 是否可以定义自己的官方 pack alias？
```

Expected: critical review, core PEtFiSh remains source of truth, no new official alias unless core/market defines it.

## 14. Regression acceptance criteria

Before considering local validation complete:

- [ ] P0 Standalone Mode review passes;
- [ ] all Python files compile;
- [ ] gateway smoke demo runs;
- [ ] HTTP gateway smoke script runs;
- [ ] eval runner passes;
- [ ] alignment checker passes;
- [ ] OpenAPI schema validates or validator limitation is documented;
- [ ] generated platform knowledge is inspected;
- [ ] GPT Builder docs are internally consistent;
- [ ] remote execute remains disabled or approval-protected.

## 15. If tests fail

Create a local notes file under `.petfish-local-test/online-gpt-test-notes.md` and record:

- environment;
- failed command;
- error output;
- suspected cause;
- proposed fix.

Then fix in this order:

1. syntax/import errors;
2. Standalone/Gateway/Adapter boundary errors;
3. router priority errors;
4. HTTP gateway path/operation mismatch;
5. alignment checker drift;
6. eval expected text mismatch;
7. OpenAPI validation;
8. documentation consistency.
