<!-- BEGIN pack: research-skill-pack -->
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

## Skill路由

| 用户意图 | 推荐skill |
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
<!-- END pack: research-skill-pack -->
