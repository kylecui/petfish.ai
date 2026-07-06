# AI Writing Patterns Catalog

This reference catalogs concrete AI writing patterns that `de-ai-detector` looks for. Each entry includes a description, an AI-version example, a human-version counter-example, the detection method used by the script or LLM stage, and a default severity.

## Severity Legend

- **CRITICAL**: Strong AI signal; almost always hurts readability.
- **HIGH**: Reliable AI signal; usually worth rewriting.
- **MEDIUM**: Context-dependent; flag for review.
- **LOW**: Weak signal; only matters when clustered with other patterns.

---

## Chinese Patterns

### 1. 三段式排比 (Triplet Parallelism)

- **Description**: Three parallel phrases or sentences of equal length and similar grammar, often carrying abstract nouns.
- **AI version**: "我们需要提升效率、质量和体验。"
- **Human version**: "响应时间从 2s 降到 200ms，人工录入错误也消失了。"
- **Detection**: Regex for `X、Y和Z` or three comma-separated 4-6 character phrases.
- **Severity**: MEDIUM

### 2. 空洞总结句 (Empty Summary Phrases)

- **Description**: Concluding or transitional phrases that add no new information.
- **AI version**: "综上所述，这一方案具有重要意义。"
- **Human version**: "因此，我们选择用无状态服务承载这部分流量。"
- **Detection**: Regex for `综上所述`, `总而言之`, `值得注意的是`, `不言而喻`, `毋庸置疑`.
- **Severity**: HIGH

### 3. 模板化过渡 (Templated Transitions)

- **Description**: Rigid first/second/third or on-one-hand/on-the-other-hand structures.
- **AI version**: "首先，我们分析了需求。其次，我们设计了架构。最后，我们完成了实现。"
- **Human version**: "先看需求：报表导出每天触发上万次，但旧实现是单线程。"
- **Detection**: Regex starters such as `首先`, `其次`, `最后`, `一方面`, `另一方面`, `第一`, `第二`, `第三`.
- **Severity**: MEDIUM

### 4. 均匀句长 (Low Burstiness)

- **Description**: Sentence lengths stay in a narrow band; no short or long outliers.
- **AI version**: (five sentences all 28-32 Chinese characters)
- **Human version**: (a mix of 10, 45, 18, 6, and 38 characters)
- **Detection**: Coefficient of variation (CV) of sentence character counts.
- **Severity**: HIGH

### 5. 词汇趋同 (Vocabulary Convergence)

- **Description**: The same formal/empty verbs and nouns recur across the text.
- **AI version**: "本项目旨在赋能团队，致力于打造高效闭环，持续沉淀最佳实践。"
- **Human version**: "这个脚本把初始化、依赖检查和模板生成串成一条命令。"
- **Detection**: Count occurrences of known AI buzzwords; low type-token ratio.
- **Severity**: MEDIUM

### 6. 缺乏人称 (No Personal Voice)

- **Description**: The text never uses `我`, `我们`, or `笔者`, preferring passive `本文`/`本研究`.
- **AI version**: "本文旨在探讨该问题的重要性。"
- **Human version**: "我在这三个月里踩过三个坑。"
- **Detection**: Pronoun presence check; flag paragraphs with zero first/second person pronouns.
- **Severity**: MEDIUM

### 7. 过度正式 (Over-Formal Tone)

- **Description**: No colloquial touches, asides, contractions, or concrete examples.
- **AI version**: "该现象的产生具有多方面的原因。"
- **Human version**: "这个问题我遇到过两次，一次是缓存没清，一次是并发超限。"
- **Detection**: Low density of concrete numbers/examples plus high density of nominalizations.
- **Severity**: LOW

### 8. 段落均等 (Paragraph Templating)

- **Description**: Paragraphs have nearly identical sentence counts and internal skeleton.
- **AI version**: Four paragraphs, each exactly 4 sentences: background → method → result → conclusion.
- **Human version**: Paragraphs of 2, 5, 3, and 7 sentences following content needs.
- **Detection**: Sentence-count variance across paragraphs; flag if max-min ≤ 1 for 4+ paragraphs.
- **Severity**: MEDIUM

### 9. 破折号滥用 (Dash Abuse)

- **Description**: Em-dashes used to create false drama or summary.
- **AI version**: "这不是一个工具——而是一个生态。"
- **Human version**: "这个工具负责调度，具体包括任务分发和状态同步。"
- **Detection**: Regex for `——` in non-quoted text.
- **Severity**: LOW

### 10. 连接词堆叠 (Connector Stacking)

- **Description**: Every sentence carries an explicit logical connector, leaving no implicit logic.
- **AI version**: "因此，我们观察到 X。然而，Y 也成立。具体来说，Z 成立。"
- **Human version**: "X 成立。Y 也成立，不过只在标注子集上。"
- **Detection**: Connector-to-sentence ratio.
- **Severity**: MEDIUM

### 11. 空洞 not X but Y (Empty Contrast)

- **Description**: `不是……而是……` or `不仅……更是……` where the second half is still abstract.
- **AI version**: "我们不是在做工具，而是在重塑工作流。"
- **Human version**: "这个命令不只生成文件，还会检查依赖版本和平台兼容性。"
- **Detection**: Regex for contrast structures followed by abstract nouns.
- **Severity**: HIGH

### 12. 列表化过重 (List Heavy)

- **Description**: Prose is converted into long bulleted or numbered lists without narrative glue.
- **AI version**: A 10-item list where each item is a generic noun phrase.
- **Human version**: A short list (≤5 items) with a sentence explaining why the grouping matters.
- **Detection**: Ratio of list-item lines to total non-empty lines.
- **Severity**: LOW

### 13. 浮夸副词 (Grand Adverbs)

- **Description**: Adverbs such as `极大地`, `显著地`, `全面地`, `深刻地` without a measured claim.
- **AI version**: "该优化极大地提升了系统性能。"
- **Human version**: "这个改动把 P99 从 1.2s 降到 180ms。"
- **Detection**: Regex for `极大地|显著地|全面地|深刻地|有效地` without a nearby number.
- **Severity**: MEDIUM

---

## English Patterns

### 14. Low Burstiness

- **Description**: Sentence word counts cluster tightly; missing short and long alternation.
- **AI version**: Five sentences each 18-22 words.
- **Human version**: A mix of 8, 32, 14, 5, and 27 words.
- **Detection**: CV of sentence word counts.
- **Severity**: HIGH

### 15. Templated Transitions

- **Description**: Repeated use of `Furthermore`, `Moreover`, `Additionally`, `However`, `Therefore`.
- **AI version**: "Furthermore, the system is robust. Moreover, it scales. Additionally, it is secure."
- **Human version**: "The system stays up under load; scaling, however, requires the cache partition described in Section 3."
- **Detection**: Transition phrase density.
- **Severity**: MEDIUM

### 16. Hedging Phrases

- **Description**: Empty hedging that weakens claims without adding uncertainty information.
- **AI version**: "It is worth noting that performance may be important."
- **Human version**: "If latency exceeds 200ms, users abandon the checkout flow."
- **Detection**: Regex for `It is worth noting`, `It should be mentioned`, `It is important to`.
- **Severity**: HIGH

### 17. Uniform Paragraph Structure

- **Description**: Every paragraph follows the same sentence-count and rhetorical skeleton.
- **AI version**: Four paragraphs, each 4 sentences: topic → evidence → analysis → wrap-up.
- **Human version**: Paragraph lengths and openings vary with the argument.
- **Detection**: Sentence-count variance and paragraph-starter diversity.
- **Severity**: MEDIUM

### 18. Vocabulary Predictability

- **Description**: Over-use of AI-frequent words (`delve`, `nuanced`, `robust`, `leverage`, `paradigm`).
- **AI version**: "We need a nuanced approach to leverage this robust paradigm."
- **Human version**: "We retry failed requests with exponential backoff and log every transient error."
- **Detection**: Match against high-frequency AI word list.
- **Severity**: MEDIUM

### 19. Passive Voice Overuse

- **Description**: Too many sentences use `be + past participle`, hiding the actor.
- **AI version**: "The bug was fixed and the tests were run."
- **Human version**: "I fixed the race condition and ran the tests."
- **Detection**: Regex for common passive constructions.
- **Severity**: MEDIUM

### 20. Not only...but also

- **Description**: Formulaic emphatic structure that often pads the sentence.
- **AI version**: "Not only does the tool detect issues, but it also fixes them."
- **Human version**: "The tool detects issues and, when configured, can fix them automatically."
- **Detection**: Regex for `not only .* but also`.
- **Severity**: LOW

### 21. List Heavy

- **Description**: Excessive conversion of prose into bullet lists.
- **AI version**: A 12-bullet list of abstract benefits.
- **Human version**: One short list with a sentence of context.
- **Detection**: List-item line ratio.
- **Severity**: LOW

### 22. Empty Concluding Sentences

- **Description**: Final sentences that restate importance without adding information.
- **AI version**: "This demonstrates the importance of careful planning."
- **Human version**: "We ship the release only after the smoke tests pass on staging."
- **Detection**: Regex for `This demonstrates`, `This highlights`, `This underscores`.
- **Severity**: HIGH

### 23. Syntactic Repetition

- **Description**: Three or more consecutive sentences start with the same word or phrase.
- **AI version**: "The model achieves X. The model handles Y. The model scales to Z."
- **Human version**: "The model achieves X. Edge cases need a fallback path. At scale, throughput degrades linearly."
- **Detection**: Sentence-starter repetition within a paragraph.
- **Severity**: MEDIUM

### 24. Em-Dash Abuse

- **Description**: Dashes used to manufacture emphasis or false contrast.
- **AI version**: "This is the solution—the only way forward—to solve our problems."
- **Human version**: "This solution fixes the memory leak by replacing the default allocator."
- **Detection**: Regex for repeated or clause-spanning em-dashes.
- **Severity**: LOW

---

## Using This Catalog

- The Stage 1 script (`detect_ai.py`) implements the regex/heuristic rules marked above.
- The Stage 2 LLM prompt uses the flagged Stage 1 results plus this catalog to produce qualitative pattern names, quotes, and fix suggestions.
- Do not treat any single pattern as proof of AI authorship. Severity and clustering matter.
