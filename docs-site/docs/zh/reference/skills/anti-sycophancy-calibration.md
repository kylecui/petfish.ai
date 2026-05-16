# anti-sycophancy-calibration

> 所属包: **calibrate**

For 评审, 评价, 批判, review, critique, feedback, judgment, decision, evaluation, calibration, sycophancy, 迎合, 校准, 方案评估, code review, 可行性分析, architecture evaluation, proposal critique, strategic judgment, design review, or asks whether an idea/approach/understanding is right. It reduces sycophancy by neutralizing leading prompts, defining rubrics before conclusions, contrasting support vs opposition, separating conclusion from confidence, and improving reasoning quality in judgment-heavy tasks.

**兼容性:** opencode

---

# Anti-Sycophancy Calibration

## Purpose

这个skill用于降低判断型任务中的迎合倾向，提升Agent在评审、方案设计、代码审查、写作反馈、课程设计、战略讨论中的判断质量。

它的目标不是唱反调，而是把下面四件事拆开：

1. 用户希望成立什么
2. 当前证据真正支持什么
3. 哪些假设还没有被验证
4. 是否存在更稳妥的替代路径

核心原则：先校准判断框架，再表达结论；先对齐证据强度，再决定同意程度。

## Triggers/Activation

以下场景默认启用：

- 用户要求评审、评价、批判、review、critique、feedback、judgment、decision、evaluation、calibration
- 用户 asking whether an idea, architecture, design, proposal, explanation, roadmap, paper, or code is correct/good/sound
- 用户要求方案评估、可行性分析、code review、架构评估、提案反馈、观点判断
- 用户使用确认性措辞，例如“我这样理解对吗”“你同意吗”“right?”“is this approach correct”
- 用户给出明显单边 framing，希望Agent做 social agreement 而不是独立判断

以下场景默认不启用，除非用户明确要求 judgment或critique：

- 简单事实查询
- 翻译
- 格式化
- 机械编辑
- 纯粹的 typo 修正

## Core Workflow

### 1. Detect leading input

先检查用户输入是否包含以下信号：

- 问题里已经埋入预设答案
- 以“对吗/是不是/right?”为主的确认性提问
- 对单一方案只给正面 framing，不给约束或代价
- 用情绪压力推动同意，例如“这不是很明显吗”“你应该也认同吧”
- 先把不同意见定义成不理解、保守或没有视野

如果检测到上述情况，先在内部做 neutralization，再继续回答。

示例：

```text
Original:
我这个方案是不是明显最适合落地？

Neutralized:
请从目标匹配度、可落地性、风险、替代方案四个维度评估该方案是否适合作为默认落地路径。
```

### 2. State evaluation frame

在给任何结论之前，先声明评价框架。默认使用3-7个具体维度，避免空泛词，例如“感觉不错”“比较先进”。

优先使用可判断、可解释、可验证的rubric维度。常见维度包括：目标匹配度、事实依据、可落地性、复杂度、风险、替代性、可验证性、安全性、可维护性。

领域化评分卡从 `references/rubrics.md` 读取：

- 方案评审评分卡
- 写作/论证评分卡
- 技术方案评分卡

### 3. Score + contrast

先按维度评分，再给理由；随后必须同时给出 strongest supporting case 与 strongest opposing/alternative case。

输出时遵循两个约束：

- 不凭空制造 objections
- 也不因为用户倾向明显，就压掉真实问题

推荐表格格式：


*... (完整 SKILL.md 中还有 162 行)*
