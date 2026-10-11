---
name: opencode-crash-taxonomy
description: OpenCode crash 四类分类诊断（只读知识型）。用于 session crash 分析、crash log analysis：贴日志或 opencode.log 片段，跑 classify_crash.py 分类——模型解析失败（ProviderModelNotFoundError）/ agent 身份解析失败（UnknownError: UnknownError @ createUserMessage、prompt_async failed、session died）/ 存储层 SqliteError / 使用上限配额，输出置信度与建议动作。Use when 后台任务老是失败、后台子任务崩溃、session crash。深取证读 references/db-forensics.md，恢复动作交 opencode-session-doctor。
compatibility: opencode
metadata:
  version: "1.0.0"
  author: "Petfish"
---

# OpenCode Crash Taxonomy — crash 四分类诊断

## Purpose

给定 opencode.log 片段，按四类签名分类 crash，输出置信度与建议动作。只读诊断知识层：0 写操作；恢复交 `opencode-session-doctor`。

## Triggers

触发短语：session crash、crash 分析、UnknownError、prompt_async failed、模型解析失败、贴日志、后台任务老是失败、SqliteError、使用上限、crash log analysis、session died、后台子任务崩溃

## 四类分类表（唯一真值）

| 类 | 故障 | 检测签名（opencode.log） | 根因层 | 置信度 |
|---|---|---|---|---|
| 1 | 模型解析失败 | `ProviderModelNotFoundError: Model not found: <prov>/<model>` | provider 不在注册表 / 未认证 / 未声明自定义 provider | 高 |
| 2 | agent 身份解析失败 | `Die(UnknownError: UnknownError)` @ `createUserMessage` | display name ≠ registry key，prompt 注入绕过别名归一化（上游 #54256/#42507，快照 2026-10-10） | 高 |
| 3 | 存储层故障 | `Die(SqliteError...)` / `database or disk is full` / `locked` | 磁盘打满、event 表无界膨胀（上游 #33356，快照 2026-10-10）、锁竞争 | 高 |
| 4 | 配额/限流 | `已达到 N 小时的使用上限` / HTTP 429 / 无上下文 `UnknownError` 伴随特定 provider 流 | provider 限额 | 中（需结合上下文） |

## 关键经验规则（必须遵守）

1. `UnknownError: UnknownError` 的字面量即 NamedError 类名，真实原因在 `.data.message`——**禁止**凭签名直接断言，必须回查 DB/log 取内层文本
2. DB `message.data` 是 JSON 列，agent/model 字段用 JSON 提取（`json_extract`），不是表列
3. `event` 表无时间列，陈旧度经 `aggregate_id → session → MAX(message.time_created)` 两跳推导
4. crash session 死亡判据：crash 时间戳后无任何新 message/part 行

## Workflow

1. 拿到 log 片段（用户贴日志，或引导定位 opencode.log）
2. 跑分类脚本（亦支持 stdin 管道）：

```bash
uv run .opencode/skills/opencode-crash-taxonomy/scripts/classify_crash.py <logfile>
```

3. 读 JSON 输出：`class` / `confidence` / `inner_message` / `suggested_action` / `matches`；多类命中按 3>2>1>4 取最高，`note` 标 `mixed`
4. 深取证（session 死活、agent 存量、event 膨胀度）→ `references/db-forensics.md`
5. 恢复动作 → `opencode-session-doctor`（同 pack）

## 边界

- 只读：0 写操作、0 网络；opencode.db 只跑 SELECT / `.schema`
- 上游 issue 引用须标快照日期 **2026-10-10**（结论会漂移，复查见 `references/upstream-issues.md`）
- 日志样例见 `references/crash-signatures.md`（全合成脱敏，含误报说明）

## Must do

- 命中 `UnknownError` 必须回查 `.data.message` 再下结论
- 用 classify_crash.py 机械分类；多类混合保留 mixed 标记与全部命中类
- DB 取证命令从 db-forensics.md 复制只读模板

## Must not do

- 禁止凭 `UnknownError: UnknownError` 字面量直接断言根因
- 禁止对 opencode.db 执行任何写操作
- 禁止省略快照日期引用上游 issue 结论
- 禁止在本 skill 内执行恢复动作（resume/重启/重发）
