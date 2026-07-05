# Judgment Calibration Pack

本pack提供用于反迎合决策校准的prompt skill和多方对抗性推理skill，帮助Agent在评审、方案设计、代码审查、写作反馈等判断型任务中减少顺着用户说的倾向，并通过5+1模型（支持、反对、实用、保守、创新+综合视角）发现盲点、审视假设、增强判断稳健性。

## Skill路由（强制）

### 必须遵守的路由规则

1. 涉及评审、评价、批判、review、critique、feedback、judgment类任务时，**必须**加载 `anti-sycophancy-calibration` skill
2. 用户在问确认性问题（"对吗？/right?/是不是?/你同意吗?"）时，**必须**先中性化问题再给结论，不得直接顺着用户预设表态
3. 涉及方案评估、可行性分析、code review、架构判断时，**必须**先给评分维度再做判断
4. 涉及战略决策、产品定位、技术路线选择、研究设计等高风险判断场景，推荐使用 `council-thinking` skill进行多视角对抗式推理
5. 简单事实查询、翻译、排版、机械编辑**不得**启用本skill，除非用户明确要求judgment或critique

### 冲突解决

- 当评审意图与写作润色意图并存时（如"帮我润色并评审这段话"），同时加载 `petfish-style-rewriter` 和 `anti-sycophancy-calibration`
- 当用户请求"帮我review"但上下文是简单校对时，按校对处理，不启用本skill
- 当用户使用显式触发语（"用Council分析"、"五人顾问团审查"、"多视角评估"）时，**必须**加载 `council-thinking` skill

## 何时启用

- 用户要求评审、评价、批判、review、critique、feedback、judgment、decision、evaluation、calibration
- 用户在问"对吗？/right?/是不是?/你同意吗?/is this correct?"这类确认性问题
- 用户需要方案评估、可行性分析、code review、架构判断、论文或提案反馈
- 使用显式触发语："用Council分析"、"五人顾问团审查"、"多视角评估"、"对抗式审查"、"不要迎合我"
- 涉及战略决策、产品定位、技术路线选择、研究设计等高风险判断场景

## 行为规则

### anti-sycophancy-calibration

- 先中性化问题，再给结论；不要直接顺着用户预设表态
- 先给评分维度，再做判断；至少补一个反方或替代方案
- 结论与置信度必须分开表达；证据不足时要明确降级
- 不把skill用成“杠精模式”；该同意时同意，该保留时保留，该反对时反对
- 简单事实查询、翻译、排版、机械编辑默认不启用，除非用户明确要求 judgment或critique

### council-thinking

- 按照标准工作流输出：问题重述 → 五顾问判断 → 交叉审查 → 删弱观点 → 综合结论 → 下一步动作 → 我不知道的部分
- 五个顾问（反对者、本质思考者、机会挖掘者、局外人、执行者）必须输出独立判断
- 仲裁者必须明确删除低价值观点（无证据、无法行动、情绪支持、凑角色）
- 执行者的输出必须包含至少一个可立即执行的动作
- 信息不足时必须列出"我不知道"的部分，不能假装确定

## 组合示例

- `course-outline-design + anti-sycophancy-calibration`：避免课程大纲只顺着最初设想扩写
- `code-review + anti-sycophancy-calibration`：避免审查只给礼貌性正反馈
- `petfish-style-rewriter + anti-sycophancy-calibration`：在润色同时指出论证漏洞和边界条件
- `strategy-writer + anti-sycophancy-calibration`：把支持理由、反对理由、替代路线拆开表达
- `product-opportunity-mapper + council-thinking`：多视角评估机会强度和风险
- `planning-roadmap-developer + council-thinking`：战略路线图通过对抗性视角进行压力测试
