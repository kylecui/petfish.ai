# PEtFiSh Upgrade Guide (for AI Agents)

> If you are an AI coding assistant reading this document, follow the steps below to upgrade PEtFiSh for the user. Do NOT summarize or skip steps. Execute them in order.

---

## When to use this guide

Use this guide when:
- User already has PEtFiSh installed (check: `.opencode/installed-packs.json` or similar exists)
- User wants to update to the latest version
- User is on v0.4.x or earlier and needs to get to v0.5.x

If PEtFiSh is NOT installed yet, use `docs/agent-install.md` instead.

---

## Step 0: Assess current state

1. Check installed version:

```bash
# Look for installed-packs.json
cat .opencode/installed-packs.json 2>/dev/null || cat .claude/installed-packs.json 2>/dev/null || echo "No registry found"
```

2. Check what packs are currently installed by looking at the skills directory:

```bash
ls .opencode/skills/ 2>/dev/null || ls .claude/skills/ 2>/dev/null
```

3. Tell the user what you found:

```
><(((^> 胖鱼 PEtFiSh — Upgrade Check

Current state:
- Platform: [detected]
- Installed packs: [list from registry or directory scan]
- Version: [from registry or "unknown (pre-registry)"]

I'll upgrade you to the latest release.
```

---

## Step 1: Detect environment

Same as install guide:
1. OS: macOS/Linux/WSL → Bash, Windows → PowerShell
2. Platform: detect from markers or use your own platform identity

> **Important**: You are an AI agent — use `--platform <your_platform>` explicitly.

---

## Step 2: Understand what's changing (v1.3.x → v1.4.x)

### Breaking changes to be aware of:

| Change | Impact | Auto-handled? |
|--------|--------|---------------|
| packs/ restructured → `packs/core/` + `packs/optional/` | Pack directories moved under new parent dirs | ✅ Yes — installer scans both core/ and optional/ |
| Optional packs distributed via petfish-market | Remote installer resolves optional packs from market | ✅ Yes — `query_market_index()` / `Query-MarketIndex` auto-handle |
| `skill-publish` added to toolchain | Toolchain now has 9 skills (was 8) | ✅ Yes — included in `toolchain` pack upgrade |

### New features in v1.4.x:

- **`skill-publish`** — new toolchain skill bridging quality-gate PASS → petfish-market availability
- **Market-aware installers** — remote installers (`remote-install.sh`, `remote-install.ps1`) query petfish-market for optional pack downloads; no user-visible command change
- **`catalog_query.py`** — `--install <alias>` flag with market awareness; auto-resolves optional pack sources
- **`marketplace_search.py`** — prioritizes petfish-market as primary search source
- **petfish-market** — `registry/official/` with 10 official pack entries; `index.json` v2
- **Pack count** — 4 core packs (init, companion, petfish, toolchain) + 10 optional packs via market

### Migration steps for v1.4.x:

1. Re-run the installer with `--force` to pick up the new pack structure:
   ```bash
   curl -fsSL https://raw.githubusercontent.com/kylecui/petfish.ai/master/remote-install.sh | bash -s -- --pack all --force --platform <PLATFORM>
   ```
2. Core packs install as before. Optional packs are resolved via petfish-market automatically.
3. If you use toolchain skills, the upgrade includes the new `skill-publish` skill.

---

## Step 2b: Understand what's changing (v1.2.x → v1.3.x)

### Breaking changes to be aware of:

| Change | Impact | Auto-handled? |
|--------|--------|---------------|
| `petfish-companion` skill renamed → `fish-brain` | Skill directory name changed | ✅ Yes — installer handles legacy names |
| `marketplace-connector` skill renamed → `fish-market` | Skill directory name changed | ✅ Yes — installer handles legacy names |
| 8 toolchain skills moved from `companion` → new `toolchain` pack | Skills now in separate pack | ⚠️ Install `toolchain` pack separately if needed |

### New features in v1.3.x:

- **`toolchain` pack** — 8 skill lifecycle skills extracted from `companion` (skill-author, skill-lint, repo-skill-miner, skill-security-auditor, quality-gate, skill-description-optimizer, skill-trigger-evaluator, skill-usage-tracker)
- **`fish-brain`** (鱼伴) — renamed from `petfish-companion`; same orchestration and sensing role
- **`fish-market`** (鱼市) — renamed from `marketplace-connector`; same external search role
- **`companion` pack** now ships only 2 core skills (fish-brain + fish-market)
- Total packs: 12 → 13; total skills: unchanged at 96

### Migration steps for v1.3.x:

1. Re-run the installer with `--force` to get renamed skills:
   ```bash
   curl -fsSL https://raw.githubusercontent.com/kylecui/petfish.ai/master/remote-install.sh | bash -s -- --pack companion --force --platform <PLATFORM>
   ```
2. If you use toolchain skills (lint, audit, gate, etc.), install the new pack:
   ```bash
   curl -fsSL https://raw.githubusercontent.com/kylecui/petfish.ai/master/remote-install.sh | bash -s -- --pack toolchain --platform <PLATFORM>
   ```
3. Update any AGENTS.md or config references from `petfish-companion` → `fish-brain` and `marketplace-connector` → `fish-market`.

---

## Step 2: Understand what's changing (v0.4.x → v0.5.x)

### Breaking changes to be aware of:

| Change | Impact | Auto-handled? |
|--------|--------|---------------|
| Repo renamed `SKILL_builder` → `petfish.ai` | Install URLs changed | ✅ Yes — new scripts auto-resolve |
| Pack renamed `context-router-skill` → `fish-trail` | Skill directory name changed | ✅ Yes — installer handles legacy names |
| State dir `.ai-context/` → `.petfish/fish-trail/` | MCP data location moved | ✅ Yes — server auto-migrates on first start |
| MCP server version 0.3.0 → 0.5.1 | New tools available (31 total, was 28) | ✅ Yes — comes with pack update |

### New features in v0.5.x:

- **fish-trail** pack with 31 MCP tools (topic routing, reporting, validation)
- **fish-\* alias system** — install packs via fish-trail, fish-core, fish-init etc.
- **Topic routing scripts** — `topic_route.py`, `topic_report.py`, `topic_validate.py`
- **Context firewall** — must_load/may_load/must_not_load for topic isolation
- **trust** pack — skill trust governance engine (new pack)

---

## Step 3: Upgrade all installed packs

You can run `/petfish upgrade` to see the upgrade command for your OS, or run the remote installer with `--force` flag directly:

**Bash:**
```bash
curl -fsSL https://raw.githubusercontent.com/kylecui/petfish.ai/master/remote-install.sh | bash -s -- --pack all --force --platform <PLATFORM>
```

**PowerShell:**
```powershell
& ([scriptblock]::Create((irm https://raw.githubusercontent.com/kylecui/petfish.ai/master/remote-install.ps1))) -Pack all -Force -Platform <PLATFORM>
```

Replace `<PLATFORM>` with the detected platform (e.g. `opencode`, `claude`, `codex`, etc.).

> **What `--force` does**: Re-installs all packs even if they appear current. This ensures renamed packs (like context-router-skill → fish-trail) get properly migrated.

> **What `--pack all` does**: Installs/upgrades every available pack. If the user only wants specific packs, replace `all` with a comma-separated list (e.g. `companion,context,petfish`).

---

## Step 4: Handle legacy pack cleanup

After upgrade, check if old pack directories remain:

```bash
# Check for legacy context-router directories
ls .opencode/skills/context-router/ 2>/dev/null && echo "⚠️  Legacy context-router directory still exists"
ls .opencode/skills/context-router-skill/ 2>/dev/null && echo "⚠️  Legacy context-router-skill directory still exists"
```

If legacy directories exist, remove them:

```bash
rm -rf .opencode/skills/context-router/ .opencode/skills/context-router-skill/ 2>/dev/null
```

**PowerShell:**
```powershell
Remove-Item -Recurse -Force .opencode/skills/context-router/, .opencode/skills/context-router-skill/ -ErrorAction SilentlyContinue
```

---

## Step 5: Update opencode.json / config (if applicable)

If the project has an `opencode.json` with MCP configuration for context-router, update it:

**Before (old):**
```json
{
  "permissions": {
    "context-router": { "allow": ["*"] }
  },
  "mcpServers": {
    "context-state": {
      "command": "uv",
      "args": ["run", "python", ".opencode/skills/context-router/mcp/context-state/server.py"]
    }
  }
}
```

**After (new):**
```json
{
  "permissions": {
    "fish-trail": { "allow": ["*"] }
  },
  "mcpServers": {
    "context-state": {
      "command": "uv",
      "args": ["run", "python", ".opencode/skills/fish-trail/mcp/context-state/server.py"]
    }
  }
}
```

Key changes:
- Permission key: `context-router` → `fish-trail`
- MCP path: `.opencode/skills/context-router/mcp/...` → `.opencode/skills/fish-trail/mcp/...`

> If the project does NOT use the context/fish-trail MCP, skip this step.

---

## Step 6: Update AGENTS.md pack markers (if applicable)

If the project's AGENTS.md contains context-router pack markers, they need updating:

**Find and replace:**
- `<!-- BEGIN pack: context-router-skill -->` → `<!-- BEGIN pack: fish-trail -->`
- `<!-- END pack: context-router-skill -->` → `<!-- END pack: fish-trail -->`

The installer should handle this automatically with `--force`, but verify:

```bash
grep -n "context-router" AGENTS.md 2>/dev/null
```

If any remain, the `--force` install should have replaced them. If not, manually update the markers.

---

## Step 7: Verify state directory migration

The fish-trail MCP server auto-migrates `.ai-context/` → `.petfish/fish-trail/` on first start. Verify:

```bash
# Check if old state dir exists (will be migrated on next MCP start)
ls .ai-context/ 2>/dev/null && echo "Old state dir exists — will auto-migrate on next MCP server start"

# Check if new state dir exists
ls .petfish/fish-trail/ 2>/dev/null && echo "✅ New state dir already present"
```

No manual action needed — the server handles migration transparently. Old data (topics, sessions, decisions) will be preserved.

---

## Step 8: Restart and verify

> **Important**: After upgrading, you MUST restart your AI coding tool for new skills to load.

| Platform | Restart hint |
|---|---|
| opencode | `⚠️  Restart needed. Exit: Ctrl+C \| Resume: opencode -s <session_id>` |
| claude | `⚠️  Restart needed. Exit: /exit or Ctrl+C \| Resume: claude --continue` |
| codex | `ℹ️  Restart may be needed. Exit with Ctrl+C and re-launch.` |
| cursor | `⚠️  Restart needed. Reload window: Ctrl+Shift+P → "Reload Window"` |
| copilot | `⚠️  Restart needed. Reload window: Ctrl+Shift+P → "Reload Window"` |
| windsurf | `⚠️  Restart needed. Reload window: Ctrl+Shift+P → "Reload Window"` |
| antigravity | `⚠️  Restart needed. Exit: Ctrl+C` |

After restart, verify:

```
/petfish
```

Should show updated pack versions. Then confirm fish-trail MCP is working:

```
# The fish-trail MCP should auto-start and show 31 tools
```

Tell the user:

```
><(((^> PEtFiSh upgraded!

Changes applied:
- [list upgraded packs]
- fish-trail: 31 MCP tools (topic routing, reporting, validation)
- State dir: auto-migrates .ai-context → .petfish/fish-trail/
- New: context firewall, topic graph validation

Next steps:
  /petfish catalog    — See all available skills (including new ones)
  /petfish stats      — Check usage statistics
```

---

## Upgrade from specific versions

### From v0.3.x or earlier (pre-context-router)

These versions don't have context-router at all. Just run Step 3 (`--pack all --force`) and skip Steps 4-7.

### From v0.4.0–v0.4.9 (context-router, pre-session)

Has context-router but no session management. Follow all steps. The `--force` upgrade will:
- Replace context-router skill with fish-trail
- Add session management tools (10 new tools)
- Add topic routing scripts

### From v0.4.10–v0.4.15 (context-router with sessions)

Has full context-router with 28 tools. Follow all steps. The upgrade will:
- Rename skill directory
- Add 3 new tools (topic_route, topic_report, topic_validate → 31 total)
- Migrate state directory path

### From v0.5.0 (already renamed)

Already has fish-trail naming. Run Step 3 with `--force` to pick up the latest scripts and docs. Skip Steps 4-6.

---

## Troubleshooting

- **"Pack already installed"** without `--force`: The installer skips packs at the same version. Use `--force` to re-install regardless.
- **Legacy directories remain after upgrade**: Manually delete `.opencode/skills/context-router/` or `.opencode/skills/context-router-skill/` — the installer creates the new `fish-trail/` directory but doesn't remove old ones.
- **MCP server won't start**: Check that `uv` is installed and the path in `opencode.json` points to `.opencode/skills/fish-trail/mcp/context-state/server.py` (not the old context-router path).
- **Topic data missing after upgrade**: The auto-migration only runs once. If `.ai-context/` was deleted before the server migrated it, data is lost. Check `.petfish/fish-trail/` for your topics.
- **AGENTS.md has duplicate pack markers**: If both old (`context-router-skill`) and new (`fish-trail`) markers exist, remove the old ones manually.
- **Chinese text appears garbled (Mojibake)**: Your terminal is not using UTF-8 encoding. Fix: `export LANG=en_US.UTF-8` (Linux/macOS) or `chcp 65001` (Windows). The installers set UTF-8 automatically, but AI agent output may still be garbled if the terminal itself is misconfigured.

---

## About PEtFiSh

**GitHub**: https://github.com/kylecui/petfish.ai
**Website**: https://petfish.ai
**What's new in v1.4.x**: packs/ split into core/ + optional/, skill-publish, market-first distribution for optional packs, petfish-market registry with 9 official entries
