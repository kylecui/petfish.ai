# Fish Trail — 话题治理器

本pack为项目提供上下文治理能力，降低跨话题污染风险。

## Skill路由（强制）

### 必须遵守的路由规则

1. 涉及话题管理、上下文治理、污染检测、话题切换类任务时，**必须**路由到 `fish-trail` skill
2. 用户说"整理话题"、"切换到X"、"合并话题"、"topic管理"时，**必须**加载fish-trail执行深度治理
3. 当system prompt中注入的topic context显示high-risk话题切换时，**必须**暂停正常处理，向用户说明风险并建议fork/switch/reset
4. 对merge、archive、bridge三种关系类型，检测置信度低时**必须**提示用户确认，**不得**自动执行

### 冲突解决

- 当话题治理与正常任务并行时，话题治理优先级更高——先处理上下文风险，再执行任务
- 当MCP不可用时，不阻塞正常工作，静默降级

## Topic Context: Plugin Injection（非MCP工具调用）

### 机制

Topic context由 `system-prompt-context-inject` 插件自动注入到system prompt的cached prefix中。**你无需也不应在每轮交互中调用 `topic_detect` 或 `get_memory_context`**——插件已处理。

### 3-Block注入结构（#164+#166+#167）

插件输出3个独立block，每个block有不同的变更频率：

| Block | 内容 | 变更频率 | 用途 |
|-------|------|---------|------|
| `## Topics` | 话题ID、标题、状态列表 | 每100轮 | 稳定注册表 |
| `## Related` | 相关话题一行摘要 + 关系 | 每20轮 | 温话题提醒 |
| `## Focus` | 当前话题 + 反射摘要 + 模式标记 | 每轮 | 活跃焦点 |

### 模式标记（Mode Indicator）

Focus block末尾的方括号标记控制MCP调用行为：

```
[disk|rMCP:off|detail:topic_show]
```

| 标记 | 含义 | 行为 |
|------|------|------|
| `disk` | 当前运行在disk模式 | 话题感知由插件注入，非MCP实时检测 |
| `rMCP:off` | 例行MCP调用已抑制 | **禁止**自动调用topic_detect、get_memory_context、topic_list等 |
| `detail:topic_show` | 冷数据按需获取工具 | 需要完整话题详情（scope、summary、tags、edges）时使用topic_show |

### #165: MCP调用条件化规则

根据模式标记决定MCP调用策略：

**禁止的例行调用（rMCP:off时）：**
- ❌ `topic_detect` — 插件已处理，每轮无需调用
- ❌ `get_memory_context` — 插件已注入，每轮无需调用
- ❌ `topic_list` — 插件已注入 `## Topics` block
- ❌ `topic_graph` — 插件已注入 `## Related` block

**允许的按需调用：**
- ✅ `topic_show` — 需要完整话题详情时（冷数据）
- ✅ `topic_create` — 用户发起新话题
- ✅ `topic_update` — 交互后更新话题摘要/状态
- ✅ `topic_link`/`topic_unlink` — 用户发起话题关系操作
- ✅ `topic_archive` — 用户发起归档
- ✅ `session_bind`/`session_list`/`session_resume` — 会话管理

**禁止 → 允许的升级条件：**
- 用户明确发起话题管理操作
- Focus block显示high-risk切换信号
- Agent需要理解另一个话题的完整上下文（使用topic_show）

### 根据注入的context采取行动

| 话题状态 | 行为 |
|---------|------|
| 当前话题继续（无切换信号） | 静默继续 |
| 检测到话题切换 | 回复开头一行说明上下文变更 |
| 检测到high-risk切换（跨领域大幅切换） | 向用户说明话题变更风险，建议fork/switch/reset |
| Focus block包含RESET | 上下文已清除，开始新话题 |

### 何时使用MCP工具

MCP工具**仅限**用户主动发起的话题管理操作和冷数据按需获取：

| 场景 | 使用MCP工具 | 原因 |
|------|-----------|------|
| 例行话题感知 | ❌ 不使用 | 插件已注入3个block |
| 例行记忆上下文 | ❌ 不使用 | 插件已注入Focus+Related |
| 查看话题列表 | ❌ 不使用 | 插件已注入Topics block |
| 需要完整话题详情 | ✅ 调用topic_show | 冷数据，按需获取 |
| 用户问"有哪些话题" | ✅ 调用topic_list | 用户触发，需返回完整列表 |
| 用户要求切换/分叉/合并话题 | ✅ 调用对应MCP工具 | 状态变更，需事务保证 |
| 用户要求创建新话题 | ✅ 调用topic_create | 状态变更 |

### One-turn延迟

插件从磁盘读取上一轮的状态。首次对话（冷启动）时无注入，第二轮起才有完整的topic context。质量评估（N=18）显示此延迟不影响使用。

### 交互后更新

当本次交互产生实质性成果（代码变更、文档输出、决策结论等）时，调用`topic_update`更新当前topic的summary和status。

### 交互后Reflective Brief

当本次交互产生实质性成果时，调用topic_update并附带reflective_brief：
- brief ≤200字符（≈40-80 tokens），必须包含：当前阶段 + 核心动作/决策
- 示例："v1.2 design complete, 2 proposals drafted"
- 示例："#169 console.log→stderr fix committed, pre-release updated"
- 不要写："继续开发中"（无信息量，会被MCP server拒绝）
- 不要写：完整长句（太浪费tokens）
- MCP server会校验brief质量（10-200字符，无低质量模式），无效brief会被拒绝并用启发式替代
- 连续3次提交无效brief会触发自动降级，后续不再接受agent brief

### 会话管理

fish-trail支持会话级追踪。会话（session）绑定外部平台的session ID或自动推断创建。

- **会话绑定**：在会话开始时调用`session_bind`绑定外部session_id和当前topic
- **事件追踪**：用户发起话题管理操作时，自动记录到session timeline
- **会话查询**：通过`session_list`按topic、时间、状态过滤，回答"昨天我们做了什么？"
- **会话恢复**：通过`session_resume`查找与特定topic关联的最近session，支持跨会话上下文继承

会话数据存储在`.petfish/fish-trail/sessions/`，与topic数据独立管理。

### 话题关系类型

检测到的关系类型决定上下文处理策略：

- **continue**：完全继承当前上下文
- **fork**：从当前topic分叉，继承部分上下文，创建子topic
- **switch**：切换到已有topic，加载该topic的Context Package
- **merge**：合并两个topic（需用户确认）
- **archive**：归档当前topic，冻结上下文
- **reset**：清空上下文，建立干净包
- **bridge**：两个topic间建立桥接，只继承交叉部分（需用户确认）

对merge、archive、bridge三种类型，检测置信度较低时必须提示用户确认，不得自动执行。

### 会话边界自动管理

fish-trail自动管理会话边界：

- 用户发起archive或reset操作时，自动关闭关联session
- `session_bind`时自动清理不活跃超过24小时的session
- 使用`session_close`显式关闭session并附带summary
- `session_resume`返回resume context（session summary + timeline digest），支持跨会话上下文继承
- 新增`session_timeline`查看session时间线摘要
- 使用`session_query`按时间范围、topic、agent查询活动（回答"昨天我们做了什么？"）
- 使用`session_agents`查看agent-topic归属关系（哪个agent处理了哪个topic）
- 使用`topic_recommend`从topic图谱推荐关联topic

### MCP不可用时的降级行为

当context-state MCP server未启动、连接失败或调用超时时：

- 不报错，不阻塞正常工作
- 插件注入的topic context仍然可用（来自磁盘缓存）
- 仅MCP工具调用不可用（用户主动的话题管理操作受影响）
- 每次会话最多提示一次"⚠ fish-trail MCP未连接"

## 深度治理触发条件

以下情况自动加载`.opencode/skills/fish-trail/SKILL.md`执行完整5步工作流：

- 插件注入的topic context显示high-risk话题切换
- 用户主动要求话题管理（"整理一下话题"、"切换到X"、"把这两个话题合并"等）
- 用户使用fish-trail相关关键词（topic、话题、上下文、污染、继承、隔离等）
