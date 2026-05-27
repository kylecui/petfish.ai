---
name: venue-destination-research
description: 研究并评估城市/酒店/会场/景点候选，覆盖可达性、容量、成本、设施、安全、天气与法规许可，输出推荐/备选/淘汰清单。Use when the user says "场地调研", "venue research", "目的地选择", "destination research", "活动地点", "event location", "选酒店", "合适的场地", "去哪里", "where should we go", "许可要求", or "weather risk".
compatibility: opencode
license: Apache-2.0
---

## 作用/Purpose

围绕活动brief对候选场地或目的地进行结构化研究与对比，输出可执行的选址依据。该skill必须覆盖：
1) 候选集构建与筛选逻辑；
2) 多维评估（可达性、容量、成本、设施、安全、天气、法规）；
3) 证据化对比与推荐结论。

输出应支持明确的选址决策，而不是“地点罗列”。

---

## 触发场景/Trigger Scenarios

- 用户要求“场地调研 / venue research / 目的地选择 / destination research”
- 需要评估多个城市、酒店、会场或景点作为活动承载地点
- 需要比较容量、价格、设施、交通与评价差异
- 需要确认地方政策、许可要求、季节天气与安全风险
- 需要为后续行程设计提供地点输入

---

## 输入/Input

- `experience-brief.md`
- 候选范围（城市、区域、场地类型、半径限制）
- participant constraints（行动便利性、预算、时间、语言或文化约束）
- evaluation criteria（容量、交通、成本、服务、可用性）
- 可选：历史活动场地反馈、供应商名单、合同模板

---

## 输出/Output

- `venue-research.md` 或 `destination-research.md`

---

## 工作流/Workflow

1. 读取`experience-brief.md`并提炼必须满足的选址约束与评分维度。
2. 构建候选池，按地理范围、类型、预算区间进行初筛。
3. 对每个候选收集关键信息：可达性、容量、费用结构、设施与服务。
4. 补充外部风险信息：天气模式、安全情况、本地法规与许可要求。
5. 建立对比矩阵，区分硬性淘汰条件与加分项，形成分层候选名单。
6. 标注需要外部确认的条目（实时档期、实时价格、合同条款）并给出验证动作。
7. 生成`venue-research.md`或`destination-research.md`，作为`schedule-itinerary-planner`的输入。

---

## 质量门禁/Quality Gates

- 所有候选必须满足brief中的硬约束，否则应明确标记为淘汰。
- 对比矩阵至少覆盖可达性、容量、成本、设施、安全、法规6个维度。
- 关键结论必须附来源说明，不得仅基于主观印象。
- 必须明确“推荐候选 + 备选候选 + 淘汰理由”三类结果。
- 必须显式标注实时可用性与实时价格的外部核验状态。
- 输出必须可被`schedule-itinerary-planner`直接读取并落地到时间安排。

---

## Gotchas/注意事项

- 实时可用性与实时价格会快速变化，必须通过外部渠道二次核验，不能仅依赖历史信息。
- 不要只看场地租金，应纳入税费、服务费、加班费与隐性成本。
- 不要忽略到达链路（机场/车站/地铁/停车）对整体体验的影响。
- 不要用网络评分替代实地或供应商核查，评论数据可能存在偏差。
- 不要忽视地方政策与许可门槛，尤其是公开活动与跨区域参与场景。

---

## 关联资源

- `experience-brief-framer`
- `research-source-discovery`
- `research-evidence-ledger`
- `schedule-itinerary-planner`
