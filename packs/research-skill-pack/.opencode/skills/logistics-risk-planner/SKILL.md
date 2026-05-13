---
name: logistics-risk-planner
description: 规划活动物流与风险应对，覆盖交通/住宿/设备物资/许可、controllable vs uncontrollable风险、预算超支与取消应急路径。Use when the user says "后勤规划", "logistics planning", "物资准备", "风险预案", "risk contingency", "应急方案", "event logistics", "活动保障", "活动取消", "预算超支", or "backup plan".
compatibility: opencode
license: Apache-2.0
metadata:
  version: "0.11.1"
  author: "petfish-team"
---

## 作用/Purpose

将日程方案转化为可执行的后勤保障与风险管理计划，降低执行中断概率并提升应急响应能力。该skill必须覆盖：
1) 物流链路拆解与责任分配；
2) 风险识别、分级与处置预案；
3) 关键资源、触发阈值与回退路径定义。

输出应能支持现场执行，不是仅列风险名词。

---

## 触发场景/Trigger Scenarios

- 用户要求“后勤规划 / logistics planning / 风险预案 / contingency plan”
- 需要统筹交通、住宿、设备、物资、许可和供应商接口
- 需要识别天气、取消、健康、安全、超支等风险并制定应对
- 需要在活动前建立应急阈值与决策机制
- 需要把行程方案转化为保障执行的操作计划

---

## 输入/Input

- `experience-brief.md`
- `schedule.md` 或 `itinerary.md`
- `venue-research.md` 或 `destination-research.md`
- resource baseline（预算、供应商、库存、人力）
- 可选：历史事故记录、保险条款、组织安全政策

---

## 输出/Output

- `logistics-plan.md`
- `risk-contingency.md`

---

## 工作流/Workflow

1. 解析日程中的关键节点，列出交通、住宿、设备、物资、许可等物流需求。
2. 建立物流任务清单：负责人、截止时间、依赖关系与验收标准。
3. 识别风险事件并分级，区分可控风险（controllable）与不可控风险（uncontrollable）。
4. 为高优先级风险定义触发条件、监测信号、响应动作与升级路径。
5. 设计资源冗余与回退方案（替代供应商、替代交通、预算缓冲、备用场地）。
6. 校验计划可执行性：人力负载、预算占用、时序冲突、许可合规。
7. 生成`logistics-plan.md`与`risk-contingency.md`，并为`event-runbook-writer`提供执行输入。

---

## 质量门禁/Quality Gates

- 物流清单必须覆盖关键活动节点的全部资源依赖。
- 每项高风险事件必须包含触发条件、响应步骤与责任人。
- 风险分类必须显式区分controllable与uncontrollable并采用不同策略。
- 必须至少定义1条预算超支应对路径与1条活动取消应对路径。
- 合规项（许可、安全、保险）必须有状态标记与截止时间。
- 输出必须可被`event-runbook-writer`直接转为执行清单。

---

## Gotchas/注意事项

- 不要把所有风险都当成同一类型处理，必须区分可控与不可控风险。
- 不要只列“可能发生什么”，要明确“何时触发、谁来响应、怎么收敛”。
- 不要忽视供应商单点故障，关键资源应有替代来源。
- 不要遗漏许可、保险与安全流程，合规缺口会直接导致活动中断。
- 不要把预算缓冲设为零，活动执行阶段通常会出现临时成本波动。

---

## 关联资源

- `schedule-itinerary-planner`
- `research-evidence-ledger`
- `research-quality-reviewer`
- `event-runbook-writer`
