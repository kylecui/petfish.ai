# Companion Gateway

胖鱼的Companion Gateway是每条消息的自动入口。不靠agent"记得"去做——直接写在项目指令文件的最高优先级位置，每轮都跑。

PEtFiSh's Companion Gateway runs automatically before every user message. It doesn't rely on the AI agent "remembering" to do it — it's injected at the highest priority position in the project's instructions file, so it executes every round.

## 工作原理 / How It Works

```
用户消息 / User message
    → [Companion Gateway]
          │
          ├─ Step 1: Topic Check (topic_detect MCP)
          ├─ Step 2: Skill Sense (capability gap detection)
          └─ Step 3: Proceed (normal processing)
```

### Step 1: Topic Check / 话题检测

调用MCP的 `topic_detect`，看当前消息跟活跃话题什么关系。

Calls `topic_detect` via MCP to assess the relationship between the current message and the active topic.

三个风险等级 / Three risk levels：
- **low (0-30)**：没事，静默继续。Silent, continue.
- **medium (31-60)**：回复开头说一句上下文范围。One-line context note at reply start.
- **high (61-100)**：暂停，告诉你话题漂了，建议fork/switch/reset。Pause, flag the drift, suggest action.

MCP挂了？不卡你，静默降级。If MCP is down, degrades silently — won't block your work.

### Step 2: Skill Sense / 能力感知

三层检测，看你是不是缺了什么能力。

Three-tier detection to spot capability gaps.

**Tier 1 — 关键词匹配 / Keyword whitelist**：基于 `catalog_query.py` 里的TRIGGERS表做匹配。你说"部署"，它知道推荐deploy pack。三个条件同时满足才推荐：消息命中关键词 + 该pack没装 + 本session没推荐过。

Matches against TRIGGERS in `catalog_query.py`. You say "deployment" → it knows to recommend the deploy pack. Only recommends when: keyword hit + pack not installed + not already recommended this session.

**Tier 2 — 意图感知 / Intent detection**：Tier 1没命中时，判断你是不是在要一个需要外部集成的能力——发邮件、画甘特图、接监控——而agent自己和已装的skill都做不了。触发时建议 `/petfish search <关键词>`。

When Tier 1 doesn't match, checks whether you're asking for something that needs external integration — email, charts, monitoring — that neither the agent nor installed skills can handle. Suggests `/petfish search <keyword>`.

**Tier 3 — 没事 / No gap**：什么都没检测到，闭嘴。Nothing detected, stay silent.

推荐挂在回复末尾，不打断你。每个领域每session最多提醒一次。

Recommendations appear at the end of the reply, never interrupting. Each domain is mentioned at most once per session.

### Step 3: Proceed / 正常处理

Gateway跑完，进入正常工作。

Gateway done, normal processing begins.

### 交互后更新 / Post-Interaction Update

这轮交互有实质成果（改了代码、输出了文档、做了决定）？调用 `topic_update` 更新话题状态。

If this interaction produced real output (code changes, documents, decisions), calls `topic_update` to refresh topic state.

## Debug模式 / Debug Mode

在 `.petfish/fish-trail/config.yaml` 里配置：

Configure in `.petfish/fish-trail/config.yaml`:

```yaml
companion_gateway:
  debug: true
```

- `debug: true`：每次都把Gateway决策过程打出来（开发用）。Shows every Gateway decision (for development).
- `debug: false`（默认 / default）：只在medium/high风险或有推荐时才显示。Only shows for medium/high risk or when there's a recommendation.

Debug输出长这样 / Debug output looks like：

```
🐟 [gateway] topic: relation=continue, risk=12 (low), confidence=0.92 → silent
🐟 [gateway] skill: no gap → pass

🐟 [gateway] topic: relation=switch, risk=67 (high), confidence=0.85 → suggest fork
🐟 [gateway] skill: gap=deploy (detected "Docker部署") → recommend

🐟 [gateway] topic: relation=continue, risk=5 (low), confidence=0.95 → silent
🐟 [gateway] skill: tier2 gap detected (intent="send email", need="email integration") → suggest search
```

## 依赖 / Dependencies

Gateway靠两个东西：

Gateway depends on two components:

**1. context-state MCP** — 在 `opencode.json` 里配置 / Configured in `opencode.json`：
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

**2. catalog_query.py TRIGGERS** — companion skill里的关键词匹配表 / Keyword table in the companion skill：
```
.opencode/skills/petfish-companion/scripts/catalog_query.py
```

## 安装 / Install

装上 `companion` + `context` pack就自动生效：

Install the `companion` + `context` packs — Gateway activates automatically:

```bash
curl -fsSL https://raw.githubusercontent.com/kylecui/petfish.ai/master/remote-install.sh \
  | bash -s -- --pack companion,context
```

Gateway规则通过AGENTS.md的pack merge机制注入目标项目。

Gateway rules are injected into the target project via the AGENTS.md pack merge mechanism.

## 验证 / Verify

验证关键词匹配 / Test keyword matching：
```bash
uv run python .opencode/skills/petfish-companion/scripts/catalog_query.py --search "Docker"
# 应返回 deploy pack / Should return: deploy pack
```

验证MCP连接 / Test MCP connectivity：
```bash
uv run python .opencode/skills/fish-trail/mcp/context-state/server.py
# 应启动JSON-RPC server / Should start JSON-RPC server
```

跑测试 / Run tests：
```bash
uv run pytest tests/test_companion_gateway.py -v
```
