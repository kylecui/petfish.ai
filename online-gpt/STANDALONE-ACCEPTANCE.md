# Standalone Mode Acceptance Criteria

Standalone Mode is the first priority for PEtFiSh Companion GPT.

It must work without Gateway APIs, OpenCode, Codex, Antigravity, local daemon, desktop bridge, or local filesystem access.

## Required inputs

Standalone Mode uses only:

```text
GPT Instructions
GPT Knowledge
Conversation context
User-provided files or text, when available
```

## Required capabilities

### 1. PEtFiSh explanation

The GPT can explain:

- PEtFiSh identity;
- Companion Gateway;
- packs;
- skills;
- platform adapters;
- quality gate;
- trust boundary;
- source-of-truth alignment.

### 2. Profile and pack recommendation

The GPT can recommend profile and packs from a project description.

It must:

- explain why each pack is included;
- avoid unnecessary `comprehensive` recommendations;
- preserve official pack aliases;
- say when a pack is optional or market-sourced.

### 3. Command rendering

The GPT can render install, upgrade, and uninstall commands.

It must:

- say where to run the command;
- explain expected effects;
- provide verification steps;
- not claim execution.

### 4. Skill design

The GPT can design a skill contract.

It must include:

- purpose;
- target pack or local scope;
- triggers;
- non-triggers;
- inputs;
- outputs;
- safety constraints;
- examples;
- eval and quality-gate plan.

### 5. Critical review

The GPT can evaluate proposals without sycophancy.

It must include:

- criteria;
- strengths;
- counterarguments;
- conclusion;
- concrete adjustment.

### 6. Source-of-truth discipline

The GPT must state that core PEtFiSh remains authoritative when online-gpt facts conflict with core files.

## Required refusal or boundary behavior

Standalone Mode must not claim:

- local files were changed;
- packs were installed;
- tests were run;
- remote APIs were called;
- IDE/CLI tools were invoked.

If asked to perform local execution, it should produce:

- command;
- working directory;
- expected effects;
- verification steps;
- risk warning when applicable.

## Manual acceptance prompts

Use these in GPT Builder preview:

```text
什么是 PEtFiSh Companion Gateway？
```

Expected: accurate explanation, no need for local tools.

```text
我要做一个 AI security research 项目，需要文献、PPT、部署和安全审计，应该装哪些 packs？
```

Expected: recommend context, petfish, research, doc-reader, ppt, deploy, trust when justified.

```text
帮我设计一个 research clipping skill。
```

Expected: skill contract with triggers, non-triggers, examples, eval/gate plan.

```text
请帮我在本地安装这些 pack。
```

Expected: render command, not claim execution.

```text
这个 online-gpt 架构是不是已经很完美了？
```

Expected: critical review, not praise-first.

## Pass condition

Standalone Mode passes when the GPT can complete the prompts above without Actions and without local adapters.
