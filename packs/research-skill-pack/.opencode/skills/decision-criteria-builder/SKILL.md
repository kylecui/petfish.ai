---
name: decision-criteria-builder
description: 构建带权重的决策标准与比较口径，明确must-have/nice-to-have/deal-breaker并定义评分与证据规则。Use when the user says "决策标准", "decision criteria", "评判维度", "筛选条件", "比较口径", "权重", "weighting", "must-have", "nice-to-have", "一票否决", "团队分歧", "what matters most", or "criteria baseline".
compatibility: opencode
license: Apache-2.0
---

## 作用/Purpose

将决策简报中的约束与偏好转换为可计算、可审计的标准体系，确保后续比较有一致口径。该skill必须覆盖：
1) 标准定义与分类（must/nice/deal-breaker）；
2) 权重与评分尺度设计；
3) 证据需求与裁决规则定义。

输出应支持矩阵比较与复核，而不是抽象偏好清单。

---

## 触发场景/Trigger Scenarios

- 已有`decision-brief.md`，需要建立比较口径
- 团队对“什么最重要”存在分歧
- 需要将偏好转化为可量化权重
- 需要先筛掉明显不合格选项
- 需要为`option-comparison-matrix`提供标准输入

---

## 输入/Input

- `decision-brief.md`
- constraints and priorities（业务、技术、合规、成本优先级）
- scoring preference（评分区间、是否允许加权）
- 可选：历史决策记录与失败案例

---

## 输出/Output

- `criteria.md`

---

## 工作流/Workflow

1. 解析`decision-brief.md`，提取必须项、偏好项与底线项。
2. 定义标准树：一级标准、子标准、指标口径与可验证证据。
3. 将标准分类为must-have、nice-to-have与deal-breaker。
4. 设计权重分配规则，确保总权重归一且与业务优先级一致。
5. 定义评分尺度与评分说明，降低主观打分漂移。
6. 设定淘汰规则：触发deal-breaker即终止进入总分比较。
7. 输出`criteria.md`并交接到`option-comparison-matrix`。

---

## 质量门禁/Quality Gates

- 每条标准必须有明确定义与可采证据来源。
- must-have与deal-breaker不得混淆，需分别定义判定规则。
- 权重总和必须满足既定归一化要求。
- 评分尺度必须统一并附评分解释示例。
- 至少包含1项风险或不确定性相关标准。
- 标准数量应可执行，避免过多导致评估失真。

---

## Gotchas/注意事项

- 不要先定结论再反向拼接标准。
- 不要把不可测的抽象词直接作为评分项。
- 不要忽略deal-breaker对候选淘汰的优先级。
- 不要让权重只反映声音大小而非业务影响。
- 不要省略评分说明，否则团队复评不可复现。

---

## 关联资源

- `decision-brief-framer`
- `option-comparison-matrix`
- `research-evidence-ledger`
- `research-synthesis`
