# Tracking Guide — Implementation Details / 追踪指南——实现细节

Data storage schema, metric formulas, retention policies, and integration patterns for skill usage tracking.

技能使用追踪的数据存储架构、指标计算公式、数据保留策略及集成模式。

---

## 1. JSON Schema Specification / JSON架构规范

### 1.1 根对象结构（当前实现）

> **Status: Current** — This is the actual schema written by track_usage.py v0.4.

```json
{
  "project": "/absolute/path/to/project",
  "platform": "opencode|claude|cursor|codex|copilot|windsurf|antigravity",
  "created": "2026-05-01T10:00:00",
  "updated": "2026-05-02T15:30:00",
  "skills": { /* 见1.2 */ }
}
```

**约束条件：**
- `project`：记录项目根目录绝对路径
- `platform`：来自 `--target` 目录下的平台检测结果
- `created`, `updated`：ISO 8601格式，本地时间（无时区后缀）
- 无 `tracker_version`、无 `schema_updated_at`、无 `metadata` 汇总块

### 1.2 Skill 对象结构（当前实现）

> **Status: Current** — This is the actual per-skill schema written by track_usage.py v0.4.

```json
{
  "skills": {
    "petfish-companion": {
      "activations": 45,
      "last_used": "2026-05-02T15:30:00",
      "first_used": "2026-05-01T10:00:00",
      "sessions": 8,
      "feedback": {
        "helpful": 8,
        "not_helpful": 1
      }
    }
  }
}
```

**字段说明：**

| 字段 | 类型 | 说明 |
|------|------|------|
| `activations` | int | 该skill的总激活次数 |
| `last_used` | string | 最后一次激活时间（ISO 8601，本地时间） |
| `first_used` | string | 首次激活时间（ISO 8601，本地时间） |
| `sessions` | int | 触发过该skill的会话数（每次 `--action session` +1） |
| `feedback.helpful` | int | 标记为 helpful 的反馈计数 |
| `feedback.not_helpful` | int | 标记为 not_helpful 的反馈计数 |

---

### 1.3 计划架构 v2（Planned Schema v2）

> **Status: Planned** — Not yet implemented in track_usage.py v0.4. Current behavior: only the flat schema in 1.1–1.2 is written.

以下为 v2 计划扩展的根对象结构：

```json
{
  "tracker_version": "2.0",
  "platform": "opencode|claude|cursor|codex|copilot|windsurf|antigravity",
  "project_root": "/absolute/path/to/project",
  "created_at": "2026-05-01T10:00:00Z",
  "updated_at": "2026-05-02T15:30:00Z",
  "schema_updated_at": "2026-01-01T00:00:00Z",
  "metadata": {
    "total_activations": 87,
    "total_skills": 15,
    "active_skills": 12,
    "dormant_skills": 3
  },
  "skills": { /* 见计划v2 skill结构 */ }
}
```

计划 v2 skill 对象结构：

```json
{
  "skills": {
    "petfish-companion": {
      "metadata": {
        "first_seen": "2026-05-01T10:00:00Z",
        "last_used": "2026-05-02T15:30:00Z",
        "install_source": "global|project|builtin",
        "activation_context": "call_omo_agent|skill_trigger|manual_invocation"
      },
      "activation": {
        "total": 45,
        "by_session": [
          { "session_id": "ses_abc123", "count": 3, "first_at": "2026-05-01T10:05:00Z", "last_at": "2026-05-01T11:30:00Z" },
          { "session_id": "ses_def456", "count": 5, "first_at": "2026-05-02T09:15:00Z", "last_at": "2026-05-02T15:30:00Z" }
        ]
      },
      "feedback": {
        "helpful": { "count": 8, "ratings": [5, 5, 4, 5, 5, 4, 5, 5], "avg_score": 4.75 },
        "not_helpful": { "count": 1, "ratings": [2], "avg_score": 2 },
        "neutral": { "count": 2, "ratings": [3, 3], "avg_score": 3 }
      },
      "performance": {
        "avg_response_time_ms": 324,
        "max_response_time_ms": 1200,
        "min_response_time_ms": 45,
        "timeout_count": 0
      }
    }
  }
}
```

计划 v2 字段约束：

| 字段 | 类型 | 范围/枚举 | 必须 | 说明 |
|------|------|---------|------|------|
| `install_source` | string | `global\|project\|builtin` | ✓ | skill来源标记，用于追踪生命周期 |
| `activation_context` | string | `call_omo_agent\|skill_trigger\|manual_invocation` | ✓ | 激活来源，区分自动vs人工 |
| `ratings` | array<1-5> | [1, 5] | — | 用户评分，仅在feedback时记录 |
| `avg_score` | float | [1, 5] | — | 该类反馈的平均评分，自动计算 |
| `avg_response_time_ms` | int | [0, ∞) | — | 平均响应时间，性能分析用 |

---

## 2. Metric Calculation Formulas / 指标计算公式

> **Note on current implementation**: The `report` action in track_usage.py v0.4 implements basic versions of three metrics: activation share% (该skill激活数/总激活数), satisfaction% (helpful/(helpful+not_helpful)), and dormancy (7+ days since last use). The full formulas below are the planned calculation targets for v2.

### 2.1 激活相关指标

**激活率 (Activation Rate)**

```
激活率 = (该skill的月激活次数) / (所有skill的月激活次数) × 100%

用途：识别热门skill与冷门skill的分布
边界条件：
- 若总激活为0，则为 undefined（不记录）
- 若新skill（<7天），单独统计为"新skill"不纳入基准
```

**会话覆盖率 (Session Coverage)**

```
会话覆盖率 = (该skill被用过的会话数) / (项目总会话数)

用途：衡量skill的跨会话使用广度
边界条件：
- 同一会话中多次激活只计1次
- 会话开始时间由OpenCode/Claude等平台自动标记
```

**激活浓度 (Activation Density)**

```
激活浓度 = (该skill的总激活数) / (该skill的首用至末用的天数)

用途：衡量使用的集中程度（高浓度=经常用，低浓度=间歇使用）
边界条件：
- 若首用=末用（同天首次且唯一），则分母=1
- 若天数>365，标记为"长期低频"
```

### 2.2 反馈相关指标

**满意度 (Satisfaction Score)**

```
满意度 = (Σ helpful_ratings - Σ not_helpful_ratings) / (总反馈数) × 2

范围：[-2, 2]，其中：
  ≥ 1.5    ⟹ 高满意 (Very Satisfied)
  [0.5, 1.5) ⟹ 中满意 (Satisfied)
  [-0.5, 0.5) ⟹ 中立 (Neutral)
  < -0.5   ⟹ 不满 (Unsatisfied)

示例计算：
- 8个5分反馈 + 1个2分反馈 = (40 - 2) / 9 × 2 = 8.44 / 9 = 0.938 ✓ 中满意
```

**反馈覆盖率 (Feedback Coverage)**

```
反馈覆盖率 = (给过反馈的激活数) / (总激活数) × 100%

目标：≥ 20% 时反馈数据可信
警告：< 10% 时标记为"反馈不足"
```

### 2.3 健康度综合指标

**Skill健康度 (Health Score) — 100分制**

```
Health = A × 激活率权重 + B × 满意度权重 + C × 会话覆盖率权重

权重分布：
A = 激活率百分位 ÷ 100 × 40    （40分：使用量）
B = (满意度 + 2) ÷ 4 × 40       （40分：质量，转换到[0,1]）
C = 会话覆盖率 × 20              （20分：覆盖广度）

Health 分层：
≥ 80  ⟹ ★★★★★ 优秀（核心skill）
70-80 ⟹ ★★★★   良好（常用且满意）
50-70 ⟹ ★★★    中等（有用但使用不足）
30-50 ⟹ ★★     警告（需改进或推广）
< 30  ⟹ ★      风险（候选移除或重构）
```

---

## 3. Feedback Scoring Methodology / 反馈评分方法

> **Status: Planned (5-level system)** — Not yet implemented in track_usage.py v0.4. Current behavior: feedback is binary — `--feedback helpful` or `--feedback not_helpful`. No ratings, no neutral category. The 5-level system below is the planned v2 target.

### 3.1 当前实现：二元反馈

track_usage.py v0.4 仅支持：

```bash
--feedback helpful       # feedback.helpful += 1
--feedback not_helpful   # feedback.not_helpful += 1
```

满意度报告计算方式：`satisfaction = helpful / (helpful + not_helpful) × 100%`

### 3.2 计划：五级制评分体系

| 分数 | 标签 | 用户行为 | 含义 |
|------|------|--------|------|
| 5 | Very Helpful | 👍 + 评论"完全解决问题" | Skill直接解决用户需求，输出高质量 |
| 4 | Helpful | 👍 | Skill有用但有小问题（轻微改进空间） |
| 3 | Neutral | 😐 | Skill输出有用但不符合期望；或部分有用 |
| 2 | Not Helpful | 👎 | Skill激活成功但输出无关或低质 |
| 1 | Harmful | 👎 + 标记问题 | Skill导致错误决策或浪费时间 |

### 3.3 计划：加权反馈权值

为了防止极端反馈扭曲数据，采用 **时间衰减加权**：

```
反馈权值 = 基础权值 × 时间衰减因子

基础权值：
- 5分：1.0
- 4分：0.8
- 3分：0.5（中立，权值最低）
- 2分：0.2（负面但权值小于1）
- 1分：0.0（有害，完全排除）

时间衰减因子（指数衰减，7天半衰期）：
decay = 2^(-(距今天数 / 7))

示例：
- 今天的5分反馈：1.0 × 2^0 = 1.0
- 7天前的5分反馈：1.0 × 2^(-1) = 0.5
- 14天前的5分反馈：1.0 × 2^(-2) = 0.25
```

### 3.4 计划：反馈异常检测

标记可疑反馈（防止水军或误操作）：

```
异常条件：
1. 同skill在5分钟内连续反馈 ≥5次
   ⟹ 标记为"批量反馈"，分别记录但加 × 0.5 权值

2. 同session内反馈与激活次数比 > 0.8
   ⟹ 标记为"过度反馈"，该session反馈 × 0.7 权值

3. 同用户（OpenCode会话ID）给某skill反馈 > 20次
   ⟹ 该用户对该skill的后续反馈 × 0.5 权值（防止重度用户偏差）
```

---

## 4. Data Retention & Rotation Policy / 数据保留与轮换策略

> **Status: Planned** — Not yet implemented in track_usage.py v0.4. Current behavior: data persists indefinitely in `.opencode/skill-usage.json` until manual `--action reset`. No compression, no auto-cleanup, no rotation occurs.

### 4.1 计划：保留周期

| 数据类型 | 保留时长 | 触发操作 |
|---------|--------|---------|
| 实时激活事件 | 当前会话 | 会话结束时聚合到`by_session` |
| 按session聚合 | 90天 | 自动压缩到月维度 |
| 按月聚合 | 12个月 | 自动压缩到年维度 |
| 按年聚合 | 永久 | 保留用于长期趋势 |

### 4.2 计划：压缩 (Compression) 规则

**从session级压缩到月级：**

```json
/* 压缩前：90条by_session记录 */
"by_session": [
  { "session_id": "ses_abc123", "count": 3, ... },
  { "session_id": "ses_def456", "count": 5, ... },
  ...
]

/* 压缩后：12条月度统计 */
"by_month": [
  {
    "year_month": "2026-05",
    "session_count": 45,      /* 该月总会话数 */
    "activation_count": 245,   /* 该月总激活数 */
    "avg_per_session": 5.4,
    "feedback_summary": {
      "helpful": 35,
      "not_helpful": 2,
      "neutral": 8
    }
  }
]
```

### 4.3 计划：自动清理 (Auto-Cleanup)

```python
# 伪代码：在每次生成report时执行
def cleanup_old_data(usage_json, retention_days=90):
    cutoff_date = now() - timedelta(days=retention_days)
    
    # 1. 压缩old sessions
    old_sessions = [s for s in skills[name]['activation']['by_session'] 
                    if parse_iso(s['last_at']) < cutoff_date]
    if len(old_sessions) > 30:
        compress_to_monthly_view(old_sessions)
        remove_session_entries(old_sessions)
    
    # 2. 清理僵尸反馈（>1年无激活但有旧反馈）
    if skill['last_used'] < cutoff_date - 365:
        archive_feedback_to_separate_file()
        clear_recent_feedback()
    
    # 3. 重新计算metadata.dormant_skills
```

---

## 5. Integration Patterns / 集成模式

### 5.1 其他Skill如何上报数据

任何skill可通过调用tracker来上报事件。以下为当前实现支持的实际CLI用法：

```bash
# 激活上报（companion自动调用）
uv run .opencode/skills/skill-usage-tracker/scripts/track_usage.py \
  --action activate \
  --skill my-skill \
  --target /path/to/project

# 会话记录（每次新会话调用一次）
uv run .opencode/skills/skill-usage-tracker/scripts/track_usage.py \
  --action session \
  --skill my-skill \
  --target /path/to/project

# 用户反馈上报（二元：helpful 或 not_helpful）
uv run .opencode/skills/skill-usage-tracker/scripts/track_usage.py \
  --action feedback \
  --skill my-skill \
  --feedback helpful \
  --target /path/to/project

# 生成报告（文本格式）
uv run .opencode/skills/skill-usage-tracker/scripts/track_usage.py \
  --action report \
  --target /path/to/project

# 生成报告（JSON格式）
uv run .opencode/skills/skill-usage-tracker/scripts/track_usage.py \
  --action report \
  --target /path/to/project \
  --json

# 重置所有数据
uv run .opencode/skills/skill-usage-tracker/scripts/track_usage.py \
  --action reset \
  --target /path/to/project
```

**支持的 CLI 参数：** `--action`, `--skill`, `--feedback (helpful|not_helpful)`, `--target`, `--json`

> **Status: Planned** — The following args are **not** supported in v0.4: `--context`, `--metadata`, `--rating`, `--comment`, `--events-file`, `--on-change`, `--output`. The `batch-upload` action does not exist.
>
> 计划中的批量上报示例（v2）：
> ```bash
> uv run .opencode/skills/skill-usage-tracker/scripts/track_usage.py \
>   --action batch-upload \
>   --events-file /tmp/events.jsonl \
>   --target /path/to/project
> ```

### 5.2 Skill内嵌集成

> **Status: Planned** — Not yet implemented in track_usage.py v0.4. There is no Python library module. Current behavior: integration must go through the CLI subprocess pattern shown in 5.1.

计划中的 Python 库调用方式（v2）：

```python
# my_skill/scripts/my_main.py
from skill_usage_tracker.lib import UsageTracker

tracker = UsageTracker(project_root="/path/to/project")

# 在skill执行前
tracker.record_activation(
    skill_name="my-skill",
    context="skill_trigger",
    metadata={"input_tokens": 450}
)

# 在skill执行后
try:
    result = run_skill_logic()
    tracker.record_feedback(
        skill_name="my-skill",
        rating=5,
        session_id=os.getenv("OPENCODE_SESSION_ID")
    )
except Exception as e:
    tracker.record_feedback(
        skill_name="my-skill",
        rating=1,
        comment=f"Error: {str(e)}"
    )
```

### 5.3 监听模式 (Watch Mode)

> **Status: Planned** — Not yet implemented in track_usage.py v0.4. The `--action watch` and `--on-change` args do not exist. Current behavior: no passive monitoring; callers must invoke the script explicitly.

计划中的文件监听模式（v2）：

```bash
# 监听 .opencode/skill-usage.json 变更，并运行自定义处理脚本
uv run .opencode/skills/skill-usage-tracker/scripts/track_usage.py \
  --action watch \
  --target /path/to/project \
  --on-change /path/to/my_handler.py
```

---

## 6. Privacy & Data Minimization / 隐私与数据最小化

### 6.1 不可记录的数据

设计上严格禁止以下数据进入usage.json：

| 禁止项 | 原因 | 检查方式 |
|-------|------|--------|
| 用户输入/提示词 | PII风险，可能包含代码/密钥 | 脚本参数白名单，非白名单参数拦截 |
| 文件路径/文件内容 | 项目隐私 | 只记录skill名，不记录target |
| 用户身份/邮箱 | PII直接关联 | 仅用session ID（平台生成，匿名） |
| 输出内容摘要 | 可能泄露项目信息 | 禁止记录output字段 |
| 网络请求/响应体 | 外部API隐私 | 只记录响应时间，不记录payload |

### 6.2 数据最小化原则

```python
# ✓ 记录
{
  "skill_name": "petfish-companion",
  "activations": 45,
  "session_id": "ses_abc123",  # 由平台自动生成，匿名
  "response_time_ms": 324,
  "rating": 5
}

# ✗ 禁止
{
  "user_email": "john@example.com",
  "project_path": "/Users/john/secret-startup",
  "input_prompt": "explain how to exploit CVE-2024-xxxx",
  "output_summary": "The API uses basic auth without HTTPS",
  "file_modified": "src/auth.ts"
}
```

### 6.3 用户控制

```bash
# 查看当前记录的所有skill
cat .opencode/skill-usage.json | jq '.skills | keys'

# 清空整个项目的tracking数据
uv run .opencode/skills/skill-usage-tracker/scripts/track_usage.py \
  --action reset \
  --target .

# 或直接删除文件
rm .opencode/skill-usage.json
```

> **Status: Planned** — The following user-control actions are **not** supported in v0.4: `purge` (per-skill delete) and `export`. Current behavior: use `reset` to clear all data, or delete the file manually.
>
> 计划中的精细控制（v2）：
> ```bash
> # 删除特定skill的所有记录
> uv run .opencode/skills/skill-usage-tracker/scripts/track_usage.py \
>   --action purge \
>   --skill unwanted-skill \
>   --target .
>
> # 导出数据副本（用于外部分析）
> uv run .opencode/skills/skill-usage-tracker/scripts/track_usage.py \
>   --action export \
>   --target . \
>   --output /tmp/my_usage_backup.json
> ```

---

## 7. Example Tracking Records / 示例追踪记录

### 7.1 当前实现的 usage.json 示例

> **Status: Current** — This is what track_usage.py v0.4 actually writes.

```json
{
  "project": "/home/user/my-project",
  "platform": "opencode",
  "created": "2026-05-01T10:00:00",
  "updated": "2026-05-02T15:30:00",
  "skills": {
    "petfish-companion": {
      "activations": 45,
      "last_used": "2026-05-02T15:30:00",
      "first_used": "2026-05-01T10:00:00",
      "sessions": 8,
      "feedback": {
        "helpful": 8,
        "not_helpful": 1
      }
    },
    "skill-lint": {
      "activations": 15,
      "last_used": "2026-05-02T14:00:00",
      "first_used": "2026-05-01T12:00:00",
      "sessions": 2,
      "feedback": {
        "helpful": 3,
        "not_helpful": 0
      }
    },
    "marketplace-connector": {
      "activations": 2,
      "last_used": "2026-04-25T10:30:00",
      "first_used": "2026-04-20T08:00:00",
      "sessions": 1,
      "feedback": {
        "helpful": 0,
        "not_helpful": 1
      }
    }
  }
}
```

### 7.2 计划 v2 Schema 示例（Planned v2 Schema Example）

> **Status: Planned** — Not yet implemented in track_usage.py v0.4.

```json
{
  "tracker_version": "2.0",
  "platform": "opencode",
  "project_root": "/home/user/my-project",
  "created_at": "2026-05-01T10:00:00Z",
  "updated_at": "2026-05-02T15:30:00Z",
  "schema_updated_at": "2026-01-01T00:00:00Z",
  "metadata": {
    "total_activations": 87,
    "total_skills": 15,
    "active_skills": 12,
    "dormant_skills": 3,
    "period": "2026-05-01 ~ 2026-05-02"
  },
  "skills": {
    "petfish-companion": {
      "metadata": {
        "first_seen": "2026-05-01T10:00:00Z",
        "last_used": "2026-05-02T15:30:00Z",
        "install_source": "global",
        "activation_context": "call_omo_agent",
        "health_score": 92
      },
      "activation": {
        "total": 45,
        "by_session": [
          {
            "session_id": "ses_abc123",
            "count": 3,
            "first_at": "2026-05-01T10:05:00Z",
            "last_at": "2026-05-01T11:30:00Z"
          },
          {
            "session_id": "ses_def456",
            "count": 5,
            "first_at": "2026-05-02T09:15:00Z",
            "last_at": "2026-05-02T15:30:00Z"
          }
        ],
        "by_month": [
          {
            "year_month": "2026-04",
            "session_count": 25,
            "activation_count": 120,
            "avg_per_session": 4.8
          }
        ]
      },
      "feedback": {
        "helpful": {
          "count": 8,
          "ratings": [5, 5, 4, 5, 5, 4, 5, 5],
          "avg_score": 4.75,
          "weighted_avg": 4.62
        },
        "not_helpful": {
          "count": 1,
          "ratings": [2],
          "avg_score": 2,
          "weighted_avg": 1.8
        },
        "neutral": {
          "count": 2,
          "ratings": [3, 3],
          "avg_score": 3,
          "weighted_avg": 2.7
        }
      },
      "performance": {
        "avg_response_time_ms": 324,
        "max_response_time_ms": 1200,
        "min_response_time_ms": 45,
        "p95_response_time_ms": 950,
        "timeout_count": 0
      },
      "metrics": {
        "activation_rate": 51.7,
        "session_coverage": 0.64,
        "activation_density": 22.5,
        "satisfaction_score": 0.94,
        "feedback_coverage": 0.22
      }
    }
  }
}
```

### 7.3 字段注解（v2 计划字段）

| 字段 | 示例 | 注释 |
|------|------|------|
| `health_score` | 92 | 综合评分，用于UI展示排序（计划v2） |
| `weighted_avg` | 4.62 | 应用时间衰减后的加权平均，用于报告（计划v2） |
| `p95_response_time_ms` | 950 | 第95百分位响应时间，识别性能瓶颈（计划v2） |
| `activation_density` | 22.5 | 每天激活次数（avg），高值=重度依赖（计划v2） |
| `session_coverage` | 0.64 | 使用该skill的会话占比，广度指标（计划v2） |
| `feedback_coverage` | 0.22 | 反馈数/激活数，低值=反馈不足，需提醒用户（计划v2） |
| `status: DORMANT` | — | 7天+未用时自动标记（当前report已实现dormant flag） |
