# Paper Writing Rules for Evidence-Backed Scientific Drafting

这份规则面向“已有研究材料，准备写论文”的阶段。它的目标不是教你写漂亮句子，而是确保论文叙事与证据强度一致，避免常见投稿失败模式：贡献膨胀、对照组不公平、选择性报告、相关工作堆砌、局限性空话化。

## 1) Contribution must not exceed evidence

最核心规则：**你能声称多强，只取决于你证据有多强**。如果证据只覆盖某类数据集、某个系统规模或某些攻击类型，就不能把结论写成普适定律。

建议把每条贡献写成“可验证命题”：

- C1：在X场景中，相比强基线B，方法A把P99延迟降低Y%；
- C2：在分布漂移条件下，方法A保持Z%的召回；
- C3：实现层面把部署复杂度限制在N项配置以内。

这三条分别对应性能、稳健性、可部署性。每条都必须在evaluation中有明确结果支撑。若某条仅有定性证据，应降低表述强度（例如“indicates”“suggests”而非“proves”）。

## 2) Introduction is argument design, not storytelling

引言应按固定逻辑推进：**Problem → Gap → Insight → Contributions**。

- Problem：问题重要性和现实影响；
- Gap：现有方法在哪些条件下失效，证据来自哪些文献或实验事实；
- Insight：你抓到的机制性突破点；
- Contributions：可验证、可映射、可复核的条目。

常见错误是把引言写成背景综述，导致读者读完仍不知道论文到底解决了什么。纠偏方法是：每段末尾都问自己“这一段是否推进了论证？”如果不能推进，就删或移到background。

## 3) Related work must be thematic, not paper stacking

相关工作不是“我读过很多论文”的证明，而是“我知道你的工作坐标在哪里”的证明。禁止逐篇摘要堆叠。

推荐结构：

1. 按主题/方法族分组；
2. 每组先写该路线解决了什么；
3. 再写该路线在你的问题上为什么不够；
4. 最后写你与该组的关系（继承/替代/补足）。

并且要做覆盖审计：related work应覆盖 evidence ledger中核心来源的至少80%。如果覆盖率不足，通常意味着你把“支持自己观点的文献”挑了出来，而忽略了可能反驳你的路线。

## 4) Evaluation must respond to claims, not fill pages

评估章节常见失败是“实验很多，但主张没被回答”。

你需要一张 Claim–Evaluation Map：

- Claim C1 对应 E1、E2；
- Claim C2 对应 E3；
- Claim C3 对应 E4 + Ablation A1。

若有claim找不到对应实验，删claim或补实验。若有实验不支持任何claim，删实验或把它转为附录探索结果。

另外，evaluation中必须交代：

- baseline为何合理且公平；
- workload是否代表目标场景；
- 统计检验和效应量是否充分；
- 负结果或边界案例是否被报告。

## 5) Abstract must contain a concrete result

摘要不能停留在“we propose X”。至少给出一条定量结果或明确发现。例如：

- “Across three production-like workloads, our method reduces P99 latency by 18–26% compared to the strongest baseline while preserving detection recall within 1.2%.”

这样的句子让读者在30秒内判断论文价值。没有结果的摘要，在审稿中通常被视为贡献不清或证据不足。

## 6) Limitations must be genuine constraints

局限性不是“未来工作”占位符。真正有价值的局限性应包含：

- 适用条件（仅在某类网络拓扑/数据分布成立）；
- 失败场景（高噪声、极端负载、对抗策略变化）；
- 资源约束（算力、内存、部署前提）；
- 外部有效性风险（跨域泛化不确定）。

写出这些边界不会削弱论文，反而能提升可信度。审稿人更担心“你没看见边界”，而不是“你承认了边界”。

## 7) Anti-patterns and correction strategies

### A) Contribution inflation

症状：把局部改进写成范式突破。

纠偏：把结论收缩到证据覆盖范围，明确“in our setting”而非“in general”。

### B) Strawman baselines

症状：只选过时或弱基线。

纠偏：补充强基线，或解释不可复现实证据并给出替代比较。

### C) Selective reporting

症状：只报告最优结果，不报告失败run。

纠偏：报告多次运行统计、失败比例和边界场景。

### D) Limitation as future work

症状：把真实缺陷改写成“后续会做更好”。

纠偏：先写当前不能解决什么，再写后续可能方向。

### E) Related work laundry list

症状：逐篇列举，不形成比较维度。

纠偏：按主题重组并加入“我们相对位置”段。

## 8) Section-level checklist

### Title
- 是否准确反映方法和问题范围？

### Abstract
- 是否有定量结果或具体发现？
- 是否包含问题、方法、结果、边界？

### Introduction
- 是否清晰呈现problem-gap-insight链路？
- 贡献是否可验证？

### Related Work
- 是否按主题组织？
- 是否覆盖核心证据来源（>=80%）？

### Method / Design
- 机制是否可解释、可复现？

### Evaluation
- 每条贡献是否有对应结果？
- 是否披露公平性设置和统计处理？

### Limitations
- 是否包含真实约束与失败条件？

### Conclusion
- 是否回到研究问题而非重复摘要？

## 9) Practical writing protocol

建议按以下顺序写作，而不是从引言硬写到结论：

1. 先写 claim-evaluation map；
2. 再写 evaluation（事实层）；
3. 再写 method（解释层）；
4. 再写 related work（定位层）；
5. 最后写 introduction、abstract、conclusion（叙事层）。

这样做能减少“先写大话，再找证据补洞”的风险。

## 10) Final rule

科学论文写作的核心不是“文风高级”，而是“可反驳后仍成立”。如果每条主张都有证据映射、每个比较都公平、每个局限都真实、每个结论都有边界，你的草稿即使语言尚不完美，也已经具备学术可信度。反过来，语言再华丽，若证据链断裂，审稿人会迅速看穿。
