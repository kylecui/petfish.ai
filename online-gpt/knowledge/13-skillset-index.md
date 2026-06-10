# PEtFiSh Skillset Index

This file is a master index of all PEtFiSh skills, organized by pack and category. Companion GPT uses this index to understand the full PEtFiSh capability landscape and route user intent to the correct pack and skill.

## Core Packs (4)

| Pack | Alias | Skills | Distribution |
|------|-------|--------|-------------|
| petfish-companion-skill | `companion` | fish-brain, fish-market | petfish.ai (core) |
| fish-trail | `context` | fish-trail | petfish.ai (core) |
| petfish-toolchain-skill | `toolchain` | skill-author, skill-lint, skill-security-auditor, quality-gate, skill-publish, skill-description-optimizer, skill-trigger-evaluator, repo-skill-miner, skill-usage-tracker | petfish.ai (core) |
| project-initializer-skill | `init` | project-initializer | petfish.ai (core) |

## Optional Packs (8)

| Pack | Alias | Skills | Distribution |
|------|-------|--------|-------------|
| petfish-style-skill | `petfish` | petfish-style-rewriter | petfish-market |
| anti-sycophancy-calibration-pack | `calibrate` | anti-sycophancy-calibration | petfish-market |
| trustskills-governance-pack | `trust` | skill-trust-governance | petfish-market |
| fish-reflection-pack | `reflect` | fish-reflection | petfish-market |
| opencode-course-skills-pack | `course` | 15 course development skills | petfish-market |
| opencode-ppt-skills | `ppt` | ppt-reader, ppt-writer | petfish-market |
| opencode-skill-pack-testcases-usage-docs | `testdocs` | generate-test-cases, generate-usage-docs | petfish-market |
| repo-deploy-ops-skill-pack | `deploy` | 6 deployment + ops skills | petfish-market |
| research-skill-pack | `research` | 13 research pipeline skills | petfish-market |

## Skills by Category

### Companion Gateway (always-on orchestration)

| Skill | Pack | Role |
|-------|------|------|
| fish-brain | companion | Runs Gateway Steps 0-6. Tier 0/1/2 sensing. 15+ /petfish commands. |
| anti-sycophancy-calibration | calibrate | Proactive activation in Step 2.5 (evaluation questions) |
| fish-trail | context | Topic context check via plugin injection |

### Toolchain (skill lifecycle)

| Skill | Role |
|-------|------|
| skill-author | Scaffold new skills, improve existing ones |
| skill-lint | Structural and quality validation |
| skill-security-auditor | Security risk audit (0.0-1.0 score) |
| quality-gate | Release gate: lint → security → metadata → PASS/CONDITIONAL/FAIL |
| skill-publish | Bridge gate PASS → petfish-market availability |
| skill-description-optimizer | Optimize trigger descriptions |
| skill-trigger-evaluator | Test trigger accuracy with query sets |
| repo-skill-miner | Mine reusable workflows from repos |
| skill-usage-tracker | Track activation events and usage |

### Writing & Review

| Skill | Pack | Role |
|-------|------|------|
| petfish-style-rewriter | petfish | Rewrite text in PEtFiSh style. 5 modes. AI-slop detection. |
| anti-sycophancy-calibration | calibrate | Reduce sycophantic agreement in judgment tasks |

### Topic & Context

| Skill | Pack | Role |
|-------|------|------|
| fish-trail | context | Topic governance, 5-dimension contamination scoring, 7 relationship types |

### Governance & Trust

| Skill | Pack | Role |
|-------|------|------|
| skill-trust-governance | trust | Governance classification for skills (5-level scale) |

### Learning & Reflection

| Skill | Pack | Role |
|-------|------|------|
| fish-reflection | reflect | 3-level reflection model (L1/L2/L3), converts failures into prevention rules |

### Discovery

| Skill | Pack | Role |
|-------|------|------|
| fish-market | companion | Cross-source skill/MCP discovery across 7 sources |

### Domain Packs (detailed in separate Knowledge files)

| Pack | Domain |
|------|--------|
| course | Course development: 15 skills (orchestrator, outline, content, lab, QA, QC, methodology, diagrams, etc.) |
| ppt | Presentation: ppt-reader, ppt-writer |
| testdocs | Test cases + usage documentation |
| deploy | Deployment + operations: 6 skills (discovery, readiness, executor, verifier, lifecycle, incident-rollback) |
| research | Research pipeline: 13 skills (router, brief, source, note, evidence, synthesis, report, quality-review, etc.) |

## Skill Selection Guide

When a user asks about a PEtFiSh capability, use this guide to recommend the correct pack:

| User says | Recommended pack(s) |
|-----------|-------------------|
| "我需要部署" / "deploy" | `deploy` |
| "设计课程" / "course" | `course` |
| "做 PPT" / "slides" | `ppt` |
| "写测试用例" / "test cases" | `testdocs` |
| "润色文字" / "去AI味" / "说人话" | `petfish` |
| "评审一下" / "review" / "批判" | `calibrate` |
| "整理话题" / "上下文污染了" | `context` |
| "研究 / 调研 / 文献" | `research` |
| "复盘" / "反思" / "lessons learned" | `reflect` |
| "安全审计" / "信任检查" | `trust` |
| "创建 skill" / "发布 skill" | `toolchain` |
| "搜索 skill" / "找 MCP" | `companion` (fish-market) |
