---
name: product-user-research
description: 设计并分析用户研究（访谈、问卷、可用性测试、用户画像、用户旅程图），将用户证据转化为产品决策输入。Use when the user says "用户研究", "user research", "访谈设计", "interview guide", "问卷设计", "survey design", "用户画像", "persona", "用户旅程图", "journey map", "usability test", "可用性测试", "PRD洞察", or "路线图洞察".
compatibility: opencode
license: Apache-2.0
---

## 作用/Purpose

将产品问题拆解为可执行用户研究计划，并产出可追溯的洞察结论。该skill必须覆盖：
1) 研究问题定义与决策映射；
2) 研究工具设计与样本招募计划；
3) 证据化分析与persona/journey沉淀。

输出应直接支持产品取舍，而不是停留在“用户反馈摘要”。

---

## 触发场景/Trigger Scenarios

- 用户要求“用户研究 / user research / 访谈设计 / interview guide”
- 需要设计“问卷设计 / survey design / 可用性测试”并定义执行口径
- 需要将研究结果沉淀为用户画像（persona）或用户旅程图
- 团队需回答“哪些用户问题最影响当前产品决策”
- 需要为PRD或路线图提供有证据的用户洞察

---

## 输入/Input

- research brief（研究目标、决策问题、约束）
- target user segments（目标用户分层与筛选条件）
- product context（产品阶段、核心场景、已知风险）
- 可选：既有访谈记录、工单数据、行为日志摘要

---

## 输出/Output

- `interview-guide.md`
- `survey-design.md`
- `user-personas.md`
- `findings-summary.md`

---

## 工作流/Workflow

1. 定义研究问题，并逐条绑定预期产品决策。
2. 选择方法组合（访谈/问卷/可用性测试）并说明适用边界。
3. 设计研究工具：访谈提纲、问卷结构、可用性任务脚本。
4. 制定招募计划：样本分层、筛选标准、样本量与排期。
5. 定义分析框架：编码维度、聚类规则、证据强度标准。
6. 汇总研究发现：区分事实观察、推断、建议与不确定性。
7. 产出 persona 与 journey map，并标注证据来源。
8. 提炼可执行建议，明确对应决策与风险。

---

## 质量门禁/Quality Gates

- 研究问题必须逐条关联到具体产品决策。
- 研究工具中不得出现引导性问题（leading questions）。
- 所有核心发现必须可追溯到原始数据或记录片段。
- persona必须有证据支撑，不得凭空虚构角色画像。
- 至少识别1项关键不确定性并给出补充研究建议。

---

## Gotchas/注意事项

- 不要把“用户一句话反馈”直接当作普遍需求。
- 不要用样本便利性替代样本代表性，应显式说明偏差。
- 问卷题目不要混合多个变量，避免结果不可解释。
- 可用性测试应基于真实任务，不要只做演示式点击。
- persona不是营销文案，必须反映行为模式与目标冲突。

---

## 关联资源

- None (standalone)
