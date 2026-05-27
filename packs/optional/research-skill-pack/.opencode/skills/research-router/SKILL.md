---
name: research-router
description: 研究入口与任务路由器。根据用户请求判断研究类型（科学研究、产品研究、规划研究、学习研究、决策研究、风险采购研究、活动体验研究）、复杂度并推荐合适的研究skill链路。Use when the user says "研究", "帮我研究", "仔细研究", "research", "investigate", "survey", "lit review", "literature review", "调研", "文献", "综述", "竞品分析", "市场分析", "论文方向", "规划方案", or gives a vague research intent that needs routing to the correct research skill chain. Also triggers for agent-initiated research subtasks: feasibility study, architecture research, technology assessment, design research, fork analysis, approach comparison, state-of-the-art review, 可行性分析, 技术选型, 方案对比, 现状调研.
compatibility: opencode
license: Apache-2.0
---

## 作用/Purpose

作为研究任务的统一入口，先做任务判型与路由，再输出可执行的研究任务计划，避免一上来就搜资料或直接写结论。

## 触发场景/Trigger Scenarios

- 用户说“帮我研究一下… / 做调研 / 综述 / 竞品分析 / 规划方案 / 论文方向 / 市场分析”。
- 用户目标模糊，需要先结构化研究任务。
- 用户不确定该走科学研究、产品研究还是规划研究链路。
- Agent自发子任务涉及可行性分析、技术选型、方案对比、架构调研、现状了解等研究性动作。

## 输入/Input

- 用户原始请求与上下文约束（时间、交付对象、可用资源）。
- 可选：已有brief、历史结论、业务背景。

## 输出/Output

- `Research Task Plan`（Markdown），至少包含：
  - research_type（Scientific / Product / Planning / Mixed）
  - complexity_level（light / standard / full）
  - recommended_skill_chain
  - initial_questions
  - expected_artifacts
  - key_risks

## 工作流/Workflow

1. 解析用户意图，提取目标、对象、时限、交付偏好。
2. 分类研究类型（Scientific / Product / Planning / Mixed）。
3. 评估复杂度与范围（问题数量、证据要求、决策影响面）。
4. 选择推荐skill链路（轻量路线或完整路线）。
5. 生成`Research Task Plan`并明确下一步入口（如`research-brief-framer`）。
6. 参考 `routing-rules.md` 与 `research-type-taxonomy.md` 做一致性校验。

## 质量门禁/Quality Gates

- 必须明确 `research_type`。
- 必须给出 `recommended_skill_chain`。
- 必须定义 `expected_artifacts`。
- 不得直接输出最终研究报告。

## Gotchas/注意事项

- 不要把“产品研究”等同于“竞品分析”。
- 不要把“科学研究”等同于“找几篇论文总结”。
- 不要把“规划研究”等同于“写战略口号”。
- 未判型前，不要跳到资料收集或结论写作。
