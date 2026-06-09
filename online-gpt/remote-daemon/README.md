# Remote Daemon

This directory contains the contract for a future `petfish_remote` daemon that can connect PEtFiSh Companion GPT to local runtimes.

The daemon is not required for GPT Builder configuration or command rendering. It is required only for verified local preview and approved execution.

## Files

```text
remote-daemon/
├── README.md
└── SPEC.md
```

## Default stance

Remote execution is disabled by default.

A daemon implementation must first support:

1. runtime registration;
2. project aliases;
3. side-effect-free preview;
4. Trust Gate integration;
5. approval token flow;
6. audit trace;
7. secret redaction.

Only after those are working should execution adapters be enabled.
