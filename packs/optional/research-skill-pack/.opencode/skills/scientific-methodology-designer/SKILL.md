---
name: scientific-methodology-designer
description: 科学方法设计：把研究想法落成可证伪research design，定义研究对象、核心假设、I/O、差异化、验证路径与validity threats，明确可声称与不可声称边界。Use when users ask “方法设计/methodology/research design/如何验证/实验方法/method section/validity threats”.
compatibility: opencode
license: Apache-2.0
---

## 作用/Purpose

把“有想法”变成“可验证研究方案”。该skill要求从研究问题出发，明确研究对象、核心假设、方法输入输出、与现有工作的差异、验证方案、有效性威胁与不可声称边界。目标是生成可执行、可证伪、可复核的方法学设计，供后续实验规划与论文写作直接使用。

---

## 触发场景/Trigger Scenarios

- 用户要求“方法设计 / research design / methodology”
- 用户问“这个想法怎么验证才站得住”
- 已有gap与贡献方向，需要落成研究方案
- 论文或技术报告需要 method section 骨架
- 需要系统梳理 validity threats 与结论边界

---

## 输入/Input

- 研究问题与目标贡献（来自brief/gap分析）
- 文献矩阵与候选基线方法
- 可选：资源约束（数据、时间、算力、实验环境）
- 可选：目标输出场景（论文、系统原型、技术报告）

---

## 输出/Output

- `research-design.md` — 研究设计主文档
- `methodology.md` — 方法细化（流程、I/O、差异化、验证计划）
- `validity-threats.md` — 有效性威胁与缓解策略

---

## 工作流/Workflow

1. 固化研究对象与问题边界，避免方法目标漂移。
2. 提炼可检验假设，写明成立条件与失败条件。
3. 定义方法输入/输出与关键处理流程。
4. 对比已有方法，明确差异化点与预期收益。
5. 设计验证路径（实验、对照、消融、统计或证明）。
6. 识别并记录 validity threats（internal/external/construct/conclusion/ecological）。
7. 明确不可声称结论，约束论文/报告表述边界。
8. 形成可执行计划并连接后续 experiment planner。
9. 参考 `methodology-patterns.md` 与 `validity-threats.md` 校准完整性。

---

## 质量门禁/Quality Gates

必须明确回答以下8个问题：

1. 研究对象是什么？
2. 要解决的问题是什么？
3. 核心假设是什么？
4. 方法输入和输出是什么？
5. 与已有方法相比差异在哪里？
6. 如何证明有效？
7. 哪些威胁会影响结论？
8. 哪些结论不能声称？

若任一问题缺失，方法设计视为未完成。

---

## Gotchas/注意事项

- 不要把“系统实现步骤”当成“研究方法”；需先定义可证伪假设。
- 不要只写成功路径，必须写失败判据与边界。
- 不要回避威胁分析；威胁披露是可信度组成部分。
- 不要把基线对比写成口头差异，需可测量、可复核。
- 不要宣称超出验证范围的结论。

---

## 关联资源

- References: `methodology-patterns.md`, `validity-threats.md`
