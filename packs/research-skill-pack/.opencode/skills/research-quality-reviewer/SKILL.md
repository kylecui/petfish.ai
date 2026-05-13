---
name: research-quality-reviewer
description: 研究报告独立质审：检查证据覆盖、引用完整性、逻辑链、反面证据、方法匹配、可执行建议、风险披露与AI腔（AI slop），给出发布前评级。Use when users ask “报告审查/quality review/发布前检查/check my report/citations/AI腔检测”.
compatibility: opencode
license: Apache-2.0
---

## 作用/Purpose

作为独立审查者，对研究报告进行多维度质量评估。检查证据覆盖率、逻辑链完整性、引用完整性、反面证据讨论、方法适配性、建议可操作性、表达质量和风险披露，给出整体评级和改进建议。

---

## 触发场景/Trigger Scenarios

- 研究报告准备接受审查
- 需要检查证据覆盖和引用完整性
- 需要检测AI生成的空洞表达、无根据主张或修辞填充
- 需要发布前的质量评级
- 需要验证从证据到发现到建议的逻辑链

---

## 输入/Input

- 研究报告（report.md）
- 证据账本（evidence-ledger.jsonl）
- 研究简报（research brief）
- 综合分析（可选）

---

## 输出/Output

- `quality-review.md` — 多维度质量审查报告
- `ai-slop-review.md` — AI表达质量检查报告

---

## 工作流/Workflow

1. **加载报告、证据账本、简报** — 确认审查材料完整
2. **逐维度检查** — 按9个审查维度逐项评估
3. **评分** — 每个维度评为 pass / partial / fail
4. **识别阻断问题** — 标记必须修复才能发布的问题
5. **生成整体评级** — A / B / C / D / F
6. **列出改进建议** — 按优先级排列
7. **运行AI腔检查** — 检测空洞表达和修辞填充

---

## 审查维度/Review Dimensions

1. **question-alignment** — 报告是否回答了所有研究问题？
2. **evidence-completeness** — 关键主张是否有 evidence_id 引用？
3. **citation-coverage** — 事实性主张是否有行内引用？
4. **logic-chain** — 发现到建议之间是否有逻辑跳跃？
5. **counter-evidence** — 矛盾来源是否被讨论？
6. **method-fit** — 综合方法是否适合研究类型？
7. **actionability** — 建议是否包含优先级和条件？
8. **expression-quality** — 是否有无依据的最高级或模糊主张？
9. **risk-disclosure** — 局限性和数据时效性是否覆盖？

---

## 质量门禁/Quality Gates

- 审查者必须独立于撰写者（生成和审查分离）
- 阻断问题必须在发布前解决
- C级及以下需要修订
- AI腔指标："increasingly important", "in today's rapidly evolving", "it is worth noting", "comprehensive and robust" without evidence

---

## Gotchas/注意事项

- 审查≠挑刺：目标是提升报告质量，不是否定工作
- 生成和审查必须分离——不能自己写自己审
- partial 不是"差不多行了"，而是"有具体改进空间"
- AI腔检查不是文字游戏——核心是每个修饰词是否有证据支撑
- 评级要给出具体理由，不能只给字母

---

## 关联资源

- Scripts: `report_quality_gate.py`
- References: `quality-gates.md`, `ai-slop-checklist.md`
