---
name: research-insight-log
description: 灵感、假设、类比、问题和研究构想记录器。保存"尚未证明但可能重要"的研究想法及其触发来源和验证路径。Use when capturing ideas, analogies, hypotheses, questions, or research hunches during reading that are not yet proven but may be valuable for the research.
compatibility: opencode
license: Apache-2.0
---

## 作用/Purpose

在研究过程中捕获灵感闪现、跨领域类比、未验证假设、研究缺口和潜在贡献点。这些想法尚未经过验证，但可能对研究方向、论文贡献、产品机会或规划判断有重要价值。通过结构化记录，避免灵感丢失，并为后续验证提供清晰路径。

---

## 触发场景/Trigger Scenarios

- 用户说"我突然想到…"或"记一下这个想法"
- Agent在阅读多个来源时发现跨源连接
- 发现潜在研究缺口、论文贡献点、产品机会或规划判断
- 某个概念可以迁移到另一领域
- 用户希望保留一个想法但暂不展开

---

## 输入/Input

- 用户口述的想法或Agent发现的连接
- 触发来源：source_ids、note_ids、当前上下文
- 想法分类提示（可选）

**Insight types**: analogy, hypothesis, research-question, method-idea, experiment-idea, product-opportunity, planning-judgment, contradiction, terminology, writing-angle

---

## 输出/Output

- `insight-log.jsonl` — 结构化灵感记录（每行一条JSON）
- `idea-inbox.md` — 人类可读的想法收件箱

---

## 工作流/Workflow

1. **捕获灵感** — 用清晰标题记录核心想法
2. **分类** — 确定 insight_type（analogy, hypothesis, research-question, method-idea, experiment-idea, product-opportunity, planning-judgment, contradiction, terminology, writing-angle）
3. **记录触发来源** — 标注 source_ids、note_ids、触发上下文
4. **描述潜在价值** — 说明 potential_value（为什么这个想法可能重要）
5. **列出验证问题** — needs_validation：要回答哪些问题才能确认/否定
6. **列出可能产出** — possible_outputs：如果验证成功可以产出什么
7. **设置状态** — status 设为 "open"

---

## 质量门禁/Quality Gates

- 必须有标题（title）
- 必须说明触发来源（source/notes/context至少一项）
- 必须说明潜在价值（potential_value）
- 必须列出至少1个验证问题（needs_validation）
- 状态必须为：open, validated, rejected, merged
- 灵感不能未经验证直接作为事实进入报告

---

## Gotchas/注意事项

- 灵感记录≠结论，不要混淆"可能有价值"和"已经证明"
- 记录时宁粗勿漏，后续可以批量清理
- 跨领域类比需要标注原始领域和目标领域
- 定期回顾 idea-inbox，将已验证的提升为证据，将无效的标记为 rejected
- 运行 `insight_lint.py` 检查结构完整性

---

## 关联资源

- Scripts: `insight_lint.py`
- References: `insight-types.md`
- Assets: `insight-log-empty.jsonl`
