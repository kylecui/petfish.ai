# Anti-patterns

This catalog lists AI-like and slogan-heavy patterns to avoid, organized by severity. CRITICAL patterns almost always produce AI-flavored text and should be rewritten. HIGH patterns strongly suggest machine generation unless they carry substantive content. MEDIUM and LOW patterns are acceptable when they serve a real communicative purpose.

Severity rule of thumb:

- **CRITICAL**: rewrite by default; keep only with explicit justification.
- **HIGH**: flag and review; rewrite if the phrase is doing rhetorical rather than informational work.
- **MEDIUM**: acceptable when tied to concrete evidence or necessary structure.
- **LOW**: tolerable in small doses; remove only when they accumulate or become repetitive.

---

## CRITICAL

### 1. AI-like Openings

These openings signal generic AI generation because they launch from abstraction rather than a concrete situation.

Avoid:

- 在当今数字化时代
- 在当今高度复杂的时代背景下
- 随着技术的不断发展
- 在高度复杂的网络对抗格局中
- 面对日益严峻的安全挑战
- 当前，X已经成为不可忽视的重要问题
- In recent years, ... has attracted significant attention
- With the rapid development of ...

Better:

```text
随着 X 的部署范围扩大，Y 问题开始影响 Z。
```

```text
X 在 Y 场景中已经暴露出 Z 类错误，这是当前需要解决的主要问题。
```

### 2. Slogan-heavy Expressions

Avoid:

- 赋能
- 普惠
- 拔高
- 民主化
- 银弹式
- 立体认知
- 能力放大器
- 蜂群式
- 全链路闭环（if not technically explained）
- 从看得懂到管得住
- 打造完整能力闭环
- 底座
- 护城河
- 生态
- 布局
- 拉通
- 透传
- 对齐
- 沉淀
- 矩阵
- revolutionary, game-changing, disruptive (unless directly evidenced)

Use concrete expressions instead:

- 降低使用门槛
- 提升执行效率
- 扩大攻击面
- 增加防御压力
- 提高策略执行的一致性
- 减少人工配置成本
- 统一调度接口
- 减少跨系统不一致

### 3. Unsupported Generalization

Bad:

```text
该方案能够全面提升企业安全能力。
```

Better:

```text
该方案能够减少策略分发和执行之间的不一致，从而提升访问控制的稳定性。
```

### 4. Empty not X but Y

Bad:

```text
这不是一个工具，而是一个平台。
不是简单生成内容，而是重塑工作流。
It's not just a tool, but a transformative journey for your team.
```

Better:

```text
这是一个平台，负责统一调度工具、上下文和执行状态。
它把需求澄清、目录初始化、规则生成和skill安装放到同一流程中。
It automates the documentation process, allowing developers to focus on core logic.
```

Keep only when the second half adds specific mechanism, object, or outcome.

### 5. Excessive Parallelism / Empty Triplets

Bad:

```text
提升效率、质量和体验
更快、更准、更安全
迎接挑战，抓住机遇，开创未来
```

Use only when the structure is necessary and each item carries distinct, concrete meaning. Otherwise, simplify or expand.

---

## HIGH

### 6. Overused Quotation Marks for Emphasis

Bad:

```text
攻击能力的“普惠”与“拔高”
```

Better:

```text
AI 对攻击门槛和攻击效率的影响
```

Keep quotation marks for actual quotes, first introduction of a term, or when the term boundary must be explicit.

### 7. English AI High-frequency Words

Replace with concrete technical terms or descriptions:

- delve → explore, examine, investigate
- nuanced → subtle, context-dependent, fine-grained
- robust → stable, fault-tolerant, reliable
- seamless → smooth, without manual steps
- leverage → use, exploit, build on
- transformative → changes X into Y
- foster → encourage, support, create conditions for
- encompass → include, cover
- utilize → use
- holistic → end-to-end, system-wide
- synergy → combined effect
- paradigm → model, pattern, approach
- empower → enable, allow
- harness → capture, use

Exception: retain when the word has a precise technical meaning in context (e.g., "robust algorithm" in a statistics paper).

### 8. Overly Long Sentence

Bad:

```text
根据客户 RFP，本项目的核心目标不是单纯教授 AI 技术原理，也不是把课程做成纯安全算法训练营，而是围绕企业员工在 AI 应用过程中的实际风险，建立一套由浅入深、从认知到治理、从开发到运营、从案例到组织落地的 AI 安全培训体系。
```

Better:

```text
根据客户 RFP，本项目的目标不是单纯讲授 AI 技术原理，也不是建设安全算法训练营。

课程应围绕企业员工在 AI 应用过程中的实际风险展开，逐步覆盖认知、治理、开发、运营和组织落地等内容。
```

### 9. Flattering Tone

Avoid:

- 非常荣幸
- 深受启发
- 具有重大而深远的意义
- 必将开创全新局面
- It is an honor to...
- We are thrilled to...

Use:

- 本文认为
- 从实践角度看
- 该问题值得进一步分析
- We found that...

### 10. Empty Framework Phrases (Chinese)

These phrases often pad sentences without adding content.

- 值得注意的是
- 不可忽视的是
- 在……的背景下
- 众所周知
- 不言而喻
- 毋庸置疑
- 从某种程度上说

Keep only when they introduce a substantive observation that follows immediately.

### 11. Vocabulary Convergence (Chinese)

Avoid clustering these verbs in the same paragraph:

- 旨在
- 致力于
- 赋能
- 助力
- 推动
- 促进
- 深化
- 强化
- 优化
- 提升

Vary verbs or replace with concrete actions.

---

## MEDIUM

### 12. Passive Generalization (Chinese)

Bad:

```text
该方法被广泛应用于图像识别任务。
```

Better:

```text
该方法广泛用于图像识别任务。
```

Or name the users:

```text
多个视觉团队已将该方法用于图像识别任务。
```

### 13. Template Transitions

Weak when empty:

- 首先……其次……最后……
- 一方面……另一方面……
- 第一……第二……第三……

Keep when each step carries distinct content. Otherwise, use organic transitions:

- 更具体地看
- 与此相对
- 换个角度
- 问题在于
- 这意味着

### 14. Excessive Parallel Structure (Chinese 排比)

Three or more consecutive sentences with the same template = AI pattern unless deliberate rhetoric.

Bad:

```text
A 提升了效率。B 提升了效率。C 也提升了效率。
```

Better:

```text
A 减少了重复配置。B 缩短了初始化时间。C 处理的是错误恢复。
```

### 15. Empty Positive Action Phrases

- 迎接挑战
- 抓住机遇
- 乘风破浪
- 砥砺前行
- moving forward
- going forward

Replace with the specific next step or decision.

### 16. Corporate/AI Grandstanding

- 使命
- 担当
- 深耕
- 携手共创
- 共同打造
- 加持
- 落地
- 闭环
- 链路
- 布局

Acceptable when tied to a concrete plan. Rewrite when used as abstraction.

---

## LOW

### 17. Mild Emphasis Adverbs

- 极大地
- 显著地
- 全面地
- 深刻地
- greatly, significantly, substantially

Require evidence; delete if unsupported. Prefer numbers or conditions.

### 18. Empty Contrast Markers

- 然而
- 但是
- 不过
- however, yet, nevertheless

Acceptable when they signal a real turn. Remove when the contrast is trivial or the marker appears in every sentence.

### 19. Generic Progress Markers

- 不断
- 持续
- 逐步
- 日益
- increasingly, continuously

Acceptable when the progression is measurable. Otherwise, replace with a concrete phase or condition.

### 20. Mild AI Transitions

- 基于此
- 由此可见
- 综上所述（in body text)
- accordingly, consequently

Acceptable in summaries. Remove when used to bridge weakly related sentences.

### 21. Routine Hedging Stacks

- 可能也许
- 或许会
- 在一定程度上可能
- may potentially, could possibly

One hedge per claim is enough; choose the strongest epistemic meaning.

---

## Severity Summary Table

| Severity | Rewrite by default? | Examples |
|---|---|---|
| CRITICAL | Yes | AI openings, slogans, unsupported generalization, empty not-X-but-Y, empty triplets |
| HIGH | Usually | quotation-mark emphasis, English AI words, long sentences, flattering tone, empty framework phrases, vocabulary convergence |
| MEDIUM | When empty | passive generalization, template transitions, 排比, empty positive phrases, corporate grandstanding |
| LOW | Only when accumulated | mild adverbs, empty contrast markers, generic progress markers, mild transitions, hedge stacks |

---

## Quick Reference: Replace Table

| Avoid | Better |
|---|---|
| 赋能 | 使……能够、提供能力、降低门槛 |
| 拔高 | 提升、增加 |
| 普惠 | 降低门槛、扩大可用范围 |
| 银弹 | 单一方案、针对性方案 |
| 闭环 | 完整流程、端到端流程 |
| 链路 | 流程、步骤 |
| 矩阵 | 列表、集合、多维表 |
| 底座 | 基础层、基础设施 |
| 拉通 | 对齐、协调 |
| 对齐 | 达成一致、同步 |
| 透传 | 直接传递、原样转发 |
| 助力 | 帮助、推动 |
| 旨在 | 目的是、为了 |
| 致力于 | 专注于、主要做 |
| 被广泛应用于 | 广泛用于、X 已将其用于 |
| 值得注意的是 | （删除，直接给出事实） |
| 在……的背景下 | 由于…… / 面对…… |
| delve | examine, explore |
| robust | stable, fault-tolerant |
| leverage | use, build on |
| transformative | changes X to Y |
| seamless | without manual steps |

## Before/After Examples by Pattern

These examples show the same thought expressed twice: once with the anti-pattern, once without.

### AI-like opening

- Before: "在当今数字化时代，网络安全已成为企业不可忽视的重要问题。"
- After: "随着零信任架构的部署范围扩大，访问策略与执行点之间的不一致开始频繁暴露。"

### Slogan-heavy expression

- Before: "本方案能够全面赋能企业安全运营能力。"
- After: "本方案将告警归并、策略分发和事件响应集中到同一控制台，减少了跨工具切换成本。"

### Unsupported generalization

- Before: "该模型显著优于现有方法。"
- After: "在五个公开数据集上，该模型将 F1 分数提高了 3–7 个百分点，并在长尾类别上表现出更稳定的召回率。"

### Empty not-X-but-Y

- Before: "这不仅是一个工具，更是一个平台。"
- After: "这个工具统一了配置解析、依赖检测和发布验证三个步骤。"

### Empty triplet

- Before: "提升效率、质量和体验"
- After: "将重复配置时间从 30 分钟缩短到 2 分钟，并降低了初始化出错率。"

### Overused quotation marks

- Before: "攻击能力的"普惠"与"拔高"正在重塑威胁格局。"
- After: "AI 降低了攻击工具的入门门槛，也提高了自动化攻击的效率。"

### English AI high-frequency word

- Before: "We leverage a robust framework to foster seamless integration."
- After: "We rely on the framework's retry and backoff mechanisms to remove manual handoffs between stages."

### Overly long sentence

- Before: "本项目的核心目标不是单纯教授 AI 技术原理，也不是把课程做成纯安全算法训练营，而是围绕企业员工在 AI 应用过程中的实际风险，建立一套由浅入深、从认知到治理、从开发到运营、从案例到组织落地的 AI 安全培训体系。"
- After: "本项目的目标不是讲授 AI 技术原理，也不是建设安全算法训练营。课程应围绕员工在 AI 应用中的实际风险展开，逐步覆盖认知、治理、开发、运营和组织落地。"

### Flattering tone

- Before: "我们非常荣幸能够参与这一具有重大而深远意义的项目。"
- After: "我们梳理了贵方 RFP 中的约束，并针对三个关键风险提出了实施方案。"

### Empty framework phrase

- Before: "值得注意的是，该指标在过去一年中呈现上升趋势。"
- After: "该指标在过去一年中从 12% 上升到 34%。"

### Passive generalization

- Before: "该方法被广泛应用于图像识别任务。"
- After: "多个视觉团队已将该方法用于图像识别任务。"

### Template transition

- Before: "首先，我们收集数据；其次，我们训练模型；最后，我们评估结果。"
- After: "我们收集数据后训练模型，并在三个测试集上评估结果。"

### Excessive parallel structure

- Before: "A 提升了效率。B 提升了效率。C 也提升了效率。"
- After: "A 减少了重复配置，B 缩短了初始化时间，C 处理的是错误恢复。"

### Corporate grandstanding

- Before: "我们将携手共创安全运营新生态。"
- After: "我们建议分三阶段集成现有 SOC 工具，并在第二阶段引入自动化编排。"

### Mild emphasis adverb

- Before: "该优化极大地提升了系统性能。"
- After: "该优化将 P99 延迟从 420ms 降到 95ms。"

### Empty contrast marker

- Before: "该方案很快。然而，它需要更多内存。"
- After: "该方案 latency 很低，但需要更多内存。"

### Generic progress marker

- Before: "系统正在不断完善中。"
- After: "系统已支持 A、B 两种协议；C 协议预计在 Q3 完成。"

### Routine hedging stack

- Before: "这可能会在一定程度上提高效率。"
- After: "这在实验设置中将吞吐量提高了约 18%。"

## Pattern Clustering Rules

Multiple anti-patterns often appear together. When you see one, scan for its usual companions:

- AI-like opening + unsupported generalization + slogan-heavy expression
- Empty not-X-but-Y + empty triplet + English AI buzzword
- Template transition + excessive parallel structure + empty framework phrase
- Corporate grandstanding + flattering tone + mild emphasis adverb
- Passive generalization + generic progress marker + routine hedging stack

Fix the central pattern first; the satellite patterns usually become easier to remove once the core claim is concrete.

## When NOT to Fix

Some patterns are not errors. Do not rewrite them.

1. **User's deliberate voice**. If the source text is intentionally informal, motivational, or slogan-heavy, preserve the user's intent.
2. **Quoted material**. Do not de-AI inside direct quotations.
3. **Genre conventions**. Legal contracts, API reference docs, and regulatory filings have their own register; do not force Petfish style onto them.
4. **Necessary structure**. A course outline, taxonomy, or checklist uses parallel structure by design.
5. **Technical brand language**. If "赋能" or "闭环" is the customer's official product terminology and they ask you to keep it, keep it.
6. **Short isolated instances**. One slogan in a 2,000-word draft is LOW severity; leave it unless the user explicitly asks for strict de-AI.

The goal is not zero tolerance. The goal is to remove patterns that signal generic AI generation while preserving communication intent.
