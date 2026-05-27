---
name: planning-roadmap-developer
description: 战略路线图开发与分阶段落地设计（里程碑、依赖关系、决策门、资源节奏），整合环境、利益相关方、情景、政策与技术评估输入。Use when the user says "战略路线图", "roadmap", "strategic planning", "milestone plan", "dependency map", "decision gate", "phased strategy", "季度规划", "年度规划", "go/no-go gate", or "执行路线图".
compatibility: opencode
license: Apache-2.0
---

## 作用/Purpose

将规划研究链路中的多源输入整合为可执行的阶段性战略路线图，明确里程碑、依赖关系、资源配置与决策门。该skill必须覆盖：
1) 战略目标到行动路径的分解；
2) 阶段划分、关键里程碑与依赖编排；
3) 决策门与调整机制设计。

输出应服务执行治理与持续校准，而不是静态“路线图图片”。

---

## 触发场景/Trigger Scenarios

- 用户要求“战略路线图 / roadmap / milestone plan”
- 需要把研究结论转成可落地的阶段计划
- 需要定义关键依赖关系和跨团队协同节奏
- 需要设置go/no-go决策门与调整触发条件
- 需要形成年度/季度战略推进路径

---

## 输入/Input

- environment and stakeholder inputs（来自`planning-environment-scanner`与`planning-stakeholder-analyst`）
- scenario and policy inputs（来自`planning-scenario-planner`与`planning-policy-researcher`）
- technology priorities（来自`planning-technology-assessor`）
- 可选：预算框架、资源容量、组织OKR、执行历史数据

---

## 输出/Output

- `strategic-roadmap.md`
- `milestone-plan.md`
- `dependency-map.md`

---

## 工作流/Workflow

1. 汇总规划链路输入，统一目标口径、约束条件与时间范围。
2. 将战略目标拆解为阶段成果、关键能力建设与执行动作。
3. 设计阶段结构（短中长期）并定义每阶段里程碑与验收标准。
4. 构建依赖关系图，标注前置条件、关键路径与跨团队接口。
5. 设置决策门（go/no-go/pivot）与触发信号，绑定证据更新机制。
6. 映射资源与风险，明确缓冲策略、替代路径与升级机制。
7. 产出路线图、里程碑计划与依赖图，并定义后续复盘与迭代节奏。

---

## 质量门禁/Quality Gates

- 路线图必须明确阶段目标、时间窗口与可验证输出。
- 每个里程碑必须有验收标准与责任归属。
- dependency map需显式标注关键路径与高风险依赖。
- 决策门必须绑定触发条件、所需证据与决策责任人。
- 路线图需体现情景、政策与技术约束，不得脱离输入前提。
- 至少提供1条风险升级路径与1条替代执行路径。

---

## Gotchas/注意事项

- 不要把路线图写成愿景口号，缺少执行动作与验收标准。
- 不要忽略跨团队依赖，避免里程碑在执行中失真。
- 不要将固定时间表凌驾于外部信号与决策门之上。
- 不要把一次性计划当成最终版本，应保留迭代机制。
- 不要遗漏关键假设与约束来源，避免后续追责困难。

---

## 关联资源

- `planning-environment-scanner`
- `planning-stakeholder-analyst`
- `planning-scenario-planner`
- `planning-policy-researcher`
- `planning-technology-assessor`
