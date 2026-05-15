# Installation

PEtFiSh installs into your AI coding assistant's skill directory. The process takes under 2 minutes.

## Prerequisites

- **An AI coding assistant** — OpenCode, Claude Code, Cursor, Codex, Copilot, Windsurf, or Antigravity
- **`uv`** — Python package manager ([install uv](https://docs.astral.sh/uv/getting-started/installation/)) — required for Python-based skills and MCP servers
- **`python3`** — used by the installer for lightweight JSON processing (stdlib only, no virtual environment needed)

## Quick Install

Install the two essential packs — `init` (project initializer) and `companion` (Companion Gateway + 10 built-in skills):

=== "macOS / Linux / WSL"

    ```bash
    curl -fsSL https://raw.githubusercontent.com/kylecui/petfish.ai/master/remote-install.sh \
      | bash -s -- --pack init,companion --detect
    ```

=== "Windows PowerShell"

    ```powershell
    & ([scriptblock]::Create((irm https://raw.githubusercontent.com/kylecui/petfish.ai/master/remote-install.ps1))) -Pack "init,companion" -Detect
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

=== "macOS / Linux / WSL"

    ```bash
    curl -fsSL https://raw.githubusercontent.com/kylecui/petfish.ai/master/remote-install.sh \
      | bash -s -- --pack deploy --detect
    ```

=== "Windows PowerShell"

    ```powershell
    & ([scriptblock]::Create((irm https://raw.githubusercontent.com/kylecui/petfish.ai/master/remote-install.ps1))) -Pack "deploy" -Detect
    ```

## Available Packs

| Pack | Purpose | Skills |
|---|---|---|
| `init` | Project initializer and `/initproject` wizard | 1 |
| `companion` | Companion Gateway, `/petfish`, 10 built-in lifecycle skills | 10 |
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

=== "macOS / Linux / WSL"

    ```bash
    curl -fsSL https://raw.githubusercontent.com/kylecui/petfish.ai/master/remote-install.sh \
      | bash -s -- --pack all --force
    ```

=== "Windows PowerShell"

    ```powershell
    & ([scriptblock]::Create((irm https://raw.githubusercontent.com/kylecui/petfish.ai/master/remote-install.ps1))) -Pack all -Force
    ```

Or run `/petfish upgrade` to see the upgrade command for your OS.

## Troubleshooting

??? tip "curl not found"
    Use `wget` instead:
    ```bash
    wget -qO- https://raw.githubusercontent.com/kylecui/petfish.ai/master/remote-install.sh | bash -s -- --pack init,companion --detect
    ```

??? tip "PowerShell execution policy blocks the script"
    ```powershell
    Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
    ```

??? tip "uv not found"
    Install uv: <https://docs.astral.sh/uv/getting-started/installation/>

??? tip "Platform detection picks the wrong platform"
    Use `--platform <name>` explicitly instead of `--detect`:
    ```bash
    curl -fsSL ... | bash -s -- --pack init,companion --platform opencode
    ```

## Private Repositories

For private or enterprise GitHub repos:

=== "macOS / Linux / WSL"

    ```bash
    curl -fsSL -H "Authorization: token $GITHUB_TOKEN" \
      https://raw.githubusercontent.com/kylecui/petfish.ai/master/remote-install.sh \
      | GITHUB_TOKEN=$GITHUB_TOKEN bash -s -- --pack init,companion
    ```

=== "Windows PowerShell"

    ```powershell
    & ([scriptblock]::Create((irm https://raw.githubusercontent.com/kylecui/petfish.ai/master/remote-install.ps1))) -Pack "init,companion" -GitHubToken $env:GITHUB_TOKEN
    ```
