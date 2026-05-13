---
name: planning-stakeholder-analyst
description: 利益相关方分析与参与策略设计（影响力-关注度映射、关系网络、诉求识别），为规划研究建立可执行协同路径。Use when the user says "利益相关方分析", "干系人分析", "stakeholder analysis", "stakeholder map", "影响力-关注度", "influence-interest matrix", "engagement strategy", "engagement plan", "关键决策主体", "诉求冲突", "conflict mapping", or "参与策略".
compatibility: opencode
license: Apache-2.0
---

## 作用/Purpose

识别并结构化分析规划议题中的关键利益相关方，明确其影响力、诉求、风险偏好与互动策略，并形成可执行参与计划。该skill必须覆盖：
1) 关键角色识别与分层；
2) 影响力-关注度与关系网络分析；
3) 参与节奏、沟通策略与冲突缓解方案。

输出应可直接支撑情景规划、政策研究与路线图决策。

---

## 触发场景/Trigger Scenarios

- 用户要求“利益相关方分析 / stakeholder analysis / stakeholder map”
- 需要识别关键决策主体与潜在阻力方
- 需要制定沟通和参与计划（engagement plan）
- 需要评估多方诉求冲突对战略规划的影响
- 需要将组织内外部角色纳入规划证据链

---

## 输入/Input

- planning brief（规划目标、关键决策、治理边界）
- stakeholder candidates（初始角色清单与组织关系）
- decision context（制度约束、资源约束、时间窗口）
- 可选：访谈记录、历史协作冲突、组织架构信息

---

## 输出/Output

- `stakeholder-map.md`
- `engagement-plan.md`

---

## 工作流/Workflow

1. 明确分析边界：议题范围、权责边界与决策周期。
2. 识别并分层利益相关方，区分核心决策者、关键影响者与受影响群体。
3. 构建影响力-关注度矩阵，标注每类角色的优先沟通策略。
4. 分析角色关系与潜在联盟/冲突路径，识别高风险互动点。
5. 使用`research-note-capture`与`research-evidence-ledger`沉淀角色诉求证据。
6. 制定参与计划：沟通目标、频率、机制、责任人与反馈闭环。
7. 输出供`planning-scenario-planner`与`planning-policy-researcher`复用的角色约束与行为假设。

---

## 质量门禁/Quality Gates

- 关键利益相关方覆盖必须完整，不能遗漏高影响角色。
- 每个角色画像需明确诉求、影响力、立场与不确定性。
- 关系与冲突判断必须有证据支撑，不得主观臆测。
- engagement plan需包含明确行动、责任人与时间节奏。
- 至少识别2类潜在冲突并给出缓解策略。
- 输出需包含可供后续情景与政策研究调用的行为假设清单。

---

## Gotchas/注意事项

- 不要把组织头衔等同于真实影响力。
- 不要忽视“低权力高受影响”群体的执行阻力。
- 不要将单次访谈意见直接泛化为群体共识。
- 不要只做静态映射，需考虑角色立场随时间变化。
- 不要缺失反馈闭环，否则参与计划难以迭代。

---

## 关联资源

- `research-note-capture`
- `research-evidence-ledger`
- `research-synthesis`
- `planning-environment-scanner`
- `planning-scenario-planner`
