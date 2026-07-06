# AI腔检测与改写指南

## 检测原则

不是永远禁止这些表达，而是检测到后判断是否有信息增量。没有增量就删、改短、改实。

## 四类AI腔特征

### 1. 破折号滥用
- 典型问题：用"——"强行制造节奏、转折、总结感
- 处理方式：能用逗号、句号、冒号表达的，不用破折号
- 例外：中文论文标题副标题、解释性插入语、强烈转折可保留

### 2. 英文AI高频词
- 警惕词表：delve, nuanced, robust, seamless, leverage, transformative, foster, encompass, utilize, multifaceted, holistic, synergy, paradigm, empower
- 处理方式：改成具体动作、对象、约束或结论
- 例外：技术文档中这些词有明确技术含义时可保留（如"robust algorithm"在论文中可接受）

### 3. 三人组排比
- 典型问题：总是写成"A、B和C""更快、更准、更安全""效率、质量、体验"
- 处理方式：只保留真正需要并列的要素；能解释因果时，不堆名词
- 例外：正式定义、课程框架、章节结构、政策口径可保留
- 关键区分：不要机械删除所有排比。只有当并列项空泛、互相重叠、无法展开为具体内容时，才视为AI腔。

### 4. 空洞not X but Y
- 典型问题："不是简单的工具，而是……""不仅是……更是……"
- 处理方式：如果后半句没有具体机制、对象、结果，就删掉
- 例外：用于纠正误解、重新定义概念、提出核心立场时可保留

### 5. 句式过度对称（syntactic over-symmetry）
- 典型问题：连续3句以上使用相同句式模板，例如"X实现Y。A实现B。M实现N。"或"First… Second… Third… Therefore…"
- 处理方式：在每段中至少打破一次模板——把结论前置、插入例子、用短句打断
- 例外：形式化定义、编号步骤、算法描述中的有序列举可保留
- 关键区分：学术写作中的句式变化是人类作者的标志。完全对称的段落即使没有口号也是AI腔。详见 `references/academic-writing.md` Part 1 特征3。

### 6. 句长波动不足（low burstiness）
- 典型问题：所有句子长度集中在狭窄区间（变异系数CV < 0.4），没有长句和短句的交替
- 处理方式：在长复合句后跟一个短句（≤8词或≤15字）；在短句后允许一个长句（≥30词或≥50字）
- 例外：法律条文、规格说明等要求句式统一的文体可保留
- 检测方式：`scripts/style_check.py` 会计算句长变异系数。学术写作尤其需要burstiness，见 `references/academic-writing.md` Part 2 技巧2.4。

### 7. 段落模板化（paragraph templating）
- 典型问题：连续4段以上句数相同（±1句），每段都遵循"背景→方法→结果→结论"的相同骨架
- 处理方式：故意写出至少一个短段（2–3句）和一个长段（5–7句）；让至少一段以结论或限制开头
- 例外：实验报告中的标准化小节、论文中的方法节按步骤组织时可保留

### 8. 连接词堆叠（connector stacking）
- 典型问题：每句都有显式逻辑连接词（"因此""另一方面""具体来说""However""Therefore"），没有让读者自己推断两步以内的逻辑
- 处理方式：每页至少删掉一个显式连接词，改为隐式衔接
- 例外：论证密度高、读者需要明确追踪推理链的技术分析可多用

## 改写动作表

| AI腔模式 | 不好的写法 | 更好的处理 |
|---|---|---|
| 滥用破折号 | 这不是一个工具——而是一个平台 | 这是一个平台，负责统一调度工具、上下文和执行状态 |
| 三人组排比 | 提升效率、质量和体验 | 减少重复配置，并降低初始化出错率 |
| 空洞not X but Y | 不是简单生成内容，而是重塑工作流 | 它把需求澄清、目录初始化、规则生成和skill安装放到同一流程中 |
| 高级词堆叠 | nuanced approach to robust orchestration | 先判断任务类型，再加载对应skill，避免一次性塞入所有规则 |
| 英文AI高频词 | 我们需要leverage这个transformative的框架来foster创新 | 我们通过该框架提供的自动化能力，将原本需要3天的初始化流程缩短至1小时 |
| Dash abuse | This is the solution—the only way forward—to solve our problems | This solution addresses the root cause of the memory leak by implementing a custom allocator |
| Triplet parallelism | Improving speed, accuracy, and efficiency | Reducing response time by 20% and eliminating manual data entry errors |
| Empty not X but Y | It's not just a tool, but a transformative journey for your team | It automates the documentation process, allowing developers to focus on core logic |
| 句式过度对称 | The model achieves high accuracy. The model handles edge cases. The model scales to large datasets. | The model achieves high accuracy on the standard benchmark. Edge cases require a fallback path, which we describe in Section 3. At scale, throughput degrades linearly rather than gracefully. |
| 句长波动不足 | We designed the system. We tested the system. We deployed the system. We evaluated the system. (每句7词) | We designed and tested the system in a controlled environment. Deployment followed. Evaluation, however, revealed a throughput regression we had not anticipated. |
| 段落模板化 | (连续5段，每段都是4句：背景句→方法句→结果句→结论句) | Break the pattern: write a 2-sentence observation paragraph, then a 6-sentence analysis paragraph. |
| 连接词堆叠 | Therefore, we observe X. However, Y also holds. Specifically, Z follows. In conclusion, W. | We observe X. Y also holds, though the effect is smaller. Z follows when the sample is restricted to the labeled subset. |

## Detection Metrics

AI-generated text tends to score differently from human text on several measurable dimensions. `scripts/style_check.py` computes these where applicable. For standalone, report-grade detection, see the `de-ai-detector` skill.

### Burstiness (sentence-length coefficient of variation)

- **Definition**: standard deviation of sentence lengths divided by the mean length (CV).
- **AI signal**: low CV (< 0.4 with ≥ 5 sentences). Sentence lengths cluster around a narrow band.
- **Human signal**: higher CV. A mix of short, medium, and long sentences.
- **Rewrite move**: after a long sentence, add a short one (≤ 8 words / ≤ 15 characters); after several short sentences, allow one longer sentence.
- **Exception**: legal texts, specification lists, and some technical procedures intentionally keep uniform length.

### Type-token ratio (TTR)

- **Definition**: number of unique words (types) divided by total words (tokens). A low TTR indicates repetitive vocabulary.
- **AI signal**: TTR is lower than expected for the genre; the model reuses the same safe words.
- **Human signal**: higher TTR; authors introduce domain-specific synonyms, slight redundancies, and verbal tics.
- **Rewrite move**: replace the single most probable word with a slightly less common but accurate alternative; vary verbs and noun phrases.
- **Caveat**: TTR is sensitive to text length. Compare only within similar-length passages.

### Transition density

- **Definition**: number of explicit logical connectors per 100 words or per paragraph.
- **AI signal**: every sentence carries a connector; the text over-explains its own logic.
- **Human signal**: some transitions are implicit; the reader follows two-step inferences without signposting.
- **Rewrite move**: drop at least one explicit connector per page and rely on juxtaposition or pronoun reference.
- **Exception**: dense technical arguments may legitimately need frequent connectors.

### Syntactic repetition index

- **Definition**: percentage of sentences in a paragraph that share the same starter or template.
- **AI signal**: 3+ consecutive sentences begin with the same pattern.
- **Human signal**: varied openings; at least one sentence per paragraph breaks the dominant template.
- **Rewrite move**: move the conclusion forward, insert an example, or start with a limitation.

### Paragraph templating score

- **Definition**: difference between the longest and shortest paragraph (in sentences) across a section.
- **AI signal**: all paragraphs have the same sentence count (±1).
- **Human signal**: paragraphs vary by ≥ 2 sentences.
- **Rewrite move**: deliberately write one short paragraph (2–3 sentences) and one longer paragraph (5–7 sentences) per page.

### Connector stacking score

- **Definition**: percentage of sentences that begin with an explicit connector.
- **AI signal**: > 50% of sentences start with a connector.
- **Human signal**: 20–40% connector usage, with implicit logic elsewhere.
- **Rewrite move**: convert explicit connectors to implicit transitions where the relationship is obvious.

## Integration with de-ai-detector

This reference focuses on manual/self-check rules. For automated detection that produces a structured report:

1. Run `de-ai-detector` on the source text.
2. The report lists flagged patterns with severity and location.
3. Load the report into `petfish-style-rewriter` and fix flags in severity order.
4. Re-run detection or `scripts/style_check.py` to verify.

## 保留条件

不要过度清洗。以下情况不视为AI腔：
- 正式论述中的有序分层结构（如"一是……二是……三是……"）
- 技术/论文写作中的"背景、问题、方案、效果"分层论证
- 课程大纲中的模块名称并列
- 英文论文中符合学术规范的词汇使用
- 有信息增量的对比结构

## 说人话评分卡

每段完成后按以下标准自评（5分制）：

| 维度 | 说明 | 满分 |
|---|---|---|
| 信息密度 | 是否提供了具体对象、动作、原因、结果？ | 5 |
| 句子自然度 | 是否像真实作者会写的话？ | 5 |
| 结构必要性 | 排比、转折、总结是否服务论证？ | 5 |
| 术语克制 | 术语是否必要，是否解释清楚？ | 5 |
| 风格一致性 | 是否符合用户已有写作风格？ | 5 |
| 句长波动 | 是否有长短句交替（burstiness），而非全部中等长度？ | 5 |
| 句式多样性 | 是否避免了连续3句以上相同模板？ | 5 |

低于4分的段落必须改写。

学术写作另需检查 `references/academic-writing.md` Part 6 的学术专项自检清单。

## 检测流程图

Use this flow for every paragraph in a de-AI rewrite:

```text
1. Surface scan
   ├── dash abuse? ──yes──→ replace with comma/colon/period
   ├── English AI buzzword? ──yes──→ replace with concrete action/object
   ├── empty triplet? ──yes──→ collapse or expand with causality
   └── hollow not-X-but-Y? ──yes──→ delete or replace with mechanism

2. Linguistic scan
   ├── syntactic symmetry (≥3 same-template sentences)? ──yes──→ break one template
   ├── low burstiness (CV < 0.4)? ──yes──→ insert short/long sentence
   ├── paragraph templating (≥4 same-shape paragraphs)? ──yes──→ vary length/opening
   └── connector stacking (>50% sentences start with connector)? ──yes──→ drop one connector

3. Chinese-specific scan
   ├── 排比句 (≥3 parallel sentences)? ──yes──→ rewrite if empty
   ├── 空洞框架词? ──yes──→ delete or replace with concrete observation
   ├── 被动泛化? ──yes──→ name agent or use active verb
   └── 词汇趋同? ──yes──→ vary verbs or use concrete description

4. Verify
   └── Does the fix preserve factual claims and technical terms?
       no  → revert and try a lighter rewrite
       yes → continue
```

Run the flow once per paragraph, not once per document. Surface issues are the cheapest to fix; linguistic issues take priority when they recur.

## 严重度校准指南

Not every flag requires the same response. Calibrate by severity and context.

| Severity | When to assign | Rewrite response |
|---|---|---|
| CRITICAL | Pattern is empty, repeated, and central to the claim | Rewrite immediately; keep only with explicit justification |
| HIGH | Pattern weakens readability or credibility | Rewrite unless it carries a precise technical meaning |
| MEDIUM | Pattern is present but supported by evidence | Soften, shorten, or add concrete anchor |
| LOW | Pattern is isolated and harmless | Note and rewrite only if it accumulates |
| KEEP | Pattern serves real structure, definition, or rhetoric | Leave intact; do not "fix" for the sake of fixing |

A good rule of thumb: if removing the pattern also removes information, keep it. If removing the pattern only improves rhythm, rewrite it.

## 避免误杀（False Positive Avoidance）

Over-correction is a different kind of artificiality. Avoid these common false positives:

1. **Formal lists and definitions**. A numbered procedure ("Step 1… Step 2… Step 3…") is not connector stacking; it is a list.
2. **Technical terms that happen to be AI buzzwords**. "Robust" in "robust statistics" or "leverage" in "leverage ratio" are domain terms, not AI flavor.
3. **Deliberate rhetorical parallelism**. A speaker may repeat a sentence pattern for emphasis; preserve it when it is intentional and emotionally warranted.
4. **Regulatory or contractual language**. Phrases like "shall not" or "provided that" are required by register, not AI signals.
5. **User-provided quotes**. Do not rewrite inside quotation marks unless the user explicitly asks for paraphrase.
6. **Short uniform paragraphs in emails**. Email bullets often share a shape; treat them as a genre convention, not paragraph templating.

When in doubt, ask: "If a human editor rewrote this, would they change this phrase?" If the answer is no, leave it.
