# 系统提示注入策略对AI Agent Token消耗的影响：一项对照实验

## 摘要

OpenCode v0.11.0引入tiered架构后导致Token总消耗增加了36.6%。本研究通过三方对照实验评估了两种system prompt注入策略（all-rules与smart-rules）对上下文管理机制和Token消耗的具体影响。实验结果表明，利用cached prefix机制缓存规则可以显著降低会话上下文的膨胀速度，进而减少compaction的触发次数。其中all-rules策略表现最优，相比v0.10.x基线降低了19.1%的总Token消耗，并将compaction次数从2次降至1次。研究证实compaction频率是决定LLM应用Token效率的核心因素，单次compaction成本远超插件注入开销。这一结论为AI Agent的上下文架构设计和系统提示优化提供了清晰的实证参考。

## 一、引言

在构建和运行LLM Agent时，上下文窗口（context window）管理是决定系统稳定性与运行成本的核心环节。当前主流模型通常具备固定的上下文上限，当对话历史逼近该上限时，系统必须执行compaction机制。compaction的过程涉及对既有对话历史生成总结，并丢弃大量原始上下文。这一机制虽然保证了对话的延续，但会产生高昂的额外成本，每次执行通常需要消耗数万Token。

现代LLM API支持system prompt缓存机制（cached prefix）。通过将静态规则置于系统提示中，系统可以在多个请求间复用这些Token，而无需将其计入每次对话的增量上下文中。合理利用cached prefix是控制Token消耗的关键。

OpenCode v0.11.0的更新引入了tiered AGENTS.md架构，将原本1037行的全量内联规则拆分为一个57行的主入口文件与7个按需加载的子规则文件（agents-rules/*.md）。此重构旨在提升规则的可维护性并降低初始提示体积。但在标准A/B测试中，该设计引发了严重的性能衰退：相比v0.10.x基线的744,904 Tokens，v0.11.0的Token总消耗达到1,017,201 Tokens，增幅为36.6%，且compaction次数从2次增加到3次。

回归的根因在于动态加载机制改变了规则文本在LLM上下文中的存储位置。在tiered设计下，LLM必须使用Read tool动态读取子规则文件。每次工具调用的结果均会被写入会话上下文（conversation context）。由于会话上下文属于不可缓存的用户轮次内容，随着对话轮次增加，规则文本不断累积，导致上下文窗口迅速达到compaction阈值。

为解决此问题，本研究利用OpenCode的`experimental.chat.system.transform`插件钩子，设计了两种将规则重新注入system prompt的方案。本研究旨在通过严格的对照实验，量化这两种注入策略对Token消耗的影响，并为后续架构演进提供决策依据。

## 二、方法

### 2.1 实验设计

本研究采用三方对照测试架构，在同一物理主机上并行运行三个独立的测试环境。

1. **Baseline (端口3100)**：模拟v0.10.x行为，AGENTS.md采用1037行全量inline模式，不使用任何插件。
2. **All-rules (端口3200)**：采用v0.11.0的57行tiered架构，挂载`system-prompt-all-rules.ts`插件，该插件直接将7个子规则文件全量注入system prompt。
3. **Smart-rules (端口3300)**：采用v0.11.0的57行tiered架构，挂载`system-prompt-smart-rules.ts`插件，该插件根据活跃话题状态动态匹配并注入相关规则文件。

### 2.2 测试负载与环境

测试模型统一采用github-copilot/claude-sonnet-4。测试工作流由自定义的Python自动化脚本（`ab_test_harness.py`）配合Bash编排脚本驱动。

负载设计包含21条标准消息，分布于3个交替执行的话题（python-setup、database、cicd），每个话题执行7轮递进对话。在21轮对话结束后，脚本会追加3条召回问题，用于测试系统在经历compaction后的上下文细节保持能力。

测试分为两个独立轮次（Round）进行：
* Round 1：Baseline对齐All-rules策略
* Round 2：Baseline对齐Smart-rules策略

### 2.3 环境隔离与一致性验证

在多实例并行测试中，任何配置串扰都会导致数据失效。针对初期测试暴露的环境污染问题，本实验实施了严格的隔离与验证程序。

为防止端口复用导致CWD（当前工作目录）指向错误，启动流程中加入了基于`/proc/PID/cwd`的显式目录验证。针对OpenCode向上查找`.git`目录的特性，为避免测试目录继承父项目的96个skills定义（约58K Tokens），系统为每个隔离测试目录独立执行了`git init`初始化。

启动后，测试脚本提取首条消息的`effective_ctx`字段以验证system prompt体积，结果完全符合理论预期：
* Baseline验证值为45,021 Tokens，符合32K基础提示加13K内联规则的预期。
* All-rules验证值为45,041 Tokens，增量仅为20 Tokens。
* Smart-rules验证值为32,452 Tokens，符合基础提示加单条匹配规则的预期。

## 三、结果与分析

### 3.1 All-rules策略表现 (Round 1)

第一轮测试比对了v0.10.x基线与All-rules插件的性能。

| 指标 | Baseline (v0.10.x) | All-Rules Plugin | 变化 |
|------|-------------------|-----------------|------|
| Input tokens | 455,533 | 327,834 | -28.0% |
| Output tokens | 131,384 | 147,205 | +12.0% |
| Cache read | 5,692,657 | 6,082,194 | +6.8% |
| Total tokens | 586,917 | 475,039 | -19.1% |
| 消息数 | 76 | 87 | +14.5% |
| Compaction 次数 | 2 | 1 | -50% |
| 峰值上下文 | 152,990 | 145,530 | -4.9% |
| 耗时 | 2,041s | 2,383s | +16.8% |
| 错误 | 0 | 0 | — |

All-rules策略显著降低了输入Token的消耗，使总Token需求下降了19.1%。最核心的差异在于compaction次数从基线的2次减少为1次。

### 3.2 Smart-rules策略表现 (Round 2)

第二轮测试比对了v0.10.x基线与Smart-rules插件的性能。

| 指标 | Baseline (v0.10.x) | Smart-Rules Plugin | 变化 |
|------|-------------------|-------------------|------|
| Input tokens | 576,137 | 510,717 | -11.4% |
| Output tokens | 149,061 | 124,995 | -16.1% |
| Cache read | 5,654,659 | 4,508,906 | -20.3% |
| Total tokens | 725,198 | 635,712 | -12.3% |
| 消息数 | 64 | 64 | 0% |
| Compaction 次数 | 2 | 1 | -50% |
| 峰值上下文 | 152,844 | 141,031 | -7.7% |
| 耗时 | 2,442s | 2,187s | -10.4% |
| 错误 | 0 | 0 | — |

Smart-rules策略同样将compaction次数降至1次，总Token消耗相比当前轮次的基线下降了12.3%。

### 3.3 全局效率对比

整合历史回归数据与本次对照实验结果，呈现如下全局视图：

| 方案 | Total Tokens | vs v0.10.x | Compactions | 每条消息平均 | 耗时 |
|------|-------------|-----------|-------------|-------------|------|
| v0.10.x baseline (R1) | 586,917 | — | 2 | 7,722 | 2,041s |
| v0.11.0 + all-rules | 475,039 | -19.1% | 1 | 5,460 | 2,383s |
| v0.10.x baseline (R2) | 725,198 | — | 2 | 11,331 | 2,442s |
| v0.11.0 + smart-rules | 635,712 | -12.3% | 1 | 9,933 | 2,187s |
| v0.11.0 无插件 (历史) | 1,017,201 | +36.6% | 3 | — | — |

需要指出，在两次独立的基线测试中（均使用3100端口配置），Token总量出现了显著差异（586,917对725,198）。此差异源于LLM生成内容的固有随机性，在固定工作流下模型给出的步骤细节和代码长度难以完全一致。因此，跨轮次的绝对数值比较缺乏严格意义，但单轮次内部的相对变化率具备高度可靠性。

## 四、讨论

### 4.1 Compaction开销的主导作用

实验数据清晰表明，Token消耗的波动主要由compaction机制的触发频率驱动。插件自身的处理开销在整体成本中占比极小。

在基线测试中，系统触发compaction的阈值位于130K至153K Tokens之间。触发后，系统强制生成总结并将上下文截断至47K至49K Tokens。这一过程直接丢弃了约90K的已有上下文，且总结请求本身需要额外消耗5K至10K Tokens。单次compaction的综合Token成本被评估为50K至80K。

| 运行 | 第 1 次 Compaction | 第 2 次 Compaction |
|------|-------------------|-------------------|
| R1 Baseline | msg 17 (ctx ~145K→47K) | msg 49 (ctx ~153K→49K) |
| R2 Baseline | msg 18 (ctx ~137K→48K) | msg 50 (ctx ~153K→48K) |
| R1 All-Rules | msg 15 (ctx ~136K→47K) | 无 |
| R2 Smart-Rules | msg 34 (ctx ~124K→36K) | 无 |

插件方案之所以能有效减少compaction次数，是因为它们改变了规则上下文的存储生命周期。在v0.11.0无插件状态下，LLM通过Read工具读取的文件内容被全量装载至uncached状态的会话上下文中，迅速透支了可用窗口。通过插件将规则提前注入system prompt，这部分体积被成功转移至cached prefix区域，不再随对话轮次累加计算。

All-rules插件引入的静态开销仅为20个新增系统提示Tokens，以及每轮对话中约12.6K的cache read增量。在87轮对话中累计产生的1.1M cache read Tokens，按当前API定价仅等值于0.33美元，远低于减少一次compaction所挽回的成本。

### 4.2 All-rules与Smart-rules架构权衡

尽管Smart-rules策略在理论上提供了更精确的上下文管理，但实验结果显示All-rules策略在当前规模下具有压倒性优势。

从工程复杂度考量，All-rules插件仅需71行代码，且为零配置运行，新增Markdown规则文件可自动生效。相反，Smart-rules实现需要131行代码，且强依赖外部注册表，必须手动维护硬编码的映射逻辑。

Smart-rules存在多处静默失败风险节点。当注册表不可读、活跃话题为空、映射关系过期或关键词匹配出现假阴性时，系统将退化为无规则状态而不报错。基于子字符串的匹配机制同时容易引发假阳性，导致不相关规则被错误注入。

结合模型容量评估，以150K窗口和135K触发阈值为基础，减去32K核心提示，剩余空间决定了策略选型的边界。当全局规则集小于30K Tokens时，All-rules可保留超过73K的自由对话空间，这是绝对安全的区间。当前测试使用的7个规则文件总计约9.4K Tokens，显然处于All-rules的最优适用范围内。仅当全局规则集突破50K Tokens，导致单轮加载可能直接触发compaction时，Smart-rules的动态裁剪特性才具备应用价值。

## 五、结论

本研究通过受控实验量化了system prompt动态注入对Token管理的影响。基于上述数据分析，得出以下结论：

1. 基于`experimental.chat.system.transform`钩子的插件方案可以有效解决v0.11.0架构引发的36.6% Token回归问题，并实现超越旧版基线的运行效率。
2. 在长上下文对话中，compaction频率是决定总体Token成本的绝对主导因素。单次compaction带来的额外成本远超任何静态前缀缓存的读取成本。
3. 在现有约10K Tokens规模的规则集下，All-rules策略在性能改善幅度、代码复杂度及系统鲁棒性上均优于Smart-rules策略。
4. 综合评估显示，v0.11.0配合All-rules插件是当前最优的上下文管理配置。

建议将All-rules插件纳入标准部署流程中。针对规模更大的未来规则集，Smart-rules机制需在解决其静态映射维护和故障透传问题后，作为按需降级的后备方案提供。

## 附录

### 附录A：复现指南与关键步骤

本实验依赖特定的插件钩子实现system prompt内容的动态覆写。以下为核心API参考规范：

```typescript
"experimental.chat.system.transform": async (
  input: { sessionID?: string; model: Model },
  output: { system: string[] }
) => Promise<void>
```

实现时需注意直接修改`output.system`数组。被注入的内容由底层API提供商自动识别为cached prefix。

### 附录B：实验环境排错记录

实验初期遭遇的数据污染提示了两个关键工程陷阱，复现者需严格规避：
1. OpenCode的路径解析机制强依赖`.git`目录进行根节点定位。隔离的测试环境必须具备独立的`.git`初始化状态，否则会导致配置向上渗透，继承父级工作区的海量skills定义，使得初始system prompt从正常值暴涨。
2. 守护进程的CWD管理存在滞后性。驻留环境中的旧服务器进程不会自动响应新测试目录的建立，必须执行显式的进程清理，并在每次冷启动时核对`/proc/PID/cwd`信息。
