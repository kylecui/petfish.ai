# Online GPT Review Blockers

This document records the current review result for the local-team completion claim.

Review status: **READY FOR RC REVIEW**

All identified blockers (B1, F1, F2, F3) are now resolved. The RC is ready for re-review.

## Summary

The local team has resolved all review blockers identified in the previous review round. The profiler control-flow bug is fixed, gateway-only OpenAPI is the primary validation target, health/version metadata is enriched, and HTTP smoke covers all endpoints.

## Blocker 1: `profile_project()` may return `None` for normal P0/P1 profiling

### File

```text
online-gpt/gateway/modules/profiler.py
```

### Problem

The online-review special case returns correctly, but the generic profile logic appears after `_is_online_review_project()` and after that helper's `return` statement.

As a result, the generic security/deploy/research/ppt/course profiling block is unreachable, and `profile_project()` can return `None` for normal project descriptions that are not detected as online code review projects.

### Why this is blocking

This breaks primary P0/P1 behavior, including:

```text
POST /v1/catalog/suggest
POST /v1/project/profile
router.py install_plan path
```

`gateway/app.py` maps both `suggestPacks` and `profileProject` directly to `profile_project()`.

`gateway/router.py` also calls `profile_project()` in the install route and expects an envelope:

```text
prof = profile_project(...)
packs = prof["data"].get(...)
```

If `prof` is `None`, the route can fail at runtime.

### Required fix

Move the generic profile classification logic back into `profile_project()`.

`_is_online_review_project()` must only detect whether the request is an online review project. It must not contain generic profile-building code after its own `return`.

Expected structure:

```text
def profile_project(...):
    initialize packs/profile/reasons

    if _is_online_review_project(...):
        return online_review_envelope

    if security/audit/trust terms:
        add trust/deploy/testdocs
        profile = security

    if deploy terms:
        add deploy

    if test terms:
        add testdocs

    if research terms:
        add research/doc-reader

    if ppt terms:
        add ppt

    if course terms:
        add course/doc-reader

    return generic_profile_envelope


def _is_online_review_project(...):
    return online and review
```

### Required direct smoke test

Run from repository root:

```text
python - <<'PY'
import sys
sys.path.insert(0, "online-gpt/gateway")
from modules.profiler import profile_project

cases = [
    ("AI security research project with docs, PPT, deploy and trust policy", "opencode"),
    ("ChatGPT-only code review project", "online"),
    ("course material with labs and PPT", "opencode"),
    ("deployment project with rollback and health checks", "opencode"),
]

for text, platform in cases:
    result = profile_project(text, platform=platform)
    assert result is not None, (text, platform, "returned None")
    assert result["ok"] is True, result
    assert "packs" in result["data"], result
    assert result["data"]["packs"], result
    print(text, "=>", result["data"].get("recommended_profile"), result["data"]["packs"])
PY
```

Expected: all cases return valid module envelopes with non-empty `packs`.

## Required follow-up fixes

These are not as severe as the profiler blocker, but they should be fixed before RC tagging.

### Follow-up 1: Local test plan should validate gateway-only OpenAPI for first release

File:

```text
online-gpt/LOCAL-TEST-PLAN.md
```

Current issue:

Some sections still instruct testers to validate or inspect:

```text
online-gpt/actions/openapi.yaml
```

For first-release P1 Gateway Mode, the primary schema must be:

```text
online-gpt/actions/openapi.gateway-only.yaml
```

Required change:

- Use `openapi.gateway-only.yaml` for first-release / P1 validation.
- Keep full `openapi.yaml` only as non-first-release or P2 reference material.

### Follow-up 2: `server.py` health/version response should match runbook expectations

File:

```text
online-gpt/gateway/server.py
```

Current issue:

`/v1/health` and `/v1/version` exist, but their response body is thinner than the Gateway deployment runbook and OpenAPI expectations.

Required `/v1/health` fields:

```json
{
  "ok": true,
  "service": "petfish-online-gateway",
  "mode": "gateway-only",
  "remote_execute_enabled": false
}
```

Required `/v1/version` fields:

```json
{
  "ok": true,
  "service": "petfish-online-gateway",
  "version": "0.1.0",
  "source": "kylecui/petfish.ai",
  "git_ref": "<env-or-dev>"
}
```

Use environment variables when available:

```text
PETFISH_GATEWAY_ENV
PETFISH_GATEWAY_VERSION
PETFISH_GATEWAY_GIT_REF
PETFISH_REMOTE_EXECUTE_ENABLED
```

Default to safe values when env vars are absent.

### Follow-up 3: `http-smoke.sh` should cover `/v1/health` and `/v1/version`

File:

```text
online-gpt/gateway/http-smoke.sh
```

Required additions:

```text
echo "== v1 health =="
curl -sS "$BASE_URL/v1/health" | python -m json.tool

echo "== v1 version =="
curl -sS "$BASE_URL/v1/version" | python -m json.tool
```

Keep `/healthz` for backward compatibility.

## Positive findings to preserve

The following local-team changes are directionally correct and should be preserved:

### `online` platform support

`online` is now represented in schema/platform handling. This is correct for ChatGPT page / ChatGPT Project usage.

### `installer.py` online semantic-only behavior

For `platform == "online"`, install rendering should not generate a local mutation command. It should return semantic-only advice and state that no local files are modified.

This behavior is correct and should be kept.

### `trust_gate.py` online runtime boundary

For `target_runtime == "online"` plus execution terms, Trust Gate should return preview-only behavior and explain that online runtime has no local execution adapter.

This behavior is correct and should be kept.

### Gateway-only OpenAPI excludes P2 remote endpoints

`actions/openapi.gateway-only.yaml` must continue to exclude:

```text
/v1/remote/preview
/v1/remote/execute
```

This is correct for first-release Gateway Mode.

## Required retest after fixes

Run these after applying the fixes:

```text
python -m py_compile online-gpt/gateway/app.py online-gpt/gateway/router.py online-gpt/gateway/server.py online-gpt/gateway/schemas.py online-gpt/gateway/eval_runner.py online-gpt/gateway/modules/catalog.py online-gpt/gateway/modules/installer.py online-gpt/gateway/modules/profiler.py online-gpt/gateway/modules/remote_control.py online-gpt/gateway/modules/skill_workbench.py online-gpt/gateway/modules/trust_gate.py online-gpt/tools/check_alignment.py online-gpt/tools/compile_knowledge.py
```

```text
python online-gpt/gateway/app.py
```

```text
python online-gpt/gateway/server.py --host 127.0.0.1 --port 8787
```

In another terminal:

```text
bash online-gpt/gateway/http-smoke.sh
```

Validate gateway-only OpenAPI:

```text
uvx openapi-spec-validator online-gpt/actions/openapi.gateway-only.yaml
```

Run the direct profiler smoke test listed above.

## Acceptance after fix

Mark this review as resolved only if:

- `profile_project()` never returns `None` for valid project descriptions;
- P0/P1 pack/profile recommendation works for security, research, deploy, course, and online-review cases;
- `/v1/health` and `/v1/version` return runbook-compatible metadata;
- HTTP smoke covers both legacy `/healthz` and versioned health/version endpoints;
- first-release validation uses `openapi.gateway-only.yaml`;
- P2 Adapter remains boundary/regression only.

## Current decision

```text
READY FOR RC REVIEW (not yet publication-ready)
```

Next action: re-review by reviewer; GPT Builder / production publication still requires final human confirmation.
