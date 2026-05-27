---
name: research-brief-framer
description: 将模糊研究意图转化为结构化research brief，明确研究问题、范围边界、证据要求与验收标准。Use when the user says "研究目标", "研究问题", "research brief", "研究计划", "启动研究", "研究任务", or when a vague research goal needs structuring into a formal research brief with core questions, sub-questions, scope boundaries, evidence requirements, and acceptance criteria.
compatibility: opencode
license: Apache-2.0
---

## 作用/Purpose

把“想研究什么”转成“如何可执行地研究”，形成可交接、可评审、可验收的研究brief。

## 触发场景/Trigger Scenarios

- 用户研究目标不清晰。
- 用户只有主题，没有研究问题。
- 用户要启动长期研究项目。
- 用户希望将研究任务交接给Agent执行。

## 输入/Input

- 用户目标陈述（topic/业务问题/决策场景）。
- 可选上下文：时间预算、资源限制、利益相关方、已有假设。

## 输出/Output

- `research-brief.md`
- `research-questions.md`
- `scope-boundaries.md`

## 工作流/Workflow

1. 解析用户目标，抽取研究对象与决策用途。
2. 判定研究类型（Scientific / Product / Planning / Mixed）。
3. 定义研究对象、边界、交付形式。
4. 拆解核心问题与可执行子问题。
5. 写明假设、约束与不确定性。
6. 定义证据要求（来源类型、质量标准、最低覆盖）。
7. 定义验收标准与完成判据。
8. 参照 `research-brief-template.md`、`research-questions-template.md` 与 `brief-quality-rubric.md` 完成校验。

## 质量门禁/Quality Gates

- 至少 1 个核心研究问题。
- 至少 3 个可执行子问题。
- 必须包含 In Scope 与 Out of Scope。
- 必须指定最终输出形式。
- 必须指定证据要求。

## Gotchas/注意事项

- 不要用口号替代研究问题。
- 子问题必须可验证、可落地，不要过于抽象。
- 范围边界不清会导致后续source discovery失控。
- 未定义验收标准时，不应宣称brief完成。
