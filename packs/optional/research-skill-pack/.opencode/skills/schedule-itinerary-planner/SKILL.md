---
name: schedule-itinerary-planner
description: 基于activity brief与场地研究设计可执行日程/行程，平衡活动密度、转场缓冲、休息餐食与A/B备选方案。Use when the user says "行程安排", "行程规划", "itinerary", "itinerary planning", "agenda", "日程设计", "schedule planning", "活动流程", "event agenda", "多天活动", "会议议程", "trip route", "帮我排时间", or "plan the day".
compatibility: opencode
license: Apache-2.0
---

## 作用/Purpose

将活动目标和地点条件转化为有时间颗粒度的执行计划，确保节奏、体验与可行性平衡。该skill必须覆盖：
1) 主流程时间块设计；
2) 转场、休息、餐食与缓冲管理；
3) 备选路径与天气应对方案。

输出应能直接用于执行与沟通，而不是概念性“活动流程图”。

---

## 触发场景/Trigger Scenarios

- 用户要求“行程安排 / itinerary planning / 日程设计 / schedule planning”
- 需要把场地候选转化为小时级活动安排
- 需要设计多天活动、会议议程或旅行线路
- 需要平衡活动密度与参与者体力负荷
- 需要准备天气变化或档期变动的替代安排

---

## 输入/Input

- `experience-brief.md`
- `venue-research.md` 或 `destination-research.md`
- date and duration（活动日期、天数、起止时段）
- participant needs（体力、作息、饮食、无障碍）
- 可选：交通时刻表、活动资源预订窗口、供应商服务时段

---

## 输出/Output

- `schedule.md` 或 `itinerary.md`

---

## 工作流/Workflow

1. 读取brief与场地研究结论，确认目标活动、地点约束与优先级。
2. 按天/半天拆分时间块，先放置不可移动的关键活动。
3. 设计转场与缓冲：为跨地点移动预留交通时间与迟到容错。
4. 插入休息、餐食、社交与恢复段，控制连续高强度时长。
5. 为关键时段制定A/B备选方案，覆盖天气与场地临时变化。
6. 校验节奏平衡、地点连贯性与参与者可承受强度。
7. 输出`schedule.md`或`itinerary.md`，并标注供`logistics-risk-planner`使用的物流需求点。

---

## 质量门禁/Quality Gates

- 日程必须覆盖全部关键目标活动，且每项活动有明确时间窗口。
- 跨地点安排必须包含可验证的转场时间，不得假设“即时到达”。
- 每半天至少设置1个缓冲或恢复节点，避免持续超负荷。
- 餐食与休息安排必须匹配参与者约束（饮食、健康、无障碍）。
- 至少为2个关键环节提供可执行备选方案（天气/场地变化）。
- 输出必须标注物流依赖与风险点，便于下游`logistics-risk-planner`接续。

---

## Gotchas/注意事项

- 不要忽略地点之间的真实交通时间，应考虑高峰期、排队和安检因素。
- 不要把所有高价值活动集中在同一时段，避免执行失败导致整体崩盘。
- 不要省略餐食与恢复时间，尤其是全天或多天活动场景。
- 不要只做单一路径计划，至少保留关键节点的可替代安排。
- 不要用理论最佳节奏替代参与者真实耐受度，应留出冗余。

---

## 关联资源

- `experience-brief-framer`
- `venue-destination-research`
- `research-evidence-ledger`
- `logistics-risk-planner`
