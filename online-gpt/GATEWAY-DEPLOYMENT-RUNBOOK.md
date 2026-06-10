# Gateway Deployment Runbook

This runbook describes how to deploy the PEtFiSh Online Gateway for P1 Gateway Mode.

It does not enable Adapter Mode execution.

## Deployment scope

In scope:

- Gateway-only API;
- health and version endpoints;
- route/profile/catalog/install/trust/skill endpoints;
- API key authentication;
- HTTPS reverse proxy;
- request logging;
- rate limiting;
- remote execution kill switch.

Out of scope:

- local daemon connection;
- OpenCode/Codex/Antigravity execution;
- remote execute enablement;
- desktop bridge;
- unscoped shell access.

## Runtime model

```text
ChatGPT GPT Actions
    -> HTTPS Gateway host
    -> reverse proxy
    -> python online-gpt/gateway/server.py
    -> deterministic gateway modules
```

## Recommended hosts

```text
https://api-staging.petfish.ai
https://api.petfish.ai
```

Use staging first.

## Environment variables

Recommended:

```text
PETFISH_GATEWAY_ENV=staging
PETFISH_GATEWAY_VERSION=0.1.0
PETFISH_GATEWAY_GIT_REF=<commit-sha>
PETFISH_GATEWAY_API_KEY=<secret>
PETFISH_REMOTE_EXECUTE_ENABLED=false
PETFISH_ADAPTER_MODE_ENABLED=false
```

The stdlib skeleton may not consume all variables yet. Production wrappers should.

## Local smoke deployment

From repository root:

```text
python online-gpt/gateway/server.py --host 127.0.0.1 --port 8787
```

In another terminal:

```text
bash online-gpt/gateway/http-smoke.sh
```

Expected:

- `/healthz` returns ok;
- `/v1/health` returns ok;
- `/v1/version` returns version metadata;
- P1 POST endpoints return module envelopes;
- no local execution occurs.

## Minimal reverse proxy shape

Use any HTTPS-capable reverse proxy.

Conceptual routing:

```text
api-staging.petfish.ai -> 127.0.0.1:8787
api.petfish.ai         -> 127.0.0.1:8787
```

Required proxy behavior:

- terminate TLS;
- pass JSON bodies unchanged;
- preserve request path;
- reject large bodies;
- redact Authorization in logs;
- add trace ID if possible.

## Authentication

First release recommendation:

```text
Authorization: Bearer <PETFISH_GATEWAY_TOKEN>
```

Alternative:

```text
X-PEtFiSh-Gateway-Key: <PETFISH_GATEWAY_TOKEN>
```

Production wrapper must reject requests without a valid key.

Do not put tokens in:

- repository files;
- Knowledge files;
- test notes committed to git;
- GPT conversation starters.

## Required P1 endpoints

Gateway-only GPT Actions must use only:

```text
GET  /v1/health
GET  /v1/version
POST /v1/kernel/route
POST /v1/catalog/search
POST /v1/catalog/suggest
POST /v1/install/render
POST /v1/project/profile
POST /v1/skill/design
POST /v1/trust/classify
```

Do not expose these through gateway-only Actions:

```text
POST /v1/remote/preview
POST /v1/remote/execute
```

They may exist in `server.py` as P2 skeleton endpoints, but first-release GPT Actions must not import them.

## Gateway-only OpenAPI preparation

Before importing into GPT Builder:

1. Copy `online-gpt/actions/openapi.gateway-only.yaml`.
2. Replace server URL with staging or production host.
3. Validate schema.
4. Confirm no `/v1/remote/*` paths exist.

Validation:

```text
uvx openapi-spec-validator online-gpt/actions/openapi.gateway-only.yaml
```

## Health check expectations

`/v1/health` should return:

```json
{
  "ok": true,
  "service": "petfish-online-gateway",
  "mode": "gateway-only",
  "remote_execute_enabled": false
}
```

`/v1/version` should return:

```json
{
  "service": "petfish-online-gateway",
  "version": "0.1.0",
  "source": "kylecui/petfish.ai",
  "git_ref": "<commit-sha>"
}
```

## Logging requirements

Log:

```text
trace_id
operation
path
ok
module
mode
result_level
latency_ms
status_code
```

Do not log:

```text
Authorization
API key
password
secret
token
private customer content
raw local filesystem content
```

## Rate limiting

Initial recommendation:

```text
staging:    60 requests/minute per key
production: 120 requests/minute per key
```

Reduce during preview if logs show accidental loops.

## Kill switches

Production wrapper must support:

```text
PETFISH_REMOTE_EXECUTE_ENABLED=false
PETFISH_ADAPTER_MODE_ENABLED=false
```

If a full schema is accidentally imported, these flags must still prevent execution.

## Staging acceptance

- [ ] HTTPS endpoint reachable.
- [ ] API key required.
- [ ] `/v1/health` ok.
- [ ] `/v1/version` returns correct git ref.
- [ ] Gateway-only OpenAPI imports in GPT Builder.
- [ ] P1 prompt tests pass.
- [ ] No `/v1/remote/*` paths in gateway-only schema.
- [ ] remote execute disabled.
- [ ] logs redact secrets.

## Production acceptance

- [ ] Staging acceptance complete.
- [ ] Production host uses release commit or tag.
- [ ] API key rotated for production.
- [ ] P0 Preview still passes without Actions.
- [ ] P1 Gateway Preview passes with production Actions.
- [ ] P2 boundary prompts do not overclaim control.
- [ ] rollback plan exists.

## api-stage operational procedures

### Server layout

```text
Host:       165.154.218.237 (SSH: ubuntu@)
Gateway:    /home/ubuntu/petfish-gateway/gateway/
Static site: /var/www/petfish.ai/
Service:    petfish-gateway.service (systemd)
Reverse proxy: nginx (sites: petfish-gateway, petfish.ai, remote.petfish.ai)
Co-tenant:  petfish-remote.service (Telegram bot) — DO NOT TOUCH
```

### Deploy gateway update

The server does not have a git clone. Files are deployed via scp.

```bash
# 0. Run schema drift check locally (MUST pass before deploy)
python3 online-gpt/gateway/check_schema_drift.py
# If drift > 0, fix handler or schema before deploying.

# 1. Backup current files
ssh ubuntu@165.154.218.237 \
  "cd /home/ubuntu/petfish-gateway/gateway && \
   cp app.py app.py.bak && \
   cp router.py router.py.bak"

# 2. Upload changed files
scp online-gpt/gateway/app.py ubuntu@165.154.218.237:/home/ubuntu/petfish-gateway/gateway/app.py
scp online-gpt/gateway/router.py ubuntu@165.154.218.237:/home/ubuntu/petfish-gateway/gateway/router.py

# 3. Restart only the gateway service (NOT nginx, NOT remote)
ssh ubuntu@165.154.218.237 \
  "sudo systemctl restart petfish-gateway.service && \
   sleep 2 && \
   sudo systemctl status petfish-gateway.service --no-pager"

# 4. Smoke test (includes Phase 0 drift check on server)
ssh ubuntu@165.154.218.237 \
  "python3 /home/ubuntu/petfish-gateway/gateway/smoke_full.py"
```

### Rollback gateway

```bash
ssh ubuntu@165.154.218.237 \
  "cd /home/ubuntu/petfish-gateway/gateway && \
   cp app.py.bak app.py && \
   cp router.py.bak router.py && \
   sudo systemctl restart petfish-gateway.service"
```

### Known limitations

- No CI/CD — manual scp + restart.
- API key is hardcoded in systemd unit file (`/etc/systemd/system/petfish-gateway.service`).
- No automatic backup rotation — `.bak` files accumulate.
- Gateway runs on `/usr/bin/python3` (system python), not uv-managed.

## Rollback

If Gateway Actions behave incorrectly:

1. Disable Actions in GPT Builder.
2. Revert GPT to P0 Standalone Mode.
3. Keep published GPT private or link-only.
4. Inspect Gateway logs by trace ID.
5. Fix staging first.
6. Re-import schema only after validation.

If remote execution appears enabled unexpectedly:

1. Disable Actions immediately.
2. Set kill switches to false.
3. Rotate Gateway API key.
4. Inspect whether full `openapi.yaml` was imported.
5. Replace with `openapi.gateway-only.yaml`.
6. Run P2 boundary regression prompts.
