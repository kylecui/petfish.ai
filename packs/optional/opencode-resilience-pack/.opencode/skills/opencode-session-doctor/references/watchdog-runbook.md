# Watchdog Runbook — 分诊、恢复与治理操作手册

> 深度分类与 DB 取证：`opencode-crash-taxonomy`（同 pack 姊妹 skill）。上游 issue 引用快照日期 2026-10-10，上游结论会漂移。

## 0. 日志定位与 tail 命令

日志默认路径：`~/.local/share/opencode/log/opencode.log`（Linux/macOS）；Windows 下通常在 `%USERPROFILE%\.local\share\opencode\log\opencode.log`。路径随发行版与安装方式漂移——找不到时用 `opencode` CLI 或进程环境变量定位，不要臆造路径。

```text
# Linux / macOS
tail -F ~/.local/share/opencode/log/opencode.log | grep --line-buffered "prompt_async failed"

# Windows PowerShell
Get-Content "$env:USERPROFILE\.local\share\opencode\log\opencode.log" -Wait | Select-String "prompt_async failed"
```

注意日志轮转：`tail -F`（大写）能跟随轮转后的新文件句柄，`tail -f` 不能；PowerShell `-Wait` 同理依赖文件句柄语义。

## 1. 分诊表（signature → class → action → retry policy）

| 内层签名 | 类 | 动作 | 重试策略 |
|---|---|---|---|
| `Die(UnknownError: UnknownError)` @ `createUserMessage` | 2 agent 解析失败 | 提取 sessionID → session resume + 用正确注册键重发 continuation | 单 session 最多 1 次 |
| `Die(SqliteError: ...)` / `database or disk is full` / `locked` | 3 存储层 | 检查 `df`；止血升级；按 db-forensics.md 只读取证 | **禁止重试** |
| `已达到 N 小时的使用上限` / `HTTP 429` / 无上下文 `UnknownError` 伴随特定 provider 流 | 4 配额 | 记录重置时间，挂起该 provider 的任务发射 | 重置后恢复 |
| `ProviderModelNotFoundError` | 1 模型解析 | 回到 L1：跑 preflight_model_audit.py 修配置 | 修复后重跑对账 |

## 2. Resume + 重发分步流程（类 2 专用）

1. **提取 sessionID**：在 `prompt_async failed` 行或其上下文中找 `ses_` 前缀标识（形如 `ses_XXXX`，亦可用 classify_crash.py 输出的 `session_id` 字段）
2. **确认死亡判据**（必须）：crash 时间戳之后无任何新 message/part 行——查询模板见 crash-taxonomy 的 `db-forensics.md` 经验规则 4。session 仍活着则**不恢复**（可能是误报）
3. **选正确注册键**：打开 oh-my-openagent.json，在顶层 agent 键中选目标 agent 的 **registry key**（小写连字符形式），不是 display name。对照插件 `AGENT_DISPLAY_NAMES` 的映射确认键存在
4. **resume**：用平台 session resume 能力恢复会话——resume 保留既有消息，仅丢失最后一次（即 crash 时未完成的 continuation）
5. **重发 continuation**：以正确注册键重发 continuation prompt
6. **留痕**：记录 sessionID、时间戳、分类、动作、结果
7. **重试上限**：同一 session 自动恢复最多 1 次；再次失败 → 升级给用户，不再自动重试

恢复留痕建议格式（一行一条，追加到会话笔记或对话明示）：

```text
2026-10-09T11:15:00Z resume ses_XXXX class=2 key=<registered-key> result=ok retry_count=1
```

## 3. 配额挂起机制（类 4）

1. 从内层文本提取**重置时间**（如 `将在 <timestamp> 重置`）；提取不到时向用户询问
2. 记录到会话笔记或对话明示：`provider X quota suspended until <timestamp>`
3. 挂起期间：**不再向该 provider 发射任何后台/并行任务**；新任务改派其它已认证 provider 或排队
4. 到达重置时间后：先跑 L1 对账确认 provider 仍已认证，再恢复发射

挂起记录建议格式：

```text
quota-suspend provider=fake-provider-2 until=2026-10-09T18:00:00Z noted_at=2026-10-09T12:58:30Z
```

## 4. 升级模板（类 3 止血 / 类 2 二次失败）

向用户升级时按此骨架输出（替换尖括号内容）：

```text
[incident] <class> @ <timestamp> session=<ses_XXXX>
证据: <命中的原始日志行>
已做: <df 检查结果 / resume 尝试结果>
需要人工: <清磁盘 / 重启服务 / 换 provider>
回滚入口: <上一个可用配置或 checkpoint>
```

## 5. L3 配置编辑保护（启发式）

**规则**：检测到活跃 background task（loop 状态）时，若 config/plugins 被编辑 → 告警"配置重写触发 reload 窗口，活跃后台任务可能在窗口内批量崩溃；建议等任务收敛后再改配置"（上游 #54172，快照 2026-10-10，**启发式标注**）。

启发式判定信号（任一即可告警）：

- 存在运行中的 loop 任务且 oh-my-openagent.json 的 mtime 在任务启动之后
- 插件目录内容哈希在任务存活期内变化
- 上一轮 watchdog 刚报过 crash，且配置 mtime 落在 crash 前数分钟内

mtime 检查命令（只读）：

```text
# Linux / macOS
stat -c '%y' ~/.config/opencode/oh-my-openagent.json

# Windows PowerShell
(Get-Item "$env:USERPROFILE\.config\opencode\oh-my-openagent.json").LastWriteTime
```

### 匿名化案例研究（仅时间线，无真实路径/session）

某次实战中观察到级联：**10:37** 配置重写 → **11:09 / 12:04 / 12:58** 三次任务级 crash。机制假说：配置重写触发 reload 窗口，窗口内正在 continuation 的后台子任务拿到不一致的 agent/provider 视图而批量死亡。该相关性未做因果验证，故标注为启发式规则，用于告警而非阻断。

## 6. 恢复失败决策树

```text
resume + 重发
  ├─ 成功 → 留痕 retry_count=1，继续观察 watchdog
  └─ 失败（同 session 第二次 crash）
       ├─ 签名仍是类 2 → 不再自动重试，按升级模板交人工
       ├─ 签名变成类 3 → 立即止血，查磁盘与 event 膨胀
       └─ 签名变成类 4 → 走配额挂起，不改派前先做 L1 对账
```

## 7. 多 provider 改派检查清单（类 4 挂起期间）

1. 候选 provider 在注册表中存在且已认证（跑 L1 对账确认）
2. 候选 provider 的模型上下文窗口覆盖任务需求
3. 改派记录在留痕中注明：`reroute from=X to=Y reason=quota-suspend`
4. 原 provider 重置后回切前，重新跑一次 L1 对账

## 8. 事故后复盘

任何 incident 处置完成后，触发 fish-reflection L2 复盘：输出含 `trigger` / `root_cause` / `prevention_rule` / `scope` 四字段的复盘卡片；普遍性规则建议沉淀到 AGENTS.md 开发经验沉淀区。
