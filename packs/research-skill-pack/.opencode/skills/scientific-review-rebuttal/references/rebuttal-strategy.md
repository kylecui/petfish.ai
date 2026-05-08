# Rebuttal Strategy: Evidence-First, Respectful, and Actionable

rebuttal的目标不是“赢过审稿人”，而是“让评审相信你理解问题、提供证据、愿意修订”。高质量rebuttal通常具备三点：准确分类评论、逐条回应有证据、承诺修订可执行。低质量rebuttal通常有三点：情绪化、防御性、空泛承诺。

## 1) First principle: classify before responding

收到评论后，不要立刻写长段回复。先把每条评论分类，这会直接决定回应策略。建议使用以下五类：

1. **Factual error（事实错误）**：审稿评论含可验证错误；
2. **Misunderstanding（理解偏差）**：论文表达不清导致误解；
3. **Valid criticism（有效批评）**：评论指出真实缺陷；
4. **Scope disagreement（范围分歧）**：对论文边界认知不同；
5. **Style preference（风格偏好）**：写法或组织方式建议。

这一步是硬要求。未分类直接回应，常导致混乱和冲突。

## 2) Response policy by category

### A) Factual error

策略：礼貌指出事实，并给可核验证据（页码、图表、公式、附录）。

模板：

> Thank you for raising this point. We believe there may be a factual mismatch here. In Section X (Page Y), we state [...], and Figure Z reports [...]. To avoid confusion, we will revise the wording to make this explicit.

注意：即使审稿人错，也不要写“Reviewer is wrong”。用“may be a mismatch”更稳妥。

### B) Misunderstanding

策略：先承认表述不清，再补充解释和修订动作。

模板：

> Thank you for the clarification request. We agree that our original text was not sufficiently clear. We will revise Section X to explicitly state [...], add an example in Figure Y, and improve the transition between Sections A and B.

核心点：误解往往反映表达问题，不要把责任全推给审稿人。

### C) Valid criticism

策略：直接承认问题，给出修复计划和影响范围。

模板：

> We agree with this criticism. The current evaluation does not fully cover [...]. In the revision, we will add [...], report [...], and discuss the impact on claims C2 and C3.

这是最能建立信任的回复类型。承认有效批评不会削弱你，反而显示学术诚实。

### D) Scope disagreement

策略：明确论文目标边界，解释不做某项工作的原因，并给最小补充。

模板：

> This is an important direction. Our current scope focuses on [...], while [...] is beyond the intended contribution of this paper. To make the boundary explicit, we will add a scope statement in Section X and discuss this extension in Limitations.

注意：范围分歧不是“拒绝做事”，而是“清楚界定并说明代价”。

### E) Style preference

策略：能改就改，低成本提升可读性。

模板：

> Thank you for the suggestion on presentation. We will adopt this style change in the revised draft to improve readability.

风格建议通常不应硬刚，除非影响技术正确性。

## 3) Point-by-point template (recommended)

每条评论都用固定四段：

1. **理解确认**：我们理解评论关注点是什么；
2. **回应结论**：同意/部分同意/不同意；
3. **证据与理由**：引用论文位置、实验结果、附录证据；
4. **修订动作**：明确会改什么、改到哪里。

模板骨架：

```markdown
### Reviewer #N, Comment #M

**Comment summary**
[用1-2句复述，证明你理解了问题]

**Response**
[同意/部分同意/不同意]

**Evidence**
[页码、章节、图表、公式、实验结果]

**Revision plan**
[将新增/重写/移动哪些内容，位置在哪]
```

## 4) Rules you must never break

1. **Never be dismissive**：禁止“this comment is irrelevant”这类表述；
2. **Acknowledge valid points**：有效批评必须承认，不绕；
3. **Evidence for disagreements**：不同意必须带证据；
4. **Concrete revisions**：不能只写“will improve”，要写“improve what and where”；
5. **No new unsupported claims**：rebuttal不能引入论文未支撑的新主张。

## 5) Handling major vs minor comments

建议先处理高影响评论：

- **Major**：新颖性、技术正确性、评估充分性、可复现性；
- **Minor**：术语统一、图例、格式、语法。

如果时间有限，优先确保major评论有充分回应和修订承诺。minor问题可在末尾集中说明已统一修正。

## 6) What to do when you disagree strongly

强烈不同意时，依然遵循“尊重 + 证据 + 边界”：

1. 先肯定问题价值；
2. 再说明你为什么不同意（数据、理论、目标范围）；
3. 最后给折中修订（澄清文本、补充讨论、加限制说明）。

示例：

> We appreciate this concern and agree that robustness is important. Our current claim is limited to in-distribution settings (Section 1, Paragraph 3). We therefore do not claim robustness under adaptive attacks. To prevent overstatement, we will revise the introduction and add a dedicated limitation paragraph.

这类写法能坚持立场，同时减少对抗感。

## 7) Rebuttal evidence pack

建议在写回复前准备“证据包”：

- 关键图表定位（页码+图号）；
- 关键实验补充结果；
- 术语定义对照表；
- claim-evaluation map；
- limitation和scope声明草案。

有证据包，回复会更短更硬；没有证据包，容易变成长篇解释。

## 8) Common failure patterns in rebuttal

### 失败1：情绪化防御
表现：反复强调“我们的方法很好”。
改法：删主观形容词，替换为证据句。

### 失败2：回避关键问题
表现：只回应次要细节。
改法：先列major评论，逐条闭环。

### 失败3：承诺过度
表现：承诺大量新实验但无法按期完成。
改法：只承诺可交付修订，剩余放limitation。

### 失败4：逐字反驳不做修订
表现：回应看似充分，论文不改。
改法：每条回复绑定修订位置。

## 9) Suggested final structure of rebuttal letter

1. 开场感谢与总览（1段）；
2. 对主要问题的总体修订摘要（2-4条）；
3. Reviewer 1逐条回复；
4. Reviewer 2逐条回复；
5. Reviewer 3逐条回复；
6. 结尾重申贡献边界与修订完成度。

每条回复控制在“清楚且可核验”的长度，避免冗长辩论。

## 10) Final checklist before submission

- 每条评论是否已分类？
- 每条不同意是否附证据？
- 每条同意是否附修订动作？
- 是否存在任何dismissive语气？
- 是否有无法兑现的承诺？

结论：rebuttal是一次“可信度管理”。你不需要在每点都赢，但必须在每点都专业、诚实、可验证。真正高通过率的rebuttal，不是最激进的，而是最清晰、最克制、最有证据的。
