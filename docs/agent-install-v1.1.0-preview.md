# PEtFiSh v1.1.0 Preview — Fish Trail Tiered Memory v2

> **⚠️ PRE-RELEASE — 测试版本，不影响稳定版安装。**
>
> 此版本从 `feat/fish-trail-tiered-memory-v2` 分支发布，尚未合并到 master。
> 仅供测试和预览 Tiered Memory v2 功能。稳定版安装指南见 [agent-install.md](agent-install.md)。

---

## 适用场景

- 已安装 PEtFiSh (`context` pack)，想试用 Tiered Memory v2
- 开发/测试 fish-trail 新功能
- 在非生产环境验证 v2 的行为

**如果只是想用稳定版，请使用 [agent-install.md](agent-install.md)。**

---

## Step 0: Greet the user

Say:

```
><(((^> 胖鱼 PEtFiSh v1.1.0 Preview — Tiered Memory v2

这是测试版本，包含新的分层记忆功能。安装后会替换当前的 context (fish-trail) pack。
```

---

## Step 1: 安装 / 升级

### 新安装

**PowerShell:**
```powershell
& ([scriptblock]::Create((irm https://raw.githubusercontent.com/kylecui/petfish.ai/v1.1.0/remote-install.ps1))) -Pack context -Platform opencode -Detect
```

**Bash:**
```bash
curl -fsSL https://raw.githubusercontent.com/kylecui/petfish.ai/v1.1.0/remote-install.sh | bash -s -- --pack context --platform opencode --detect
```

### 升级已有安装

**PowerShell:**
```powershell
& ([scriptblock]::Create((irm https://raw.githubusercontent.com/kylecui/petfish.ai/v1.1.0/remote-install.ps1))) -Pack context -Platform opencode -Force
```

**Bash:**
```bash
curl -fsSL https://raw.githubusercontent.com/kylecui/petfish.ai/v1.1.0/remote-install.sh | bash -s -- --pack context --platform opencode --force
```

> `--force` 会覆盖当前的 context pack。不需要先卸载。

---

## Step 2: 验证安装

重启 AI 编码工具后，运行：

```
/petfish
```

确认 `fish-trail` pack 版本显示为 `1.1.0`。

验证 MCP server 启动：

```
/petfish catalog
```

应看到 context-state MCP 工具列表包含新增的 `get_memory_context` 工具。

---

## v1.1.0 新功能

| 组件 | 功能 |
|------|------|
| **TopicRegistryV2** | 4态生命周期 (active/warm/cold/archived) + 压实感知状态转换 |
| **MemoryPressureMonitor** | Token预算感知分层保留引擎 + 预算分配器 (NORMAL/L1/L2/L3) |
| **MemoryContextProvider** | `get_memory_context()` MCP 工具 — 分层上下文输出 + 缓存 |
| **FeatureFlags** | 组件级开关 (`FISH_TRAIL_*` env) + config.json + kill-switch |
| **Migration V1→V2** | 自动检测 + 备份 + 幂等迁移 |

340 tests，全部通过。

---

## 回退到稳定版

如果遇到问题，回退到 master 稳定版：

**PowerShell:**
```powershell
& ([scriptblock]::Create((irm https://raw.githubusercontent.com/kylecui/petfish.ai/master/remote-install.ps1))) -Pack context -Platform opencode -Force
```

**Bash:**
```bash
curl -fsSL https://raw.githubusercontent.com/kylecui/petfish.ai/master/remote-install.sh | bash -s -- --pack context --platform opencode --force
```

---

## 已知限制

- V2 registry 与 V1 数据独立存储，不影响已有话题数据
- 首次启动时自动执行 V1→V2 迁移（创建备份）
- `get_memory_context` 需要 feature flag 启用：在项目 `.petfish/fish-trail/config.json` 中设置 `"v2_enabled": true`

---

## Troubleshooting

- **MCP server 不启动**：确认 `uv` 已安装，`.opencode/skills/fish-trail/mcp/context-state/` 路径正确
- **`get_memory_context` 返回错误**：检查 `config.json` 中 `feature_flags.v2_enabled` 是否为 `true`
- **话题数据为空**：V1→V2 迁移仅执行一次，确认 `.petfish/fish-trail/` 中有 `topic-registry.json`
- **想彻底清理 v2 数据**：删除 `.petfish/fish-trail/topic-registry.json`，server 会重建空注册表

---

## 反馈

遇到问题请在 GitHub 提交 issue：
https://github.com/kylecui/petfish.ai/issues

---

## About PEtFiSh

**GitHub**: https://github.com/kylecui/petfish.ai
**Website**: https://petfish.ai
