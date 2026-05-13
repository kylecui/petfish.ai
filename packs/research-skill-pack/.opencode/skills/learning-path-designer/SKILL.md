---
name: learning-path-designer
description: 基于学习目标与资源清单设计分阶段学习路径，定义阶段目标、资源组合、练习任务、交付物与评估检查点。Use when the user says "学习路径", "learning path", "学习路线", "roadmap", "分阶段学习", "阶段规划", "phase plan", "学习里程碑", "milestone", "检查点", "checkpoint", "理论+实操", or "怎么安排学习".
compatibility: opencode
license: Apache-2.0
---

## 作用/Purpose

将学习目标与资源清单转化为可执行的阶段化学习路径，明确“学什么、何时学、如何验收”。该skill必须覆盖：
1) 阶段划分与目标递进；
2) 资源与练习任务编排；
3) 交付物与评估检查点设计。

输出应可直接执行并可跟踪进展，而不是泛化建议。

---

## 触发场景/Trigger Scenarios

- 已有学习简报和资源清单，需要落地执行计划
- 需要把学习拆成阶段并定义里程碑
- 需要平衡理论学习、实操练习与交付产出
- 需要制定可检查的学习节奏与复盘机制
- 需要避免“学了很多但不会用”的路径偏差

---

## 输入/Input

- `learning-brief.md`
- `resource-list.md` 与 `resource-index.jsonl`
- schedule constraints（每周时长、总周期、可用环境）
- 可选：偏好学习方式、必须完成的项目任务

---

## 输出/Output

- `learning-path.md`

---

## 工作流/Workflow

1. 读取学习目标与资源分层，确认阶段总数与周期边界。
2. 设计阶段结构（入门、夯实、应用、强化等）及每阶段目标。
3. 为每阶段绑定资源组合，区分必修与选修内容。
4. 配置练习任务与实战任务，确保与目标能力逐项映射。
5. 定义阶段交付物（笔记、实验、项目、演示）与验收标准。
6. 设置检查点与复盘节奏，明确风险信号与纠偏策略。
7. 输出`learning-path.md`，标注后续可衔接`decision-brief-framer`进行路径取舍。

---

## 质量门禁/Quality Gates

- 每个阶段必须有明确目标与完成定义（DoD）。
- 阶段任务必须覆盖理论、实践与反馈闭环。
- 交付物必须可审阅、可验证，不得仅写“理解了”。
- 评估检查点必须有时间与指标，不得空泛。
- 路径总负荷必须与时间预算一致，避免不可执行。
- 至少包含1个综合实战任务以验证迁移能力。

---

## Gotchas/注意事项

- 不要把路径写成资源目录，必须强调行动与产出。
- 不要阶段过细导致管理成本过高。
- 不要只安排输入学习，缺少输出会导致掌握失真。
- 不要忽略复盘与纠偏，学习路径需要动态调整。
- 不要脱离真实应用场景，否则迁移效果弱。

---

## 关联资源

- `learning-goal-framer`
- `learning-resource-discovery`
- `research-evidence-ledger`
- `planning-roadmap-developer`
