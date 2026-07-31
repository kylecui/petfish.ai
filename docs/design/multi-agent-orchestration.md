# PEtFiSh Multi-Agent Orchestration Design

> **Status**: DESIGN — for discussion and phased implementation
> **Date**: 2026-07-31
> **Depends on**: companion-gateway.ts (Phase 2), skill-index.json, OpenCode task system

---

## 1. Problem Statement

Current PEtFiSh routes skills via description matching — the model loads one skill at a time based on keyword triggers. This is single-agent, sequential, and lacks:

- **Parallel specialist execution** — can't run research + writing + review simultaneously
- **Coordinator pattern** — companion can't decompose a complex task and delegate pieces
- **Result aggregation** — no mechanism to merge outputs from multiple specialist skills
- **Context isolation** — delegated subtasks can't run in isolated context (pollution risk)

WorkBuddy (Tencent) and Cline already implement multi-agent orchestration. PEtFiSh's companion vision requires this capability.

## 2. Design Principles

1. **Build on OpenCode's task system** — don't reinvent; use `task()` for delegation
2. **Companion as coordinator** — companion-gateway.ts decides WHEN to decompose
3. **Skills as specialist contracts** — each skill declares its input/output contract
4. **Context firewall** — delegated tasks run with scoped context, not full session
5. **Progressive autonomy** — user can set autonomy level (suggest → delegate → auto)

## 3. Architecture

```
User Request
    │
    ▼
┌──────────────────────────────────┐
│ companion-gateway.ts             │
│  ├── Skill Sense (what skills?)  │
│  ├── Task Complexity Assessment  │
│  └── Orchestration Decision      │
│      ├── simple → route to skill │
│      └── complex → decompose     │
└──────────────────────────────────┘
    │ (complex path)
    ▼
┌──────────────────────────────────┐
│ Orchestrator (new plugin hook)   │
│  ├── Decompose into subtasks     │
│  ├── Assign skills to subtasks   │
│  ├── Launch parallel tasks       │
│  └── Aggregate results           │
└──────────────────────────────────┘
    │
    ├─→ task(skills=["research-source-discovery"], ...)
    ├─→ task(skills=["product-competitor-analysis"], ...)
    └─→ task(skills=["planning-stakeholder-analyst"], ...)
         │
         ▼ (results collected)
┌──────────────────────────────────┐
│ Synthesis Agent                  │
│  ├── Merge evidence from tasks   │
│  ├── Resolve conflicts           │
│  └── Produce unified output      │
└──────────────────────────────────┘
```

## 4. Skill Contract Extension

Each skill in `skill-index.json` gains optional orchestration metadata:

```json
{
  "name": "research-source-discovery",
  "description": "...",
  "orchestration": {
    "role": "specialist",
    "input_contract": ["research_brief", "scope"],
    "output_contract": ["source_index_jsonl", "source_count"],
    "can_coordinate": false,
    "parallel_safe": true
  }
}
```

Skills with `"can_coordinate": true` can decompose further.

## 5. Orchestration Patterns

### Pattern A: Pipeline (Sequential)
```
brief-framer → source-discovery → note-capture → evidence-ledger → synthesis → report
```
Already supported by research pack's default flow.

### Pattern B: Fan-out/Fan-in (Parallel)
```
           ┌→ product-competitor-analysis ─┐
brief ────→├→ planning-stakeholder-analyst ├→ synthesis → report
           └→ product-user-research ───────┘
```
New: companion launches 3 parallel tasks, waits for all, synthesizes.

### Pattern C: Reviewer Loop
```
draft → quality-reviewer → (if issues) → revise → quality-reviewer → (if pass) → deliver
```
Already partially supported by quality-gate pattern.

### Pattern D: Expert Panel (Council)
```
problem → ┌→ critic ──────────┐
          ├→ essence thinker ──┤
          ├→ opportunity scout ┤→ arbiter → conclusion
          ├→ outsider ─────────┤
          └→ executor ─────────┘
```
Already implemented by council-thinking skill.

## 6. Implementation Phases

### Phase A: Task Complexity Assessment (Low effort)
Add to companion-gateway.ts:
- Heuristic: if user message contains 3+ distinct task domains → "complex"
- If complex → inject "Consider decomposing into parallel subtasks" suggestion
- This is prompt-level guidance, not programmatic enforcement

### Phase B: Orchestrator Plugin (Medium effort)
New plugin `orchestrator.ts`:
- Hook: `experimental.chat.system.transform` (runs after companion-gateway)
- Reads skill-index.json orchestration metadata
- If companion-gateway flagged "complex" → inject decomposition plan
- Uses OpenCode `task()` API for actual delegation

### Phase C: Result Aggregation (Medium effort)
- Synthesis skill enhancement: accept multiple task results as input
- Conflict detection: if two tasks produce contradictory findings, flag for user
- Evidence merging: combine JSONL outputs from parallel tasks

### Phase D: Context Firewall (High effort)
- Scoped context packages for delegated tasks
- Each task gets only relevant topic context, not full session
- Uses fish-trail's context_build/export mechanism

### Phase E: Autonomy Levels (Low effort)
Add to project-mode.yaml:
```yaml
autonomy: suggest  # suggest | delegate | auto
```
- `suggest`: companion recommends decomposition, user approves
- `delegate`: companion decomposes and executes, user reviews
- `auto`: companion decomposes, executes, and delivers

## 7. What NOT to Build

- **Custom agent runtime** — use OpenCode's existing task system
- **Inter-agent messaging** — tasks communicate via file system (JSONL/Markdown)
- **Agent registry** — skill-index.json already serves this purpose
- **Complex scheduling** — parallel tasks via OpenCode's background task system

## 8. Success Metrics

- Complex tasks complete faster (parallel vs sequential)
- Context pollution reduced (scoped delegation)
- User can set autonomy level and trust the system
- Skills compose without manual orchestration

## 9. Risks

| Risk | Mitigation |
|---|---|
| Task overhead exceeds savings | Complexity threshold prevents trivial decomposition |
| Result conflicts confuse user | Synthesis skill explicitly flags contradictions |
| Context firewall too restrictive | Configurable scope per task type |
| Autonomy level too aggressive | Default to "suggest", require explicit upgrade |

## 10. Relationship to Current Work

This design builds on:
- **companion-gateway.ts** (Phase 2) — adds complexity assessment
- **skill-index.json** (Phase 2) — adds orchestration metadata
- **market.py CLI** (Phase 3) — skills with orchestration metadata are marketplace-ready
- **agentskills.io standard** (Phase 4) — orchestration fields are PEtFiSh extensions

No rewriting of existing work needed — purely additive.
