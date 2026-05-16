# 其他 Pack 指南

本指南介绍了其余的 PEtFiSh skill packs，它们虽然不需要单独的完整指南，但在合适的上下文中仍然是强大的工具。

---

## PPT Pack

**别名:** `ppt` | **Skills:** 2 (`ppt-reader`, `ppt-writer`)

PPT pack 以编程方式读取、审计和生成 PowerPoint 演示文稿。它弥合了结构化 Markdown 内容与精美的幻灯片演示文稿之间的差距。

### 安装

=== "Windows PowerShell"

    ```powershell
    & ([scriptblock]::Create((irm https://raw.githubusercontent.com/kylecui/petfish.ai/master/remote-install.ps1))) -Pack ppt
    ```

=== "macOS / Linux / WSL"

    ```bash
    curl -fsSL https://raw.githubusercontent.com/kylecui/petfish.ai/master/remote-install.sh | bash -s -- --pack ppt
    ```

### 功能介绍

| Skill | 用途 |
|---|---|
| `ppt-reader` | 从现有的 PPTX 文件中提取幻灯片清单、备注、评论、媒体链接和结构 |
| `ppt-writer` | 从 Markdown/文档生成新的演示文稿，应用模板，运行视觉 QA |

### 何时使用

- 将课程内容或研究报告转换为演示幻灯片
- 审计现有演示文稿的一致性、敏感信息或结构问题
- 从结构化的 Markdown 笔记或会议纪要生成幻灯片演示文稿
- 统一整个演示文稿的幻灯片模板

### 工作流

```text
ppt-reader (audit existing deck)
    → produce rewrite brief
    → ppt-writer (generate new deck)
    → ppt-writer qa_deck (visual QA)
    → fix issues → re-verify
```

### 示例提示词

```text
Read this PPTX and give me a slide inventory with notes and structure.
```

```text
Generate a 15-slide deck from docs/02-content/module-01.md using our corporate template.
```

!!! tip "迭代 QA 循环"
    `ppt-writer` skill 使用 生成 → QA → 修复 → 重新验证 的循环。不要指望一次就能得到完美的演示文稿。QA 步骤会捕获布局问题、内容缺失和违反模板的情况。

---

## Calibrate Pack

**别名:** `calibrate` | **Skills:** 1 (`anti-sycophancy-calibration`)

Calibrate pack 可防止 AI 盲目赞同你。它将结构化的评估纪律注入到任何需要大量判断的任务中。

### 安装

=== "Windows PowerShell"

    ```powershell
    & ([scriptblock]::Create((irm https://raw.githubusercontent.com/kylecui/petfish.ai/master/remote-install.ps1))) -Pack calibrate
    ```

=== "macOS / Linux / WSL"

    ```bash
    curl -fsSL https://raw.githubusercontent.com/kylecui/petfish.ai/master/remote-install.sh | bash -s -- --pack calibrate
    ```

### 功能介绍

每当您要求进行审查、批评、评估或决策时，`anti-sycophancy-calibration` skill 就会激活。它强制 AI 做到：

1. **中和诱导性提示词** — 在评估之前剥离出您暗示的偏好答案
2. **先定义评分标准** — 在说某件事是否“好”之前，先确立“好”的标准是什么
3. **寻找反方论点** — 找出至少一个提案可能错误的原因
4. **将结论与置信度分离** — 既要说明它的想法，也要说明它的确定程度

### 何时使用

- 代码审查（“这个架构正确吗？”）
- 提案批评（“你觉得这个计划怎么样？”）
- 设计审查（“这个 UI 好吗？”）
- 战略决策（“我们应该继续这样做吗？”）
- 任何时候，当你发现自己希望 AI 验证你现有的信念时

### 示例提示词

```text
Review this architecture proposal and tell me if it's production-ready.
```

```text
Is my approach to error handling correct here?
```

!!! warning "它不会奉承你"
    此包的全部意义在于获得诚实的反馈。如果你问“这个好吗？”，而回答是“不好，原因如下”，这说明 skill 工作正常。不要因为不喜欢这个答案就禁用它。

### 组合模式

calibrate pack 与其他 skills 结合使用效果很好：

- `course-outline-design` + `calibrate` → 防止课程大纲仅仅是确认你最初的设想
- `research-report-writer` + `calibrate` → 强制报告承认反面证据
- `decision-recommendation` + `calibrate` → 确保建议不仅仅是附和你的偏好

---

## Petfish Style Pack

**别名:** `petfish` | **Skills:** 1 (`petfish-style-rewriter`)

Petfish Style pack 将文本重写为清晰、结构化、工程导向的语气。它去除了 AI 腔调（AI slop）、网络陈词滥调和修辞上的废话。

### 安装

=== "Windows PowerShell"

    ```powershell
    & ([scriptblock]::Create((irm https://raw.githubusercontent.com/kylecui/petfish.ai/master/remote-install.ps1))) -Pack petfish
    ```

=== "macOS / Linux / WSL"

    ```bash
    curl -fsSL https://raw.githubusercontent.com/kylecui/petfish.ai/master/remote-install.sh | bash -s -- --pack petfish
    ```

### 功能介绍

将中文或英文内容（技术文档、提案、专利、电子邮件、课程材料）重写为 Petfish 写作风格：

- **结构化** — 清晰的总-分-总组织结构
- **简明扼要** — 没有填充词，没有模棱两可的话，没有“值得注意的是”
- **基于证据** — 主张由数据而非修辞支撑
- **工程导向** — 问题驱动的分析，而非叙述性的废话

### 何时使用

- 润色技术文档
- 去除生成文本的 AI 味（删除“深入探讨”、“值得注意的是”、“总而言之”）
- 重写提案，使其更直接且更具可操作性
- 将冗长的学术写作转化为犀利的工程散文

### 示例提示词

```text
用我的语言习惯表达：[paste text]
```

```text
去AI味，按工程化风格重写这段：[paste text]
```

```text
Make this sound human but still professional: [paste text]
```

### 会被删除的内容

| AI 腔调模式 | 替换为 |
|---|---|
| "It's important to note that..." | （删除，或替换为直接陈述） |
| "Delving into the intricacies of..." | 直接陈述观点 |
| "In today's rapidly evolving landscape..." | （删除） |
| "This comprehensive guide will..." | （删除，直接开始指南） |
| 不必要的重申引言的结论 | （删除） |

---

## TestDocs Pack

**别名:** `testdocs` | **Skills:** 2 (`generate-test-cases`, `generate-usage-docs`)

TestDocs pack 根据实际代码库代码生成测试用例和使用文档，而不是通用的模板。

### 安装

=== "Windows PowerShell"

    ```powershell
    & ([scriptblock]::Create((irm https://raw.githubusercontent.com/kylecui/petfish.ai/master/remote-install.ps1))) -Pack testdocs
    ```

=== "macOS / Linux / WSL"

    ```bash
    curl -fsSL https://raw.githubusercontent.com/kylecui/petfish.ai/master/remote-install.sh | bash -s -- --pack testdocs
    ```

### 功能介绍

| Skill | 用途 |
|---|---|
| `generate-test-cases` | 从实际代码和设计文档生成测试矩阵（冒烟、回归、边界、负面测试） |
| `generate-usage-docs` | 从代码库生成 README、快速入门、API 文档、故障排除指南 |

### 何时使用

- 在实现一个功能并需要测试覆盖时
- 当入职培训文档缺失或过时时
- 当你需要从源码生成 API/CLI/SDK 文档时
- 当准备发布并需要进行覆盖率差距分析时

### 示例提示词

```text
Generate test cases for the authentication module. Include boundary and negative tests.
```

```text
Generate a Quick Start guide and API reference from the current codebase.
```

!!! tip "基于实际代码，而非通用模板"
    这些 skills 在生成输出之前会读取您的实际代码。测试用例引用真实的函数签名，文档引用真实的 CLI 标志。它们不是通用的模板 —— 它们是特定于项目的产物。

---

## Context Pack

**别名:** `context` | **Skills:** 1 (`fish-trail`) | **MCP Server:** `context-state`

Context pack 提供话题治理（topic governance）功能 —— 当您在同一会话中在不相关的任务之间切换时，它可以防止跨话题污染。

### 安装

=== "Windows PowerShell"

    ```powershell
    & ([scriptblock]::Create((irm https://raw.githubusercontent.com/kylecui/petfish.ai/master/remote-install.ps1))) -Pack context
    ```

=== "macOS / Linux / WSL"

    ```bash
    curl -fsSL https://raw.githubusercontent.com/kylecui/petfish.ai/master/remote-install.sh | bash -s -- --pack context
    ```

### 功能介绍

`fish-trail` skill 及其 `context-state` MCP server 维护一个话题图谱，该图谱跟踪您正在处理的内容，并检测上下文何时发生漂移或受到污染。

**核心能力：**

- **话题检测** — 对每条消息与活跃话题的关系进行分类
- **污染评分** — 量化跨话题污染的风险
- **上下文包** — 为每个话题构建隔离的上下文包
- **会话管理** — 跟踪哪些会话处理了哪些话题
- **话题路由** — 通过上下文防火墙将查询路由到最相关的话题

### 何时使用

- 在同一个 AI 会话中处理多个不相关的项目
- 上下文积累和漂移的长时间运行的会话
- 会话之间的交接（上下文包保留了状态）
- 当您注意到 AI 混淆了不同任务的细节时

### 工作原理（常驻运行）

安装后，fish-trail 将作为 Companion Gateway 的一部分自动运行：

1. **每条消息** → `topic_detect` 对关系进行分类（继续/派生/切换/合并/归档/重置）
2. **低风险 (0-30)** → 静默，不打断
3. **中风险 (31-60)** → 关于上下文继承的简短提示
4. **高风险 (61-100)** → 暂停并建议派生/切换/重置

### 示例交互

```text
User: "Let's switch to the billing feature now"
Agent: [topic_detect → switch detected, risk=72]
       "I detect a topic switch from 'auth-module' to 'billing-feature'.
        Suggesting a fork to preserve auth context separately.
        Should I fork, switch, or continue in the current topic?"
```

```text
User: "整理一下话题"
Agent: [loads fish-trail skill for deep governance]
       Shows topic graph, recommends archiving stale topics,
       and builds fresh context packages for active ones.
```

### 可用的 MCP Tools

`context-state` MCP server 暴露了 30 多个用于编程式话题管理的 tools：

| Tool 类别 | 示例 |
|---|---|
| 话题增删改查 | `topic_create`, `topic_update`, `topic_archive`, `topic_search` |
| 关系 | `topic_link`, `topic_unlink`, `topic_graph`, `topic_recommend` |
| 上下文 | `context_build`, `context_freeze`, `context_export` |
| 污染 | `contamination_score`, `contamination_explain` |
| 会话 | `session_bind`, `session_resume`, `session_query`, `session_agents` |
| 路由 | `topic_route`, `topic_detect`, `topic_report` |

!!! tip "最适合长会话"
    Context pack 在持续数小时或跨越多天的会话中大放异彩。对于一次性快速任务，这种开销不值得。但对于跨多个功能的持续开发工作，它可以防止导致 bug 的微妙的上下文渗透。

---

## Pack 比较矩阵

| Pack | Skills | 主要使用场景 | 投入成本 |
|---|---|---|---|
| `ppt` | 2 | 幻灯片生成和审计 | 中等 |
| `calibrate` | 1 | 诚实的评估和审查 | 低（常驻运行） |
| `petfish` | 1 | 写作风格强制执行 | 低 |
| `testdocs` | 2 | 从代码生成测试用例和文档 | 中等 |
| `context` | 1 + MCP | 话题隔离和治理 | 低（常驻运行） |

### 应该安装哪些？

- **所有人**都应该安装 `petfish`（写作质量）和 `calibrate`（诚实的反馈）
- **开发者**应该添加 `testdocs`（测试覆盖率）和 `context`（长会话）
- **演讲者**应该添加 `ppt`（幻灯片生成）
- **或者直接使用 profile**：`comprehensive` 会安装所有内容
