# PEtFiSh Online Gateway Skeleton

This directory contains a reference skeleton for the deterministic part of PEtFiSh Companion GPT.

It intentionally avoids framework dependencies. A production gateway can wrap these functions with FastAPI, Cloudflare Workers, an MCP server, or another HTTP runtime.

## Goals

- keep routing and policy testable outside GPT;
- keep GPT Actions schemas aligned with module contracts;
- make side-effect boundaries explicit;
- support mock/read-only/dry-run adapters before real remote execution is connected.

## Files

```text
gateway/
├── README.md
├── app.py              # simple dispatcher for local smoke tests
├── schemas.py          # shared constants and envelope helpers
├── router.py           # Companion Kernel routing logic
└── modules/
    ├── catalog.py
    ├── installer.py
    ├── profiler.py
    ├── skill_workbench.py
    ├── trust_gate.py
    └── remote_control.py
```

## Local smoke use

```bash
python online-gpt/gateway/app.py
```

The skeleton should print representative outputs for route, profile, install render, trust classify, and remote preview.

## Adapter rule

Real adapters must preserve the same module envelope:

```json
{
  "ok": true,
  "module": "installer",
  "mode": "dry_run",
  "result_level": "command_rendered",
  "data": {},
  "warnings": [],
  "errors": [],
  "audit": {}
}
```
