# Crash Signatures — 四类签名与合成日志样例

> 所有样例均为**合成脱敏**数据：session ID、时间戳、provider/model 名全部为虚构（`ses_XXXX`、`fake-provider/fake-model`），不对应任何真实 incident。
> 上游 issue 引用快照日期：2026-10-10（上游结论会漂移）。

---

## 类 1 — 模型解析失败

**签名**：`ProviderModelNotFoundError: Model not found: <prov>/<model>`

**匹配正则**（与 classify_crash.py 同步）：

```regex
ProviderModelNotFoundError
Model not found:\s*\S+/\S+
```

**根因层**：provider 不在注册表 / 未认证 / 未声明自定义 provider。

### 合成样例

```text
2026-10-09T10:41:12.884Z ERROR [session ses_7f3a9c21] prompt_async failed
  ProviderModelNotFoundError: Model not found: fake-provider/fake-model
    at resolveModel (dist/provider/registry.js:412:11)
    at promptAsync (dist/session/prompt.js:88:19)
```

第二个样例（fallback 链触发，注意 stack 帧不同）：

```text
2026-10-09T10:42:55.101Z ERROR [session ses_7f3a9c21] fallback chain exhausted
  ProviderModelNotFoundError: Model not found: fake-provider/fallback-model-2
    at resolveFallback (dist/provider/fallback.js:77:15)
```

### 误报说明

- 模型名打错（真实 provider 下的不存在 model id）也命中本签名——分类仍是类 1，但修复是改 model id 而非注册 provider。
- 自定义 provider 已声明但注册表快照过旧时，签名相同；用 preflight_model_audit.py 区分"未注册"与"未认证"。

---

## 类 2 — agent 身份解析失败

**签名**：`Die(UnknownError: UnknownError)` @ `createUserMessage`

**匹配正则**：

```regex
Die\(UnknownError: UnknownError\)
UnknownError: UnknownError          # 需配合 createUserMessage 上下文，否则降级类 4
createUserMessage                   # 上下文判定：整份日志任一位置出现即可
```

**根因层**：display name ≠ registry key，prompt 注入绕过别名归一化（上游 #54256/#42507，快照 2026-10-10）。

### 合成样例

```text
2026-10-09T11:09:03.512Z ERROR [session ses_b28d4e07] prompt_async failed
  Die(UnknownError: UnknownError)
    at createUserMessage (dist/session/message.js:156:13)
    at continueSession (dist/session/loop.js:64:9)
  data: {"message": "agent 'Fake Helper' is not a registered agent key"}
```

**注意**：内层 `data.message` 才是真实原因；外层 `UnknownError: UnknownError` 只是 NamedError 类名。

### 误报说明

- 裸 `UnknownError` 且上下文是特定 provider 流（无 `createUserMessage`）时更像类 4 配额问题——必须回查 `.data.message` 区分。
- `createUserMessage` 栈帧出现但内层文本指向磁盘/SQLite 时，按类 3 处置（优先级 3 > 2）。

---

## 类 3 — 存储层故障

**签名**：`Die(SqliteError...)` / `database or disk is full` / `locked`

**匹配正则**：

```regex
SqliteError
database or disk is full
database is locked
\bdisk is full\b
```

**根因层**：磁盘打满、event 表无界膨胀（上游 #33356，快照 2026-10-10）、锁竞争。

### 合成样例

```text
2026-10-09T12:04:47.230Z ERROR [session ses_5c1f8a93] prompt_async failed
  Die(SqliteError: database or disk is full)
    at insertEvent (dist/storage/event.js:54:7)
2026-10-09T12:04:47.241Z WARN  [storage] event table write failed, retry=0
```

锁竞争变体（瞬时 WAL 检查点冲突）：

```text
2026-10-09T12:05:02.998Z ERROR [session ses_5c1f8a93] prompt_async failed
  Die(SqliteError: database is locked)
    at beginTransaction (dist/storage/tx.js:31:9)
```

### 误报说明

- `locked` 单独出现可能只是瞬时锁竞争（WAL 检查点）；需结合 `SqliteError` 或 `disk is full` 确认。
- 磁盘清理后重试仍失败时，查 event 表膨胀（见 db-forensics.md 的膨胀度查询）。

---

## 类 4 — 配额/限流

**签名**：`已达到 N 小时的使用上限` / `HTTP 429` / 无上下文 `UnknownError` 伴随特定 provider 流

**匹配正则**：

```regex
已达到.*?使用上限
HTTP 429
\bstatus(?:\s*code)?\s*429\b
rate\s*limit
usage\s*limit
```

**根因层**：provider 限额。

### 合成样例

```text
2026-10-09T12:58:19.067Z ERROR [session ses_9e04b6d2] prompt_async failed
  provider=fake-provider-2 stream aborted: 已达到 5 小时的使用上限，将在 2026-10-09T18:00:00Z 重置
2026-10-09T12:58:19.071Z ERROR HTTP 429 from https://api.fake-provider-2.example/v1/chat
```

### 误报说明

- 本类置信度为**中**：`429` 也可能是瞬时限流（几秒级重试即恢复），`已达到 ... 使用上限` 才是硬配额。
- 无上下文 `UnknownError` 若伴随特定 provider 流且内层文本为空，倾向类 4；若伴随 `createUserMessage`，倾向类 2。必须回查 `.data.message`。

---

## 优先级与混合命中

多类签名同时出现时按 **3 > 2 > 1 > 4** 取最高优先级，并在输出 `note` 字段标 `mixed`。存储层优先是因为磁盘/SQLite 故障会污染其它一切信号（写不进 event 表时，模型与配额错误可能都报不出来）。

混合样例（应分类为类 3 并标 `mixed: also matched classes [1]`）：

```text
2026-10-09T12:04:47.230Z ERROR [session ses_aaaa0001] prompt_async failed
  Die(SqliteError: database is locked)
2026-10-09T12:04:48.000Z ERROR [session ses_bbbb0002] prompt_async failed
  ProviderModelNotFoundError: Model not found: fake-provider/fake-model
```

---

## classify_crash.py 输出字段对照

| 字段 | 含义 | 示例值（合成） |
|---|---|---|
| `class` | 命中类号，未命中为 null | `2` |
| `name` | 类名（中英） | `agent 身份解析失败 (agent identity resolution)` |
| `confidence` | 置信度 | `high` / `medium` / `low` |
| `inner_message` | `.data.message` 内层文本，未提取到为 null | `agent 'Fake Helper' is not a registered agent key` |
| `suggested_action` | 建议动作 | 见脚本 `SUGGESTED_ACTIONS` 常量 |
| `matches` | 命中行（截断至 200 字符，最多 10 条） | 原始日志行 |
| `note` | 混合标记，仅在多类命中时出现 | `mixed: also matched classes [1]` |
| `session_id` | 从命中行或全文中提取的 `ses_` 标识 | `ses_b28d4e07` |

## 日志截取窗口建议

| 类 | 建议窗口 | 理由 |
|---|---|---|
| 1 | crash 前后各 2 分钟 | 解析失败是即时的，上下文需求小 |
| 2 | crash 前 10 分钟 | 需要 `createUserMessage` 调用链与 continuation 触发点 |
| 3 | crash 前 30 分钟 | 磁盘/锁问题是累积的，早期 WARN 行有预警价值 |
| 4 | crash 前 1 小时 | 配额耗尽前通常有渐进式 429 与重试退避行 |

## 签名变迁风险

检测签名绑定当前发行版的日志格式。上游重命名错误类（如 `NamedError` 体系调整）、改动 stack 帧函数名或切换日志框架，都会使既有正则失配。升级 opencode 版本后，用合成样例重跑 classify_crash.py 做回归：四类样例仍应各自命中原类。失配时按 `uv run` 输出 diff 调整 `PATTERNS` 常量并递增 pack 版本。
