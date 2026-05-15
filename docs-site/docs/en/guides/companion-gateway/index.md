# Companion Gateway

The Companion Gateway runs automatically before every user message. It doesn't rely on the AI agent "remembering" — it's injected at the highest priority position in your project's instructions file.

## How It Works

```
User message
    → [Companion Gateway]
          │
          ├─ Step 0: Mode Read
          ├─ Step 1: Topic Check
          ├─ Step 1.5: Failure Signal Detection
          ├─ Step 2: Skill Sense
          ├─ Step 2.5: Anti-Sycophancy Check
          └─ Step 3: Proceed
```

---

## Step 0: Mode Read

On the first message of each session, the Gateway reads `.opencode/project-mode.yaml`:

```yaml
depth: balanced       # urgent | balanced | thorough
rigor: false          # true | false (forced true when depth=thorough)
```

### Depth

Controls how aggressively the agent debugs, searches, and responds to failures.

| Depth | Bug Handling | Dependencies | Search | Failure Response |
|---|---|---|---|---|
| `urgent` | Workaround first, log TODO | Use alternatives | First credible result | Quick fix, continue |
| `balanced` | Normal debug flow | Understand then fix | 2–3 sources | Standard flow |
| `thorough` | Must find root cause | Full impact analysis | Multi-source cross-check | Evidence-driven fix |

### Rigor

When `rigor: true` (or forced by `depth: thorough`):

- Complex tasks (3+ steps or 3+ files) require a formal plan file
- Plans are reviewed by a plan critic before implementation
- Assumptions must be stated explicitly before acting on them

### Session Overrides

Switch modes mid-session without editing the file:

| Say this | Effect |
|---|---|
| "urgent", "快速", "workaround" | Switch to urgent mode |
| "balanced", "正常" | Switch to balanced mode |
| "thorough", "仔细", "root cause" | Switch to thorough mode |
| "rigor", "严谨", "plan first" | Enable rigor |
| "快做", "skip plan" | Disable rigor |

Changes revert next session. If the config file doesn't exist, defaults to `balanced` + `rigor: false`.

---

## Step 1: Topic Check

Calls `topic_detect` via the context-state MCP to assess whether your message belongs to the current topic.

| Risk Level | What Happens |
|---|---|
| **Low** (0–30) | Silent. No output. |
| **Medium** (31–60) | One-line note at the start of the reply explaining context inheritance. |
| **High** (61–100) | Pauses normal processing. Flags the drift and suggests fork/switch/reset. |

!!! info "Graceful degradation"
    If the context-state MCP isn't running, Topic Check silently skips. Your work continues uninterrupted. You'll see a one-time notice: "⚠ fish-trail MCP not connected."

---

## Step 1.5: Failure Signal Detection

Scans the **previous assistant turn** and tool error output for known failure patterns. If a matching pack exists and isn't installed, recommends it.

All four conditions must be met:

1. Previous turn explicitly acknowledged inability, or a tool returned a known error pattern
2. A known skill pack can solve this failure class
3. This signal hasn't been recommended this session (dedup)
4. The corresponding pack isn't already installed

### Signal → Pack Mapping

| Failure Pattern | Recommended Pack |
|---|---|
| Cannot read/parse PDF or PPTX | `ppt` |
| Deploy/Docker failure | `deploy` |
| Test case generation difficulty | `testdocs` |
| Research depth insufficient | `research` |
| Context contamination/drift | `context` |

When triggered, you'll see:

```
💡 Detected previous-turn failure signal — deploy skill can handle this.
   Install: /petfish install deploy
```

---

## Step 2: Skill Sense

Three-tier detection to spot capability gaps before they cause failures.

### Tier 1 — Keyword Whitelist

Matches your message against known trigger keywords. You say "deployment" → PEtFiSh knows to recommend the `deploy` pack. Only fires when: keyword match + pack not installed + not already recommended this session.

### Tier 2 — Intent Detection

When Tier 1 doesn't match, checks whether your request needs external integration (email, charts, monitoring) that neither the agent nor installed skills can handle. Suggests `/petfish search <keyword>` to find a matching skill or MCP server.

**Examples:**

| Request | Fires? | Why |
|---|---|---|
| "Help me deploy this" | Tier 1 | "deploy" keyword match |
| "Send an email to the team" | Tier 2 | Needs email integration |
| "Refactor this function" | No | Agent native capability |
| "Fix this type error" | No | Agent native capability |

### Tier 3 — No Gap

Nothing detected. Silent.

Recommendations always appear at the end of the reply, never interrupting the main response. Each domain is mentioned at most once per session.

---

## Step 2.5: Anti-Sycophancy Check

Before answering evaluative questions ("is this good?", "is this right?", "what do you think?"):

1. **Pause.** Don't agree immediately.
2. **Define "good"** in this context — establish a rubric before forming a conclusion.
3. **Find at least one reason** the proposal might be wrong.
4. **Then** form a conclusion.

If no counter-argument can be found after genuine effort → agreement is justified.
If this step is skipped → sycophancy is occurring.

### Proactivity Linked to Rigor

| Rigor | Anti-Sycophancy Level |
|---|---|
| Off | Only for explicit evaluative questions ("好吗?", "is this right?") |
| On | Also for implicit approval-seeking and technical assertions |

---

## Step 3: Proceed

Gateway complete. Normal processing begins with the right context in place.

### Post-Interaction Update

If the interaction produced real output (code changes, documents, decisions), the Gateway calls `topic_update` to refresh topic state for future context checks.

---

## Debug Mode

Configure in `.petfish/fish-trail/config.yaml`:

```yaml
companion_gateway:
  debug: true   # true = show every decision, false = only medium/high
```

Debug output appears at the top of every reply:

```
🐟 [gateway] topic: relation=continue, risk=12 (low), confidence=0.92 → silent
🐟 [gateway] skill: no gap → pass
```

```
🐟 [gateway] topic: relation=switch, risk=67 (high), confidence=0.85 → suggest fork
🐟 [gateway] skill: gap=deploy (detected "Docker deployment") → recommend
```

```
🐟 [gateway] topic: relation=continue, risk=5 (low), confidence=0.95 → silent
🐟 [gateway] skill: tier2 gap detected (intent="send email", need="email integration") → suggest search
```

| Setting | Behavior |
|---|---|
| `debug: true` | Always show Gateway decisions |
| `debug: false` (default) | Only show for medium/high risk or when there's a recommendation |

---

## Dependencies

The Gateway relies on two optional components:

### context-state MCP

Provides Topic Check (Step 1) and post-interaction updates. Configured in `opencode.json`:

```json
{
  "mcp": {
    "context-state": {
      "type": "local",
      "command": ["uv", "run", "python",
        ".opencode/skills/fish-trail/mcp/context-state/server.py"]
    }
  }
}
```

Install with: `/petfish install context`

### catalog_query.py

Provides Skill Sense keyword matching (Step 2) and Failure Signal Detection (Step 1.5):

```
.opencode/skills/petfish-companion/scripts/catalog_query.py
```

Installed automatically with the `companion` pack.

---

## Verify

Test keyword matching:

```bash
uv run python .opencode/skills/petfish-companion/scripts/catalog_query.py \
  --search "Docker"
# Should return: deploy pack
```

Test failure signal detection:

```bash
uv run python .opencode/skills/petfish-companion/scripts/catalog_query.py \
  --check-failures "无法读取PDF文件"
# Should return: ppt pack recommendation
```

Test MCP connectivity:

```bash
uv run python .opencode/skills/fish-trail/mcp/context-state/server.py
# Should start JSON-RPC server
```
