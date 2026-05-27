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

低于4分的段落必须改写。
