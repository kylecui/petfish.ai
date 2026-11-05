# 卡组 R — 证据阶段（论证、复现与反方证据）

衔接执行技能：research-evidence-ledger（证据账本）、research-synthesis（综合分析）。

---

### R01 主张—证据—担保三件套

- 主张: 每个研究主张都要能拆成 Claim（主张）、Evidence（证据）、Warrant（担保：为什么这条证据能支撑这个主张）三件，缺一件的论证是断的
- 原理: 读者默认只看到 Claim 和 Evidence，Warrant 缺失时"证据不支持结论"是最高频的审稿意见；显式写出 Warrant 能在写作期暴露论证断裂
- 怎么用: 对论文的每个核心主张做三行拆解；写不出 Warrant 的主张，要么补证据链，要么降级措辞
- 认同度: 有出处
- 出处: Toulmin, The Uses of Argument（主张-资料-担保论证模型）；Booth, Colomb & Williams, The Craft of Research（研究论证章节）
- 适用阶段: evidence
- 对抗式提问: 这条证据为什么能支撑这个主张，而不是仅仅"同时出现"？

---

### R02 可复现性清单前置

- 主张: 可复现性的十项要求（记录版本/环境、原始数据留存、脚本化全流程等）在研究开始时就要进设计，不是投稿前补
- 原理: 事后补可复现性的成本远高于前置；多数不可复现源于开始时没记录环境与随机种子等"当时显然"的信息
- 怎么用: 立项时把十条规则转成研究仓的目录约定（env 清单、data/、scripts/、results/ 分离）；每阶段结束对照自查
- 认同度: 有出处
- 出处: Sandve, Nekrutenko, Taylor & Hovig (2013), Ten Simple Rules for Reproducible Computational Research
- 适用阶段: evidence
- 对抗式提问: 半年后换一台机器，有人能仅凭你的仓库复现出同一张表吗？

---

### R03 综述按主张组织，不按论文罗列

- 主张: 文献综述的组织单元应当是"主题主张"，每段用多篇文献共同支撑一个主张；而不是一篇文献一段的流水账
- 原理: 按论文罗列只能证明"读过"，按主张组织才能显示"领域知识结构"；审稿人从前者的段落顺序直接判断综述质量
- 怎么用: 先列出领域的 5-8 个核心主张，每个主张下挂支持/反对文献（挂接 research-evidence-ledger 的 evidence_id）；写不出主张挂接的文献放进"背景阅读"而非正文
- 认同度: 有出处
- 出处: Booth, Colomb & Williams, The Craft of Research（以问题和主张组织综述的章节）
- 适用阶段: evidence
- 对抗式提问: 遮住作者名，你的综述段落还能看出"领域在争论什么"吗？

---

### R04 反方证据专门收集

- 主张: 与自己假设相反的证据要设专门的检索与收集流程，而不是等撞上才记录——反方证据的缺席本身要作为一项验证结果
- 原理: 确认偏差使研究者系统性低估反方证据；文献中存在大量"没有效果"的负结果因无人收集而被低估
- 怎么用: 在 research-source-discovery 的检索式里显式加入反方关键词；evidence-ledger 里为反方证据保留独立分区；综合时"未找到反方证据"要写成检索过的结论而非默认事实
- 认同度: 共识
- 出处: Ioannidis (2005), Why Most Published Research Findings Are False; Munafo et al. (2017), A manifesto for reproducible science; Open Science Collaboration (2015), Estimating the reproducibility of psychological science
- 适用阶段: evidence
- 对抗式提问: 如果你的假设是错的，最可能出现的反方证据长什么样？你检索过它吗？
