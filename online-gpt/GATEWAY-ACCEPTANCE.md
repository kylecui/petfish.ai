# Gateway Mode Acceptance Criteria

Gateway Mode is the second priority for PEtFiSh Companion GPT.

It adds online API capabilities while preserving the rule that IDE/CLI tools are optional adapters, not dependencies.

## Required inputs

Gateway Mode uses:

```text
GPT Instructions
GPT Knowledge
GPT Actions
PEtFiSh Online Gateway API
```

It does not require:

- OpenCode;
- Codex;
- Antigravity;
- Cursor;
- GitHub Copilot;
- Windsurf;
- local daemon;
- local filesystem access.

## Required API capabilities

Gateway Mode must expose:

- request routing;
- catalog search;
- pack suggestion;
- project profiling;
- install command rendering;
- skill design;
- action risk classification;
- remote preview contract;
- disabled or approval-protected remote execute contract.

## Required paths

These paths must exist in both `actions/openapi.yaml` and `gateway/server.py`:

```text
/v1/kernel/route
/v1/catalog/search
/v1/catalog/suggest
/v1/install/render
/v1/project/profile
/v1/skill/design
/v1/trust/classify
/v1/remote/preview
/v1/remote/execute
```

## Required dispatcher coverage

These operation IDs must exist in `gateway/app.py`:

```text
routeCompanionRequest
searchCatalog
suggestPacks
renderInstallCommand
profileProject
designSkill
classifyActionRisk
previewRemoteExecution
executeRemoteCommand
```

## Required boundaries

Gateway Mode must not:

- claim local execution;
- require local IDE/CLI agents;
- weaken source-of-truth alignment;
- invent official pack aliases;
- bypass Trust Gate;
- enable remote execute by default.

## Manual local acceptance commands

Start the server:

```text
python online-gpt/gateway/server.py --host 127.0.0.1 --port 8787
```

Run smoke requests:

```text
bash online-gpt/gateway/http-smoke.sh
```

Expected:

- health check returns `ok: true`;
- route endpoint returns a module envelope;
- suggest endpoint returns profile/pack suggestions;
- install endpoint returns `command_rendered`;
- trust endpoint returns risk classification;
- remote execute remains disabled or approval-protected.

## Pass condition

Gateway Mode passes when the HTTP API implements the OpenAPI operation surface and returns module envelopes without relying on local IDE/CLI tools.
