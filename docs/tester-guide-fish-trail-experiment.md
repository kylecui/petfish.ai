# Tester Guide: Fish Trail Deployment & Context-Filter A/B Experiment

## Overview

This guide covers two things:

1. **How to deploy fish-trail** (the topic/task management MCP server) in your test project
2. **How to run the A/B experiment** for Issue #135's context-filter plugin
3. **How fish-trail task management works** (conceptual reference)

---

## Part 1: Deploying Fish Trail

### What is Fish Trail?

Fish Trail is a topic governance system that tracks what you're working on, detects topic drift, and manages context isolation. It runs as an MCP server (stdio transport) alongside OpenCode.

### Prerequisites

- **uv** installed (`curl -LsSf https://astral.sh/uv/install.sh | sh` or `powershell -c "irm https://astral.sh/uv/install.ps1 | iex"`)
- **OpenCode** installed and working
- A project directory where you want to test

### Step 1: Install the context pack

From the petfish.ai repo root (or via remote installer):

```bash
# Local install (if you have the repo cloned)
./install.sh --pack context --target /path/to/your/test-project --platform opencode

# OR remote install
curl -fsSL https://raw.githubusercontent.com/kylecui/petfish.ai/master/remote-install.sh \
  | bash -s -- --pack context --target /path/to/your/test-project
```

```powershell
# PowerShell (local)
.\install.ps1 -Pack context -Target C:\path\to\your\test-project -Platform opencode

# OR remote
& ([scriptblock]::Create((irm https://raw.githubusercontent.com/kylecui/petfish.ai/master/remote-install.ps1))) -Pack context -Target C:\path\to\your\test-project
```

This installs the `fish-trail` skill and its MCP server into your project.

### Step 2: Verify opencode.json MCP config

After installation, your project's `opencode.json` should contain:

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

If it doesn't exist, add it manually or merge from the installed `opencode.example.json`.

### Step 3: Initialize state directory

The MCP server stores data in `.petfish/fish-trail/`. It auto-creates on first use, but you can bootstrap it:

```bash
mkdir -p .petfish/fish-trail/{topics,contexts,sessions,decisions}
```

Create a minimal config:

```yaml
# .petfish/fish-trail/config.yaml
base_dir: .petfish/fish-trail

companion_gateway:
  debug: true   # true = show all gateway decisions; false = only medium/high risk
```

### Step 4: Start OpenCode

```bash
opencode
```

The MCP server starts automatically when OpenCode launches (stdio transport — no separate process needed).

### Step 5: Verify MCP is running

In OpenCode, the agent should have access to tools like `topic_create`, `topic_detect`, `topic_list`, `session_bind`, etc. You can verify by asking:

> "Create a test topic called 'hello-world' with scope 'testing fish-trail setup'"

If it works, you'll see the topic created in `.petfish/fish-trail/topics/`.

### Troubleshooting

| Symptom | Fix |
|---------|-----|
| "context-state MCP not found" | Check `opencode.json` has the `mcp.context-state` entry |
| "uv: command not found" | Install uv: `curl -LsSf https://astral.sh/uv/install.sh \| sh` |
| "ModuleNotFoundError" | Ensure the `.opencode/skills/fish-trail/mcp/context-state/` directory has all `.py` files (server.py, topic_store.py, topic_detector.py, contamination_scorer.py, context_builder.py, session_store.py) |
| MCP timeout | The server is pure stdlib Python — no external deps. Check Python ≥3.11 is available via `uv run python --version` |

---

## Part 2: Running the A/B Experiment (Issue #135)

### What We're Testing

The **topic-context-filter plugin** removes off-topic messages from the LLM context window before each request. We want to measure:

- **Token reduction**: ≥30% input token savings for multi-topic sessions
- **Zero regression**: Single-topic sessions must be completely unaffected
- **No breakage**: tool_use/tool_result pairs must never be orphaned

### Experiment Setup

You need **two identical project directories** — one with the plugin enabled, one without.

#### Directory structure:

```
test-baseline/          ← No plugin
  .opencode/plugin/     ← Empty or missing topic-context-filter.ts
  .petfish/fish-trail/  ← Same topic data as test-plugin

test-plugin/            ← Plugin enabled
  .opencode/plugin/
    topic-context-filter.ts   ← The plugin under test
  .petfish/fish-trail/        ← Same topic data as test-baseline
```

#### Step 1: Prepare test-baseline

```bash
mkdir test-baseline && cd test-baseline
# Install petfish context pack
curl -fsSL https://raw.githubusercontent.com/kylecui/petfish.ai/master/remote-install.sh \
  | bash -s -- --pack context --detect
# Create some topics (see "Seeding Multi-Topic Data" below)
```

#### Step 2: Prepare test-plugin

```bash
cp -r test-baseline test-plugin
# Copy the plugin into test-plugin
cp /path/to/petfish.ai/.opencode/plugin/topic-context-filter.ts test-plugin/.opencode/plugin/
```

#### Step 3: Seed multi-topic data

Both directories need identical topic data. Create at least 3 topics in `.petfish/fish-trail/`:

```json
// .petfish/fish-trail/topic-registry.json
{
  "version": 1,
  "active_topic": "topic_database",
  "topics": {
    "topic_database": {
      "title": "Database Migration",
      "status": "active",
      "created_at": "2026-05-01T00:00:00Z",
      "updated_at": "2026-05-01T00:00:00Z"
    },
    "topic_auth": {
      "title": "Auth System",
      "status": "active",
      "created_at": "2026-05-01T00:00:00Z",
      "updated_at": "2026-05-01T00:00:00Z"
    },
    "topic_cicd": {
      "title": "CI/CD Pipeline",
      "status": "active",
      "created_at": "2026-05-01T00:00:00Z",
      "updated_at": "2026-05-01T00:00:00Z"
    }
  },
  "links": []
}
```

Create corresponding topic files in `.petfish/fish-trail/topics/`:

```json
// .petfish/fish-trail/topics/topic_database.json
{
  "id": "topic_database",
  "title": "Database Migration",
  "scope": "PostgreSQL schema design, migrations, indexes",
  "tags": ["database", "postgres", "migration", "sql", "schema"],
  "status": "active",
  "created_at": "2026-05-01T00:00:00Z",
  "updated_at": "2026-05-01T00:00:00Z"
}
```

(Create similar files for `topic_auth.json` and `topic_cicd.json`)

#### Step 4: Start the two OpenCode servers

Terminal 1 (baseline):
```bash
cd test-baseline
OPENCODE_SERVER_PASSWORD=test opencode serve --port 3100
```

Terminal 2 (plugin):
```bash
cd test-plugin
OPENCODE_SERVER_PASSWORD=test opencode serve --port 3200
```

#### Step 5: Run the A/B harness

```bash
cd /path/to/petfish.ai
AB_BASELINE_PORT=3100 AB_PLUGIN_PORT=3200 AB_PASSWORD=test \
  uv run evals/v011-sysprompt-plugin-report/scripts/ab_test_harness.py
```

The harness sends identical multi-topic conversation sequences to both servers and compares token usage.

### What the Harness Measures

| Metric | Description | Target |
|--------|-------------|--------|
| Input tokens (baseline) | Tokens sent to LLM without filtering | — |
| Input tokens (plugin) | Tokens sent to LLM with filtering | ≥30% less |
| Output quality | Response completeness/accuracy | No degradation |
| Error rate | Plugin crashes or malformed responses | 0% |
| Single-topic delta | Token difference in single-topic sessions | 0% (no change) |

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `AB_BASELINE_PORT` | 3100 | Port for baseline server |
| `AB_PLUGIN_PORT` | 3200 | Port for plugin server |
| `AB_PASSWORD` | "test" | Server auth password |
| `AB_MODEL` | "github-copilot/claude-sonnet-4" | Model for both servers |

### Manual Verification (Alternative to Harness)

If the automated harness isn't available, you can manually test:

1. Start OpenCode in `test-plugin/`
2. Have a multi-topic conversation (discuss database schema, then auth system, then come back to database)
3. Check `.opencode/plugin/` logs or observe that responses about database remain coherent even after long auth discussions
4. Compare token usage in OpenCode's usage display (if available)

### Expected Results

| Scenario | Expected Behavior |
|----------|-------------------|
| 3+ topics, 20+ messages, active topic = database | Auth and CI/CD messages filtered → ≥30% token reduction |
| Single topic (all database) | Plugin detects single-topic → no filtering (0% change) |
| Short conversation (<10 messages) | Plugin skips filtering entirely |
| fish-trail MCP not running | Plugin degrades gracefully — no filtering, no errors |
| Malformed topic-registry.json | Plugin catches error, returns messages unmodified |

---

## Part 3: How Fish Trail Task Management Works

### Conceptual Model

Fish Trail manages **topics** (units of work) and **sessions** (time-bounded interactions).

```
Session (time-based)
  └── bound to Topic (work-based)
       ├── title: "Database Migration"
       ├── scope: what this topic covers
       ├── tags: keywords for matching
       ├── status: active | paused | archived
       └── summary: current state of work
```

### Topic Lifecycle

```
create → active → (pause) → archive
                ↑         ↓
                └── resume ┘
```

### Key Operations

| Operation | What it does | When to use |
|-----------|-------------|-------------|
| `topic_create` | Create a new topic | Starting new work |
| `topic_detect` | Classify incoming message vs active topic | Every message (automated) |
| `topic_update` | Update topic summary/status | After meaningful progress |
| `topic_archive` | Freeze and store topic | Work complete |
| `session_bind` | Link an external session ID to a topic | Session start |
| `session_resume` | Find best session to continue for a topic | Returning to prior work |
| `topic_route` | Find most relevant topic for a query | Ambiguous context |

### How Topic Detection Works

Every incoming message is classified against the active topic:

1. **Keyword matching** — message text vs topic tags/scope
2. **Semantic similarity** — (optional, if embeddings enabled)
3. **Conversation continuity** — recent messages establish momentum

Result: `{ relation, risk_level, confidence }`

| Risk Level | Meaning | Action |
|------------|---------|--------|
| 0-30 (low) | Clearly same topic | Continue silently |
| 31-60 (medium) | Related but drifting | Note context boundary |
| 61-100 (high) | Different topic entirely | Suggest fork/switch |

### Data Storage

All state lives in `.petfish/fish-trail/`:

```
.petfish/fish-trail/
├── config.yaml          # Server config
├── topic-registry.json  # Index of all topics + active_topic pointer
├── topics/              # Per-topic JSON files (title, scope, tags, summary)
├── contexts/            # Built context packages
├── sessions/            # Session timeline data
└── decisions/           # Routing decision audit log
```

### Context Filter Plugin Integration

The topic-context-filter plugin (Issue #135) reads from this same data:

1. Reads `topic-registry.json` → gets `active_topic`
2. Reads `topics/{active_topic}.json` → gets tags/scope
3. Uses tags as keywords to classify messages
4. Removes messages that don't match the active topic (with safety guards)

This is why both the MCP server and the plugin need the `.petfish/fish-trail/` directory populated with topic data.

---

## Appendix: Quick Reference

### Install fish-trail (one command)

```bash
curl -fsSL https://raw.githubusercontent.com/kylecui/petfish.ai/master/remote-install.sh \
  | bash -s -- --pack context --detect
```

### Verify fish-trail is working

Ask the agent: *"list all topics"* — should return topic list or empty.

### Run the experiment (one command, after setup)

```bash
AB_PASSWORD=test uv run evals/v011-sysprompt-plugin-report/scripts/ab_test_harness.py
```

### Key files to watch

- `.petfish/fish-trail/topic-registry.json` — topic state
- `.opencode/plugin/topic-context-filter.ts` — the plugin under test
- `evals/v011-sysprompt-plugin-report/scripts/ab_test_harness.py` — measurement tool
