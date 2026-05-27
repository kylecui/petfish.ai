# Fish-Trail Tiered Memory v2 — Development TODO

## Deferred Items (from spec review)

### Architectural Decisions (Applied ✓)
- [x] §6.1 MCP-primary integration (Patch 2)
- [x] §6.4 Plugin system descoped to v3 (Patch 1)

### In-Flight Conditions (must address during development)

- [ ] **Per-component feature flags** — §5 Migration需要per-component开关（Registry/Pressure/Eviction/Budget各自独立启停），spec当前只有全局`enabled`开关
- [ ] **Eval plan patch** — Budget Allocator仅5 runs不够（建议≥15），需补充error-path覆盖（10个场景中2个insufficient）、migration rollback test、fallback degradation test
- [ ] **Eviction semantics明确化** — §3.3 Eviction Manager的"archive"语义需与v1 `topic_archive` MCP tool对齐，明确eviction后topic是否仍可通过MCP查询

### Future Optimization (DEFERRED)
- [ ] §6.x OpenCode Compaction Lifecycle Hook — 等待上游支持后可将memory注入从每次交互优化为compaction-time构建
- [ ] §6.4 Plugin Interface — v3再引入，当前v2保持closed architecture

## Development Roadmap

### Phase 1: Foundation (Week 1-3)
- [ ] Topic Registry数据结构与持久化
- [ ] Memory Pressure Monitor基础实现
- [ ] `get_memory_context()` MCP tool实现
- [ ] Per-component feature flags框架

### Phase 2: Core Logic (Week 4-7)
- [ ] Tiered state machine (hot→warm→cold→archive)
- [ ] Budget Allocator算法
- [ ] Eviction Manager（对齐v1 archive语义）
- [ ] Companion Gateway集成

### Phase 3: Quality & Migration (Week 8-10)
- [ ] v1→v2 migration路径实现
- [ ] Eval plan执行（P0-P4 academic + product验证）
- [ ] Performance benchmark（latency/accuracy targets）
- [ ] Error path与fallback测试

### Phase 4: Hardening & Release (Week 11-12)
- [ ] Golden scenario回归测试
- [ ] Documentation更新
- [ ] fish-trail pack集成
- [ ] Release candidate
