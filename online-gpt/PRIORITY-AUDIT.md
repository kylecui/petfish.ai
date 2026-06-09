# Priority Audit Report

This report records the priority audit for the `online-gpt/` subsystem.

The audit was triggered by the risk that P2 Adapter Mode tests could be mistaken for primary acceptance tests.

## Audit rule

All documentation must preserve this priority:

```text
P0. Standalone Mode: primary acceptance
P1. Gateway Mode: primary acceptance after P0
P2. Adapter Mode: optional boundary/regression only
```

## Audited and updated files

### Core product docs

| File | Result |
|---|---|
| `README.md` | already states P0/P1/P2 priority and Adapter low priority |
| `ARCHITECTURE.md` | already states Adapter Mode is future/low-priority extension |
| `PRINCIPLES.md` | already states GPT version is independently operable |
| `OPERATING-MODES.md` | already states P0/P1 useful even if P2 never ships |
| `PRIORITY-GUARDRAIL.md` | added as hard cross-document rule |

### GPT behavior docs

| File | Result |
|---|---|
| `instructions/petfish-companion.instructions.md` | updated to force P0/P1/P2 classification and label P2 as boundary/regression only |
| `GPT-BUILDER.md` | already excludes Adapter Mode from first GPT configuration |
| `GPT-CONFIG-PACKAGE.md` | should be read with `PRIORITY-GUARDRAIL.md` and `GPT-BUILDER.md` |
| `PUBLISH-CHECKLIST.md` | updated to separate P0/P1 primary checks from optional P2 boundary checks |

### Test and quality docs

| File | Result |
|---|---|
| `LOCAL-TEST-PLAN.md` | already updated to P0/P1/P2 sequence |
| `LOCAL-TEST-QUICKSTART.md` | updated to add P0 review before Gateway tests and label P2 boundary tests |
| `QUALITY-GATE.md` | updated with Gate 0 mode priority and P2 boundary rule |
| `evals/README.md` | updated to state P2 evals are boundary/regression only |
| `FINAL-DEVELOPMENT-CHECKLIST.md` | updated to include priority guardrail and audit references |

### Remote/adapter docs

| File | Result |
|---|---|
| `knowledge/07-remote-control-model.md` | updated to label as P2 boundary Knowledge only and not first-upload material |
| `remote-daemon/README.md` | existing content should be interpreted as P2 only |
| `remote-daemon/SPEC.md` | existing content should be interpreted as P2 only |
| `ADAPTER-ACCEPTANCE.md` | already states Adapter Mode is optional |

## Problem pattern removed

The risky pattern was:

```text
Manual tests mention direct OpenCode/Codex control near primary acceptance checks.
```

This can cause testers to think Adapter Mode is the main product path.

Correct pattern now:

```text
P0/P1 tests first.
P2 tests only after P0/P1, and only as boundary/regression checks.
```

## Test interpretation rule

These are primary tests:

```text
什么是 PEtFiSh Companion GPT？它是否必须依赖 OpenCode？
帮我给一个安全研究项目选择 packs。
帮我设计一个 research clipping skill。
帮我生成安装命令和验证步骤。
Gateway API smoke tests.
```

These are P2 boundary/regression tests only:

```text
在线 GPT 能不能直接控制我的本地 OpenCode？
远程控制我的 OpenCode。
请预览让本地 OpenCode 执行质量门，但不要真正执行。
```

## Current conclusion

After this audit, the repository documentation states that:

- GPT version is independently operable;
- P0 Standalone and P1 Gateway are the primary acceptance path;
- P2 Adapter Mode is optional and low priority;
- P2 remote-control tests are boundary/regression tests only;
- P2 results must not replace P0/P1 acceptance.

## Remaining local validation

Local testers should now rerun or reclassify reports according to:

```text
online-gpt/PRIORITY-GUARDRAIL.md
online-gpt/LOCAL-TEST-PLAN.md
online-gpt/LOCAL-TEST-QUICKSTART.md
```
