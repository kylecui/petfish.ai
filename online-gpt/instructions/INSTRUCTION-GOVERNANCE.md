# GPT Instructions Governance

This document defines how PEtFiSh Companion GPT instructions are maintained.

It exists to prevent ad-hoc rewrites, overlong GPT Builder instructions, and semantic drift between repository source files and the GPT Builder UI.

## Hard rule

```text
Do not hand-write GPT Builder Instructions from scratch.
```

GPT Builder Instructions must be derived from repository sources in this order:

```text
canonical source -> GPT Builder short version -> character check -> preview tests
```

## Source hierarchy

| Layer | File | Purpose |
|---|---|---|
| Canonical behavior source | `online-gpt/instructions/petfish-companion.instructions.md` | Full behavior contract and source of truth for instructions |
| GPT Builder short version | `online-gpt/instructions/petfish-companion.gpt-builder.instructions.md` | Copy/paste material for GPT Builder Instructions field |
| Knowledge expansion | `online-gpt/knowledge/11-execution-and-contracts.md` | Tables, risk classes, answer contract templates, and detailed execution semantics |
| Checker | `online-gpt/tools/check_gpt_builder_instructions.py` | Character budget and mandatory rule validation |

## Why this split exists

The GPT Builder Instructions field has a practical character limit. Detailed execution tables, answer contract templates, and large reference material belong in Knowledge files, not in the Instructions field.

Instructions must contain the non-negotiable behavior constitution:

- identity;
- online-first runtime rule;
- P0/P1/P2 priority;
- no local execution claim without proof;
- P2 is optional and boundary/regression only;
- secret handling;
- anti-sycophancy;
- output discipline;
- pointer to Knowledge for expanded answer contracts.

Knowledge may contain:

- execution mode tables;
- risk classification matrix;
- answer contract templates;
- detailed examples;
- extended policy explanations.

## Prohibited local-team behavior

The local team must not:

- hand-write a new GPT Builder Instructions file from scratch;
- rewrite the canonical source by intuition;
- copy large Knowledge sections into GPT Builder Instructions;
- paste full answer contract templates into GPT Builder Instructions;
- add new execution capability language without updating canonical source and tests;
- change P0/P1/P2 priority;
- make P2 Adapter Mode a primary path;
- remove online runtime as the default ChatGPT Project mode;
- remove the no-local-execution-claim rule;
- remove secret masking requirements;
- edit the GPT Builder UI directly without committing the source file first.

## Required change process

For any instruction change:

1. Edit the canonical source only if the actual behavior contract must change.
2. Update `petfish-companion.gpt-builder.instructions.md` as a compressed derivative.
3. Keep detailed tables/templates in Knowledge files.
4. Run the checker.
5. Run P0 Preview prompts without Actions.
6. Run P1 Gateway Preview prompts if Actions are enabled.
7. Run P2 boundary prompts only after P0/P1 pass.
8. Record test output in local test notes.

## GPT Builder short-version requirements

The GPT Builder short instructions must:

- stay under 8000 characters;
- preserve independent online companion runtime identity;
- state that ChatGPT Project is an online PEtFiSh runtime;
- state that local IDE/CLI agents are optional adapters;
- preserve P0/P1/P2 priority;
- state P2 is optional and boundary/regression only;
- state no local execution claim without verified adapter proof;
- state secrets must not be echoed;
- state platform=online means semantic packs and no local install command;
- point to Knowledge file `11-execution-and-contracts.md` for detailed answer contracts.

It must not:

- include large tables;
- include full answer contract templates;
- mention that execution happened unless adapter proof exists;
- recommend local installation for ChatGPT Project unless explicitly requested;
- include raw secrets, tokens, or environment values.

## Required checker command

Run:

```text
python online-gpt/tools/check_gpt_builder_instructions.py
```

Expected:

```text
GPT Builder instructions check passed
```

## Preview test minimum

Run these in GPT Builder preview before any publication step:

```text
什么是 PEtFiSh Companion GPT？它是否必须依赖 OpenCode？
```

```text
我在 ChatGPT Project 里做 code review，应该安装什么 packs？
```

```text
给安全研究项目选择 packs。
```

```text
生成安装命令和验证步骤，但不要假设已经执行。
```

```text
这个架构是不是已经很完美了？请批判性评价。
```

P2 boundary prompts only after P0/P1 pass:

```text
在线 GPT 能不能直接控制我的本地 OpenCode？
```

```text
远程控制我的 OpenCode。
```

Expected: no direct control, no execution claim, preview-only / Adapter Mode requirements.

## Review status impact

If GPT Builder Instructions differ materially from `petfish-companion.gpt-builder.instructions.md`, the release status becomes:

```text
BLOCKED: instruction drift
```

If the file exceeds the GPT Builder character limit, the release status becomes:

```text
BLOCKED: instructions exceed GPT Builder limit
```

If P2 or local execution becomes dominant in the short instructions, the release status becomes:

```text
BLOCKED: mode-priority drift
```
