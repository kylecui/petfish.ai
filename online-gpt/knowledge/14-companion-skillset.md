# Companion Skillset: Gateway + Toolchain

This file describes the companion skillset — the always-on orchestration layer and the toolchain skills. These skills form the PEtFiSh operational backbone.

---

## 1. fish-brain — Companion Gateway

**Pack**: `companion` (core)
**Role**: Always-on orchestrator. Runs before every user message.

### Purpose

The Companion Gateway is not a user-facing skill. It's an automatic layer injected at the highest priority, ensuring every interaction follows PEtFiSh discipline.

### Gateway Steps (6 steps per round)

```
User message
  → Step 0: Mode Read (local .opencode/project-mode.yaml or online ChatGPT Project)
  → Step 1: Topic Check (topic_detect via context-state MCP or conversation heuristics)
  → Step 1.5: Failure Signal Detection (previous turn errors → pack recommendation)
  → Step 2: Skill Sense (capability gap detection)
  → Step 2.5: Anti-Sycophancy Check (evaluation questions)
  → Step 3: Proceed (normal processing)
```

### Three-Tier Sensing

| Tier | What it detects | Action |
|------|----------------|--------|
| T0 | Previous turn failure patterns (PDF, deploy, test, research, context) | Recommend matching pack |
| T1 | Keyword-triggered domain gaps (20+ domain→pack mappings) | Recommend pack if not installed |
| T2 | Unknown domain intent (email, charts, monitoring, APIs) | Search marketplace for skills/MCP |

### Domain → Pack Mappings (T1)

| User says | Pack needed |
|-----------|------------|
| 部署 / deploy / Docker / CI/CD / 回滚 | `deploy` |
| 课程 / 教学 / 大纲 / 实验 | `course` |
| PPT / 幻灯片 / presentation | `ppt` |
| 测试用例 / test case / usage doc | `testdocs` |
| 润色 / 说人话 / 去AI味 / 写作风格 | `petfish` |
| 评审 / 评价 / 批判 / review / calibration | `calibrate` |
| topic / 话题 / 上下文污染 / 隔离 | `context` |
| 研究 / 调研 / 文献 / evidence / 综述 | `research` |

### /petfish Commands (15+)

| Command | Action |
|---------|--------|
| `/petfish` | Status of installed packs |
| `/petfish catalog` | Browse all packs |
| `/petfish suggest` | Recommend packs for project |
| `/petfish install <alias>` | Show install command |
| `/petfish search <keyword>` | Cross-marketplace search |
| `/petfish create <name>` | Create new skill |
| `/petfish lint [path]` | Validate skill quality |
| `/petfish audit <path>` | Security audit skill |
| `/petfish gate <path>` | Run quality gate (lint+security) |
| `/petfish publish <path>` | Publish skill to market |
| `/petfish optimize <path>` | Optimize skill description |
| `/petfish eval <path>` | Test trigger accuracy |
| `/petfish stats` | View usage statistics |
| `/petfish upgrade` | Check for updates |
| `/petfish uninstall` | Uninstall pack |

---

## 2. fish-market — Marketplace Connector

**Pack**: `companion` (core)
**Role**: Cross-source discovery for skills and MCP servers.

### Purpose

Search for PEtFiSh skills and MCP servers across 7 sources. Invoked when fish-brain T2 detects an unknown capability gap, or when the user explicitly asks to find a skill or MCP server.

### Search Sources (priority order)

1. PEtFiSh official packs (petfish.ai)
2. PEtFiSh Market (community registry)
3. Glama (MCP server registry)
4. Smithery (MCP server registry)
5. SkillKit (skill registry)
6. anthropics/skills (official Claude skill examples)
7. GitHub search (fallback)

### Triggers

- `/petfish search <keyword>`
- "找 skill" / "find a skill for..."
- "有没有可以...的 skill？"
- "MCP server for..."
- "search marketplace"

---

## 3. Toolchain Skills

**Pack**: `toolchain` (core)
**Role**: Skill lifecycle management — create, validate, audit, gate, publish.

### Toolchain Pipeline

```
repo-skill-miner → skill-author → skill-lint → skill-security-auditor
    → quality-gate → skill-publish → skill-description-optimizer
    → skill-trigger-evaluator ←→ skill-usage-tracker
```

### skill-author

Creates new PEtFiSh skills from scratch. Supports 8 skill types: automation, workflow, knowledge, writing, review, research, project, hybrid.

**Triggers**: "create a skill", "generate skill", "new skill", "skill for X"

### skill-lint

Validates skill quality: frontmatter checks, body guidance, script safety, trigger coverage. Outputs score/100 and ERROR/WARN/INFO severities.

**Triggers**: "lint skill", "check skill", "validate skill"

### skill-security-auditor

Security-only risk audit. Scans for prompt injection, secret access, dangerous commands, remote execution. Returns 0.0-1.0 risk score.

**Triggers**: "audit skill security", "check skill safety", "security review"

### quality-gate

Pre-publish release gate. Runs 3-stage pipeline: lint → security → metadata → PASS/CONDITIONAL/FAIL decision.

**Pass criteria**: lint ≥80, risk ≤0.3, 0 CRITICAL/HIGH
**Conditional**: lint ≥80, risk 0.3-0.5, HIGH but no CRITICAL
**Fail**: lint <80, risk >0.5, has CRITICAL

**Triggers**: "publish skill", "run quality gate", "check before publish"

### skill-publish

Bridges quality-gate PASS to petfish-market availability. Generates registry JSON, updates index.json.

**Triggers**: "publish skill", "release to market", "发布到市场"

### skill-description-optimizer

Improves frontmatter description precision for better trigger matching.

**Triggers**: "optimize description", "improve trigger", "description too broad"

### skill-trigger-evaluator

Tests trigger accuracy with positive/negative query sets. Reports pass rate, false positive/negative rates.

**Triggers**: "evaluate triggers", "test skill trigger", "trigger accuracy"

### repo-skill-miner

Inspects GitHub/local repos for reusable workflows to convert into skills.

**Triggers**: "analyze this repo for skills", "mine skills from...", "skillize this repo"

### skill-usage-tracker

Tracks skill activation events, session coverage, and user feedback. Identifies high-value vs dormant skills. Local only.

**Triggers**: "usage stats", "which skills are popular", "skill analytics"
