# 更新日志

完整的发布说明请参见 [GitHub Releases](https://github.com/kylecui/petfish.ai/releases)。

---

## v3.0 — Companion 全面改造

### v3.1.0

多agent编排（Phase 0-5）：task()并行验证（1.43x加速）、skill I/O contracts（3个pilot skills）、companion-gateway中的orchestration hint、dispatch tracking、结果聚合+冲突检测、autonomy levels（suggest/delegate/auto）。文档/网站更新。council-thinking references精简。

### v3.0.0

程序化companion-gateway.ts（6步执行通过TypeScript插件）。topic-context-filter修复（placeholder累积bug、effective topic detection、per-topic message archiving）。删除legacy installers（install.py统一入口）。skill-index.json（100 skills）。Market CLI。Web-grounding rules。13/13 registry合并到monorepo。102/102 agentskills.io合规。新增2个pack：drawio-radar-chart、typst-pdf-builder。

## v0.11 — Companion Gateway 增强：主动智能

### v0.11.7

文档更新补齐 —— 更新了 companion-gateway 文档（中英文）、README 和网站，以反映 6 步 Gateway 流程；发布了关于 Token 成本工程的博客文章。

### v0.11.6

Companion Gateway 6 步流程实现完成 —— 所有六个步骤（Mode Read、Topic Check、Failure Signal Detection、Skill Sense、Anti-Sycophancy Check、Proceed）均已集成并正式运行。

### v0.11.5

Rigor 阈值优化 —— 仅对 3 个以上步骤或涉及 3 个以上文件的任务执行 Momus 计划和评审；较简单的任务无需正式的计划文件，只需声明假设并在执行后进行验证即可。

### v0.11.4

Anti-Sycophancy Check（步骤 2.5）—— 优先确立评估标准（rubric-first），在同意之前强制搜索反方观点；主动性级别与 Rigor 模式绑定（off=仅限显式请求，on=包含隐式请求及断言）。

### v0.11.3

Rigor Mode —— project-mode.yaml 中的 `rigor: true` 增加了“先计划后评审”的纪律要求：复杂任务需编写正式的计划文件，执行前需通过 Momus 评审，并显式声明假设。当 `depth: thorough` 时强制开启。

### v0.11.2

Project Mode（步骤 0）—— 在 `.opencode/project-mode.yaml` 中增加 `depth`（urgent/balanced/thorough）和 `rigor`（on/off）配置轴；支持仅在当前会话中通过口头指令覆盖配置（不写入文件）。

### v0.11.1

Failure Signal Detection（步骤 1.5）—— 扫描上一轮 AI 助手的回复以寻找已知的失败模式（PDF/deploy/test/research/context），若相关 pack 未安装则推荐安装。通过 `catalog_query.py --check-failures` 实现。

### v0.11.0

Gateway 从 3 步扩展为 6 步 —— 在常驻的 Companion Gateway 流程中新增 Mode Read、Failure Signal Detection 和 Anti-Sycophancy Check。

---

## v0.10 — Research Pack 扩展：7 大领域

### v0.10.10

自动更新能力 —— `check_installed.py --check-updates` 查询 GitHub 最新 release 并对比已安装的 pack 版本；`catalog_query.py --upgrade` 显示适配操作系统的升级命令；Companion Gateway 现已在会话开始时检查更新；新增 `/petfish upgrade` 命令。同时修复了 `KNOWN_PACKS` 中缺失 `research` 别名的问题。

### v0.10.9

系统性触发关键词覆盖修复 —— 将所有 11 个 packs（约 74 个 skills）的 skill descriptions 与正文触发词对齐；在 `lint_skill.py` 中添加 `check_trigger_coverage()` lint 规则；将 trigger-coverage 检查集成到 `run_gate.py` 的决策逻辑中；在根目录 AGENTS.md 中添加 Description-Body 对齐纪律要求；扩展了 `catalog_query.py` 中的 research 触发词。关闭了 #91, #89, #88 问题。

### v0.10.7–v0.10.8

修复 research pack 集成 —— 完成了 research pack 的 9 触点检查清单（远程安装器、companion catalog、README、文档、网站）。沉淀了“一次审计，一次修复”的开发经验。

### v0.10.6

修复 4 个积压问题 —— 用 `qa_scan.py` 替换了重复的 QA 脚本（#80），为 suggest 命令添加 `--target` 以隔离 fixture（#73），补充了 JSONL/Markdown 设计文档并改善了 research pack 的用户体验（#79），通过 `--semantic` 标志添加了语义+关键词混合触发评分功能（#77）。关闭了 #80, #73, #79, #77 问题。

### v0.10.5

Adapter skills —— 增加了 4 个轻量级领域适配器（travel、conference、training、content-selection），通过特定领域的字段和检查清单增强主研究链路。目前该 pack 拥有 50 个 skills。

### v0.10.4

Risk-procurement 和 experience-event 研究领域 —— 新增 11 个 skills。目前该 pack 拥有 46 个 skills。

### v0.10.3

Learning 和 decision 研究领域 —— 新增 7 个 skills。目前该 pack 拥有 35 个 skills。

### v0.10.2

Planning 研究领域 —— 新增 6 个 skills。目前该 pack 拥有 28 个 skills。

### v0.10.1

消除 SKILL_builder 痕迹 —— 修复了 6 个文件中的 10 处过期引用；`catalog_query.py` 的 fallback 机制现在返回实际计数。关闭了 #87, #86 问题。

### v0.10.0

Product 研究领域 —— 新增 5 个 skills（user-research、competitor-analysis、opportunity-mapper、validation-planner、decision-brief）。目前该 pack 拥有 22 个 skills。

---

## v0.9 — Research Skill Pack

### v0.9.6

修复 smoke fixture 缺失 `adr/` 目录的问题（#85）；修复 trigger eval 运行器未捕获所有 `evals/trigger/*.json` 的问题（#84）。

### v0.9.5

修复 4 个 research skills 中的 SKILL.md schema 不匹配问题（#83, #82, #78）；修复 `repo_inventory.py` 包含 node_modules 的问题（#81）；修复所有 4 个安装器写入 skill/command/agent 数量为零的问题（#71）。关闭 5 个 issue。

### v0.9.4

Research pack 的 scientific 领域 —— 新增 7 个 skills（citation-auditor、literature-review、gap-finder、methodology-designer、experiment-planner、paper-writer、review-rebuttal）。目前该 pack 拥有 17 个 skills。

### v0.9.3

使 Research pack 可安装 —— 包括 pack-manifest、安装器注册、companion catalog 集成、更新 README 和 CHANGELOG。

### v0.9.2

Research pack QA 基础设施 —— seeded fixtures、E2E smoke tests（15 个 pytest）、trigger-eval 测试工具、本地 smoke 运行器以及 CI 门禁。关闭了 #74, #75, #76 问题。

### v0.9.1

将 research 别名添加到所有 4 个安装器和 companion catalog 中。

### v0.9.0

Research skill pack MVP —— 包含 10 个核心 skills、7 个 JSON schemas、9 个 Python 脚本以及 pack 基础设施。

---

## v0.8 — 多平台与 Agent 纪律

### v0.8.1

通用 agent 原则（跨仓库保护、网络重试）；完成了 ops AGENTS.md 模板；代码配置体验沉淀；为访问私有仓库添加 deployment-executor 参考资料。关闭了 #66, #67, #68, #69 问题。

### v0.8.0

多平台指令文件生成（#63）—— `detect_all_platforms()`，针对 Token 受限的平台进行内容压缩，添加 Claude Code hook 脚本，在全项目中强制执行 uv 优先的 Python 策略。

---

## v0.7 — 稳定性与 Pack 版本管理

### v0.7.2

修复 #57 的根本原因（使用 `grep -qF` 替换 `echo | grep`）；修复 #65（`topic_detector.py` 中缺失的 8 个 QA 双语术语）。

### v0.7.1

修复 `merge_agents_md` 中的 #57 旧名称识别问题；将 fish-trail 和 petfish-companion-skill 升级至 1.0.0（#64）；修复损坏的 AGENTS.md 标记；更新所有 4 个安装器脚本。

---

## v0.6 — Companion 故事线

### v0.6.4

双语网站和文档；归档过时的 v0.2 文档。

### v0.6.3

Companion 故事线重塑；修复 #57 `--force` 升级 bug。

### v0.6.2

修复 companion pack 的 skill 感知、安装器去重、catalog 降级处理以及通用平台检测问题。

### v0.6.1

修复 `topic_graph` 持久化、schema 对齐以及感知意图的 skill 识别问题。

### v0.6.0

Companion Gateway 提供始终在线的话题检查、3 级 skill 感知机制以及 debug 模式。

---

## v0.5 — Fish Trail 与仓库重命名

### v0.5.4

修复 `topic_graph` 缺失 `version` 字段以及 `topic_report` 中过时检测的问题。

### v0.5.3

添加 agent 升级指南和 Web 升级提示。

### v0.5.2

添加 v0.4.x → v0.5.x 升级指南。

### v0.5.1

预发布文档和测试套件更新。

### v0.5.0

将 `SKILL_builder` 重命名为 `petfish.ai`；将 context-router 重命名为 `fish-trail`；增加 31 个 MCP tools、安装器别名、状态目录迁移及话题路由脚本。

---

## v0.4 — Context Router 与会话管理

### v0.4.10–v0.4.12

增加感知话题的会话管理，新增 10 个 MCP tools，支持跨会话恢复、边界策略、活动查询、agent 归属与话题推荐。修复安装指导、触发词提取范围及 `deploy_dirs` 的误报问题。

### v0.4.5–v0.4.9

修复 MCP schema 问题、特定平台的重启提示、CJK 检测及触发器评估。

### v0.4.0

新增 context router pack，包含话题检测、污染评分、上下文隔离及 18 个 MCP tools。

---

## v0.3 — 质量与平台加固

- anti-sycophancy-calibration pack。
- 风格 v4 AI 生成痕迹（AI slop）检测。
- 发布纪律，可自动解析 latest release 标签。
- 修复 PowerShell 的 UTF-8 编码问题。
- 支持逗号分隔的多 pack 安装。

---

## v0.2 — Skill 生命周期管理

- **Phase 1**: 支持 8 平台的适配器和 companion skill，具备感知、装配与治理能力。
- **Phase 2**: 市场搜索、skill 创作及代码风格 linting（质量检查）。
- **Phase 3**: 仓库挖掘、安全审计与发布质量门禁（quality gate）。
- **Phase 4**: 描述优化、触发器评估及使用情况追踪。

---

## v0.1 — Skill 安装器

- 支持远程安装的多 pack 安装器。
- 包含 7 个 skill packs：`course`、`deploy`、`testdocs`、`petfish`、`ppt`、`init` 和 `companion`。
