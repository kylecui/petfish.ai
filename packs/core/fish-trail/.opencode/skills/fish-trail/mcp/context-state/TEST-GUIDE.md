# Fish-Trail Tiered Memory v2 — Test Guide

> **For**: QA/测试团队  
> **Branch**: `feat/fish-trail-tiered-memory-v2`  
> **Status**: Phase 3 Task 1 complete (269/269 tests passing)  
> **Date**: 2026-05-20  

---

## 1. Quick Start

```bash
# 进入项目目录
cd packs/core/fish-trail/.opencode/skills/fish-trail/mcp/context-state/

# 运行全部测试（约2秒）
uv run pytest -v

# 运行单个测试文件
uv run pytest test_memory_context.py -v

# 运行带覆盖率
uv run pytest --cov=. --cov-report=term-missing
```

**前置要求**: 已安装 `uv`（项目唯一Python环境管理工具）

---

## 2. 架构概览

### 2.1 模块关系图

```
┌─────────────────────────────────────────────────────────┐
│                    server.py                             │
│              (MCP Server 入口)                           │
│  接收tool调用 → 路由到各handler → 返回结果              │
└────────┬──────────┬──────────┬──────────┬───────────────┘
         │          │          │          │
         ▼          ▼          ▼          ▼
┌──────────┐ ┌────────────┐ ┌──────────┐ ┌────────────────┐
│TopicReg  │ │MemoryCtx   │ │Consolid. │ │OutputFormatter │
│  V2      │ │  Provider  │ │  Gate    │ │                │
└──────────┘ └────────────┘ └──────────┘ └────────────────┘
         │          │          │
         ▼          ▼          ▼
┌──────────┐ ┌────────────┐ ┌──────────────────┐
│Migration │ │MemPressure │ │  FeatureFlags    │
│v1→v2     │ │  Monitor   │ │(全局开关控制)     │
└──────────┘ └────────────┘ └──────────────────┘
```

### 2.2 核心模块说明

| 模块 | 文件 | 职责 |
|------|------|------|
| **TopicRegistryV2** | `topic_registry_v2.py` | 话题注册表，管理topic生命周期、层级(hot/warm/cold/archive)、访问频率追踪 |
| **MemoryContextProvider** | `memory_context.py` | 根据话题层级和token预算，生成分层上下文（热话题详细，冷话题摘要） |
| **MemoryPressureMonitor** | `memory_pressure_monitor.py` | 监控内存压力，触发compaction（压缩）和tier降级 |
| **ConsolidationGate** | `consolidation_gate.py` | 决策门：判断何时触发consolidation，基于压力阈值和冷却时间 |
| **OutputFormatter** | `output_formatter.py` | 将分层上下文格式化为最终输出（Markdown/structured） |
| **FeatureFlags** | `feature_flags.py` | 全局功能开关，控制v2启用、v1回退、连续检测等 |
| **MigrationV1toV2** | `migration_v1_to_v2.py` | v1数据格式自动迁移到v2，含备份和回滚 |
| **ContextStateServer** | `server.py` | MCP server主入口，31个tool handler |

### 2.3 数据流

```
用户消息 → topic_detect → TopicRegistryV2 (更新访问记录)
                                    │
                    MemoryPressureMonitor (检查压力)
                                    │
                        ┌───────────┴───────────┐
                        │ 压力低               │ 压力高
                        │ 正常返回             │
                        │                     ▼
                        │           ConsolidationGate
                        │           (是否触发压缩?)
                        │                     │
                        │                     ▼
                        │           TopicRegistryV2
                        │           (tier降级: hot→warm→cold→archive)
                        │                     │
                        ▼                     ▼
                    MemoryContextProvider
                    (按tier分配token预算)
                              │
                              ▼
                      OutputFormatter
                      (格式化输出)
```

### 2.4 Feature Flags（功能开关）

| Flag | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `v2_enabled` | bool | `True` | 启用v2分层内存系统 |
| `v1_fallback_on_error` | bool | `True` | v2出错时自动回退v1 |
| `enable_continuous_detection` | bool | `True` | 启用连续话题检测 |
| `consolidation_enabled` | bool | `True` | 启用自动压缩 |
| `pressure_monitoring_enabled` | bool | `True` | 启用压力监控 |

---

## 3. 测试文件详解

### 3.1 测试矩阵（269 tests total）

| 测试文件 | 测试数 | 覆盖模块 | 关注点 |
|----------|--------|----------|--------|
| `test_topic_registry_v2.py` | 37 | TopicRegistryV2 | 注册/查询/tier管理/访问追踪/持久化 |
| `test_memory_context.py` | 28 | MemoryContextProvider | 分层上下文生成/token预算分配/tier策略 |
| `test_memory_pressure_monitor.py` | 49 | MemoryPressureMonitor | 压力计算/阈值触发/冷却期/降级建议 |
| `test_consolidation_gate.py` | 37 | ConsolidationGate | 门控决策/压力联动/冷却时间/强制触发 |
| `test_output_formatter.py` | 32 | OutputFormatter | Markdown格式/结构化输出/tier标注/截断 |
| `test_feature_flags.py` | 44 | FeatureFlags | 开关组合/动态切换/配置加载/hash一致性 |
| `test_migration_v1_to_v2.py` | 24 | MigrationV1toV2 | v1检测/自动迁移/备份/回滚/边界条件 |
| `test_integration_v2.py` | 18 | 端到端集成 | 模块协作/完整流程/回退机制 |

### 3.2 各文件核心测试场景

#### `test_topic_registry_v2.py` (37 tests)
- Topic CRUD操作（创建、读取、更新、删除）
- Tier管理（hot/warm/cold/archive 四层晋升和降级）
- 访问频率追踪和衰减
- 持久化/加载（JSON序列化/反序列化）
- v1格式自动检测和迁移触发
- 元数据（session_id, config_hash）

#### `test_memory_context.py` (28 tests)
- 按tier分配token预算（hot获得更多token）
- 空注册表处理
- 单topic和多topic场景
- Token预算不足时的降级策略
- MemoryContextResult数据结构验证

#### `test_memory_pressure_monitor.py` (49 tests)
- 压力值计算（topic数量 × 平均大小 / 容量）
- 多级阈值（low/medium/high/critical）
- 冷却期（触发后N秒内不重复触发）
- 降级建议生成（哪些topic该降级）
- 边界条件（0 topic、1 topic、极大topic）

#### `test_consolidation_gate.py` (37 tests)
- 门控决策逻辑（should_consolidate返回bool）
- 与压力监控的联动
- 冷却时间遵守
- 强制触发（override_cooldown）
- Feature flag禁用时的行为

#### `test_output_formatter.py` (32 tests)
- Markdown输出格式验证
- Tier标注（🔥hot / 💤warm / 🧊cold）
- Token截断策略
- 空上下文处理
- 结构化JSON输出模式

#### `test_feature_flags.py` (44 tests)
- 所有flag的默认值
- 动态切换（运行时修改flag）
- 从配置文件加载
- Flag组合效果（v2_enabled=False时其他flag不生效）
- Config hash计算（配置变更检测）

#### `test_migration_v1_to_v2.py` (24 tests)
- v1格式检测（version字段缺失或为1）
- 完整迁移流程（v1→v2格式转换）
- 备份创建（迁移前自动备份）
- 回滚能力（迁移失败时恢复）
- 边界：空文件、损坏JSON、已是v2格式
- 迁移幂等性（多次运行结果一致）

#### `test_integration_v2.py` (18 tests)
- 完整流程：注册topic → 压力检测 → 门控决策 → 生成上下文
- Feature flag组合对流程的影响
- v1 fallback路径验证
- 错误恢复（模块异常时的优雅降级）

---

## 4. 与评估计划的映射

参见 `dev_reference/fish-trail_revise/04-evaluation-qa-plan.md`

### 4.1 产品功能验证（Part 2）对应关系

| 评估计划要求 | 当前测试覆盖 | 状态 |
|-------------|-------------|------|
| Topic层级管理 | `test_topic_registry_v2.py` | ✅ 已覆盖 |
| 分层上下文生成 | `test_memory_context.py` | ✅ 已覆盖 |
| 压力监控与自动降级 | `test_memory_pressure_monitor.py` | ✅ 已覆盖 |
| Consolidation触发机制 | `test_consolidation_gate.py` | ✅ 已覆盖 |
| 输出格式化 | `test_output_formatter.py` | ✅ 已覆盖 |
| Feature flag控制 | `test_feature_flags.py` | ✅ 已覆盖 |
| v1→v2迁移 | `test_migration_v1_to_v2.py` | ✅ 已覆盖 |
| 端到端集成 | `test_integration_v2.py` | ✅ 已覆盖 |
| 性能基准（响应时间/内存） | — | ⏳ Phase 3 待完成 |
| 错误路径与回退 | 部分在integration | ⏳ Phase 3 待补充 |
| P4长会话实验 | — | ⏳ Phase 4 |

### 4.2 已覆盖的质量维度

- ✅ **功能正确性**: 269个单元+集成测试
- ✅ **向后兼容**: v1迁移测试（24个场景）
- ✅ **优雅降级**: feature flag + fallback测试
- ✅ **配置管理**: flag组合、动态切换、hash一致性
- ⏳ **性能**: 响应时间、内存占用基准（待Phase 3）
- ⏳ **压力测试**: 大量topic场景下的稳定性（待Phase 3）

---

## 5. 待完成测试（Phase 3 剩余 + Phase 4）

### Phase 3 剩余任务

1. **Eval Plan对齐**: 逐条核对 `04-evaluation-qa-plan.md` Part 2 所有test case是否有对应自动化测试
2. **性能基准**: 
   - 100/500/1000 topics时的响应时间
   - 内存占用随topic数量的增长曲线
   - Consolidation触发时的延迟
3. **错误路径补充**:
   - 磁盘满时的行为
   - JSON损坏时的恢复
   - 并发访问冲突

### Phase 4 任务

- P4长会话实验的自动化harness
- 端到端MCP integration test（真实server启动）
- 回归测试套件固化

---

## 6. 关键设计决策（测试时需了解）

| 决策 | 说明 | 测试影响 |
|------|------|----------|
| Tier层级为4级 | hot → warm → cold → archive | 测试需覆盖所有4级及转换 |
| v1检测逻辑 | `version is None` 或 `version == 1`(int) | 迁移测试需含两种v1格式 |
| v2版本标识 | 字符串 `"2.0"` | 不是整数2 |
| TopicEntry.state | 从JSON加载后为string，非Enum | 比较时用字符串 |
| FeatureFlags字段 | 无 `v2_memory_context` 字段 | 仅有上述5个flag |
| Server构造函数 | `ContextStateServer(base_dir: str)` 必须传路径 | 测试需提供tmp目录 |
| Fallback机制 | v2出错时回退v1，在try/except内 | 测试需模拟v2异常 |

---

## 7. 已知限制与注意事项

1. **Windows环境**: 开发和测试均在Windows上运行，路径使用反斜杠
2. **测试速度**: 全部269个测试在~2秒内完成，无需特殊优化
3. **无外部依赖**: 所有测试使用内存数据或tmp目录，无需数据库/网络
4. **Explore subagent不可用**: 如需代码搜索请直接用grep工具，勿使用explore agent

---

## 8. 联系方式

- **开发分支**: `feat/fish-trail-tiered-memory-v2`
- **最新commit**: `7e22bd4` (Phase 3 Task 1 complete)
- **规格文档**: `dev_reference/fish-trail_revise/03-product-spec-tiered-memory.md`
- **评估计划**: `dev_reference/fish-trail_revise/04-evaluation-qa-plan.md`
- **实验执行计划**: `dev_reference/fish-trail_revise/01-experiment-execution-plan.md`
