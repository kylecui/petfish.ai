# Naming Convention Rules

## Terminology governance

For each important concept, maintain one preferred term and known aliases.

Example:

```yaml
preferred_terms:
  AI智能体:
    aliases:
      - AI Agent
      - Agent
      - 智能代理
    rule: "中文正文中优先使用AI智能体；首次出现可写作AI智能体（AI Agent）。"
```

## File naming

Infer file naming from the baseline series. Common acceptable patterns:

- `01-introduction.md`
- `01_引言.md`
- `chapter-01-introduction.md`
- `第01章-引言.md`

Do not rename files automatically unless the user asks. Report suggested renames separately.

## Chapter naming

Chapter titles should be parallel in granularity and tone.

Bad drift:

- `第1章 背景与意义`
- `第二章 我们终于要讲核心技术了`
- `Chapter 3: The Big Amazing Solution`

Better:

- `第1章 背景与意义`
- `第2章 核心问题分析`
- `第3章 技术方案设计`

## Concept naming

Do not collapse near terms without analysis:

- `控制平面` and `管理平面` may be different.
- `数据平面` and `执行平面` may overlap but are not always identical.
- `策略执行点` and `网关` may refer to different implementation roles.

Mark ambiguous replacements as `review-needed`.
