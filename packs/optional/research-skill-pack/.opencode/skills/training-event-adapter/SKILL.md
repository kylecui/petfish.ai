---
name: training-event-adapter
description: 为培训与工作坊场景补充学习目标映射、学员前置条件、实验环境、讲师材料、考核认证、出勤追踪与反馈闭环检查清单，不复制主流程。Use when the user says "培训安排", "training workshop", "课程交付", "workshop delivery", "实训营", "lab training", "学习目标", "认证考核", "实验环境", or "帮我组织一次培训活动".
compatibility: opencode
license: Apache-2.0
---

## 作用/Purpose

本skill是轻量adapter，不复制主研究流程。

它仅为培训/工作坊交付场景补充领域字段、约束条件与执行检查清单，确保experience-event链路与学习目标链路在同一方案中一致。

本skill不独立替代培训设计流程，而是负责结构化增强并路由到对应research-mode skills。

---

## 触发场景/Trigger Scenarios

- 用户要求“培训安排 / training workshop / 课程交付 / workshop delivery”
- 需要把学习目标与活动日程、实验任务、评估机制做一一映射
- 需要规划学员前置条件、实验环境准备与讲师授课提示
- 需要组织认证考核、出勤追踪与课后跟进闭环
- 需要降低培训现场因环境问题导致的交付失败风险

---

## 输入/Input

- training brief（培训目标、受众画像、时长、预算、地点）
- learning objectives（可衡量学习目标与能力等级）
- trainee prerequisites（学员前置知识、设备条件、账号权限）
- optional context（历史培训问题、现有教材、题库与认证规则）

---

## 输出/Output

- `training-domain-fields.md`
- `training-delivery-checklist.md`
- `training-routing-plan.md`
- `training-verification-log.md`

---

## 工作流/Workflow

1. 明确培训交付目标，并将活动目标与学习目标进行映射对齐。
2. 补充培训领域字段：学员前置条件、实验环境、材料准备、讲师注记、评估认证、反馈收集、跟进行动、出勤追踪。
3. 标注硬约束：环境可用性、账号权限、设备规格、时间配比与班级容量。
4. 生成培训交付检查清单，覆盖课前准备、课中控制、课后评估与跟进。
5. 路由到research-mode skills：experience-brief-framer + learning-goal-framer → venue-destination-research → schedule-itinerary-planner → logistics-risk-planner → event-runbook-writer。
6. 对实验环境、评估规则、物料版本与讲师分工执行预演验证并记录时间戳。

---

## 质量门禁/Quality Gates

- 学习目标必须与课程环节、实验任务和评估项建立映射关系。
- 学员前置条件与环境依赖必须显式列出并可检查。
- 交付检查清单必须覆盖课前/课中/课后三阶段并指定责任人。
- 路由计划必须同时包含experience-event与learning链路入口。
- 环境验证记录必须有测试日期、版本与结果结论。

---

## Gotchas/注意事项

- 实验环境必须在活动前完成测试，培训中环境失败通常是灾难性风险。
- 不要假设学员设备与网络一致，应设置最低兼容基线与备用方案。
- 讲师材料与学员材料应严格分离，避免答案或内部提示误发。
- 认证与考核规则需提前公示，避免现场争议影响交付秩序。
- 课后跟进若无时间点与责任人，反馈闭环通常无法落地。

---

## 关联资源

- experience-brief-framer
- learning-goal-framer
- venue-destination-research
- schedule-itinerary-planner
- logistics-risk-planner
- event-runbook-writer
