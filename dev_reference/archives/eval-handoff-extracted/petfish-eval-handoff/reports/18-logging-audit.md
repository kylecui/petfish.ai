# Fish-Trail Logging Adequacy Audit

**Date**: 2026-05-23
**Scope**: What fish-trail v1.1.0 logs vs what it should log

## What IS Logged

### 1. OpenCode server logs (`~/.local/share/opencode/log/`)
- MCP server registration: `service=mcp key=context-state toolCount=31`
- Permission evaluations: `service=permission permission=context-state_topic_list`
- Plugin loading: `service=plugin path=...system-prompt-context-inject.ts`
- **Does NOT log**: tool call arguments, tool results, model decisions about tools

### 2. MCP server internal state (`.petfish/fish-trail/`)
- `topic_graph.json`: topic nodes and edges (currently empty — v2 migration issue)
- `sessions/index.json`: session metadata (2 entries, minimal)
- `decisions/decision-log.json`: explicit decision records (**0 entries** — never used)
- `routes/last_route.json`: last routing result
- `active_context.md`: current topic context

### 3. topic_detect session events
- When topic_detect is called WITH session_id: records `{ts, type: "topic_transition", topic_id, relation, risk}`
- Stored in session's `timeline` array
- **Only recorded if model passes session_id** (not guaranteed)

## What is NOT Logged

### Critical gaps

| Operation | State Change | Audit Trail | Issue |
|-----------|-------------|-------------|-------|
| `topic_create` | New topic added | **NONE** | No record of who/when/why created |
| `topic_update` | Summary/status changed | **NONE** | No diff, no before/after |
| `topic_link` | Relationship created | **NONE** | No record of who linked or why |
| `topic_unlink` | Relationship removed | **NONE** | Destructive op with no trace |
| `topic_archive` | Topic frozen | **NONE** | No justification recorded |
| `session_bind` | New session created | **NONE** | No record of binding context |
| `session_close` | Session closed | Summary only | No timeline digest |

### Structural gaps

1. **No structured logging from MCP server** — server.py (1273 lines) uses no logging framework, no stdout/stderr output
2. **decision_log requires explicit model call** — the model must call the `decision_log` tool; it's never called automatically and our testing shows decision-log.json has 0 entries
3. **No tool call argument logging** — opencode logs permission checks but not what arguments were passed to MCP tools
4. **No tool result logging** — no way to see what topic_detect returned or what get_memory_context provided
5. **No timing data** — no way to measure MCP tool response times
6. **Decision log is always empty** — across all our testing sessions, decision-log.json has 0 entries

### Impact

1. **Undebuggable**: If topic state is wrong, there's no way to trace how it got that way
2. **No accountability**: topic_create, topic_update, topic_archive are state mutations with zero audit trail
3. **No performance data**: Can't tell if MCP tool calls are slow or fast
4. **No usage analytics**: Can't tell which tools are actually used in practice
5. **Plugin-inject blind**: The plugin reads from disk, but can't tell if the on-disk state is stale or corrupt

## How We Discovered This

Our investigation into MCP tool calling reliability required us to build an HTTP proxy (`/tmp/deepseek_proxy.py`) to intercept API requests, because:
- OpenCode's logs only show permission evaluations, not tool call arguments or results
- The MCP server produces no stdout/stderr output
- decision-log.json is always empty (model doesn't call the decision_log tool)
- Session timeline only records topic_detect events, not other mutations

This means the ONLY way to debug fish-trail behavior is external instrumentation — a sign that internal observability is insufficient.

## Recommendations

### P0: Auto-log mutations
topic_create, topic_update, topic_archive, topic_link, topic_unlink should automatically append to decision-log.json. Currently decision_log is an explicit tool call that no model ever makes. Making it automatic ensures every state change has an audit trail.

**Implementation**: At the end of each mutation handler in server.py, call `self.store.log_decision()` with:
```json
{
  "action": "topic_create",
  "source_topic": null,
  "target_topic": "<new_topic_id>",
  "risk_level": "info",
  "user_confirmed": false,
  "payload": { "title": "...", "scope": "..." }
}
```

### P1: MCP server stdout logging
Add Python `logging` to server.py (1273 lines, currently 0 logging calls) with structured output:
- Tool calls: `INFO topic_create args={...} duration=3ms`
- Errors: `ERROR topic_create failed: ...`
- State changes: `INFO topic_create created topic_abc123`

This enables opencode to capture MCP server output in its own log stream.

### P2: Plugin-inject validation logging
The system-prompt-context-inject plugin should log:
- What topic state it read from disk (topic IDs, summaries)
- Whether the read succeeded or failed
- What it injected into the system prompt (truncated)

This helps debug the one-turn-delay issue and verify the plugin is reading fresh data.

### P3: Health / diagnostic tool
Add a `diagnostic` tool that returns:
- Current topic count and active topic
- Last N decision-log entries
- Last session event timestamp
- Config state (Tier 1 only? Tier 2 embedding available?)

This gives a quick way to check system health without reading individual files.
