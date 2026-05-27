---
name: research-synthesis
description: 研究综合分析：将evidence ledger转为主题聚类、对比矩阵、缺口分析、矛盾分析与置信度分级，形成key findings与recommendation options。Use when users ask “综合分析/证据整合/对比方法/形成结论与建议/synthesis matrix”, requiring findings↔evidence traceability and contradiction handling.
compatibility: opencode
license: Apache-2.0
---

## 作用/Purpose

将证据账本中的离散证据综合为结构化的研究发现。通过主题综合、对比矩阵、缺口分析、矛盾分析等方法，识别模式、揭示矛盾、分级置信度，并推导出有证据支撑的建议。

---

## 触发场景/Trigger Scenarios

- 已有证据账本，需要形成主题、模式、矛盾、结论
- 需要将多篇论文/竞品/政策组织成对比矩阵
- 需要从证据推导建议
- 需要对结论进行置信度分级

**Synthesis methods**: Thematic synthesis, Comparative matrix, Gap analysis, Contradiction analysis, Causal chain, Decision matrix, Confidence grading

---

## 输入/Input

- 证据账本（evidence-ledger.jsonl）
- 主张映射（claim-map.md）
- 研究简报（research brief）
- 矛盾记录（contradiction-log.md，可选）

---

## 输出/Output

- `synthesis-matrix.md` — 综合分析矩阵
- `key-findings.md` — 关键发现
- `contradiction-matrix.md`（可选）— 矛盾对比矩阵
- `recommendation-options.md`（可选）— 建议选项

---

## 工作流/Workflow

1. **加载证据账本和主张映射** — 读取 evidence-ledger.jsonl 和 claim-map.md
2. **选择综合方法** — 根据研究类型选择：Thematic synthesis / Comparative matrix / Gap analysis / Contradiction analysis / Causal chain / Decision matrix / Confidence grading
3. **按主题/维度聚类证据** — 将证据归入主题簇或对比维度
4. **识别模式和矛盾** — 发现反复出现的模式，标记矛盾点
5. **对每个发现进行置信度分级** — high / medium / low，注明依据
6. **推导建议并关联证据** — 每条建议必须追溯到具体发现
7. **输出综合矩阵** — 生成 synthesis-matrix.md 和 key-findings.md

---

## 质量门禁/Quality Gates

- 不得隐藏矛盾证据
- 不得将"来源中出现频率高"等同于"重要"
- 区分描述性结论与规范性建议
- 每条建议必须追溯到发现
- 每个发现必须追溯到证据

---

## Gotchas/注意事项

- 综合≠汇总：不是把所有证据罗列出来，而是发现结构和关系
- 矛盾是有价值的发现，不要试图消除或忽略
- 置信度分级要诚实——"证据不足以下结论"本身就是有效结论
- 对比矩阵的维度选择决定了分析质量，花时间在维度设计上
- 避免确认偏误：主动寻找反面证据

---

## 关联资源

- References: `synthesis-patterns.md`, `confidence-grading.md`
