---
name: research-citation-auditor
description: 引用审计与source verification：逐条核对claim→evidence_id→source_id链路，识别unsupported claims、引用缺口、来源失效/过时、统计口径不一致及“最新/领先/主流/最佳”证据不足。Use when users ask “citation audit/检查引用/引用覆盖/check citations/source verification/unsupported claims”.
compatibility: opencode
license: Apache-2.0
---

## 作用/Purpose

在研究报告发布前执行引用一致性审计：从报告中的关键claim反向追踪到 evidence ledger 和 source index，确认“claim → evidence_id → source_id → accessible location”链条完整、可验证、未过时。重点识别无支持断言、遗漏引用、失效来源、时效性断裂，以及“最新/领先/主流/最佳”类高强度措辞缺乏证据支撑的问题。

---

## 触发场景/Trigger Scenarios

- 用户要求“引用审计 / citation audit / 检查引用 / check citations”
- 报告准备对外提交，需做最终 source verification
- 团队质疑报告是否存在 unsupported claims
- 需要评估引用覆盖率与关键claim证据密度
- 需要专门检查统计、法规、产品特性类陈述是否可追溯且仍有效

---

## 输入/Input

- 研究报告草稿（Markdown或等价结构）
- `evidence-ledger.jsonl`（含 evidence_id、source_id、confidence、location）
- `source-index.jsonl`（含 source_id、url_or_path、published/accessed date、freshness）
- 可选：`claim-map.md`、`contradiction-log.md`、`uncertainty-log.md`

---

## 输出/Output

- `citation-audit.md` — 审计总报告（覆盖率、阻断项、风险项）
- `unsupported-claims.md` — 缺少有效证据映射的claim清单
- `source-coverage.md` — source覆盖统计与失效/过时来源清单

---

## 工作流/Workflow

1. 提取报告中的关键claim并编号（事实、对比、趋势、结论、建议依据）。
2. 对每个claim检查是否映射到至少一个 `evidence_id`。
3. 对每个 `evidence_id` 校验是否能映射到合法 `source_id`。
4. 对每个 `source_id` 校验可访问位置、访问时间、时效状态与版本信息。
5. 对高风险语义词（最新、领先、主流、最佳、业界公认）执行强化核验。
6. 对统计类claim核验日期、样本、范围、口径一致性。
7. 对法规类claim核验生效日期、适用范围、是否已修订/废止。
8. 对产品特性claim核验当前版本与发布日期，避免把历史功能当现状。
9. 输出阻断问题（必须修复）与风险问题（可解释保留）。
10. 参考 `references/citation-policy.md` 做规则一致性对照。

---

## 质量门禁/Quality Gates

- 关键claim必须可追溯到 `evidence_id` 与 `source_id`。
- 关键来源必须可访问（URL可达或本地路径可定位）。
- 统计类claim必须同时说明时间、样本、范围/口径。
- 法规类claim必须说明生效状态与适用边界。
- 产品特性claim必须验证当前版本，不得使用过时版本宣传页替代。
- 对“最新/领先/主流/最佳”类断言，若证据不足则降级措辞或标记unsupported。

---

## Gotchas/注意事项

- 不要把“有引用”误判为“引用有效”；链条完整性比数量更重要。
- 不要仅依赖二手摘要判断法规与统计，优先核对原始来源。
- 不要忽略证据与claim语义不匹配（例如证据描述A，claim声称A+全局结论）。
- 不要把过时来源当作现状证明；必须标明时间上下文。
- 引用审计是发布门禁，不是写作润色；先修正证据链，再优化措辞。

---

## 关联资源

- References: `citation-policy.md`
