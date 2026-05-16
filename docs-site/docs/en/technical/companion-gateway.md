# Companion Gateway Architecture

How PEtFiSh implements an always-on interception layer that runs before every user message — without modifying the AI platform.

---

## Design Challenge

AI agents forget. They don't maintain state across turns unless explicitly told to. Context drifts silently, capability gaps go unnoticed, and sycophantic agreement replaces honest evaluation.

The typical solution — adding "remember to check X" to the system prompt — fails at scale. Agents skip optional instructions under token pressure, and there's no enforcement mechanism.

PEtFiSh's Companion Gateway solves this with a different approach: **mandatory pre-processing injected at the highest priority position in the instructions file**, making it structurally impossible to skip.

---

## Architecture

```text
User message arrives
    │
    ▼
┌─────────────────────────────────────────┐
│         Companion Gateway               │
│                                         │
│  Step 0: Mode Read ──────── Config      │
│  Step 1: Topic Check ────── MCP Server  │
│  Step 1.5: Failure Signal ── Catalog    │
│  Step 2: Skill Sense ────── Catalog     │
│  Step 2.5: Anti-Sycophancy              │
│  Step 3: Proceed                        │
│                                         │
│  Post: Topic Update ────── MCP Server   │
└─────────────────────────────────────────┘
    │
    ▼
Normal task processing
```

The Gateway is not a middleware layer or API proxy. It's a block of behavioral instructions placed at the top of the project's `AGENTS.md` file. The AI agent executes these steps as part of its own reasoning process — no external runtime required.

### Why This Works

Three properties make the Gateway reliable:

1. **Position priority.** Instructions at the top of `AGENTS.md` are processed before any task-specific rules. The agent reads the Gateway before it reads anything else.

2. **Unconditional execution.** The Gateway section uses imperative language ("MUST execute", "before processing") rather than conditional ("if applicable", "when needed"). This reduces the chance of the agent optimizing it away.

3. **Graceful degradation.** Every step that depends on external services (MCP, scripts) has a fallback that doesn't block normal work. The Gateway never makes your agent worse — it only makes it better when its dependencies are available.

---

## Step Design Rationale

The six steps weren't designed together. They evolved from observed failure modes in real projects.

### Step 0: Mode Read — Adaptive Behavior

**Problem solved:** Different project phases need different agent behavior. A production hotfix needs urgency; a design review needs thoroughness. Without explicit configuration, the agent defaults to a middle ground that satisfies neither.

**Design choice:** Two orthogonal axes (`depth` and `rigor`) rather than a single "mode" parameter. This lets you have `urgent + rigor` (fast but disciplined) or `thorough + no rigor` (deep but informal).

**Session overrides** exist because editing a YAML file mid-conversation is disruptive. The agent recognizes natural language mode switches ("let's be thorough here") and adjusts without file I/O.

### Step 1: Topic Check — Context Contamination Prevention

**Problem solved:** When users switch topics without explicit signaling, the agent carries forward context from the previous topic. This causes subtle bugs: variable names from topic A leak into topic B's code, decisions made for topic A constrain topic B's options.

**Design choice:** Delegate detection to an MCP server (`context-state`) rather than embedding heuristics in the prompt. The MCP server maintains a topic graph with contamination scoring, which is too stateful for prompt-only implementation.

**Risk levels** (low/medium/high) exist because not all topic shifts are dangerous. Asking a clarifying question within the same domain is low risk. Switching from "deploy service A" to "refactor service B" is high risk — the agent might apply service A's deployment constraints to service B's refactoring.

See [Token Cost Engineering](compaction.md) for how topic-aware compaction reduces token costs by 20%.

### Step 1.5: Failure Signal Detection — Learning from Mistakes

**Problem solved:** When an agent fails at a task (can't read a PDF, deployment errors), it typically apologizes and moves on. The user may not know that a skill pack exists that would solve the problem.

**Design choice:** Pattern matching against the previous turn's text, not real-time tool monitoring. This is simpler to implement and doesn't require hooking into tool execution. The trade-off is a one-turn delay — the recommendation appears after the failure, not during it.

**Deduplication** (once per session per signal) prevents the Gateway from nagging. If the user ignores the recommendation, it doesn't repeat.

### Step 2: Skill Sense — Proactive Gap Detection

**Problem solved:** Users don't know what skills are available. They ask the agent to do something, the agent tries with its base capabilities, and the result is mediocre — when a specialized skill would have produced much better output.

**Three-tier design:**

| Tier | Mechanism | Coverage | False Positive Risk |
|---|---|---|---|
| Tier 1 | Keyword whitelist | Known packs only | Very low |
| Tier 2 | Intent classification | Unknown domains | Moderate |
| Tier 3 | No detection | — | Zero |

Tier 1 is deliberately conservative — it only fires for known pack domains with confirmed keyword matches. Tier 2 uses broader intent analysis but only triggers at high confidence (>70%). Tier 3 is the default: when in doubt, stay silent.

**End-of-reply placement** ensures recommendations never interrupt the agent's actual work. The user gets their answer first, then the suggestion.

### Step 2.5: Anti-Sycophancy Check — Honest Evaluation

**Problem solved:** AI agents agree with users by default. When asked "is this a good approach?", they'll find reasons to say yes even when the approach has significant problems. This is particularly dangerous for architecture decisions, code reviews, and strategic planning.

**Design choice:** A mandatory counter-argument search before any evaluative conclusion. The agent must find at least one reason the user's proposal might be wrong before it's allowed to agree.

**Rigor linkage:** When rigor mode is off, anti-sycophancy only activates for explicit evaluative questions ("is this right?"). When rigor is on, it also activates for implicit approval-seeking ("I'm thinking of using X") and technical assertions ("this should work because..."). This graduated approach avoids slowing down casual conversations while providing full protection during critical decisions.

---

## Implementation Mechanics

### Injection via AGENTS.md

The Gateway is not a separate system — it's a section within `AGENTS.md` that gets merged during pack installation. The installation process:

1. `companion` pack includes Gateway rules in its `AGENTS.md` fragment
2. The installer merges this fragment into the project's `AGENTS.md` using marker-based merge (`<!-- agents-rules/... -->`)
3. The Gateway section is positioned at the top, before any pack-specific rules
4. On upgrade (`--force`), the section is replaced while preserving user-added content outside markers

This means the Gateway works on any platform that reads `AGENTS.md` (or equivalent) — OpenCode, Claude Code, Codex, Cursor, GitHub Copilot, Windsurf, and Antigravity. No platform-specific hooks required.

### External Dependencies

The Gateway interacts with two external components, both optional:

**context-state MCP server** — Provides topic detection (Step 1) and post-interaction updates. Runs as a local process, stores state in `.petfish/fish-trail/`. Installed via the `context` pack.

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

**catalog_query.py** — Provides keyword matching (Step 2) and failure signal detection (Step 1.5). A Python script in the `companion` pack that reads pack metadata and trigger definitions.

```bash
# Keyword matching
uv run python .opencode/skills/petfish-companion/scripts/catalog_query.py \
  --search "Docker"

# Failure signal detection
uv run python .opencode/skills/petfish-companion/scripts/catalog_query.py \
  --check-failures "无法读取PDF文件"
```

When either component is unavailable, the corresponding steps silently skip. The Gateway never produces errors — it only produces recommendations or silence.

### Debug Mode

For development visibility, the Gateway supports a debug mode that shows every decision:

```
🐟 [gateway] topic: relation=continue, risk=12 (low), confidence=0.92 → silent
🐟 [gateway] skill: no gap → pass
```

This is configured in `.petfish/fish-trail/config.yaml` and defaults to off. When developing or debugging Gateway behavior, turning it on reveals the full decision chain without requiring log files or external monitoring.

---

## Design Constraints

Several constraints shaped the Gateway's architecture:

### No Runtime Required

The Gateway must work without any running service. MCP servers and scripts enhance it, but the core behavioral rules (Mode Read, Anti-Sycophancy Check) work purely through prompt instructions. This means even a freshly installed project with no MCP configuration still benefits from the Gateway.

### Token Budget

The Gateway section in `AGENTS.md` consumes tokens on every interaction. The current implementation is approximately 2,500 tokens — roughly 3% of a typical 80K context window. This budget is justified by the [system prompt injection experiment](sysprompt-design.md) showing that well-structured instructions reduce compaction frequency, producing a net token savings of ~19%.

### One-Turn Latency

Failure Signal Detection (Step 1.5) scans the previous turn, not the current one. This means the first failure isn't caught — only subsequent interactions benefit. This is an intentional trade-off: real-time tool monitoring would require platform-specific hooks that break the "works everywhere" design goal.

### Session Scope

Mode overrides and recommendation deduplication are session-scoped. The Gateway has no persistent memory beyond what the MCP server provides for topic state. This simplifies the implementation but means each new session starts fresh — mode reverts to the config file default, and recommendation dedup resets.

---

## Evolution

The Gateway started as a 3-step process in v0.6.0:

```text
v0.6.0: Topic Check → Skill Sense → Proceed
v0.11.0: Mode Read → Topic Check → Failure Signal → Skill Sense → Anti-Sycophancy → Proceed
```

Each addition came from a specific failure mode observed in production use:

| Version | Step Added | Failure Mode |
|---|---|---|
| v0.6.0 | Topic Check | Context contamination across topics |
| v0.6.0 | Skill Sense | Users not discovering available skills |
| v0.11.0 | Mode Read | Wrong behavior intensity for project phase |
| v0.11.1 | Failure Signal | Repeated failures without pack recommendations |
| v0.11.4 | Anti-Sycophancy | Uncritical agreement with flawed proposals |

The 6-step structure is likely not final. Future additions will follow the same pattern: observe a systematic failure mode, design a minimal intervention, and add it as a new step with graceful degradation.

---

## Related

- [System Prompt Architecture](sysprompt-design.md) — how Gateway rules fit into the layered instruction system
- [Token Cost Engineering](compaction.md) — how topic-aware context management reduces session costs
- [Companion Gateway Guide](../guides/companion-gateway/index.md) — user-facing setup and usage instructions
