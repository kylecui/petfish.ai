# Platform Support

PEtFiSh supports 8 AI coding platforms. Each platform uses a different skills directory and instructions file, but the skill content is identical.

## Supported Platforms

| Platform | `--platform` | Skills Directory | Instructions File | Auto-detect Markers |
|---|---|---|---|---|
| OpenCode | `opencode` | `.opencode/skills/` | `AGENTS.md` | `.opencode/`, `opencode.json` |
| Claude Code | `claude` | `.claude/skills/` | `CLAUDE.md` | `.claude/`, `CLAUDE.md` |
| Codex | `codex` | `.agents/skills/` | `AGENTS.md` | `.codex/` |
| Cursor | `cursor` | `.cursor/skills/` | `.cursor/rules/*.mdc` | `.cursor/`, `.cursorrules` |
| GitHub Copilot | `copilot` | `.github/skills/` | `.github/copilot-instructions.md` | `.github/copilot-instructions.md` |
| Windsurf | `windsurf` | `.windsurf/skills/` | `.windsurfrules` | `.windsurf/`, `.windsurfrules` |
| Antigravity | `antigravity` | `.agents/skills/` | `AGENTS.md` + `GEMINI.md` | `.agents/`, `GEMINI.md` |
| Universal | `universal` | `.agents/skills/` | `AGENTS.md` | Fallback |

## Auto-Detection

Use `--detect` and the installer checks for platform markers in this order:

1. Look for platform-specific directories and files (see markers above)
2. If multiple platforms are detected, the first match wins
3. If none match, fall back to `universal`

```bash
# Auto-detect
curl -fsSL ... | bash -s -- --pack companion --detect

# Explicit (overrides detection)
curl -fsSL ... | bash -s -- --pack companion --platform opencode
```

You can also run `/petfish detect` after installation to see what platform PEtFiSh detected.

## Platform Groups

The installer supports group targets to install across multiple platforms at once:

| Group | Platforms Included |
|---|---|
| `all` | All 8 platforms |
| `primary` | `opencode`, `claude`, `codex` |
| `ide` | `cursor`, `copilot`, `windsurf` |
| `cli` | `opencode`, `claude`, `codex`, `antigravity` |

```bash
# Install to all CLI-based platforms
./install.sh --pack companion --platform cli
```

## Per-Platform Details

### OpenCode

- **Skills**: `.opencode/skills/<skill-name>/SKILL.md`
- **Instructions**: `AGENTS.md` at project root — the installer merges pack content between `<!-- BEGIN pack: ... -->` and `<!-- END pack: ... -->` markers
- **Config**: `opencode.json` — MCP servers, permissions, and tool config are merged from `opencode.example.json` in each pack
- **Commands**: `.opencode/commands/` — slash commands (e.g., `/course-init`)
- **Agents**: `.opencode/agents/` — role-based agents

### Claude Code

- **Skills**: `.claude/skills/<skill-name>/SKILL.md`
- **Instructions**: `CLAUDE.md` at project root — same merge strategy as AGENTS.md
- **Hooks**: Claude Code supports hook scripts for pre/post skill loading
- **Note**: Content is condensed for Claude's smaller context window

### Codex

- **Skills**: `.agents/skills/<skill-name>/SKILL.md`
- **Instructions**: `AGENTS.md` at project root
- **Note**: Shares the `.agents/` directory with Antigravity

### Cursor

- **Skills**: `.cursor/skills/<skill-name>/SKILL.md`
- **Instructions**: `.cursor/rules/*.mdc` — each pack gets a separate `.mdc` rule file
- **Note**: Token-limited platform; instructions are condensed to fit context budget

### GitHub Copilot

- **Skills**: `.github/skills/<skill-name>/SKILL.md`
- **Instructions**: `.github/copilot-instructions.md` — single file, pack content appended
- **Note**: Token-limited platform; instructions are condensed

### Windsurf

- **Skills**: `.windsurf/skills/<skill-name>/SKILL.md`
- **Instructions**: `.windsurfrules` at project root
- **Note**: Token-limited platform; instructions are condensed

### Antigravity

- **Skills**: `.agents/skills/<skill-name>/SKILL.md`
- **Instructions**: `AGENTS.md` + `GEMINI.md` — dual instruction files
- **Note**: Shares the `.agents/` directory with Codex; `GEMINI.md` contains Gemini-specific instructions

## Global vs Project Install

| Mode | When to Use | Directory |
|---|---|---|
| **Project** (default) | Most packs — project-specific skills | `<project>/<platform-dir>/skills/` |
| **Global** (`--global`) | `init` and `companion` — shared across all projects | `~/<platform-dir>/skills/` (user home) |

The `init` and `companion` packs default to global install since they're useful across all projects. All other packs default to project-level install.

```bash
# Global install (default for init/companion)
./install.sh --pack init --global

# Project install (default for everything else)
./install.sh --pack deploy --target /path/to/project
```
