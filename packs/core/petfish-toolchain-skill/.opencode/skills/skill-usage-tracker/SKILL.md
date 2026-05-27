---
name: skill-usage-tracker
description: >
  追踪并分析skill使用：记录激活事件、会话覆盖、helpful/not_helpful反馈，
  生成usage report识别高价值与低活跃skill并给出推荐优化。Use for “usage
  stats”, “which skills are popular”, “skill analytics”, “track usage”,
  project-skill affinity analysis, and local governance insights via
  .opencode/skill-usage.json.
metadata:
  author: petfish-team
  version: 0.2.0
  short-description: Skill使用追踪 — 记录、分析、推荐
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

```
┌──────────────────────────────────────────┐
│  ><(((^>  Skill Usage Report             │
├──────────────────────────────────────────┤
│  Project: /path/to/project               │
│  Period:  2026-05-01 → 2026-05-02        │
│  Total activations: 87                   │
│                                          │
│  Top Skills:                             │
│    1. petfish-companion  45 ⬆️ (51.7%)   │
│    2. skill-lint         15   (17.2%)    │
│    3. skill-author       12   (13.8%)    │
│                                          │
│  Dormant Skills (no use in 7+ days):     │
│    ⚪ marketplace-connector              │
│    ⚪ repo-skill-miner                   │
│                                          │
│  Satisfaction:                           │
│    👍 92% helpful (11/12 rated)          │
└──────────────────────────────────────────┘
```

## 4. 洞察与推荐

### 4.1 高价值skill识别

满足以下条件的skill为高价值：
- 激活频率高（top 25%）
- 满意度高（helpful率 > 80%）
- 多项目使用

### 4.2 低活跃skill识别

满足以下条件的skill需要关注：
- 7天以上未使用
- 激活次数 < 3
- 可能原因：描述不准确、功能与其他skill重叠、不匹配项目类型

### 4.3 推荐优化

基于使用数据，tracker可以建议：
- 常用skill组合（A和B经常一起用 → 推荐打包）
- 描述优化候选（有安装但激活率低的skill）
- 新skill开发方向（用户频繁手动做某类任务但没有对应skill）

## 5. 隐私与数据

### 必须遵守：
- 使用数据仅存储在项目本地（`.opencode/skill-usage.json`）
- 不上传任何使用数据到远程服务器
- 不记录用户输入内容，只记录skill名称和激活事件
- 用户可随时删除使用数据文件

### 不得做：
- 收集或传输用户对话内容
- 将使用数据与用户身份关联
- 在未告知用户的情况下追踪使用
