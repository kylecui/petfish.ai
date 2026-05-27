---
name: decision-recommendation
description: 基于decision brief、criteria与comparison matrix生成最终推荐，明确生效条件、备选/回退路径、风险、试点验证与决策日志。Use when the user says "最终建议", "recommendation", "final decision", "decision recommendation", "推荐方案", "go/no-go", "决策结论", "回退策略", "pilot", "PoC", "执行计划", or "decision log".
compatibility: opencode
license: Apache-2.0
---

## 作用/Purpose

将前序决策研究结果整合为可执行推荐结论，并明确条件边界与后续验证路径。该skill必须覆盖：
1) 推荐结论与触发条件；
2) 备选方案与切换策略；
3) 风险、验证与决策留痕。

输出应可直接用于决策会签与执行跟踪，而不是“意见汇总”。

---

## 触发场景/Trigger Scenarios

- 已完成比较矩阵，需要形成最终决策建议
- 需要明确推荐的生效条件与风险边界
- 需要给出备选路线与回退策略
- 需要形成可审计的决策日志
- 需要将研究结论转化为执行计划

---

## 输入/Input

- `decision-brief.md`
- `criteria.md`
- `comparison-matrix.md`
- 可选：额外风险评估、试点反馈、组织约束更新

---

## 输出/Output

- `recommendation.md`

---

## 工作流/Workflow

1. 汇总决策简报、标准与矩阵结果，确认结论输入完整性。
2. 形成主推荐方案，说明“为什么是它”与适用条件。
3. 给出次优备选与切换条件，定义何时触发替代路径。
4. 梳理关键风险、不确定性与潜在失败模式。
5. 设计验证步骤（试点、PoC、阶段验收）与成功阈值。
6. 记录决策日志：结论、证据摘要、责任人、时间与复审点。
7. 输出`recommendation.md`，并建议必要时回流`decision-brief-framer`更新边界。

---

## 质量门禁/Quality Gates

- 推荐结论必须可追溯到比较矩阵与证据条目。
- 推荐条件必须明确，不得写成无条件结论。
- 必须至少提供1个可执行备选方案。
- 风险项必须包含影响、概率或触发信号描述。
- 验证步骤必须有时间窗与量化阈值。
- 决策日志必须记录责任人与复审时间点。

---

## Gotchas/注意事项

- 不要把“最高分”直接等同于“最佳决策”，需看条件匹配。
- 不要省略备选与回退路径，决策需要弹性。
- 不要只写风险名称，不写触发信号与应对动作。
- 不要忽略执行验证，推荐必须可被现实检验。
- 不要遗漏决策留痕，否则后续复盘失真。

---

## 关联资源

- `decision-brief-framer`
- `decision-criteria-builder`
- `option-comparison-matrix`
- `research-evidence-ledger`
