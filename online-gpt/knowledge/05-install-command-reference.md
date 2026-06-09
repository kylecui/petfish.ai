# Install Command Reference

This file is intended for GPT Knowledge upload.

## Preferred installer

When available, prefer the unified Python installer:

```bash
uv run https://raw.githubusercontent.com/kylecui/petfish.ai/master/install.py --pack <alias> --platform <platform> --target .
```

Common flags:

| Flag | Meaning |
|---|---|
| `--pack <alias>` | pack alias or comma-separated aliases |
| `--target <path>` | target project path |
| `--platform <platform>` | explicit platform adapter |
| `--detect` | auto-detect local platform markers |
| `--force` | reinstall or overwrite existing pack files |
| `--global` | install into user-level global location |
| `--offline` | use cloned local repository only |
| `--list` | list available packs |

## Branch-aware fallback

Some older branches may still document legacy shell installers. If `install.py` is not available on the target branch or release, use the branch-documented shell command and explicitly state the fallback.

Windows PowerShell legacy style:

```powershell
& ([scriptblock]::Create((irm https://raw.githubusercontent.com/kylecui/petfish.ai/master/remote-install.ps1))) -Pack <alias> -Platform opencode
```

macOS/Linux/WSL legacy style:

```bash
curl -fsSL https://raw.githubusercontent.com/kylecui/petfish.ai/master/remote-install.sh | bash -s -- --pack <alias> --platform opencode
```

## Command rendering contract

Every install command response should include:

- working directory;
- generated command;
- expected changed files/directories;
- verification command;
- rollback note.

## Verification examples

OpenCode:

```bash
ls .opencode/skills
cat AGENTS.md
```

Codex / Antigravity / Universal:

```bash
ls .agents/skills
cat AGENTS.md
```

Claude Code:

```bash
ls .claude/skills
cat CLAUDE.md
```

## Uninstall note

Uninstall is a local state mutation. GPT should generate the command and warn about expected changes unless a verified local adapter performs it.

## Online projects (ChatGPT Project)

ChatGPT Projects do not require local installation. When `--platform online` or when the user is working in a ChatGPT Project:

- No `uv run install.py` command is needed.
- Packs are semantic references applied through GPT Instructions and Knowledge.
- The GPT should explain what each pack provides conceptually, not render an install command.
- If the user later wants local installation, render the appropriate local command with `--platform <local-platform>`.

Do not render `uv run install.py --platform online`. The `online` platform is a semantic runtime, not an install target.
