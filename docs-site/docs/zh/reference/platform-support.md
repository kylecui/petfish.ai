# 平台支持

PEtFiSh 支持 8 款 AI 编程平台。每个平台使用不同的技能目录和指令文件，但技能内容是完全一致的。

## 支持的平台

| 平台 | `--platform` | 技能目录 | 指令文件 | 自动检测标记 |
|---|---|---|---|---|
| OpenCode | `opencode` | `.opencode/skills/` | `AGENTS.md` | `.opencode/`, `opencode.json` |
| Claude Code | `claude` | `.claude/skills/` | `CLAUDE.md` | `.claude/`, `CLAUDE.md` |
| Codex | `codex` | `.agents/skills/` | `AGENTS.md` | `.codex/` |
| Cursor | `cursor` | `.cursor/skills/` | `.cursor/rules/*.mdc` | `.cursor/`, `.cursorrules` |
| GitHub Copilot | `copilot` | `.github/skills/` | `.github/copilot-instructions.md` | `.github/copilot-instructions.md` |
| Windsurf | `windsurf` | `.windsurf/skills/` | `.windsurfrules` | `.windsurf/`, `.windsurfrules` |
| Antigravity | `antigravity` | `.agents/skills/` | `AGENTS.md` + `GEMINI.md` | `.agents/`, `GEMINI.md` |
| Universal | `universal` | `.agents/skills/` | `AGENTS.md` | 回退默认 |

## 自动检测

使用 `--detect` 参数，安装器会按以下顺序检查平台专属标记：

1. 寻找特定平台的目录和文件（见上方标记说明）
2. 如果检测到多个平台，优先匹配第一个
3. 如果都没有匹配，则回退到 `universal`

```bash
# 自动检测
curl -fsSL ... | bash -s -- --pack companion --detect

# 显式指定（覆盖自动检测）
curl -fsSL ... | bash -s -- --pack companion --platform opencode
```

安装完成后，你也可以运行 `/petfish detect` 来查看 PEtFiSh 检测到了哪个平台。

## 平台组

安装器支持平台组目标，可以一次性安装到多个平台：

| 组 | 包含的平台 |
|---|---|
| `all` | 所有 8 个平台 |
| `primary` | `opencode`, `claude`, `codex` |
| `ide` | `cursor`, `copilot`, `windsurf` |
| `cli` | `opencode`, `claude`, `codex`, `antigravity` |

```bash
# 安装到所有基于 CLI 的平台
./install.sh --pack companion --platform cli
```

## 各平台详情

### OpenCode

- **技能**：`.opencode/skills/<skill-name>/SKILL.md`
- **指令**：位于项目根目录的 `AGENTS.md` — 安装器会在 `<!-- BEGIN pack: ... -->` 和 `<!-- END pack: ... -->` 标记之间合并 pack 内容
- **配置**：`opencode.json` — MCP server、权限和工具配置将从每个 pack 的 `opencode.example.json` 中合并
- **命令**：`.opencode/commands/` — 斜杠命令（如 `/course-init`）
- **代理**：`.opencode/agents/` — 基于角色的 agent

### Claude Code

- **技能**：`.claude/skills/<skill-name>/SKILL.md`
- **指令**：位于项目根目录的 `CLAUDE.md` — 合并策略与 `AGENTS.md` 相同
- **钩子**：Claude Code 支持在加载技能前后执行钩子脚本 (hook scripts)
- **注意**：为了适应 Claude 较小的上下文窗口，内容经过了精简

### Codex

- **技能**：`.agents/skills/<skill-name>/SKILL.md`
- **指令**：位于项目根目录的 `AGENTS.md`
- **注意**：与 Antigravity 共享 `.agents/` 目录

### Cursor

- **技能**：`.cursor/skills/<skill-name>/SKILL.md`
- **指令**：`.cursor/rules/*.mdc` — 每个 pack 拥有独立的 `.mdc` 规则文件
- **注意**：受 token 限制的平台；指令内容经过精简以适应上下文预算

### GitHub Copilot

- **技能**：`.github/skills/<skill-name>/SKILL.md`
- **指令**：`.github/copilot-instructions.md` — 单文件，追加 pack 内容
- **注意**：受 token 限制的平台；指令内容经过精简

### Windsurf

- **技能**：`.windsurf/skills/<skill-name>/SKILL.md`
- **指令**：位于项目根目录的 `.windsurfrules`
- **注意**：受 token 限制的平台；指令内容经过精简

### Antigravity

- **技能**：`.agents/skills/<skill-name>/SKILL.md`
- **指令**：`AGENTS.md` + `GEMINI.md` — 双指令文件
- **注意**：与 Codex 共享 `.agents/` 目录；`GEMINI.md` 包含针对 Gemini 的特定指令

## 全局 vs 项目安装

| 模式 | 何时使用 | 目录 |
|---|---|---|
| **项目** (默认) | 大多数 pack — 项目专属技能 | `<project>/<platform-dir>/skills/` |
| **全局** (`--global`) | `init` 和 `companion` — 在所有项目间共享 | `~/<platform-dir>/skills/` (用户主目录) |

`init` 和 `companion` pack 默认采用全局安装，因为它们在所有项目中都很有用。其他所有 pack 默认采用项目级安装。

```bash
# 全局安装（init/companion 的默认行为）
./install.sh --pack init --global

# 项目安装（其他所有 pack 的默认行为）
./install.sh --pack deploy --target /path/to/project
```