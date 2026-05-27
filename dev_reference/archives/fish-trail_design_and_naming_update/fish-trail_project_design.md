# fish-trail 项目设计与开发方案

> fish-trail 是胖鱼（PEtFiSh）体系中的话题轨迹管理器。  
> 它借鉴 Graphify 的“先索引后回源、图谱化导航、增量更新、证据分级”思想，但管理对象不是项目文件，而是长期对话、项目目标、历史决策、任务状态、产物文件和 skills 关系。

---

## 0. 一句话定位

**Graphify 解决“项目文件太多，Agent 不该每次重读”；fish-trail 解决“历史话题太多，Agent 不该每次混读”。**

fish-trail 的目标不是替代 memory，也不是简单 summary，而是为 AI Agent 提供一个：

- 可查询的 topic graph；
- 可裁剪的 active context；
- 可更新的 topic card；
- 可审计的 evidence chain；
- 可执行的 context firewall。

最终目标是让胖鱼不仅能“安装 skills”，还能长期维护一个 AI-agent 友好的项目协作环境。

---

## 1. 背景与问题

在长期 AI 协作中，我们经常遇到以下问题。

### 1.1 话题污染

不同项目、不同阶段、不同目标的上下文经常混在一起，例如：

```text
rSwitch 论文
胖鱼 skills 开发
AI 安全课程
OpenClash 配置
CSA 人才体系
比赛安排
```

这些内容都可能存在历史对话中，但多数任务只需要其中很小一部分。如果 Agent 误加载不相关上下文，就会产生“看似聪明但方向错误”的回答。

### 1.2 上下文重复消耗

同一项目会反复讨论，每次新任务都要重新解释：

```text
我们之前怎么决定的？
这个方案为什么放弃？
当前版本和上个版本差异是什么？
哪些内容不要再混进来？
```

普通 summary 可以缓解一部分问题，但不能稳定回答“该加载什么、不该加载什么”。

### 1.3 决策漂移

长期讨论中，经常出现：

```text
旧方案被新方案替代
某个名字被重新定义
某个方向被明确放弃
某个 topic 被拆成两个 topic
```

如果没有结构化记录，Agent 会把旧结论、新结论、临时想法混在一起。

---

## 2. 项目目标

fish-trail 的目标是构建一套面向 AI Agent 长期协作的 topic 管理系统。

### 2.1 核心目标

1. 将长期对话、项目材料、决策记录、任务状态和 skills 关系组织成 topic graph。
2. 在每次任务开始前，为 Agent 生成最小必要上下文。
3. 显式区分必须加载、可以加载和禁止混入的上下文。
4. 对 topic 关系、决策来源和上下文裁剪过程进行证据分级。
5. 支持 topic 的增量更新、拆分、合并、废弃和交接。
6. 与胖鱼的 `/initproject`、`/petfish`、`context-router` 等能力集成。

### 2.2 非目标

fish-trail 第一阶段不做以下事情：

- 不做完整知识图谱数据库；
- 不依赖 Neo4j、向量数据库或复杂 MCP 服务；
- 不替代项目文件索引工具；
- 不把所有历史对话原文写入项目；
- 不将 topic graph 作为最终事实来源；
- 不自动合并或删除 topic，除非用户确认。

---

## 3. 产品定位

### 3.1 产品名称

```text
fish-trail
```

中文可称：

```text
鱼迹
胖鱼话题轨迹
胖鱼话题治理器
```

建议正式名称：

```text
fish-trail: Topic Graph and Context Routing Pack for PEtFiSh
```

### 3.2 中文描述

fish-trail 是胖鱼的话题轨迹管理器。它将长期对话、项目材料、决策记录、任务状态和 skills 关系组织成 topic graph，在每次任务开始前为 Agent 生成最小必要上下文，降低话题污染和重复上下文消耗。

### 3.3 英文描述

fish-trail is a topic graph and context routing pack for PEtFiSh. It organizes long-running conversations, project artifacts, decisions, tasks, and skills into a navigable topic graph, then generates minimal active context for AI agents before each task.

---

## 4. 在胖鱼体系中的位置

fish-trail 是胖鱼体系中的一个核心 pack，而不是独立孤立工具。

```text
PEtFiSh / SKILL_builder
├── initproject        # 初始化项目
├── petfish            # skill 生命周期管理
├── context-router     # 运行时上下文路由
├── fish-trail         # 话题轨迹管理
├── skill-security     # skill 安全审计
├── skill-eval         # skill 评测
└── project packs      # course/code/deploy/ppt 等
```

### 4.1 与 `/initproject` 的关系

```text
/initproject
  ↓
创建项目
  ↓
安装 fish-trail
  ↓
生成初始 topic graph
  ↓
Agent 后续任务先经过 fish-trail 路由
```

### 4.2 与 `/petfish` 的关系

```text
/petfish suggest
  ↓
读取当前 topic
  ↓
推荐相关 skills

/petfish gate
  ↓
校验 topic graph
  ↓
检查上下文污染风险
  ↓
检查 stale topics
```

### 4.3 与 `context-router` 的关系

建议边界如下：

```text
fish-trail:
  维护 topic graph、topic card、decision log、上下文防火墙规则

context-router:
  在任务执行时调用 fish-trail，决定当前 Agent 应读取哪些上下文
```

换句话说：

```text
fish-trail 是状态层
context-router 是运行时路由器
```

---

## 5. 设计原则

### 5.1 先索引，后回源

Agent 不应默认读取全部历史对话或全部项目文件。

默认流程应为：

```text
用户请求
  ↓
fish-trail 识别 topic
  ↓
读取 topic card 和 topic graph
  ↓
生成 active context
  ↓
Agent 只在需要事实验证时回源
```

### 5.2 topic 不是标签，而是上下文对象

一个 topic 至少包含：

```text
标题
一句话定位
当前结论
已确认决策
相关产物
相关 skills
相关 topic
不应混入的 topic
待解决问题
证据来源
新鲜度
```

### 5.3 事实、推断、建议必须分层

fish-trail 必须区分：

```text
用户明确说过的
文件或代码直接显示的
Agent 推断出来的
Agent 建议新增的
不确定需要确认的
已经废弃的
```

这是避免“AI 脑补 topic 关系”的核心。

### 5.4 增量更新优先

不要每次重建全部 topic graph。

每轮任务结束，只做：

```text
新增事实抽取
新增决策抽取
topic 关系更新
active_context 更新
staleness 标记
```

### 5.5 上下文防火墙

fish-trail 不只是告诉 Agent“加载什么”，还要告诉 Agent“不该加载什么”。

```yaml
must_load:
  - 当前 topic card
  - 当前 topic 决策

may_load:
  - 相邻 topic 摘要

must_not_load:
  - 无关 topic
  - 已废弃决策
  - 过期 summary
```

---

## 6. 核心产物

fish-trail 应在项目中生成一组持久化文件。

### 6.1 项目内状态目录

```text
.petfish/
└── fish-trail/
    ├── topic_graph.json
    ├── TOPIC_REPORT.md
    ├── active_context.md
    ├── topic_cards/
    │   ├── petfish.md
    │   ├── graphify-borrowing.md
    │   ├── fish-trail.md
    │   └── rswitch-paper.md
    ├── decisions/
    │   ├── decision_log.md
    │   └── decision_index.json
    ├── evidence/
    │   ├── evidence_index.json
    │   └── sources.json
    ├── routes/
    │   ├── last_route.json
    │   └── route_history.jsonl
    ├── reports/
    │   ├── topic_health.md
    │   ├── context_pollution_report.md
    │   └── stale_topics.md
    ├── cache/
    │   └── source_hashes.json
    └── config.yaml
```

### 6.2 建议提交到 Git 的文件

```text
.petfish/fish-trail/topic_graph.json
.petfish/fish-trail/TOPIC_REPORT.md
.petfish/fish-trail/topic_cards/
.petfish/fish-trail/decisions/
.petfish/fish-trail/config.yaml
```

### 6.3 建议加入 `.gitignore` 的文件

```text
.petfish/fish-trail/cache/
.petfish/fish-trail/routes/route_history.jsonl
.petfish/fish-trail/active_context.md
```

`active_context.md` 是运行时产物，不应成为长期事实来源。

---

## 7. 数据模型设计

### 7.1 Topic Node

```json
{
  "id": "topic-fish-trail",
  "type": "topic",
  "title": "fish-trail 话题轨迹管理器",
  "summary": "借鉴 Graphify 的图谱化索引思想，为胖鱼构建跨会话 topic graph 和上下文路由层。",
  "status": "active",
  "priority": "high",
  "intent": ["design", "implement", "integrate"],
  "keywords": [
    "fish-trail",
    "topic graph",
    "context routing",
    "context firewall",
    "PEtFiSh",
    "Graphify"
  ],
  "related_skills": ["context-router", "petfish", "skill-eval"],
  "related_artifacts": [
    ".petfish/fish-trail/TOPIC_REPORT.md",
    ".opencode/skills/fish-trail/SKILL.md"
  ],
  "evidence_level": "extracted",
  "confidence": 0.95,
  "freshness": {
    "status": "fresh",
    "last_updated": "2026-05-05",
    "source_hash": "sha256:..."
  },
  "open_questions": [
    "fish-trail 是否独立于 context-router 发布？",
    "是否需要 HTML topic map？",
    "是否接入 Graphify 作为文件索引后端？"
  ]
}
```

### 7.2 Relation Edge

```json
{
  "id": "edge-fish-trail-inspired-by-graphify",
  "source": "topic-fish-trail",
  "target": "topic-graphify-borrowing",
  "relation": "inspired_by",
  "summary": "fish-trail 借鉴 Graphify 的先索引后回源、图谱化导航、证据分级和增量更新机制。",
  "evidence_level": "extracted",
  "confidence": 0.95,
  "evidence": [
    {
      "type": "conversation",
      "quote": "我更想在我们的 topic 管理借鉴 Graphify",
      "source_id": "conversation-2026-05-05"
    }
  ],
  "created_at": "2026-05-05",
  "updated_at": "2026-05-05"
}
```

### 7.3 Evidence Level

```yaml
evidence_levels:
  extracted:
    meaning: 来自用户原话、源文件、commit、issue 或明确产物
    default_confidence: 0.90

  inferred:
    meaning: 基于上下文合理推断，但用户没有直接说
    default_confidence: 0.65

  ambiguous:
    meaning: 可能相关，但证据不足，需要用户确认
    default_confidence: 0.40

  proposed:
    meaning: Agent 建议新增、拆分、合并或关联
    default_confidence: 0.50

  deprecated:
    meaning: 曾经成立，但已被新决策替代
    default_confidence: 0.30
```

### 7.4 Relation Types

```yaml
relation_types:
  refines: A 细化 B
  depends_on: A 依赖 B
  inspired_by: A 借鉴 B
  supersedes: A 替代 B
  conflicts_with: A 与 B 冲突
  related_to: A 与 B 一般相关
  produces: A 产出 B
  uses_skill: A 使用某 skill
  belongs_to_project: A 属于某项目
  should_not_mix_with: A 不应与 B 默认混入同一上下文
  evidence_for: A 是 B 的证据
```

其中最重要的是：

```text
should_not_mix_with
```

这是 fish-trail 区别于普通知识图谱的地方。

---

## 8. Topic Card 模板

每个 topic 应生成一张 Markdown 卡片。

```markdown
---
topic_id: topic-fish-trail
title: fish-trail 话题轨迹管理器
status: active
priority: high
last_updated: 2026-05-05
evidence_level: extracted
---

# fish-trail 话题轨迹管理器

## 一句话定位

fish-trail 是胖鱼的话题轨迹管理器，用 topic graph 维护长期对话、项目材料、决策记录和 skills 关系，并为 Agent 生成最小必要上下文。

## 当前结论

- fish-trail 应作为胖鱼的独立 pack 实现。
- 它应借鉴 Graphify 的“先索引后回源”机制，但管理对象是 topic 而不是文件。
- 它必须支持证据分级、增量更新和上下文防火墙。
- 它不应替代源材料，只负责导航、路由和上下文裁剪。

## 已确认决策

| 决策 | 证据等级 | 日期 | 来源 |
|---|---|---:|---|
| 使用 fish-trail 作为项目名称 | extracted | 2026-05-05 | 用户明确认可 |
| 优先借鉴 Graphify 到 topic 管理 | extracted | 2026-05-05 | 用户明确提出 |
| 做成胖鱼独立 pack | inferred | 2026-05-05 | 基于胖鱼架构推断 |

## 相关 topic

- Graphify 借鉴
- 胖鱼 PEtFiSh
- context-router
- skill 生命周期管理
- 话题污染治理

## 不应默认混入的 topic

- rSwitch eBPF 实现细节
- OpenClash 配置
- 比赛赛程安排
- AI 安全课程大纲

## 相关产物

- `.petfish/fish-trail/topic_graph.json`
- `.petfish/fish-trail/TOPIC_REPORT.md`
- `.opencode/skills/fish-trail/SKILL.md`

## 待解决问题

1. 是否需要 HTML 可视化 topic map？
2. 是否接入 Graphify 作为项目文件索引后端？
3. context-router 和 fish-trail 的边界如何定义？
4. 话题拆分/合并是否需要人工确认？

## 下一步

实现 MVP：topic_detect、topic_update、topic_route、topic_report 四个脚本。
```

---

## 9. 系统架构

### 9.1 总体架构

```text
用户请求
  ↓
fish-trail topic detector
  ↓
topic_graph.json
  ↓
route planner
  ↓
context firewall
  ↓
active_context.md
  ↓
Agent 执行任务
  ↓
task outcome extractor
  ↓
topic updater
  ↓
topic cards / decision log / topic graph
```

### 9.2 模块拆分

```text
fish-trail/
├── detector       # 判断当前请求属于哪个 topic
├── router         # 选择 must_load / may_load / must_not_load
├── updater        # 更新 topic graph 和 topic cards
├── reporter       # 生成 TOPIC_REPORT.md
├── validator      # 校验 topic graph 结构和证据等级
├── firewall       # 上下文隔离策略
├── stale-checker  # 过期 topic 检测
└── adapter        # opencode / petfish / context-router 适配
```

---

## 10. 命令设计

建议作为 `/petfish topic` 子命令发布。

### 10.1 初始化

```bash
/petfish topic init
```

初始化 fish-trail 目录和配置。

### 10.2 检测 topic

```bash
/petfish topic detect "用户当前请求"
```

识别请求对应 topic。

### 10.3 路由上下文

```bash
/petfish topic route "用户当前请求"
```

生成 `active_context.md`。

### 10.4 更新 topic

```bash
/petfish topic update --from-session notes.md
```

从一次对话记录或任务结果中更新 topic graph。

### 10.5 生成报告

```bash
/petfish topic report
```

生成 `TOPIC_REPORT.md`。

### 10.6 查看 topic card

```bash
/petfish topic card topic-fish-trail
```

生成或查看某个 topic card。

### 10.7 拆分 topic

```bash
/petfish topic split topic-old --into topic-a topic-b
```

拆分混杂 topic。

### 10.8 合并 topic

```bash
/petfish topic merge topic-a topic-b
```

合并重复 topic。

### 10.9 建立关系

```bash
/petfish topic relate topic-a topic-b --type depends_on
```

人工确认 topic 关系。

### 10.10 检查过期 topic

```bash
/petfish topic stale
```

列出可能过期 topic。

### 10.11 检查上下文污染

```bash
/petfish topic quarantine
```

列出疑似污染 topic 或不应混合的上下文。

### 10.12 生成交接包

```bash
/petfish topic handoff topic-fish-trail
```

生成新会话交接包。

---

## 11. OpenCode Skill 设计

### 11.1 目录结构

```text
.opencode/
└── skills/
    └── fish-trail/
        ├── SKILL.md
        ├── SECURITY.md
        ├── scripts/
        │   ├── topic_detect.py
        │   ├── topic_route.py
        │   ├── topic_update.py
        │   ├── topic_report.py
        │   ├── topic_validate.py
        │   ├── topic_stale.py
        │   └── topic_handoff.py
        ├── references/
        │   ├── topic-schema.md
        │   ├── routing-policy.md
        │   ├── evidence-levels.md
        │   ├── context-firewall.md
        │   └── update-rules.md
        ├── assets/
        │   ├── topic-card-template.md
        │   ├── active-context-template.md
        │   ├── topic-report-template.md
        │   └── config-template.yaml
        └── evals/
            ├── evals.json
            └── files/
```

### 11.2 SKILL.md 草案

```markdown
---
name: fish-trail
description: Use this skill when the user asks to manage long-running topics, prevent context pollution, route a task to the right prior discussion, generate handoff summaries, split or merge conversation topics, or maintain topic graphs for PEtFiSh projects. It creates and updates topic cards, topic_graph.json, active_context.md, decision logs, and context firewall rules.
license: MIT
compatibility: opencode; requires Python 3.10+ and preferably uv
metadata:
  pack: petfish
  category: topic-management
  maturity: experimental
---

# fish-trail

fish-trail manages topic graph and context routing for long-running AI-assisted projects.

## When to use

Use this when:

- The user wants to continue a previous topic without mixing unrelated context.
- The user asks to split, merge, summarize, or hand off topics.
- The current task depends on historical decisions.
- The project contains multiple active workstreams.
- The user mentions context pollution, topic governance, Graphify-inspired topic graph, or PEtFiSh topic management.

## Core rule

Do not load broad historical context by default. First route the task through fish-trail, then load only the minimum necessary topic context.

## Workflow

1. Detect the relevant topic:

   ```bash
   python scripts/topic_detect.py --query "<user request>"
   ```

2. Generate active context:

   ```bash
   python scripts/topic_route.py --query "<user request>" --write-active-context
   ```

3. Read `.petfish/fish-trail/active_context.md`.

4. Perform the user task using only the selected context unless source verification is required.

5. After the task, update topic state:

   ```bash
   python scripts/topic_update.py --from-notes <task-notes-file>
   ```

6. Validate:

   ```bash
   python scripts/topic_validate.py
   ```

## Evidence discipline

Classify every new relation as extracted, inferred, ambiguous, proposed, or deprecated. Never present inferred or ambiguous relations as confirmed decisions.

## Context firewall

Respect must_load, may_load, and must_not_load sections in active_context.md.
```

---

## 12. 脚本设计

### 12.1 脚本原则

所有脚本应遵循：

```text
非交互
幂等
默认 dry-run 友好
结构化 JSON 输出
错误信息可行动
支持 --help
支持 --project-root
```

### 12.2 `topic_detect.py`

用途：识别当前请求属于哪个 topic。

示例：

```bash
python scripts/topic_detect.py \
  --query "按照这个思路给出完整的项目设计和开发方案" \
  --project-root .
```

输出：

```json
{
  "matched_topics": [
    {
      "topic_id": "topic-fish-trail",
      "score": 0.93,
      "reason": "Query asks for complete project design and development plan based on prior fish-trail discussion.",
      "evidence_level": "extracted"
    }
  ],
  "is_cross_topic": false,
  "needs_new_topic": false,
  "recommended_action": "route"
}
```

MVP 算法：

```text
关键词匹配
topic card 摘要相似度
recent route 历史加权
显式用户短语加权
```

### 12.3 `topic_route.py`

用途：生成 `active_context.md`。

输出示例：

```markdown
# Active Context

## Current topic

fish-trail 话题轨迹管理器

## User request

按照这个思路给出完整的项目设计和开发方案

## Must load

- `.petfish/fish-trail/topic_cards/fish-trail.md`
- `.petfish/fish-trail/decisions/decision_log.md`
- `.petfish/fish-trail/topic_graph.json`

## May load

- topic: Graphify 借鉴
- topic: 胖鱼 PEtFiSh
- topic: context-router

## Must not load

- rSwitch eBPF 细节
- OpenClash 配置
- 比赛赛程安排
- AI 安全课程大纲

## Confirmed decisions

- 使用 fish-trail 作为名称。
- 优先在 topic 管理中借鉴 Graphify。
- 使用 topic graph 和 context firewall 降低上下文污染。

## Open questions

- 是否需要 HTML 可视化？
- 是否接入 Graphify 后端？
```

### 12.4 `topic_update.py`

用途：任务完成后更新 topic graph、topic card 和 decision log。

输入可以是：

```text
task notes
assistant final answer
manual update yaml
```

示例：

```bash
python scripts/topic_update.py \
  --from-notes .petfish/fish-trail/routes/last_task_notes.md \
  --topic topic-fish-trail
```

更新内容：

```text
新增决策
新增 open questions
新增相关 artifact
新增 topic 关系
废弃旧关系
更新时间戳
```

### 12.5 `topic_report.py`

生成全局报告。

示例结构：

```markdown
# Fish Trail Topic Report

## Overview

当前项目共有 17 个 topics，其中 5 个 active、4 个 stale、2 个 ambiguous、3 个需要人工确认关系。

## Hub topics

- 胖鱼 PEtFiSh
- fish-trail
- skills 安全治理
- rSwitch 论文

## Recently active

- fish-trail
- Graphify 借鉴
- SKILL_builder

## Possible pollution risks

| Topic A | Topic B | Risk | Reason |
|---|---|---|---|
| AI 安全课程 | skills 开发 | medium | 都涉及课程开发 skills，但目标不同 |
| rSwitch 论文 | rSwitch 工程实现 | high | 论文叙事与代码 debug 容易混淆 |

## Stale topics

| Topic | Last updated | Reason |
|---|---:|---|
| old-context-router-design | 2026-04-23 | superseded by fish-trail |

## Suggested maintenance

1. 合并 `topic-graphify-evaluation` 和 `topic-graphify-borrowing`。
2. 将 `topic-context-router` 拆为 `topic-routing-policy` 和 `topic-conversation-handoff`。
```

### 12.6 `topic_validate.py`

校验内容：

```text
topic_graph.json 合法
所有 topic_id 唯一
所有 edge source/target 存在
evidence_level 合法
deprecated 关系不进入 must_load
must_not_load 没有自相矛盾
topic card frontmatter 完整
```

输出示例：

```json
{
  "status": "pass",
  "errors": [],
  "warnings": [
    {
      "code": "AMBIGUOUS_EDGE",
      "message": "edge-topic-a-topic-b is ambiguous and should be confirmed."
    }
  ]
}
```

---

## 13. Context Firewall 设计

### 13.1 三层上下文

```yaml
must_load:
  description: 当前任务必须加载，否则容易答偏
  max_items: 8

may_load:
  description: 有帮助但不默认展开
  max_items: 10

must_not_load:
  description: 明确不应混入的 topic、文件、旧决策
  max_items: 20
```

### 13.2 路由策略

```yaml
routing_policy:
  exact_user_reference:
    action: must_load
    weight: 1.0

  recent_active_topic:
    action: may_load
    weight: 0.4

  same_project:
    action: may_load
    weight: 0.3

  should_not_mix_with:
    action: must_not_load
    weight: 1.0

  deprecated_decision:
    action: must_not_load
    weight: 1.0

  ambiguous_relation:
    action: may_load
    require_warning: true
```

### 13.3 防污染报告

```markdown
# Context Pollution Report

## Detected risks

1. 当前请求与 `topic-context-router` 高度相关，但该 topic 已有部分结论被 `topic-fish-trail` 替代。
2. `topic-graphify-evaluation` 和 `topic-graphify-borrowing` 存在重复，应合并或明确边界。
3. `topic-rswitch-paper` 与当前任务无关，应加入 must_not_load。

## Recommended changes

- Add edge: `topic-fish-trail supersedes topic-old-context-router-design`
- Add edge: `topic-rswitch-paper should_not_mix_with topic-fish-trail`
```

---

## 14. 与 Graphify 的关系

fish-trail 不直接复制 Graphify，而是吸收四个设计模式：

| Graphify 机制 | fish-trail 迁移 |
|---|---|
| 项目知识图谱 | topic graph |
| GRAPH_REPORT.md | TOPIC_REPORT.md |
| graph.json | topic_graph.json |
| 图谱导航后回源 | topic 路由后回源 |
| 置信度/证据标记 | evidence_level |
| 增量更新 | topic delta update |
| god nodes | hub topics |
| surprising connections | cross-topic relations |
| stale graph | stale topic |

未来可以增加 Graphify 适配器：

```text
fish-trail 管理对话 topic
Graphify 管理项目文件知识
二者通过 artifact 节点连接
```

示例：

```json
{
  "source": "topic-rswitch-paper",
  "target": "artifact-graphify-rswitch-graph",
  "relation": "uses_artifact",
  "summary": "rSwitch 论文 topic 使用 Graphify 生成的项目结构图作为代码理解入口。"
}
```

---

## 15. 与 PEtFiSh 命令集成

### 15.1 `/initproject`

初始化项目时：

```text
1. 创建 .petfish/fish-trail/
2. 创建初始 topic：project-overview
3. 创建初始 decision：项目类型、目标、约束
4. 安装 .opencode/skills/fish-trail
5. 在 AGENTS.md 加入 fish-trail 使用规则
```

AGENTS.md 注入：

```markdown
## Topic Management

This project uses fish-trail for topic graph and context routing.

Before working on a task that may depend on prior discussions:

1. Run fish-trail topic routing.
2. Read `.petfish/fish-trail/active_context.md`.
3. Follow the must_load / may_load / must_not_load rules.
4. Update fish-trail after significant decisions or topic changes.
```

### 15.2 `/petfish suggest`

根据当前 topic 推荐 skills：

```text
topic = fish-trail

推荐：
- context-router
- skill-eval
- skill-security-auditor
- markdown-writer
```

### 15.3 `/petfish gate`

加入 fish-trail 质量检查：

```text
topic graph valid
no orphan topics
no invalid evidence level
no stale active topic
no unresolved high-risk pollution edge
```

---

## 16. 安全与隐私设计

### 16.1 安全边界

fish-trail 处理的是高价值上下文，因此不能随意外传。

默认策略：

```text
本地文件存储
不上传远程服务
不读取敏感文件
不记录密钥
不把完整对话原文写入 topic card
只保存摘要、证据引用和必要短摘
```

### 16.2 敏感信息处理

默认跳过：

```text
.env
*.key
*.pem
auth.json
credentials*
token*
secret*
```

如果证据来自敏感文件，只记录：

```text
source_type: sensitive_file
source_path: redacted
evidence_summary: "A credential-related configuration exists."
```

不记录原文。

### 16.3 Prompt Injection 防护

如果从外部文档、网页、issue、邮件中抽取 topic，必须标记：

```yaml
source_trust: external_untrusted
```

且不能把外部文本中的“指令”写入 Agent 执行规则。

### 16.4 SECURITY.md 结构

```markdown
# fish-trail Security Model

## Threat surface

- Topic graph poisoning
- Prompt injection from external content
- Sensitive data leakage
- Incorrect topic merge
- Stale decision reuse
- Context firewall bypass

## Mitigations

- Evidence levels
- Source trust labels
- Sensitive file ignore rules
- Manual confirmation for merge/split
- Deprecated decision marking
- Validation before route
```

---

## 17. 评测方案

评测不能只看“是否生成 summary”，而要看它是否减少污染、是否能正确路由。

### 17.1 eval 目录

```text
.opencode/skills/fish-trail/evals/
├── evals.json
├── files/
│   ├── mixed-conversation.md
│   ├── old-decisions.md
│   ├── topic_graph.sample.json
│   └── polluted-context.md
└── expected/
    ├── active_context.expected.md
    └── topic_graph.expected.json
```

### 17.2 测试用例

```json
{
  "skill_name": "fish-trail",
  "evals": [
    {
      "id": "route-current-topic",
      "prompt": "我们继续 fish-trail，把它做成完整设计方案",
      "expected_output": "Routes to topic-fish-trail, loads Graphify borrowing and PEtFiSh topics as may_load, excludes unrelated rSwitch implementation details.",
      "files": ["evals/files/topic_graph.sample.json"],
      "assertions": [
        "active_context.md is generated",
        "topic-fish-trail appears in must_load",
        "topic-rswitch-xdp-debug appears in must_not_load",
        "No deprecated decision appears in must_load"
      ]
    },
    {
      "id": "detect-topic-split",
      "prompt": "这个 topic 里既有课程开发又有 skill 安全，帮我拆一下",
      "expected_output": "Proposes two topics and marks split as proposed, not extracted.",
      "assertions": [
        "Two new topic candidates are proposed",
        "Evidence level is proposed",
        "Original topic is not deleted without confirmation"
      ]
    },
    {
      "id": "avoid-context-pollution",
      "prompt": "继续之前那个部署运维 skill",
      "expected_output": "Routes to deploy/ops skill topic and does not load AI 安全课程 topic.",
      "assertions": [
        "deploy topic is selected",
        "course topic is excluded or only may_load with low score",
        "Reason for exclusion is recorded"
      ]
    }
  ]
}
```

### 17.3 评测指标

```yaml
metrics:
  routing_accuracy:
    target: ">= 0.85"

  pollution_avoidance:
    target: ">= 0.90"

  stale_decision_block_rate:
    target: ">= 0.95"

  topic_update_validity:
    target: ">= 0.95"

  human_acceptance:
    target: ">= 0.80"
```

---

## 18. 技术选型

### 18.1 语言与运行环境

建议：

```text
Python 3.10+
uv
标准库优先
```

MVP 依赖：

```toml
dependencies = [
  "pydantic>=2,<3",
  "jinja2>=3,<4",
  "rapidfuzz>=3,<4"
]
```

后续可选：

```toml
optional = [
  "networkx>=3,<4",
  "pyvis>=0.3,<0.4"
]
```

### 18.2 为什么第一版不用图数据库

不需要 Neo4j，也不需要复杂向量库。

理由：

```text
topic 数量早期不会很大
JSON 足够可审计
Markdown 足够人类可读
git diff 友好
便于胖鱼安装和卸载
```

---

## 19. 开发路线图

### Phase 0：设计冻结

目标：冻结 schema 和 MVP 边界。

交付：

```text
references/topic-schema.md
references/routing-policy.md
assets/topic-card-template.md
assets/active-context-template.md
```

退出标准：

```text
能手工写出一个 topic_graph.json
能手工写出一个 topic card
能解释 fish-trail 和 context-router 边界
```

---

### Phase 1：MVP 脚本

目标：JSON + Markdown 闭环。

实现：

```text
topic_detect.py
topic_route.py
topic_update.py
topic_report.py
topic_validate.py
```

功能：

```text
初始化目录
识别 topic
生成 active_context
更新 topic card
生成 TOPIC_REPORT
校验 topic graph
```

退出标准：

```text
在 SKILL_builder 自身 repo 中运行
能管理至少 5 个 topic
能生成有效 active_context.md
```

---

### Phase 2：OpenCode skill 化

目标：作为 OpenCode skill 可用。

实现：

```text
.opencode/skills/fish-trail/SKILL.md
SECURITY.md
evals/evals.json
AGENTS.md 注入片段
```

退出标准：

```text
OpenCode 能发现 fish-trail
Agent 能按 SKILL.md 调用脚本
任务结束能更新 topic
```

---

### Phase 3：PEtFiSh 集成

目标：进入胖鱼命令体系。

新增：

```text
/petfish topic init
/petfish topic route
/petfish topic update
/petfish topic report
/petfish topic stale
/petfish topic handoff
```

退出标准：

```text
/initproject 可选择安装 fish-trail
/petfish gate 检查 fish-trail 状态
/petfish suggest 可基于 topic 推荐 skills
```

---

### Phase 4：可视化与高级能力

目标：形成 Graphify 式可见产物。

新增：

```text
topic_map.html
topic health dashboard
context pollution report
topic merge/split assistant
Graphify artifact adapter
```

退出标准：

```text
能用 HTML 查看 topic graph
能发现 hub topics 和污染风险
能手动确认 merge/split
```

---

## 20. 最小可用版本目录

建议先在 SKILL_builder 中新增：

```text
packs/
└── fish-trail/
    ├── README.md
    ├── pack.yaml
    ├── .opencode/
    │   └── skills/
    │       └── fish-trail/
    │           ├── SKILL.md
    │           ├── SECURITY.md
    │           ├── scripts/
    │           ├── references/
    │           ├── assets/
    │           └── evals/
    ├── templates/
    │   └── petfish-state/
    │       └── fish-trail/
    └── examples/
        └── skill-builder-self/
```

### 20.1 `pack.yaml`

```yaml
name: fish-trail
version: 0.1.0
description: Topic graph and context routing pack for PEtFiSh projects.
platforms:
  - opencode
  - claude-code
  - universal
requires:
  python: ">=3.10"
  tools:
    - uv
provides:
  commands:
    - petfish topic init
    - petfish topic route
    - petfish topic update
    - petfish topic report
  artifacts:
    - .petfish/fish-trail/topic_graph.json
    - .petfish/fish-trail/TOPIC_REPORT.md
    - .petfish/fish-trail/topic_cards/
```

---

## 21. MVP 实现优先级

| 优先级 | 功能 | 价值 | 难度 |
|---:|---|---|---|
| P0 | topic_graph.json schema | 基础 | 低 |
| P0 | topic card 模板 | 基础 | 低 |
| P0 | active_context.md 生成 | 最高 | 中 |
| P0 | context firewall | 最高 | 中 |
| P1 | topic update | 高 | 中 |
| P1 | decision log | 高 | 低 |
| P1 | topic report | 高 | 中 |
| P2 | split / merge | 中高 | 中 |
| P2 | stale detection | 中高 | 中 |
| P3 | HTML topic map | 中 | 中 |
| P3 | Graphify adapter | 中 | 中高 |
| P4 | MCP server | 高但后置 | 高 |

---

## 22. 关键风险与缓解

### 22.1 topic graph 被 AI 污染

缓解：

```text
证据分级
source_trust
人工确认 ambiguous / proposed 关系
validate 脚本
```

### 22.2 维护成本过高

缓解：

```text
只在重大任务后更新
自动增量更新
topic card 保持短
过期 topic 自动标记
```

### 22.3 Agent 忽略 active_context

缓解：

```text
SKILL.md 明确工作流
AGENTS.md 加入强规则
/petfish gate 检查是否更新
任务结束时强制 topic delta
```

### 22.4 topic 拆太细

缓解：

```text
topic 最小粒度规则：
只有当上下文加载集合、决策集合或任务目标明显不同，才拆分 topic。
```

### 22.5 topic 合并误伤

缓解：

```text
merge 默认只生成 proposal
需要用户确认
保留 supersedes 关系
不直接删除旧 topic
```

---

## 23. 成功标准

### 23.1 第一阶段成功标准

```text
能在 SKILL_builder 自身项目中稳定管理 5-10 个 topic
能生成有效 active_context
能明显减少无关上下文混入
```

### 23.2 第二阶段成功标准

```text
能与 /initproject 集成
新项目初始化时自动创建 topic graph
Agent 任务开始前会先读 active_context
```

### 23.3 第三阶段成功标准

```text
能支持多项目长期协作
能生成 handoff 包
能检测过期决策和上下文污染
```

### 23.4 最终成功标准

```text
fish-trail 成为胖鱼区别于普通 skill installer 的核心能力：
不是只安装 skills，而是维护 AI 协作项目的长期上下文轨迹。
```

---

## 24. 第一批 topic 种子

在 SKILL_builder 项目中，可以初始化这些 topic：

```yaml
topics:
  - id: topic-petfish-core
    title: 胖鱼 PEtFiSh 核心定位

  - id: topic-skill-lifecycle
    title: Skill 生命周期管理

  - id: topic-project-init
    title: 项目初始化助手

  - id: topic-fish-trail
    title: fish-trail 话题轨迹管理器

  - id: topic-graphify-borrowing
    title: Graphify 机制借鉴

  - id: topic-skill-security
    title: Skill 安全治理

  - id: topic-context-router
    title: 上下文路由与话题治理

  - id: topic-opencode-adapter
    title: OpenCode 适配
```

---

## 25. 建议的 MVP 闭环

第一版不要先做复杂可视化。只追求一个最小闭环：

```text
topic_graph.json
  ↓
topic card
  ↓
active_context.md
  ↓
任务执行
  ↓
topic_update
  ↓
TOPIC_REPORT.md
```

只要这个闭环跑通，fish-trail 就已经比普通 summary 强很多。

---

## 26. 最终判断

fish-trail 应该成为胖鱼的一个关键转折点。

胖鱼如果只做 skill installer，价值是：

```text
帮我安装合适的 skills
```

加入 fish-trail 后，价值会升级成：

```text
帮我长期维护一个 AI-agent 友好的项目工作区；
不仅知道装什么 skills，还知道当前任务属于哪个 topic、该加载哪些历史决策、哪些上下文不能混进来。
```

这才是胖鱼真正的产品壁垒。
