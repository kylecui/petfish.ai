# Research Pack 三层架构模式

本文档记录research skill pack采用的三层架构设计，供后续pack设计参考。

## 架构概览

```
┌─────────────────────────────────────────────┐
│  Adapter Layer（适配层）                      │
│  轻量SKILL.md-only，无脚本/schema/references │
│  travel-adapter, conference-adapter, ...     │
├─────────────────────────────────────────────┤
│  Mode Layer（模式层）                         │
│  按问题类型组织的domain-specific链路          │
│  scientific, product, planning, learning,    │
│  decision, risk-procurement, experience-event│
├─────────────────────────────────────────────┤
│  Core Layer（核心层）                         │
│  10个可复用pipeline skill                    │
│  research-router, source-finder,             │
│  evidence-evaluator, synthesis-writer, ...   │
└─────────────────────────────────────────────┘
```

## 设计原则

### 1. 按问题类型抽象，不按生活领域拆分

错误做法：为travel、shopping、health各建一套完整pipeline → skill爆炸、大量重复。

正确做法：按问题类型（learning、decision、risk）建pipeline，领域差异通过adapter层解决。

### 2. 三层职责分离

| 层 | 职责 | 内容 | 数量 |
|---|------|------|------|
| Core | 通用研究pipeline | SKILL.md + schemas + scripts + references | 10 |
| Mode | 领域链路编排 | SKILL.md + schemas + references（部分有scripts） | ~36 |
| Adapter | 领域增强 | 仅SKILL.md（无脚本/schema/references） | 4 |

### 3. Adapter的设计约束

Adapter是最轻量的skill类型：
- 只有SKILL.md，不含scripts/、references/、schemas/
- 不独立触发，只在主链路中被router注入
- 负责注入domain-specific字段和checklist（如travel的签证/保险提醒）
- 新增领域 = 新增一个SKILL.md文件，不需要改动core或mode层

### 4. Core pipeline skill不需要trigger eval

Core skill通过router链式调用，不由用户直接触发。因此：
- 43/50 skill有trigger eval（用户可触发的）
- 7 core pipeline skill无trigger eval（设计如此）

## 实际规模

- 50 skills总计
- 7个domain（scientific, product, planning, learning, decision, risk-procurement, experience-event）
- 4个adapter（travel, conference, training-event, content-selection）
- 无跨层重复

## 适用场景

当需要设计一个覆盖多个领域的skill pack时，优先考虑此三层模式：
1. 先抽象出通用pipeline（Core）
2. 按问题类型建链路（Mode）
3. 用adapter注入领域差异

避免为每个领域复制一整套pipeline。
