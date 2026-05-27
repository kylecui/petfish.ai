---
name: learning-prerequisite-mapper
description: 为学习目标梳理前置知识与依赖关系，形成分层先修结构与补齐顺序，避免学习路径断层。Use when the user says "前置知识", "prerequisite", "先修要求", "学习依赖", "knowledge dependency", "基础不够", "知识断层", "需要先学什么", "依赖顺序", "补齐优先级", "跳级学习", "知识模块", "先修依赖图", "最小可学路径", "阻塞点", or "知识缺口".
compatibility: opencode
license: Apache-2.0
metadata:
  version: "0.11.1"
  author: "petfish-team"
---

## 作用/Purpose

将学习简报中的目标能力拆解为可执行的先修依赖图，并明确“先补什么、后学什么”。该skill必须覆盖：
1) 前置知识节点识别与分层；
2) 依赖关系与阻塞点标注；
3) 补齐优先级与最小可学路径输出。

输出应直接驱动资源发现与学习路径编排，而不是停留在笼统建议。

---

## 触发场景/Trigger Scenarios

- 已有`learning-brief.md`，需要明确先修知识与依赖顺序
- 用户反馈“基础不够”，需要定位知识断层
- 需要将目标能力拆成可补齐的知识模块
- 需要为后续资源检索提供分层输入
- 需要避免学习路径中出现“跳级学习”失败

---

## 输入/Input

- `learning-brief.md`（来自`learning-goal-framer`）
- learner baseline（当前知识、经验、可完成任务）
- domain constraints（学习时长、环境、工具限制）
- 可选：过往学习记录、失败案例、已有笔记

---

## 输出/Output

- `prerequisite-map.md`

---

## 工作流/Workflow

1. 读取学习目标与能力边界，抽取目标所需核心能力单元。
2. 识别先修知识节点，区分必备节点与增强节点。
3. 建立节点依赖关系，标注强依赖、弱依赖与并行可学项。
4. 结合学习者基线映射已具备项与缺口项，识别阻塞点。
5. 生成分层结构（基础层→核心层→应用层）与补齐顺序。
6. 输出最小可行先修路径与风险提示，避免过度前置扩张。
7. 生成`prerequisite-map.md`，并标注下一步交接到`learning-resource-discovery`。

---

## 质量门禁/Quality Gates

- 必须列出至少8个先修节点，且每个节点有层级标签。
- 每个目标能力至少映射1条可追踪先修链路。
- 每个阻塞点必须给出对应补齐动作与预计投入（小时/天）。
- 依赖关系需显式区分强依赖与可替代路径。
- 必须输出“最小可学路径”，且步骤数不少于3步。
- 输出中不得出现未定义术语；首次出现术语必须有一句解释。

---

## Gotchas/注意事项

- 不要把“相关知识”全部当成“前置知识”，会导致范围膨胀。
- 不要忽略学习者已掌握内容，否则会重复补基础。
- 不要只给列表不建依赖，列表无法指导学习顺序。
- 不要把可选增强项写成强依赖，会造成不必要阻塞。
- 不要输出抽象口号，必须落到可执行补齐动作。

---

## 关联资源

- `learning-goal-framer`
- `learning-resource-discovery`
- `learning-path-designer`
- `research-evidence-ledger`
