<p align="center">
  <img src="../../assets/petfish-logo.png" alt="胖鱼 PEtFiSh logo" width="360" />
</p>

# 胖鱼 PEtFiSh

**你的AI伙伴**

[English](../../README.md)

<p align="center">
  <img src="../../assets/petfish-icon-256.png" alt="胖鱼 PEtFiSh icon" width="128" />
</p>

---

## 胖鱼是什么

从项目第一行代码到最终交付，胖鱼始终相伴。不是你想起来才调用的工具集，是每一轮交互都参与的AI伙伴。

📖 **[文档站](https://docs.petfish.ai)** — 入门指南、使用教程、Pack参考、开发者文档

```
┌─────────────────────────────────────────────────────┐
│  ><(((^>  胖鱼 PEtFiSh v3.0                       │
│                                                     │
│  常伴  每一轮交互都在                                │
│  守护  感知缺口、守护上下文、阻断污染                │
│  可信  Lint + 审计 + 红线 = 验证出的信任             │
│  秉正  不迎合、标准不降格                            │
│                                                     │
│  /petfish — 你的常驻伙伴                             │
└─────────────────────────────────────────────────────┘
```

支持8个AI编程平台，一条命令完成安装。

---

## 快速开始

```bash
uv run https://raw.githubusercontent.com/kylecui/petfish.ai/master/install.py --pack init,companion --detect
```

装完输入 `/initproject`——胖鱼问你项目类型，自动装上匹配的能力包。

> 安装脚本自动获取最新稳定release，不用指定版本号。

---

## 四个承诺

### 常伴 — 每一轮交互都在

Companion Gateway在每条消息前**程序化执行**（v3.0+ 通过 companion-gateway.ts 插件，不再仅靠prompt指令）。不需要你主动调用。从`/initproject`那一刻起，胖鱼就是你工作流的一部分。

### 守护 — 在你掉坑之前拦住

三层感知模型：关键词白名单匹配已知领域 → 意图级缺口检测 → 无缺口静默通过。上下文污染超过60分？主动拦截。每个领域每session最多提醒一次，不打扰。

### 可信 — 信任是验证出来的

每个Skill都过质量门禁：Lint 100分制打分、安全审计0.0–1.0风险评分、四条红线命中即deny。TrustSkills引擎六维风险评估、五级动作裁决。信任不是宣称的，是审计出来的。

### 秉正 — 标准不因便利而降格

反迎合校准：先中性化问题再给结论，至少补一个反方。质量门禁不放水，红线命中即deny。推你往更高标准走。

---

## /petfish 命令

| 命令 | 说明 |
|------|------|
| `/petfish` | 查看已装skill状态 |
| `/petfish catalog` | 浏览全量技能目录 |
| `/petfish suggest` | 基于项目特征推荐skill |
| `/petfish install <alias>` | 获取安装命令 |
| `/petfish search <keyword>` | 跨市场搜索skill和MCP server |
| `/petfish create <name>` | 创建新skill |
| `/petfish mine <repo>` | 从仓库挖掘候选skill |
| `/petfish lint [path]` | 验证skill格式质量（100分制） |
| `/petfish audit <path>` | 安全审计（0.0-1.0风险评分） |
| `/petfish gate <path>` | 完整发布门禁 |
| `/petfish optimize <path>` | 分析并优化skill描述 |
| `/petfish eval <path>` | 测试触发准确率 |
| `/petfish stats` | 查看使用统计 |
| `/petfish upgrade` | 显示升级命令 |
| `/petfish detect` | 检测当前平台 |

---

## 4个核心包（每次安装必带）
> 核心包随 petfish.ai 仓库直接分发。

| 别名 | 定位 | 规模 |
|------|------|------|
| `companion` | 胖鱼本体——常伴核心，2个核心skill（fish-brain 鱼伴、fish-market 鱼市） | 2 skills, 1 cmd |
| `init` | 项目初始化向导 | 1 skill, 1 cmd |
| `petfish` | 工程写作风格套件 — 3 skills: `petfish-style-rewriter`、`de-ai-detector`、`style-extractor` | 3 skills |
| `toolchain` | Skill生命周期工具链——9个skill，从创作到上架 | 9 skills |

## 12个可选包（通过 petfish-market 获取）
> 可选包通过 [petfish-market](https://github.com/kylecui/petfish-market) 分发。安装命令自动解析，用户无感知。

| 别名 | 定位 | 规模 |
|------|------|------|
| `context` | 话题治理器——守护核心 | 1 skill, 31 MCP |
| `calibrate` | 判断校准与多视角对抗推理（fish-calibrate + council-thinking） | 2 skills |
| `trust` | Skill可信度治理——可信核心 | 1 skill |
| `course` | 课程开发全套 | 15 skills, 10 cmds, 8 agents |
| `deploy` | 部署与运维 | 7 skills |
| `testdocs` | 测试用例与文档 | 2 skills |
| `ppt` | PPT设计 | 2 skills |
| `research` | 研究工作台——科研、产品、规划等8个领域 | 54 skills |
| `reflect` | 结构化反思——捕获失败原因与纠正措施 | 1 skill |
| `drawio` | Draw.io雷达图生成器——精确顶点坐标计算 | 1 skill |
| `typst` | Typst PDF构建——Markdown转PDF，中文排版 | 1 skill |
| `style-governor` | 系列文档风格一致性治理——术语漂移检测 | 1 skill |

---

## 平台支持

| 平台 | Skills目录 | 指令文件 |
|------|-----------|----------|
| OpenCode | `.opencode/skills/` | `AGENTS.md` |
| Claude Code | `.claude/skills/` | `CLAUDE.md` |
| Codex | `.agents/skills/` | `AGENTS.md` |
| Cursor | `.cursor/skills/` | `.cursor/rules/*.mdc` |
| GitHub Copilot | `.github/skills/` | `copilot-instructions.md` |
| Windsurf | `.windsurf/skills/` | `.windsurfrules` |
| Antigravity | `.agents/skills/` | `AGENTS.md` + `GEMINI.md` |
| Universal | `.agents/skills/` | `AGENTS.md` |

用 `--detect` 自动检测平台，或 `--platform <name>` 手动指定。

---

## Online Companion（在线伙伴）

PEtFiSh 现在有 ChatGPT GPT 版本 —— 不需要本地安装，不依赖 OpenCode、Codex、Cursor 或任何本地 IDE/CLI。

### 运行模式

| 模式 | 说明 |
|------|------|
| Standalone | 纯 GPT 指令 + 知识库 |
| Gateway | 在线 API |
| Adapter | 可选本地执行（低优先级） |

### 能力范围

**能做：**
- 解释 PEtFiSh
- 推荐 pack 和 profile
- 设计 skill
- 渲染安装命令
- 做批判性 review
- 反迎合校准
- 风险分类

**不能做：**
- 读本地文件
- 跑本地测试
- 改仓库
- 调用本地 IDE/CLI
- commit/push/deploy（需要本地安装或 adapter）

### 快速开始

首次发布范围：P0 Standalone + P1 Gateway-only Actions。

详细文档：[docs/online-projects.md](online-projects.md)

### 专用配置

`review-online` profile 专门用于 ChatGPT Project 代码审查。

---

## 升级

运行 `/petfish upgrade` 查看适合当前OS的升级命令，或直接重跑安装命令加 `--force`：

```bash
uv run https://raw.githubusercontent.com/kylecui/petfish.ai/master/install.py --pack all --force
```

或者让AI帮你：

```
Upgrade PEtFiSh by following: https://raw.githubusercontent.com/kylecui/petfish.ai/master/docs/agent-upgrade.md
```

---

## 环境要求

- **`uv`** — 所有带外部依赖的Python skill、MCP server和脚本都通过uv管理虚拟环境。MCP server用 `uv run` 启动，独立脚本用PEP 723 inline metadata或pack级 `pyproject.toml` 声明依赖。项目中不使用 `pip install`。安装器在uv未安装时会发出警告。
- `python3` — 安装器中仅用于stdlib级JSON解析和指令文件翻译（无需虚拟环境）

---

## 更多文档

- [安装指南](petfish-install-prompt.md)
- [Companion Gateway 技术文档](companion-gateway.md)
- [网站](https://petfish.ai)

---

## 版本历史

### v3.0 — Companion全面改造

- **v3.0.0**: 11个用户问题系统性修复。companion-gateway.ts全量6步程序化插件（不再仅靠prompt）。topic-context-filter placeholder累积bug修复 + effective topic detection + per-topic message archiving。删除4个legacy installers（install.ps1/sh, remote-install.ps1/sh），install.py统一入口。skill-index.json（100 skills）+ market CLI + web-grounding rules。13/13 registry合并到monorepo + 2 pack迁移（drawio-radar-chart, typst-pdf-builder）。102/102 agentskills.io合规。多agent编排设计完成（Momus审查通过，Phase 0-5实现：task() spike验证 + skill I/O contracts + orchestration hint + dispatch tracking + result aggregation + autonomy levels）。

### v1.9 — 测试团队 issue 解决 + 交付链路修复

- **v1.9.5**: Pack 重命名 `anti-sycophancy-calibration-pack` → `judgment-calibration-pack`；新增 `council-thinking` skill（5+1 多视角对抗推理）；pack 现包含 2 个 skill（fish-calibrate + council-thinking）；别名 `calibrate` 不变；`legacy_names` 保留升级兼容性。
- **v1.9.4**: 修复已交付修复中残留的 3 个 bug — #234（`path.lower().parts` 每次调用都崩溃，Path 没有 `.lower()` 方法；改为遍历 `path.parts` 逐个小写化）、#235（`fix_docx_tables()` 漏掉了 index-0 处空表头的情况；增加检测+交换）、#207（PACK_RENAMES 清理放在 `load_registry` 中——仅内存态，从未持久化；移至 `save_registry`）。全部通过运行时测试验证。
- **v1.9.3**: 交付链路修复——所有可选包（doc-reader、testdocs、series-style-governor、trustskills-governance）现在从 monorepo 的 v1.9.2 提供而非过时的独立仓库引用。用户运行 `--pack all --force` 现在能拿到 #230–#237 的全部修复。
- **v1.9.2**: CI 转绿（363 个测试通过）+ 交付链路修复。doc-reader 加入 TRIGGERS（修复 `test_all_aliases_have_triggers`）；`合理` → `合理吗`（修复 calibrate 对非评价性消息如"变量命名是否合理"的误报）；`test_style_check` 期望 keys 按新指标更新。市场索引更新随后单独提交。
- **v1.9.1**: 修复 #241——`install.py` 检测 legacy 全局 skill 目录（`petfish-companion`、`marketplace-connector`、`context-router-skill`）并在升级时告警。`agent-upgrade.md` 增加 Codex 故障排查说明：Codex 旧线程中的 skill 条目是平台级缓存问题——升级后开新线程即可。
- **v1.9.0**: 测试团队 issue 全部解决 + CI 转绿。汇总 v1.8.1 的 #230–#237 修复以及 #207（install.py PACK_RENAMES stale registry 清理）。CI 回归修复：`合理` 触发词收窄为 `合理吗` 防止误报；`doc-reader` 加入 ALIAS_MAP（修复 profile 校验）；`test_style_check.py` 期望 keys 按新指标更新。

### v1.8 — 契约驱动 Companion

- **v1.8.2**: 修复 #207——`install.py` 通过 PACK_RENAMES 映射清理重命名 pack 的 stale registry 条目（`series-style-governor` → `series-style-governor-pack` 重复条目在下次 `load_registry()` 时自动移除）。
- **v1.8.1**: Bugfix 发布——测试团队报的 8 个 issue。#230 `gateway_classifiers.py` 改为自包含（无外部依赖）；#231 fish-trail 测试断言更新适配 v2 feature-flag 默认值；#232 CI 测试路径修复（`fish-style` → `petfish-style-rewriter`）；#233 trustskills 安装说明指向 GitHub URL；#234 `project_inventory.py` 边界感知路径匹配（不再出现 qa-testdocs 污染）；#235 `doc-reader` 新增 `fix_docx_tables()` 后处理器修复 markitdown 表格 bug；#236 `normalize_terms` 正则增加 `\s` 排除（修复 `aliases:` 被当作 term key）；#237 `audit_series_style` 对未实现维度报告"Not checked"而非"Pass"。
- **v1.8.0**: 契约驱动 Gateway 原子 + 可观测性 + 阅读笔记记忆。5 个 Gateway 步骤形式化为机制原子，带显式契约、golden/known-bad fixtures 和确定性验证器（42/42 检查 PASS）。Gateway Trace：always-on 结构化 trace 输出 + verify_trace.py。Reading-Notes（Step 2.6）：agent 在阅读代码/文档/配置时记录结构化笔记，带陈旧检测（file_mtime + file_size stat 比对）。实施纪律（最小代码：先读后写 + 六问检查）写入 AGENTS.md。修复循环发现并补齐了缺失的 calibrate TRIGGERS（"好吗"/"合理"/"你觉得"）。Companion pack 版本：1.1.0 → 1.3.0。

### v1.7 — 安装加固

- **v1.7.0**: 安装加固 + online-gpt + gateway 修复。

### v1.6 — 在线伙伴

- **v1.6.0**: Online Companion GPT。

### v1.5 — 统一安装器

- **v1.5.2**: 修复 #224：remote 模式下的 `--pack all` 和 `--list`。
- **v1.5.1**: 修复 #223：doc-reader-skill 市场注册。
- **v1.5.0**: 统一 Python 安装器（PEP 723 inline script，`uv run` 远程执行，内置镜像回退）。

### v1.4 — 市场优先分发

- **v1.4.6**: 本地安装器市场优先下载 — install.sh和install.ps1均支持查询petfish-market自动获取本地缺失的可选包，支持镜像回退和--offline标志。修复#193：bash安装器中社区包状态消息重定向到stderr。
- **v1.4.5**: 全部9个可选包解耦到独立GitHub仓库（Phase 3+4）。course、research、testdocs、ppt、deploy加入v1.4.3/v1.4.4已解耦的4个单skill包。市场索引更新；所有可选包独立版本管理。`packs/optional/`保留在monorepo作为本地开发暂存区。
- **v1.4.4**: 修复EXTRACT_DIR回归——从find命令中排除community-staging（#193后续）。Phase 2解耦：fish-reflection、anti-sycophancy、trustskills-governance迁入独立仓库。
- **v1.4.3**: 修复安装社区包时COMMUNITY_STAGING未绑定变量（#193）。Phase 1试点：petfish-style-skill解耦到kylecui/petfish-pack-petfish-style。
- **v1.4.2**: 文档同步——README + REPO-LANDSCAPE.md依赖表更新。
- **v1.4.1**: 远程安装器完成market-first解析接入。`resolve_pack()` / `Resolve-PackName()` 对可选包查询petfish-market `index.json`，缓存元数据（`repo`/`ref`/`path`/`version`）供下载阶段使用。核心包始终从petfish.ai主tarball解析。Bash安装器新增外部仓库下载支持（`MARKET_PACK_DIRS`）——当可选包的市场条目指向petfish.ai以外的仓库时，自动单独下载。市场不可达时静默回退到硬编码ALIASES。
- **v1.4.0**: packs/重构为`core/`（4个核心包：init、companion、petfish、toolchain）和`optional/`（9个可选包：course、testdocs、deploy、ppt、calibrate、context、trust、research、reflect）。可选包通过petfish-market分发，安装器自动解析。新增工具链skill `skill-publish`连接质量门禁PASS与市场发布。远程安装器增加市场查询钩子（`query_market_index()` / `Query-MarketIndex`）。`catalog_query.py`新增`--install <alias>`标志和市场感知。`marketplace_search.py`优先petfish-market源。petfish-market新增`registry/official/`（9个官方pack条目）和`index.json` v2。

### v1.3 — 模块解耦：Companion + Toolchain 拆分

- **v1.3.0**: 从`companion`中拆出8个工具链skill，组成新的`toolchain` pack（`petfish-toolchain-skill`）；`petfish-companion`重命名为`fish-brain`（鱼伴），`marketplace-connector`重命名为`fish-market`（鱼市）；`companion` pack现在只包含2个核心skill；总pack数12→13，总skill数不变（96个）。

### v0.11 — Companion Gateway增强：主动智能

- **v0.11.7**: 文档补齐——更新companion-gateway文档（中英文）、README、网站以反映6步Gateway流程；发布Token Cost Engineering博客文章。
- **v0.11.6**: Companion Gateway 6步实现完成——全部六步（Mode Read、Topic Check、Failure Signal Detection、Skill Sense、Anti-Sycophancy Check、Proceed）集成并运行。
- **v0.11.5**: Rigor阈值细化——仅3+步骤或3+文件的任务需要Momus计划+评审；简单任务保留假设声明和事后验证，跳过正式计划文件。
- **v0.11.4**: 反迎合检查（Step 2.5）——rubric-first评估，同意前强制寻找反论；主动性等级与Rigor绑定（off=仅显式提问，on=隐式+技术断言）。
- **v0.11.3**: Rigor模式——project-mode.yaml中`rigor: true`增加计划-评审纪律：复杂任务需正式计划文件、Momus评审后才实施、显式声明假设。`depth: thorough`时强制开启。
- **v0.11.2**: 项目模式（Step 0）——`.opencode/project-mode.yaml`中的`depth`（urgent/balanced/thorough）和`rigor`（on/off）两轴；session内口头切换不写文件。
- **v0.11.1**: 失败信号检测（Step 1.5）——扫描上轮assistant回复匹配已知失败模式（PDF/部署/测试/研究/上下文），未安装时推荐对应pack。通过`catalog_query.py --check-failures`实现。
- **v0.11.0**: Gateway从3步扩展到6步——在always-on Companion Gateway流程中新增Mode Read、Failure Signal Detection和Anti-Sycophancy Check。

### v0.10 — Research Pack扩展：7个领域

- **v0.10.10**: 自动更新能力——`check_installed.py --check-updates`查询GitHub最新release并比对已装pack版本；`catalog_query.py --upgrade`显示当前OS的升级命令；Gateway在session启动时检查更新；新增`/petfish upgrade`命令。同时修复`KNOWN_PACKS`中缺失的`research`别名。
- **v0.10.9**: 系统性触发词覆盖修复——全部11个pack约74个skill的description与body触发词对齐；`lint_skill.py`新增`check_trigger_coverage()`规则；`run_gate.py`集成trigger-coverage到决策逻辑；根AGENTS.md新增Description-Body对齐纪律；`catalog_query.py`扩展research触发词。关闭 #91, #89, #88。
- **v0.10.7–v0.10.8**: 修复research pack集成——完成9触点检查清单（远程安装器、companion catalog、README、文档、网站）。沉淀"一次全审一次全修"开发经验。
- **v0.10.6**: 修复4个积压issue——qa_scan.py替换重复QA脚本(#80)、suggest添加`--target`(#73)、JSONL/Markdown设计文档化(#79)、混合语义+关键词触发评分`--semantic`(#77)。关闭 #80, #73, #79, #77。
- **v0.10.5**: Adapter skills——4个轻量领域适配器（travel/conference/training/content-selection），通过领域特定字段和清单增强主研究链。Pack达到50个skill。
- **v0.10.4**: 风险采购与活动体验研究领域——11个新skill，trigger eval，smoke test覆盖。Pack达到46个skill。
- **v0.10.3**: 学习与决策研究领域——7个新skill，trigger eval，smoke test覆盖。Pack达到35个skill。
- **v0.10.2**: 规划研究领域——6个新skill，trigger eval，smoke test覆盖。Pack达到28个skill。
- **v0.10.1**: SKILL_builder残留清理——6个文件中修复10处过时引用；catalog_query.py fallback返回实际计数。关闭 #87, #86。
- **v0.10.0**: 产品研究领域——5个新skill，trigger eval，smoke test覆盖。Pack达到22个skill。

### v0.9 — Research Skill Pack

- **v0.9.6**: 修复smoke fixture缺失adr/目录(#85)；修复trigger eval runner glob路径(#84)。
- **v0.9.5**: 修复4个research skill的SKILL.md schema不匹配(#83, #82, #78)；修复repo_inventory.py包含node_modules(#81)；修复全部4个安装器写入零计数(#71)。关闭5个issue。
- **v0.9.4**: Research pack科学研究领域——7个新skill（citation-auditor到review-rebuttal），trigger eval，smoke test。Pack达到17个skill。
- **v0.9.3**: Research pack可安装——pack-manifest、安装器注册、companion catalog集成、README和CHANGELOG。
- **v0.9.2**: Research pack QA基础设施——seed fixtures、E2E smoke tests（15个pytest）、trigger-eval harness、本地smoke runner、CI gates。关闭 #74, #75, #76。
- **v0.9.1**: Research别名注册到全部4个安装器和companion catalog。
- **v0.9.0**: Research skill pack MVP——10个核心skill、7个JSON schema、9个Python脚本、pack基础设施。

### v0.8 — 多平台生成 & Agent纪律

- **v0.8.1**: 通用agent纪律（跨仓库保护、网络重试）；完整ops项目模板（11段）；code项目经验沉淀（Development Gotchas, Architecture Decisions）；部署skill参考文档（私有仓库访问、本地补丁管理）。关闭 #66, #67, #68, #69。
- **v0.8.0**: 多平台指令文件生成（#63）——`detect_all_platforms()`、token受限平台内容压缩、Claude Code hook脚本、uv优先Python策略。

### v0.7 — 稳定性 & Pack版本化

- **v0.7.2**: 修复#57根因（`grep -qF`替换`echo | grep`）；修复#65（topic_detector.py缺失8条QA双语术语）。
- **v0.7.1**: 修复#57 legacy名称识别；fish-trail和companion升级至1.0.0（#64）；修复AGENTS.md标记损坏；更新全部4个安装脚本。

### v0.6 — Companion Gateway

- **v0.6.4**: 网站和文档双语化，归档过时v0.2文档
- **v0.6.3**: 伙伴叙事重塑，修复#57 --force升级bug
- **v0.6.2**: 修复companion pack技能感知、安装器去重、catalog回退、universal平台检测
- **v0.6.1**: 修复topic_graph持久化、validate schema对齐、意图感知技能推荐
- **v0.6.0**: Companion Gateway——每条消息自动话题检测 + 三层能力感知 + 开发者调试模式

### v0.5 — Fish Trail

- **v0.5.0–v0.5.4**: 仓库重命名petfish.ai，fish-trail pack（31个MCP工具），话题路由/报告/验证脚本

### v0.4 — 上下文治理

- **v0.4.0–v0.4.12**: 上下文治理pack，话题感知会话管理（31个MCP工具），bug修复

### v0.3 — 质量加固

- 反迎合校准pack，AI腔检测，发布纪律，PowerShell UTF-8修复

### v0.2 — Skill生命周期

- 8平台适配器，跨市场搜索，安全审计，发布质量门禁

### v0.1 — Skill安装器

- 多pack安装器，7个skill pack

---

> **胖鱼 PEtFiSh** — 你的AI伙伴。从init到交付，胖鱼始终相伴。
