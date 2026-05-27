---
name: planning-technology-assessor
description: 技术评估与采用准备度分析（TRL成熟度、落地可行性、集成复杂度、战略匹配），将技术变量纳入规划决策。Use when the user says "技术评估", "technology assessment", "TRL", "adoption readiness", "integration feasibility", "strategic fit", "技术里程碑", "技术决策门", "maturity matrix", or "technology prioritization".
compatibility: opencode
license: Apache-2.0
---

## 作用/Purpose

评估候选技术在成熟度、可采用性、集成复杂度与战略适配度上的表现，形成可执行的技术决策依据。该skill必须覆盖：
1) 技术成熟度与验证状态评估；
2) 采用与集成条件识别；
3) 在不同情景与政策约束下的战略匹配分析。

输出应支撑路线图阶段决策，而不是技术清单罗列。

---

## 触发场景/Trigger Scenarios

- 用户要求“技术评估 / technology assessment / TRL”
- 需要判断候选技术是否具备采用准备度
- 需要评估技术集成可行性与依赖条件
- 需要在政策约束和情景变化下比较技术路径
- 需要为路线图设定技术里程碑与决策门

---

## 输入/Input

- scenario and policy constraints（来自`planning-scenario-planner`与`planning-policy-researcher`）
- technology candidates（候选技术清单、现状与目标能力）
- integration context（现有系统、流程、人才与预算约束）
- 可选：PoC结果、供应商评估、历史实施复盘

---

## 输出/Output

- `technology-assessment.md`
- `maturity-matrix.md`
- `adoption-readiness.md`

---

## 工作流/Workflow

1. 确定评估目标与技术候选范围，定义成功标准与比较口径。
2. 建立TRL与采用准备度评估框架，明确评分维度和证据要求。
3. 汇总情景与政策输入，识别对技术路径的外部约束条件。
4. 逐项评估技术成熟度、集成复杂度、资源需求与风险暴露。
5. 使用`research-evidence-ledger`登记关键判断证据，区分已验证与待验证项。
6. 形成成熟度矩阵与采用准备度报告，标注关键依赖与阻塞因素。
7. 输出对`planning-roadmap-developer`可直接引用的技术优先级与决策门建议。

---

## 质量门禁/Quality Gates

- 每项技术评估必须包含TRL等级与判定依据。
- 采用准备度需覆盖组织能力、流程、数据、合规与成本维度。
- 集成可行性判断需明确关键依赖与不可行约束。
- 高风险技术路径必须附带缓解方案或替代路径。
- 至少识别1个短期可落地与1个中长期潜力技术选项。
- 输出必须包含可供路线图使用的阶段性决策门定义。

---

## Gotchas/注意事项

- 不要把技术热度当作成熟度或可落地性。
- 不要忽视组织与流程能力不足带来的采用失败风险。
- 不要只评估单点技术，需评估系统集成链路。
- 不要跳过政策与合规约束对技术路线的影响。
- 不要把PoC成功直接外推为规模化部署成功。

---

## 关联资源

- `research-evidence-ledger`
- `research-synthesis`
- `planning-scenario-planner`
- `planning-policy-researcher`
- `planning-roadmap-developer`
