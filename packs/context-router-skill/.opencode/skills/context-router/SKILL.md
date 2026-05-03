# Context Router — 话题治理器

## 触发条件

以下情况自动加载本skill：

- `topic_detect`返回风险等级**high**（分数61-100）
- 用户主动要求话题管理（关键词：整理话题、切换话题、合并话题、归档、清空上下文等）
- 用户提及context-router相关概念（topic、话题治理、上下文污染、继承策略等）

## 前置条件

- context-state MCP server已启动（通过opencode.json配置的stdio transport）
- `.ai-context/`目录已存在（首次使用时由`topic_create`自动创建）

## 核心概念

### Topic

话题单元。每个topic有独立的scope、summary、status和Context Package。详见`references/topic-model.md`。

### 关系类型（7种）

| 关系 | 含义 | 检测可靠性 | 自动执行 |
|------|------|-----------|---------|
| continue | 继续当前话题 | 高 | 是 |
| fork | 从当前分叉 | 高 | 是 |
| switch | 切换到已有话题 | 高 | 是 |
| reset | 清空上下文重新开始 | 高 | 是 |
| merge | 合并两个话题 | 中 | 否，需确认 |
| archive | 归档完成话题 | 中 | 否，需确认 |
| bridge | 建立桥接关系 | 低 | 否，需确认 |

### 污染风险评分

5维度评分（0-100），详见`references/contamination-scoring.md`。

| 等级 | 分段 | 行为 |
|------|------|------|
| low | 0-30 | 静默继续 |
| medium | 31-60 | 简要提示上下文范围 |
| high | 61-100 | 触发本skill完整工作流 |

### Context Package

为topic生成的Markdown上下文文件，详见`references/context-package-spec.md`。三种变体：标准包、桥接包、导出包。

## 工作流（5步）

当本skill被触发时，按以下5步执行：

### Step 1: Detect Topic Event — 识别话题变更信号

**目标**：判断用户当前消息与活跃topic的关系。

**操作**：

1. 调用MCP tool `topic_detect`，传入用户消息文本
2. 获取返回结果：`relation`（关系类型）、`confidence`（置信度）、`risk`（污染风险分数）、`suggestion`（建议动作）

**MCP调用示例**：

```
tool: topic_detect
input: {
  "text": "<用户消息文本>",
  "current_topic": "<当前活跃topic ID>"
}
output: {
  "relation": "switch",
  "confidence": 0.85,
  "risk": 45,
  "risk_level": "medium",
  "target_topic": "topic_20260502_c3d4",
  "suggestion": "切换到topic「部署配置」，加载其Context Package"
}
```

**决策规则**：

- confidence ≥ 0.7 且 relation为高可靠类型（continue/fork/switch/reset）→ 进入Step 2
- confidence < 0.7 或 relation为低可靠类型（merge/archive/bridge）→ 向用户确认关系类型后进入Step 2
- risk_level为low → 静默执行，不打断用户

### Step 2: Classify & Score — 确定关系类型 + 污染风险评分

**目标**：确认关系类型，获取详细污染评分。

**操作**：

1. 若Step 1已有高置信度结果，直接使用
2. 若需要详细评分（risk_level ≥ medium），调用`contamination_score`获取5维度明细
3. 若需要解释评分来源，调用`contamination_explain`

**MCP调用示例**：

```
tool: contamination_score
input: {
  "topic_a": "<source topic ID>",
  "topic_b": "<target topic ID>"
}
output: {
  "total": 52,
  "level": "medium",
  "dimensions": {
    "topic_distance": 12,
    "goal_conflict": 10,
    "term_overloading": 10,
    "output_format_divergence": 10,
    "history_bias": 10
  }
}
```

### Step 3: Decide Context Policy — 继承/隔离/确认策略

**目标**：根据关系类型和风险等级决定上下文处理策略。

**策略矩阵**：

| 关系 | low风险 | medium风险 | high风险 |
|------|---------|-----------|---------|
| continue | 完全继承，静默 | 完全继承，提示范围 | 完全继承，提示+确认 |
| fork | 自动fork，继承部分 | 自动fork，列出继承项 | fork前确认继承范围 |
| switch | 自动switch | switch，提示两个topic差异 | switch前确认，高亮风险维度 |
| merge | — | 确认后merge | 确认后merge，详细解释风险 |
| archive | — | 确认后archive | 确认后archive |
| reset | 自动reset | 自动reset | 自动reset（用户意图明确） |
| bridge | — | 确认后bridge | 确认后bridge，详细解释交叉范围 |

### Step 4: Build Context Package — 生成当前任务专用上下文包

**目标**：根据Step 3的策略生成或更新Context Package。

**操作**：

根据关系类型选择对应的MCP tool：

| 关系 | MCP Tool | 操作 |
|------|----------|------|
| continue | `context_build` | 更新当前topic的Context Package |
| fork | `topic_create` + `context_build` | 创建子topic，生成新Context Package（继承部分父topic上下文） |
| switch | `context_build` | 为目标topic重新生成Context Package |
| merge | `topic_create` + `context_build_bridge` | 创建合并topic，生成包含两个来源的Context Package |
| archive | `context_freeze` + `topic_archive` | 冻结Context Package，归档topic |
| reset | `topic_create` + `context_build` | 创建全新topic，生成空白Context Package |
| bridge | `topic_link` + `context_build_bridge` | 建立桥接关系，生成交叉Context Package |

**MCP调用示例（fork场景）**：

```
# 1. 创建子topic
tool: topic_create
input: {
  "title": "JWT认证API设计",
  "scope": "Express路由，JWT token生成与验证，中间件",
  "parent": "topic_20260503_a1b2"
}
output: {
  "id": "topic_20260503_e5f6",
  "status": "active"
}

# 2. 生成Context Package
tool: context_build
input: {
  "topic_id": "topic_20260503_e5f6"
}
output: {
  "path": ".ai-context/contexts/topic_20260503_e5f6.context.md",
  "size": 1234
}
```

### Step 5: Update Topic Registry — 更新本地topic状态 + 记录决策

**目标**：持久化本次路由决策，更新topic状态。

**操作**：

1. 调用`decision_log`记录本次路由决策
2. 调用`topic_update`更新相关topic的status和summary
3. 若active_topic发生变化，registry自动更新指针

**MCP调用示例**：

```
# 1. 记录决策
tool: decision_log
input: {
  "relation": "fork",
  "source_topic": "topic_20260503_a1b2",
  "target_topic": "topic_20260503_e5f6",
  "risk_score": 45,
  "risk_level": "medium",
  "action": "created child topic, inherited partial context",
  "user_confirmed": false
}

# 2. 更新topic
tool: topic_update
input: {
  "topic_id": "topic_20260503_e5f6",
  "summary": "从父topic分叉，关注JWT认证API设计"
}
```

## MCP Tools速查

### Topic lifecycle

| Tool | 参数 | 返回 |
|------|------|------|
| `topic_create` | title, scope, parent? | topic对象 |
| `topic_list` | status? | topic列表 |
| `topic_show` | topic_id | topic详情 + 关联topics |
| `topic_update` | topic_id, fields... | 更新后的topic |
| `topic_archive` | topic_id | 归档确认 |
| `topic_search` | query | 匹配topic列表 |
| `topic_link` | source, target, relation | link对象 |
| `topic_unlink` | source, target | 删除确认 |
| `topic_graph` | — | nodes + edges |

### Detection

| Tool | 参数 | 返回 |
|------|------|------|
| `topic_detect` | text, current_topic | relation, confidence, risk, suggestion |

### Context operations

| Tool | 参数 | 返回 |
|------|------|------|
| `context_build` | topic_id | Context Package路径 + 大小 |
| `context_build_bridge` | topic_a, topic_b | Bridge Package路径 |
| `context_export` | topic_id, reason? | Export Package路径 |
| `context_freeze` | topic_id | Frozen Package路径 |

### Contamination

| Tool | 参数 | 返回 |
|------|------|------|
| `contamination_score` | topic_a, topic_b | total, level, dimensions |
| `contamination_explain` | topic_a, topic_b | 各维度评分理由 |

### Decision tracking

| Tool | 参数 | 返回 |
|------|------|------|
| `decision_log` | relation, source, target, risk, action... | log entry |
| `decision_history` | topic_id?, limit? | 决策历史列表 |

## 降级与容错

### MCP不可用

当MCP server未启动或连接失败时：

- 不报错，不阻塞正常工作
- 跳过所有MCP tool调用
- 在回复中附带一行提示："⚠ context-router MCP未连接，话题治理未激活。"
- 每次会话最多提示一次

### 检测结果异常

当`topic_detect`返回异常或超时：

- 默认假设relation=continue，risk=0
- 记录异常到decision log（MCP可用时）
- 不打断用户工作流

### 存储空间不足

当`.ai-context/`目录过大：

- `context_build`在生成前检查目录大小
- 超过阈值（默认10MB）时建议用户运行`topic_archive`清理旧topic
- 不自动删除任何文件

## 参考文档

- `references/topic-model.md` — Topic数据模型与关系类型
- `references/contamination-scoring.md` — 污染风险评分算法
- `references/context-package-spec.md` — Context Package格式规范
