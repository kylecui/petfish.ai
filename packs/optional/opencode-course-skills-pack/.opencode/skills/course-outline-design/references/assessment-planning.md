# 测评规划参考（assessment-planning）

> 定位：`course-outline-design` 的按需参考层。在大纲层规划课程测评时查用，**不内联进SKILL.md正文，不整篇塞进生成提示词**。题目级设计细节（题干规范、评分标准、题库组织）见 `course-assessment-design` skill。

## 1. 形成性/总结性配比框架

| 维度 | 形成性 Formative | 总结性 Summative |
|---|---|---|
| 目的 | 调整教学、给学员即时反馈 | 判定达标、评分/发证 |
| 时机 | 每课时/每模块内 | 模块边界/课程末 |
| 计分 | 低计分或不计分 | 正式计分 |
| 反馈 | 即时、具体、指向下一步 | 等级/分数+总评 |
| 容错 | 鼓励试错 | 控制失误影响 |

配比建议（按课程类型）：

- 标准培训 standard-training：形成性:总结性 ≈ 7:3（重过程反馈）
- 认证/应试类 certification：≈ 4:6（重终评，但形成性保底练习量）
- 工作坊 workshop：≈ 8:2（总结性以成果展示为主）

规划动作：在大纲的"Assessment / lab mapping"节，为每个模块标注至少1个形成性触点；总结性测评只出现在模块边界或课程末，不在课时内插入。

## 2. 题型-目标匹配矩阵

题型服务于目标层级（Bloom），不倒置——先定目标层级，再选题型。

| Bloom层级 | 首选题型（中/英） | 备选题型 | 反模式 |
|---|---|---|---|
| 记忆 Remember | 单选题 multiple-choice (MCQ) | 判断题 true-false | 用论述题考记忆（评分成本浪费） |
| 理解 Understand | 短答题 short-answer | 单选题（干扰项须来自真实误解） | 用MCQ考"理解"却只测再认 |
| 应用 Apply | 实验题 lab / performance task | 补全题 completion problem | 纸面MCQ冒充应用考核 |
| 分析 Analyze | 项目题 project / 案例分析 case analysis | 多选题 multiple-response（组合推理） | 无材料无数据的空泛"分析题" |
| 评价 Evaluate | 评审题 critique + 评分量表 rubric item | 论证型短答 | 无行为锚点的rubric |
| 创造 Create | 项目里程碑 project milestone + 验收清单 | 作品集 portfolio | 一次成型大项目、无checkpoint |

## 3. 与上下游的衔接

- 锚题（anchor items）：跨测评周期不变的抽样复测题（每库3-5题），用于①对比批次间得分、校准难度漂移，②作为间隔复测载体（核心概念换语境再现，对应 `course-content-authoring/references/pedagogy-compact.md` §5.2）；大纲层只声明复测点位，题目标记归 `course-assessment-design` 9字段之⑧。
- 题目级设计（9字段模式、题干规范、难度分布、锚题标记、题库组织）：路由到 `course-assessment-design`。
- 与labs的边界：labs重"做中学"（环境+步骤+验收），测评重"考所会"（目标绑定+计分）；项目里程碑类测评与labs共建时可双挂（lab提供练习场，assessment提供计分点）。
- 约束自检：`docs/00-project/course-type.yaml` 声明类型后，`course-quality-assurance/references/outline-constraints/` 预设中的 `required_assessment_types[]` 应与本矩阵"首选题型"列保持一致。

## 使用规则

- 本文件是参考层：规划测评时读取所需小节，不整篇加载，不进大纲正文。
