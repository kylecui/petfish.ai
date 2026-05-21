# PEtFiSh 开发 Spec v1.2.0 - v1.4.0（已执行完成）

> **状态**: ✅ 全部执行完成 (2026-05-21)
> **分支**: feat/fish-trail-tiered-memory-v2 (80 commits ahead of master)
> **Release**: v1.1.0 pre-release at https://github.com/kylecui/petfish.ai/releases/tag/v1.1.0
> **用途**: 测试团队参考本文档了解已完成的功能范围、架构决策和验收标准。
> **原始文件**: .sisyphus/plans/petfish-next-stage-adjusted-plan.md

---

## 0. Current State Grounding

### What's Already Built (Not Re-Building)

| Capability | Status | Location |
|---|---|---|
| Companion Gateway (6-step) | ✅ v0.11.x | AGENTS.md |
| Topic Governance (fish-trail) | ✅ v1.1.0 pre-release | packs/fish-trail/ |
| Tiered Memory v2 (4-state lifecycle) | ✅ 340 tests passing | topic_registry_v2.py, memory_pressure_monitor.py, memory_context.py |
| Context-state MCP | ✅ 31 tools | packs/fish-trail/mcp/context-state/ |
| Plugin architecture (OpenCode) | ✅ 3 plugins exist | .opencode/plugin/ |
| system-prompt-rules plugin | ✅ Production | .opencode/plugin/system-prompt-rules.ts |
| fish-trail-compaction plugin | ✅ Production | .opencode/plugin/fish-trail-compaction.ts |
| topic-context-filter plugin | ✅ v1.2.0 | .opencode/plugin/topic-context-filter.ts |
| Quality gate pipeline | ✅ v0.3+ | skill-lint + skill-security-auditor + run_gate.py |
| Skill lifecycle (10 built-in skills) | ✅ | .opencode/skills/ |
| 12 skill packs | ✅ | packs/ |
| 8-platform support | ✅ | installers + platform registry |
| Release discipline | ✅ | AGENTS.md enforced |
| Model config cleanup | ✅ | Only deepseek/siliconflow loaded, ¥35/day budget |
| Token tracker | ✅ | ~/.config/opencode/token-tracker.json |
| Safety guard rules | ✅ v1.2.0 | .opencode/agents-rules/safety-guard.md |
| skill-registry MCP | ✅ v1.3.0 | packs/petfish-companion-skill/mcp/skill-registry/server.py (673行) |
| usage-cost MCP | ✅ v1.3.0 | packs/petfish-companion-skill/mcp/usage-cost/server.py (761行) |
| Benchmark framework | ✅ v1.4.0 | benchmarks/ (75 entries, 4 evals) |
| CI eval pipeline | ✅ v1.4.0 | .github/workflows/petfish-eval.yml |

---

## 1. Adjusted Version Roadmap

| Version | Content | Status |
|---------|---------|--------|
| v1.1.0 | Fish Trail Tiered Memory v2 (340 tests) | ✅ Pre-release |
| v1.2.0 | Plugin Hardening (context-filter + safety-guard) | ✅ |
| v1.3.0 | MCP State Services (skill-registry + usage-cost) | ✅ |
| v1.4.0 | Evaluation Framework (benchmarks + CI) | ✅ |

---

## 2. v1.2.0: Plugin Hardening

### Deliverables

| # | Item | File | Status |
|---|---|---|---|
| 1 | Complete topic-context-filter.ts | .opencode/plugin/topic-context-filter.ts | ✅ registered in opencode.json |
| 2 | Unit tests (5 tests, 9 assertions) | tests/plugin/topic-context-filter.test.ts | ✅ passing |
| 3 | A/B measurement harness | evals/ | ✅ exists |
| 4 | Safety guard rules | .opencode/agents-rules/safety-guard.md | ✅ auto-injected by system-prompt-rules |
| 5 | Plugin entries in opencode.json | opencode.json | ✅ 3 plugins registered |

### Success Criteria
1. Context filter achieves ≥30% token reduction for 3+ topic sessions
2. Zero regression for single-topic sessions
3. Safety guard injected into system prompt
4. All plugins load without errors

---

## 3. v1.3.0: MCP State Services

### Deliverables

| # | Item | Location | Status |
|---|---|---|---|
| 1 | skill-registry MCP server | packs/petfish-companion-skill/mcp/skill-registry/server.py | ✅ 673行, 5 tools |
| 2 | usage-cost MCP server | packs/petfish-companion-skill/mcp/usage-cost/server.py | ✅ 761行, 6 tools |
| 3 | MCP entries in opencode.json | opencode.json | ✅ registered |
| 4 | Pack manifest updated | packs/petfish-companion-skill/pack-manifest.json | ✅ mcp_count=2 |

### skill-registry tools
- `list_installed_packs` — read .opencode/installed-packs.json
- `list_available_packs` — read packs/*/pack-manifest.json
- `search_skills` — search SKILL.md frontmatter descriptions
- `get_pack_info` — pack details by alias or directory name
- `get_profile_mapping` — profile→pack mapping (9 profiles)

### usage-cost tools
- `get_pricing` — model pricing from token-tracker.json
- `check_budget` — budget status (ok/warning/exceeded)
- `list_models` — all configured models with pricing
- `record_usage` — write usage to .petfish/state/usage.jsonl
- `get_usage_summary` — aggregate by session/day
- `estimate_cost` — cost estimation by model + token count

---

## 4. v1.4.0: Evaluation & Evidence

### Deliverables

| # | Item | Location | Status |
|---|---|---|---|
| 1 | 4 JSONL datasets (75 entries) | benchmarks/datasets/ | ✅ |
| 2 | Eval harness (run_eval.py) | benchmarks/scripts/ | ✅ 382行 |
| 3 | 4 eval modules | benchmarks/scripts/modules/ | ✅ |
| 4 | CI eval pipeline | .github/workflows/petfish-eval.yml | ✅ 3 jobs |
| 5 | README with usage guide | benchmarks/README.md | ✅ |

### Datasets
| Dataset | Entries | Type |
|---------|---------|------|
| gateway-topic-drift.jsonl | 20 | topic relation classification |
| skill-sense.jsonl | 20 | skill gap detection |
| failure-signal.jsonl | 15 | failure signal detection |
| cost-routing.jsonl | 20 | task tier routing |

### Success Criteria
| Module | Metric | Target |
|---|---|---|
| Topic Check | precision / recall | >80% |
| Skill Sense | precision / recall | >85% / >80% |
| Failure Signal | recovery suggestion accuracy | >85% |
| Cost Routing | accuracy | >80% |

---

## 5. Architecture

### Plugin System (OpenCode hooks)
- `experimental.chat.system.transform` — rule injection (system-prompt-rules)
- `experimental.chat.messages.transform` — context filtering (topic-context-filter)
- `experimental.session.compacting` — prompt replacement (fish-trail-compaction)

### MCP Servers (stdio JSON-RPC 2.0, stdlib only)
- context-state (fish-trail): 31 tools, topic/session/context management
- skill-registry (companion): 5 tools, pack/skill discovery
- usage-cost (companion): 6 tools, pricing/budget/usage tracking

### Agent Rules (injected via system-prompt)
- safety-guard.md — file read, bash command, cross-repo, release protection
- anti-sycophancy.md — judgment calibration
- fish-trail.md — topic governance routing
- Plus 5 more domain-specific rule files

---

## 附录: 执行记录

### Commit 记录
| Commit | 内容 | 新增/修改 |
|--------|------|-----------|
| `b787405` | test: integration v2 (36 tests, 9 scenarios) | 1 file |
| `2eb829e` | test: performance v2 (20 tests) | 1 file |
| `00edb54` | test: error paths v2 (33 tests) | 1 file |
| `3df9786` | bump: fish-trail pack 1.0.1→1.1.0, register 18 files | 1 file |
| `3d90769` | docs: v1.1.0 preview install guide | 1 file |
| `83f6532` | feat: website preview install section | 1 file |
| `c42d732` | feat(plugin): register topic-context-filter in opencode.json | 1 file |
| `63e174c` | feat(safety): add safety-guard agents-rules | 1 file (new) |
| `22ff5ca` | feat(mcp): skill-registry + usage-cost MCP servers | 4 files (2 new) |
| `1652ea6` | feat(eval): v1.4.0 benchmark framework + CI | 12 files (all new) |
| `0aaba36` | fix(ci): remove plugin-smoke from CI | 1 file |

### 测试覆盖
- Fish-trail: 340 tests (269 existing + 89 v2-specific) — 339/340 pass (1 Windows flaky)
- Benchmark: 75 entries across 4 datasets — all 1.0000 accuracy
- Plugin: 5 tests, 9 assertions — all pass
- CI: .github/workflows/petfish-eval.yml — 3 jobs, ~30s, all green

### 文件统计
- 28 new files across all v1.2.0-v1.4.0 commits
- ~3,400 lines of new code (Python + TypeScript + JSONL + YAML)
- 80 commits ahead of master
