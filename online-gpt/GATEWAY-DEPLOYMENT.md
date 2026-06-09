# Gateway Mode Deployment Plan

Gateway Mode is the second priority after Standalone Mode.

It provides online APIs for PEtFiSh Companion GPT without depending on OpenCode, Codex, Antigravity, desktop clients, or local daemons.

## Goal

Deploy a PEtFiSh Online Gateway that supports GPT Actions for:

- request routing;
- catalog search;
- profile suggestion;
- pack resolution;
- install command rendering;
- skill contract rendering;
- Trust Gate classification;
- server-side eval and policy checks.

## Non-goals

Gateway Mode does not need to:

- execute local shell commands;
- control OpenCode/Codex/Antigravity;
- access a user's local filesystem;
- replace 胖鱼遥控器;
- require a desktop daemon.

## Recommended service shape

```text
ChatGPT GPT
    |
    | GPT Actions
    v
PEtFiSh Online Gateway API
    |
    +-- Kernel Router
    +-- Catalog Service
    +-- Profile Service
    +-- Install Renderer
    +-- Skill Workbench
    +-- Trust Gate
    +-- Eval Service
    +-- Audit/Event Log
```

## Minimal deployable API

The first deployable Gateway should expose:

```text
POST /v1/kernel/route
POST /v1/catalog/search
POST /v1/catalog/suggest
POST /v1/install/render
POST /v1/project/profile
POST /v1/skill/design
POST /v1/trust/classify
GET  /v1/health
GET  /v1/version
```

`/v1/remote/preview` and `/v1/remote/execute` may remain unimplemented, disabled, or hidden from the GPT Action schema until Adapter Mode becomes relevant.

## Suggested stack

Since Gateway Mode is API-focused and server resources are available, use a simple service stack first:

```text
FastAPI or similar Python HTTP layer
stdlib/deterministic gateway modules
JSON files or SQLite for initial catalog state
structured JSON logs
reverse proxy with TLS
```

Do not introduce a complex service mesh, queue, or database until needed.

## Configuration

Suggested environment variables:

```text
PETFISH_GATEWAY_ENV=dev|staging|prod
PETFISH_GATEWAY_VERSION=0.1.0
PETFISH_GATEWAY_ALLOWED_ORIGINS=...
PETFISH_GATEWAY_LOG_LEVEL=info
PETFISH_GATEWAY_CATALOG_SOURCE=local|market|hybrid
PETFISH_GATEWAY_REMOTE_EXECUTE_ENABLED=false
```

Remote execution must default to false.

## Server-side data sources

Priority order:

1. core repository source-of-truth files;
2. generated Knowledge/cached index;
3. petfish-market registry;
4. future database cache.

Gateway must not invent pack aliases or profile mappings.

## Health and version endpoints

`GET /v1/health` should return:

```json
{
  "ok": true,
  "service": "petfish-online-gateway",
  "mode": "gateway",
  "remote_execute_enabled": false
}
```

`GET /v1/version` should return:

```json
{
  "service": "petfish-online-gateway",
  "version": "0.1.0",
  "source": "petfish.ai",
  "git_ref": "dev-or-release-sha"
}
```

## Logging

Log per request:

- trace ID;
- operation ID;
- result level;
- module;
- risk class when applicable;
- warnings count;
- error count;
- elapsed time.

Do not log raw secrets or full user payloads by default.

## Deployment sequence

1. Keep Standalone Mode working in GPT Builder.
2. Deploy Gateway with health/version only.
3. Add catalog/profile/install/trust endpoints.
4. Import Actions into GPT Builder against staging URL.
5. Run action examples.
6. Run eval suite against local skeleton and deployed API.
7. Promote URL to production GPT configuration.
8. Keep Adapter Mode disabled.

## Acceptance criteria

Gateway Mode is acceptable when:

- OpenAPI imports in GPT Builder;
- health/version endpoints work;
- catalog/profile/install/trust endpoints return module envelopes;
- install rendering does not claim execution;
- Trust Gate classifies risky actions;
- source-of-truth alignment checks pass;
- remote execution is disabled or absent.
