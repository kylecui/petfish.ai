# API Infrastructure Plan

This plan covers Gateway Mode API infrastructure that is not completed by repository-only edits.

The repository now includes a stdlib HTTP server for local smoke testing. Production infrastructure is a separate deployment task.

## Current repository state

Implemented:

- OpenAPI contract: `actions/openapi.yaml`;
- local dispatcher: `gateway/app.py`;
- stdlib HTTP server: `gateway/server.py`;
- smoke script: `gateway/http-smoke.sh`;
- module contracts: `gateway/CONTRACTS.md`;
- HTTP docs: `gateway/HTTP-GATEWAY.md`.

Not implemented in repository-only work:

- public hosted API endpoint;
- authentication;
- persistent catalog backend;
- production logs;
- rate limiting;
- secret redaction middleware;
- deployment automation.

## Recommended deployment phases

### Phase 1: Local API smoke

Run locally:

```text
python online-gpt/gateway/server.py --host 127.0.0.1 --port 8787
bash online-gpt/gateway/http-smoke.sh
```

Goal: verify path-to-operation mapping and module envelopes.

### Phase 2: Internal hosted Gateway

Host the Gateway behind an internal URL.

Add:

- HTTPS;
- simple API key or signed request auth;
- request size limit;
- structured logging;
- trace ID;
- CORS policy suitable for GPT Actions;
- environment-controlled remote execute disable flag.

### Phase 3: GPT Actions integration

Update `actions/openapi.yaml` server URL from placeholder to the internal hosted Gateway.

Import into GPT Builder.

Test:

- route;
- catalog suggest;
- command rendering;
- skill design;
- Trust Gate classification;
- remote preview;
- remote execute disabled behavior.

### Phase 4: Catalog backend

Replace static pack metadata with a source-of-truth-backed catalog provider.

Candidate sources:

- core repository pack manifests;
- petfish-market registry;
- generated index artifact;
- signed static JSON bundle.

### Phase 5: Adapter Mode bridge

Only after Gateway Mode is stable:

- register local daemon;
- implement preview only;
- integrate Trust Gate;
- add approval token;
- add audit trace;
- keep execution disabled until all checks pass.

## Production non-goals for this phase

Do not implement yet:

- autonomous local execution;
- unscoped shell access;
- persistent secret storage;
- online-only pack semantics;
- replacement Companion Gateway logic.

## Acceptance before GPT publication

- Standalone Mode works without Actions.
- Gateway Mode API passes local smoke tests.
- OpenAPI schema imports into GPT Builder.
- Remote execute is disabled or approval-protected.
- Source-of-truth alignment checks pass.
