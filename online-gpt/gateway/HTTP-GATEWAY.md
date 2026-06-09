# HTTP Gateway

`gateway/server.py` provides a stdlib-only HTTP surface for Gateway Mode.

It is intended for local smoke testing and simple deployment experiments. A production deployment may later wrap the same dispatch contracts with FastAPI, Cloudflare Workers, or another serverless platform.

## Start server

```text
python online-gpt/gateway/server.py --host 127.0.0.1 --port 8787
```

Health check:

```text
curl -sS http://127.0.0.1:8787/healthz | python -m json.tool
```

## Smoke script

In another terminal:

```text
bash online-gpt/gateway/http-smoke.sh
```

## Implemented paths

| Path | Operation ID |
|---|---|
| `GET /healthz` | health check |
| `POST /v1/kernel/route` | `routeCompanionRequest` |
| `POST /v1/catalog/search` | `searchCatalog` |
| `POST /v1/catalog/suggest` | `suggestPacks` |
| `POST /v1/install/render` | `renderInstallCommand` |
| `POST /v1/project/profile` | `profileProject` |
| `POST /v1/skill/design` | `designSkill` |
| `POST /v1/trust/classify` | `classifyActionRisk` |
| `POST /v1/remote/preview` | `previewRemoteExecution` |
| `POST /v1/remote/execute` | `executeRemoteCommand` |

## Contract

Every POST endpoint accepts a JSON object whose fields match the corresponding dispatcher function.

Every endpoint returns a module envelope.

## Gateway Mode boundary

The HTTP gateway is not an execution agent.

It can:

- route;
- profile;
- search catalog metadata;
- render commands;
- classify risk;
- produce previews.

It must not claim local execution. Local execution requires Adapter Mode and execution proof.

## Production wrapper requirements

A production wrapper should add:

- authentication;
- rate limiting;
- request size limits;
- structured trace IDs;
- secret redaction;
- deployment logging;
- OpenAPI validation;
- optional persistent catalog source.

The wrapper should not duplicate module policy. Policy belongs in gateway modules and Trust Gate.
