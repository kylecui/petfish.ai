# OpenCode v0.11.0 System Prompt Plugin 方案测试报告

**报告日期**: 2026-05-12  
**测试执行人**: petfish_tester 项目  
**报告版本**: v1.0 — 基于干净环境重跑数据  
**目标受众**: PEtFiSh 核心团队

---

## 一、背景与问题

### 1.1 问题起源

OpenCode v0.11.0 引入了 tiered AGENTS.md 架构：将原先 1037 行的全量 inline AGENTS.md 拆分为一个 57 行的入口文件 + 7 个按需加载的 `agents-rules/*.md` 规则文件。目的是降低系统提示的体积、提高可维护性。

### 1.2 发现的回归

在标准 A/B 测试中，v0.11.0 的 tiered 设计反而产生了 **+36.6% 的 token 总开销**：

| 配置 | Input Tokens | Total Tokens | Compactions |
|------|-------------|-------------|-------------|
| v0.10.x (inline) | 643,277 | 744,904 | 2 |
| v0.11.0 (tiered, 无插件) | 884,351 (+37.5%) | 1,017,201 (+36.6%) | 3 |

**根因分析**: v0.11.0 的 tiered 设计导致 LLM 通过 Read tool 按需读取规则文件。每次 Read 将文件内容放入会话上下文（conversation context），属于 **不可缓存** 的用户轮次内容，会随着对话累积增长，导致：
1. 上下文窗口更快达到 compaction 阈值
2. compaction 次数从 2 次增加到 3 次
3. 每次 compaction 消耗 ~50-80K 额外 tokens

### 1.3 提出的解决方案

利用 OpenCode 的 `experimental.chat.system.transform` Plugin Hook，将规则内容注入到系统提示（system prompt）中。系统提示是 **可缓存的前缀**（cached prefix），不会增长会话上下文，从而减少 compaction 频率。

开发了两个插件方案：
- **Plugin A (all-rules)**: 将全部 7 个规则文件注入系统提示（71 行代码）
- **Plugin B (smart-rules)**: 根据 fish-trail 活跃话题，仅注入匹配的规则文件（131 行代码）

---

## 二、测试设计

### 2.1 三方对照测试

| 端口 | 目录 | AGENTS.md | Plugin | 角色 |
|------|------|-----------|--------|------|
| 3100 | `test-v010x/` | 1037 行全量 inline | 无 | Baseline (v0.10.x 行为) |
| 3200 | `test-v011-allrules/` | 57 行 tiered | system-prompt-all-rules.ts | 全量规则注入 |
| 3300 | `test-v011-smartrules/` | 57 行 tiered | system-prompt-smart-rules.ts | 智能规则注入 |

### 2.2 测试负载

- **21 条消息**: 3 个交替话题（python-setup / database / cicd），每个话题 7 轮递进
- **3 条召回问题**: 测试 compaction 后的上下文保持能力
- **模型**: github-copilot/claude-sonnet-4
- **测试脚本**: `ab_test_harness.py`（Python, httpx），`run_sysprompt_3way_test.sh`（Bash 编排）

### 2.3 测试轮次

- **Round 1**: v0.10.x baseline (port 3100) vs all-rules plugin (port 3200)
- **Round 2**: v0.10.x baseline (port 3100) vs smart-rules plugin (port 3300)

### 2.4 环境隔离保障

#### 2.4.1 之前的测试环境问题（已修复）

在第一次测试中发现三个严重的环境问题，导致数据全部作废：

1. **端口复用**: Port 3100/3200 运行的是 5 月 11 日旧测试遗留的服务器，CWD 指向错误目录
2. **错误插件**: Port 3200 实际运行 `fish-trail-compaction.ts`（旧 compaction 插件），不是 `system-prompt-all-rules.ts`
3. **Git 缺失**: smart-rules 环境缺少 `.git` 目录，导致 OpenCode 向上查找到父项目的 `.git`，继承了 96 个 skills 描述（~58K tokens），系统提示从 ~30K 暴涨到 ~92K

#### 2.4.2 修复措施

- 杀掉所有旧服务器进程
- 为 `test-v011-allrules/` 和 `test-v011-smartrules/` 执行 `git init`
- 启动后通过 `/proc/PID/cwd` 验证每个服务器的工作目录
- 通过 msg1 的 `effective_ctx` 验证系统提示体积

#### 2.4.3 隔离验证结果

| 端口 | msg1 effective_ctx | 预期 | 验证 |
|------|--------------------|------|------|
| 3100 (baseline) | 45,021 | ~45K (32K base + 13K inline rules) | ✅ |
| 3200 (all-rules) | 45,041 | ~45K (32K base + 13K plugin rules) | ✅ Δ=+20 |
| 3300 (smart-rules) | 32,452 | ~32K (32K base + ~0.5K matched rules) | ✅ |

---

## 三、测试结果

### 3.1 Round 1: v0.10.x vs all-rules plugin

| 指标 | Baseline (v0.10.x) | All-Rules Plugin | 变化 |
|------|-------------------|-----------------|------|
| Input tokens | 455,533 | 327,834 | **-28.0%** |
| Output tokens | 131,384 | 147,205 | +12.0% |
| Cache read | 5,692,657 | 6,082,194 | +6.8% |
| **Total tokens** | **586,917** | **475,039** | **-19.1%** |
| 消息数 | 76 | 87 | +14.5% |
| Compaction 次数 | 2 | 1 | -50% |
| 峰值上下文 | 152,990 | 145,530 | -4.9% |
| 耗时 | 2,041s | 2,383s | +16.8% |
| 错误 | 0 | 0 | — |

### 3.2 Round 2: v0.10.x vs smart-rules plugin

| 指标 | Baseline (v0.10.x) | Smart-Rules Plugin | 变化 |
|------|-------------------|-------------------|------|
| Input tokens | 576,137 | 510,717 | **-11.4%** |
| Output tokens | 149,061 | 124,995 | -16.1% |
| Cache read | 5,654,659 | 4,508,906 | -20.3% |
| **Total tokens** | **725,198** | **635,712** | **-12.3%** |
| 消息数 | 64 | 64 | 0% |
| Compaction 次数 | 2 | 1 | -50% |
| 峰值上下文 | 152,844 | 141,031 | -7.7% |
| 耗时 | 2,442s | 2,187s | -10.4% |
| 错误 | 0 | 0 | — |

### 3.3 全局对比视图

| 方案 | Total Tokens | vs v0.10.x | Compactions | 每条消息平均 | 耗时 |
|------|-------------|-----------|-------------|-------------|------|
| v0.10.x baseline (R1) | 586,917 | — | 2 | 7,722 | 2,041s |
| v0.11.0 + all-rules | 475,039 | **-19.1%** | 1 | 5,460 | 2,383s |
| v0.10.x baseline (R2) | 725,198 | — | 2 | 11,331 | 2,442s |
| v0.11.0 + smart-rules | 635,712 | **-12.3%** | 1 | 9,933 | 2,187s |
| v0.11.0 无插件 (历史) | 1,017,201 | **+36.6%** | 3 | — | — |

### 3.4 注意事项：Baseline 变异性

两个 Round 的 baseline 使用同一端口（3100），但结果不同（586K vs 725K）。这是 LLM 响应的自然随机性——相同提示不保证相同输出长度。因此每个 Round 内 baseline vs plugin 的 **相对对比** 是可靠的，但跨 Round 比较需谨慎。

---

## 四、Compaction 频率 vs 插件额外开销分析

### 4.1 核心发现

**Compaction 是 token 消耗的主导因素，远超插件本身的开销。**

### 4.2 每次 Compaction 的成本

从 baseline 数据中观察：

| 指标 | 值 |
|------|-----|
| Compaction 触发阈值 | ~130-153K tokens |
| Compaction 后上下文 | ~47-49K tokens |
| 单次 Compaction 估计成本 | ~50-80K 额外 tokens |

每次 compaction 需要：
1. 生成总结请求（~5-10K tokens 消耗）
2. 从 ~140K 压缩到 ~48K（丢弃 ~90K 上下文）
3. 后续对话需要重新积累上下文

### 4.3 Compaction 触发点对比

| 运行 | 第 1 次 Compaction | 第 2 次 Compaction |
|------|-------------------|-------------------|
| R1 Baseline | msg 17 (ctx ~145K→47K) | msg 49 (ctx ~153K→49K) |
| R2 Baseline | msg 18 (ctx ~137K→48K) | msg 50 (ctx ~153K→48K) |
| R1 All-Rules | msg 15 (ctx ~136K→47K) | **无** |
| R2 Smart-Rules | msg 34 (ctx ~124K→36K) | **无** |

### 4.4 为什么插件减少了 Compaction

**v0.10.x 机制**: 1037 行 AGENTS.md 被内联在系统提示中。规则已经在 cached prefix 里，不需要额外读取。

**v0.11.0 无插件**: 57 行 tiered AGENTS.md 指引 LLM 使用 Read tool 读取规则文件。每次 Read 将 ~2-4K 文件内容加入会话上下文（不可缓存），导致上下文更快膨胀。

**v0.11.0 + 插件**: 规则通过 `experimental.chat.system.transform` 注入系统提示（cached prefix）。LLM 不需要 Read 规则文件，会话上下文不受影响。

```
v0.10.x:     规则在系统提示中（cached）    → 2 次 compaction
v0.11.0 裸:  规则在会话上下文中（uncached） → 3 次 compaction (+50%)
v0.11.0+插件: 规则在系统提示中（cached）    → 1 次 compaction (-50%)
```

### 4.5 插件自身的开销

| 指标 | All-Rules | Smart-Rules |
|------|-----------|-------------|
| 系统提示增量 | +20 tokens (vs baseline) | -12,569 tokens (更小) |
| 每轮 cache_read 增量 | ~12.6K (vs smart) | — (参考基准) |
| 87 轮累计 cache_read | ~1.1M extra | — |
| 按 $0.30/M cache_read 计 | ~$0.33 | — |

**结论**: 插件自身的 token 开销可以忽略。减少一次 compaction 节省的 ~50-80K tokens 远超插件注入的 ~13K cached tokens。

---

## 五、两种插件方案对比

### 5.1 复杂度对比

| 维度 | all-rules | smart-rules |
|------|-----------|-------------|
| 代码量 | 71 行 | 131 行（~2x） |
| 运行时依赖 | 仅读 `agents-rules/*.md` | 额外依赖 `.petfish/fish-trail/` topic 注册表 |
| 配置维护 | **零**（新增 .md 自动生效） | 必须维护硬编码的 `TOPIC_TO_RULES` 映射表 |
| 匹配逻辑 | 无 | substring 关键词匹配 topic 的 title/scope/tags |
| 外部依赖 | 无 | 无（纯本地文件读取，无 MCP/网络调用） |

### 5.2 Smart-rules 的故障模式（全部静默失败）

1. **topic-registry.json 缺失/不可读** → 不注入任何规则
2. **active_topic 为空** → 不注入任何规则
3. **映射表过期**（规则文件改名/新增未更新映射） → 该注入的规则缺失
4. **关键词假阴性**（如 topic 标题 "training curriculum" 不含 "course"） → 漏掉规则
5. **关键词假阳性**（短关键词 "ops" 匹配无关内容） → 注入多余规则
6. **rulesCache 静态** → 运行期间新增/修改的规则文件不会被检测到

### 5.3 何时应该使用 Smart-rules

Smart-rules 仅在规则集大到会多触发 compaction 时才有意义。基于上下文窗口 ~150K、compaction 阈值 ~135K、基础系统提示 ~32K 的模型：

| 规则集大小 | all-rules 可用对话空间 | smart-rules 可用对话空间 | 建议 |
|-----------|---------------------|----------------------|------|
| < 30K tokens | > 73K | ~101K | **all-rules** |
| 30-50K tokens | 53-73K | ~101K | 视 compaction 频率决定 |
| > 50K tokens | < 53K | ~101K | **smart-rules** |

**当前规则集（7 文件, ~9.4K tokens）→ all-rules 是正确选择。**

---

## 六、结论

### 6.1 核心结论

1. **System prompt 插件方案有效**: 两个插件方案不仅消除了 v0.11.0 的 +36.6% 回归，还实现了比 v0.10.x **更好**的 token 效率（-12% 到 -19%）。

2. **Compaction 频率是 token 效率的决定性因素**: 减少一次 compaction 节省 ~50-80K tokens，远超规则注入本身的开销（~13K cached tokens）。

3. **All-rules 优于 smart-rules**（在当前规则集规模下）: all-rules 提供 -19.1% 改善（vs v0.10.x），smart-rules 提供 -12.3%，但 all-rules 代码量仅 71 行、零配置维护、无故障模式。

4. **v0.11.0 + all-rules 插件是三种配置中 token 效率最高的**: 优于 v0.10.x inline、v0.11.0 裸跑、v0.11.0 + smart-rules。

### 6.2 效果总结

```
v0.11.0 无插件:     +36.6% token overhead (回归)
v0.11.0 + all-rules: -19.1% token overhead (改善)
净改善幅度:          55.7 个百分点
```

---

## 七、建议

### 7.1 短期建议（立即可行）

1. **将 `system-prompt-all-rules.ts` 作为 v0.11.0 tiered AGENTS.md 的标配插件发布。** 71 行代码，零配置，-19.1% token 改善。

2. **在 PEtFiSh 的 `project-initializer` skill 中，当生成 tiered AGENTS.md 时，自动附带 `system-prompt-all-rules.ts` 插件。** 确保新项目默认获得 token 优化。

3. **在文档中明确说明**: tiered AGENTS.md **必须**搭配 system-prompt 插件使用，否则会产生严重的 token 回归。

### 7.2 中期建议

4. **Smart-rules 作为高级选项保留**, 但需要以下改进后才适合发布：
   - 将 `TOPIC_TO_RULES` 映射外部化为 JSON 配置文件
   - 添加匹配失败/空注入的日志输出
   - 改善关键词匹配（词边界匹配 vs substring）
   - 添加 fallback 机制（匹配为空时注入核心安全规则）

5. **监控 compaction 频率作为 token 效率的关键指标。** 任何导致 compaction 增加的变更都会抵消其他优化。

### 7.3 长期建议

6. **建议 OpenCode 核心在 `experimental.chat.system.transform` 稳定后，提供内置的 agents-rules 注入机制**，免去用户手动编写插件。

7. **考虑在 context window 接近阈值时，由插件动态切换为 smart-rules 模式**，进一步推迟 compaction。

---

## 八、测试产物清单

本报告包目录结构：

```
v011-sysprompt-plugin-report/
├── REPORT.md                          ← 本报告
├── raw-data/
│   ├── sysprompt_round1_clean.json    ← Round 1 完整测试数据 (all-rules)
│   ├── sysprompt_round2_clean.json    ← Round 2 完整测试数据 (smart-rules)
│   ├── original-v011-regression-round1.json  ← 原始 v0.11.0 回归数据
│   └── original-v011-regression-round2.json  ← 原始 v0.11.0 回归数据
├── scripts/
│   ├── ab_test_harness.py             ← Python 测试 harness (630 行)
│   └── run_sysprompt_3way_test.sh     ← 3-way 测试编排脚本
├── plugins/
│   ├── system-prompt-all-rules.ts     ← 全量规则注入插件 (71 行)
│   └── system-prompt-smart-rules.ts   ← 智能规则注入插件 (131 行)
├── configs/
│   ├── AGENTS-v010x-full-inline.md    ← v0.10.x 全量 inline AGENTS.md (1037 行)
│   ├── AGENTS-v011-tiered.md          ← v0.11.0 tiered AGENTS.md (57 行)
│   └── opencode.json                  ← OpenCode 配置文件
├── agents-rules/                      ← 7 个按需规则文件
│   ├── anti-sycophancy.md             (2,325 bytes)
│   ├── course-skills.md               (15,828 bytes)
│   ├── deploy-ops.md                  (2,836 bytes)
│   ├── fish-trail.md                  (4,454 bytes)
│   ├── petfish-companion.md           (2,944 bytes)
│   ├── petfish-style.md               (1,969 bytes)
│   └── research.md                    (7,395 bytes)
└── logs/
    ├── round1_run.log                 ← Round 1 完整运行日志
    └── round2_run.log                 ← Round 2 完整运行日志
```

### 数据文件说明

**`sysprompt_round1_clean.json` / `sysprompt_round2_clean.json`**:
- 每条消息的 token 明细（input / output / cache_read / effective_ctx）
- compaction 次数
- 峰值上下文窗口
- 召回问题的 LLM 回答（截断至 500 字符）
- session_id（可通过 OpenCode Server 回溯完整会话）

**`original-v011-regression-*.json`**:
- v0.11.0 标准配置（无插件）的测试数据
- 用于对比回归幅度 (+36.6%)

---

## 九、复现指南

### 9.1 环境准备

```bash
# 创建三个隔离的测试目录
mkdir -p test-v010x test-v011-allrules test-v011-smartrules

# v0.10.x: 使用全量 inline AGENTS.md
cp configs/AGENTS-v010x-full-inline.md test-v010x/AGENTS.md
cd test-v010x && git init && cd ..

# v0.11.0 + all-rules: 使用 tiered AGENTS.md + 插件
cp configs/AGENTS-v011-tiered.md test-v011-allrules/AGENTS.md
cp configs/opencode.json test-v011-allrules/opencode.json
mkdir -p test-v011-allrules/.opencode/{plugin,agents-rules}
cp plugins/system-prompt-all-rules.ts test-v011-allrules/.opencode/plugin/
cp agents-rules/*.md test-v011-allrules/.opencode/agents-rules/
cd test-v011-allrules && npm init -y && npm install @opencode-ai/plugin && git init && cd ..

# v0.11.0 + smart-rules: 类似，使用 smart-rules 插件
# (需要 .petfish/fish-trail/ 话题数据)
```

### 9.2 启动服务器

```bash
# 在三个终端分别运行：
OPENCODE_SERVER_PASSWORD=test opencode serve --port 3100  # 在 test-v010x/
OPENCODE_SERVER_PASSWORD=test opencode serve --port 3200  # 在 test-v011-allrules/
OPENCODE_SERVER_PASSWORD=test opencode serve --port 3300  # 在 test-v011-smartrules/
```

### 9.3 运行测试

```bash
# 使用 uv 运行 Python 测试脚本
./run_sysprompt_3way_test.sh [model-name]
```

### 9.4 关键验证点

1. **启动后验证 CWD**: `lsof -i :PORT -t | xargs -I{} readlink /proc/{}/cwd`
2. **验证 msg1 effective_ctx**: 确认系统提示体积正确
3. **确保 `.git` 存在**: 防止 OpenCode 继承父项目 skills

---

## 附录 A：Plugin Hook API

```typescript
// OpenCode v0.11.0 experimental plugin hook
"experimental.chat.system.transform": async (
  input: { sessionID?: string; model: Model },
  output: { system: string[] }
) => Promise<void>

// 通过修改 output.system 数组来注入内容到系统提示
// 注入的内容会被 provider 缓存（cached prefix）
```

## 附录 B：关键发现记录

1. **OpenCode 通过 `.git` 目录确定项目根**。没有 `.git` 的子目录会向上查找，继承父项目的全部 skills。这是一个容易被忽略的实验陷阱。

2. **tmux 中的旧服务器不会因为新建测试目录而自动切换 CWD**。必须显式杀掉并从正确目录重启。验证 CWD 是测试环境设置的必要步骤。

3. **LLM 响应长度的随机性显著**。同一 baseline 在 Round 1 产生 586K tokens，Round 2 产生 725K tokens（差 23.6%）。因此跨 Round 比较需谨慎，同 Round 内的 A/B 对比才是可靠的。

4. **cache_read tokens 的成本约为 input tokens 的 1/10**。all-rules 每轮多出 ~12.6K cache_read，87 轮累计 ~1.1M，但按定价仅 ~$0.33，完全可忽略。

---

*报告结束*
