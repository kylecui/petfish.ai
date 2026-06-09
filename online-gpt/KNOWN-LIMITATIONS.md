# Known Limitations

This document records limitations of the current `online-gpt/` subsystem skeleton.

## 1. Gateway is a skeleton

The gateway is stdlib-only and deterministic. It is not yet an HTTP service.

Current status:

- can dispatch local smoke actions;
- can render install commands;
- can profile projects heuristically;
- can classify common action risks;
- can preview remote-control flow;
- cannot call real petfish-market;
- cannot inspect a local repository;
- cannot execute local OpenCode, Codex, or Antigravity.

## 2. Remote execution is disabled

`/v1/remote/execute` exists as a contract, but execution must remain disabled until a trusted daemon, approval flow, and audit log exist.

## 3. Knowledge files are partly hand-curated

Knowledge files are aligned with core PEtFiSh intent, but not all are generated from source-of-truth files yet.

`tools/compile_knowledge.py` is a scaffold for reducing manual drift.

## 4. Eval runner checks gateway output, not final GPT prose

The current eval runner validates deterministic routing output. It does not evaluate the final natural-language answer produced by ChatGPT.

Future work should add:

- GPT response snapshot tests;
- prompt regression tests;
- OpenAPI integration tests;
- remote daemon preview tests.

## 5. OpenAPI is a contract, not a deployed service

`actions/openapi.yaml` uses a placeholder server URL. It must be replaced when a real gateway is deployed.

## 6. Alignment checker is conservative

`tools/check_alignment.py` catches obvious drift only. It does not yet parse all pack manifests or compare every profile mapping automatically.

## 7. Local tests are required before merge or publication

Use:

```text
online-gpt/LOCAL-TEST-PLAN.md
```

Do not publish the GPT or enable remote execution before local tests pass.
