# PEtFiSh Next-Stage Adjusted Plan

> **Status**: Adjusted from `dev_reference/next-gen-design/petfish_next_stage_research_plan.md`
> **Date**: 2026-05-21
> **Based on**: Current state at fish-trail v1.1.0 pre-release

---

## 0. Current State Grounding

### What's Already Built (Not Re-Building)

| Capability | Status | Location |
|---|---|---|
| Companion Gateway (6-step) | ✅ v0.11.x | AGENTS.md |
| Topic Governance (fish-trail) | ✅ v1.1.0 pre-release | packs/core/fish-trail/ |
| Tiered Memory v2 (4-state lifecycle) | ✅ 340 tests passing | topic_registry_v2.py, memory_pressure_monitor.py, memory_context.py |
| Context-state MCP | ✅ 31 tools | packs/core/fish-trail/mcp/context-state/ |
| Plugin architecture (OpenCode) | ✅ 3 plugins exist | .opencode/plugin/ |
| system-prompt-rules plugin | ✅ Production | .opencode/plugin/system-prompt-rules.ts |
| fish-trail-compaction plugin | ✅ Production | .opencode/plugin/fish-trail-compaction.ts |
| topic-context-filter plugin | 🔶 In-progress (issue-135) | .opencode/plugin/topic-context-filter.ts |
| Quality gate pipeline | ✅ v0.3+ | skill-lint + skill-security-auditor + run_gate.py |
| Skill lifecycle (10 built-in skills) | ✅ | .opencode/skills/ |
| 12 skill packs | ✅ | packs/ |
| 8-platform support | ✅ | installers + platform registry |
| Release discipline | ✅ | AGENTS.md enforced |
| Model config cleanup | ✅ | Only deepseek/siliconflow loaded, ¥35/day budget |
| Token tracker | ✅ | ~/.config/opencode/token-tracker.json |

### What's NOT Built Yet (Genuine Gaps)

| Gap | Priority | Why |
|---|---|---|
| Per-request context filtering | HIGH | Issue-135; plugin exists but needs completion |
| Skill registry as MCP service | MEDIUM | catalog_query.py exists but not MCP-ified |
| Usage/cost MCP service | MEDIUM | Token tracker exists but no MCP interface |
| Cost guard plugin (loop detection, limits) | LOW | Budget is under control for now |
| Safety guard plugin (secret blocking) | LOW | Current AGENTS.md rules are sufficient |
| Quality hook plugin (auto-trigger gate) | LOW | Manual gate workflow works |
| Evaluation framework (benchmarks/) | MEDIUM | No structured eval datasets exist |
| Adapter decoupling (OMO → optional) | LOW | Current OMO integration is stable |
| Core Baseline profile (no-OMO) | LOW | Not yet tested standalone |
| Evidence reports (per-release) | MEDIUM | No eval data to report yet |

---

## 1. Strategic Direction (From Original Plan — Preserved)

The original plan's five transformations remain valid:

| From | To | Status |
|---|---|---|
| skills-first | runtime-first | ✅ Direction correct; already started via plugins |
| prompt discipline | plugin-enforced discipline | 🔶 In progress (3 plugins exist) |
| implicit context | MCP-backed state | ✅ Partially done (context-state MCP v2) |
| OMO-assisted development | OMO-decoupled evaluation | ⬜ Not started |
| feature-rich | evidence-backed | ⬜ Not started (needs eval framework) |

**One-line summary** (preserved from original):

> PEtFiSh下一步要证明的不是"我有很多skills"，而是"我能让AI Agent工作区更稳定、更少污染、更少失败、更低成本、更可审计"。

---

## 2. Adjusted Version Roadmap

### Original vs Adjusted

| Original | Adjusted | Reason |
|---|---|---|
| v0.12 Cost-Aware Gateway | **Deferred** → merge into issue-135 | Budget is stable; model routing policy is low-priority. Cost guard concepts fold into existing plugins. |
| v0.13 Plugin-Enforced Runtime | **PROMOTED → v1.2.0** (issue-135 + hardening) | 3 plugins already exist. Complete the context filter, then harden. |
| v0.14 MCP-backed State | **PARTIALLY DONE → v1.3.0** (skill-registry + usage-cost MCPs only) | context-state MCP v2 is complete. Only 2 MCPs remain. |
| v0.15 Evaluation & Proof | **v1.4.0** (unchanged priority) | Still essential for evidence-backed claims. |
| v0.16 Adapter Decoupling | **LONG-TERM → post-v1.4.0** | Not urgent. Current OMO integration is stable. |

### Adjusted Sequence

```
v1.1.0 (pre-release) → v1.2.0 → v1.3.0 → v1.4.0 → (future)
  fish-trail v2       plugin      MCP        eval
  tiered memory       hardening   state      proof
```

---

## 3. v1.2.0: Plugin Hardening (PROMOTED — Next Step)

### Why Promoted

- 3 plugin files exist; opencode.json plugin entries will be added during v1.2.0
- issue-135 (context filter) is the concrete, well-planned next step
- Plugin-enforced discipline is the highest-ROI investment right now
- Cost guard concepts (loop detection, model limits) can be folded in later

### Deliverables

| # | Item | File | Status |
|---|---|---|---|
| 1 | Complete topic-context-filter.ts | .opencode/plugin/topic-context-filter.ts | 🔶 Issue-135 in progress |
| 2 | Unit tests (6 test scenarios from plan) | tests/plugin/topic-context-filter.test.ts | 🔶 Test file exists |
| 3 | A/B measurement harness | evals/ (existing harness) | 🔶 Exists |
| 4 | Safety guard rules (as plugin) | .opencode/plugin/petfish-safety-guard.ts | ⬜ New |
| 5 | Plugin documentation | docs/plugins/ | ⬜ New |

### Success Criteria

1. Context filter achieves ≥30% token reduction for 3+ topic sessions
2. Zero regression for single-topic sessions
3. Safety guard blocks .env/secret reads (100% interception)
4. All plugins load without errors in opencode.json
5. Existing 340 tests still pass after plugin changes

### Files Touched

- `.opencode/plugin/topic-context-filter.ts` — complete implementation
- `.opencode/plugin/petfish-safety-guard.ts` — new
- `tests/plugin/topic-context-filter.test.ts` — expand
- `opencode.json` — plugin entries
- `docs/plugins/README.md` — new

---

## 4. v1.3.0: MCP State Services (SCOPED DOWN)

### Why Scoped Down

- context-state MCP v2 is already built (31 tools, 340 tests)
- Only 2 MCPs remain: skill-registry and usage-cost
- quality-gate MCP is optional — current CLI workflow works

### Deliverables

| # | Item | Location |
|---|---|---|
| 1 | skill-registry MCP server | packs/core/petfish-companion-skill/mcp/skill-registry/ |
| 2 | usage-cost MCP server | packs/core/petfish-companion-skill/mcp/usage-cost/ |
| 3 | Gateway integration (Gateway reads from MCP) | AGENTS.md update |
| 4 | MCP startup/config documentation | docs/mcp/ |

### Success Criteria

1. `skill-registry` MCP returns pack/profile mapping via MCP tools
2. `usage-cost` MCP outputs session/task cost from token-tracker data
3. Companion Gateway's Skill Sense step queries skill-registry MCP instead of inline catalog_query.py
4. No regression in Gateway response time (MCP calls must be <100ms)

### Files Touched

- `packs/core/petfish-companion-skill/mcp/skill-registry/server.py` — new
- `packs/core/petfish-companion-skill/mcp/usage-cost/server.py` — new
- `packs/core/petfish-companion-skill/pack-manifest.json` — update
- `AGENTS.md` — update Gateway to use MCP

---

## 5. v1.4.0: Evaluation & Evidence (UNCHANGED PRIORITY)

### Why Unchanged

- The original plan's eval framework is sound
- We need structured evidence before scaling further
- This is the gate to prove PEtFiSh "works"

### Deliverables (from original plan, adjusted)

| # | Item |
|---|---|
| 1 | `benchmarks/datasets/` — 7 eval datasets (gateway, skill-sense, failure-signal, anti-sycophancy, cost-routing, install-e2e, pack-touchpoint) |
| 2 | `benchmarks/scripts/` — run_*_eval.py for each dataset |
| 3 | `tests/e2e-install/` — automated install E2E tests |
| 4 | `.github/workflows/petfish-eval.yml` — CI eval pipeline |
| 5 | `reports/v1.4.0-evaluation.md` — first evidence report |

### Success Criteria (from original, preserved)

| Module | Metric | Target |
|---|---|---|
| Topic Check | precision / recall | >80% |
| Skill Sense | precision / recall | >85% / >80% |
| Failure Signal | recovery suggestion accuracy | >85% |
| Anti-Sycophancy | counterargument detection rate | >80% |
| Gateway | avg calls per turn | ≤1 |
| Install E2E | fresh install success | >95% |
| Pack Lifecycle | 9-touchpoint coverage | 100% |
| Quality Gate | false pass rate | <5% |

---

## 6. Architecture Adjustments

### What Stays from Original Plan

- **Policy Layer**: The `.opencode/petfish/policy/` directory concept is valid. But instead of building all 6 policies upfront, build them as needed:
  - `cost-policy.yaml` → deferred to when budget becomes a problem
  - `model-routing-policy.yaml` → deferred (current config is simple enough)
  - `gateway-policy.yaml` → implicit in AGENTS.md today; formalize in v1.3.0
  - `permission-policy.yaml` → folded into safety-guard plugin in v1.2.0
  - `rigor-policy.yaml` → implicit in project-mode.yaml today
- **Skill/Plugin/MCP/Policy boundary**: The original plan's 4-way responsibility split is correct and should be documented in `docs/architecture/`

### What Changes from Original Plan

- **No separate v0.12 Cost-Aware Gateway phase**: Cost concerns are folded into existing plugins. Model routing is stable enough for now.
- **No 6-phase sequential timeline**: Instead, v1.2.0-v1.4.0 are parallelizable where dependencies allow
- **Plugin system is OpenCode-specific**: The plan's TypeScript plugin assumption is correct — OpenCode's `experimental.chat.*.transform` hooks are the plugin API. Cross-platform plugins are not feasible short-term.
- **Evaluation comes AFTER MCP hardening, not before**: We can't measure Gateway effectiveness until Gateway reads from MCP state.

### Dependency Graph

```
v1.1.0 (done)
  └─→ v1.2.0 (plugin hardening)
       ├─→ issue-135 context filter (no deps)
       └─→ safety guard plugin (no deps)
            └─→ v1.3.0 (MCP state)
                 ├─→ skill-registry MCP (depends on catalog_query.py structure)
                 └─→ usage-cost MCP (depends on token-tracker.json format)
                      └─→ v1.4.0 (evaluation)
                           ├─→ benchmark datasets
                           ├─→ CI eval pipeline
                           └─→ evidence reports
```

---

## 7. Deferred / Removed Items

| Item | Original Plan | Disposition | Reason |
|---|---|---|---|
| petfish-gateway-plugin | v0.12 | **Deferred** | Gateway already runs as AGENTS.md instructions. Converting to plugin adds complexity without clear benefit. |
| petfish-cost-guard-plugin | v0.12 | **Deferred** | Budget is stable at ¥35/day. Loop detection is nice-to-have but not urgent. |
| petfish-quality-hook-plugin | v0.13 | **Deferred** | Manual gate workflow via `/petfish gate` works. Plugin enforcement can wait. |
| quality-gate MCP | v0.14 | **Deferred** | CLI-based gate (`run_gate.py`) is sufficient. |
| Adapter decoupling (v0.16) | v0.16 | **Long-term** | Current OMO integration is stable. Decoupling is a major architectural lift. |
| Cross-platform plugins | Implicit in v0.16 | **Not feasible** | OpenCode plugins are TypeScript hooks. Other platforms have different extension mechanisms. |

---

## 8. Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Context filter over-aggressively removes needed context | Medium | High | Conservative keyword matching; safety window; graceful degradation |
| MCP calls slow down Gateway response | Low | Medium | Cache MCP results; keep Gateway checks <100ms |
| Eval datasets don't match real usage | Medium | Medium | Seed from real session logs; iterate based on feedback |
| Budget spikes after adding MCP services | Low | Low | MCP services are local; no API calls; no cost |

---

## 9. Immediate Next Action

**Complete issue-135 (context filter plugin)** — this is the highest-priority, most concrete next step. All planning is done (`.sisyphus/plans/issue-135-phase3-context-filter.md`). Implementation can begin immediately.

---

## Appendix: Version Numbering Clarification

| What | Version | Meaning |
|---|---|---|
| PEtFiSh product version | v0.11.x | Overall project version (used in this plan's v1.2.0-v1.4.0 as NEXT milestones) |
| fish-trail pack version | v1.1.0 | Individual pack version (tiered memory v2) |
| petfish-companion pack version | v1.0.0 | Companion pack version |
| Other packs | v1.0.0 | Standardized at v1.0.0 |

The adjusted plan uses **PEtFiSh product version** for milestones (v1.2.0, v1.3.0, v1.4.0) to align with the original plan's intent while acknowledging the jump from v0.11.x.
