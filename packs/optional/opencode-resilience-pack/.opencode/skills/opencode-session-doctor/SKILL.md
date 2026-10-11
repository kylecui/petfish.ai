---
name: opencode-session-doctor
description: OpenCode 长任务三层韧性守护。用于 起并行任务前 pre-flight 发射前校验（preflight_model_audit.py 模型解析对账：provider 注册/模型存在/已认证 + agent 别名三方对账）、后台任务 watchdog（盯 prompt_async failed，按四类分诊，agent 解析类自动恢复：session resume + 重发，单 session 最多 1 次）、L3 配置变更治理。Use when session doctor、并行任务校验、模型解析失败怎么查、自动恢复、quota suspended、长任务守护。
compatibility: opencode
metadata:
  version: "1.0.0"
  author: "Petfish"
---

# OpenCode Session Doctor — pre-flight + watchdog + 受限恢复

## Purpose

长任务三层守护：L1 发射前模型对账（阻断坏引用）、L2 运行时 watchdog 与受限自动恢复、L3 治理钩子。深度分类与 DB 取证交 `opencode-crash-taxonomy`。

## Triggers

触发短语：起并行任务前、pre-flight、发射前校验、session doctor、模型解析对账、后台任务 watchdog、prompt_async failed、自动恢复、长任务、并行任务校验、session resume、quota suspended

## L1 — Pre-flight（发射前校验）

起并行/后台任务**之前**必须跑对账；`BLOCK` 即阻断发射，先修配置再复跑：

```bash
uv run .opencode/skills/opencode-session-doctor/scripts/preflight_model_audit.py
```

默认路径（随 OS/安装方式漂移，可用 `--config` / `--registry` / `--auth` 覆盖）：

| 文件 | 默认路径 |
|---|---|
| config | `~/.config/opencode/oh-my-openagent.json` |
| registry | `~/.cache/opencode/models.json` |
| auth | `~/.local/share/opencode/auth.json` |

校验内容：收集全部 `model` / `fallback_models` 引用，逐条查 (a) provider 在注册表 (b) model id 存在 (c) provider 已认证（只看 key 存在性，**永不输出密钥值**，报告只写 `authenticated: yes/no`）；外加 agent 别名三方对账（display name vs registry key，best-effort，限制见 runbook）。`--json` 输出 `{refs_total, refs_bad, agents_inconsistent, verdict}`；exit 0=PASS，1=BLOCK，2=文件缺失。

## L2 — Watchdog（运行时检测与受限自动恢复）

tail opencode.log（默认 `~/.local/share/opencode/log/opencode.log`，路径随 OS 漂移，见 runbook），匹配 `prompt_async failed` 后按四类分诊（深度取证引用 `opencode-crash-taxonomy`）：

| 类 | 处置 | 重试 |
|---|---|---|
| 2 agent 解析失败 | 提取 sessionID → session resume + 正确注册键重发 continuation | 单 session 最多 1 次 |
| 3 存储层 | 查 `df`；**不重试**；incident 式止血升级 | 禁止 |
| 4 配额 | 记重置时间，挂起该 provider 的任务发射 | 重置后恢复 |

resume+重发分步流程、配额挂起机制、升级模板见 `references/watchdog-runbook.md`。

## L3 — 治理钩子

1. 配置/插件编辑 + 活跃 loop 任务 → 告警"配置重写触发 reload 窗口"（上游 #54172，快照 2026-10-10，启发式标注，机制见 runbook 案例）
2. 事故处置后触发 fish-reflection L2 复盘，沉淀 prevention_rule

## MUST NOT（硬边界，逐字遵守）

- 不直接写 opencode.db（只读分析；写操作必须人工确认）
- 不自动重启 opencode 服务（只提示）
- L2 自动恢复仅对 agent 解析类启用，单 session 最多重试 1 次

## Must do

- L1 `BLOCK` 时先修配置再复跑，不得带坏引用发射
- 恢复前确认死亡判据：crash 时间戳后无新 message/part 行
- 每次恢复留痕：sessionID、时间、分类、动作、结果

## Must not do

- 禁止类 3 重试；禁止同 session 第 2 次自动恢复
- 禁止打印或记录 auth.json 任何密钥值
- 禁止自动重启服务或直接写 opencode.db
