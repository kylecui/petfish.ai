# 升级

PEtFiSh 的升级方式是带上 `--force` 参数重新运行安装器。你的项目文件、MCP 状态以及配置都会被保留。

## 检查更新

在你的 AI 助手中运行 `/petfish upgrade`。它会查询最新的 GitHub release，如果有新版本可用，则会显示升级命令。

你也可以手动检查：

```bash
# 查看最新 release
gh release view --repo kylecui/petfish.ai --json tagName -q .tagName
```

## 升级所有 Pack

```bash
uv run https://raw.githubusercontent.com/kylecui/petfish.ai/master/install.py --pack all --force --detect
```

!!! tip "--force 的作用"
    即使 pack 看起来已经是最新版本，也会重新安装所有的 pack。如果不加 `--force`，已存在的 pack 会被跳过，只会安装缺失的 pack。

## 升级特定的 Pack

将 `all` 替换为以逗号分隔的列表：

```bash
# 仅升级 companion 和 research
uv run https://raw.githubusercontent.com/kylecui/petfish.ai/master/install.py --pack companion,research --force
```

## 升级后

!!! warning "需要重启"
    升级完成后，请**重启你的 AI 编程工具**以加载新技能。

    | 平台 | 如何重启 |
    |---|---|
    | OpenCode | `Ctrl+C` 然后重新启动。恢复会话：`opencode -s <session_id>` |
    | Claude Code | `/exit` 或 `Ctrl+C`。恢复会话：`claude --continue` |
    | Codex | `Ctrl+C` 然后重新启动 |
    | Cursor | `Ctrl+Shift+P` → "Reload Window" |
    | Copilot | `Ctrl+Shift+P` → "Reload Window" |
    | Windsurf | `Ctrl+Shift+P` → "Reload Window" |
    | Antigravity | `Ctrl+C` 然后重新启动 |

然后验证：

```
/petfish
```

这将显示更新后的 pack 版本和技能数量。

## 版本升级说明

### 从 v0.4.x 或更早版本 → v0.5+

主要变更：

- 仓库重命名 `SKILL_builder` → `petfish.ai`（安装 URL 已自动更改）
- Pack 重命名 `context-router-skill` → `fish-trail`
- 状态目录迁移 `.ai-context/` → `.petfish/fish-trail/`（自动迁移）

使用 `--force` 升级会处理所有的重命名工作。升级后，请清理旧的残留目录：

=== "macOS / Linux / WSL"

    ```bash
    rm -rf .opencode/skills/context-router/ .opencode/skills/context-router-skill/
    ```

=== "Windows PowerShell"

    ```powershell
    Remove-Item -Recurse -Force .opencode\skills\context-router\, .opencode\skills\context-router-skill\ -ErrorAction SilentlyContinue
    ```

### 从 v0.5.x → v0.6+

- 引入 Companion Gateway（三步工作流）
- 没有破坏性变更；`--force` 会获取新特性

### 从 v0.10.x → v0.11+

- Gateway 扩展为 6 步（新增模式读取、失败信号检测、反迎合检查）
- 没有破坏性变更；`--force` 会获取新的 AGENTS.md 内容

## 故障排除

| 问题 | 解决方案 |
|---|---|
| "Pack already installed" | 使用 `--force` 重新安装 |
| 遗留目录残留 | 手动删除旧的技能目录（见上方说明） |
| MCP server 无法启动 | 检查是否已安装 `uv`，并确认配置中的路径指向新的 `fish-trail/` 目录 |
| AGENTS.md 有重复的标记 | 手动移除旧的 `context-router-skill` 标记 |
| 升级后技能未加载 | 重启你的 AI 工具（见上方表格） |

另请参阅：[常见问题与故障排除](faq.md)
