---
name: learning-practice-planner
description: 基于学习路径设计分层练习与实操任务，构建从概念巩固到项目迁移的练习闭环。Use when the user says "练习计划", "practice plan", "实操任务", "hands-on", "动手练习", "Concept Drill", "Code Lab", "Mini Project", "Transfer Task", "验收标准", "练习设计", "动手训练", "coding exercise", "小项目实践", "练习编排", "复盘节奏", "概念练习", "看懂了但做不出", or "练什么".
compatibility: opencode
license: Apache-2.0
metadata:
  version: "0.11.1"
  author: "petfish-team"
---

## 作用/Purpose

将学习路径转化为可执行练习方案，明确每阶段“练什么、如何验收、如何递进”。该skill必须覆盖：
1) 练习类型分层与任务编排；
2) 练习与能力目标逐项映射；
3) 练习产出、反馈与纠偏机制设计。

输出应能直接进入执行，不是泛泛“多练习”的建议。

---

## 触发场景/Trigger Scenarios

- 已有`learning-path.md`，需要生成可执行练习计划
- 需要把资源学习转化为动手训练任务
- 需要平衡概念练习、代码实验与小项目实践
- 需要定义练习验收标准与复盘节奏
- 需要降低“看懂了但做不出”的学习偏差

---

## 输入/Input

- `learning-path.md`（来自`learning-path-designer`）
- `resource-list.md`
- practice constraints（时间预算、环境条件、工具限制）
- 可选：历史练习表现、偏好任务类型、业务场景题库

---

## 输出/Output

- `practice-plan.md`

---

## 工作流/Workflow

1. 解析学习路径阶段目标，提取每阶段应验证的能力点。
2. 设计练习分层：Concept Drill、Code Lab、Mini Project、Transfer Task等类型。
3. 为每阶段编排任务序列，定义任务目标、输入、产出与完成标准。
4. 绑定资源与任务，标记必做项、选做项与挑战项。
5. 设置反馈机制：自检清单、同伴评审、失败重做条件与纠偏动作。
6. 规划节奏与负荷，校准每周任务量与总周期可执行性。
7. 输出`practice-plan.md`，并标注下一步交接到`learning-progress-reviewer`。

---

## 质量门禁/Quality Gates

- 每个阶段至少包含2类不同练习类型。
- 每个任务必须包含可验证产出（代码、文档、演示或报告）。
- 每个任务必须定义完成标准（DoD）且至少1条量化指标。
- 计划中必须有至少1个Mini Project用于综合能力验证。
- 总任务负荷需与输入时间预算偏差不超过20%。
- 必须定义至少1条失败后纠偏路径（重做/降阶/补学）。

---

## Gotchas/注意事项

- 不要只列资源链接而不定义练习动作。
- 不要所有任务同难度，需有递进梯度。
- 不要仅做概念题，必须包含真实操作任务。
- 不要忽略验收标准，否则“完成”不可判定。
- 不要把复盘放到最后一次性做，需阶段化反馈。

---

## 关联资源

- `learning-path-designer`
- `learning-resource-discovery`
- `learning-progress-reviewer`
- `decision-criteria-builder`
