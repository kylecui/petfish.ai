---
name: research-report-writer
description: 基于research brief、evidence ledger与synthesis写正式研究报告/执行摘要，支持科学研究、产品研究、规划研究、白皮书与提案，确保每个claim可追溯evidence_id并披露方法与局限。Use when users ask “写研究报告/executive summary/白皮书/提案/论文初稿/report writing”.
compatibility: opencode
license: Apache-2.0
---

## 作用/Purpose

将证据账本和综合分析转化为正式的研究报告。支持多种报告类型（科学研究、产品研究、规划研究、白皮书、提案），确保每个主张都有证据追溯，建议与发现分离，并包含方法论说明和局限性披露。

---

## 触发场景/Trigger Scenarios

- 需要生成研究报告、提案、白皮书、论文初稿、产品研究报告、规划报告
- 已有研究简报、证据和分析，准备输出最终文档
- 需要执行摘要（executive summary）

---

## 输入/Input

- 研究简报（research brief）
- 证据账本（evidence-ledger.jsonl）
- 综合分析（synthesis-matrix.md, key-findings.md）
- 报告类型指定（可选）

---

## 输出/Output

- `report.md` — 正式研究报告
- `executive-summary.md` — 执行摘要

---

## 工作流/Workflow

1. **加载简报、证据账本、综合分析** — 确认输入材料完整
2. **选择报告模板** — 根据研究类型选择对应结构
3. **逐节撰写，关联证据** — 每个事实性主张标注 evidence_id
4. **生成执行摘要** — 独立可读，涵盖核心发现和建议
5. **添加局限性和风险披露** — 诚实说明数据边界和方法局限
6. **交叉检查引用完整性** — 确认所有主张都有证据引用

**默认报告结构**:

1. Executive Summary
2. Background and Scope
3. Method
4. Key Findings (each linked to evidence)
5. Analysis
6. Recommendations (each linked to findings)
7. Limitations and Risks
8. References

---

## 质量门禁/Quality Gates

- 每个事实性主张必须引用 evidence_id
- PROPOSED/建议必须明确标注
- 必须包含局限性（Limitations）章节
- 必须包含方法论（Method）章节
- 不得出现"越来越重要"、"广泛认为"等无来源表述
- 执行摘要必须独立可读

---

## Gotchas/注意事项

- 报告是证据的呈现，不是观点的堆砌
- 执行摘要面向决策者，用结论-证据-建议的结构，不要铺垫
- 建议章节要区分"证据支持的建议"和"经验判断的建议"
- 局限性不是形式主义——要具体说明哪些结论受限于哪些数据边界
- 避免AI腔：不用"值得注意的是"、"综合而言"、"全面且稳健"等空洞表达

---

## 关联资源

- Assets: `research-report-template.md`, `executive-summary-template.md`
