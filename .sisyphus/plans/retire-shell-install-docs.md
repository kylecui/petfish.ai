# Plan: Retire Shell Installers from User-Facing Docs

## Problem

AI agents read `docs/agent-install.md` and `docs/agent-upgrade.md`, then blindly execute old PS1/curl commands that fail in China networks. The new `uv run install.py` installer already exists on `master` but the docs never caught up.

**User impact**: Anyone following the AI-agent install prompt gets broken PS1 commands. This is the primary install path for new users.

## Scope

### Files to update (user-facing, high priority)

| # | File | Change |
|---|------|--------|
| 1 | `docs/agent-install.md` | Rewrite Step 3 to use `uv run install.py` |
| 2 | `docs/agent-upgrade.md` | Rewrite Step 3 to use `uv run install.py` |
| 3 | `README.md` Quick Start | Replace PS1/curl blocks with `uv run` |
| 4 | `docs/zh/README.md` Quick Start | Same as above, Chinese |
| 5 | `AGENTS.md` (root) | Update "one-line install" prompt |
| 6 | `docs/petfish-install-prompt.md` | Update install prompt text |
| 7 | `docs/zh/petfish-install-prompt.md` | Same, Chinese |

### Files to update (docs-site, medium priority)

| # | File | Change |
|---|------|--------|
| 8 | `docs-site/docs/en/getting-started/installation.md` | Replace PS1/curl with `uv run` |
| 9 | `docs-site/docs/zh/getting-started/installation.md` | Same, Chinese |
| 10 | `docs-site/docs/en/getting-started/upgrade.md` | Replace PS1/curl with `uv run` |
| 11 | `docs-site/docs/zh/getting-started/upgrade.md` | Same, Chinese |
| 12 | `docs-site/docs/en/developer/contributing.md` | Update install examples |
| 13 | `docs-site/docs/zh/developer/contributing.md` | Same, Chinese |
| 14 | `docs-site/docs/en/faq.md` | Update install references |
| 15 | `docs-site/docs/zh/faq.md` | Same, Chinese |
| 16 | `docs-site/docs/{en,zh}/guides/*/index.md` (8 files) | Update per-pack install commands |
| 17 | `docs-site/docs/{en,zh}/reference/packs/*.md` (20 files) | Update per-pack install commands |
| 18 | `docs/companion-gateway.md` | Update install reference |
| 19 | `docs/zh/companion-gateway.md` | Same, Chinese |

### Files NOT to update

- `remote-install.ps1`, `remote-install.sh`, `install.ps1`, `install.sh` — keep as-is, they still work for users who have them locally
- `online-gpt/knowledge/05-install-command-reference.md` — already correct
- `online-gpt/gateway/modules/installer.py` — already correct
- `website/*.html` — website install commands; update separately if needed
- `docs/archive/*` — frozen historical docs, do not touch
- `dev_reference/archives/*` — frozen, do not touch
- `research/*` — frozen research outputs, do not touch

## New Install Command Template

**All platforms, single command:**

```bash
uv run https://raw.githubusercontent.com/kylecui/petfish.ai/master/install.py --pack <alias> --platform <PLATFORM>
```

**Install init + companion:**

```bash
uv run https://raw.githubusercontent.com/kylecui/petfish.ai/master/install.py --pack init,companion --platform <PLATFORM>
```

**Upgrade all:**

```bash
uv run https://raw.githubusercontent.com/kylecui/petfish.ai/master/install.py --pack all --force --platform <PLATFORM>
```

**List packs:**

```bash
uv run https://raw.githubusercontent.com/kylecui/petfish.ai/master/install.py --list
```

**Auto-detect platform:**

```bash
uv run https://raw.githubusercontent.com/kylecui/petfish.ai/master/install.py --pack <alias> --detect
```

**Offline (from cloned repo):**

```bash
uv run ./install.py --pack <alias> --platform <PLATFORM> --target .
```

## agent-install.md Rewrite Strategy

The doc must guide AI agents to use `uv run install.py`. Key changes:

1. **Step 0-2**: Keep greeting, environment detection, pack selection — these are fine
2. **Step 3**: Replace ALL PS1/bash commands with single `uv run install.py` command
   - 3a: `uv run install.py --pack init,companion --platform <PLATFORM>`
   - 3b: `uv run install.py --pack <alias> --platform <PLATFORM>` for each additional pack
   - OR better: install all selected packs in one command: `uv run install.py --pack init,companion,<alias>,... --platform <PLATFORM>`
3. **Step 4**: Keep restart/verify — unchanged
4. **Step 5**: Keep trust governance — unchanged
5. **Troubleshooting**: Replace PS1-specific troubleshooting with `uv run`-specific:
   - "uv not found" → auto-installs in script via PEP 723
   - Network issues → `--offline` flag with cloned repo
   - Platform detection → use `--platform <name>` explicitly
6. **Offline section**: Simplify — clone repo, run `uv run ./install.py --offline`
7. Remove all PS1/curl/bash code blocks

## agent-upgrade.md Rewrite Strategy

1. **Steps 0-1**: Keep state assessment and environment detection
2. **Step 2**: Remove version-specific migration sections (v0.4→v0.5, v1.2→v1.3, v1.3→v1.4) — these are historical and the installer handles migration
3. **Step 3**: Replace with single `uv run install.py --pack all --force`
4. **Steps 4-7**: Keep legacy cleanup and MCP config updates — still valid
5. **Step 8**: Keep restart/verify — unchanged

## Prerequisites Change

Old: "python3 — used by installers for stdlib-only JSON parsing"
New: "uv — required. The installer auto-bootstraps via PEP 723. No manual Python needed."

## Risks

1. **`install.py` not on dev branch** — it's on master but not dev. Cherry-pick or merge master→dev first to get it locally for testing.
2. **Some users may have bookmarked old PS1 commands** — keep PS1/sh scripts in repo as-is; only update documentation.
3. **docs-site has ~30 files** — batch update carefully to avoid missing any.

## Implementation Order

1. Cherry-pick `install.py` to dev branch (from master)
2. Rewrite `docs/agent-install.md` (highest impact — the AI agent entry point)
3. Rewrite `docs/agent-upgrade.md`
4. Update `README.md` and `docs/zh/README.md` Quick Start
5. Update `AGENTS.md` one-line prompt
6. Update `docs/petfish-install-prompt.md` and Chinese version
7. Batch-update docs-site files (installation, upgrade, faq, contributing, per-pack guides)
8. Update `docs/companion-gateway.md` and Chinese version
9. Verify: read through all changed files, confirm no stale PS1/curl references remain
