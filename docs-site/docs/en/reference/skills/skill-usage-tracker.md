# skill-usage-tracker

> Pack: **toolchain**

>

---

# Skill Usage Tracker — 使用追踪与分析

> 数据驱动的skill生态治理。知道什么被用、什么没用、什么该推荐。

## 1. 角色定位

你负责**追踪和分析**skill的使用情况，为companion的推荐决策提供数据支持。

你不做skill的创建、修改或安装——你只做**记录、统计和洞察**。

## 2. 数据模型

### 2.1 使用记录文件

每个项目维护一个使用记录文件：`.opencode/skill-usage.json`

```json
{
  "project": "/path/to/project",
  "platform": "opencode",
  "created": "2026-05-01T10:00:00Z",
  "updated": "2026-05-02T15:30:00Z",
  "skills": {
    "petfish-companion": {
      "activations": 45,
      "last_used": "2026-05-02T15:30:00Z",
      "first_used": "2026-05-01T10:00:00Z",
      "sessions": 12,
      "feedback": {"helpful": 8, "not_helpful": 1}
    },
    "skill-lint": {
      "activations": 15,
      "last_used": "2026-05-02T14:00:00Z",
      "first_used": "2026-05-01T12:00:00Z",
      "sessions": 5,
      "feedback": {"helpful": 3, "not_helpful": 0}
    }
  }
}
```

### 2.2 字段说明

| 字段 | 含义 |
|------|------|
| activations | 总激活次数 |
| last_used | 最近一次使用时间 |
| first_used | 首次使用时间 |
| sessions | 使用过该skill的独立会话数 |
| feedback.helpful | 用户标记有帮助的次数 |
| feedback.not_helpful | 用户标记无帮助的次数 |

## 3. 核心功能

### 3.1 记录使用

当companion感知到某个skill被激活时，调用tracker记录：

```bash
uv run .opencode/skills/skill-usage-tracker/scripts/track_usage.py \
  --skill <skill-name> --action activate --target .
```

### 3.2 记录反馈

当用户对skill输出给出反馈时：

```bash
uv run .opencode/skills/skill-usage-tracker/scripts/track_usage.py \
  --skill <skill-name> --action feedback --feedback helpful --target .
```

### 3.3 查看统计

```bash
uv run .opencode/skills/skill-usage-tracker/scripts/track_usage.py \
  --action report --target .
```

### 3.4 使用报告

*... (58 more lines in full SKILL.md)*
