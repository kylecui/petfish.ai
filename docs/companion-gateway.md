# Companion Gateway

PEtFiSh's Companion Gateway runs automatically before every user message. It doesn't rely on the AI agent "remembering" to do it — it's injected at the highest priority position in the project's instructions file, so it executes every round.

## How It Works

```
User message
    → [Companion Gateway]
          │
          ├─ Step 1: Topic Check (topic_detect MCP)
          ├─ Step 2: Skill Sense (capability gap detection)
          └─ Step 3: Proceed (normal processing)
```

### Step 1: Topic Check

Calls `topic_detect` via MCP to assess the relationship between the current message and the active topic.

Three risk levels:
- **low (0-30)**: Silent, continue.
- **medium (31-60)**: One-line context note at reply start.
- **high (61-100)**: Pause, flag the drift, suggest fork/switch/reset.

If MCP is down, degrades silently — won't block your work.

### Step 2: Skill Sense

Three-tier detection to spot capability gaps.

**Tier 1 — Keyword whitelist**: Matches against TRIGGERS in `catalog_query.py`. You say "deployment" → it knows to recommend the deploy pack. Only recommends when: keyword hit + pack not installed + not already recommended this session.

**Tier 2 — Intent detection**: When Tier 1 doesn't match, checks whether you're asking for something that needs external integration — email, charts, monitoring — that neither the agent nor installed skills can handle. Suggests `/petfish search <keyword>`.

**Tier 3 — No gap**: Nothing detected, stay silent.

Recommendations appear at the end of the reply, never interrupting. Each domain is mentioned at most once per session.

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
.opencode/skills/petfish-companion/scripts/catalog_query.py
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
uv run python .opencode/skills/petfish-companion/scripts/catalog_query.py --search "Docker"
# Should return: deploy pack
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
