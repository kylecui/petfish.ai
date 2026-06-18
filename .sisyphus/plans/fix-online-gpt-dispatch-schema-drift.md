# Fix: online-gpt dispatch schema drift — allowlist filter + runtime support

## Problem

`dispatch()` in `app.py` passes raw `**payload` to handler functions. When GPT sends fields declared in OpenAPI schema but not in Python function signatures, it crashes with `TypeError: unexpected keyword argument`.

Two confirmed cases:
1. **`routeCompanionRequest` + `runtime`**: `openapi.gateway-only.yaml` declares `runtime?: RuntimeContext` in RouteRequest, but `route_companion_request()` in `router.py` doesn't accept it.
2. **`suggestPacks` + `risk_sensitive`**: schema declares `risk_sensitive?: boolean`, but dispatch routes to `profile_project()` which doesn't accept it.

## Approach: Short-term C + Long-term A

### Short-term: Unified allowlist filter in dispatch()

**File**: `online-gpt/gateway/app.py`

Add `inspect.signature`-based parameter filtering in `dispatch()`:
1. Map action names to handler functions via a dict (replace if-chain)
2. Before calling handler, filter payload to only keys matching handler's signature params
3. Add any extra keys to `warnings` in the response envelope
4. Zero behavioral change for well-formed payloads — only strips unknown fields

### Long-term: Add `runtime` to `route_companion_request()`

**File**: `online-gpt/gateway/router.py`

Add `runtime: dict | None = None` parameter to `route_companion_request()`. Use it to:
1. Override `platform` to `"online"` when `runtime.kind == "online"`
2. Set `result_level` based on `runtime.execution_truth_default`
3. Pass runtime info into response data for downstream consumers

This is a separate commit — the short-term fix works without it.

## Files to Change

1. `online-gpt/gateway/app.py` — refactor dispatch to use allowlist filter
2. `online-gpt/gateway/router.py` — add `runtime` parameter (long-term, separate commit)

## What NOT to Change

- `openapi.yaml` / `openapi.gateway-only.yaml` — schemas are correct, backend needs to catch up
- Handler function signatures for other 7 operations — they already match their schemas
- `server.py` — not involved in this dispatch path
- Test files — out of scope

## Risk Assessment

- **Low risk**: The allowlist filter is purely additive — existing payloads that match signatures are unaffected
- **Zero breaking change**: All currently working calls continue to work identically
- **The filter is defensive**: Even if we later add `runtime` to the handler, the filter becomes a no-op for that field

## Verification

1. The three test payloads from the bug report (ping, full-ish, runtime-object) should all return `ok: true`
2. The runtime-object payload should include `"warnings": ["ignored_unknown_fields: ['runtime']"]` (short-term)
3. After long-term fix, runtime-object payload should include runtime info in response data, no warning
