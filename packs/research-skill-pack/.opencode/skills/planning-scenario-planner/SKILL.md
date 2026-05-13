---
name: planning-scenario-planner
description: 情景规划与替代未来构建（关键不确定性、情景矩阵、稳健策略），将环境与利益相关方输入转化为战略选项。Use when the user says "情景规划", "scenario planning", "scenario analysis", "alternative futures", "关键不确定性", "scenario matrix", "稳健策略", "robust strategy", "多路径战略", "战略选项", "技术投资情景", or "政策应对情景".
compatibility: opencode
license: Apache-2.0
---

## 作用/Purpose

基于关键不确定性构建多个可辨识的未来情景，分析不同情景下的战略影响，并提出跨情景稳健策略。该skill必须覆盖：
1) 驱动因素与关键不确定性提炼；
2) 情景构建、叙事与一致性校验；
3) 战略含义分析与稳健策略设计。

输出应帮助团队在不确定环境下做前瞻性决策，而不是单一预测。

---

## 触发场景/Trigger Scenarios

- 用户要求“情景规划 / scenario planning / alternative futures”
- 需要围绕高不确定性议题制定多路径战略方案
- 需要评估外部变化与利益相关方行为对未来路径的影响
- 需要识别跨情景都成立的稳健策略
- 需要为技术投资或政策应对提供情景依据

---

## 输入/Input

- environment variables（来自`planning-environment-scanner`的趋势与信号）
- stakeholder assumptions（来自`planning-stakeholder-analyst`的行为约束）
- decision focus（核心决策问题与时间范围）
- 可选：历史情景案例、风险清单、战略假设库

---

## 输出/Output

- `scenario-set.md`
- `implications-matrix.md`
- `robust-strategy-brief.md`

---

## 工作流/Workflow

1. 汇总环境扫描与利益相关方分析结果，建立驱动因素池。
2. 识别关键不确定性并筛选高影响、高不确定组合。
3. 构建2x2或多维情景结构，定义每个情景的核心假设。
4. 编写情景叙事，校验内部一致性与外部可解释性。
5. 评估各情景下的风险、机会、能力缺口与决策触发点。
6. 构建含义矩阵，映射“情景→战略动作→预期结果”。
7. 提炼跨情景稳健策略，并输出给`planning-policy-researcher`与`planning-technology-assessor`进行约束校验。

---

## 质量门禁/Quality Gates

- 情景必须彼此可区分，不能只是同一路径的轻微变化。
- 每个情景必须明确关键假设与触发信号。
- 关键不确定性选择需有证据支撑并解释筛选逻辑。
- 含义矩阵需覆盖至少3类战略动作（防御/进攻/适应）。
- 稳健策略需明确在多个情景下的有效性边界。
- 输出必须显式标注传递给政策研究与技术评估的输入项。

---

## Gotchas/注意事项

- 不要把情景规划做成“最可能未来”的单一路线预测。
- 不要使用互相矛盾却未解释的情景假设组合。
- 不要只写叙事不做策略含义映射。
- 不要忽略低概率高影响事件的扰动作用。
- 不要遗漏情景触发信号，否则无法开展动态更新。

---

## 关联资源

- `planning-environment-scanner`
- `planning-stakeholder-analyst`
- `research-evidence-ledger`
- `planning-policy-researcher`
- `planning-technology-assessor`
