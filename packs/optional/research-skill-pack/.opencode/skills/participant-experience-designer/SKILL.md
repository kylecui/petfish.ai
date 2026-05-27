---
name: participant-experience-designer
description: 从参与者视角优化活动全流程体验，设计attendee journey触点、痛点缓解、互动机制与体验指标，覆盖Before到After阶段。Use when the user says "参与者体验", "participant experience", "用户旅程", "attendee journey", "体验设计", "参会体验", "触点优化", "体验指标", "journey mapping", "痛点识别", "互动设计", "体验风险", "体验检查清单", "开场体验", "转场体验", "收尾体验", or "体验连贯性".
compatibility: opencode
license: Apache-2.0
metadata:
  version: "0.11.1"
  author: "petfish-team"
---

## 作用/Purpose

将活动目标与日程安排转化为参与者旅程设计，确保“前中后”体验连续、可感知、可执行。该skill必须覆盖：
1) 参与者全旅程触点建模；
2) 关键时刻体验风险与优化动作设计；
3) 体验指标与改进闭环定义。

输出应能直接指导活动执行优化，而不是停留在体验口号。

---

## 触发场景/Trigger Scenarios

- 已有活动brief与日程，需要以参与者视角优化体验
- 需要绘制attendee journey并识别痛点
- 需要提升开场、互动、转场与收尾的体验连贯性
- 需要为执行团队提供体验检查清单
- 需要在活动前预演并降低现场体验风险

---

## 输入/Input

- event brief（来自`experience-brief-framer`）
- schedule/itinerary（来自`schedule-itinerary-planner`）
- participant profile（角色类型、期望、限制条件）
- 可选：历史活动反馈、NPS数据、投诉记录

---

## 输出/Output

- `participant-journey.md`

---

## 工作流/Workflow

1. 解析活动目标与参与者画像，定义核心体验目标与优先级。
2. 建立旅程阶段：Before、Arrival、Opening、Main Flow、Breaks、Interaction、Closing、After。
3. 为每阶段识别关键触点，标注期望感受、行为目标与支持资源。
4. 识别摩擦点与失败场景，设计预防动作与现场补救策略。
5. 定义互动机制与信息引导，优化节奏、转场与参与负担。
6. 设定可观测体验指标（到场率、参与率、满意度、留存反馈等）。
7. 输出`participant-journey.md`，并标注下一步交接到`logistics-risk-planner`。

---

## 质量门禁/Quality Gates

- 必须覆盖8个旅程阶段（Before至After）且每阶段至少1个触点。
- 每个触点必须包含“期望体验 + 执行动作 + 责任角色”。
- 至少识别5个潜在摩擦点并给出对应缓解方案。
- 必须定义至少4项可观测体验指标及采集方式。
- 关键阶段（Arrival/Opening/Main Flow/Closing）必须有应急替代方案。
- 输出必须与既有日程一致，不得出现时间冲突或角色冲突。

---

## Gotchas/注意事项

- 不要只优化“主会场”，忽略报到、转场与会后触点。
- 不要把组织者视角当成参与者视角，需按参与者任务流设计。
- 不要只写“提升体验”，必须拆到可执行动作。
- 不要忽略信息密度与认知负担，过载会显著拉低体验。
- 不要缺失异常预案，体验设计必须考虑现场波动。

---

## 关联资源

- `experience-brief-framer`
- `schedule-itinerary-planner`
- `logistics-risk-planner`
- `event-runbook-writer`
