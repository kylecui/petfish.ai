# Scope Boundaries: Topic-Aware Compaction

> 关联 Brief: `research-brief.md` (TAC-2026-001)

---

## In Scope

### 必须覆盖

| 编号 | 范围项 | 说明 |
|------|--------|------|
| IS-1 | OpenCode plugin hook集成 | 通过 `experimental.session.compacting` 介入compaction，不修改OpenCode源码 |
| IS-2 | fish-trail数据复用 | 消费现有topic summary、Context Package、contamination score |
| IS-3 | Phase 1原型 | 实现MVP plugin：将active topic的Context Package注入 `output.context[]` |
| IS-4 | Token量化 | 至少1个真实多话题session的token对比测试 |
| IS-5 | 降级设计 | fish-trail MCP不可用时的graceful fallback |
| IS-6 | 配置兼容 | 与opencode.json现有compaction配置项共存 |

### 可选覆盖

| 编号 | 范围项 | 触发条件 |
|------|--------|---------|
| OPT-1 | Phase 2设计文档 | Phase 1验证成功后 |
| OPT-2 | Phase 3可行性评估 | Phase 2设计完成后 |
| OPT-3 | 上下文质量人工评估 | 有可对比的compaction输出后 |

---

## Out of Scope

| 编号 | 排除项 | 原因 |
|------|--------|------|
| OS-1 | 修改OpenCode核心代码 | 架构约束：仅通过plugin集成 |
| OS-2 | 修改fish-trail核心topic模型 | 本研究是消费者，不改变数据源 |
| OS-3 | Claude Code / Cursor集成 | 本研究聚焦OpenCode，其他平台另立项 |
| OS-4 | Compaction触发策略优化 | 研究优化compaction内容，不改变触发时机 |
| OS-5 | 完整RAG实现 | Phase 3的预计算摘要是简化方案，不涉及向量数据库或embedding |
| OS-6 | 多用户/多实例场景 | 仅考虑单用户本地开发场景 |
| OS-7 | OpenCode上游PR | 可提issue建议，不提交代码变更 |

---

## Constraints

### 技术约束

| 编号 | 约束 | 来源 |
|------|------|------|
| TC-1 | 必须通过OpenCode plugin hook集成 | 架构决策 — 不fork OpenCode |
| TC-2 | Plugin必须处理MCP不可用的情况 | fish-trail降级规则 |
| TC-3 | 不得破坏现有compaction行为 | Phase 1必须是纯增量 |
| TC-4 | 兼容opencode.json配置 | tail_turns, preserve_recent_tokens等 |
| TC-5 | Python环境使用uv管理 | 项目规则 |

### 项目约束

| 编号 | 约束 | 来源 |
|------|------|------|
| PC-1 | 不操作sst/opencode仓库 | 跨仓库保护规则 |
| PC-2 | 版本号遵循v0.10.x | 用户指定 |
| PC-3 | 研究产出遵循research-brief-framer规范 | skill约束 |

### 质量约束

| 编号 | 约束 | 说明 |
|------|------|------|
| QC-1 | Token数据必须来自实际运行或精确模拟 | 不接受粗略估算 |
| QC-2 | 源码分析标注commit SHA | 可追溯性 |
| QC-3 | 接口行为通过实际调用验证 | 不仅依赖文档 |

---

## Assumptions

以下假设如果不成立，可能影响研究结论：

| 编号 | 假设 | 验证方式 | 风险 |
|------|------|---------|------|
| A-1 | OpenCode plugin hook在compaction时能访问session ID | Phase 1原型验证 | 高 — 如不成立，无法关联fish-trail数据 |
| A-2 | `output.context[]`的内容会被包含在compaction prompt中 | 源码分析 + 实际测试 | 高 — 如不成立，Phase 1无法注入上下文 |
| A-3 | `output.prompt`可以完全替换默认compaction prompt | 源码分析 + 实际测试 | 中 — 如不成立，Phase 2需要替代方案 |
| A-4 | fish-trail的topic summary在compaction触发时是最新的 | 检查topic_update调用频率 | 中 — 如过时，摘要质量下降 |
| A-5 | 多话题session是常见使用模式 | 用户反馈 | 低 — 已有用户场景佐证 |

---

## Decision Points

研究过程中需要做出的关键决策：

| 编号 | 决策点 | 触发条件 | 选项 |
|------|--------|---------|------|
| DP-1 | 是否继续到Phase 2 | Phase 1验证完成 | Go / Pivot / Stop |
| DP-2 | Context Package格式是否需要compaction专用变体 | Phase 1集成测试 | 复用现有 / 新建变体 |
| DP-3 | 是否向OpenCode提feature request | 集成表面不足时 | 提issue / workaround / 放弃 |
