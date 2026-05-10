# Source Discovery: Topic-Aware Compaction

> 关联 Brief: `../00_brief/research-brief.md` (TAC-2026-001)
> 日期: 2026-05-10

---

## Assumption Verification

### A-1: Plugin hook receives session ID ✅ CONFIRMED

**Evidence** (SHA `2f11c9f7ed00980101655c14b82dc5dc7524a4cf`):

```typescript
// packages/plugin/src/index.ts L246-257
"experimental.session.compacting"?: (
  input: { sessionID: string },
  output: { context: string[]; prompt?: string },
) => Promise<void>
```

```typescript
// packages/opencode/src/session/compaction.ts
const compacting = yield* plugin.trigger(
  "experimental.session.compacting",
  { sessionID: input.sessionID },
  { context: [], prompt: undefined },
)
```

`input.sessionID` is the **only** field exposed. No messages, no agent, no model info. Plugin must use sessionID as lookup key to fetch topic context from fish-trail MCP.

---

### A-2: `output.context[]` reaches compaction LLM prompt ✅ CONFIRMED

**Evidence**:

```typescript
// compaction.ts
const nextPrompt = compacting.prompt ?? buildPrompt({ previousSummary, context: compacting.context })
```

```typescript
function buildPrompt(input: { previousSummary?: string; context: string[] }) {
  const anchor = input.previousSummary
    ? ["Update the anchored summary below...", "<previous-summary>", input.previousSummary, "</previous-summary>"].join("\n")
    : "Create a new anchored summary from the conversation history above."
  return [anchor, SUMMARY_TEMPLATE, ...input.context].join("\n\n")
}
```

`context[]` strings are spread into the final prompt with `\n\n` separators, sent verbatim as the LLM `user` message.

---

### A-3: `output.prompt` fully replaces default prompt ✅ CONFIRMED

```typescript
const nextPrompt = compacting.prompt ?? buildPrompt(...)
```

The `??` operator means: if `output.prompt` is set, `buildPrompt()` (and thus `context[]`) is **entirely skipped**. Full control, but mutually exclusive with `context[]`.

---

## Plugin Mutation Pattern

Hooks mutate `output` **by reference**. No return value.

```typescript
// Correct pattern:
"experimental.session.compacting": async (input, output) => {
  output.context.push("my context string")  // mutate in-place
  // do NOT return anything
}
```

Multiple plugins chain sequentially — each sees mutations from previous plugins.

---

## Plugin Registration (3 Methods)

| Method | How | Best For |
|--------|-----|----------|
| **Auto-discovery** | Drop `.ts`/`.js` in `.opencode/plugin/` | Development, project-local |
| **Config array** | `"plugin": ["./path.ts"]` in opencode.json | Explicit project config |
| **npm package** | `"plugin": ["pkg-name"]` in opencode.json | Distribution to users |

**Load order**: built-ins → global config → global plugin dir → project config → project plugin dir.

For fish-trail: **`.opencode/plugin/fish-trail-compaction.ts`** — zero config, auto-discovered.

---

## Reference Implementations

| Repo | Pattern | Relevance |
|------|---------|-----------|
| **engram** (Gentleman-Programming) | Full compaction hook + MCP bridge + sidecar process | **Best reference** — closest to our architecture |
| **gastown** (gastownhall) | Minimal `.opencode/plugins/` drop-in | Simplest example |
| **context-mode** (mksglu) | npm-distributed, FTS5 indexing | Distribution model |
| **everything-claude-code** (affaan-m) | Hook translation layer | Shows API evolution |
| **beans** (hmans) | Minimal local plugin | Minimal pattern |

**Key insight from engram**: It calls an HTTP sidecar to fetch context, exactly like we'd call fish-trail MCP. Pattern:
```typescript
"experimental.session.compacting": async (input, output) => {
  if (input.sessionID) await ensureSession(input.sessionID)
  const data = await fetch(`/context?project=${project}`)
  if (data?.context) output.context.push(data.context)
}
```

---

## Fish-trail Existing Hooks (Claude Code)

### `fish-trail-precompact.sh`
- Reads `.petfish/fish-trail/topic-registry.json` for `active_topic`
- Loads topic file from `.petfish/fish-trail/topics/<id>.json`
- Prints topic ID, title, status, summary to stdout
- **Reusable logic**: registry lookup → topic data extraction → summary formatting

### `fish-trail-postcompact.sh`
- Prints reminder that fish-trail is active
- Instructs agent to call `topic_detect` on next user message
- **Reusable logic**: post-compaction awareness injection

### MCP Server
- No compaction-specific methods exist
- `context_build(topic_id)` produces Context Packages suitable for injection
- `session_get(session_id)` can map session → topic bindings
- **Gap**: No direct `sessionID → active topic` lookup API. Need to bridge via session store.

---

## All Available Hooks

| Hook | Purpose | Relevant? |
|------|---------|-----------|
| `experimental.session.compacting` | Inject context / replace compaction prompt | **PRIMARY** |
| `experimental.compaction.autocontinue` | Control auto-continue after compaction | **SECONDARY** — may want to disable if topic switch detected |
| `experimental.chat.system.transform` | Modify system prompt | **OPTIONAL** — could inject topic awareness into every turn |
| `experimental.chat.messages.transform` | Rewrite message history | **FUTURE** — Phase 2/3 could use this for topic-filtered history |
| `event` | Internal bus events (session.created, etc.) | **OPTIONAL** — track session lifecycle |

---

## Design Implications

### Phase 1 (MVP) — Validated Feasible

```typescript
// .opencode/plugin/fish-trail-compaction.ts
import type { Plugin } from "@opencode-ai/plugin"

const plugin: Plugin = async ({ directory }) => ({
  "experimental.session.compacting": async (input, output) => {
    try {
      // 1. Map sessionID → active topic via fish-trail MCP or registry file
      // 2. Build Context Package for active topic
      // 3. Push to output.context[]
      const pkg = await getTopicContext(input.sessionID, directory)
      if (pkg) output.context.push(pkg)
    } catch {
      // Graceful degradation — don't break compaction
    }
  }
})

export default { id: "fish-trail-compaction", server: plugin }
```

### Phase 2 — Validated Feasible

Set `output.prompt` with topic-structured template. Replaces default 8-section `SUMMARY_TEMPLATE` with topic-organized version.

### Phase 3 — Requires Further Investigation

Skip LLM by setting `output.prompt` to a pre-computed summary. But: the compaction result is still processed by LLM (the prompt becomes the user message). To truly skip LLM, would need to intercept at a different level — possibly via `experimental.chat.messages.transform` to inject the summary as a pre-existing assistant message.

### Data Flow Gap

`input.sessionID` is an OpenCode session ID, not a fish-trail session ID. Need a mapping layer:
- **Option A**: Read `.petfish/fish-trail/topic-registry.json` directly (active_topic is global, not per-session)
- **Option B**: Call fish-trail MCP `session_resume` or `topic_route` with the OpenCode session ID
- **Option C**: Use `session_bind` at session start to associate OpenCode sessionID with fish-trail session

**Recommendation**: Option A for Phase 1 (simplest — just read the registry file for active topic), Option C for Phase 2+ (proper session binding).
