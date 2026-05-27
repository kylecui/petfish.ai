# Context Package Specification

本文档定义Fish Trail的Context Package格式。

## 概述

Context Package是为特定topic生成的上下文摘要文件，Markdown格式，供agent在处理该topic时作为上下文输入。每个topic至多有一个活跃Context Package，存储在`.petfish/fish-trail/contexts/<topic-id>.context.md`。

## 设计原则

- Markdown格式：人可读，agent可直接消费
- 单文件：一个topic一个package，不拆分
- 可冻结：archive时生成不可变快照
- 可桥接：两个topic间可生成交叉上下文包

## Package格式

### 必填Section

```markdown
# Context Package: <topic-title>

## Topic Info

- **ID**: <topic-id>
- **Status**: <active|paused|archived>
- **Scope**: <scope description>
- **Created**: <ISO 8601>
- **Updated**: <ISO 8601>
- **Parent**: <parent-topic-id or "none">

## Summary

<当前话题的累积摘要，包含关键决策、进展和结论>

## Key Decisions

<本topic内做出的重要决策，每条一行>

## Active Context

<当前仍然相关的上下文信息：正在进行的工作、未解决的问题、待确认的事项>

## Related Topics

<关联topic列表，含关系类型>
```

### 可选Section

```markdown
## Constraints

<本topic的约束条件和边界>

## Files Involved

<本topic涉及的文件路径列表>

## Terminology

<本topic中的关键术语及其在此上下文中的含义>
```

## 三种变体

### 1. 标准包（Standard Package）

由`context_build`生成。包含单个topic的完整上下文。

用途：
- 恢复topic工作时加载上下文
- switch到已有topic时提供背景
- agent在交互前读取以理解当前工作状态

生成规则：
- 从topic对象提取Topic Info
- 从topic.summary生成Summary
- 从decision log中过滤当前topic的决策记录生成Key Decisions
- Active Context从最近N次交互中提取（N由topic交互深度决定）
- Related Topics从registry的links中过滤

### 2. 桥接包（Bridge Package）

由`context_build_bridge`生成。包含两个topic之间的交叉上下文。

文件名：`.petfish/fish-trail/contexts/<topic-a-id>_bridge_<topic-b-id>.context.md`

格式在标准包基础上增加：

```markdown
## Bridge Info

- **Source Topic**: <topic-a title> (<topic-a id>)
- **Target Topic**: <topic-b title> (<topic-b id>)
- **Shared Scope**: <两个topic scope的交集描述>

## Cross References

<两个topic中相互引用的概念、文件或决策>
```

生成规则：
- Shared Scope通过scope关键词交集计算
- Cross References从两个topic的summary和decision log中提取共现概念
- 只包含交叉部分，不包含各自独有的上下文

### 3. 导出包（Export Package）

由`context_export`生成。兼容`/handoff`命令格式，用于跨session传递上下文。

格式在标准包基础上增加：

```markdown
## Handoff Info

- **Exported At**: <ISO 8601>
- **Export Reason**: <用户指定或自动生成的导出原因>

## Session History

<最近的关键交互摘要，按时间排序>

## Next Steps

<建议的后续工作>
```

生成规则：
- Session History从decision log和topic更新历史中提取
- Next Steps从Active Context中的未解决项推导
- 导出后topic状态不变（不自动archive）

## 冻结机制

`context_freeze`将当前Context Package标记为不可变：

1. 复制当前`.context.md`为`.context.frozen.<timestamp>.md`
2. 冻结后的文件不再更新
3. topic状态设为`archived`
4. archive后的topic仍可被引用（通过summary和frozen package）

## 文件大小控制

Context Package的目标大小：

| 类型 | 目标大小 | 硬限制 |
|------|---------|--------|
| 标准包 | < 2KB | 5KB |
| 桥接包 | < 1KB | 3KB |
| 导出包 | < 3KB | 8KB |

超过目标大小时，summary和session history应自动压缩（保留最近和最重要的条目）。超过硬限制时警告用户。

## Context Package生命周期

```
topic创建 → 首次context_build → 交互中持续更新
                                    ↓
                              topic归档
                                    ↓
                           context_freeze（不可变快照）
                                    ↓
                           后续只读引用
```
