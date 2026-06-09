# Actions

This directory contains the GPT Actions contract for PEtFiSh Companion GPT.

## Files

```text
actions/
├── README.md
├── openapi.yaml
├── action-policy.md
└── examples/
```

## How to use

1. Deploy a gateway that implements `openapi.yaml`.
2. Replace the placeholder server URL with the deployed gateway URL.
3. Import the schema into GPT Builder Actions.
4. Test each example request before sharing the GPT.

## Contract discipline

The Actions contract is not a convenience layer around arbitrary shell execution. It is a controlled module surface:

- routing;
- catalog search;
- project profiling;
- command rendering;
- skill design;
- trust classification;
- remote preview;
- remote execution only when explicitly enabled.

## Result envelope

All Actions should return a common module envelope:

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

## Safety rule

`/v1/remote/execute` must remain disabled or approval-protected until the remote daemon, trust gate, and audit trail are implemented.
