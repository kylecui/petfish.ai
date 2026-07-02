# Research Skill Pack Rules

本项目已安装研究工作台技能包（research-skill-pack）。

## 工作原则

- 先定义问题，再搜集资料
- 先合法获取全文，再摘录原文与出处
- 先记录阅读笔记和灵光闪现，再提升为正式证据
- 先建立证据账本，再形成判断
- 先区分事实、推断、灵感、假设与建议，再写报告
- 生成与审查分离
- skill本体短小精确，复杂知识放入references与scripts

## 默认研究流程

```
research-router → research-brief-framer → research-source-discovery → research-literature-access → research-note-capture → research-insight-log → research-evidence-ledger → research-synthesis → research-report-writer → research-quality-reviewer
```

## 证据类型系统

| Type | Meaning | Can enter report? |
|---|---|---|
| EXTRACTED | Directly from source | Yes, with citation |
| INFERRED | Derived from multiple facts | Yes, with reasoning |
| AMBIGUOUS | Conflicting sources | Yes, as uncertainty |
| PROPOSED | Our suggestion/hypothesis | Yes, labeled as recommendation |

## 必须遵守

- 每条重要claim必须有source_id和evidence_id
- 不得把模型常识当作研究事实
- 不得把摘要伪装成原文
- 不得存储明文凭据
- 不得使用非法来源获取文献
- 质量审查必须独立于报告生成
- 灵感不能直接当作事实进入报告

## 研究工作区结构

```
research/
  CONTEXT.md
  00_brief/
  01_sources/
  02_notes/
  03_evidence/
  04_methods/
  05_analysis/
  06_outputs/
  07_reviews/
  adr/
```

## Skill路由（强制）

### 必须遵守的路由规则

1. **研究意图必须首先路由到 research-router**：当用户表达研究、调研、文献、综述、竞品分析、市场分析、论文方向等研究意图时，**必须**首先路由到 `research-router`，由router判断研究类型后再分发到具体skill。不得跳过router直接调用下游skill。
2. **证据链路必须完整**：涉及证据收集和报告生成的任务，**必须**按照默认研究流程（router → brief → sources → ... → report → review）执行，不得跳过中间环节直接写报告。
3. **质量审查必须独立于生成**：`research-quality-reviewer` **必须**在 `research-report-writer` 之后独立运行，不得将生成与审查合并在同一步骤。
4. **研究意图 vs 普通搜索的冲突解决**：当用户请求可能同时匹配"搜索信息"和"做研究"时，以下信号判定为研究意图并路由到research-router：
   - 包含"研究"、"调研"、"综述"、"literature"、"survey"等明确研究词汇
   - 要求系统性分析、证据收集、对比评估
   - 涉及多来源交叉验证、方法设计、实验规划
   - 要求产出结构化报告或决策建议
5. **Agent自发研究同样必须路由**：当agent在执行复合任务时自行判断需要研究（如可行性分析、架构调研、技术选型、方案对比等），即使没有用户消息显式触发，**也必须**路由到 `research-router`。判断标准：agent的子任务目标包含"调研"、"分析可行性"、"对比方案"、"评估技术"、"了解现状"等研究性动作时，视为研究意图。不得因为是agent自发行为而跳过路由。

### 意图分类 → Skill路由映射

| 用户意图 | 必须路由到 |
|---|---|
| 模糊研究请求 | research-router |
| 需要定义研究问题 | research-brief-framer |
| 需要找资料 | research-source-discovery |
| 需要获取文献全文 | research-literature-access |
| 需要摘录和阅读笔记 | research-note-capture |
| 有想法要记录 | research-insight-log |
| 需要建立证据 | research-evidence-ledger |
| 需要综合分析 | research-synthesis |
| 需要写报告 | research-report-writer |
| 需要审查报告质量 | research-quality-reviewer |
| 需要引用审计或检查无证据断言 | research-citation-auditor |
| 需要文献综述或系统回顾 | scientific-literature-review |
| 需要找研究空白或贡献点 | scientific-gap-finder |
| 需要方法设计或验证路径 | scientific-methodology-designer |
| 需要实验设计或评价指标 | scientific-experiment-planner |
| 需要写论文或论文骨架 | scientific-paper-writer |
| 需要审稿自查或回复审稿人 | scientific-review-rebuttal |
| 需要用户研究、访谈、问卷或画像 | product-user-research |
| 需要竞品分析、市场分析或SWOT | product-competitor-analysis |
| 需要机会分析、JTBD或需求挖掘 | product-opportunity-mapper |
| 需要验证计划、MVP设计或假设验证 | product-validation-planner |
| 需要产品决策简报或go/no-go建议 | product-decision-brief |
| 需要环境扫描、PESTLE或趋势分析 | planning-environment-scanner |
| 需要利益相关方分析或参与策略 | planning-stakeholder-analyst |
| 需要情景规划或不确定性分析 | planning-scenario-planner |
| 需要政策研究或法规分析 | planning-policy-researcher |
| 需要技术评估或成熟度分析 | planning-technology-assessor |
| 需要战略路线图或里程碑规划 | planning-roadmap-developer |
| 需要定义学习目标或学习计划 | learning-goal-framer |
| 需要梳理前置知识或学习依赖 | learning-prerequisite-mapper |
| 需要发现和筛选学习资源 | learning-resource-discovery |
| 需要设计分阶段学习路径 | learning-path-designer |
| 需要设计练习任务或动手实操 | learning-practice-planner |
| 需要检查学习进度或阶段复盘 | learning-progress-reviewer |
| 需要定义决策问题和约束 | decision-brief-framer |
| 需要构建决策标准和权重 | decision-criteria-builder |
| 需要方案对比打分矩阵 | option-comparison-matrix |
| 需要生成最终决策建议 | decision-recommendation |
| 需要定义风险评估对象和边界 | risk-research-brief |
| 需要供应商或开源项目尽调 | vendor-source-diligence |
| 需要安全风险审查 | security-risk-review |
| 需要合规风险检查 | compliance-check |
| 需要总拥有成本和运营风险评估 | tco-operational-risk |
| 需要最终采用建议 | adoption-recommendation |
| 需要定义活动或体验目标 | experience-brief-framer |
| 需要场地或目的地研究 | venue-destination-research |
| 需要日程或行程规划 | schedule-itinerary-planner |
| 需要参与者体验设计或旅程优化 | participant-experience-designer |
| 需要后勤和风险预案 | logistics-risk-planner |
| 需要活动执行手册 | event-runbook-writer |
| 需要旅行规划领域增强 | travel-adapter |
| 需要会议筹备领域增强 | conference-adapter |
| 需要培训活动领域增强 | training-event-adapter |
| 需要内容选择领域增强 | content-selection-adapter |

## 数据格式约定

- 面向机器消费的数据技能（source-discovery、note-capture、evidence-ledger）默认使用 JSONL。
- JSONL 便于结构化校验、lint 检查、脚本处理与流水线拼接。
- 面向人类阅读的输出技能（brief-framer、synthesis、report-writer）默认使用 Markdown。
- Markdown 更适合叙述、审阅与协作编辑。
- 这是有意设计：JSONL 负责保存可追踪证据链，Markdown 负责呈现结论与洞见。
- 两种格式都有效，不存在“谁替代谁”。
- 选择原则：下游消费者是脚本就优先 JSONL；是读者/评审就优先 Markdown。
