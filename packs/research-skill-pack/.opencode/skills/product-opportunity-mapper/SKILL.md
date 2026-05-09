---
name: product-opportunity-mapper
description: 基于用户证据与竞争格局做问题空间映射，结合JTBD识别、评分并优先级排序产品机会。Use when the user says "机会分析", "opportunity mapping", "JTBD", "Jobs to be Done", "问题空间", "problem space", "机会评估", "opportunity scoring", "需求分析", "需求挖掘", "underserved", "overserved", "优先级矩阵", or "priority matrix".
compatibility: opencode
license: Apache-2.0
---

## 作用/Purpose

将分散的用户痛点与市场信号整理为可决策的机会地图，避免“需求堆砌式”优先级。该skill必须完成：
1) 问题空间结构化建模；
2) JTBD框架化表达与机会识别；
3) 显式评分与优先级决策。

输出应明确哪些机会已验证、哪些仍为假设。

---

## 触发场景/Trigger Scenarios

- 用户提出“机会分析 / opportunity mapping / 问题空间”
- 需要用 JTBD（Jobs to be Done）统一表达用户需求
- 需要机会评分（opportunity scoring）支持路线图排序
- 需要识别 underserved/overserved 区域寻找切入点
- 需要把需求挖掘结果转成可执行优先级矩阵

---

## 输入/Input

- user research findings（用户研究发现与证据）
- competitor analysis（竞品能力与定位分析）
- market context（市场趋势、约束与业务边界）
- 可选：现有产品指标、商业目标与资源限制

---

## 输出/Output

- `opportunity-map.md`
- `jtbd-framework.md`
- `opportunity-scores.md`
- `priority-matrix.md`

---

## 工作流/Workflow

1. 综合用户痛点，提炼高频且高影响问题簇。
2. 将问题重述为JTBD（情境-动机-期望结果）格式。
3. 映射当前解决方案，识别覆盖强弱与替代路径。
4. 标记 underserved/overserved 区域并解释原因。
5. 设计评分模型（价值、可行性、风险、时效等维度）。
6. 对候选机会打分并记录证据与不确定性。
7. 形成优先级矩阵，给出阶段化推进建议。
8. 区分已验证机会与待验证假设，输出验证计划入口。

---

## 质量门禁/Quality Gates

- 每个机会项必须关联至少一条用户证据。
- 评分必须基于显式标准，不得使用隐式主观排序。
- 必须明确区分 validated opportunities 与 hypotheses。
- 优先级结论必须解释权重设置与边界条件。
- 至少识别1项高潜力但高不确定机会并给出验证建议。

---

## Gotchas/注意事项

- 不要把功能请求列表直接当机会地图。
- JTBD描述应指向目标结果，不要退化为功能术语。
- 评分模型不要过度复杂，复杂度应小于决策收益。
- 不要忽视机会间依赖关系，避免局部最优排序。
- 高分不等于立即投入，需结合资源窗口与战略一致性。

---

## 关联资源

- None (standalone)
