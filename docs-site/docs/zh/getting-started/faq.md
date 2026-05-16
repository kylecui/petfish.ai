# 常见问题与排错

## 安装

### "Pack already installed" —— 我该如何更新？

安装器会跳过看起来已经是最新的 packs。请使用 `--force` 重新安装：

=== "macOS / Linux / WSL"

    ```bash
    curl -fsSL https://raw.githubusercontent.com/kylecui/petfish.ai/master/remote-install.sh \
      | bash -s -- --pack all --force
    ```

=== "Windows PowerShell"

    ```powershell
    & ([scriptblock]::Create((irm https://raw.githubusercontent.com/kylecui/petfish.ai/master/remote-install.ps1))) -Pack all -Force
    ```

或者在你的 AI 助手中运行 `/petfish upgrade` 以查看适用于你操作系统的确切命令。

### 安装器提示 "uv not found"

PEtFiSh 的 Python skills 和 MCP servers 依赖于 [uv](https://docs.astral.sh/uv/getting-started/installation/)。请先安装它：

=== "macOS / Linux / WSL"

    ```bash
    curl -LsSf https://astral.sh/uv/install.sh | sh
    ```

=== "Windows PowerShell"

    ```powershell
    powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
    ```

### 我的 AI 平台未能自动识别

请显式使用 `--platform` 参数：

```bash
--platform opencode   # or claude, cursor, codex, copilot, windsurf, antigravity
```

请参阅 [平台支持](../reference/platform-support.md) 了解识别标识与对应目录。

### 我可以安装到私有/企业仓库吗？

可以。请传递 GitHub token：

=== "macOS / Linux / WSL"

    ```bash
    curl -fsSL -H "Authorization: token $GITHUB_TOKEN" \
      https://raw.githubusercontent.com/kylecui/petfish.ai/master/remote-install.sh \
      | GITHUB_TOKEN=$GITHUB_TOKEN bash -s -- --pack companion
    ```

=== "Windows PowerShell"

    ```powershell
    & ([scriptblock]::Create((irm https://raw.githubusercontent.com/kylecui/petfish.ai/master/remote-install.ps1))) -Pack companion -GitHubToken $env:GITHUB_TOKEN
    ```

---

## Companion Gateway

### Companion Gateway 没有运行

Gateway 嵌入在 `AGENTS.md`（或对应平台的等效文件）的指令文件中。它会在处理每条消息时自动运行——无需启动独立的进程。请检查：

1. 已安装 `companion` pack：检查你的 skills 目录中是否有 `petfish-companion/`
2. 你的指令文件（如 `AGENTS.md`、`CLAUDE.md` 等）中包含 Gateway 相关内容

### "⚠ fish-trail MCP not connected"

这意味着 context-state MCP server 未在运行。Gateway 仍可工作——只是话题治理（topic governance）被禁用了。修复方法：

1. 确保 `context` pack 已安装
2. 检查 `opencode.json`（或等效配置）中已配置该 MCP server
3. 验证是否已安装 `uv` 且 server 路径正确

### 我该如何切换项目模式（project modes）？

在对话中直接说出关键词即可——无需编辑文件：

- **urgent**: "紧急", "urgent", "快速", "workaround"
- **balanced**: "正常", "balanced", "标准流程"
- **thorough**: "仔细", "thorough", "root cause", "彻底"
- **rigor on**: "严谨", "rigor", "plan first"
- **rigor off**: "快做", "直接做", "skip plan"

或通过编辑 `.opencode/project-mode.yaml` 以进行持久化设置。

---

## Skills & Packs

### 如何查看已安装的内容？

在你的 AI 助手中运行 `/petfish`。它会显示所有已安装的 packs 和 skills。

### Skill 无法触发

1. 检查该 skill 中 `SKILL.md` 的 description——AI 仅根据 frontmatter（前言）中的 `description` 字段进行匹配
2. 尝试使用该 skill 的触发短语中列出的关键词
3. 运行 `/petfish eval <path>` 来测试触发的准确性
4. 运行 `/petfish optimize <path>` 来优化描述信息

### 如何创建自定义 skill？

运行 `/petfish create <name>` 或直接使用 `skill-author` skill。它会自动生成一个有效的 skill 目录骨架，其中包含 `SKILL.md`、参考文档以及可选脚本。

### 如何发布一个 skill？

运行 `/petfish gate <path>` 以执行完整的质量门禁流程（lint 检查 → 安全审计 → 元数据验证 → 决策）。门禁会输出 PASS、CONDITIONAL 或 FAIL 结果。

---

## 升级

### 如何检查更新？

运行 `/petfish upgrade`——它将查询最新的 GitHub release，如果有新版本，则会显示相应的升级命令。

### `--force` 是用来做什么的？

它会强制重新安装 packs，即使它们看起来已经是最新版。在以下情况使用它：

- 有可用的新版本时
- 你想要获取被重命名的 packs 或迁移的文件时
- 似乎出现了某些故障，你希望执行一次干净的重装时

### 升级时我会丢失数据吗？

不会。安装器只对 skills 目录进行写入。你的项目文件、MCP 状态（话题、会话）以及配置都会被保留。fish-trail MCP server 会在需要时自动迁移状态目录。

---

## MCP & Fish Trail

### 提供了哪些 MCP tools？

`context` pack 通过 context-state server 提供了 31 个 MCP tools，涵盖：

- 话题管理（创建、更新、归档、搜索、链接、路由）
- 会话追踪（绑定、恢复、关闭、查询、时间线）
- 污染评分与上下文构建
- 决策日志与话题图谱验证

### 升级后我的话题数据不见了

从 `.ai-context/` 到 `.petfish/fish-trail/` 的自动迁移仅在服务器首次启动时运行一次。如果在迁移前旧目录被删除了，数据将会丢失。请检查 `.petfish/fish-trail/` 以查看你当前的话题数据。

---

## 通用问题

### 我需要什么 Python 版本？

对于包含脚本的 skills 需要 Python 3.10+。安装器本身仅使用标准库（通过 `python3 -c` 进行 JSON 解析），因此任何 Python 3 版本均可用于安装。

### PEtFiSh 可以离线使用吗？

安装完成后是可以的。Skills 均为本地文件。网络调用仅在安装/升级时（从 GitHub 下载），或当你使用了依赖网络搜索的 skills（如 marketplace-connector）时发生。

### 如何卸载某个 pack？

请使用本地安装器：

=== "macOS / Linux / WSL"

    ```bash
    ./install.sh --uninstall <alias>
    ```

=== "Windows PowerShell"

    ```powershell
    .\install.ps1 -Uninstall <alias>
    ```

!!! note
    卸载功能仅支持通过本地安装器操作，无法使用远程一行命令（one-liner）卸载。
