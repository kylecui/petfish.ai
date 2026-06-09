# 胖鱼 PEtFiSh — 管好你的AI Skill

你用Cursor写了一套`.cursorrules`，又在Claude Code里维护一份`CLAUDE.md`，OpenCode那边还有`AGENTS.md`。三套规则，内容差不多，但格式、路径、配置文件全不一样。

改了一处，另外两处忘了同步。AI在不同平台表现不一致，你花时间排查，发现是规则没对齐。

再往深想：

- 你写的这些skill，触发准确率到底多少？
- 里面有没有`subprocess.call(shell=True)`这种安全隐患？
- 哪些skill写了之后其实从来没被触发过？

这些问题在skill数量少的时候不严重。一旦团队有十几二十个skill在用，碎片化、无治理、无追踪三个问题同时出现。

胖鱼就是干这个的。

---

## 它做什么

胖鱼把AI的能力单元抽象为Skill。一个Skill不只是一段提示词——它有结构、有脚本、有元数据、有验证逻辑。

三件核心的事：

1. **一套skill，8个平台装**：写一次`SKILL.md`，自动翻译成Cursor的`.mdc`、Claude Code的`CLAUDE.md`、Copilot的`copilot-instructions.md`等格式，安装到对应路径。支持OpenCode、Claude Code、Codex、Cursor、Copilot、Windsurf、Antigravity、Universal。

2. **全生命周期管理**：发现（mine）→ 创建（author）→ 格式检查（lint）→ 安全审计（audit）→ 发布门禁（gate）→ 描述优化（optimize）→ 触发评测（eval）→ 使用追踪（track）。

3. **质量门禁**：lint打分（100分制）→ 安全审计（0.0-1.0风险分）→ quality gate给出PASS/CONDITIONAL/FAIL。跟代码CI一个思路。

---

## 13个Skill Pack（4个核心 + 9个可选）

> 核心pack（init、companion、petfish、toolchain）随petfish.ai分发。可选pack通过petfish-market获取。

| Alias | 做什么 | Skills |
|---|---|---:|
| `init` | 项目初始化向导 | 1 |
| `companion` | 胖鱼本体——10个skill生命周期管理工具 | 10 |
| `course` | 课程开发（提纲、正文、实验、QA/QC） | 15 |
| `deploy` | 部署与运维 | 7 |
| `testdocs` | 测试用例与文档生成 | 2 |
| `petfish` | 工程写作风格——让AI说人话 | 1 |
| `ppt` | PPT设计 | 2 |
| `trust` | skill可信度治理引擎 | 1 |
| `calibrate` | 反迎合决策校准 | 1 |
| `context` | 话题治理与上下文隔离 | 1 |
| `research` | 研究工作台——七大领域，证据驱动 | 50 |

安装时传入`--detect`，胖鱼自动识别你用的是哪个AI平台，把skill放到正确的目录。

---

## 10个内置Skill

`companion` pack内置10个管理类skill，覆盖skill从发现到追踪的全过程：

| Skill | 干什么 |
|---|---|
| **petfish-companion** | 总控调度——动态读取所有pack，路由`/petfish`命令 |
| **marketplace-connector** | 跨6个来源搜索skill（胖鱼仓库、SkillKit、Smithery、Glama、anthropics/skills、GitHub） |
| **skill-author** | 生成符合规范的skill脚手架 |
| **skill-lint** | 100分制格式检查，40+条规则 |
| **repo-skill-miner** | 分析GitHub仓库，提取可skill化的模块 |
| **skill-security-auditor** | 静态安全分析，输出0.0-1.0风险评分 |
| **quality-gate** | 编排lint+audit，给出发布决策 |
| **skill-description-optimizer** | 分析skill描述的触发准确率和歧义度 |
| **skill-trigger-evaluator** | 用测试集跑precision/recall |
| **skill-usage-tracker** | 记录使用频率和反馈评分 |

---

## 质量门禁

```
skill目录
  ├─ Lint ── Score ≥ 80? → 继续
  ├─ Security Audit ── Risk ≤ 0.5? 无CRITICAL? → 继续
  ├─ Metadata ── name/version/description有效? → 继续
  └─ Decision ── PASS / CONDITIONAL / FAIL
```

lint按error(-10)、warn(-5)、info(-1)从100分往下扣。security audit按finding权重（info=0, low=0.1, medium=0.3, high=0.6, critical=1.0）算风险分。两个结果喂给quality gate做最终判定。

---

## trustskills治理引擎

胖鱼内置的security auditor做静态模式匹配，快但浅。trustskills是另一层——按可执行行为分析：

- **6个风险维度**：shell(0.25)、network(0.25)、file_write(0.15)、sensitive_data(0.15)、script_risk(0.10)、persistence(0.10)
- **5级治理动作**：allow → allow_with_ask → sandbox_required → manual_review_required → deny
- **4条红线**：subprocess+network combo、敏感路径读写、sudo without approval、subprocess+os combo

红线是硬拒绝，不走分数阈值。命中即deny。

---

## 上下文感知

胖鱼不只被动等你调用。它会"听"对话。你开始聊部署但没装deploy pack，它提醒一次。不多不少，每个pack每次会话最多提醒一次。

---

## 安装

```bash
uv run https://raw.githubusercontent.com/kylecui/petfish.ai/master/install.py --pack init,companion
```

> 安装脚本自动获取最新稳定release版本，无需手动指定版本号。

装完输入`/initproject`。胖鱼问你项目类型，自动装上匹配的skill pack。

---

## `/petfish`命令

| 命令 | 说明 |
|---|---|
| `/petfish` | 查看已装skill状态 |
| `/petfish catalog` | 浏览全量技能目录 |
| `/petfish suggest` | 基于项目结构推荐skill |
| `/petfish search <kw>` | 跨市场搜索skill |
| `/petfish mine <repo>` | 从仓库挖掘候选skill |
| `/petfish create <name>` | 创建新skill |
| `/petfish lint [path]` | 质量打分 |
| `/petfish audit <path>` | 安全审计 |
| `/petfish gate <path>` | 完整发布门禁 |
| `/petfish optimize <path>` | 优化skill描述 |
| `/petfish eval <path>` | 测试触发准确率 |
| `/petfish stats` | 使用统计 |
| `/petfish detect` | 检测当前AI平台 |
| `/petfish install <alias>` | 获取安装命令 |

---

## 为什么用它

不是因为它"智能""先进"。是因为：

- **跨平台同步是真痛点**——你不想手动维护8份规则
- **skill需要CI**——跟代码一样，没检查过的指令不该进生产
- **治理需要自动化**——人审skill不scale，规则引擎可以
- **追踪才能改进**——不知道触发率和使用率，优化无从谈起

胖鱼（PEtFiSh）谐音"朋友"。它不是又一个提示词集合，是帮你管skill的工具链。

---

**GitHub**：https://github.com/kylecui/petfish.ai

---

*><(((^> 胖鱼 PEtFiSh — AI Worker's Companion*
