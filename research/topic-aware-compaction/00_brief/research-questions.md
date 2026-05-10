# Research Questions: Topic-Aware Compaction

> 关联 Brief: `research-brief.md` (TAC-2026-001)

---

## Core Question (CQ)

**fish-trail的话题管理机制能否增强OpenCode的compaction流程，使其在多话题长会话中显著减少token消耗并提高上下文质量？**

---

## Sub-Questions

### SQ1: 集成可行性

**OpenCode的plugin hook是否提供了足够的集成表面？**

| 维度 | 具体问题 |
|------|---------|
| 接口能力 | `experimental.session.compacting` 的 `output.context[]` 和 `output.prompt` 分别能做什么？两者能否同时使用？ |
| 数据可达 | Plugin执行时能否访问session历史？能否获取当前session ID以关联fish-trail数据？ |
| 时序 | Plugin在compaction流程中的执行时机是什么？在LLM调用前还是后？ |
| 降级 | Plugin抛出异常时，OpenCode是否fallback到默认compaction？ |
| 配置 | 用户如何启用/禁用plugin？是否需要修改opencode.json？ |

**验收标准**: 能够画出完整的plugin调用时序图，标注每个hook的输入/输出和异常处理。

---

### SQ2: Token节约量化

**Topic-aware compaction能减少多少compaction输入tokens？**

| 维度 | 具体问题 |
|------|---------|
| Baseline | 现有compaction在4话题/200K session中，输入LLM的token量是多少？ |
| Phase 1 | 注入Context Package后，compaction质量提升但输入token量是否变化？ |
| Phase 2 | 用topic-structured prompt替换默认prompt，输入token量减少多少？ |
| Phase 3 | 跳过LLM直接使用预计算摘要，输入token量减少多少？ |
| 边际效益 | 话题数量从2→4→8时，节约比例如何变化？是否存在拐点？ |

**验收标准**: 至少1个真实场景的精确token对比数据（baseline vs Phase 1），误差≤20%。

---

### SQ3: 上下文质量

**Topic-structured的压缩摘要质量是否优于通用模板？**

| 维度 | 具体问题 |
|------|---------|
| 信息保真度 | 压缩后是否丢失了关键决策、约束或上下文？ |
| 话题隔离度 | 不同话题的信息是否被正确分离，而非混合？ |
| 可追溯性 | 压缩后的摘要是否保留了足够的信息用于继续当前话题？ |
| 评估方法 | 如何量化"上下文质量"？是否需要人工评估？ |

**验收标准**: 定义至少3个质量维度的评估方法，并在Phase 1验证中应用。

---

### SQ4: 实现路径

**三阶段渐进设计是否是最优路径？**

| 维度 | 具体问题 |
|------|---------|
| Phase依赖 | Phase 2是否必须依赖Phase 1的经验？能否直接跳到Phase 2？ |
| 风险递增 | 每个Phase引入的新风险是什么？如何缓解？ |
| 回滚策略 | 每个Phase如果效果不佳，如何回退到上一Phase？ |
| 替代路径 | 是否存在其他实现路径（如纯RAG、纯规则、hybrid）比三阶段更优？ |

**验收标准**: 每个Phase有明确的入口条件、退出条件和回滚方案。

---

### SQ5: 边界条件

**Topic-aware compaction在哪些场景下失效？**

| 场景 | 问题 |
|------|------|
| 单话题session | 是否退化为等价于默认compaction？额外开销是否可接受？ |
| 话题边界模糊 | 当两个话题高度交织时，topic-aware是否反而产生信息丢失？ |
| Topic summary过时 | 如果topic_update不及时，预计算摘要的时效性如何保证？ |
| MCP不可用 | fish-trail MCP连接失败时，降级行为是否平滑？ |
| 极短session | Session很短（<10轮）时，compaction不触发，plugin是否有副作用？ |

**验收标准**: 每个边界场景有明确的预期行为描述和降级策略。

---

## Question Dependencies

```
CQ
├── SQ1 (集成可行性) ← 必须先回答，决定后续是否可行
├── SQ2 (Token量化) ← 依赖SQ1的接口理解
├── SQ3 (上下文质量) ← 依赖SQ1的实现方案
├── SQ4 (实现路径) ← 依赖SQ1+SQ2+SQ3的综合判断
└── SQ5 (边界条件) ← 贯穿所有SQ，独立可答
```

SQ1是阻塞性问题：如果集成可行性为No，后续SQ2-4无需深入。SQ5独立于可行性判断，任何结论下都需要回答。
