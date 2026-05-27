---
name: travel-adapter
description: 为旅行场景补充目的地类型、签证入境、天气季节、本地交通、货币语言、健康保险与跨城/跨国核验清单，不复制主流程。Use when the user says "旅行规划", "trip planning", "旅游攻略", "travel itinerary", "vacation planning", "跨国行程", "签证", "入境政策", "去哪玩", or "帮我安排一次旅行".
compatibility: opencode
license: Apache-2.0
---

## 作用/Purpose

本skill是轻量adapter，不复制主研究流程。

它仅为旅行类体验活动补充领域字段、约束条件与检查清单，用于增强已有experience-event研究链路的输入完整性与落地可靠性。

本skill不单独产出完整方案，而是将任务路由到对应research-mode skills并追加旅行特有校验要求。

---

## 触发场景/Trigger Scenarios

- 用户要求“旅行规划 / trip planning / 旅游攻略 / travel itinerary”
- 需要在目的地选择中加入签证、季节、交通、预算与保险约束
- 需要为跨城市或跨国行程建立可执行且可验证的旅行检查清单
- 需要把“想去哪玩”转化为可路由到experience-event链路的结构化输入
- 需要在活动执行前识别旅行物流和政策变动风险

---

## 输入/Input

- travel brief（出行目标、预算范围、人数与时间窗）
- destination preferences（城市/自然/文化/海滨偏好）
- traveler constraints（签证身份、健康情况、语言能力、可接受转运复杂度）
- optional context（已有候选目的地、酒店/航班偏好、历史出行失败点）

---

## 输出/Output

- `travel-domain-fields.md`
- `travel-constraints-checklist.md`
- `travel-routing-plan.md`
- `travel-verification-log.md`

---

## 工作流/Workflow

1. 识别旅行目标与边界，将核心目标映射为experience-event主链路输入。
2. 补充旅行领域字段：目的地类型、签证入境、天气季节、本地交通、货币语言、健康疫苗、保险与预订时间线。
3. 标注硬约束与软偏好，区分必须满足项（如签证、入境、健康）与可优化项（如便利度、文化体验密度）。
4. 生成旅行检查清单，覆盖证件、资金、沟通、移动、礼仪、应急与取消改签策略。
5. 路由到research-mode skills：experience-brief-framer → venue-destination-research → schedule-itinerary-planner → logistics-risk-planner → event-runbook-writer。
6. 记录需要外部实时核验的项目，并在输出中附验证日期与信息来源类型。

---

## 质量门禁/Quality Gates

- 目的地、时间窗、预算与出行人数四类基础字段必须完整。
- 签证/入境、天气季节、交通衔接三类高风险字段必须有独立核验项。
- 检查清单必须区分“出发前”“行程中”“突发情况”三个阶段。
- 路由计划必须明确主链路skill顺序，不得把adapter当作独立流程替代。
- 所有时效性信息必须标注验证日期。

---

## Gotchas/注意事项

- 实时价格、库存可用性、签证规则与天气信息必须外部核验，agent不能保证旅行物流准确性。
- 不要把单一平台报价视为最终成本，需考虑税费、汇率与隐藏费用。
- 不要忽略目的地节假日、罢工、交通中断等时段性风险。
- 文化礼仪和法律红线应按目的地分别核验，避免通用化假设。
- 跨境医疗与保险条款需要核对适用地区和免责范围。

---

## 关联资源

- experience-brief-framer
- venue-destination-research
- schedule-itinerary-planner
- logistics-risk-planner
- event-runbook-writer
