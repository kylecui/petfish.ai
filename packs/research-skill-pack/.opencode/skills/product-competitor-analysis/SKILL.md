---
name: product-competitor-analysis
description: 系统化执行竞品发现、功能矩阵、定位分析、SWOT与市场规模估算，提炼可执行差异化方向。Use when the user says "竞品分析", "competitor analysis", "竞品", "competitive landscape", "功能矩阵", "feature matrix", "市场分析", "market analysis", "SWOT", "定位分析", "positioning", "market sizing", "差异化", or "differentiation".
compatibility: opencode
license: Apache-2.0
---

## 作用/Purpose

建立可审查的竞争格局分析，不依赖主观印象判断“谁是对手”。该skill要求：
1) 明确竞争范围与样本边界；
2) 用证据构建功能与定位对比；
3) 形成可执行的差异化与进入策略输入。

输出应为产品战略服务，而非“信息罗列型竞品笔记”。

---

## 触发场景/Trigger Scenarios

- 用户提出“竞品分析 / competitor analysis / competitive landscape”
- 需要制作功能矩阵并比较主流方案能力边界
- 需要定位分析（positioning）或SWOT用于策略评审
- 需要市场分析与market sizing评估机会规模
- 需要回答“我们与现有方案相比可如何差异化”

---

## 输入/Input

- product brief（产品定位、目标价值、核心能力）
- target market（目标市场、客群、地域或行业范围）
- known competitors（已知竞品清单）
- 可选：定价信息、渠道信息、公开案例与评测

---

## 输出/Output

- `competitor-matrix.md`
- `positioning-map.md`
- `swot-analysis.md`
- `market-brief.md`

---

## 工作流/Workflow

1. 定义竞争范围：直接竞品、替代方案、潜在进入者。
2. 发现并筛选竞品，记录纳入/排除标准。
3. 构建功能矩阵，逐项标注证据来源与更新时间。
4. 分析定位，至少建立两条定位轴并映射主要竞品。
5. 进行SWOT，区分内部能力与外部机会/威胁。
6. 估算市场规模，明确TAM/SAM/SOM口径与假设。
7. 识别差异化机会，转化为可执行产品策略选项。
8. 标注高不确定区，提出后续验证优先项。

---

## 质量门禁/Quality Gates

- 分析对象必须包含至少3个竞争者（含替代方案可计入）。
- 功能矩阵每个关键条目必须有证据依据，禁止主观臆断。
- 定位图必须至少定义2条清晰轴线并解释轴选择理由。
- 差异化机会必须可执行（可转化为策略动作或实验）。
- 市场规模估算必须显式展示核心假设与计算边界。

---

## Gotchas/注意事项

- 不要只比较功能数量，应比较关键任务完成质量。
- 不要把营销口号当作产品能力证据。
- 不要忽视替代方案（人工流程/通用工具）的竞争压力。
- 市场规模不能只给总量数字，必须解释可达性。
- SWOT不要写成口号，需连接到具体行动建议。

---

## 关联资源

- None (standalone)
