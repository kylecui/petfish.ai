# Platform Adapter Reference

This file is intended for GPT Knowledge upload.

## Supported platforms

| Platform | `--platform` | Skills directory | Instructions file | Auto-detect markers |
|---|---|---|---|---|
| OpenCode | `opencode` | `.opencode/skills/` | `AGENTS.md` | `.opencode/`, `opencode.json` |
| Claude Code | `claude` | `.claude/skills/` | `CLAUDE.md` | `.claude/`, `CLAUDE.md` |
| Codex | `codex` | `.agents/skills/` | `AGENTS.md` | `.codex/` |
| Cursor | `cursor` | `.cursor/skills/` | `.cursor/rules/*.mdc` | `.cursor/`, `.cursorrules` |
| GitHub Copilot | `copilot` | `.github/skills/` | `.github/copilot-instructions.md` | `.github/copilot-instructions.md` |
| Windsurf | `windsurf` | `.windsurf/skills/` | `.windsurfrules` | `.windsurf/`, `.windsurfrules` |
| Antigravity | `antigravity` | `.agents/skills/` | `AGENTS.md` + `GEMINI.md` | `.agents/`, `GEMINI.md` |
| Universal | `universal` | `.agents/skills/` | `AGENTS.md` | fallback |
| ChatGPT Project | `online` | N/A (online) | GPT Instructions | ChatGPT Project page |

## Online vs local

ChatGPT Project (`platform: online`) is an online PEtFiSh runtime, not a local platform adapter. It does not have a local filesystem, IDE, or CLI. Packs are semantic references applied through GPT Instructions and Knowledge. No installation command is needed.

## GPT shell behavior

When the user names a platform:

1. render platform-specific install commands;
2. identify the expected instruction file;
3. state where skills will be installed;
4. state how to verify installation.

When the user does not name a platform:

- use `--detect` when generating local commands;
- avoid pretending to know the local project markers.

## Multi-runtime remote control

Future remote-control adapters should treat local runtime as explicit metadata:

```json
{
  "host": "windows",
  "runtime": "wsl",
  "agent": "opencode",
  "project_alias": "petfish.ai"
}
```

Supported runtime classes should include:

- host native;
- WSL;
- Hyper-V guest;
- VMware guest;
- remote SSH host.

Remote adapters must not infer a filesystem path unless the local daemon confirms it.
