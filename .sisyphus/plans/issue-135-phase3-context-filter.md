# Issue #135 Phase 3: Per-Request Context Filtering Plugin

## Objective

Implement a `messages.transform` plugin that filters non-active-topic messages from the LLM context window before every request, targeting ≥30% input token reduction for multi-topic sessions.

## Why

Phase 2 (compaction hook) only modifies summary prompts — it cannot reduce per-request tokens. Phase 3 intercepts the actual message array via `experimental.chat.messages.transform` and removes/summarizes off-topic messages before the LLM sees them.

## Architecture

### Plugin Location

`.opencode/plugin/topic-context-filter.ts` — new file, same directory as the runtime-loaded `system-prompt-rules.ts`. This is the directory referenced by `opencode.json` plugin entries. The `lib/plugin/` directory is the installer source; our plugin lives at the runtime path directly since this repo IS the source.

### Hook

```typescript
"experimental.chat.messages.transform": async (_input, output) => {
  // output.messages is the mutable array
  // MUST use splice() — assignment is a no-op (confirmed: issue #25754)
}
```

### Data Flow

```
messages.transform fires
  → Read .petfish/fish-trail/topic-registry.json (active_topic)
  → Read .petfish/fish-trail/topics/{active_topic}.json (title, tags, scope)
  → Classify each message by topic relevance (keyword match)
  → Build filtered array:
      - KEEP: last N messages (safety window)
      - KEEP: messages matching active topic
      - KEEP: tool_use/tool_result pairs (never split)
      - REPLACE: off-topic message clusters → 1-line summary placeholder
  → Splice filtered array into output.messages
```

## Implementation Phases

### Phase 3a: Minimum Viable (this PR)

**Scope**: Keyword-based classification, fixed safety window, graceful degradation.

**Files changed**:
1. `.opencode/plugin/topic-context-filter.ts` — new plugin (~150-200 lines)
2. `opencode.json` — add plugin entry: `[".opencode/plugin/topic-context-filter.ts", { "enabled": true }]`

**Algorithm**:

1. **Init** (plugin load time):
   - Read `TOPIC_TO_RULES` keyword map (reuse from system-prompt-rules.ts or define similar)
   - Set `SAFETY_WINDOW = 3` (always keep last 3 messages)
   - Set `MIN_MESSAGES_TO_FILTER = 10` (don't bother filtering short conversations)

2. **Per-request** (hook fires):
   - If `output.messages.length < MIN_MESSAGES_TO_FILTER` → return (no-op)
   - Read `topic-registry.json` → get `active_topic` ID
   - If no active topic → return (no-op, graceful degrade)
   - Read topic JSON → extract title, scope, tags → build keyword set
   - For each message (except last SAFETY_WINDOW):
     - Extract text from `msg.parts` (join all `type: "text"` parts)
     - Score relevance: count keyword hits in text
     - Mark as `keep` (score > 0) or `remove` (score = 0)
    - **Single-topic guard**: Count distinct topic clusters among scored messages. If only ONE topic cluster is detected (i.e., all keyword-hitting messages share the same topic domain), return early — no splice needed. Detection: build a set of matched topic domains from TOPIC_TO_RULES; if set size ≤ 1, this is a single-topic session. Messages with score=0 (generic replies like "OK", "done") are ignored in this check — they don't indicate a different topic, just topic-neutral content.
    - **Fallback for generic messages in single-topic sessions**: When single-topic guard fires, ALL messages are kept unchanged (including score=0 generic ones), guaranteeing zero modification.
   - **Low-yield guard**: If fewer than 20% of messages would be removed, return early — not worth the placeholder noise for marginal savings.
   - Post-process: ensure tool_use/tool_result pairs stay together
     - If a tool_use is kept, its next tool_result must also be kept (and vice versa)
   - Build filtered array:
     - Kept messages: pass through unchanged
     - Removed messages: collapse consecutive removed messages into a single placeholder message:
       ```
       { info: { role: "assistant" }, parts: [{ type: "text", text: "[N messages from other topics omitted]" }] }
       ```
   - `output.messages.splice(0, output.messages.length, ...filtered)`

3. **Graceful degradation**:
   - topic-registry.json missing/unreadable → return unmodified
   - topic JSON missing → return unmodified
   - Any exception → catch, log warning, return unmodified
   - Never throw — plugin failures must not break the session

**Safety invariants**:
- Last 3 messages ALWAYS kept (regardless of topic)
- tool_use/tool_result pairs NEVER split
- Single-topic sessions: no messages removed (only 1 topic domain detected → guard fires, score=0 generics preserved)
- If ≤10 messages total: skip filtering entirely

**Configuration** (plugin options):
```json
{
  "safetyWindow": 3,
  "minMessages": 10,
  "enabled": true
}
```

### Phase 3b: Robust (future)

- Per-topic summaries from MCP `context_build` instead of generic placeholder
- Message-topic index cache (avoid re-classifying old messages)
- Richer keyword extraction from topic scope/summary fields
- Configurable aggressiveness levels

### Phase 3c: Optimized (future)

- Token counting (tiktoken or char estimate) to target specific budget
- Adaptive safety window (expand when topic is ambiguous)
- Coordinate with Phase 2 compaction (filter before compaction triggers)
- Metrics/telemetry for actual savings

## Key Constraints

1. **splice not assignment** — `output.messages = x` is a silent no-op. Must use `output.messages.splice(0, output.messages.length, ...filtered)`.
2. **input is `{}`** — no session ID, model, or metadata available in the hook input.
3. **Message structure** — access role via `msg.info.role`, text via `msg.parts[].text` where `part.type === "text"`.
4. **Hook ordering** — `messages.transform` fires BEFORE `system.transform`. Our system-prompt-rules plugin still works normally.
5. **No LLM calls** — classification must be pure keyword/regex, no API calls. Plugin must be fast.
6. **Coexistence** — must not conflict with system-prompt-rules.ts or any future compaction plugin.

## Success Criteria

1. ≥30% input token reduction for sessions with 3+ distinct topics and >10 messages
2. Zero breakage for single-topic sessions — single-topic guard detects only 1 topic domain present and returns early before any splice, guaranteed no modification (score=0 generic messages are NOT treated as "different topic")
3. Any failure returns unmodified messages (no regression possible)
4. tool_use/tool_result pairs never orphaned
5. Plugin loads in <10ms, per-request overhead <5ms (file reads are the bottleneck — consider caching)

## Risk Assessment

| Risk | Mitigation |
|------|-----------|
| Over-aggressive filtering removes needed context | Safety window + MIN_MESSAGES threshold + topic matching is additive (any keyword hit = keep) |
| Keyword matching too coarse | Phase 3a is conservative; false positives (keeping too much) preferred over false negatives |
| File I/O per request is slow | Cache topic-registry.json with mtime check (same pattern as system-prompt-rules caches rule files at init) |
| Plugin breaks on malformed topic data | Every read wrapped in try/catch → graceful degrade |
| Placeholder messages confuse the LLM | Use clear format: `[N messages from other topics omitted]` — LLMs handle this well |

## Test Plan

### Fixture Setup

Create `tests/plugin/fixtures/` with:
- `topic-registry-multi.json` — registry with active_topic pointing to a "database" topic
- `topic-database.json` — topic with title "Database Migration", tags ["database", "postgres", "migration"]
- `messages-multi-topic.json` — 20+ messages spanning 3 topics (database, auth, UI), with tool_use/tool_result pairs

### Test 1: Multi-topic filtering (unit)

**Tool**: `vitest` (or `tsx` script if no test runner configured)
**Setup**: Load fixture messages + topic registry. Call the classification + filtering logic directly.
**Command**: `npx tsx tests/plugin/topic-context-filter.test.ts`
**Expected**:
- Messages containing "database", "postgres", "migration" keywords → kept
- Messages about "auth", "login", "JWT" with no database keywords → removed
- Last 3 messages → always kept regardless of content
- tool_use/tool_result pairs → never split (if tool_use kept, its tool_result kept too)
- Output array shorter than input by ≥30%

### Test 2: Single-topic no-op (unit)

**Setup**: Messages in fixture contain a mix of database keywords and generic replies ("OK", "done", "got it") — simulating a real single-topic conversation where not every message mentions the topic explicitly.
**Expected**: Output === input (no splice called). Function detects only 1 topic domain ("database") among keyword-hitting messages and returns early via single-topic guard. Score=0 generic messages are preserved.

### Test 3: Short conversation no-op (unit)

**Setup**: Message array with 8 messages (below MIN_MESSAGES=10 threshold).
**Expected**: Output === input. Function returns early.

### Test 4: Graceful degradation (unit)

**Setup**: topic-registry.json path points to nonexistent file.
**Expected**: No error thrown. Output === input. Console.warn logged.

### Test 5: Integration — plugin loads without error

**Command**: `npx tsx -e "import p from './.opencode/plugin/topic-context-filter.ts'; console.log((await p({directory: '.'}, {enabled: true})).name)"`
**Expected**: Prints `topic-context-filter` without throwing.

### Test 6: A/B token measurement (manual, post-merge)

**Tool**: `uv run evals/v011-sysprompt-plugin-report/scripts/ab_test_harness.py`
**Setup**: Run 5 multi-topic sessions with plugin enabled vs disabled.
**Expected**: Mean input token reduction ≥30% for 3+ topic sessions. Single-topic sessions show 0% change.

## Estimated Effort

Phase 3a: 1-2 days implementation + 1 day testing = 2-3 days total.
