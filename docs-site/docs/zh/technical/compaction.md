# Token Cost Engineering

PEtFiSh 如何通过降低 compaction 频率与改变行为模式，将 AI agent session 成本降低 20%。

---

## 成本难题

长时间的 AI agent session 非常昂贵 —— 并非因为 prompt 体积或响应长度，而是因为 **compaction**（压缩）。当对话上下文填满时，平台会总结历史记录以腾出空间。每一次 compaction 事件都会消耗 5 万到 8 万 token 的开销。

AI agent session 中首要的成本驱动因素并不是你发送了什么，而是 compaction 触发的频率。

PEtFiSh 进行了两项对照实验，旨在理解并降低这一成本。

---

## 背景：为什么 v0.11.0 出现了 37% 的性能回退

PEtFiSh v0.11.0 为 agent 规则引入了分层架构：不再使用一个 1,037 行的内联文件，而是将规则拆分为一个 57 行的入口文件加上 7 个按需加载的子文件。这样更清晰，也更易于维护。

但在 A/B 测试中揭示了 **36.6% 的 token 回退 (regression)**。原因在于：动态加载的规则落入了未缓存的对话上下文中。它们随着每一次工具调用不断累积，导致上下文窗口更快膨胀，从而触发更多次的 compaction（从 2 次增加到 3 次），每次都需要消耗 5-8 万 token。

解决方案并不是“退回到内联文件”，而是要弄清楚规则应当存在于 LLM 内存架构的*哪里*。

---

## 实验 1：System Prompt 注入

利用 OpenCode 的 `experimental.chat.system.transform` 钩子开发了两个插件，将规则重新移回已缓存的 system prompt 前缀中：

- **All-rules** — 将所有 7 个规则文件（约 9.4K tokens）注入 system prompt 中。71 行代码，零配置。
- **Smart-rules** — 根据活动 topic 动态匹配规则。131 行代码，需要一个映射注册表。

### 结果

21 条消息，3 个 topics，使用 `claude-sonnet-4` 模型：

| Metric | Baseline (v0.10.x) | All-Rules Plugin | Delta |
|---|---|---|---|
| Total tokens | 586,917 | 475,039 | **-19.1%** |
| Input tokens | 455,533 | 327,834 | -28.0% |
| Compactions | 2 | 1 | **-50%** |
| Peak context | 152,990 | 145,530 | -4.9% |

Smart-rules 实现了 12.3% 的成本节省，但被证明是脆弱的 —— 缺失映射时会导致静默失败，有关键字匹配的假阳性，并增加了手动维护的负担。对于 30K tokens 以下的规则集，all-rules 在所有维度上都占优。

### 核心洞见

将所有规则注入 system prompt 所带来的 20 token 额外开销微不足道。真正关键的是，已缓存的前缀内容**不计入 compaction 阈值的累积**。少一次 compaction，就意味着节省了 5-8 万 tokens。

---

## 实验 2：Topic-Aware Compaction

另一项独立研究提出：当 compaction *真的*触发时，PEtFiSh 的 topic 管理机制能否让它变得更智能？

fish-trail topic 系统已经在追踪你正在处理的工作 —— 哪些 topics 处于活跃状态，它们的关系，以及它们的摘要。Phase 2 插件利用这些 topic 数据重构了 compaction prompt，告诉模型：“这里有 3 个 topics，请将它们分开压缩，并优先保留活跃的 topic。”

### 结果

21 条消息，3 个交织的 topics，使用 `claude-sonnet-4` 模型：

| Metric | Baseline | Topic Plugin | Delta |
|---|---|---|---|
| Total tokens | 857,115 | 683,522 | **-20.3%** |
| API calls | 140 | 89 | -36.4% |
| Wall time | 49 min | 30 min | -39.4% |
| Cache reads | 10.6M | 5.3M | -49.9% |
| Recall quality | Pass | Pass | **无损** |

### 意外收获：行为模式的改变

预期的成本节省本应来自更好的压缩率。但实际情况并非如此。

最主要的机制是**行为模式的改变 (behavioral change)**。当模型接收到以 topic 结构化的上下文时，它会生成更聚焦的响应 —— 更少的中间工具调用（4.2 次/消息 对比 6.7 次/消息），更加整合的答案。这产生了一种级联效应：更少的 API 调用 → 更少的缓存读取 → 更快的绝对耗时。

这就是为什么 Phase 3（跳过 LLM 直接使用预计算摘要）被搁置的原因：它无法触发这种行为效应。模型需要在 compaction 期间*处理*以 topic 结构化的上下文，而不仅仅是接收一个预构建的摘要。

---

## 研究发现

1. **Compaction 频率主导了 token 成本。** 其他一切 —— prompt 体积、输出长度、缓存策略 —— 都是次要的。降低 compaction 次数，成本就会大幅下降。

2. **缓存前缀是免费地产。** system prompt 中的规则几乎没有成本（缓存读取比输入 tokens 便宜约 10 倍）。而存在于对话上下文中的规则则是一颗不断走向下一次 compaction 的定时炸弹。

3. **Topic 结构能改变模型行为。** 不仅仅是压缩质量 —— 当模型拥有其工作内容的结构化上下文时，它实际上变得更加高效。

4. **大道至简。** All-rules（71 行代码，零配置）在成本和可靠性上都击败了 Smart-rules（131 行代码，依赖注册表）。不要去优化那些不需要优化的东西。

---

## 局限性

- 仅在 `claude-sonnet-4` 模型上测试过。其他模型可能有所不同。
- 基于 21 条消息并涉及 3 个 topics 的 sessions。更大规模的 sessions 可能会呈现不同规律。
- 仅限单用户场景。未测试多窗口并发 sessions。
- OpenCode 的插件钩子被标记为 `experimental`（实验性） —— 尽管已有 11 个以上的外部项目在生产环境中使用它们。

---

## 可用性

这两款插件均随 PEtFiSh 提供：

- **System prompt 插件**：包含在 `companion` pack 中
- **Topic-aware compaction 插件**：包含在 `context` pack (fish-trail) 中

```bash
# Install both plugins
curl -fsSL https://raw.githubusercontent.com/kylecui/petfish.ai/master/remote-install.sh \
  | bash -s -- --pack companion,context --detect
```

完整的实验数据、A/B 测试脚手架以及原始结果均可参见 [GitHub 仓库](https://github.com/kylecui/petfish.ai)：

- Experiment 1: `evals/v011-sysprompt-plugin-report/PAPER.md`
- Experiment 2: `research/topic-aware-compaction/06_outputs/research-report.md`

所有实验均在 OpenCode 中通过 `github-copilot` 驱动下的 `claude-sonnet-4` 模型运行。

---

## 延伸阅读

- [System Prompt Architecture](sysprompt-design.md) — PEtFiSh 如何构建 agent 指令
- [Companion Gateway](companion-gateway.md) — 始终在线的预处理管道