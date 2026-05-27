# Companion Gateway

胖鱼的Companion Gateway是每条消息的自动入口。不靠agent"记得"去做——直接写在项目指令文件的最高优先级位置，每轮都跑。

## 工作原理

```
用户消息
    → [Companion Gateway]
          │
          ├─ Step 0: Mode Read (project-mode.yaml)
          ├─ Step 1: Topic Check (topic_detect MCP)
          ├─ Step 1.5: Failure Signal Detection (上轮错误检测)
          ├─ Step 2: Skill Sense (能力缺口检测)
          ├─ Step 2.5: Anti-Sycophancy Check (评价性问题)
          └─ Step 3: Proceed (正常处理)
```

### Step 0: 项目模式读取

每次session首条消息时读取 `.opencode/project-mode.yaml`（如存在）：

```yaml
depth: balanced       # urgent | balanced | thorough
rigor: false          # true | false (depth=thorough时强制为true)
```

**Depth** 控制调试、搜索和失败响应的激进程度：

| Depth | Bug处理 | 依赖问题 | 搜索策略 | 失败响应 |
|---|---|---|---|---|
| urgent | 先绕过，记TODO | 用替代方案 | 第一个可信结果 | 快速修→继续 |
| balanced | 正常调试流程 | 理解基础后修复 | 2-3来源 | 标准流程 |
| thorough | 必须找根因 | 全影响分析 | 多源交叉验证 | 证据驱动修复 |

**Rigor**（为true或被 `depth: thorough` 强制时）增加计划-评审纪律：3+步骤任务需要正式计划文件、Momus评审后才实施、显式声明假设。

**Session内切换**：用户说"紧急"/"仔细"/"严谨"等关键词时在当前session内切换模式，不写文件。下次session自动恢复。

文件不存在时默认 `depth: balanced, rigor: false`，不阻塞。

### Step 1: 话题检测

调用MCP的 `topic_detect`，看当前消息跟活跃话题什么关系。

三个风险等级：
- **low (0-30)**：没事，静默继续。
- **medium (31-60)**：回复开头说一句上下文范围。
- **high (61-100)**：暂停，告诉你话题漂了，建议fork/switch/reset。

MCP挂了？不卡你，静默降级。

### Step 1.5: 失败信号检测

扫描**上一轮assistant回复**和工具错误输出，匹配已知失败模式。命中且存在对应skill/pack时推荐安装。

**触发条件（全部满足）：**
1. 上一轮明确承认无法完成或工具返回已知错误模式。
2. 存在已知skill/pack可以解决该类失败。
3. 该信号本session未推荐过（去重）。
4. 对应skill/pack未安装。

**信号→Pack映射：**

| 失败模式 | 推荐Pack |
|---|---|
| 无法读取/解析PDF/PPTX | `ppt` |
| 部署/Docker失败 | `deploy` |
| 测试用例生成困难 | `testdocs` |
| 研究深度不足 | `research` |
| 上下文污染/漂移 | `context` |

输出格式：
```
💡 检测到上轮失败信号 — <pack> skill可以处理此类问题。安装: /petfish install <pack>
```

### Step 2: 能力感知

三层检测，看你是不是缺了什么能力。

**Tier 1 — 关键词匹配**：基于 `catalog_query.py` 里的TRIGGERS表做匹配。你说"部署"，它知道推荐deploy pack。三个条件同时满足才推荐：消息命中关键词 + 该pack没装 + 本session没推荐过。

核心包（init、companion、petfish、toolchain）直接从petfish.ai安装。可选包（course、research、deploy等）通过petfish-market分发——安装命令自动解析，用户无感知。

**Tier 2 — 意图感知**：Tier 1没命中时，判断你是不是在要一个需要外部集成的能力——发邮件、画甘特图、接监控——而agent自己和已装的skill都做不了。触发时建议 `/petfish search <关键词>`。

**Tier 3 — 没事**：什么都没检测到，闭嘴。

推荐挂在回复末尾，不打断你。每个领域每session最多提醒一次。

> **v1.4说明**：可选pack（course、research、deploy等）通过petfish-market分发。当Skill Sense推荐可选pack时，安装命令通过market解析——用户体验相同，底层解析路径不同。

### Step 2.5: 反迎合检查

在回答评价性问题（"好吗?"、"对吗?"、"what do you think?"）之前：

1. **暂停**。不要立即同意。
2. 定义"好"在此语境下的含义（rubric-first）。
3. 找到至少**一个**提案可能错误的原因。
4. 然后再形成结论。

如果真诚努力后找不到反论 → 同意是合理的。
如果跳过此步骤 → 你在迎合用户。

**主动性与Rigor绑定：**

| Rigor | Anti-Sycophancy Level |
|---|---|
| off | 仅对显式评价性问题（"好吗?", "对吗?"） |
| on | 也对隐式寻求认可 + 技术断言进行检查 |

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
.opencode/skills/fish-brain/scripts/catalog_query.py
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
uv run python .opencode/skills/fish-brain/scripts/catalog_query.py --search "Docker"
# 应返回 deploy pack
```

验证失败信号检测：
```bash
uv run python .opencode/skills/fish-brain/scripts/catalog_query.py --check-failures "无法读取PDF文件"
# 应返回 ppt pack 推荐
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
