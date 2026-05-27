# Topic Graph Schema Reference

本文档定义fish-trail的topic_graph.json数据结构。

## topic_graph.json

存储位置：`.petfish/fish-trail/topic_graph.json`

顶层结构：

```json
{
  "version": 1,
  "nodes": [],
  "edges": []
}
```

## Topic Node

每个node代表一个topic。

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `id` | string | 是 | 唯一标识符，格式`topic-<slug>` |
| `type` | string | 是 | 固定值`"topic"` |
| `title` | string | 是 | 人可读标题 |
| `summary` | string | 是 | 当前结论摘要 |
| `status` | enum | 是 | `active` / `paused` / `archived` / `deprecated` |
| `priority` | enum | 否 | `high` / `medium` / `low` |
| `intent` | string[] | 否 | 意图标签：design, implement, review, research等 |
| `keywords` | string[] | 是 | 关键词，用于topic匹配和路由 |
| `related_skills` | string[] | 否 | 关联的skill名称 |
| `related_artifacts` | string[] | 否 | 关联的文件路径 |
| `evidence_level` | enum | 是 | `extracted` / `inferred` / `ambiguous` / `proposed` / `deprecated` |
| `confidence` | float | 是 | 0.0-1.0 |
| `freshness` | object | 是 | 见下方 |
| `open_questions` | string[] | 否 | 未解决问题 |

### Freshness

```json
{
  "status": "fresh",
  "last_updated": "2026-05-05",
  "source_hash": "sha256:..."
}
```

status取值：`fresh`（7天内更新）、`recent`（30天内）、`stale`（超过30天）。

### 示例

```json
{
  "id": "topic-fish-trail",
  "type": "topic",
  "title": "fish-trail 话题轨迹管理器",
  "summary": "借鉴Graphify的图谱化索引思想，为胖鱼构建跨会话topic graph和上下文路由层。",
  "status": "active",
  "priority": "high",
  "intent": ["design", "implement"],
  "keywords": ["fish-trail", "topic graph", "context routing", "context firewall"],
  "related_skills": ["fish-trail"],
  "related_artifacts": [".opencode/skills/fish-trail/SKILL.md"],
  "evidence_level": "extracted",
  "confidence": 0.95,
  "freshness": {
    "status": "fresh",
    "last_updated": "2026-05-05",
    "source_hash": "sha256:abc123"
  },
  "open_questions": ["是否需要HTML可视化？"]
}
```

## Relation Edge

每个edge代表两个topic之间的关系。

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `id` | string | 是 | 唯一标识符，格式`edge-<source>-<relation>-<target>` |
| `source` | string | 是 | 源topic ID |
| `target` | string | 是 | 目标topic ID |
| `relation` | enum | 是 | 见relation types |
| `summary` | string | 否 | 关系说明 |
| `evidence_level` | enum | 是 | 同topic node |
| `confidence` | float | 是 | 0.0-1.0 |
| `evidence` | object[] | 否 | 证据列表 |
| `created_at` | string | 是 | ISO 8601日期 |
| `updated_at` | string | 是 | ISO 8601日期 |

### Relation Types

| 类型 | 含义 | Context Firewall影响 |
|------|------|---------------------|
| `refines` | A细化B | A的must_load包含B |
| `depends_on` | A依赖B | A的must_load包含B |
| `inspired_by` | A借鉴B | A的may_load包含B |
| `supersedes` | A替代B | B的must_not_load（deprecated） |
| `conflicts_with` | A与B冲突 | 互相must_not_load |
| `related_to` | 一般相关 | may_load |
| `produces` | A产出B | A的may_load包含B |
| `uses_skill` | A使用skill | 路由参考 |
| `belongs_to_project` | A属于项目 | 组织结构 |
| `should_not_mix_with` | A不应与B混入同一上下文 | 互相must_not_load |
| `evidence_for` | A是B的证据 | A的must_load包含B |

最关键的类型：`should_not_mix_with`和`supersedes`，直接驱动context firewall。

### Evidence

```json
{
  "type": "conversation",
  "quote": "我更想在我们的topic管理借鉴Graphify",
  "source_id": "conversation-2026-05-05"
}
```

type取值：`conversation`、`commit`、`file`、`issue`、`decision`。

## Evidence Levels

| 等级 | 含义 | 默认confidence |
|------|------|---------------|
| `extracted` | 来自用户原话、源文件、commit、issue | 0.90 |
| `inferred` | 基于上下文合理推断 | 0.65 |
| `ambiguous` | 可能相关但证据不足 | 0.40 |
| `proposed` | Agent建议新增 | 0.50 |
| `deprecated` | 已被新决策替代 | 0.30 |

## 校验规则

以下规则由`topic_validate.py`执行：

1. 所有topic ID唯一
2. 所有edge的source和target必须存在于nodes中
3. evidence_level必须是合法枚举值
4. confidence必须在0.0-1.0范围内
5. deprecated的edge不应出现在must_load中
6. `should_not_mix_with`和`conflicts_with`的边不应出现在must_load中
7. topic card的frontmatter topic_id必须存在于graph中
