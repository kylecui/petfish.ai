---
name: conference-adapter
description: 为会议/研讨会场景补充CFP截止、讲者管理、AV与直播录制、注册胸牌、赞助履约、并行议程与会后proceedings检查清单，不复制主流程。Use when the user says "会议筹备", "conference planning", "研讨会组织", "workshop planning", "CFP", "speaker management", "keynote", "panel", "poster", "直播录制", or "帮我办一场会议".
compatibility: opencode
license: Apache-2.0
metadata:
  version: "0.11.1"
  author: "petfish-team"
---

## 作用/Purpose

本skill是轻量adapter，不复制主研究流程。

它仅为会议/研讨会类体验活动补充领域字段、约束条件与执行检查清单，强化experience-event主链路在会务组织场景下的可执行性。

本skill不替代主流程，只负责结构化补充并路由到对应research-mode skills。

---

## 触发场景/Trigger Scenarios

- 用户要求“会议筹备 / conference planning / 研讨会组织 / workshop planning”
- 需要管理CFP/投稿截止、讲者邀约、会场AV与直播录制
- 需要规划注册报到、胸牌系统、赞助包与社交活动
- 需要协调多会场并行议程（keynote/panel/workshop/poster）
- 需要产出会后材料（回放、摘要、proceedings）

---

## 输入/Input

- conference brief（会议目标、受众规模、日期与预算）
- conference type（academic/industry/internal）
- program constraints（议程时长、并行分会、会场容量、合规要求）
- optional context（既有讲者名单、赞助级别、历史活动复盘）

---

## 输出/Output

- `conference-domain-fields.md`
- `conference-ops-checklist.md`
- `conference-routing-plan.md`
- `conference-verification-log.md`

---

## 工作流/Workflow

1. 明确会议目标与会议类型，映射到experience-event主链路的统一输入结构。
2. 补充会务领域字段：CFP/投稿节点、讲者管理、AV技术要求、注册胸牌、赞助体系、会后论文集与回放。
3. 定义关键约束：session形式（keynote/panel/workshop/poster）、并行场地冲突、录制与直播合规边界。
4. 生成会务检查清单，覆盖讲者沟通、技术彩排、报到流程、赞助交付与现场运营。
5. 路由到research-mode skills：experience-brief-framer → venue-destination-research → schedule-itinerary-planner → logistics-risk-planner → event-runbook-writer。
6. 记录独立确认项（讲者档期、技术设备、直播链路、版权授权）并附验证时间。

---

## 质量门禁/Quality Gates

- 会议类型、受众规模、议程结构与预算边界必须完整定义。
- CFP/讲者/注册/AV四类关键路径必须有明确负责人与时间节点。
- 会务检查清单必须覆盖会前彩排、会中应急、会后归档三个阶段。
- 路由链路必须显式保留experience-event主流程顺序。
- 所有高时效运营信息必须带验证日期与状态。

---

## Gotchas/注意事项

- 讲者可用性与技术搭建必须独立确认，不能仅依据初始意向。
- 并行议程常出现人流与场地冲突，需提前做峰值容量校验。
- 直播录制涉及版权与肖像授权，必须在会前完成合规确认。
- 不要把赞助承诺视为已交付，需逐项核验物料和权益履约。
- 会后proceedings与回放发布时间要与审稿/编辑排期对齐。

---

## 关联资源

- experience-brief-framer
- venue-destination-research
- schedule-itinerary-planner
- logistics-risk-planner
- event-runbook-writer
