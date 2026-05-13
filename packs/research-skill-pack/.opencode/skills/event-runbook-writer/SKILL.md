---
name: event-runbook-writer
description: 将活动研究成果转为可执行runbook/run of show，覆盖before/during/after时间线、角色分工、检查清单、沟通升级链路、应急SOP与复盘模板。Use when the user says "活动执行手册", "event runbook", "run of show", "现场执行", "operation playbook", "execution checklist", "SOP", "活动SOP", "升级路径", "应急SOP", or "活动复盘模板".
compatibility: opencode
license: Apache-2.0
metadata:
  version: "0.11.1"
  author: "petfish-team"
---

## 作用/Purpose

把体验活动从“计划”推进到“可执行”，通过标准化runbook降低现场协同成本并提升异常处理效率。该skill必须覆盖：
1) 端到端时间线与阶段划分；
2) 角色职责、检查清单与沟通机制；
3) 应急流程与事后复盘模板。

输出应可直接用于执行与交接，而非仅作汇报材料。

---

## 触发场景/Trigger Scenarios

- 用户要求“活动执行手册 / event runbook / run of show”
- 需要将日程与后勤风险方案整合成现场操作文档
- 需要定义角色分工、联络链路与升级路径
- 需要准备执行检查清单与紧急响应流程
- 需要标准化活动后复盘与改进输入

---

## 输入/Input

- `experience-brief.md`
- `schedule.md` 或 `itinerary.md`
- `logistics-plan.md`
- `risk-contingency.md`
- 可选：组织通讯录、指挥层级、场地平面图、供应商联系人

---

## 输出/Output

- `event-runbook.md`

---

## 工作流/Workflow

1. 汇总上游成果并划分执行阶段：before event、during event、after event。
2. 构建主时间线（run of show），对齐关键活动、决策点与责任角色。
3. 设计分角色检查清单（组织者、主持、后勤、安全、技术支持）。
4. 定义沟通机制：频道、汇报频率、升级路径、关键联系人备份。
5. 嵌入应急流程：触发信号、决策权限、处置SOP与回退步骤。
6. 增补复盘模板：目标达成、异常记录、证据链接、改进事项与owner。
7. 生成`event-runbook.md`并验证与上游计划一致，避免执行口径冲突。

---

## 质量门禁/Quality Gates

- runbook必须显式分为before event、during event、after event三个阶段。
- 每个关键节点必须有时间、负责人、输入依赖与完成标准。
- 沟通与升级路径必须至少覆盖正常流程与紧急流程两条链路。
- 应急SOP必须可执行，至少包含触发条件、动作步骤与停止条件。
- 复盘模板必须包含可追溯证据字段，不得只留主观感受。
- 文档内容必须与`schedule`和`logistics/risk`保持一致，不得出现冲突指令。

---

## Gotchas/注意事项

- 不要把runbook写成“计划摘要”，它应是现场可直接操作的执行文档。
- 不要混淆before/during/after三个阶段，否则责任边界会失焦。
- 不要只定义主负责人，关键岗位应配置备份联系人。
- 不要省略紧急场景演练步骤，未演练的SOP通常不可用。
- 不要把复盘停留在口头结论，需沉淀结构化改进项与责任人。

---

## 关联资源

- `logistics-risk-planner`
- `research-evidence-ledger`
- `research-report-writer`
- `research-quality-reviewer`
