# DB Forensics — opencode.db 只读取证 playbook

> **⚠ 永不写 opencode.db。** 本 playbook 所有命令均为只读（SELECT / `.schema` / 只读 PRAGMA）。任何写操作（INSERT/UPDATE/DELETE/写模式 PRAGMA）必须人工确认后由人执行，agent 不得自行执行。
> 建议先复制再取证：`cp opencode.db /tmp/opencode-forensics.db`，对副本操作，避免锁竞争影响运行中的实例。

## 只读打开方式（双保险）

即使全部命令都是 SELECT，也建议用只读模式打开，杜绝意外写：

```text
# URI 只读模式
sqlite3 "file:opencode.db?mode=ro" "SELECT COUNT(*) FROM message;"

# 或进入交互模式后立即设 query_only
sqlite3 opencode.db
PRAGMA query_only = ON;
```

WAL 副产物检查（只读，列目录即可）：

```text
ls -la opencode.db-wal opencode.db-shm 2>/dev/null
```

`-wal` 文件体量异常大通常意味着检查点积压，与类 3 的锁竞争相互印证。

## Schema 定向

```text
sqlite3 opencode.db ".schema message"
sqlite3 opencode.db ".schema part"
sqlite3 opencode.db ".schema event"
```

关键结构：

- `message` 表：`id`、`session_id`、`time_created`、`data`（**JSON 列**）
- `part` 表：`id`、`message_id`、`time_created`、`data`（JSON 列）
- `event` 表：`aggregate_id`、payload——**无时间列**

辅助定向命令（全部只读）：

```text
sqlite3 opencode.db ".tables"
sqlite3 opencode.db ".indexes message"
sqlite3 opencode.db "PRAGMA page_count;"
sqlite3 opencode.db "PRAGMA page_size;"
```

`page_count × page_size` 给出文件体量上界，用于评估 event 膨胀是否已到危险水位。

## 经验规则 2：message.data 是 JSON 列

agent/model 字段不是表列，必须用 `json_extract`：

```sql
-- 查 session 内消息用到的 agent 与 model（只读）
SELECT
  m.id,
  json_extract(m.data, '$.agent')  AS agent_key,
  json_extract(m.data, '$.model')  AS model_ref,
  m.time_created
FROM message m
WHERE m.session_id = 'ses_XXXX'          -- 替换为目标 session
ORDER BY m.time_created DESC
LIMIT 50;
```

常见错误：`SELECT data.agent FROM message`——不存在该列，直接报错。

统计 agent 存量分布（找 display name 混进 registry key 的证据）：

```sql
SELECT
  json_extract(m.data, '$.agent') AS agent_key,
  COUNT(*) AS hits
FROM message m
GROUP BY agent_key
ORDER BY hits DESC
LIMIT 30;
```

## 经验规则 3：event 表无时间列（两跳推导陈旧度）

event 表的陈旧度须经 `aggregate_id → session → MAX(message.time_created)` 两跳推导：

```sql
-- event 膨胀度 + 最后活跃时间推导（只读）
SELECT
  e.aggregate_id,
  COUNT(*) AS event_count,
  (SELECT MAX(m.time_created)
   FROM message m
   WHERE m.session_id = e.aggregate_id) AS last_message_at
FROM event e
GROUP BY e.aggregate_id
ORDER BY event_count DESC
LIMIT 20;
```

`last_message_at` 距今越久、event_count 越大，越是类 3（存储层）膨胀嫌疑。

## 经验规则 4：crash session 死亡判据

**判据：crash 时间戳之后无任何新 message/part 行。**

```sql
-- 1) crash 时间点后的 message（只读）
SELECT COUNT(*) FROM message
WHERE session_id = 'ses_XXXX'
  AND time_created > '2026-10-09T12:04:47Z';   -- 替换为 crash 时间戳

-- 2) crash 时间点后的 part（只读，经 message 关联）
SELECT COUNT(*) FROM part p
JOIN message m ON m.id = p.message_id
WHERE m.session_id = 'ses_XXXX'
  AND p.time_created > '2026-10-09T12:04:47Z';
```

两个 COUNT 均为 0 → session 确认死亡，可交 `opencode-session-doctor` 走 resume + 重发流程；任一非 0 → session 仍活着，可能是 watchdog 误报。

## 经验规则 1：取内层文本

`UnknownError: UnknownError` 字面量即 NamedError 类名，真实原因在 `.data.message`。日志行内嵌 JSON 时直接提取：

```text
# classify_crash.py 已自动提取 inner_message；手工回查时：
sqlite3 opencode.db "SELECT json_extract(data, '$.message') FROM message WHERE id = 'msg_XXXX';"
```

## 补充取证查询（只读）

消息角色分布（user/assistant 比例异常可揭示 continuation 风暴）：

```sql
SELECT
  json_extract(m.data, '$.role') AS role,
  COUNT(*) AS hits
FROM message m
WHERE m.session_id = 'ses_XXXX'
GROUP BY role;
```

part 类型分布（定位 crash 发生在哪种 part 写入阶段）：

```sql
SELECT
  json_extract(p.data, '$.type') AS part_type,
  COUNT(*) AS hits
FROM part p
JOIN message m ON m.id = p.message_id
WHERE m.session_id = 'ses_XXXX'
GROUP BY part_type;
```

session 活跃时间范围（判断长任务实际跨度）：

```sql
SELECT
  MIN(m.time_created) AS first_seen,
  MAX(m.time_created) AS last_seen,
  COUNT(*) AS message_total
FROM message m
WHERE m.session_id = 'ses_XXXX';
```

## 副本取证 checklist

1. `cp opencode.db /tmp/opencode-forensics.db`（WAL 存在时连同 `-wal`、`-shm` 一起复制）
2. 对副本执行全部查询，原库保持不动
3. 取证完成后删除副本，避免陈旧数据被误读为现状
4. 报告中注明证据来自副本及复制时间点

## 取证顺序建议

1. `.tables` / `.schema` 定向 → 2) 死亡判据（规则 4）→ 3) json_extract 取 agent/model 存量（规则 2）→ 4) event 膨胀度（规则 3）→ 5) `page_count × page_size` 水位评估 → 6) 汇总证据交分类结论。
