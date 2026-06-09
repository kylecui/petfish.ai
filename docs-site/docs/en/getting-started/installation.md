# Installation

PEtFiSh installs into your AI coding assistant's skill directory. The process takes under 2 minutes.

## Prerequisites

- **An AI coding assistant** — OpenCode, Claude Code, Cursor, Codex, Copilot, Windsurf, or Antigravity
- **`uv`** — Python package manager ([install uv](https://docs.astral.sh/uv/getting-started/installation/)) — the installer auto-bootstraps via PEP 723

## Quick Install

Install the two essential packs — `init` (project initializer) and `companion` (Companion Gateway + built-in skills):

```bash
uv run https://raw.githubusercontent.com/kylecui/petfish.ai/master/install.py --pack init,companion --detect
```

The `--detect` flag auto-detects your AI platform. You can also specify it explicitly with `--platform opencode` (or `claude`, `cursor`, `codex`, `copilot`, `windsurf`, `antigravity`).

!!! note "Auto-versioning"
    The installer automatically downloads the **latest stable release**. No version pinning needed.

## Choose Your Profile

After installing `init` and `companion`, run `/initproject` in your AI assistant to pick a profile. Each profile auto-installs matching packs:

| Profile | Packs Installed |
|---|---|
| `minimal` | `petfish` |
| `code` | `deploy`, `petfish`, `testdocs` |
| `course` | `course`, `petfish` |
| `ops` | `deploy`, `petfish` |
| `security` | `deploy`, `petfish`, `testdocs`, `trust` |
| `research` | `petfish`, `research` |
| `writing` | `petfish`, `ppt` |
| `comprehensive` | `course`, `deploy`, `petfish`, `ppt`, `testdocs`, `trust`, `context`, `research`, `reflect` |

Or install packs manually:

```bash
uv run https://raw.githubusercontent.com/kylecui/petfish.ai/master/install.py --pack deploy --detect
```

## Available Packs

| Pack | Purpose | Skills |
|---|---|---|
| `init` | Project initializer and `/initproject` wizard | 1 |
| `companion` | Companion Gateway, `/petfish`, built-in lifecycle skills | 2 |
| `course` | Course outline, content, labs, QA/QC workflows | 15 |
| `deploy` | Deployment, CI/CD, health check, rollback, ops | 7 |
| `testdocs` | Test case and usage documentation generation | 2 |
| `petfish` | Engineering writing style | 1 |
| `ppt` | Slide and presentation design | 2 |
| `calibrate` | Anti-sycophancy calibration for reviews | 1 |
| `context` | Topic governance and context isolation | 1 |
| `trust` | Skill trust governance engine | 1 |
| `research` | Research workbench — 50 skills across 8 domains | 50 |
| `reflect` | Structured reflection and corrective actions | 1 |

## Platform Support

PEtFiSh supports 8 AI coding platforms:

| Platform | Skills Directory | Instructions File |
|---|---|---|
| OpenCode | `.opencode/skills/` | `AGENTS.md` |
| Claude Code | `.claude/skills/` | `CLAUDE.md` |
| Codex | `.agents/skills/` | `AGENTS.md` |
| Cursor | `.cursor/skills/` | `.cursor/rules/*.mdc` |
| GitHub Copilot | `.github/skills/` | `.github/copilot-instructions.md` |
| Windsurf | `.windsurf/skills/` | `.windsurfrules` |
| Antigravity | `.agents/skills/` | `AGENTS.md` + `GEMINI.md` |
| Universal | `.agents/skills/` | `AGENTS.md` |

## Restart Required

!!! warning "Restart your AI assistant after installing"
    Most AI coding platforms load skills at session start. After installation, **exit and re-launch** your AI assistant for skills to take effect.

    | Platform | How to restart |
    |---|---|
    | OpenCode | `Ctrl+C`, then `opencode` (or `opencode -s <session_id>` to resume) |
    | Claude Code | `/exit` or `Ctrl+C`, then `claude --continue` |
    | Cursor / Copilot / Windsurf | `Ctrl+Shift+P` → "Reload Window" |
    | Codex | `Ctrl+C` and re-launch (skills may reload dynamically) |

## Verify

After restarting, run `/petfish` in your AI assistant. You should see your installed packs and skill counts.

## Upgrade

Re-run the install command with `--force` to upgrade:

```bash
uv run https://raw.githubusercontent.com/kylecui/petfish.ai/master/install.py --pack all --force
```

Or run `/petfish upgrade` to see the upgrade command.

## Troubleshooting

??? tip "uv not found"
    Install uv: <https://docs.astral.sh/uv/getting-started/installation/>

??? tip "Platform detection picks the wrong platform"
    Use `--platform <name>` explicitly instead of `--detect`:
    ```bash
    uv run https://raw.githubusercontent.com/kylecui/petfish.ai/master/install.py --pack init,companion --platform opencode
    ```

??? tip "Network issues (China / restricted firewall)"
    The installer has built-in mirror fallback (`ghfast.top` → `ghproxy.com`) with retries. If all mirrors fail, clone the repo and install offline:
    ```bash
    git clone https://github.com/kylecui/petfish.ai.git
    uv run ./petfish.ai/install.py --pack <alias> --platform <PLATFORM> --target . --offline
    ```

## Private Repositories

For private or enterprise GitHub repos:

```bash
GITHUB_TOKEN=xxx uv run https://raw.githubusercontent.com/kylecui/petfish.ai/master/install.py --pack init,companion
```
