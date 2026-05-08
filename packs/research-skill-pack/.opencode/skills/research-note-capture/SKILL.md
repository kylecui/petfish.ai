---
name: research-note-capture
description: 摘录笔记捕获，记录原文摘录、出处位置、转述与“为什么重要”，避免过早综合结论。Use when reading sources and you need to capture key excerpts with provenance, location, paraphrase, and why-it-matters before synthesis or final claims.
compatibility: opencode
license: Apache-2.0
---

## 作用/Purpose

把阅读过程沉淀为可追溯证据笔记，保障“原文—位置—解释—用途”链条完整，为后续证据账本与结论写作提供基础。

## 触发场景/Trigger Scenarios

- 用户说“帮我读这篇文章并摘录重点”。
- 用户要求记录“有价值的原文和出处”。
- 用户上传 PDF/DOC/网页并要求阅读笔记。
- 用户明确要求“先摘录，不要太快总结”。
- 阅读中发现关键定义、数据、方法或判断依据。

## 输入/Input

- `source_id` 与来源元信息。
- 文本载体与访问信息（版本、访问方式、页码/章节能力）。
- 研究问题或关注标签（可选）。

## 输出/Output

- `excerpt-notes.jsonl`
- `reading-notes/SRC-XXXXXX.md`
- `quote-bank.md`

## 工作流/Workflow

1. 确认 `source_id` 与版本信息。
2. 记录访问方式与可追溯元数据。
3. 按章节/主题分块阅读。
4. 抽取关键原文片段。
5. 记录位置（page/section/paragraph）。
6. 编写 `paraphrase`（转述，不改写原意）。
7. 编写 `why_it_matters`（与研究问题的关联）。
8. 添加 `tags` 与 `related_questions`。
9. 可选同步至 `quote-bank.md`。
10. 如摘录支持正式主张，移交至 `research-evidence-ledger`。
11. 使用 `note_lint.py` 做记录规范检查，并参照 `excerpt-note-method.md`、`excerpt-notes-empty.jsonl`、`reading-note-template.md`。

## Schema

`excerpt-notes.jsonl` 每行一个 JSON 对象，字段如下：

**Required fields**

- `note_id` (string): pattern `NOTE-\d+`
- `source_id` (string): non-empty
- `original_text` (string): non-empty
- `location` (object): at least one key (e.g. `{"page": 5, "section": "3.1"}`)

**Optional / recommended fields (warnings if missing)**

- `paraphrase` (string)
- `why_it_matters` (string)

```json
{"note_id":"NOTE-89","source_id":"SRC-120045","original_text":"Index staleness strongly correlates with retrieval errors in weekly release cycles.","location":{"page":5,"section":"3.1"},"paraphrase":"Weekly release cadence may require more frequent index refresh to avoid stale retrieval.","why_it_matters":"Directly informs refresh policy design for the target system."}
```

## 质量门禁/Quality Gates

- 每条摘录必须有 `source_id`。
- 直接引用必须有精确位置。
- 必须区分 `original_text` 与 `paraphrase`。
- 每条摘录必须有 `why_it_matters`。
- 不得整篇复制原文进入笔记。
- 不得把摘要伪装成原始证据。

## Gotchas/注意事项

- 摘录阶段不做综合结论。
- 转述要忠实原意，避免主观增删。
- 位置字段缺失会导致证据不可复核。
- 片段要“最小充分”，避免冗长抄录。
