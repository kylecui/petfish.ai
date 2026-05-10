# Research Brief: Topic-Aware Compaction

> **研究编号**: TAC-2026-001
> **研究类型**: 产品研究（Product Research）
> **复杂度**: Standard
> **发起日期**: 2026-05-10
> **研究者**: PEtFiSh Team

---

## 1. Core Research Question

**fish-trail的话题管理机制能否增强OpenCode的compaction流程，使其在多话题长会话中显著减少token消耗并提高上下文质量？**

具体而言：当一个session包含多个交错话题时，现有compaction将所有内容无差别压缩。我们研究的是：利用fish-trail已有的topic模型、Context Package和contamination scoring，能否让compaction变为topic-aware，从而实现：
- 按话题结构化压缩，而非全量压缩
- 按当前话题相关性选择性保留上下文，而非盲目保留尾部
- 利用已有topic summary跳过LLM压缩，直接注入预计算摘要

---

## 2. Sub-Questions

### SQ1: 集成可行性
OpenCode的plugin hook（`experimental.session.compacting`）是否提供了足够的集成表面，使fish-trail能在不修改OpenCode核心代码的前提下介入compaction流程？

### SQ2: Token节约量化
在典型多话题session（4个话题，200K tokens）中，topic-aware compaction相比现有机制能减少多少compaction输入tokens？各阶段（注入、替换、跳过LLM）的节约分别是多少？

### SQ3: 上下文质量
topic-structured的压缩摘要是否比现有通用模板产生更高质量的上下文保留？质量如何衡量（信息保真度、话题隔离度、决策可追溯性）？

### SQ4: 实现路径
三阶段渐进设计（Phase 1: context注入 → Phase 2: prompt替换 → Phase 3: 跳过LLM）是否是最优实现路径？每阶段的风险和依赖是什么？

### SQ5: 边界条件
在哪些场景下topic-aware compaction可能表现不佳或不适用？（如：单话题session、话题边界模糊、topic summary过时）

---

## 3. Research Type & Approach

**类型**: 产品研究 — 评估现有能力（fish-trail）与目标平台（OpenCode）的集成可行性，量化收益，设计实现路径。

**方法**:
1. **源码分析**（已完成）: 逆向分析OpenCode compaction机制（触发条件、算法、hook接口、配置项）
2. **数据模型映射**（已完成）: 映射fish-trail的topic/session/context数据结构到compaction需求
3. **原型验证**（待执行）: 实现Phase 1 MVP plugin，在真实多话题session中测试
4. **量化对比**（待执行）: 对比baseline vs topic-aware的token消耗和上下文质量

---

## 4. Scope

### In Scope

- OpenCode `experimental.session.compacting` plugin hook的集成设计
- fish-trail现有数据（topic summary, Context Package, contamination score）的复用
- 三阶段渐进实现路径的设计与Phase 1原型
- Token节约的量化估算与验证
- 上下文质量的评估框架

### Out of Scope

- 修改OpenCode核心代码（仅通过plugin接口集成）
- 修改fish-trail的核心topic模型（仅消费现有数据）
- Claude Code / Cursor等其他平台的compaction集成（本研究聚焦OpenCode）
- Compaction触发策略的优化（仅优化compaction执行内容）
- RAG式检索的完整实现（Phase 3的预计算摘要是简化版，不涉及向量检索）

### Constraints

- 必须通过OpenCode plugin hook集成，不fork OpenCode
- fish-trail MCP不可用时必须graceful降级，不阻塞compaction
- Phase 1必须是纯增量（enhance, not replace），不影响现有compaction行为
- 实现必须兼容opencode.json现有配置项（tail_turns, preserve_recent_tokens等）

---

## 5. Expected Output

| 产出物 | 格式 | 用途 |
|--------|------|------|
| 研究报告 | Markdown | 完整分析、设计方案、量化数据 |
| Plugin设计文档 | Markdown | Phase 1-3的技术设计 |
| Phase 1原型代码 | TypeScript | OpenCode plugin实现 |
| Token对比数据 | JSONL/表格 | 量化验证结果 |
| 集成指南 | Markdown | 用户如何启用topic-aware compaction |

---

## 6. Evidence Requirements

### 必须提供的证据

- **E1**: OpenCode plugin hook的完整接口签名与行为验证（源码级）
- **E2**: fish-trail Context Package在compaction场景下的数据完整性验证
- **E3**: 至少1个多话题session的token消耗对比数据（baseline vs Phase 1）
- **E4**: Phase 1 plugin的功能验证（注入成功、降级正常、不破坏现有行为）

### 可选证据

- **E5**: Phase 2/3的token节约模拟估算
- **E6**: 上下文质量的人工评估（信息保真度打分）
- **E7**: 与其他compaction增强方案（如纯RAG）的对比

### 证据质量标准

- 所有token数据必须来自实际运行或精确模拟，不接受粗略估算
- 源码分析必须标注commit SHA
- 接口行为必须通过实际调用验证，不仅依赖文档

---

## 7. Acceptance Criteria

本研究在满足以下全部条件时视为完成：

1. **可行性判定**: 明确回答"fish-trail能否通过OpenCode plugin hook介入compaction"（Yes/No/Conditional）
2. **量化收益**: 提供至少1个真实场景的token节约数据，误差≤20%
3. **设计方案**: Phase 1的完整技术设计，包含接口定义、数据流、降级策略、配置项
4. **原型验证**: Phase 1 plugin可运行，通过功能验证（注入、降级、兼容性）
5. **风险披露**: 明确列出已知风险、边界条件和未验证假设

---

## Appendix: Prior Analysis Summary

### 已识别的三个Token浪费

1. **无差别压缩 (Topic-Blind)**: 多话题内容混合压缩，摘要质量被稀释
2. **盲目尾部保留 (Blind Tail)**: 保留最后2轮对话，不考虑话题相关性
3. **无结构摘要 (Unstructured Summary)**: 通用模板，不按话题组织

### 三阶段设计概要

| Phase | 策略 | Token节约 | 风险 |
|-------|------|-----------|------|
| 1 (MVP) | 注入topic context到`output.context[]` | ~15% | 低 — 纯增量 |
| 2 (Replace) | 用topic-structured prompt替换默认prompt | ~60% | 中 — 替换默认行为 |
| 3 (Skip LLM) | 预计算摘要，跳过LLM compaction | ~95% | 高 — 依赖summary质量 |

### OpenCode集成表面

- Hook: `experimental.session.compacting` → `output.context[]` (append) / `output.prompt` (replace)
- Config: `agents.compaction.model`, `compaction.auto`, `compaction.tail_turns`
- Source: `sst/opencode` SHA `ce89bcb8`
