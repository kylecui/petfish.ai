# Companion Gateway Architecture

PEtFiSh 如何在无需修改 AI 平台的前提下，实现一个在每条用户消息之前运行的 always-on 拦截层。

---

## 设计挑战

AI agents 是会遗忘的。除非被明确要求，否则它们不会在多轮对话间保持状态。这导致上下文会悄无声息地偏离，能力缺口未被察觉，而毫无底线的迎合（sycophantic agreement）则取代了诚实的评估。

典型的解决方案 —— 在 system prompt 中添加“记得检查 X” —— 无法在规模扩大时奏效。在 token 的压力下，agents 会跳过那些可选的指令，而且也没有任何强制执行机制。

PEtFiSh 的 Companion Gateway 通过另一种方式解决了这个问题：**在指令文件中优先级最高的位置注入强制预处理步骤 (mandatory pre-processing)**，使其在结构上无法被跳过。

---

## 架构

```text
User message arrives
    │
    ▼
┌─────────────────────────────────────────┐
│         Companion Gateway               │
│                                         │
│  Step 0: Mode Read ──────── Config      │
│  Step 1: Topic Check ────── MCP Server  │
│  Step 1.5: Failure Signal ── Catalog    │
│  Step 2: Skill Sense ────── Catalog     │
│  Step 2.5: Anti-Sycophancy              │
│  Step 3: Proceed                        │
│                                         │
│  Post: Topic Update ────── MCP Server   │
└─────────────────────────────────────────┘
    │
    ▼
Normal task processing
```

Gateway 并非中间件或 API 代理。它是被放置在项目 `AGENTS.md` 文件顶部的行为指令块。AI agent 将执行这些步骤视为自身推理过程的一部分 —— 不需要任何外部运行时。

### 为什么这能行得通

以下三个属性使得 Gateway 能够可靠运行：

1. **位置优先级**。位于 `AGENTS.md` 顶部的指令会先于任何特定任务的规则被处理。Agent 在读取其他任何内容之前必定会先读取 Gateway。

2. **无条件执行**。Gateway 部分使用了祈使句（“必须执行 (MUST execute)”、“在处理前 (before processing)”）而非条件句（“如果适用 (if applicable)”、“当需要时 (when needed)”）。这降低了 agent 将其优化掉的几率。

3. **优雅降级 (Graceful degradation)**。每一个依赖外部服务（MCP、scripts）的步骤都有相应的 fallback，并且不会阻塞正常工作。Gateway 永远不会让你的 agent 变糟 —— 它只会在依赖项可用时让 agent 变得更好。

---

## 步骤设计初衷

这六个步骤并非一开始就被设计在一起。它们是从实际项目中观察到的失败模式中逐步演变而来的。

### Step 0: Mode Read — 自适应行为

**解决的问题：** 项目的不同阶段需要不同的 agent 行为模式。一个生产环境的紧急修复需要速度，而架构评审则需要周密。如果没有显式配置，agent 会默认采用一种既不够快也不够严谨的折中方案。

**设计选择：** 使用正交的两个维度（`depth` 和 `rigor`），而不是单一的“模式”参数。这允许你组合出 `urgent + rigor`（快速但有纪律）或 `thorough + no rigor`（深入但不拘小节）。

**Session 覆盖机制** 之所以存在，是因为在对话中途编辑 YAML 配置文件非常打断心流。Agent 能识别自然语言的模式切换（例如“让我们仔细审查一下”），并且无需进行文件读写即可调整自身行为。

### Step 1: Topic Check — 防范上下文污染

**解决的问题：** 当用户在没有明确给出信号的情况下切换话题时，agent 会将前一个 topic 的上下文带入其中。这会引发微妙的 bugs：topic A 的变量名泄漏到 topic B 的代码里，或者为 topic A 做出的决策限制了 topic B 的选项。

**设计选择：** 将检测工作委托给一个 MCP server（`context-state`），而不是把启发式规则嵌入到 prompt 里。MCP server 维护着一个带有污染评分的 topic 图谱，这样的状态追踪对纯 prompt 的实现方案来说过于复杂。

**风险等级 (Risk levels)**（低/中/高）的存在是因为并非所有的话题切换都危险。在同一领域内提出澄清问题属于低风险；而从“部署服务 A”切换到“重构服务 B”则是高风险 —— agent 可能会将服务 A 的部署约束误应用到服务 B 的重构中。

有关 topic-aware compaction 如何将 token 成本降低 20% 的详细信息，请参阅 [Token Cost Engineering](compaction.md)。

### Step 1.5: Failure Signal Detection — 从错误中学习

**解决的问题：** 当 agent 在一项任务中失败时（例如无法读取 PDF 或部署报错），它通常会道歉然后继续。用户可能并不知道其实存在一个可以解决此问题的 skill pack。

**设计选择：** 对前一轮对话文本进行模式匹配，而不是进行实时的工具监控。这在实现上更简单，而且无需挂载到工具的执行流程中。代价是会产生一轮对话的延迟 —— 推荐会在失败发生之后出现，而不是在发生时。

**去重机制 (Deduplication)**（每个 session 中每个信号只触发一次）可以防止 Gateway 喋喋不休。如果用户忽略了推荐，它绝不再犯烦。

### Step 2: Skill Sense — 主动检测能力缺口

**解决的问题：** 用户不清楚当前有哪些 skills 可用。他们要求 agent 做某事，agent 凭借其基础能力去尝试，结果往往平庸 —— 而如果调用专用的 skill，本可以得到好得多的结果。

**三层设计：**

| 层级 | 机制 | 覆盖范围 | 误报风险 |
|---|---|---|---|
| Tier 1 | 关键词白名单 | 仅限已知 packs | 极低 |
| Tier 2 | 意图分类 | 未知领域 | 中等 |
| Tier 3 | 不检测 | — | 零 |

Tier 1 刻意保持保守 —— 它只在确认与已知 pack 领域关键词匹配时才会触发。Tier 2 采用更宽泛的意图分析，但只在高置信度（>70%）时触发。Tier 3 是默认层级：如果有疑虑，那就保持沉默。

**回复末尾放置 (End-of-reply placement)** 确保推荐永远不会打断 agent 的实际工作。用户首先得到他们想要的答案，随后才是建议。

### Step 2.5: Anti-Sycophancy Check — 诚实评估

**解决的问题：** AI agents 默认倾向于认同用户。当被问到“这个方案好吗？”时，即使方案存在明显缺陷，它们也会找理由说好。这在架构决策、代码审查和战略规划中尤其危险。

**设计选择：** 在给出任何评估性结论之前，强制进行反面论证。Agent 必须至少找到一个说明用户提案可能存在问题的理由，然后才被允许表示赞同。

**与 Rigor 模式联动：** 当 rigor 模式关闭时，anti-sycophancy 仅针对明确的评估问题（“这样对吗？”）激活。当 rigor 打开时，它也会针对隐式的认可寻求（“我打算用 X”）和技术断言（“这个应该能运行，因为……”）激活。这种渐进式策略避免了在闲聊中拖慢节奏，同时在关键决策时提供全面保护。

---

## 实现机制

### 通过 AGENTS.md 注入

Gateway 并非一个独立的系统 —— 它是 `AGENTS.md` 文件中的一个区块，在 pack 安装时被合并进去。安装流程如下：

1. `companion` pack 的 `AGENTS.md` 片段中包含 Gateway 规则。
2. 安装器使用基于标记的合并（`<!-- agents-rules/... -->`）将该片段注入项目的 `AGENTS.md`。
3. Gateway 区块被定位在最顶部，优先于任何 pack 的特定规则。
4. 在升级（`--force`）时，该区块会被替换，而保留标记外用户自定义的内容。

这意味着 Gateway 可以在任何读取 `AGENTS.md`（或等效文件）的平台上工作 —— 包括 OpenCode, Claude Code, Codex, Cursor, GitHub Copilot, Windsurf 和 Antigravity。无需任何平台特定的钩子。

### 外部依赖

Gateway 与两个可选的外部组件进行交互：

**context-state MCP server** — 提供 topic 检测 (Step 1) 以及交互后的更新。作为一个本地进程运行，将状态存储在 `.petfish/fish-trail/` 目录下。通过 `context` pack 安装。

```json
{
  "mcp": {
    "context-state": {
      "type": "local",
      "command": ["uv", "run", "python",
        ".opencode/skills/fish-trail/mcp/context-state/server.py"]
    }
  }
}
```

**catalog_query.py** — 提供关键词匹配 (Step 2) 以及错误信号检测 (Step 1.5)。它是 `companion` pack 中的一个 Python 脚本，负责读取 pack 的元数据与触发定义。

```bash
# Keyword matching
uv run python .opencode/skills/petfish-companion/scripts/catalog_query.py \
  --search "Docker"

# Failure signal detection
uv run python .opencode/skills/petfish-companion/scripts/catalog_query.py \
  --check-failures "无法读取PDF文件"
```

当上述任意一个组件不可用时，对应的步骤会静默跳过。Gateway 从不抛出错误 —— 它只给出推荐，或者保持沉默。

### Debug 模式

为了提升开发时的可见性，Gateway 支持一个调试模式，用于展示每次决策的细节：

```
🐟 [gateway] topic: relation=continue, risk=12 (low), confidence=0.92 → silent
🐟 [gateway] skill: no gap → pass
```

这在 `.petfish/fish-trail/config.yaml` 中配置，默认为关闭。在开发或调试 Gateway 行为时，将其打开便能展示完整的决策链，而无需依赖日志文件或外部监控工具。

---

## 设计约束

一些限制条件塑造了 Gateway 的架构：

### 无需运行时

Gateway 必须在没有任何后台服务运行的情况下依然有效。MCP server 和 scripts 可以增强它的能力，但核心行为规则（如 Mode Read, Anti-Sycophancy Check）仅依赖于 prompt 指令工作。这意味着即使是一个刚安装且没有任何 MCP 配置的新项目，同样能从 Gateway 中受益。

### Token 预算

`AGENTS.md` 中的 Gateway 区块在每次交互时都会消耗 token。当前的实现约占 2,500 tokens —— 大概是一个典型 80K context 窗口的 3%。这一预算开销是合理的，因为 [system prompt 注入实验](sysprompt-design.md) 表明：结构良好的指令能够降低 compaction 的频率，最终产生约 19% 的净 token 节省。

### 单轮延迟

Failure Signal Detection (Step 1.5) 扫描的是前一轮对话，而非当前这轮。这意味着它无法捕捉到首次发生的失败 —— 只有后续的交互才能受益。这是一种深思熟虑的取舍：要实现实时工具监控，就需要依赖平台专属的挂载钩子，但这打破了“在任何平台均可工作”的设计目标。

### Session 作用域

模式覆盖（Mode overrides）和推荐去重都是针对单个 session 的。Gateway 自身没有持久化记忆，其状态依赖 MCP server 维护的 topic 状态。这简化了实现，但也意味着每个新 session 都是从零开始 —— 模式会恢复为配置文件中的默认值，推荐去重也会重置。

---

## 演进历史

Gateway 最初在 v0.6.0 版本中作为一个三步流程被引入：

```text
v0.6.0: Topic Check → Skill Sense → Proceed
v0.11.0: Mode Read → Topic Check → Failure Signal → Skill Sense → Anti-Sycophancy → Proceed
```

每一次的添加，都源于我们在生产环境中观察到的特定失败模式：

| Version | 增加的步骤 | 解决的失败模式 |
|---|---|---|
| v0.6.0 | Topic Check | 跨主题造成的上下文污染 |
| v0.6.0 | Skill Sense | 用户未能发现可用的 skills |
| v0.11.0 | Mode Read | agent 在处理项目不同阶段时表现得缺乏轻重缓急 |
| v0.11.1 | Failure Signal | 用户在重复遭遇失败时未能获得相应的 pack 推荐 |
| v0.11.4 | Anti-Sycophancy | 对存在明显缺陷的方案表示出无原则的赞同 |

现有的 6 步架构很可能不是最终形态。未来的新增功能依然会遵循相同的模式：观察系统性的失败模式，设计最小化干预机制，并作为一个具备优雅降级能力的新步骤加入进来。

---

## 延伸阅读

- [System Prompt Architecture](sysprompt-design.md) — Gateway 规则如何融入分层指令系统中
- [Token Cost Engineering](compaction.md) — topic-aware 上下文管理如何降低 session 成本
- [Companion Gateway Guide](../guides/companion-gateway/index.md) — 面向用户的配置与使用指南