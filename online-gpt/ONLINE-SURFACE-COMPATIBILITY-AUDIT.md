# Online GPT Surface Compatibility Audit

**Date**: 2026-06-09 | **Branch**: `dev` | **Status**: Audit

This document audits all PEtFiSh Companion GPT output surfaces and defines the correct output format for each.

---

## 1. Surface Taxonomy

PEtFiSh Companion GPT serves five distinct output surfaces. Each surface requires a different output format.

| Surface | Consumer | Correct Output | Wrong Output |
|---|---|---|---|
| **ChatGPT Project** | Human user in a ChatGPT Project | Project Instructions (natural language) | YAML, JSON, install commands |
| **GPT Builder** | GPT Builder UI operator | Configuration steps + file references | Project YAML, local install configurations |
| **Gateway Actions** | GPT Actions runtime | JSON envelope (`ModuleEnvelope`) | Human-friendly prose, configuration docs |
| **Local IDE/CLI project** | User with local agent installed | Install commands, YAML config, file tree, verification steps | ChatGPT Project instructions |
| **Skill Authoring** | User designing a PEtFiSh skill | SKILL.md draft, trigger list, eval/gate plan | Generic advice without contract |

### The Surface-First Rule

> Every output must first determine its target surface, then select the correct format.

Wrong surface outputs degrade trust:
- YAML in a ChatGPT Project → user cannot use it directly
- Install commands in a ChatGPT Project → user has no local agent to run them
- Human prose in Gateway Actions → GPT cannot parse it
- ChatGPT Project instructions to a local user → they need install commands, not conversation prompts

---

## 2. Surface Output Contracts

### 2.1 ChatGPT Project → Project Instructions

When the user is in a ChatGPT Project:

**Must output**:
- Natural language Project Instructions that can be pasted into ChatGPT Project settings
- Semantic pack references (explain what each pack provides, not how to install)
- Review discipline and output templates

**Must NOT output**:
- YAML configuration blocks (they belong in profile files, not Project Instructions)
- Install commands (`uv run install.py...`)
- Platform adapter instructions that assume local filesystem
- Claims of local execution

**Example — correct**:
```
# PEtFiSh Online Code Review Project Instructions

This is an online PEtFiSh code review project.
Do not assume access to a local repository, IDE, CLI, filesystem, git history,
CI logs, or runtime unless the user uploads or pastes them.

## Enabled semantic packs
- companion: run Companion Gateway before substantive review work
- context: isolate PRs, modules, and review threads
- petfish: keep review writing precise and actionable
- testdocs: reason about tests, coverage, and acceptance cases
- trust: classify risky changes and policy boundaries

## Review discipline
For every review:
1. State the verdict.
2. Separate blocking and non-blocking issues.
3. ...
```

**Example — wrong**:
```yaml
# Do NOT output this in a ChatGPT Project
profile: review-online
packs:
  core:
    - companion
    - context
  optional:
    - deploy
```

### 2.2 GPT Builder → Configuration Steps

When assisting with GPT Builder setup:

**Must output**:
- Step-by-step configuration instructions
- File paths to copy from
- Checker validation commands

**Must NOT output**:
- Raw YAML configuration that should go in Instructions/Knowledge
- Project-specific instructions
- Local install commands

### 2.3 Gateway Actions → JSON Envelope

When GPT uses Actions to call online Gateway endpoints:

**Must output**:
- `ModuleEnvelope` JSON

**Must NOT output**:
- Human-friendly prose in place of structured JSON
- Configuration instructions embedded in API responses

### 2.4 Local IDE/CLI Project → Install Commands + YAML

When the user explicitly asks for local setup:

**Must output**:
- Install commands with `--platform <platform>`
- YAML profile/pack configuration
- File tree and expected paths
- Verification commands

**Must NOT output**:
- ChatGPT Project instructions as default for local users
- `platform=online` when user has a local IDE

### 2.5 Skill Authoring → SKILL.md + Gate Plan

When designing a PEtFiSh skill:

**Must output**:
- SKILL.md draft with triggers, non-triggers, boundaries
- Lint/audit/gate plan
- Eval cases

**Must NOT output**:
- Generic advice without contract
- Skill design without misuse examples

---

## 3. Online Runtime Specific Rules

### 3.1 platform=online means semantic references

When `platform=online`:
- Packs are semantic references, not install targets
- `install command` field = null / `operation: semantic_only`
- No local filesystem access assumed
- `execution_truth_default: advice_only`

### 3.2 ChatGPT Project ≠ Local IDE

```
ChatGPT Project != opencode
ChatGPT Project != codex
ChatGPT Project != claude
ChatGPT Project  = online PEtFiSh runtime
```

Do not suggest `--platform opencode` unless user explicitly asks for local setup.

### 3.3 YAML is source, not delivery for online

For online projects, YAML profiles exist as source/reference material. The user-facing delivery for ChatGPT Project is Project Instructions. When a user says "give me the config", in a ChatGPT Project context, translate YAML to natural language instructions.

---

## 4. Audit of Current Online-GPT Surfaces

### 4.1 Knowledge Files

| File | Surface | Status |
|------|---------|--------|
| `00-source-of-truth-note.md` | GPT Knowledge | ✅ Correct |
| `01-system-overview.md` | GPT Knowledge | ✅ Correct (has online project mode) |
| `02-companion-gateway.md` | GPT Knowledge | ⚠️  Local-first Mode Read — online section added in remediation |
| `03-pack-index.md` | GPT Knowledge | ✅ Correct (has review-online) |
| `04-platform-adapters.md` | GPT Knowledge | ✅ Correct (has ChatGPT Project row) |
| `05-install-command-reference.md` | GPT Knowledge | ✅ Correct (has online projects section) |
| `06-quality-gate-reference.md` | GPT Knowledge | ✅ Correct |
| `08-failure-playbook.md` | GPT Knowledge | ✅ Correct |
| `09-skill-workbench-reference.md` | GPT Knowledge | ✅ Correct |
| `10-trust-gate-reference.md` | GPT Knowledge | ✅ Correct |
| `11-execution-and-contracts.md` | GPT Knowledge | ✅ Correct |
| *(missing)* | GPT Knowledge | ❌ No companion skillset reference |
| *(missing)* | GPT Knowledge | ❌ No fish-* classic skillset reference |
| *(missing)* | GPT Knowledge | ❌ No surface output contracts |

### 4.2 Instructions

| Source | Status |
|--------|--------|
| `petfish-companion.gpt-builder.instructions.md` | ✅ Contains online runtime rule, platform=online rule |
| `petfish-companion.instructions.md` | ✅ Canonical source correct |

### 4.3 Gateway Modules

| Module | Output | Surface Match |
|--------|--------|:--:|
| `router.py` | ModuleEnvelope | ✅ Gateway |
| `profiler.py` | ModuleEnvelope (review-online / generic) | ✅ Gateway |
| `installer.py` | ModuleEnvelope (command_rendered / semantic_only) | ✅ Gateway |
| `trust_gate.py` | ModuleEnvelope (risk classification) | ✅ Gateway |

### 4.4 Project Instructions

| File | Surface | Status |
|------|---------|--------|
| `project-instructions/code-review.md` | ChatGPT Project | ✅ Correct |

---

## 5. Gaps Identified

### Gap 1: Surface Output Contracts

No explicit rule tells the GPT which output format to use for which surface. The GPT should self-check: "What surface is the user on?" before formatting output.

**Fix**: Create `knowledge/12-surface-output-contracts.md`.

### Gap 2: Skillset Knowledge Coverage

The GPT knows the PEtFiSh framework structure but doesn't know what skills exist, what they do, or how to use them. This makes it a "framework with no skills body".

**Fix**: Create skillset Knowledge files (§6).

### Gap 3: YAML as Chat Output

The profiler and profile definitions use YAML internally. If the GPT relays YAML directly to a ChatGPT Project user, the output is wrong for that surface.

**Fix**: Add surface output contract rules; update profiler to include surface-appropriate formatting hints.

### Gap 4: Eval Coverage for Surface Discipline

No evals test that the GPT selects the correct output format for each surface.

**Fix**: Add surface compatibility eval cases.

---

## 6. Recommended Fixes

### Fix 1: Create `knowledge/12-surface-output-contracts.md`

Define the surface-first rule and per-surface output contracts.

### Fix 2: Create `knowledge/13-skillset-index.md`

A master index of all PEtFiSh skills, organized by pack and category.

### Fix 3: Create `knowledge/14-companion-skillset.md`

The companion/fish-* core skillset — Companion Gateway, Topic Governance, Style, Skill Authoring, Quality Gates.

### Fix 4: Create `knowledge/15-fish-classic-skillset.md`

The classic fish-* skills — research, course, ppt, deploy ops, testdocs, doc-reader, calibrate, trust governance, reflection.

### Fix 5: Update GPT Builder Documents

Add new Knowledge files to upload lists in RUNBOOK, CREATION-PLAN, PRODUCTION-READINESS-CHECKLIST.

### Fix 6: Add Surface Compatibility Eval Cases

```jsonl
{"id":"surface-chatgpt-no-yaml","input":"帮我的 ChatGPT Project 生成 review 配置","must_include":["Project Instructions","natural language"],"must_not_include":["yaml","```yaml"],"category":"surface-compat"}
{"id":"surface-local-yaml-ok","input":"给我一个本地 OpenCode 项目的 YAML 配置","must_include":["yaml","opencode"],"category":"surface-compat"}
{"id":"surface-online-no-install","input":"我在 ChatGPT Project 里，帮我安装 context pack","must_include":["semantic","不需要安装","advice_only"],"must_not_include":["uv run","install.py","--platform"],"category":"surface-compat"}
```

---

## 7. Acceptance Criteria

The surface compatibility audit is resolved when:

1. [ ] `knowledge/12-surface-output-contracts.md` exists and defines all 5 surfaces.
2. [ ] `knowledge/13-skillset-index.md` exists with complete skill catalog.
3. [ ] `knowledge/14-companion-skillset.md` exists.
4. [ ] `knowledge/15-fish-classic-skillset.md` exists.
5. [ ] GPT-BUILDER-RUNBOOK.md Knowledge list updated to include all new files.
6. [ ] GPT-CREATION-PLAN.md Knowledge list updated.
7. [ ] PRODUCTION-READINESS-CHECKLIST.md references updated.
8. [ ] LOCAL-TEST-PLAN.md includes surface compatibility test cases.
9. [ ] Surface compatibility eval cases exist.
10. [ ] No YAML is recommended as primary ChatGPT Project delivery.
11. [ ] No local install commands are rendered for platform=online.
