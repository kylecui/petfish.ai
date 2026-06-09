# Final Development Checklist

This checklist records repository work that should be complete before local testing begins.

## Product principle

- [x] GPT version is independently operable.
- [x] IDE/CLI tools are optional execution adapters.
- [x] Core PEtFiSh remains source of truth.
- [x] Standalone, Gateway, and Adapter modes are explicitly defined.
- [x] Remote execution is optional and disabled by default.

Files:

```text
PRINCIPLES.md
OPERATING-MODES.md
ALIGNMENT.md
SOURCE-OF-TRUTH.md
```

## Mode acceptance

- [x] Standalone Mode acceptance criteria.
- [x] Gateway Mode acceptance criteria.
- [x] Adapter Mode acceptance criteria.

Files:

```text
STANDALONE-ACCEPTANCE.md
GATEWAY-ACCEPTANCE.md
ADAPTER-ACCEPTANCE.md
```

## GPT Builder package

- [x] GPT Builder guide.
- [x] GPT configuration package.
- [x] Instructions package.
- [x] Knowledge upload list.
- [x] Actions import instructions.
- [x] Publish checklist.

Files:

```text
GPT-BUILDER.md
GPT-CONFIG-PACKAGE.md
PUBLISH-CHECKLIST.md
instructions/
knowledge/
actions/
```

## Gateway Mode API

- [x] OpenAPI contract.
- [x] Dispatcher operation mapping.
- [x] stdlib HTTP server.
- [x] HTTP smoke script.
- [x] API mapping documentation.
- [x] Gateway contracts documentation.

Files:

```text
actions/openapi.yaml
gateway/app.py
gateway/server.py
gateway/http-smoke.sh
gateway/API-MAPPING.md
gateway/CONTRACTS.md
gateway/HTTP-GATEWAY.md
```

## Gateway modules

- [x] Router.
- [x] Catalog.
- [x] Profiler.
- [x] Installer command renderer.
- [x] Skill Workbench.
- [x] Trust Gate.
- [x] Remote control preview/disabled execution.
- [x] Shared schema envelope.

Files:

```text
gateway/router.py
gateway/schemas.py
gateway/modules/catalog.py
gateway/modules/profiler.py
gateway/modules/installer.py
gateway/modules/skill_workbench.py
gateway/modules/trust_gate.py
gateway/modules/remote_control.py
```

## Evals and tools

- [x] Eval runner.
- [x] Routing evals.
- [x] Safety evals.
- [x] Knowledge evals.
- [x] Anti-sycophancy regression evals.
- [x] Core alignment regression evals.
- [x] Alignment checker scaffold.
- [x] Knowledge compiler scaffold.

Files:

```text
evals/
gateway/eval_runner.py
tools/check_alignment.py
tools/compile_knowledge.py
```

## Remote daemon and Adapter Mode

- [x] Remote daemon README.
- [x] Remote daemon spec.
- [x] Adapter Mode acceptance criteria.
- [x] Remote execution disabled-by-default rule.

Files:

```text
remote-daemon/README.md
remote-daemon/SPEC.md
ADAPTER-ACCEPTANCE.md
```

## Local test planning

- [x] Full local test plan.
- [x] Quickstart.
- [x] CI recommendation.
- [x] Quality gate.
- [x] Known limitations.
- [x] Completion note.

Files:

```text
LOCAL-TEST-PLAN.md
LOCAL-TEST-QUICKSTART.md
CI-RECOMMENDATION.md
QUALITY-GATE.md
KNOWN-LIMITATIONS.md
COMPLETION-NOTE.md
```

## Remaining local-only work

These are intentionally not completed through remote repository edits:

- [ ] Python syntax compilation.
- [ ] Local dispatcher smoke run.
- [ ] Local HTTP gateway run.
- [ ] HTTP smoke script run.
- [ ] Eval runner execution.
- [ ] Alignment checker execution.
- [ ] Knowledge compiler execution.
- [ ] OpenAPI schema validation.
- [ ] GPT Builder manual preview.

Use:

```text
LOCAL-TEST-PLAN.md
LOCAL-TEST-QUICKSTART.md
```

## Completion statement

All non-local-test repository development and documentation work for the current online-gpt phase is complete in `dev`.

The remaining work is validation from a local clone and, later, deployment of Gateway Mode API infrastructure.
