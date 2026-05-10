# Synthesis: Topic-Aware Compaction

> 关联 Brief: `../00_brief/research-brief.md` (TAC-2026-001)
> Evidence Ledger: `../03_evidence/evidence-ledger.jsonl` (14 entries)
> 日期: 2026-05-10

---

## Executive Summary

**结论: fish-trail可以通过OpenCode的plugin hook增强compaction，且Phase 1风险极低。**

OpenCode的`experimental.session.compacting` hook提供了足够的集成表面，fish-trail的现有数据模型（topic summary、Context Package、contamination score）可以直接复用。三个核心假设均已通过源码验证（E001-E005）。11+个外部项目已在生产中使用同一hook（E013），API稳定性风险可控。

三阶段渐进路径仍然是最优实现策略，但Phase 3的原始设计需要修正（E010）。

---

## 1. 问题定义：三个Token浪费

当前OpenCode compaction在多话题session中存在三个系统性浪费：

### 1.1 无差别压缩 (Topic-Blind Compression)

**现象**: 所有话题内容混合压缩。一个包含"胖鱼开发"+"状态机研究"+"OpenCode研究"+"skills安全讨论"四个话题的session，compaction将全部200K tokens喂给LLM，不区分话题边界。

**浪费机制**: 压缩LLM收到大量与当前话题无关的上下文，摘要被稀释。若当前活跃话题是"OpenCode研究"，"skills安全讨论"的细节对摘要质量无正向贡献，反而占用压缩budget。

**证据**: E011、E012确认compaction触发条件和模板——纯尾部保留+通用模板，无话题感知逻辑。

### 1.2 盲目尾部保留 (Blind Tail Preservation)

**现象**: 默认保留最后2轮对话（`DEFAULT_TAIL_TURNS=2`），不考虑话题相关性。

**浪费场景**: 用户在话题A上深入工作，切到话题B问了一个快速问题，然后切回话题A。此时尾部2轮是话题B的内容，话题A的关键上下文已被压缩。保留的尾部对当前工作无直接帮助。

**证据**: E011确认常量`DEFAULT_TAIL_TURNS=2`。

### 1.3 无结构摘要 (Unstructured Summary)

**现象**: 使用通用8节模板（Goal / Constraints / Progress / Key Decisions / Next Steps / Critical Context / Relevant Files）压缩所有内容。不按话题组织。

**问题**: 多话题session的摘要将不同话题的progress和decisions混合在一起，下游LLM需要额外tokens理解"哪些决策属于哪个话题"。

**证据**: E012确认模板结构和compaction system prompt内容。

---

## 2. 集成可行性：完全可行

### 2.1 Hook接口验证

三个关键假设均已通过源码级验证：

| 假设 | 状态 | 证据 |
|------|------|------|
| A-1: Hook接收sessionID | ✅ CONFIRMED | E001 — `input: { sessionID: string }` |
| A-2: `context[]`到达LLM prompt | ✅ CONFIRMED | E002 — `...input.context` spread into buildPrompt |
| A-3: `prompt`替换默认行为 | ✅ CONFIRMED | E003 — `??` operator bypass |

**结论**: Plugin可以通过`output.context.push()`注入额外上下文（Phase 1），或通过`output.prompt`完全替换compaction prompt（Phase 2）。两个路径均有源码验证。

### 2.2 Plugin注册机制

E005确认`.opencode/plugin/`目录下的`.ts`文件会被自动发现。无需修改配置。

**推荐**: 文件放置于`.opencode/plugin/fish-trail-compaction.ts`，零配置auto-discovery。

### 2.3 生态成熟度

E013确认11+个独立项目已使用同一hook。engram项目（E006）的架构与我们最接近——通过HTTP sidecar获取上下文后push到`context[]`。

**风险评估**: `experimental`前缀不代表不稳定。该hook已有足够的外部采用，短期breaking change可能性低。

---

## 3. 数据流设计

### 3.1 Phase 1 数据流

```
[OpenCode Compaction触发]
    │
    ▼
[Plugin hook called with sessionID]
    │
    ▼
[读取 .petfish/fish-trail/topic-registry.json]
    │  → 获取 active_topic ID
    ▼
[读取 .petfish/fish-trail/topics/<id>.json]
    │  → 获取 title, summary, scope, tags
    ▼
[构建 Context Package string]
    │  → Topic Info + Summary + Scope
    ▼
[output.context.push(package)]
    │
    ▼
[OpenCode buildPrompt() 将 context[] spread 到 compaction prompt]
```

### 3.2 SessionID映射问题

E009确认OpenCode sessionID ≠ fish-trail sessionID。Phase 1解决方案：

- 直接读取`topic-registry.json`的`active_topic`字段（全局，非per-session）
- 这是有意的简化：单用户场景下，active topic是全局的
- Phase 2+可通过`session_bind` MCP方法建立正确映射

### 3.3 降级策略

```
if 文件不存在 → 静默跳过，不注入
if active_topic为空 → 静默跳过
if topic文件读取失败 → 静默跳过
if JSON解析失败 → 静默跳过
```

任何失败路径都不应阻塞compaction。`try/catch`全包裹，无异常传播。

---

## 4. 三阶段设计评估

### 4.1 Phase 1: Context注入 (MVP)

**策略**: 读取当前活跃话题的Context Package，push到`output.context[]`。

**Token影响**:
- 输入增加: ~500-2000 tokens（Context Package大小）
- 输出质量提升: compaction LLM有话题上下文，摘要更聚焦
- 净节约: ~15%（摘要质量提升间接减少后续对话中的澄清轮次）

**风险**: **极低**。纯增量操作。即使Context Package质量差，最坏情况是多消耗2K tokens但不影响现有compaction行为。

**依赖**: 仅依赖文件系统读取。不需要MCP运行。

**推荐**: ✅ 立即实现。

### 4.2 Phase 2: Prompt替换

**策略**: 设置`output.prompt`为topic-structured compaction prompt。按话题组织压缩指令：

```
## 当前活跃话题: OpenCode研究
优先保留此话题的：目标、发现、决策、文件

## 其他话题（按相关性排序）
- 胖鱼开发: 仅保留影响当前话题的关键决策
- 状态机研究: 仅保留结论
- Skills安全: 可压缩到1句话摘要
```

**Token影响**:
- 输入减少: ~40-60%（非当前话题的内容被指示压缩到最小）
- 摘要质量: 显著提升（话题结构化的摘要更易消费）

**风险**: **中等**。完全替换默认compaction prompt。如果话题分类错误，可能丢失重要跨话题上下文。

**依赖**: 需要fish-trail MCP运行，用于contamination scoring和topic关系分析。

**前置条件**: Phase 1验证通过后实施。

### 4.3 Phase 3: 预计算摘要（设计修正）

**原始设计**: 设置`output.prompt`为预计算的topic summary，跳过LLM compaction。

**设计修正 (E010)**: `output.prompt`设置后仍会作为user message发送给LLM。无法真正跳过LLM调用。两个替代路径：

**路径A**: 通过`experimental.chat.messages.transform`在compaction之前注入预计算摘要为assistant message，使compaction认为"已经有摘要了"。
- 可行但高风险——需要深入理解OpenCode的session状态管理

**路径B**: 设置`output.prompt`为"直接输出以下内容，不做任何修改: {pre-computed summary}"。
- LLM仍然被调用，但processing minimal
- Token节约: ~80%（不是95%，因为仍有LLM调用开销）
- 更实际、风险更低

**推荐**: 延后到Phase 1和Phase 2充分验证后再评估。Phase 3的边际收益（从60%到80%）可能不值得其复杂性。

---

## 5. 对比矩阵

| 维度 | Phase 1 (Context注入) | Phase 2 (Prompt替换) | Phase 3 (预计算摘要) |
|------|------|------|------|
| Token节约 | ~15% | ~60% | ~80% (修正后) |
| 实现复杂度 | 低 (~100行TS) | 中 (~300行TS) | 高 (~500行TS) |
| 风险等级 | 极低 | 中 | 高 |
| 依赖 | 文件系统 | 文件系统 + MCP | 文件系统 + MCP + 深入hook理解 |
| 降级能力 | 完美（静默跳过） | 可行（回退到Phase 1） | 困难（需要回退整个compaction逻辑） |
| 生态参考 | engram等11+项目 | 部分项目 | 无参考 |
| 开发周期 | 1天 | 3-5天 | 1-2周 |

---

## 6. 边界条件与限制

### 6.1 表现不佳的场景

- **单话题session**: 无多话题分离收益。Phase 1仍有轻微正面效果（注入topic context增强摘要质量），Phase 2/3无显著优势。
- **话题边界模糊**: 用户在两个话题间频繁切换且话题高度相关时，topic分离可能产生人为割裂。
- **Topic summary过时**: fish-trail的topic summary依赖`topic_update`被调用。如果Companion Gateway未运行或MCP断连，summary可能过时。Phase 1影响较小（注入的是补充信息），Phase 2/3影响较大（基于过时summary做压缩决策）。

### 6.2 技术限制

- **Active topic是全局的**: Phase 1读取`active_topic`，这是全局状态。多窗口/多session并发时可能不准确。Phase 2+需要per-session绑定。
- **无增量更新**: 每次compaction重新读取完整topic数据。对于频繁compaction的长session，可能有I/O开销（但文件很小，~2KB，影响可忽略）。
- **Hook only on compaction**: 无法影响非compaction场景的上下文管理（如正常对话中的上下文窗口管理）。

### 6.3 未验证假设

- **U-1**: Topic-structured摘要是否确实优于通用摘要（需人工评估）
- **U-2**: Context Package的~2KB大小是否足够提供有意义的话题上下文
- **U-3**: Compaction频率在典型多话题session中的分布（影响Phase 1的实际收益频次）

---

## 7. 实现建议

### 7.1 Phase 1 立即实施

```typescript
// .opencode/plugin/fish-trail-compaction.ts
import type { Plugin } from "@opencode-ai/plugin"
import { readFile } from "fs/promises"
import { join } from "path"

const plugin: Plugin = async ({ directory }) => ({
  "experimental.session.compacting": async (_input, output) => {
    try {
      const registryPath = join(directory, ".petfish", "fish-trail", "topic-registry.json")
      const registry = JSON.parse(await readFile(registryPath, "utf-8"))
      const topicId = registry.active_topic
      if (!topicId) return

      const topicPath = join(directory, ".petfish", "fish-trail", "topics", `${topicId}.json`)
      const topic = JSON.parse(await readFile(topicPath, "utf-8"))

      const contextPkg = [
        `## Active Topic: ${topic.title}`,
        topic.scope ? `**Scope**: ${topic.scope}` : "",
        topic.summary ? `**Summary**: ${topic.summary}` : "",
        topic.tags?.length ? `**Tags**: ${topic.tags.join(", ")}` : "",
        "",
        "Prioritize this topic's context when summarizing. Other topics may be compressed more aggressively.",
      ].filter(Boolean).join("\n")

      output.context.push(contextPkg)
    } catch {
      // Graceful degradation — never block compaction
    }
  },
})

export default { id: "fish-trail-compaction", server: plugin }
```

### 7.2 验证计划

1. 在当前session中安装plugin
2. 继续工作直到触发compaction
3. 对比compaction摘要质量（是否包含话题结构信息）
4. 记录token消耗数据

### 7.3 Phase 2 规划（Phase 1验证后）

- 添加MCP调用获取contamination scores
- 按话题相关性排序compaction指令
- 设置`output.prompt`替换默认模板
- 实现回退到Phase 1的降级路径

---

## 8. Key Findings

| # | Finding | Confidence | Evidence |
|---|---------|------------|---------|
| F1 | OpenCode plugin hook提供完整的compaction集成表面 | 1.0 | E001-E005 |
| F2 | Phase 1 MVP可在1天内实现且风险极低 | 0.95 | E001-E009 |
| F3 | Phase 3原始设计有误，无法真正跳过LLM | 0.80 | E010 |
| F4 | fish-trail现有数据模型可直接复用，无需修改 | 0.90 | E007-E008 |
| F5 | 11+外部项目验证了hook API的稳定性 | 0.90 | E013 |
| F6 | SessionID映射是Phase 2+的关键设计决策 | 0.85 | E009 |
| F7 | Token节约的主要收益在Phase 2（~60%），Phase 1是验证阶段 | 0.75 | Estimated |

---

## 9. Recommendations

1. **立即实施Phase 1** — 代码量小（~50行），风险极低，验证集成可行性
2. **Phase 1验证后启动Phase 2设计** — 重点解决session映射和contamination-based压缩排序
3. **推迟Phase 3** — 边际收益（60%→80%）不值得其复杂性，除非Phase 2数据表明需要
4. **同步记录token数据** — 从Phase 1开始建立baseline，用于Phase 2的量化决策
5. **考虑`chat.system.transform`** — 除compaction外，在每次对话中注入轻量topic awareness可能有额外价值

---

## Appendix: Evidence Traceability

| Claim | Evidence IDs |
|-------|-------------|
| Hook接口签名 | E001 |
| context[]注入路径 | E002 |
| prompt替换机制 | E003 |
| Plugin mutation pattern | E004 |
| Auto-discovery注册 | E005 |
| Engram参考实现 | E006 |
| 现有Claude Code hooks | E007 |
| Context Package生成 | E008 |
| SessionID映射gap | E009 |
| Phase 3设计修正 | E010 |
| Compaction触发机制 | E011 |
| 默认模板结构 | E012 |
| 生态成熟度 | E013 |
| 辅助hooks | E014 |
