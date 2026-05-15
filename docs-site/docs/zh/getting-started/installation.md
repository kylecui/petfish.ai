# 安装

PEtFiSh安装到你的AI编码助手的技能目录中，整个过程不到两分钟。

## 前置条件

- **一个AI编码助手** — OpenCode、Claude Code、Cursor、Codex、Copilot、Windsurf或Antigravity
- **`uv`** — Python包管理器（[安装uv](https://docs.astral.sh/uv/getting-started/installation/)）— Python技能和MCP server需要
- **`python3`** — 安装器用于轻量JSON处理（仅stdlib，不需要虚拟环境）

## 快速安装

安装两个核心包 — `init`（项目初始化器）和`companion`（Companion Gateway + 10个内置技能）：

=== "macOS / Linux / WSL"

    ```bash
    curl -fsSL https://raw.githubusercontent.com/kylecui/petfish.ai/master/remote-install.sh \
      | bash -s -- --pack init,companion --detect
    ```

=== "Windows PowerShell"

    ```powershell
    & ([scriptblock]::Create((irm https://raw.githubusercontent.com/kylecui/petfish.ai/master/remote-install.ps1))) -Pack "init,companion" -Detect
    ```

`--detect`会自动检测你的AI平台。也可以用`--platform opencode`（或`claude`、`cursor`、`codex`、`copilot`、`windsurf`、`antigravity`）明确指定。

!!! note "自动版本管理"
    安装器会自动下载**最新稳定版本**，无需手动指定版本号。

## 选择Profile

安装`init`和`companion`后，在AI助手中运行`/initproject`选择一个profile。每个profile会自动安装对应的技能包：

| Profile | 自动安装的包 |
|---|---|
| `minimal` | `petfish` |
| `code` | `deploy`, `petfish`, `testdocs` |
| `course` | `course`, `petfish` |
| `ops` | `deploy`, `petfish` |
| `security` | `deploy`, `petfish`, `testdocs`, `trust` |
| `research` | `petfish`, `research` |
| `writing` | `petfish`, `ppt` |
| `comprehensive` | `course`, `deploy`, `petfish`, `ppt`, `testdocs`, `trust`, `context`, `research`, `reflect` |

也可以手动安装单个包：

=== "macOS / Linux / WSL"

    ```bash
    curl -fsSL https://raw.githubusercontent.com/kylecui/petfish.ai/master/remote-install.sh \
      | bash -s -- --pack deploy --detect
    ```

=== "Windows PowerShell"

    ```powershell
    & ([scriptblock]::Create((irm https://raw.githubusercontent.com/kylecui/petfish.ai/master/remote-install.ps1))) -Pack "deploy" -Detect
    ```

## 可用技能包

| 包 | 用途 | 技能数 |
|---|---|---|
| `init` | 项目初始化器和`/initproject`向导 | 1 |
| `companion` | Companion Gateway、`/petfish`、10个内置生命周期技能 | 10 |
| `course` | 课程大纲、内容、实验、QA/QC工作流 | 15 |
| `deploy` | 部署、CI/CD、健康检查、回滚、运维 | 7 |
| `testdocs` | 测试用例和使用文档生成 | 2 |
| `petfish` | 工程写作风格 | 1 |
| `ppt` | 演示文稿设计 | 2 |
| `calibrate` | 评审反迎合校准 | 1 |
| `context` | 话题治理和上下文隔离 | 1 |
| `trust` | 技能信任治理引擎 | 1 |
| `research` | 研究工作台 — 覆盖8个领域的50个技能 | 50 |
| `reflect` | 结构化反思与纠正行动 | 1 |

## 平台支持

PEtFiSh支持8个AI编码平台：

| 平台 | 技能目录 | 指令文件 |
|---|---|---|
| OpenCode | `.opencode/skills/` | `AGENTS.md` |
| Claude Code | `.claude/skills/` | `CLAUDE.md` |
| Codex | `.agents/skills/` | `AGENTS.md` |
| Cursor | `.cursor/skills/` | `.cursor/rules/*.mdc` |
| GitHub Copilot | `.github/skills/` | `.github/copilot-instructions.md` |
| Windsurf | `.windsurf/skills/` | `.windsurfrules` |
| Antigravity | `.agents/skills/` | `AGENTS.md` + `GEMINI.md` |
| Universal | `.agents/skills/` | `AGENTS.md` |

## 重启生效

!!! warning "安装后需要重启AI助手"
    大多数AI编码平台在会话启动时加载技能。安装完成后，**退出并重新启动**AI助手才能生效。

    | 平台 | 重启方式 |
    |---|---|
    | OpenCode | `Ctrl+C`，然后`opencode`（或`opencode -s <session_id>`恢复会话） |
    | Claude Code | `/exit`或`Ctrl+C`，然后`claude --continue` |
    | Cursor / Copilot / Windsurf | `Ctrl+Shift+P` → "Reload Window" |
    | Codex | `Ctrl+C`并重新启动（技能可能动态重载） |

## 验证安装

重启后，在AI助手中运行`/petfish`。你应该能看到已安装的包和技能数量。

## 升级

使用`--force`参数重新运行安装命令即可升级：

=== "macOS / Linux / WSL"

    ```bash
    curl -fsSL https://raw.githubusercontent.com/kylecui/petfish.ai/master/remote-install.sh \
      | bash -s -- --pack all --force
    ```

=== "Windows PowerShell"

    ```powershell
    & ([scriptblock]::Create((irm https://raw.githubusercontent.com/kylecui/petfish.ai/master/remote-install.ps1))) -Pack all -Force
    ```

或运行`/petfish upgrade`查看适合你操作系统的升级命令。

## 常见问题

??? tip "找不到curl"
    使用`wget`替代：
    ```bash
    wget -qO- https://raw.githubusercontent.com/kylecui/petfish.ai/master/remote-install.sh | bash -s -- --pack init,companion --detect
    ```

??? tip "PowerShell执行策略阻止脚本运行"
    ```powershell
    Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
    ```

??? tip "找不到uv"
    安装uv：<https://docs.astral.sh/uv/getting-started/installation/>

??? tip "平台自动检测识别错误"
    使用`--platform <name>`明确指定：
    ```bash
    curl -fsSL ... | bash -s -- --pack init,companion --platform opencode
    ```

## 私有仓库

对于私有或企业GitHub仓库：

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
