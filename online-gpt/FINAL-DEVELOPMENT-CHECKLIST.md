# Final Development Checklist

This checklist records repository work that should be complete before local testing, GPT Builder configuration, and Gateway staging begin.

## Current review status

Status: **READY FOR RC REVIEW**

All blockers identified in `REVIEW-BLOCKERS.md` are now resolved:
- [x] B1: profiler control-flow fixed — `profile_project()` never returns None
- [x] F1: LOCAL-TEST-PLAN.md uses `openapi.gateway-only.yaml` for first-release validation
- [x] F2: `/v1/health` and `/v1/version` return runbook-compatible metadata
- [x] F3: HTTP smoke covers all health/version endpoints

Do not publish without final review confirmation. GPT Builder / production publication requires human sign-off.

## Product principle

- [x] GPT version is independently operable.
- [x] IDE/CLI tools are optional execution adapters.
- [x] Core PEtFiSh remains source of truth.
- [x] Standalone, Gateway, and Adapter modes are explicitly defined.
- [x] Remote execution is optional and disabled by default.
- [x] P2 Adapter tests are boundary/regression tests only, not primary acceptance.

Files:

```text
PRINCIPLES.md
OPERATING-MODES.md
ALIGNMENT.md
SOURCE-OF-TRUTH.md
PRIORITY-GUARDRAIL.md
```

## Release candidate and publication readiness

- [x] Release-candidate scope documented.
- [x] GPT Builder runbook documented.
- [x] Gateway deployment runbook documented.
- [x] Production readiness checklist documented.
- [x] Documentation index updated.
- [x] README points to RC runbooks.
- [x] Review blockers resolved.

Files:

```text
RELEASE-CANDIDATE.md
REVIEW-BLOCKERS.md
GPT-BUILDER-RUNBOOK.md
GATEWAY-DEPLOYMENT-RUNBOOK.md
PRODUCTION-READINESS-CHECKLIST.md
docs/README.md
README.md
```

## Mode acceptance

- [x] Standalone Mode acceptance criteria.
- [x] Gateway Mode acceptance criteria.
- [x] Adapter Mode acceptance criteria.
- [x] P0/P1 must pass before P2 boundary results are interpreted.

Files:

```text
STANDALONE-ACCEPTANCE.md
GATEWAY-ACCEPTANCE.md
ADAPTER-ACCEPTANCE.md
```

## GPT Builder package

- [x] GPT Builder guide.
- [x] GPT Builder runbook.
- [x] GPT configuration package.
- [x] Instructions package.
- [x] Knowledge upload list.
- [x] Actions import instructions.
- [x] Publish checklist.
- [x] P2 remote-control Knowledge excluded from first-release upload unless explicitly testing boundary behavior.

Files:

```text
GPT-BUILDER.md
GPT-BUILDER-RUNBOOK.md
GPT-CONFIG-PACKAGE.md
PUBLISH-CHECKLIST.md
instructions/
knowledge/
actions/
```

## Gateway Mode API

- [x] Gateway-only OpenAPI contract.
- [x] Full OpenAPI contract kept for non-first-release reference.
- [x] Dispatcher operation mapping.
- [x] stdlib HTTP server.
- [x] HTTP smoke script.
- [x] API mapping documentation.
- [x] Gateway contracts documentation.
- [x] Gateway deployment runbook.

Files:

```text
actions/openapi.gateway-only.yaml
actions/openapi.yaml
gateway/app.py
gateway/server.py
gateway/http-smoke.sh
gateway/API-MAPPING.md
gateway/CONTRACTS.md
gateway/HTTP-GATEWAY.md
GATEWAY-DEPLOYMENT-RUNBOOK.md
```

## Gateway modules

- [x] Router.
- [x] Catalog.
- [x] Profiler blocker resolved.
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
- [x] Mode-priority regression requirement.
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
- [x] Adapter Mode marked optional and low-priority.

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
- [x] Priority audit report.
- [x] Local test plan first-release OpenAPI references updated to gateway-only schema.

Files:

```text
LOCAL-TEST-PLAN.md
LOCAL-TEST-QUICKSTART.md
CI-RECOMMENDATION.md
QUALITY-GATE.md
KNOWN-LIMITATIONS.md
COMPLETION-NOTE.md
PRIORITY-AUDIT.md
```

## Remaining local / external work

These are intentionally not completed through remote repository edits:

- [x] Resolve `REVIEW-BLOCKERS.md`.
- [x] Python syntax compilation from fresh local clone.
- [x] Local dispatcher smoke run from fresh local clone.
- [x] Local HTTP gateway run from fresh local clone.
- [x] HTTP smoke script run from fresh local clone.
- [x] Eval runner execution from fresh local clone.
- [x] Alignment checker execution from fresh local clone.
- [ ] Knowledge compiler execution from fresh local clone.
- [ ] OpenAPI schema validation from fresh local clone.
- [ ] GPT Builder manual preview.
- [ ] Gateway staging deployment.
- [ ] Gateway production deployment.
- [ ] GPT Actions authentication setup.

Use:

```text
REVIEW-BLOCKERS.md
LOCAL-TEST-PLAN.md
LOCAL-TEST-QUICKSTART.md
GPT-BUILDER-RUNBOOK.md
GATEWAY-DEPLOYMENT-RUNBOOK.md
PRODUCTION-READINESS-CHECKLIST.md
```

## Completion statement

Repository-side release preparation materials exist, but the current `online-gpt/` RC is blocked by review findings.

The next required action is to fix `REVIEW-BLOCKERS.md`, rerun the specified tests, and update local test notes.

P2 Adapter results must not be used to override or replace P0/P1 acceptance results.
