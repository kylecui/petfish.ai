# Companion Gateway

PEtFiSh's Companion Gateway runs automatically before every user message. It doesn't rely on the AI agent "remembering" to do it — it's injected at the highest priority position in the project's instructions file, so it executes every round.

## How It Works

```
User message
    → [Companion Gateway]
          │
          ├─ Step 0: Mode Read (project-mode.yaml)
          ├─ Step 1: Topic Check (topic_detect MCP)
          ├─ Step 1.5: Failure Signal Detection (previous turn errors)
          ├─ Step 2: Skill Sense (capability gap detection)
          ├─ Step 2.5: Anti-Sycophancy Check (evaluation questions)
          └─ Step 3: Proceed (normal processing)
```

### Step 0: Mode Read

Reads `.opencode/project-mode.yaml` (if present) on the first message of each session:

```yaml
depth: balanced       # urgent | balanced | thorough
rigor: false          # true | false (forced true when depth=thorough)
```

**Depth** controls how aggressively to debug, search, and respond to failures:

| Depth | Bug Handling | Dependency Issues | Search Strategy | Failure Response |
|---|---|---|---|---|
| urgent | Workaround first, log TODO | Use alternatives | First credible result | Quick fix → continue |
| balanced | Normal debug flow | Understand then fix | 2-3 sources | Standard flow |
| thorough | Must find root cause | Full impact analysis | Multi-source cross-check | Evidence-driven fix |

**Rigor** (when true or forced by `depth: thorough`) adds plan-then-review discipline: formal plan files for 3+ step tasks, Momus review before implementation, explicit assumption-stating.

**Session-only overrides**: Users can say "urgent" / "thorough" / "rigor" etc. to switch mode within a session without modifying the file. Reverts next session.

If the file doesn't exist, defaults to `depth: balanced, rigor: false`.

### Step 1: Topic Check

Calls `topic_detect` via MCP to assess the relationship between the current message and the active topic.

Three risk levels:
- **low (0-30)**: Silent, continue.
- **medium (31-60)**: One-line context note at reply start.
- **high (61-100)**: Pause, flag the drift, suggest fork/switch/reset.

If MCP is down, degrades silently — won't block your work.

### Step 1.5: Failure Signal Detection

Scans the **previous assistant turn** and tool error output for known failure patterns. When a match is found and a known skill/pack can solve it, recommends installation.

**Trigger conditions (all must be met):**
1. Previous turn explicitly acknowledged inability or tool returned a known error pattern.
2. A known skill/pack exists that can solve this failure class.
3. This signal hasn't been recommended this session (dedup).
4. The corresponding skill/pack is not already installed.

**Signal → Pack mapping:**

| Failure Pattern | Recommended Pack |
|---|---|
| Cannot read/parse PDF/PPTX | `ppt` |
| Deploy/Docker failure | `deploy` |
| Test case generation difficulty | `testdocs` |
| Research depth insufficient | `research` |
| Context contamination/drift | `context` |

Output format:
```
💡 Detected previous-turn failure signal — <pack> skill can handle this. Install: /petfish install <pack>
```

### Step 2: Skill Sense

Three-tier detection to spot capability gaps.

**Tier 1 — Keyword whitelist**: Matches against TRIGGERS in `catalog_query.py`. You say "deployment" → it knows to recommend the deploy pack. Only recommends when: keyword hit + pack not installed + not already recommended this session.

**Tier 2 — Intent detection**: When Tier 1 doesn't match, checks whether you're asking for something that needs external integration — email, charts, monitoring — that neither the agent nor installed skills can handle. Suggests `/petfish search <keyword>`.

**Tier 3 — No gap**: Nothing detected, stay silent.

Recommendations appear at the end of the reply, never interrupting. Each domain is mentioned at most once per session.

### Step 2.5: Anti-Sycophancy Check

Before answering evaluative questions ("is this good?", "is this right?", "what do you think?"):

1. **Pause**. Don't agree immediately.
2. Define what "good" means in this context (rubric-first).
3. Find at least **one** reason the proposal might be wrong.
4. Then form a conclusion.

If no counter-argument can be found after genuine effort → agreement is justified.
If this step is skipped → sycophancy is occurring.

**Proactivity linked to Rigor:**

| Rigor | Anti-Sycophancy Level |
|---|---|
| off | Only for explicit evaluative questions ("好吗?", "对吗?") |
| on | Also for implicit approval-seeking + technical assertions |

### Step 3: Proceed

Gateway done, normal processing begins.

### Post-Interaction Update

If this interaction produced real output (code changes, documents, decisions), calls `topic_update` to refresh topic state.

## Debug Mode

Configure in `.petfish/fish-trail/config.yaml`:

```yaml
companion_gateway:
  debug: true
```

- `debug: true`: Shows every Gateway decision (for development).
- `debug: false` (default): Only shows for medium/high risk or when there's a recommendation.

Debug output looks like:

```
🐟 [gateway] topic: relation=continue, risk=12 (low), confidence=0.92 → silent
🐟 [gateway] skill: no gap → pass

🐟 [gateway] topic: relation=switch, risk=67 (high), confidence=0.85 → suggest fork
🐟 [gateway] skill: gap=deploy (detected "Docker deployment") → recommend

🐟 [gateway] topic: relation=continue, risk=5 (low), confidence=0.95 → silent
🐟 [gateway] skill: tier2 gap detected (intent="send email", need="email integration") → suggest search
```

## Dependencies

Gateway depends on two components:

**1. context-state MCP** — Configured in `opencode.json`:
```json
{
  "mcp": {
    "context-state": {
      "type": "local",
      "command": ["uv", "run", "python", ".opencode/skills/fish-trail/mcp/context-state/server.py"]
    }
  }
}
```

**2. catalog_query.py TRIGGERS** — Keyword table in the companion skill:
```
.opencode/skills/fish-brain/scripts/catalog_query.py
```

## Install

Install the `companion` + `context` packs — Gateway activates automatically:

```bash
curl -fsSL https://raw.githubusercontent.com/kylecui/petfish.ai/master/remote-install.sh \
  | bash -s -- --pack companion,context
```

Gateway rules are injected into the target project via the AGENTS.md pack merge mechanism.

## Verify

Test keyword matching:
```bash
uv run python .opencode/skills/fish-brain/scripts/catalog_query.py --search "Docker"
# Should return: deploy pack
```

Test failure signal detection:
```bash
uv run python .opencode/skills/fish-brain/scripts/catalog_query.py --check-failures "无法读取PDF文件"
# Should return: ppt pack recommendation
```

Test MCP connectivity:
```bash
uv run python .opencode/skills/fish-trail/mcp/context-state/server.py
# Should start JSON-RPC server
```

Run tests:
```bash
uv run pytest tests/test_companion_gateway.py -v
```
