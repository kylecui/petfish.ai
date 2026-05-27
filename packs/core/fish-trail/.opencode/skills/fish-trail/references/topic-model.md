# Topic Model Reference

本文档定义Fish Trail的Topic数据模型、关系类型和存储结构。

## Topic对象

每个topic是一个JSON对象，存储在`.petfish/fish-trail/topics/<topic-id>.json`。

### 字段定义

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `id` | string | 是 | 唯一标识符，格式`topic_<timestamp>_<4位随机hex>` |
| `title` | string | 是 | 话题标题，人可读，用于显示和搜索 |
| `scope` | string | 是 | 话题范围描述，用于污染评分的关键词提取 |
| `status` | enum | 是 | `active` / `paused` / `archived` |
| `parent` | string \| null | 否 | 父topic ID，fork时设置 |
| `summary` | string | 否 | 当前话题的累积摘要，每次交互后可更新 |
| `created_at` | string | 是 | ISO 8601时间戳 |
| `updated_at` | string | 是 | ISO 8601时间戳，每次更新时刷新 |
| `tags` | string[] | 否 | 自由标签，辅助搜索 |
| `metadata` | object | 否 | 扩展字段，预留 |

### 示例

```json
{
  "id": "topic_20260503_a1b2",
  "title": "Context Router MCP实现",
  "scope": "MCP server开发，stdio transport，topic CRUD，Python实现",
  "status": "active",
  "parent": null,
  "summary": "已完成topic_store.py和topic_detector.py，正在实现server.py",
  "created_at": "2026-05-03T10:30:00+08:00",
  "updated_at": "2026-05-03T14:22:00+08:00",
  "tags": ["mcp", "python", "fish-trail"],
  "metadata": {}
}
```

## Topic Registry

所有topic的索引，存储在`.petfish/fish-trail/topic-registry.json`。

```json
{
  "version": 1,
  "active_topic": "topic_20260503_a1b2",
  "topics": {
    "topic_20260503_a1b2": {
      "title": "Context Router MCP实现",
      "status": "active",
      "created_at": "2026-05-03T10:30:00+08:00",
      "updated_at": "2026-05-03T14:22:00+08:00"
    }
  },
  "links": [
    {
      "source": "topic_20260503_a1b2",
      "target": "topic_20260502_c3d4",
      "relation": "fork",
      "created_at": "2026-05-03T10:30:00+08:00"
    }
  ]
}
```

`active_topic`指向当前活跃的topic ID。每次`topic_detect`基于这个topic判断新消息的关系。

## 关系类型（7种）

### 1. continue

- **含义**：继续当前话题，语义延续
- **检测信号**：同一领域关键词、无明显话题跳转
- **上下文策略**：完全继承当前Context Package
- **检测可靠性**：高。默认关系——无明确切换信号时判为continue

### 2. fork

- **含义**：从当前话题分叉出子话题
- **检测信号**："另外"、"顺便"、子任务拆分、从主话题延伸出的局部问题
- **上下文策略**：创建子topic，parent指向当前topic，继承scope相关的部分上下文
- **检测可靠性**：高。用户表述通常含明确的分叉语义

### 3. switch

- **含义**：切换到已存在的另一个topic
- **检测信号**：引用已知topic名称或ID、"回到X"、"继续之前的Y"
- **上下文策略**：保存当前topic状态，加载目标topic的Context Package
- **检测可靠性**：高。目标topic必须已存在于registry中

### 4. merge

- **含义**：将两个topic合并为一个
- **检测信号**："把X和Y合到一起"、两个topic频繁交叉引用
- **上下文策略**：生成合并摘要，新topic继承两个来源的上下文，标记来源
- **检测可靠性**：中。语义判断较复杂，需用户确认

### 5. archive

- **含义**：归档已完成的话题
- **检测信号**："这个做完了"、"可以关了"、显式完成声明
- **上下文策略**：冻结当前Context Package为不可变快照，只保留摘要供后续引用
- **检测可靠性**：中。需要区分"暂停"和"真正完成"，建议确认

### 6. reset

- **含义**：明确清空上下文，从头开始
- **检测信号**："重新开始"、"忘掉前面的"、"清空上下文"
- **上下文策略**：建立全新的干净上下文包，不继承任何历史
- **检测可靠性**：高。用户意图通常非常明确

### 7. bridge

- **含义**：在两个topic之间建立桥接关系
- **检测信号**：两个topic共享部分概念但目标不同，需要交叉引用
- **上下文策略**：只继承两个topic的交叉部分，不合并
- **检测可靠性**：低。需要理解两个topic的语义边界，必须用户确认

## 关系图（Graph）

`topic_graph` tool返回完整的topic关系图，结构为：

```json
{
  "nodes": [
    {"id": "topic_xxx", "title": "...", "status": "active"},
    {"id": "topic_yyy", "title": "...", "status": "archived"}
  ],
  "edges": [
    {"source": "topic_xxx", "target": "topic_yyy", "relation": "fork"}
  ]
}
```

图结构用于：
- `topic_show`展示关联topic
- `contamination_score`计算话题距离维度
- `context_build_bridge`确定交叉上下文范围

## ID生成规则

Topic ID格式：`topic_<YYYYMMDD>_<4位hex>`

- 日期部分取创建日期
- hex部分取`os.urandom(2).hex()`
- 不使用UUID以保持可读性和简洁
- 碰撞概率极低（同一天65536个topic）

## 存储目录结构

```
.petfish/fish-trail/
├── topic-registry.json          # 索引 + 关系图 + active_topic指针
├── topics/
│   ├── topic_20260503_a1b2.json # 完整topic对象
│   └── topic_20260502_c3d4.json
├── contexts/
│   ├── topic_20260503_a1b2.context.md  # Context Package (Markdown)
│   └── topic_20260502_c3d4.context.md
└── decisions/
    └── decision-log.json        # 路由决策日志
```
