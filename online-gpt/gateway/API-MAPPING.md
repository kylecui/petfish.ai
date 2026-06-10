# Gateway API Mapping

This document maps GPT Actions operation IDs to gateway modules.

## Mapping table

| Operation ID | Path | Module | Result level | Side effect |
|---|---|---|---|---|
| `routeCompanionRequest` | `/v1/kernel/route` | `router.py` | varies | no |
| `searchCatalog` | `/v1/catalog/search` | `modules/catalog.py` | `advice_only` | no |
| `suggestPacks` | `/v1/catalog/suggest` | `modules/profiler.py` + `modules/catalog.py` | `advice_only` | no |
| `renderInstallCommand` | `/v1/install/render` | `modules/installer.py` | `command_rendered` | no |
| `profileProject` | `/v1/project/profile` | `modules/profiler.py` | `advice_only` | no |
| `designSkill` | `/v1/skill/design` | `modules/skill_workbench.py` | `advice_only` | no |
| `classifyActionRisk` | `/v1/trust/classify` | `modules/trust_gate.py` | `advice_only` | no |
| `previewRemoteExecution` | `/v1/remote/preview` | `modules/remote_control.py` | `previewed` | no |
| `executeRemoteCommand` | `/v1/remote/execute` | `modules/remote_control.py` | `previewed` until enabled | yes when enabled |

## Dispatcher rule

The stdlib dispatcher in `app.py` uses the same operation IDs as `actions/openapi.yaml`.

This makes it possible to smoke-test Action behavior before an HTTP server exists.

## Wrapper rule

A production HTTP wrapper should be thin:

```text
HTTP request -> payload validation -> dispatch(operationId, payload) -> module envelope -> HTTP response
```

The wrapper should not duplicate module policy.

## Error rule

All module errors should still return a module envelope where possible:

```json
{
  "ok": false,
  "module": "installer",
  "mode": "dry_run",
  "result_level": "advice_only",
  "data": {},
  "warnings": [],
  "errors": ["No packs were provided."],
  "audit": {}
}
```

## Trace rule

When deployed as a service, every request should receive a trace ID.

Trace IDs should record:

- operation ID;
- module;
- result level;
- policy decision;
- timestamp;
- adapter mode.

Trace logs must not contain raw secrets.
