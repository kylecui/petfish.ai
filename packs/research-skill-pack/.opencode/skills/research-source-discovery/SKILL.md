---
name: research-source-discovery
description: 发现、筛选并登记研究来源，建立结构化source index并评估来源质量。Use when you need to find papers, official docs, competitor materials, policy documents, industry reports, datasets, or user feedback and register them in a structured source index.
compatibility: opencode
license: Apache-2.0
---

## 作用/Purpose

为研究建立可追踪的来源底座：先找全、再筛优、后登记，确保后续分析建立在可靠证据上。

## 触发场景/Trigger Scenarios

- 需要查找论文、官方文档、竞品材料、政策文件、行业报告等。
- 需要建立和维护 source index。
- 需要按 authority/relevance/freshness/verifiability/bias/granularity 评估来源质量。

## 输入/Input

- 已结构化的研究brief与问题清单。
- 可选：已有来源线索、排除列表、时间窗口。

## 输出/Output

- `source-index.jsonl`
- `bibliography.bib`
- `search-strategy.md`

## 工作流/Workflow

1. 从brief提取检索目标与关键词策略。
2. 按 source types 检索：official-doc、paper、report、website、code-repo、interview、internal-doc、dataset。
3. 按质量维度过滤与打分（authority/relevance/freshness/verifiability/bias/granularity）。
4. 将通过筛选的来源登记到 `source-index.jsonl`。
5. 同步生成 `bibliography.bib` 与 `search-strategy.md`。
6. 用 `source_index.py` 做索引一致性检查（仅调用脚本名，不嵌入脚本内容）。
7. 对照 `source-quality-rubric.md` 做最终抽检。

## 质量门禁/Quality Gates

- 每条来源必须有 `source_id`、`source_type`、`relevance_rating`。
- 必须有完整检索策略记录（渠道、关键词、过滤规则）。
- 必须覆盖多元来源，不得单一渠道偏置。

## Gotchas/注意事项

- 检索结果标题不能直接当证据。
- 不要只收集支持既有观点的来源。
- 二手博客不能替代官方文档或论文原文。
- source index 不是文献综述阶段，不在此阶段输出结论。
