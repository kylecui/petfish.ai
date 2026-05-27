---
name: research-evidence-ledger
description: 证据账本构建与claim映射：把摘录笔记提升为正式证据，分类EXTRACTED/INFERRED/AMBIGUOUS/PROPOSED，标注confidence、矛盾与不确定性，输出claim map。Use when users ask “建立证据链/证据账本/claim mapping/区分事实与推断/矛盾证据”, preparing report-ready evidence.
compatibility: opencode
license: Apache-2.0
---

## 作用/Purpose

将原始摘录笔记和来源材料转化为正式的证据条目，建立结构化的证据账本。每条证据都有明确的类型分类、置信度评级和来源追踪，支持后续的主张映射和矛盾检测，为研究报告提供坚实的证据基础。

---

## 触发场景/Trigger Scenarios

- 已有来源和笔记，需要提取事实、观点、数据、定义作为正式证据
- 需要区分事实与推断、不确定性与建议
- 需要为报告建立证据基础
- 需要主张映射（claim map）展示哪些证据支持哪些结论

**Evidence types**: EXTRACTED (direct from source, needs citation), INFERRED (derived from multiple facts, needs reasoning), AMBIGUOUS (conflicting or insufficient, note uncertainty), PROPOSED (our suggestion/hypothesis, label as recommendation)

---

## 输入/Input

- 来源索引（source index）
- 摘录笔记（excerpt notes）
- 研究简报（research brief，可选）

---

## 输出/Output

- `evidence-ledger.jsonl` — 结构化证据账本（必须）
- `claim-map.md` — 主张-证据映射图（推荐，多条证据时生成）
- `contradiction-log.md` — 矛盾记录（可选，仅存在矛盾证据时生成）
- `uncertainty-log.md` — 不确定性记录（可选，仅存在AMBIGUOUS类型证据时生成）

---

## 工作流/Workflow

1. **读取来源索引和摘录笔记** — 加载已有的 source index 和 excerpt notes
2. **识别候选主张** — 从笔记中提取可以作为证据的陈述
3. **分类证据类型** — EXTRACTED（直接引用，需标注出处）、INFERRED（多事实推导，需说明推理）、AMBIGUOUS（矛盾或不足，需注明不确定性）、PROPOSED（我方建议/假设，标为推荐）
4. **记录来源位置** — 标注 source_id、页码/段落/时间戳
5. **评定置信度** — high / medium / low
6. **识别支持或矛盾证据** — 建立证据间关联
7. **输出主张映射** — 生成 claim-map.md
8. **记录矛盾和不确定性** — 输出 contradiction-log.md 和 uncertainty-log.md

---

## Schema

`evidence-ledger.jsonl` 每行一个 JSON 对象，字段如下：

**Required fields**

- `evidence_id` (string): pattern `EV-\d+`
- `source_id` (string): non-empty
- `claim` (string): non-empty
- `evidence_type` (string): one of `EXTRACTED`, `INFERRED`, `AMBIGUOUS`, `PROPOSED`
- `confidence` (string): one of `high`, `medium`, `low`

**Optional / recommended fields**

- `notes` (string): recommended for `INFERRED`
- `contradicts` (list): recommended for `AMBIGUOUS` as a non-empty list

```json
{"evidence_id":"EV-204","source_id":"SRC-120045","claim":"Weekly index refresh improved retrieval precision by 8% in this benchmark.","evidence_type":"EXTRACTED","confidence":"high","notes":"Result extracted from benchmark table section 4.2","contradicts":["EV-199"]}
```

---

## 质量门禁/Quality Gates

- 每个重要主张必须有 source_id
- INFERRED 必须说明推理依据
- AMBIGUOUS 必须说明矛盾来源或不确定原因
- PROPOSED 不能伪装为事实
- 关键结论需要至少2条独立证据支持，或明确标注"证据不足"

---

## Gotchas/注意事项

- 不要跳过 AMBIGUOUS 分类——承认不确定性比假装确定更有价值
- 矛盾不是错误，是研究发现的一部分
- confidence 评级要基于证据质量而非来源权威性
- 定期运行 `evidence_lint.py` 检查账本完整性
- claim-map 是动态文档，随证据增加持续更新

---

## 关联资源

- Scripts: `evidence_lint.py`
- References: `evidence-taxonomy.md`
- Assets: `evidence-ledger-empty.jsonl`
