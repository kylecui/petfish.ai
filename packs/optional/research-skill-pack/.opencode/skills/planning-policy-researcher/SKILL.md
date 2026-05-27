---
name: planning-policy-researcher
description: 政策与监管研究（法规版图、政策趋势、合规要求、政策影响评估），将制度约束转化为战略规划输入。Use when the user says "政策研究", "policy research", "policy analysis", "法规分析", "regulatory landscape", "compliance", "policy trend", "法规影响", "监管风险", "regulatory risk", "政策边界", "窗口期", or "policy shock".
compatibility: opencode
license: Apache-2.0
---

## 作用/Purpose

系统分析规划议题相关的政策与监管环境，识别合规要求、政策趋势与制度性风险，并输出对战略路径的约束与机会。该skill必须覆盖：
1) 法规版图梳理与适用范围识别；
2) 政策变化趋势与监管信号跟踪；
3) 合规风险与战略影响评估。

输出应支持情景与技术评估环节，而不是停留在法规摘抄。

---

## 触发场景/Trigger Scenarios

- 用户要求“政策研究 / policy analysis / regulatory landscape”
- 需要判断法规变化对战略可行性的影响
- 需要识别合规要求与监管风险清单
- 需要为情景规划补充政策变量与政策冲击
- 需要在路线图制定前明确政策边界与窗口期

---

## 输入/Input

- planning scope（地域、行业、业务边界）
- scenario inputs（来自`planning-scenario-planner`的情景假设）
- environment inputs（来自`planning-environment-scanner`的外部趋势）
- 可选：历史政策变迁记录、合规事件、法律顾问意见

---

## 输出/Output

- `policy-landscape.md`
- `regulatory-risk.md`
- `policy-brief.md`

---

## 工作流/Workflow

1. 定义政策研究范围与法域边界，明确适用监管层级。
2. 建立法规与政策来源清单，区分强制规范与指导性政策。
3. 抽取与规划议题相关的核心条款、义务、限制与窗口期。
4. 结合情景输入评估不同政策走向下的战略影响与暴露风险。
5. 使用`research-evidence-ledger`记录法规证据与解释依据，标注不确定条款。
6. 构建监管风险矩阵，分级呈现概率、影响与应对优先级。
7. 形成政策简报，并输出供`planning-technology-assessor`与`planning-roadmap-developer`调用的约束条件。

---

## 质量门禁/Quality Gates

- 法规来源必须合法、可追溯，并标注发布日期与法域。
- 必须区分“已生效要求”与“拟议/征求意见政策”。
- 每项高风险合规点需有明确影响路径与责任对象。
- 监管风险矩阵需包含严重度、发生可能性与应对动作。
- 至少识别2个政策不确定性并给出监测建议。
- 输出需明确可供技术评估与路线图规划复用的政策约束。

---

## Gotchas/注意事项

- 不要将二手解读替代原始法规文本。
- 不要忽略地方性或行业专项监管差异。
- 不要把“未明确禁止”误判为“可执行无风险”。
- 不要只给政策描述而缺少对战略动作的影响映射。
- 不要忽略政策时间窗口对路线安排的约束。

---

## 关联资源

- `research-source-discovery`
- `research-evidence-ledger`
- `planning-scenario-planner`
- `planning-technology-assessor`
- `planning-roadmap-developer`
