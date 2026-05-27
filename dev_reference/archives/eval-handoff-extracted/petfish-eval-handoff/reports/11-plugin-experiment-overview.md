# Plugin Context Inject Experiment

## 目的

验证将话题状态和记忆上下文通过 `experimental.chat.system.transform` plugin hook
注入 system prompt（cached prefix），替代当前"每轮 LLM 调用 MCP tool call"的模式，
是否能显著降低 token 开销和延迟。

## 背景

### P1 评估发现

Fish-trail v1.1.0 FULL arm 相比 OFF-clean baseline：

| 指标 | Template A (N=10) | Template F (N=1) |
|------|-------------------|-------------------|
| API Calls | +13.9% | -28% |
| Tokens | +12.3% (d_z=0.22) | -51% |
| Wall Time | +52.8% (d_z=0.50) | -21% |
| Recall Accuracy | 1.30/2.0 (vs 1.45) | — |
| Contamination | 0% (both arms) | — |

**结论：FULL arm 增加成本但不提升质量。**

### 根因分析

经过代码审查和配置审计，确认成本来自三层：

1. **Tool schema 固定成本**（~2K tokens/轮，cached）
   - 31 个 MCP tool schema 进入 system prompt
   - 成本可忽略（cached prefix）

2. **MCP tool call round-trip**（主要成本）
   - fish-trail.md 规则要求每轮调 `topic_detect` + `get_memory_context`
   - 每次 tool call 触发一次完整 API round-trip
   - 结果进入 conversation context（不可缓存）
   - 每轮多 ~4-6K tokens + 2-8s 延迟

3. **get_memory_context 注入的分层记忆文本**（次要成本）
   - 注入到 conversation context（不可缓存）
   - 每轮 ~2-4K tokens

### 关键发现：Tier 2 embedding 从未在 P1 中生效

- `.petfish/fish-trail/config.json` 没有 `embedding` 段
- `onnxruntime` 不在 uv 管理的 Python 环境中
- `.petfish/fish-trail/models/` 目录不存在
- P1 测试全部运行在 Tier 1 纯规则模式下

v0.7.2 测试时 embedding 曾手动启用并验证通过
（`embedding.enabled: true`, cross-language similarity 0.46-0.58），
但环境迭代后未保留。

### 关键发现：Plugin hook 已存在但只注入规则文件

`system-prompt-rules.ts` 通过 `experimental.chat.system.transform` 已在运行，
但只注入 `agents-rules/*.md` 规则文件到 system prompt。
话题状态和记忆上下文仍通过 MCP tool call 获取（进入 conversation context）。

**这是设计割裂：** 规则说"调 MCP tool"，plugin 解决了"规则文件要不要 Read"的问题，
但没解决"话题状态要不要 tool call"的问题。

### 关键发现：topic_detect 本身不调远程 LLM

审查 `topic_detector.py` 确认：
- Tier 1：纯规则（关键词提取 + Jaccard 相似度 + 信号词匹配），<1ms
- Tier 2：ONNX embedding（MiniLM-L12-v2, int8），~30ms，仅在模糊区触发
- 两者都是本地计算，不调远程 API

**成本不在引擎本身，而在 LLM 使用引擎的方式：**
每次 tool call 需要 LLM 先推理"是否需要调用" + 解读返回值 = 1 extra API round-trip。

## 假设

将话题状态和记忆上下文通过 plugin hook 注入 system prompt（cached prefix），
可以：
- H1: 消除每轮 1-2 次 MCP tool call round-trip → 降低 API calls ~10%
- H2: 将不可缓存的 conversation context tokens 转为可缓存的 system prompt tokens → 降低 total tokens ~10%
- H3: 降低 wall time ~30-40%（消除 tool call 延迟）
- H4: 不降低 recall accuracy（同等信息，不同传输通道）

## 实验设计

### Arms

| Arm | Plugin | fish-trail.md | MCP tool calls |
|-----|--------|---------------|----------------|
| A: OFF-clean | 无 plugin，无 fish-trail | 不加载 | 0 |
| B: FULL-current | system-prompt-rules.ts (rules only) | 当前版本（每轮调 topic_detect + get_memory_context） | 1-2/轮 |
| C: FULL-plugin-inject | system-prompt-context-inject.ts (rules + topic state + memory) | 修改版（不自动调 MCP，仅用户显式要求时调） | ~0/轮 |

### Template

使用 P1 的 Template A（3-topic-21msg），已在 P1 中验证过。

### 指标

| 指标 | 说明 |
|------|------|
| api_calls | 总 API 调用次数 |
| total_tokens | 总 token 消耗 |
| input_tokens | 输入 tokens |
| output_tokens | 输出 tokens |
| cache_read_tokens | 可缓存读取（plugin 注入部分） |
| wall_time_s | 端到端耗时 |
| recall_accuracy | LLM-as-judge 召回准确率 |

### 成功标准

- C vs B: token 开销降低 ≥10%
- C vs B: wall time 降低 ≥20%
- C vs A: token 开销增长 <5%
- C vs A: recall accuracy 不低于 A
