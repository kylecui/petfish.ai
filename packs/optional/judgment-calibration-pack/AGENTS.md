# Judgment Calibration Pack

本 pack 提供判断校准相关的 skills：

- `fish-calibrate`：轻量单代理反迎合决策校准，用于评审、方案评估、确认性提问等场景。
- `council-thinking`：深度 5+1 多视角对抗式判断，用于复杂方案评估、战略判断、产品定位、研究设计、课程设计等场景。

## Skill 路由（强制）

### 必须遵守的路由规则

1. 涉及评审、评价、批判、review、critique、feedback、judgment 类任务时，**必须**加载 `fish-calibrate` skill。
2. 用户在问确认性问题（"对吗？/right?/是不是?/你同意吗?"）时，**必须**先中性化问题再给结论，不得直接顺着用户预设表态。
3. 涉及方案评估、可行性分析、code review、架构判断且需要深度多角度审查时，**必须**加载 `council-thinking` skill。
4. 用户说"用 Council 分析"、"五人顾问团"、"多视角判断"、"对抗式审查"、"不要迎合我，用 Council 审查"时，**必须**加载 `council-thinking` skill。
5. 简单事实查询、翻译、排版、机械编辑**不得**启用 `fish-calibrate` 或 `council-thinking`，除非用户明确要求 judgment 或 critique。

### 冲突解决

- 当评审意图与写作润色意图并存时（如"帮我润色并评审这段话"），同时加载 `petfish-style-rewriter` 和 `fish-calibrate`。
- 当用户请求"帮我 review"但上下文是简单校对时，按校对处理，不启用本 pack 中的任何 skill。
- **快速校准/单维度评审 → `fish-calibrate`；深度多视角对抗/显式 Council 请求 → `council-thinking`。两者不同时加载。**
- 如果用户请求"用 Council 快速看一下"，仍路由到 `council-thinking`，但使用快速模式而非完整模式。

## 何时启用 fish-calibrate

- 用户要求评审、评价、批判、review、critique、feedback、judgment、decision、evaluation、calibration。
- 用户在问"对吗？/right?/是不是?/你同意吗?/is this correct?"这类确认性问题。
- 用户需要方案评估、可行性分析、code review、架构判断、论文或提案的快速反馈。

## 何时启用 council-thinking

- 用户说"用 Council 分析"、"五人顾问团"、"多视角判断"、"对抗式审查"。
- 涉及复杂方案评估、战略判断、产品定位、技术路线、研究设计、课程设计、Presentation 主线设计。
- 需要"反迎合""挑错""风险审查"的复杂判断问题。
- 项目 `rigor: true` 或 `depth: thorough` 且任务明显属于复杂判断（此时由 fish-brain 在 skill 推荐层建议使用）。

## 行为规则

- 先中性化问题，再给结论；不要直接顺着用户预设表态。
- 先给评分维度或问题重述，再做判断。
- 至少补一个反方或替代方案。
- 结论与置信度必须分开表达；证据不足时要明确降级。
- 不把 skill 用成"杠精模式"；该同意时同意，该保留时保留，该反对时反对。
- council-thinking 必须完成五步流程：问题重述 → 五顾问判断 → 交叉审查 → 删弱观点 → 综合结论。
- council-thinking 最终结论不是五个观点的平均值，而是经过筛选后的判断。

## 组合示例

- `course-outline-design + fish-calibrate`：避免课程大纲只顺着最初设想扩写。
- `course-outline-design + council-thinking`：对课程整体结构做多视角对抗式审查，发现学员视角和交付视角的盲点。
- `code-review + fish-calibrate`：避免审查只给礼貌性正反馈。
- `product-decision-brief + council-thinking`：对立项假设做 Critic / Essence / Outsider 多角度审视。
- `petfish-style-rewriter + fish-calibrate`：在润色同时指出论证漏洞和边界条件。
- `strategy-writer + council-thinking`：把支持理由、反对理由、替代路线拆开表达并形成执行结论。
