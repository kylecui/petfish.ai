# PEtFiSh Multi-Agent Orchestration Design (v2)

> **Status**: DESIGN (revised) — addresses Momus REJECT + Council-Thinking review
> **Date**: 2026-07-31 (v2 revision)
> **Depends on**: companion-gateway.ts (v3.0.0), skill-index.json (v3.0.0)
> **Predecessor**: v1 design was REJECTed by Momus (missing QA, ambiguous paths, unverified hook)

---

## 0. Revision Summary

This v2 design incorporates:
- **Momus fixes**: QA scenario per phase, exact file paths, hook proof
- **Council-Thinking fixes**: spike-first validation, decoupled contracts, skill-dispatch signal (not domain count), companion-aware positioning, token cost guardrails

### Momus Blocking Issues Resolution

| # | Momus Issue | Resolution |
|---|---|---|
| 1 | Phases A-E lack QA scenarios | Every phase now has a `QA` section with tool, steps, and pass criteria |
| 2 | `companion-gateway.ts` path ambiguous | All file changes specify exact path: `.opencode/plugin/companion-gateway.ts` (primary), synced to `lib/plugin/` and `packs/core/petfish-companion-skill/.opencode/plugin/` |
| 3 | `experimental.chat.system.transform` hook unverified | **Already in use**: `.opencode/plugin/companion-gateway.ts:196` and `:279`. Verified by `scripts/verify_companion_gateway.py` (14/14 checks pass). Momus review searched wrong path. |

---

## 1. Problem Statement (Repositioned)

PEtFiSh's companion already provides skill routing, context governance (fish-trail), and programmatic gateway enforcement. What it lacks is **companion-aware parallel delegation** — the ability to fan out independent specialist investigations concurrently while maintaining the companion's anti-sycophancy, failure-signal, and contamination-boundary disciplines across delegated tasks.

This is NOT "building a generic multi-agent framework." It is extending the companion's existing discipline to cover delegated subtasks. The differentiation from Cursor/Cline/WorkBuddy is: **a multi-agent system where each delegated task inherits the companion's guardrails** (retry-before-workaround, web-grounding, anti-sycophancy, topic contamination awareness).

### What Already Exists (Correctly Categorized)

| Capability | Implementation | Type |
|---|---|---|
| Pipeline orchestration (A→B→C→D) | Research pack routing rules in AGENTS.md | **Prompt-level skill chaining** (not programmatic) |
| Reviewer loop (draft→review→fix) | quality-gate `run_gate.py` | **Programmatic within single skill** (not cross-task) |
| Expert panel (5 advisors) | council-thinking skill | **Prompt-level role simulation** (not parallel execution) |
| Context isolation | fish-trail topic scoping + context packages | **Programmatic** (already production) |
| Skill dispatch | companion-gateway.ts Skill Sense | **Programmatic** (keyword matching, v3.0.0) |

**Only Pattern B (true parallel fan-out/fan-in) is genuinely new.** Everything else exists at some level. This design focuses exclusively on adding parallel dispatch while extending the companion's discipline to cover it.

---

## 2. Design Principles

1. **Spike before build** — validate `task()` parallel capability before any infrastructure
2. **Contracts first, orchestration second** — skill I/O contracts are independently valuable
3. **Companion-aware, not generic** — every delegated task inherits gateway guardrails
4. **Token-cost conscious** — decomposition is opt-in, not default; budget guardrails required
5. **File-based result passing** — tasks communicate via JSONL/Markdown artifacts, not in-memory

---

## 3. File Paths (Exact)

All changes reference exact paths. The primary plugin source is:

```
.opencode/plugin/companion-gateway.ts        ← PRIMARY (modify here)
lib/plugin/companion-gateway.ts              ← SYNC COPY
packs/core/petfish-companion-skill/.opencode/plugin/companion-gateway.ts  ← PACK SOURCE
```

Sync rule: modify primary → copy to sync copies → commit all three. This matches the existing pattern used for `topic-context-filter.ts` and `system-prompt-context-inject.ts`.

Other files:
- `scripts/generate_skill_index.py` — skill index generator
- `.opencode/skill-index.json` — generated index (do not edit manually)
- `.opencode/project-mode.yaml` — mode config (create if not exists, per AGENTS.md spec)

---

## 4. Hook Verification

`experimental.chat.system.transform` and `tool.execute.after` are **already in production use** in companion-gateway.ts:

```typescript
// .opencode/plugin/companion-gateway.ts:196
"experimental.chat.system.transform": async (_input, output) => { ... }

// .opencode/plugin/companion-gateway.ts:279
"tool.execute.after": async (_input, output) => { ... }
```

Verified by:
```bash
$ uv run scripts/verify_companion_gateway.py
  [PASS] Hook present: experimental.chat.system.transform
  [PASS] Hook present: tool.execute.after
  ✓ All structural checks passed!
```

No new hooks are required for Phases 1-2. Phase 3 (if spike passes) uses the existing `experimental.chat.system.transform` hook — no new hook type needed.

---

## 5. Implementation Phases

### Phase 0: task() Capability Spike (BLOCKING)

**Goal**: Validate that OpenCode's `task()` API supports concurrent background execution with result collection. This is the load-bearing assumption for all downstream phases.

**Method**: Manually invoke 3 parallel background tasks with pilot skills, measure:
- (a) Do tasks actually run concurrently? (check timestamps in task output)
- (b) How do results come back? (via `background_output`? file system?)
- (c) What's the token cost delta vs sequential execution?

**Steps**:
1. Launch 3 tasks in parallel:
   ```typescript
   task(subagent_type="explore", prompt="Find auth patterns", run_in_background=true, load_skills=[])
   task(subagent_type="explore", prompt="Find database patterns", run_in_background=true, load_skills=[])
   task(subagent_type="explore", prompt="Find frontend patterns", run_in_background=true, load_skills=[])
   ```
2. Wait for all 3 completions
3. Collect results via `background_output`
4. Record: wall-clock time, token usage, result quality

**QA Scenario**:
- **Tool**: Manual execution + `usage-cost_get_usage_summary` for token measurement
- **Steps**: Launch 3 parallel tasks → wait for completion → collect results → measure tokens → compare with sequential baseline (3 tasks one at a time)
- **Expected**: Tasks run concurrently (overlapping timestamps), results are collectible, token cost is ≤3× sequential (not 6×+)
- **Pass criteria**: If task() does NOT support parallel execution OR results are not collectible → **STOP. Phases 2-5 are cancelled. Ship only Phase 1 (contracts).**
- **Fail criteria**: N/A — this is a validation spike, not a code change. The outcome determines the path.

---

### Phase 1: Skill I/O Contracts (INDEPENDENT — ship regardless of spike)

**Goal**: Add `input_contract` and `output_contract` metadata to skill-index.json. This is independently valuable: enables composition discovery, marketplace differentiation, and future orchestration — without requiring any orchestration infrastructure.

**Files**:
- `scripts/generate_skill_index.py` — add contract parsing from SKILL.md frontmatter
- `.opencode/skill-index.json` — regenerated with new fields

**Changes**:
1. In `generate_skill_index.py`, parse optional `orchestration` block from SKILL.md frontmatter:
   ```yaml
   orchestration:
     role: specialist        # specialist | coordinator
     input_contract: [research_brief, scope]
     output_contract: [source_index_jsonl, source_count]
     parallel_safe: true
   ```
2. Add 3 pilot skills with contracts:
   - `research-source-discovery`: input=[brief, scope], output=[sources.jsonl], parallel_safe=true
   - `product-competitor-analysis`: input=[domain, competitors], output=[matrix.md], parallel_safe=true
   - `planning-stakeholder-analyst`: input=[project_brief], output=[stakeholder_map.md], parallel_safe=true
3. Regenerate index

**QA Scenario**:
- **Tool**: `uv run scripts/generate_skill_index.py`
- **Steps**: Run generator → read `.opencode/skill-index.json` → find pilot skills → verify `orchestration` field exists with correct subfields
- **Expected**: 3 pilot skills have `orchestration.input_contract`, `orchestration.output_contract`, `orchestration.parallel_safe` fields
- **Pass criteria**: JSON is valid, all 3 pilots have non-empty contract arrays, `parallel_safe: true`

---

### Phase 2: Skill-Dispatch Complexity Signal (only if spike passes)

**Goal**: Replace the naive "3+ domains" heuristic with a skill-dispatch-signal-based complexity detector. When Skill Sense matches 2+ non-overlapping `parallel_safe` specialists, inject an optional decomposition hint.

**Files**:
- `.opencode/plugin/companion-gateway.ts` (primary) → sync to `lib/plugin/` + `packs/core/.../plugin/`

**Changes**:
1. In `runSkillSense()` function (currently at ~line 230), after matching domains, also check `skill-index.json` for `orchestration.parallel_safe: true` skills in matched domains
2. If 2+ non-overlapping parallel-safe specialists matched, add to injection:
   ```
   **Orchestration Hint**: 2 parallel-safe specialists matched (research-source-discovery, product-competitor-analysis). The model MAY delegate via task() if parallel execution is judged valuable. Token cost: ~2× single-agent.
   ```
3. This is a **hint, not enforcement** — the model decides whether to delegate

**QA Scenario**:
- **Tool**: `uv run scripts/simulate_gateway.py` (extend with contract-aware test case)
- **Steps**: Add test case: user message matches 2 parallel-safe skills → run simulation → verify "Orchestration Hint" appears in output with both skill names and token cost warning
- **Expected**: Output contains "Orchestration Hint" with 2 skill names and "Token cost: ~2×"
- **Pass criteria**: Hint appears only when 2+ parallel_safe skills match; does NOT appear for single-domain queries

---

### Phase 3: Parallel Dispatch Primitive (only if spike passes)

**Goal**: Implement the fan-out/fan-in pattern as a single primitive, not a framework. The model explicitly invokes parallel dispatch when it judges it valuable.

**Files**:
- `.opencode/plugin/companion-gateway.ts` — add `parallel_dispatch` tracking state
- No new plugin — reuse existing `experimental.chat.system.transform` hook

**Changes**:
1. When the model invokes `task()` with `run_in_background=true` for 2+ skills simultaneously, companion-gateway's `tool.execute.after` hook tracks the dispatch
2. State file: `.petfish/gateway/active-dispatch.json` — tracks which tasks are in flight
3. When all dispatched tasks complete, inject: "All N parallel tasks completed. Results available via background_output. Consider synthesis."
4. Token budget guardrail: if `usage-cost_check_budget` shows >80% daily budget consumed, inject "Token budget low — avoid further parallel dispatch."

**QA Scenario**:
- **Tool**: Manual execution — launch 2 parallel tasks → wait for completion → check `.petfish/gateway/active-dispatch.json`
- **Steps**: Launch 2 tasks → verify dispatch state file created with task IDs → wait for completion → verify file updated to "completed" → verify injection message appears
- **Expected**: State file tracks task lifecycle; completion injection fires
- **Pass criteria**: State file exists, tracks 2 tasks, transitions to completed

---

### Phase 4: Result Aggregation + Conflict Detection (only if Phase 3 ships)

**Goal**: Provide a synthesis mechanism for parallel task results.

**Files**:
- `.opencode/skills/research-synthesis/SKILL.md` — enhance to accept multiple result sources
- No new files — reuse existing synthesis skill

**Changes**:
1. Add section to research-synthesis SKILL.md: "When invoked after parallel dispatch, accept multiple JSONL result files as input"
2. Conflict detection rule: if two tasks produce contradictory findings (detected by comparing key claims), flag as "⚠ Conflict detected" in synthesis output
3. Conflict resolution: present both findings with evidence, let user decide (do NOT auto-resolve)

**QA Scenario**:
- **Tool**: Manual — run synthesis on 2 conflicting result files → verify conflict flag
- **Steps**: Create 2 mock JSONL files with contradictory claims → invoke synthesis → check output for conflict flag
- **Expected**: Output contains "⚠ Conflict detected" section with both claims
- **Pass criteria**: Conflict flag appears when claims contradict; does not appear when claims agree

---

### Phase 5: Autonomy Levels (independent of Phases 2-4)

**Goal**: Let users control how aggressive the companion is with decomposition.

**Files**:
- `.opencode/project-mode.yaml` — add `autonomy` field (create file if not exists, per AGENTS.md spec)
- `.opencode/plugin/companion-gateway.ts` — read autonomy level in `readProjectMode()`

**Changes**:
1. Add to `.opencode/project-mode.yaml`:
   ```yaml
   autonomy: suggest  # suggest | delegate | auto
   ```
2. In `readProjectMode()`, parse `autonomy` field (default: `suggest`)
3. Injection behavior:
   - `suggest`: inject hint only ("2 specialists matched, consider delegating")
   - `delegate`: inject hint + auto-launch tasks if user confirms
   - `auto`: auto-launch tasks without confirmation (requires explicit user opt-in)

**QA Scenario**:
- **Tool**: `uv run scripts/simulate_gateway.py` (extend with autonomy test cases)
- **Steps**: Set `autonomy: auto` in project-mode.yaml → run simulation → verify "auto-launch" message appears; Set `autonomy: suggest` → verify only hint appears
- **Expected**: Different injection text based on autonomy level
- **Pass criteria**: `suggest` → hint only; `auto` → action message; default (no file) → suggest

---

## 6. Token Cost Guardrails

| Scenario | Token Multiplier | Guardrail |
|---|---|---|
| Single agent (current) | 1× | Baseline |
| 2 parallel tasks + synthesis | ~3× | Only when model explicitly delegates |
| 3 parallel tasks + synthesis | ~4× | Requires `autonomy: delegate` or higher |
| 4+ parallel tasks | ~5-6× | Blocked if daily budget >80% consumed |

Implementation: `companion-gateway.ts` checks `usage-cost_check_budget` before injecting orchestration hints. If budget is low, suppress hints.

---

## 7. What NOT to Build

- **Custom agent runtime** — use OpenCode's `task()` API
- **Orchestrator plugin** — no new plugin; reuse companion-gateway.ts hooks
- **Inter-agent messaging** — tasks communicate via file system (JSONL/Markdown)
- **Agent registry** — skill-index.json with contracts serves this purpose
- **Complex scheduling** — model decides when to delegate; companion provides hints only
- **Auto-conflict resolution** — always surface conflicts to user, never auto-resolve

---

## 8. Success Metrics

| Metric | Measurement | Target |
|---|---|---|
| Parallel task completion | Wall-clock time vs sequential baseline | ≤60% of sequential time |
| Token cost | `usage-cost_get_usage_summary` | ≤4× single-agent for 3-task dispatch |
| User trust | User does not disable autonomy after enabling | >80% retention |
| Skill composition discovery | Skills with contracts used in chains | ≥3 pilot skills |

---

## 9. Risks (Revised with Council Input)

| Risk | L | I | Mitigation |
|---|---|---|---|
| task() doesn't support parallel execution | High | Critical | Phase 0 spike validates before any build |
| Token cost explosion (3-6×) | High | High | Budget guardrail in companion-gateway; opt-in decomposition |
| Over-decomposition noise | Med | High | Skill-dispatch signal (not domain count); only parallel_safe skills trigger |
| Result conflicts confuse user | Med | Med | Explicit conflict flag; never auto-resolve |
| Autonomy too aggressive | Low | High | Default `suggest`; explicit opt-in for `auto` |

---

## 10. Relationship to Current Work

| Component | v3.0.0 Status | This Design |
|---|---|---|
| companion-gateway.ts | ✅ Production (6-step programmatic) | Phase 2-3: add complexity signal + dispatch tracking |
| skill-index.json | ✅ 100 skills indexed | Phase 1: add contract metadata |
| fish-trail context packages | ✅ Production | Phase 4: leverage for result artifacts |
| market.py CLI | ✅ Production | Future: skills with contracts are marketplace-ready |
| agentskills.io standard | ✅ 102/102 compliant | Contract fields are PEtFiSh extension to standard |

**All changes are additive.** No existing functionality is modified or removed.
