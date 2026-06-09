# Classic Fish-* Skillset

This file describes the classic PEtFiSh fish-* skills — the standalone skills organized by domain. Companion GPT uses this Knowledge to explain what each skill does, when to recommend it, and how to route user intent.

---

## 1. fish-trail — Topic & Context Governance

**Pack**: `context` (core)

Manages topic continuity and context isolation. Prevents cross-topic contamination in long or multi-topic sessions.

### Contamination Model

5 dimensions: topic_distance, goal_conflict, term_overloading, output_format_divergence, history_bias.

### Relationship Types

| Type | Risk | Action |
|------|------|--------|
| continue | Low | Silent, inherit full context |
| fork | Medium | Inherit partial, create child topic |
| switch | Medium | Load target topic context |
| merge | High | Prompt user to confirm |
| archive | High | Freeze topic, close session |
| reset | High | Clear context, fresh start |
| bridge | High | Cross-reference only shared parts |

### MCP Server

20+ tools: topic_create/list/show/update/archive/search/link/unlink/graph, topic_detect, contamination_score/explain, context_build/bridge/export/freeze, decision_log/history, session_bind/get/list/resume/close/timeline/query/agents, topic_route/report/validate/recommend.

**Triggers**: 整理话题, 切换话题, 合并话题, 上下文污染, 清空上下文, topic governance

---

## 2. petfish-style-rewriter (fish-style) — Writing Style

**Pack**: `petfish` (optional)

Rewrites Chinese or English text into the PEtFiSh writing style: structured, problem-driven, concise, evidence-based, engineering-oriented.

### Style Rules

- Problem-modeling structure (not slogan-writing)
- Compact Chinese-English spacing: `Webhook挂载` not `Webhook 挂载`
- AI-slop detection: bans 赋能/普惠/拔高/民主化/银弹/delve/nuanced/robust/seamless/leverage/transformative
- 5-point "说人话" self-score per paragraph
- 5 modes: strict/normal/light/academic/email

**Triggers**: 润色, 说人话, 去AI味, 用我的语言习惯表达, 按我的风格写, "make it sound human but still professional"

---

## 3. anti-sycophancy-calibration (fish-calibrate) — Critical Review

**Pack**: `calibrate` (optional)

Reduces sycophantic agreement in judgment tasks. Separates what the user hopes is true from what evidence supports.

### Review Workflow

1. Detect leading input
2. State evaluation frame (rubric first)
3. Score and contrast (supporting vs opposing)
4. Separate conclusion from confidence

### Evidence Ladder

| Level | Type | Supports conclusion? |
|-------|------|:--:|
| 1 | Observable fact | ✅ |
| 2 | Sound inference from multiple facts | ✅ (with reasoning) |
| 3 | Speculative (single source, unverified) | ⚠️ (as uncertainty) |
| 4 | Unfounded guess | ❌ |

### Output Structure

```
Conclusion → Evaluation Frame → Scorecard →
Supporting Reasons → Opposing/Alternative Reasons →
Confidence Level (High/Medium/Low + what changes it)
```

**Triggers**: 评审, 评价, 批判, review, critique, "这个好吗?", "这样做对吗?", "is this approach right?", 可行性分析, architecture evaluation

---

## 4. skill-trust-governance (fish-guard) — Skill Safety

**Pack**: `trust` (optional)

Governance classification for PEtFiSh skills. Scans skills and assigns a 5-level governance rating.

### Governance Levels

| Level | Meaning |
|-------|---------|
| allow | Trusted, no restrictions |
| allow_with_ask | Confirm before sensitive actions |
| sandbox_required | Isolated environment only |
| manual_review_required | Block until human review |
| deny | Must not load or execute |

**Triggers**: 治理, 可信度, skill安全, trust scan, risk score, "check if safe to install"

---

## 5. fish-reflection — Experience Learning

**Pack**: `reflect` (optional)

Converts failures, corrections, and experience into reusable prevention rules.

### 3-Level Model

| Level | Trigger | Output |
|-------|---------|--------|
| L1 | Instant (user correction or failure) | 3-5 line inline reflection |
| L2 | Task debrief (L1 accumulated) | `.opencode/reflections/` file |
| L3 | Cross-project (recurring patterns) | `.opencode/reflections/guidance/` file |

### Reflection Card (4 fields)

trigger → root_cause → prevention_rule → scope (file/project/universal)

### Trigger Conditions (only these 3)

- T1: User corrects agent output → inline L1 after fix
- T2: Same operation fails 2+ times → pause, L1, then continue
- T3: Explicit request → L1/L2/L3 based on scale

### Anti-Triggers (NOT triggered by)

- First-time debugging
- Simple typo/format fixes
- Requirement changes
- External failures (network timeout)

**Triggers**: 反思, 复盘, 经验总结, 失败分析, 返工原因, 教训, "reflect", "lessons learned", "root cause analysis", "postmortem"

---

## 6. Domain Pack Skills

The following packs contain specialized domain skills. For detailed skill-level descriptions, see `knowledge/13-skillset-index.md`.

### course (15 skills)

Course development pipeline: orchestrator, outline design, content authoring, lab design, directory structure, QA, QC reporting, methodology playbook, plan governance, learner materials, instructor materials, markdown writing, document review, draw.io diagrams.

**Triggers**: 课程, 教学, 大纲, 实验, courseware, syllabus

### ppt (2 skills)

ppt-reader: Read/inspect/audit PPT/PPTX files.
ppt-writer: Create/rewrite/validate PPT/PPTX decks.

**Triggers**: PPT, 幻灯片, presentation, 课件, 提案

### testdocs (2 skills)

generate-test-cases: API/CLI/UI/SDK test matrix, coverage gap analysis.
generate-usage-docs: README, quick start, API docs, troubleshooting.

**Triggers**: 测试用例, test case, usage doc, 文档生成

### deploy (6 skills)

deployment-executor, deployment-verifier, repo-runtime-discovery, target-host-readiness, repo-service-lifecycle, service-operations, incident-rollback.

Pipeline: discovery → readiness → executor → verifier → operations → incident-rollback.

**Triggers**: 部署, deploy, Docker, CI/CD, 运维, rollback

### research (13 skills)

Research pipeline: router → brief-framer → source-discovery → literature-access → note-capture → insight-log → evidence-ledger → synthesis → report-writer → quality-reviewer → citation-auditor; plus scientific: literature-review, gap-finder, methodology-designer, experiment-planner, paper-writer, review-rebuttal.

**Triggers**: 研究, research, 调研, 文献综述, literature review, 论文, paper

---

## 7. Cross-Pack Skills

The following skills span multiple domains and are available as standalone capabilities:

### Decision Skills

- decision-brief-framer: Structure decision problems
- decision-criteria-builder: Build weighted criteria
- option-comparison-matrix: Compare options side by side
- decision-recommendation: Final recommendation with conditions

### Product Skills

- product-competitor-analysis: Competitor discovery and SWOT
- product-user-research: User research design
- product-opportunity-mapper: JTBD-based opportunity mapping
- product-validation-planner: MVP and validation planning

### Risk & Compliance Skills

- risk-research-brief: Tool/vendor risk assessment
- vendor-source-diligence: Vendor due diligence
- security-risk-review: Security risk assessment
- compliance-check: Compliance risk research
- tco-operational-risk: TCO and operational risk

### Planning & Learning Skills

- planning-environment-scanner: PESTLE, trend analysis
- planning-roadmap-developer: Strategic roadmap
- learning-goal-framer: Structure learning objectives
- learning-path-designer: Phased learning path
