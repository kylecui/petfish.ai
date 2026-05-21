# PEtFiSh v1.1.0 参考资料索引

> **用途**: 测试团队快速定位所有相关文件 | **分支**: feat/fish-trail-tiered-memory-v2 | **日期**: 2026-05-21

---

## 项目入口

| 文件 | 说明 |
|------|------|
| `AGENTS.md` | 项目开发纪律（Companion Gateway、Release、安全规则） |
| `README.md` | 项目总览、安装说明 |
| `.sisyphus/plans/petfish-next-stage-adjusted-plan.md` | 调整后开发计划（v1.2.0-v1.4.0 功能描述） |
| `.opencode/project-mode.yaml` | 项目模式配置（depth/rigor） |

---

## Fish Trail Pack（话题治理）

| 文件 | 类型 | 说明 |
|------|------|------|
| `packs/fish-trail/pack-manifest.json` | config | pack v1.1.0，mcp_count=1 |
| `packs/fish-trail/AGENTS.md` | spec | Fish Trail 路由规则 |
| `packs/fish-trail/.opencode/skills/fish-trail/SKILL.md` | spec | fish-trail skill 完整指令 |
| `packs/fish-trail/.opencode/skills/fish-trail/mcp/context-state/server.py` | code | MCP server (1273行, 31 tools) |
| `packs/fish-trail/.opencode/skills/fish-trail/mcp/context-state/topic_registry_v2.py` | code | 4-state 话题注册表（核心） |
| `packs/fish-trail/.opencode/skills/fish-trail/mcp/context-state/memory_pressure_monitor.py` | code | 内存压力监控 + 分层保留引擎 |
| `packs/fish-trail/.opencode/skills/fish-trail/mcp/context-state/memory_context.py` | code | 分层上下文提供器 |
| `packs/fish-trail/.opencode/skills/fish-trail/mcp/context-state/feature_flags.py` | code | Feature flags（优先级链） |
| `packs/fish-trail/.opencode/skills/fish-trail/mcp/context-state/consolidation_gate.py` | code | Consolidation 质量门禁 |
| `packs/fish-trail/.opencode/skills/fish-trail/mcp/context-state/output_formatter.py` | code | 上下文输出格式化 |
| `packs/fish-trail/.opencode/skills/fish-trail/mcp/context-state/migration_v1_to_v2.py` | code | v1→v2 迁移 |
| `packs/fish-trail/.opencode/skills/fish-trail/mcp/context-state/topic_store.py` | code | 话题持久化 |
| `packs/fish-trail/.opencode/skills/fish-trail/mcp/context-state/topic_detector.py` | code | 话题检测 |
| `packs/fish-trail/.opencode/skills/fish-trail/mcp/context-state/contamination_scorer.py` | code | 污染评分 |
| `packs/fish-trail/.opencode/skills/fish-trail/mcp/context-state/context_builder.py` | code | 上下文构建 |
| `packs/fish-trail/.opencode/skills/fish-trail/mcp/context-state/session_store.py` | code | 会话存储 |
| `packs/fish-trail/.opencode/skills/fish-trail/mcp/context-state/TEST-GUIDE.md` | doc | 测试指南 |

---

## Companion Pack（Skill 管理）

| 文件 | 类型 | 说明 |
|------|------|------|
| `packs/petfish-companion-skill/pack-manifest.json` | config | pack v1.1.0，mcp_count=2，10 skills |
| `packs/petfish-companion-skill/AGENTS.md` | spec | Companion 路由规则 |
| `packs/petfish-companion-skill/.opencode/skills/petfish-companion/SKILL.md` | spec | companion skill 完整指令 |
| `packs/petfish-companion-skill/.opencode/skills/petfish-companion/scripts/catalog_query.py` | code | pack 目录查询 |
| `packs/petfish-companion-skill/.opencode/skills/petfish-companion/scripts/check_installed.py` | code | 已安装检查 |
| `packs/petfish-companion-skill/.opencode/skills/petfish-companion/scripts/detect_platform.py` | code | 平台检测 |

---

## Plugin 系统

| 文件 | 类型 | 说明 |
|------|------|------|
| `.opencode/plugin/topic-context-filter.ts` | code | 上下文过滤（292行，experimental.chat.messages.transform） |
| `.opencode/plugin/fish-trail-compaction.ts` | code | 压缩提示词替换（180行，experimental.session.compacting） |
| `.opencode/plugin/system-prompt-rules.ts` | code | 规则注入（181行，experimental.chat.system.transform） |
| `opencode.json` | config | 3 plugin + 3 MCP 注册 |

---

## MCP 服务（新增 v1.3.0）

| 文件 | 类型 | 说明 |
|------|------|------|
| `packs/petfish-companion-skill/.opencode/mcp/skill-registry/server.py` | code | skill-registry MCP（673行, 5 tools） |
| `packs/petfish-companion-skill/.opencode/mcp/usage-cost/server.py` | code | usage-cost MCP（761行, 6 tools） |

**skill-registry tools**: list_installed_packs, list_available_packs, search_skills, get_pack_info, get_profile_mapping

**usage-cost tools**: get_pricing, check_budget, list_models, record_usage, get_usage_summary, estimate_cost

---

## Benchmark 评估框架（新增 v1.4.0）

| 文件 | 类型 | 说明 |
|------|------|------|
| `benchmarks/README.md` | doc | 评估框架使用说明 |
| `benchmarks/datasets/gateway-topic-drift.jsonl` | data | 20 条话题检测用例 |
| `benchmarks/datasets/skill-sense.jsonl` | data | 20 条技能感知用例 |
| `benchmarks/datasets/failure-signal.jsonl` | data | 15 条故障信号用例 |
| `benchmarks/datasets/cost-routing.jsonl` | data | 20 条任务路由用例 |
| `benchmarks/scripts/run_eval.py` | code | 通用评估 harness（382行） |
| `benchmarks/scripts/modules/gateway_eval.py` | code | Gateway 评估模块（91行） |
| `benchmarks/scripts/modules/skill_sense_eval.py` | code | 技能感知评估模块（125行） |
| `benchmarks/scripts/modules/failure_signal_eval.py` | code | 故障信号评估模块（106行） |
| `benchmarks/scripts/modules/cost_routing_eval.py` | code | 成本路由评估模块（99行） |

---

## CI/CD Pipeline

| 文件 | 说明 |
|------|------|
| `.github/workflows/petfish-eval.yml` | Eval pipeline：fish-trail-tests + benchmark-eval + eval-report（3 jobs, ~30s） |
| `.github/workflows/website.yml` | 网站部署（push to master 触发） |

---

## 测试文件索引

### Fish Trail (Python / pytest)

| 文件 | 测试数 |
|------|--------|
| `packs/fish-trail/.opencode/skills/fish-trail/mcp/context-state/test_topic_registry_v2.py` | 38 |
| `packs/fish-trail/.opencode/skills/fish-trail/mcp/context-state/test_memory_pressure_monitor.py` | 35 |
| `packs/fish-trail/.opencode/skills/fish-trail/mcp/context-state/test_memory_context.py` | 26 |
| `packs/fish-trail/.opencode/skills/fish-trail/mcp/context-state/test_integration_v2.py` | 36 |
| `packs/fish-trail/.opencode/skills/fish-trail/mcp/context-state/test_performance_v2.py` | 20 |
| `packs/fish-trail/.opencode/skills/fish-trail/mcp/context-state/test_error_paths_v2.py` | 33 |
| `packs/fish-trail/.opencode/skills/fish-trail/mcp/context-state/test_feature_flags.py` | 45 |
| `packs/fish-trail/.opencode/skills/fish-trail/mcp/context-state/test_consolidation_gate.py` | 22 |
| `packs/fish-trail/.opencode/skills/fish-trail/mcp/context-state/test_output_formatter.py` | 32 |
| `packs/fish-trail/.opencode/skills/fish-trail/mcp/context-state/test_migration_v1_to_v2.py` | 24 |
| 其他 legacy tests | 29 |

### Plugin (TypeScript / tsx)

| 文件 | 测试数 |
|------|--------|
| `tests/plugin/topic-context-filter.test.ts` | 5（9 assertions） |

### Benchmark (Python)

| 文件 | 条目数 |
|------|--------|
| `benchmarks/datasets/gateway-topic-drift.jsonl` | 20 |
| `benchmarks/datasets/skill-sense.jsonl` | 20 |
| `benchmarks/datasets/failure-signal.jsonl` | 15 |
| `benchmarks/datasets/cost-routing.jsonl` | 20 |

---

## 安全与合规

| 文件 | 说明 |
|------|------|
| `.opencode/agents-rules/safety-guard.md` | 安全守卫规则（文件读取限制、危险命令、跨仓库保护） |
| `.opencode/agents-rules/anti-sycophancy.md` | 反迎合校准规则 |
| `.opencode/agents-rules/fish-trail.md` | 话题治理规则 |
| `.opencode/agents-rules/petfish-companion.md` | Companion 规则 |
| `.opencode/agents-rules/research.md` | 研究规则 |
| `.opencode/agents-rules/deploy-ops.md` | 部署运维规则 |
| `.opencode/agents-rules/course-skills.md` | 课程开发规则 |
| `.opencode/agents-rules/petfish-style.md` | 写作风格规则 |

---

## Skill 参考 (SKILL.md)

| 文件 | Pack |
|------|------|
| `packs/fish-trail/.opencode/skills/fish-trail/SKILL.md` | fish-trail |
| `packs/petfish-companion-skill/.opencode/skills/petfish-companion/SKILL.md` | companion |
| `packs/petfish-companion-skill/.opencode/skills/marketplace-connector/SKILL.md` | marketplace |
| `packs/petfish-companion-skill/.opencode/skills/skill-author/SKILL.md` | skill-author |
| `packs/petfish-companion-skill/.opencode/skills/skill-lint/SKILL.md` | skill-lint |
| `packs/petfish-companion-skill/.opencode/skills/repo-skill-miner/SKILL.md` | repo-miner |
| `packs/petfish-companion-skill/.opencode/skills/skill-security-auditor/SKILL.md` | security-auditor |
| `packs/petfish-companion-skill/.opencode/skills/quality-gate/SKILL.md` | quality-gate |
| `packs/petfish-companion-skill/.opencode/skills/skill-description-optimizer/SKILL.md` | desc-optimizer |
| `packs/petfish-companion-skill/.opencode/skills/skill-trigger-evaluator/SKILL.md` | trigger-eval |
| `packs/petfish-companion-skill/.opencode/skills/skill-usage-tracker/SKILL.md` | usage-tracker |

---

## 外部参考

| 资源 | URL |
|------|-----|
| GitHub Release (pre-release) | https://github.com/kylecui/petfish.ai/releases/tag/v1.1.0 |
| 开发分支 | feat/fish-trail-tiered-memory-v2 |
| 网站 | https://petfish.ai |
| CI Pipeline | .github/workflows/petfish-eval.yml |
| 安装指南 (预览版) | docs/agent-install-v1.1.0-preview.md |

---

## QA 文档

| 文件 | 说明 |
|------|------|
| `docs/qa/qa-test-plan.md` | 正式测试计划 |
| `docs/qa/reference-index.md` | 本文件 |
| `docs/qa/dev-spec-v1.2-v1.4.md` | 开发 Spec 副本 |

---

## 快速搜索

按模块搜索文件：
```bash
# Fish Trail
grep -r "topic_registry" packs/fish-trail/ --include="*.py" -l

# Plugin
ls .opencode/plugin/

# MCP
ls packs/petfish-companion-skill/mcp/*/

# Benchmark
ls benchmarks/datasets/ benchmarks/scripts/modules/

# Tests
find packs/fish-trail -name "test_*.py" | sort
```
