# Output Schema Constraint — Implementation Plan

## Problem Statement

GPT-series models (especially GPT5.4) append unsolicited suggestions like "如果你想，我还可以做以下3件事" when an active plan/todo exists. This derails plan execution and wastes user attention.

## Recommended Approach: Hybrid (Prompt Rule + Response Gate)

Two-phase implementation. Phase 1 is zero-code. Phase 2 only if Phase 1 proves insufficient.

---

## Phase 1: AGENTS.md Prompt Rule (Zero Code)

### What

Add an "Active-Plan Response Discipline" section to `AGENTS.md` that constrains output when todos are active.

### Activation Condition

ALL of these must be true:
1. ≥1 todo item is `in_progress` or `pending`
2. User's current message is NOT asking for options/suggestions
3. Task is NOT evaluative/exploratory in nature

### Deactivation Triggers (constraint lifts)

- All todos are `completed` or `cancelled`
- User explicitly asks "what else?", "还能做什么?", "options?"
- Agent is genuinely blocked and needs user decision
- Task is evaluative (review, critique, "what do you think?")

### Forbidden Output Patterns (when active)

- "I can also..." / "我还可以..."
- "如果你想，我还可以做以下N件事"
- Unsolicited option menus or numbered suggestion lists
- Speculative adjacent work not in the current plan
- "Would you also like me to..." / "要不要我顺便..."

### Allowed Output Patterns (when active)

- Task completion summary (what was done)
- Blocker description (what's preventing progress)
- Required next action FROM THE PLAN (not invented)
- One clarification question if blocked
- Status update on current todo item

### Placement

New section in `AGENTS.md` after "Todo创建纪律（强制）" section, titled:

```markdown
## Active-Plan Response Discipline（强制）
```

### Estimated Effort

~30 lines of markdown. No code changes. No plugin. No config.

---

## Phase 2: Response Gate Plugin (Only if Phase 1 Insufficient)

### What

A post-generation plugin (`output-focus-gate.ts`) that detects and strips forbidden patterns from agent responses before delivery.

### Architecture

- Hook: `response.post` (after generation, before delivery)
- Input: agent response text + current todo state
- Logic: regex/pattern match for forbidden patterns → strip or flag
- Output: cleaned response or warning annotation

### Detection Patterns

```typescript
const FORBIDDEN_PATTERNS = [
  /如果你想[，,]我还可以/,
  /I can also/i,
  /Would you also like/i,
  /要不要我顺便/,
  /此外[，,]我还能/,
  /^\d+\.\s+.*\n\d+\.\s+.*\n\d+\.\s+/m, // numbered suggestion lists (3+)
];
```

### Activation Check

```typescript
function isConstraintActive(todos: Todo[]): boolean {
  const hasActiveTodos = todos.some(t => t.status === 'in_progress' || t.status === 'pending');
  return hasActiveTodos;
}
```

### Behavior on Match

- Strip the offending paragraph/section
- Append a single-line note: `[focus-gate: removed unsolicited suggestions — active plan exists]`
- Log for observability

### Files to Create/Modify

- CREATE: `.opencode/plugins/output-focus-gate.ts`
- MODIFY: `opencode.json` — register plugin

### Estimated Effort

~80 lines TypeScript. Requires understanding plugin hook API.

---

## Test Scenarios

| # | Scenario | Expected |
|---|----------|----------|
| 1 | Agent completes a todo, GPT appends "我还可以做3件事" | Gate strips suggestion, keeps completion summary |
| 2 | Agent is blocked, needs user decision | Blocker description passes through (exception) |
| 3 | All todos complete, agent offers next steps | Allowed (constraint inactive) |
| 4 | User asks "what else can you do?" | Allowed (explicit request) |
| 5 | No todos exist, agent offers suggestions | Allowed (constraint inactive) |
| 6 | Agent reports clean completion, no extras | Passes through unchanged |

---

## Risk Assessment

| Risk | Mitigation |
|------|-----------|
| Phase 1 ignored by weaker models | Phase 2 as hard gate |
| False positive strips legitimate content | Conservative regex; only strip clear patterns |
| Constraint too strict, agent can't communicate blockers | Explicit exception for blockers and clarification |
| Plugin API doesn't support post-response hook | Check opencode plugin docs before Phase 2 |

---

## Success Criteria

- Zero unsolicited suggestion menus when todos are active
- Agent still communicates blockers and completion normally
- No regression in plan execution throughput
