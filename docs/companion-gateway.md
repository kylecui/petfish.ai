# Companion Gateway

胖鱼的Companion Gateway是每条用户消息的强制入口点。它确保话题管理和能力感知在每一轮对话中都在运作——不依赖AI agent"记得"去做，而是写入项目指令的最高优先级位置。

## 工作原理

```
用户消息 → [Companion Gateway] → 正常处理
                │
                ├─ Step 1: Topic Check (topic_detect MCP)
                ├─ Step 2: Skill Sense (TRIGGERS关键词匹配)
                └─ Step 3: Proceed
```

### Step 1: Topic Check

调用 `context-state` MCP的 `topic_detect` tool，判断当前消息与活跃topic的关系。

返回三个风险等级：
- **low (0-30)**：静默继续
- **medium (31-60)**：回复开头一行说明上下文继承范围
- **high (61-100)**：暂停处理，建议话题操作（fork/switch/reset）

MCP不可用时静默降级，不阻塞工作。

### Step 2: Skill Sense

采用三层检测模型，判断用户消息是否暗示能力缺口：

**Tier 1 — 白名单匹配**：对用户消息做关键词匹配（基于 `catalog_query.py` TRIGGERS），判断是否触及未安装pack的领域。三个条件同时满足才推荐：
1. 消息命中某领域关键词
2. 该pack未安装
3. 本session未推荐过该pack

**Tier 2 — 意图感知**：当Tier 1未命中时，判断用户是否在请求一个需要外部集成（邮件、天气API、图表工具、监控服务等）的能力，且agent原生能力和已安装skill都不覆盖。触发时建议 `/petfish search <关键词>`。

**Tier 3 — 无缺口**：Tier 1和2均未命中，静默通过。

推荐以附带形式出现在回复末尾，不打断正常回复。每个领域每session最多推荐1次。

### Step 3: Proceed

Gateway完成后进入正常任务处理。

### 交互后更新

当本次交互产生实质性成果时，调用 `topic_update` 更新topic状态。

## Debug模式

在 `.petfish/fish-trail/config.yaml` 中配置：

```yaml
companion_gateway:
  debug: true
```

- `debug: true`：每次都显示check过程（开发用）
- `debug: false`（默认）：仅medium/high时显示

Debug输出示例：

```
🐟 [gateway] topic: relation=continue, risk=12 (low), confidence=0.92 → silent
🐟 [gateway] skill: no gap → pass
```

## 配置

Gateway依赖两个组件：

1. **context-state MCP** — 在 `opencode.json` 中配置：
```json
{
  "mcp": {
    "context-state": {
      "type": "local",
      "command": ["uv", "run", "python", ".opencode/skills/fish-trail/mcp/context-state/server.py"]
    }
  }
}
```

2. **catalog_query.py TRIGGERS** — companion skill内置的关键词匹配表，位于：
```
.opencode/skills/petfish-companion/scripts/catalog_query.py
```

## 安装

安装 `companion` + `context` pack后自动生效：

```bash
curl -fsSL https://raw.githubusercontent.com/kylecui/petfish.ai/master/remote-install.sh | bash -s -- --pack companion,context
```

Gateway规则通过AGENTS.md pack merge机制注入到目标项目。

## 测试验证

验证TRIGGERS匹配：
```bash
uv run python .opencode/skills/petfish-companion/scripts/catalog_query.py --search "Docker"
# 应返回: deploy pack
```

验证MCP可连接：
```bash
uv run python .opencode/skills/fish-trail/mcp/context-state/server.py
# 应启动JSON-RPC server，可通过stdin发送topic_detect请求
```

运行测试套件：
```bash
uv run pytest tests/test_companion_gateway.py -v
```
