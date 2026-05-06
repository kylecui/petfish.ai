# Companion Gateway

胖鱼的Companion Gateway是每条消息的自动入口。不靠agent"记得"去做——直接写在项目指令文件的最高优先级位置，每轮都跑。

## 工作原理

```
用户消息
    → [Companion Gateway]
          │
          ├─ Step 1: Topic Check (topic_detect MCP)
          ├─ Step 2: Skill Sense (能力缺口检测)
          └─ Step 3: Proceed (正常处理)
```

### Step 1: 话题检测

调用MCP的 `topic_detect`，看当前消息跟活跃话题什么关系。

三个风险等级：
- **low (0-30)**：没事，静默继续。
- **medium (31-60)**：回复开头说一句上下文范围。
- **high (61-100)**：暂停，告诉你话题漂了，建议fork/switch/reset。

MCP挂了？不卡你，静默降级。

### Step 2: 能力感知

三层检测，看你是不是缺了什么能力。

**Tier 1 — 关键词匹配**：基于 `catalog_query.py` 里的TRIGGERS表做匹配。你说"部署"，它知道推荐deploy pack。三个条件同时满足才推荐：消息命中关键词 + 该pack没装 + 本session没推荐过。

**Tier 2 — 意图感知**：Tier 1没命中时，判断你是不是在要一个需要外部集成的能力——发邮件、画甘特图、接监控——而agent自己和已装的skill都做不了。触发时建议 `/petfish search <关键词>`。

**Tier 3 — 没事**：什么都没检测到，闭嘴。

推荐挂在回复末尾，不打断你。每个领域每session最多提醒一次。

### Step 3: 正常处理

Gateway跑完，进入正常工作。

### 交互后更新

这轮交互有实质成果（改了代码、输出了文档、做了决定）？调用 `topic_update` 更新话题状态。

## Debug模式

在 `.petfish/fish-trail/config.yaml` 里配置：

```yaml
companion_gateway:
  debug: true
```

- `debug: true`：每次都把Gateway决策过程打出来（开发用）。
- `debug: false`（默认）：只在medium/high风险或有推荐时才显示。

Debug输出长这样：

```
🐟 [gateway] topic: relation=continue, risk=12 (low), confidence=0.92 → silent
🐟 [gateway] skill: no gap → pass

🐟 [gateway] topic: relation=switch, risk=67 (high), confidence=0.85 → suggest fork
🐟 [gateway] skill: gap=deploy (detected "Docker部署") → recommend

🐟 [gateway] topic: relation=continue, risk=5 (low), confidence=0.95 → silent
🐟 [gateway] skill: tier2 gap detected (intent="发邮件通知", need="邮件服务集成") → suggest search
```

## 依赖

Gateway靠两个东西：

**1. context-state MCP** — 在 `opencode.json` 里配置：
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

**2. catalog_query.py TRIGGERS** — companion skill里的关键词匹配表：
```
.opencode/skills/petfish-companion/scripts/catalog_query.py
```

## 安装

装上 `companion` + `context` pack就自动生效：

```bash
curl -fsSL https://raw.githubusercontent.com/kylecui/petfish.ai/master/remote-install.sh \
  | bash -s -- --pack companion,context
```

Gateway规则通过AGENTS.md的pack merge机制注入目标项目。

## 验证

验证关键词匹配：
```bash
uv run python .opencode/skills/petfish-companion/scripts/catalog_query.py --search "Docker"
# 应返回 deploy pack
```

验证MCP连接：
```bash
uv run python .opencode/skills/fish-trail/mcp/context-state/server.py
# 应启动JSON-RPC server
```

跑测试：
```bash
uv run pytest tests/test_companion_gateway.py -v
```
