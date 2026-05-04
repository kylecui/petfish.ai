# Context Router — 话题治理器

本pack为项目提供上下文治理能力，降低跨话题污染风险。

## Always-On行为（每次交互自动执行）

### 交互前检查

每次收到用户消息时，调用MCP tool `topic_detect`判断当前消息与活跃topic的关系。若有可用的session_id（如OpenCode session ID），应在调用时传入`session_id`参数以启用会话追踪。根据返回的风险等级执行对应行为：

| 风险等级 | 行为 |
|---------|------|
| low (0-30) | 静默继续，不做任何提示 |
| medium (31-60) | 在回复开头用一行简要说明上下文继承范围，例如："当前继续topic「X」，继承上下文包含Y和Z。" |
| high (61-100) | 主动向用户说明话题变更风险，建议处理策略（fork/switch/reset），加载context-router skill执行深度治理 |

### 交互后更新

当本次交互产生实质性成果（代码变更、文档输出、决策结论等）时，调用`topic_update`更新当前topic的summary和status。

### 会话管理

context-router支持会话级追踪。会话（session）绑定外部平台的session ID或自动推断创建。

- **会话绑定**：在会话开始时调用`session_bind`绑定外部session_id和当前topic
- **事件追踪**：`topic_detect`传入`session_id`时，自动记录话题切换事件到session timeline
- **会话查询**：通过`session_list`按topic、时间、状态过滤，回答"昨天我们做了什么？"
- **会话恢复**：通过`session_resume`查找与特定topic关联的最近session，支持跨会话上下文继承

会话数据存储在`.ai-context/sessions/`，与topic数据独立管理。

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

context-router自动管理会话边界：

- `topic_detect`检测到archive或reset信号时，自动关闭关联session
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
- 在回复中附带一行提示："⚠ context-router MCP未连接，话题治理未激活。"
- 跳过所有topic_detect和topic_update调用
- 每次会话最多提示一次，避免重复干扰

## 深度治理触发条件

以下情况自动加载`.opencode/skills/context-router/SKILL.md`执行完整5步工作流：

- topic_detect返回风险等级high
- 用户主动要求话题管理（"整理一下话题"、"切换到X"、"把这两个话题合并"等）
- 用户使用context-router相关关键词（topic、话题、上下文、污染、继承、隔离等）
