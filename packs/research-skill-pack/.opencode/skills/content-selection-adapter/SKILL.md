---
name: content-selection-adapter
description: 为内容选择场景补充偏好画像、可用性、分级限制、群体兼容、口碑聚合、实时场次票价核验与备选方案检查清单，不复制主流程。Use when the user says "内容推荐", "content selection", "看什么电影", "what to watch", "书单选择", "game recommendation", "多人偏好冲突", "场次票价", "可用性", or "帮我选一个展览/演出".
compatibility: opencode
license: Apache-2.0
---

## 作用/Purpose

本skill是轻量adapter，不复制主研究流程。

它仅为娱乐/内容选择场景补充领域字段、约束条件与检查清单，提升decision链路在时效性与群体偏好场景下的决策质量。

本skill不独立完成内容推荐流程，而是将任务路由到相应research-mode skills并补充领域验证要求。

---

## 触发场景/Trigger Scenarios

- 用户要求“内容推荐 / content selection / 看什么电影 / what to watch”
- 需要基于情绪、时长、语言、平台或类型进行内容筛选
- 需要考虑多人同行场景下的偏好冲突与可接受折中方案
- 需要结合分级限制、实时场次/库存与票价进行决策
- 需要在主推荐外给出同条件替代选项

---

## 输入/Input

- selection brief（选择目标、时间窗、预算、个人或群体场景）
- preference profile（genre、mood、duration、language、platform）
- constraints（年龄分级、地域可用性、付费上限、硬性禁忌）
- optional context（历史偏好、已看/已玩清单、黑名单内容）

---

## 输出/Output

- `content-domain-fields.md`
- `content-selection-checklist.md`
- `content-routing-plan.md`
- `content-verification-log.md`

---

## 工作流/Workflow

1. 明确选择目标与场景（个人/群体、娱乐/学习、即时/计划型），映射到decision主链路。
2. 补充内容领域字段：偏好画像、可用性检查、年龄分级、群体兼容、口碑聚合与替代推荐。
3. 定义硬约束与筛选优先级，区分不可违反条件与可协商偏好。
4. 生成内容选择检查清单，覆盖可看性、可买性、可接受性与备选可切换性。
5. 路由到research-mode skills：decision-brief-framer → decision-criteria-builder → option-comparison-matrix → decision-recommendation。
6. 记录时效信息核验（可用性、场次、票价）并标注验证日期和来源渠道类别。

---

## 质量门禁/Quality Gates

- 偏好画像必须至少包含类型、情绪、时长、语言、平台五类字段。
- 分级限制、地域可用性与预算约束必须在比较前完成过滤。
- 比较矩阵必须体现群体兼容度或冲突处理策略（若为多人场景）。
- 路由计划必须明确decision链路顺序，不得由adapter替代主决策流程。
- 所有时效性结果必须记录验证日期。

---

## Gotchas/注意事项

- 可用性、场次与票价具有时间敏感性，必须注明核验日期。
- 评分聚合可能受样本偏差影响，不能单独作为唯一决策依据。
- 多人选择场景要显式处理冲突，不要把单人偏好当群体结论。
- 平台版权与地区限制变化频繁，需做地域与账号维度双重确认。
- 备选方案应保持与主推荐相近约束，避免不可执行的“伪备选”。

---

## 关联资源

- decision-brief-framer
- decision-criteria-builder
- option-comparison-matrix
- decision-recommendation
