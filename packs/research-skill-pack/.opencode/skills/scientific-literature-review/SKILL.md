---
name: scientific-literature-review
description: 科学文献综述与systematic review：围绕RQ执行检索策略、纳入排除筛选、全文复核、文献矩阵构建与方法比较，输出研究现状、related work脉络、争议点与研究空白。Use when users ask “文献综述/literature review/systematic review/系统回顾/研究现状/找相关论文/比较方法/related work”.
compatibility: opencode
license: Apache-2.0
---

## 作用/Purpose

将“找几篇论文看看”升级为可复核的系统化文献综述流程：定义研究问题，构建检索式，跨数据库筛选候选文献，完成标题/摘要筛选与全文复核，提取到结构化文献矩阵，并输出研究脉络、方法类别与空白方向。目标是形成可用于后续gap分析和方法设计的研究底盘，而不是摘要列表。

---

## 触发场景/Trigger Scenarios

- 用户说“文献综述 / literature review / systematic review”
- 用户询问“这个方向的研究现状是什么”
- 用户要求“找相关论文并比较方法”
- 用户需要形成可追溯的 related work 基础
- 后续要做 research gap、novelty、methodology 设计

---

## 输入/Input

- 研究主题与核心研究问题（RQ）
- 时间范围、领域边界、关键词种子
- 可选：已有来源索引、已有文献清单、目标投稿场景
- 可选：排除条件（语言、文献类型、行业场景限制）

---

## 输出/Output

- `search-strategy.md` — 检索策略（关键词、布尔式、数据库、迭代记录）
- `inclusion-exclusion-criteria.md` — 纳入/排除标准与筛选理由
- `literature-matrix.md` — 文献矩阵（Paper/Method/Dataset/Metrics/Findings/Limits）
- `literature-review.md` — 研究脉络、方法分类、争议点、研究空白

---

## 工作流/Workflow

1. 定义研究问题（RQ）与子问题，明确范围和边界。
2. 构建初始检索式（关键词、同义词、布尔逻辑、限制条件）。
3. 选择数据库并记录各库检索语法与时间窗口。
4. 执行标题/摘要初筛，记录纳入与排除理由。
5. 对候选文献进行全文复核，补齐方法、数据、指标与局限。
6. 提取关键信息进入文献矩阵，绑定 evidence_id（如已接入账本）。
7. 做主题聚类与方法分类，形成研究线程（threads）。
8. 对比主流路线、边缘路线与争议结论，识别至少三类gap。
9. 输出综述结论与后续研究入口，不直接宣称最终贡献成立。
10. 参考 `literature-review-method.md` 与 `search-query-patterns.md` 校准流程一致性。

---

## 质量门禁/Quality Gates

- 必须有可复核的检索策略（数据库、检索式、检索时间）。
- 必须有纳入/排除标准，且记录筛选理由。
- 不允许仅罗列摘要，必须完成矩阵化提取与横向比较。
- 必须形成研究脉络与方法类别，不做平铺清单。
- 必须识别至少3类研究gap并说明证据基础。

---

## Gotchas/注意事项

- 不要把引用数量当作研究充分性；覆盖面与代表性更关键。
- 不要混淆“方法新”与“问题新”；二者需分别评估。
- 不要忽略负结果与失败实验，它们常是gap信号。
- 不要只看单一数据库，跨库检索可降低偏差。
- 不要在综述阶段先写结论立场，再倒填文献。

---

## 关联资源

- References: `literature-review-method.md`, `search-query-patterns.md`
- Assets: `literature-matrix-template.md`
