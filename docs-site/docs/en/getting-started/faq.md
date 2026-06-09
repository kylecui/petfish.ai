# FAQ & Troubleshooting

## Installation

### "Pack already installed" — how do I update?

The installer skips packs that appear current. Use `--force` to re-install:

```bash
uv run https://raw.githubusercontent.com/kylecui/petfish.ai/master/install.py --pack all --force
```

Or run `/petfish upgrade` in your AI assistant to see the exact command.

### The installer says "uv not found"

PEtFiSh requires [uv](https://docs.astral.sh/uv/getting-started/installation/) for Python-based skills and MCP servers. Install it:

=== "macOS / Linux / WSL"

    ```bash
    curl -LsSf https://astral.sh/uv/install.sh | sh
    ```

=== "Windows PowerShell"

    ```powershell
    powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
    ```

### My AI platform wasn't auto-detected

Use the `--platform` flag explicitly:

```bash
--platform opencode   # or claude, cursor, codex, copilot, windsurf, antigravity
```

See [Platform Support](../reference/platform-support.md) for detection markers and directories.

### Can I install to a private/enterprise repo?

Yes. Pass a GitHub token:

```bash
GITHUB_TOKEN=xxx uv run https://raw.githubusercontent.com/kylecui/petfish.ai/master/install.py --pack companion
```

---

## Companion Gateway

### The Companion Gateway isn't running

The Gateway is embedded in the `AGENTS.md` (or platform equivalent) instructions file. It runs automatically on every message — there's no separate process to start. Verify:

1. `companion` pack is installed: check your skills directory for `petfish-companion/`
2. Your instructions file (`AGENTS.md`, `CLAUDE.md`, etc.) contains the Gateway section

### "⚠ fish-trail MCP not connected"

This means the context-state MCP server isn't running. The Gateway still works — topic governance is just disabled. To fix:

1. Ensure the `context` pack is installed
2. Check `opencode.json` (or equivalent) has the MCP server configured
3. Verify `uv` is installed and the server path is correct

### How do I switch project modes?

Say keywords in conversation — no file edits needed:

- **urgent**: "紧急", "urgent", "快速", "workaround"
- **balanced**: "正常", "balanced", "标准流程"
- **thorough**: "仔细", "thorough", "root cause", "彻底"
- **rigor on**: "严谨", "rigor", "plan first"
- **rigor off**: "快做", "直接做", "skip plan"

Or edit `.opencode/project-mode.yaml` for persistent settings.

---

## Skills & Packs

### How do I see what's installed?

Run `/petfish` in your AI assistant. It shows all installed packs and skills.

### A skill isn't triggering

1. Check the skill's `SKILL.md` description — the AI matches on frontmatter `description` only
2. Try using keywords listed in the skill's trigger phrases
3. Run `/petfish eval <path>` to test trigger accuracy
4. Run `/petfish optimize <path>` to improve the description

### How do I create a custom skill?

Run `/petfish create <name>` or use the `skill-author` skill directly. It scaffolds a valid skill directory with `SKILL.md`, references, and optional scripts.

### How do I publish a skill?

Run `/petfish gate <path>` to execute the full quality gate (lint → security audit → metadata validation → decision). The gate outputs PASS, CONDITIONAL, or FAIL.

---

## Upgrade

### How do I check for updates?

Run `/petfish upgrade` — it queries the latest GitHub release and shows the upgrade command if a newer version exists.

### What does `--force` do?

It re-installs packs even if they appear current. Use it when:

- A new release is available
- You want to pick up renamed packs or migrated files
- Something seems broken and you want a clean re-install

### Do I lose my data when upgrading?

No. The installer only writes to the skills directory. Your project files, MCP state (topics, sessions), and configuration are preserved. The fish-trail MCP server auto-migrates state directories when needed.

---

## MCP & Fish Trail

### What MCP tools are available?

The `context` pack provides 31 MCP tools via the context-state server, covering:

- Topic management (create, update, archive, search, link, route)
- Session tracking (bind, resume, close, query, timeline)
- Contamination scoring and context building
- Decision logging and topic graph validation

### My topic data is missing after upgrade

The auto-migration from `.ai-context/` to `.petfish/fish-trail/` runs once on first server start. If the old directory was deleted before migration, the data is lost. Check `.petfish/fish-trail/` for your current topics.

---

## General

### What Python version do I need?

Python 3.10+ for skills with scripts. The unified Python installer (`install.py`) uses PEP 723 inline metadata and auto-bootstraps via `uv run` — no manual Python setup needed.

### Does PEtFiSh work offline?

After installation, yes. Skills are local files. The only network calls happen during install/upgrade (downloading from GitHub) and if you use web-search-dependent skills (like marketplace-connector). For offline install, clone the repo and use `--offline`.

### How do I uninstall a pack?

```bash
uv run https://raw.githubusercontent.com/kylecui/petfish.ai/master/install.py --uninstall <alias>
```

Or from a cloned repo:

```bash
uv run ./install.py --uninstall <alias>
```
