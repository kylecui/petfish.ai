# PEtFiSh 项目开发纪律

本节定义项目级开发规则，所有agent和人工操作必须遵守。

---

## Companion Gateway（每条消息强制执行）

> 胖鱼是你的AI伙伴。伙伴的意思是：每一轮交互都在。

**以下流程在处理用户消息之前强制执行，无例外。**

### Step 1: Topic Check（话题归属）

调用MCP tool `topic_detect`，传入用户消息文本和当前session_id。

```yaml
tool: topic_detect
input:
  text: "<用户消息>"
  session_id: "<当前session ID>"
  current_topic: "<活跃topic ID>"
```

根据返回的 `risk_level` 执行：

| risk_level | 行为 |
|-----------|------|
| low (0-30) | 静默继续 |
| medium (31-60) | 回复开头一行说明上下文继承范围 |
| high (61-100) | 暂停正常处理，向用户说明话题变更风险，建议fork/switch/reset |

**MCP不可用时**：不阻塞，静默跳过。每次会话最多提示一次"⚠ fish-trail MCP未连接"。

### Step 2: Skill Sense（能力缺口检测）

对用户消息进行能力缺口判断。采用三层检测模型：

#### Tier 1: 白名单匹配（已知pack领域）

基于 `catalog_query.py` TRIGGERS 关键词匹配：

| 领域关键词 | 对应Pack |
|-----------|---------|
| deploy, Docker, CI/CD, 健康检查, 回滚 | deploy |
| 课程, 教学, 大纲, 提纲, 实验 | course |
| PPT, 幻灯片, 演示 | ppt |
| 测试用例, 测试文档, test case | testdocs |
| 润色, 说人话, 去AI味, 写作风格 | petfish |
| 评审, 评价, 批判, review, calibration | calibrate |
| topic, 话题, 上下文, 污染, 隔离 | context |
| 研究, 调研, 文献, literature, research, 证据, evidence, 综述, 论文 | research |

命中 + 未安装 + 本session未推荐 → 在回复末尾附带一行推荐。

#### Tier 2: 意图感知（未知领域缺口检测）

当Tier 1未命中时，判断用户消息是否暗示了一个**当前环境无法满足的能力需求**。

**判断标准 — 同时满足以下全部条件才触发：**

1. **需要外部集成或专项工具**：用户的请求需要调用外部服务（API、邮件、消息推送、天气、翻译服务等）或专用工具（图表生成、数据库管理、特定格式转换等）
2. **Agent原生能力不覆盖**：请求超出了代码编写、文件操作、git、搜索、通用推理等agent内置能力
3. **当前已安装skill不覆盖**：检查 `installed-packs.json`，已安装的skill无法满足该需求

**触发时行为：**
- 推断最相关的关键词
- 建议：`💡 检测到能力缺口 — 可以运行 /petfish search <关键词> 看看是否有匹配的skill或MCP server。`

**排除条件（以下情况不触发Tier 2）：**
- 普通编码任务（写函数、调bug、重构、加注释）
- 项目管理任务（git操作、文件整理、目录操作）
- 通用问答（解释概念、分析代码、给建议）
- 已安装skill覆盖的领域
- 用户在进行对话管理（"继续"、"停"、"换个方向"）

**示例：**
- "帮我查一下这个API的rate limit" → 不触发（agent原生能力可以搜索文档）
- "帮我发个邮件通知团队" → 触发（需要邮件服务集成）
- "翻译这段话成日语" → 不触发（agent原生能力覆盖翻译）
- "帮我画一个甘特图" → 触发（需要图表生成工具）
- "监控这个服务的uptime" → 触发（需要监控集成）
- "明天天气如何" → 触发（需要天气API）

#### Tier 3: 无缺口（静默通过）

Tier 1和Tier 2均未命中 → 不输出任何推荐。

#### 节制规则

- 每个领域/关键词每session最多推荐1次
- 不确定是否为缺口时，倾向于不触发（宁静默不打扰）
- Tier 2判断置信度低于70%时不触发

### Step 3: Proceed（正常处理）

完成 Step 1-2 后，进入正常任务处理流程。

### 交互后更新

当本次交互产生实质性成果时，调用 `topic_update` 更新topic状态。

---

### Debug Mode（开发者模式）

当 `.petfish/fish-trail/config.yaml` 中设置 `debug: true` 时，**每次check的过程和决断必须可见**，无论风险等级高低。

```yaml
# .petfish/fish-trail/config.yaml
companion_gateway:
  debug: true   # true=每次显示check过程, false=仅medium/high时显示
```

Debug模式输出格式（置于回复最前）：

```
🐟 [gateway] topic: relation=continue, risk=12 (low), confidence=0.92 → silent
🐟 [gateway] skill: no gap → pass
```

```
🐟 [gateway] topic: relation=switch, risk=67 (high), confidence=0.85 → suggest fork
🐟 [gateway] skill: gap=deploy (detected "Docker部署") → recommend
```

```
🐟 [gateway] topic: relation=continue, risk=5 (low), confidence=0.95 → silent
🐟 [gateway] skill: tier2 gap detected (intent="发邮件通知", need="邮件服务集成") → suggest search "email"
```

**Debug模式规则：**
- `debug: true`（默认）：always显示，开发者可观察每轮决策
- `debug: false`：仅medium/high risk或有推荐时才输出
- 配置文件不存在时：默认 `debug: false`

---

## Release纪律（强制）

本项目使用GitHub Release作为用户安装的稳定来源。install脚本默认自动获取latest release tag。

### 发布流程

1. **所有开发在`dev`分支进行**
2. **功能完成后**：创建PR从`dev`合并到`master`
3. **PR合并到master后，必须立即创建GitHub Release**：
   - Tag格式：`vX.Y.Z`（语义化版本号）
   - 使用`gh release create vX.Y.Z --target master --title "vX.Y.Z - 简要描述" --notes "变更说明"`
   - Release notes必须包含本次变更的要点
4. **不允许**：master上有未打tag的合并。每次合并master = 一次release。

### 版本号规则

- **Major (X)**：破坏性变更（pack结构、install脚本接口变化）
- **Minor (Y)**：新功能（新pack、新skill、新平台支持）
- **Patch (Z)**：修复（bug fix、文档修正、小优化）

### Install脚本与Release的关系

- 用户通过固定URL下载install脚本（指向master分支）
- install脚本启动后，**自动查询GitHub API获取latest release tag**
- 实际下载的pack内容来自release tag对应的代码快照
- 如果API查询失败，fallback到master分支
- 用户可通过`--branch`参数覆盖自动检测

### 禁止事项

- 禁止合并到master后不打release tag
- 禁止使用非语义化的tag名称
- 禁止删除已发布的release（除非有安全漏洞）
- 禁止在release中包含未经测试的破坏性变更

---

## Python环境策略（强制）

本项目使用 **uv** 作为唯一的Python虚拟环境管理工具。所有skill脚本、MCP server、第三方工具的Python环境一律通过uv管理。

### 规则

- MCP server启动命令使用 `["uv", "run", "python", "server.py"]`，不使用裸 `python3`
- 有外部依赖的独立脚本使用 PEP 723 inline metadata（`# /// script`）或所属pack的 `pyproject.toml`
- 安装器中的 `python3 -c` 内联调用仅限stdlib，不需要uv（无外部依赖=无虚拟环境需求）
- 项目中不存在 `pip install`，不使用 `pip` 管理依赖
- 安装器在uv未安装时发出警告

### 禁止事项

- 禁止使用 `pip install` 安装依赖
- 禁止在MCP server配置中使用裸 `python3` 启动有外部依赖的脚本
- 禁止绕过uv直接创建或激活venv

---

## 跨仓库与网络操作纪律（强制）

### 跨仓库保护

- 不操作其它仓库的内容（即使有权限），只能通过issues反馈问题和建议
- 发现上游仓库的bug或改进需求，提issue，不直接修改上游代码
- 本地补丁必须有对应的upstream issue记录

### 网络故障重试

- 网络出现问题或可能是网络问题导致的中断（SSH无法连接、apt install失败、docker pull超时、git clone/push失败），不要急于改变当前方案，至少重试两次再行调整
- 瞬态网络故障是常态，不构成方案变更的理由

---

<!-- BEGIN pack: opencode-course-skills-pack -->
# 课程开发项目AGENTS.md

本项目使用OpenCode进行课程开发、课程治理与课程交付。

本文件定义的是**项目级全局规则**。它不替代 `.opencode/skills/*/SKILL.md`，而是为所有技能和后续代理会话提供统一边界、默认流程、目录规范、质量门禁与交付要求。

---

## 1. 项目目标

本项目面向课程产品的全生命周期工作，包括但不限于：

-课程规划与项目治理
-课程提纲设计与模块拆分
-课程正文编写与重构
-实验、演示与作业设计
-学员资料与教师资料制作
-参考文档阅读与提炼
-质量保证、质量控制与发布决策
-课程方法论与复用技能沉淀

本项目的核心目标不是“尽快写出很多文档”，而是形成：

1. 结构清晰、可追踪的课程项目资产
2. 面向交付的课程内容，而非零散草稿
3. 可复用的方法论、模板、审阅标准与skills
4. 清晰区分学员版、教师版、QA/QC版和正式发布版

---

## 2. 优先级与判断原则

处理任何任务时，默认遵循以下优先级：

1. **项目边界优先**：先判断任务属于项目治理、提纲、正文、实验、资料、QA、QC还是发布。
2. **结构一致性优先**：先保持目录、命名、版本与资料边界清晰，再追求局部文字优化。
3. **提纲先于正文**：涉及大范围内容调整时，先更新或确认提纲，再批量改正文。
4. **QA先于QC**：先做问题发现与审阅，再做闭环判定与发布建议。
5. **正式交付与参考资料分离**：`references/` 不是交付物，`release/` 才是稳定对外交付物。
6. **学员资料与教师资料严格分离**：避免答案、讲师提示、内部批注泄露到学员材料。
7. **保留可追踪性**：重大调整必须留下计划、变更记录、审阅记录或QC结论。

---

## 3. 项目资料分层

本项目默认采用以下目录语义。若实际目录存在偏差，应优先向此规范收敛。

### 3.1核心目录

- `docs/00-project/`：项目治理材料
- `docs/01-outline/`：课程顶层提纲、模块图、课时分配
- `docs/02-content/`：课程正文
- `docs/03-labs/`：实验、演示、作业与环境说明
- `docs/04-learner-pack/`：学员资料
- `docs/05-instructor-pack/`：教师资料
- `docs/06-qa/`：质量保证过程材料
- `docs/07-qc/`：质量控制结论与发布建议
- `assets/`：图片、drawio、表格、静态资源
- `references/`：外部与内部参考资料
- `release/`：阶段性交付与正式发布版本
- `archive/`：归档与废弃内容

### 3.2目录语义要求

- `docs/00-project/` 不放课程正文。
- `docs/01-outline/` 不放完整讲稿。
- `docs/02-content/` 不混入QA批注或发布决策。
- `docs/03-labs/` 中的学员手册与教师答案必须分离。
- `docs/04-learner-pack/` 中不能出现内部审阅痕迹、答案、讲师提示。
- `docs/05-instructor-pack/` 可以包含讲解提示、答案索引、课堂风险提示。
- `docs/06-qa/` 强调“发现问题、记录问题、分类问题”。
- `docs/07-qc/` 强调“问题是否关闭、是否允许发布、是否降级发布”。
- `references/` 中的材料不得直接视为正式课程内容；必须经过提炼、重写或适配后再进入 `docs/`。
- `release/` 中只放稳定版本，不放临时草稿。

详细目录规范见：`COURSE-PROJECT-STRUCTURE-STANDARD.md`

---

## 4. 命名与文件规则

### 4.1命名规则

默认使用以下规则：

-目录与文件名优先使用小写 `kebab-case`
-有顺序的内容使用两位数字前缀
-一个文件只承载一个主主题
-尽量避免 `final`、`new`、`new2`、`最新版` 这类无信息量命名
- QA/QC文件建议显式带轮次或日期

推荐示例：

- `docs/01-outline/course-overview.md`
- `docs/02-content/01-module-01/01-lesson-01.md`
- `docs/03-labs/01-lab-01/learner-guide.md`
- `docs/05-instructor-pack/instructor-guide.md`
- `docs/06-qa/qa-review-round-01.md`
- `docs/07-qc/qc-report-2026-04-16.md`

### 4.2文件内容规则

- Markdown优先作为中间工作格式与审阅格式。
-对PDF、DOCX、图片、网页等参考材料的提炼结果，应沉淀为Markdown审阅记录或课程正文，而不是长期停留在“看过了”的状态。
-课程正文中不要残留“待补充”“后面再写”“这里可能有问题”这类内部工作痕迹；这类内容应留在QA/QC文件中。
-表格、图示、课程图、实验拓扑尽量把原始编辑文件保存在 `assets/` 下可维护的位置，而不是只保留导出图片。

---

## 5. 技能使用原则

本项目优先通过skills组织工作，而不是每次从零开始描述流程。

### 5.1默认技能路由

-涉及项目统筹、任务分流、跨多个环节的复杂任务：`course-development-orchestrator`
-涉及目录初始化、结构审计、文件归位、命名规范：`course-directory-structure`
-涉及Markdown风格、模板、课程正文排版：`markdown-course-writing`
-涉及drawio、结构图、流程图、课程架构图：`drawio-course-diagrams`
-涉及PDF、Markdown、DOC/DOCX、图片等参考资料研读：`reference-document-review`
-涉及里程碑、计划、变更、风险、实施路线：`development-plan-governance`
-涉及课程总纲、模块划分、课时分配：`course-outline-design`
-涉及课程内容展开、章节重写、案例补强：`course-content-authoring`
-涉及实验目标、实验步骤、环境说明、验收标准：`course-lab-design`
-涉及学员讲义、手册、复习资料：`learner-materials`
-涉及教师讲义、答题参考、讲解节奏与授课提醒：`instructor-reference-materials`
-涉及问题发现、审阅清单、严重性分类：`course-quality-assurance`
-涉及整改闭环、发布建议、质量控制报告：`course-quality-control-reporting`
-涉及可沉淀的方法、模板、技能化路线：`course-methodology-playbook`
-涉及从公共仓库或参考资料中发现skill范式：`skill-reference-discovery`

### 5.2使用顺序

默认顺序如下：

1. 先由 `course-development-orchestrator` 判断任务所在阶段
2. 再由专项skill执行具体工作
3. 涉及发布前检查时，必须经过QA与QC两步
4. 涉及目录或大规模整理时，优先用 `course-directory-structure` 做初始化或审计

### 5.3 Commands与Agents

本项目除了skills以外，还可以通过 `.opencode/commands/` 与 `.opencode/agents/` 提高执行效率。

- `commands` 用于高频工作流入口，例如项目初始化、结构审计、提纲生成、QA/QC审阅
- `agents` 用于角色化分工，例如目录治理、提纲设计、正文编写、实验设计、QA、QC

推荐做法：

-直接执行高频工作流时，优先使用 `/course-init`、`/course-audit`、`/course-outline`、`/course-qa`、`/course-qc` 等命令
-需要明确角色分工时，优先使用 `curriculum-build`、`outline-architect`、`content-crafter`、`lab-designer`、`qa-auditor`、`qc-gatekeeper` 等代理
- commands与agents都不替代skills；它们应建立在skills和本 `AGENTS.md` 的规则之上
---

## 6. 默认工作流

### 6.1新项目初始化

新课程项目默认按以下顺序推进：

1. 明确项目目标、对象、范围、交付物
2. 建立标准目录结构
3. 写 `docs/00-project/project-brief.md`
4. 写 `docs/00-project/milestone-plan.md`
5. 写 `docs/01-outline/` 下的总纲、模块图、课时分配
6. 再开始课程正文、实验、学员资料与教师资料
7. 完成后进入QA
8. QA闭环后生成QC报告
9. 满足发布条件后形成 `release/` 版本

### 6.2现有项目接管

若接手的是已有项目，默认按以下顺序：

1. 先做结构审计，而不是直接新建文件覆盖原有资产
2. 判断当前材料分别属于project/outline/content/labs/learner/instructor/qa/qc/release/archive哪一层
3. 形成整理建议
4. 再做目录归位、拆分、重命名
5. 补齐缺失层级
6. 再启动内容增补或重写

### 6.3大范围修改

以下情况视为大范围修改，必须先有计划或提纲更新：

-调整课程总体目标、对象、定位
-大规模改变模块划分或课时分配
-重构多个章节
-增加或删除整块实验内容
-学员版和教师版重新分层
-发布目标、交付边界、验收口径发生变化

遇到上述情况，应先更新：

- `docs/00-project/change-log.md`
-必要时更新 `milestone-plan.md`
-必要时更新 `docs/01-outline/` 中的相关文件

---

## 7. 审阅与修改规则

### 7.1可以直接修改的情况

以下情况可以直接处理：

-纯排版与格式统一
-明显错字、病句、标题层级问题
-明确归属且不会引起歧义的文件归位
-不改变对外语义的轻量补充说明

### 7.2先出建议再修改的情况

以下情况应先给出方案、影响面或整理建议：

-大规模重命名
-跨目录搬迁文件
-合并或拆分多个章节
-学员版与教师版的内容边界调整
-把参考资料改写为正式课程内容
-删除疑似仍在使用的文件
-调整实验验收口径或评分标准

### 7.3保守处理原则

-不确定归属时，先产出整理建议，不贸然移动。
-不确定是否已发布时，不直接覆盖 `release/`。
-不确定是否仍被引用时，不直接删除旧文件。
-不确定是草稿还是准正式版时，先保留并标记，再整理。

---

## 8. 质量门禁

本项目采用分阶段质量门禁。没有通过前一门禁，不建议跳过直接发布。

### 8.1项目门禁

至少应具备：

-明确的项目目标
-明确的交付物边界
-基本里程碑或阶段计划
-变更记录入口

### 8.2提纲门禁

至少应具备：

-课程对象与先修要求
-模块划分
-课时分配
-课程目标与实验目标映射
-学员收益表述

### 8.3内容门禁

至少应具备：

-正文章节结构稳定
-概念定义一致
-章节之间不明显重复或冲突
-图表、案例、示例与正文对应
-没有明显内部批注残留

### 8.4实验门禁

至少应具备：

-实验目标
-环境说明
-操作步骤
-验收标准
-常见失败点或教师提示
-学员版与答案版分离

### 8.5资料包门禁

-学员包不得泄露教师提示、答案、内部审阅内容
-教师包应包含讲解提示、答案索引、时间控制建议与风险提示
-资料包中的链接、图片、引用文件应可解析

### 8.6 QA门禁

QA至少要回答：

-发现了哪些问题
-问题属于哪一类
-严重性如何
-哪些问题必须在发布前关闭

### 8.7 QC门禁

QC至少要回答：

-哪些问题已关闭
-哪些问题接受风险并延期处理
-当前版本是否允许发布
-若允许发布，是正式发布、受限发布还是内部试运行

---

## 9. 发布规则

### 9.1何时进入 `release/`

只有在下列条件满足后，才应形成或更新 `release/` 内容：

-已完成至少一轮QA
-已形成QC结论
-交付边界明确
-学员版与教师版材料边界明确
-对外材料不含明显内部痕迹

### 9.2发布目录要求

发布版本建议带版本号或日期，例如：

- `release/v0.1/`
- `release/v1.0/`
- `release/2026-04-internal-preview/`

### 9.3不应发布的内容

以下内容不应直接进入发布版本：

-仅供内部审阅的QA记录
-未脱敏的教师答案
-未整理的参考资料原件
-仍处于争议中的章节草稿
-仅为占位而存在的空文件

---

## 10. 参考资料处理规则

### 10.1参考资料不是最终交付

参考资料可来自：

- PDF
- Markdown
- DOC/DOCX
-图片
-网页
-历史对话整理稿
-外部高星skill仓库

但这些材料只能作为输入，不直接等于课程交付物。

### 10.2提炼要求

对参考资料的处理，默认要求至少输出以下一种成果：

-审阅摘要
-差距分析
-课程提纲修订建议
-内容重写建议
-实验设计输入
- QA问题单
-可沉淀为skill的流程、模板或gotchas

### 10.3外部skill参考规则

可以参考外部高质量skill仓库，但不得机械复制；应结合本项目的课程开发目标、命名规范、目录结构与质量门禁进行改造。

---

## 11. 目录初始化、审计与整理

本项目默认使用 `course-directory-structure` skill处理目录问题。

### 11.1初始化

新项目可优先运行：

```bash
uv run .opencode/skills/course-directory-structure/scripts/bootstrap_course_tree.py --root . --mode full --with-placeholders
```

### 11.2结构审计

对现有项目，优先运行：

```bash
uv run .opencode/skills/course-directory-structure/scripts/check_course_tree.py --root .
```

### 11.3整理原则

-先审计、后整理
-先出建议、后批量移动
-先拆分混合内容，再进行发布分层
-尽量减少破坏性重命名
-对可能被引用的路径保持谨慎

---

## 12. QA与QC的角色边界

### 12.1 QA的角色

QA负责：

-找问题
-记问题
-分类问题
-评估严重性
-提醒风险

QA不负责直接替代所有整改动作，也不负责单方面宣布可以发布。

### 12.2 QC的角色

QC负责：

-判断问题处理状态
-判断风险接受与否
-判断是否允许发布
-形成对项目管理和交付负责的结论性报告

### 12.3 QA/QC文档输出

- QA输出进入 `docs/06-qa/`
- QC输出进入 `docs/07-qc/`
-若生成汇总报告，默认采用Markdown，必要时再导出其他格式

---

## 13. 常见错误与禁止事项

### 13.1常见错误

-直接开始写正文，却没有项目brief和提纲
-学员版、教师版和QA批注混在一个文件里
-参考资料收集很多，但没有完成提炼
- QA做了很多意见，却没有对应QC结论
-反复生成“最终版”，但没有真正的版本管理与发布目录
-目录命名以日期或作者为主，而不是以课程结构为主

### 13.2禁止事项

-禁止把教师答案或内部提示直接混入学员资料
-禁止把 `references/` 直接当成 `release/`
-禁止在没有审计与建议的情况下大规模乱移文件
-禁止把QA记录伪装成正式课程正文
-禁止用含糊命名覆盖已有正式版本
-禁止在没有QC结论时把草稿宣称为正式发布版

---

## 14. 任务完成的最小交付标准

任何较完整的课程开发任务，至少应交付以下之一：

-已更新的目标文件
-审阅意见与问题列表
-结构整理建议
-计划与变更记录
- QA记录
- QC结论
-可复用模板或方法说明

不能只停留在“我已阅读”“建议如下”而没有可落地成果文件，除非任务本身明确只要求口头分析。

---

## 15. 推荐维护文件

建议在项目中长期维护以下文件：

- `docs/00-project/project-brief.md`
- `docs/00-project/milestone-plan.md`
- `docs/00-project/change-log.md`
- `docs/00-project/risk-register.md`
- `docs/01-outline/course-overview.md`
- `docs/01-outline/syllabus.md`
- `docs/06-qa/qa-checklist.md`
- `docs/07-qc/release-decision.md`

---

## 16. 当信息不足时的默认动作

如果信息不足，默认按以下方式处理：

1. 先识别当前任务处于哪个阶段
2. 先检查现有目录与已有文件，而不是凭空重建一切
3. 优先形成整理建议或差距分析
4. 对高影响修改先更新计划或提纲
5. 对发布相关任务，优先要求QA/QC证据链完整

---

## 17. 与本项目配套的关键文件

- `README.md`
- `COURSE-PROJECT-STRUCTURE-STANDARD.md`
- `HISTORY-TO-SKILLS-ROADMAP.md`
- `.opencode/skills/*/SKILL.md`

在发生冲突时，遵循以下解释顺序：

1. 本 `AGENTS.md`
2. 与当前任务直接相关的专项 `SKILL.md`
3. 对应skill的 `references/` 与 `assets/`
4. 其他说明文档

---

## 18. 一句话原则

先分层，后写作；先提纲，后正文；先QA，后QC；先结论可追踪，再进入发布。
<!-- END pack: opencode-course-skills-pack -->

<!-- BEGIN pack: repo-deploy-ops-skill-pack -->
# Repo Deployment & Operations Rules

本项目包含一套用于 **repo部署、验证、运维、回滚** 的OpenCode skills。

## 工作原则

-当用户要求“读取repo/GitHub项目并部署到指定主机”时，优先走完整链路：
  1. `repo-runtime-discovery`
  2. `target-host-readiness`
  3. `deployment-executor`
  4. `deployment-verifier`
  5. 如需持续管理，再使用 `service-operations`
  6. 如遇异常，再使用 `incident-rollback`

-如果用户给的是宽泛任务，例如：
  - “帮我把这个仓库部署到10.0.0.5”
  - “把这个GitHub repo跑起来并验收”
  - “把这个服务上线后帮我持续运维”

  优先启用 `repo-service-lifecycle` 作为总控技能。

## 必须遵守

-先分析repo与目标主机，再选择部署方式。
-不得在未形成最小部署计划前直接执行高风险变更。
-不操作其它仓库的内容（即使有权限），只能通过issues反馈问题和建议。
-网络出现问题或可能是网络问题导致的中断（SSH无法连接、apt install失败、docker pull超时），不要急于改变当前方案，至少重试两次再行调整。
-涉及覆盖、替换、重启、删除、迁移时，必须先说明：
  -本次动作影响范围
  -回滚入口
  -验证办法
-部署完成后必须给出至少一份验证结果：
  -健康检查
  -功能smoke test
  -日志核验
  -端口/进程/页面/API结果
-任何长期运维动作都要记录版本、时间、路径、端口、依赖、观察点。

## 输出偏好

当任务涉及部署或运维时，默认输出以下结构：

1. **识别结果**
2. **部署计划**
3. **执行结果**
4. **验证结果**
5. **回滚点**
6. **后续运维建议**

## 懒加载参考文件

只在需要时读取skill中的 `references/*.md` 与 `assets/*` 文件，不要一次性全部加载。
<!-- END pack: repo-deploy-ops-skill-pack -->

<!-- BEGIN pack: petfish-style-skill -->
# AGENTS.md

## Project Writing Policy

When the user asks to rewrite, polish, humanize, formalize, simplify, or make text closer to Petfish's writing style, use the local skill:

- `.opencode/skills/petfish-style-rewriter/SKILL.md`

Default mode is `strict` when the user says:

-用我的语言习惯表达
-按我的风格写
-说人话
-去AI味
-让我们润色一下

## Priority

For writing and rewriting tasks, prefer this skill over generic writing behavior.

## Default Output Expectations

- Clear structure
- Problem-driven analysis
- Concise language
- Evidence-based claims
- No rhetorical exaggeration
- No internet-style slogans
- No unnecessary conclusion
- Chinese-English mixed technical terms must be compact: use `Webhook挂载`, `Git提交`, `API接口`, not `Webhook挂载`, `Git提交`, `API接口`

## Important Distinction

Thinking can be exploratory, but final writing must be structured. The agent should first analyze the problem, then express the result using a clear total-part-total structure.

## Suggested User Prompts

-用我的语言习惯表达：...
-让我们润色一下：...
-说人话：...
-按petfish风格重写：...
-去掉AI味并保持工程化表达：...
<!-- END pack: petfish-style-skill -->

<!-- BEGIN pack: petfish-companion-skill -->
# PEtFiSh Companion Rules

本项目已安装胖鱼PEtFiSh伙伴skill。

## 感知规则

在对话过程中，如果用户的需求涉及以下领域，但对应skill pack尚未安装，应主动提示：

| 领域 | 对应Pack | 安装命令 |
|------|---------|---------|
| 部署/运维/Docker | deploy | `/petfish install deploy` |
| 课程/教学/大纲 | course | `/petfish install course` |
| PPT/幻灯片 | ppt | `/petfish install ppt` |
| 测试用例/文档 | testdocs | `/petfish install testdocs` |
| 写作风格/润色 | petfish | `/petfish install petfish` |
| 评审/评价/批判/校准/反迎合 | calibrate | `/petfish install calibrate` |
| 话题治理/上下文污染/topic管理 | context | `/petfish install context` |

当用户需要创建新skill、搜索外部skill、或验证skill质量时，使用companion内置的skill-author、marketplace-connector、skill-lint。

每次会话对同一pack最多主动推荐1次。

## 可用命令

- `/petfish` — 查看当前skill状态
- `/petfish catalog` — 浏览全量技能目录
- `/petfish search <keyword>` — 跨市场搜索skill和MCP server
- `/petfish suggest` — 基于项目特征推荐skill
- `/petfish install <alias>` — 获取安装命令
- `/petfish detect` — 检测当前平台
- `/petfish create <name>` — 创建新skill
- `/petfish lint [path]` — 验证skill质量
- `/petfish mine <repo>` — 从仓库挖掘候选skill
- `/petfish audit <path>` — skill安全审计
- `/petfish gate <path>` — 运行发布门禁（lint+security→决策）
- `/petfish optimize <path>` — 分析并优化skill描述
- `/petfish eval <path>` — 测试skill触发准确率
- `/petfish stats` — 查看skill使用统计

## 行为边界

- 不自动安装skill，只推荐并提供命令
- 不修改用户项目文件
- 用户拒绝后本次会话不再重复推荐
<!-- END pack: petfish-companion-skill -->

<!-- BEGIN pack: anti-sycophancy-calibration-pack -->
# Anti-Sycophancy Calibration Pack

本pack提供一个用于反迎合决策校准的prompt skill，帮助Agent在评审、方案设计、代码审查、写作反馈等判断型任务中减少顺着用户说的倾向。

## 何时启用

- 用户要求评审、评价、批判、review、critique、feedback、judgment、decision、evaluation、calibration
- 用户在问“对吗？/right?/是不是?/你同意吗?/is this correct?”这类确认性问题
- 用户需要方案评估、可行性分析、code review、架构判断、论文或提案反馈

## 行为规则

- 先中性化问题，再给结论；不要直接顺着用户预设表态
- 先给评分维度，再做判断；至少补一个反方或替代方案
- 结论与置信度必须分开表达；证据不足时要明确降级
- 不把skill用成“杠精模式”；该同意时同意，该保留时保留，该反对时反对
- 简单事实查询、翻译、排版、机械编辑默认不启用，除非用户明确要求 judgment或critique

## 组合示例

- `course-outline-design + anti-sycophancy-calibration`：避免课程大纲只顺着最初设想扩写
- `code-review + anti-sycophancy-calibration`：避免审查只给礼貌性正反馈
- `petfish-style-rewriter + anti-sycophancy-calibration`：在润色同时指出论证漏洞和边界条件
- `strategy-writer + anti-sycophancy-calibration`：把支持理由、反对理由、替代路线拆开表达
<!-- END pack: anti-sycophancy-calibration-pack -->

<!-- BEGIN pack: fish-trail -->
# Fish Trail — 话题治理器

本pack为项目提供上下文治理能力，降低跨话题污染风险。

## Always-On行为（每次交互自动执行）

### 交互前检查

每次收到用户消息时，调用MCP tool `topic_detect`判断当前消息与活跃topic的关系。若有可用的session_id（如OpenCode session ID），应在调用时传入`session_id`参数以启用会话追踪。根据返回的风险等级执行对应行为：

| 风险等级 | 行为 |
|---------|------|
| low (0-30) | 静默继续，不做任何提示 |
| medium (31-60) | 在回复开头用一行简要说明上下文继承范围，例如："当前继续topic「X」，继承上下文包含Y和Z。" |
| high (61-100) | 主动向用户说明话题变更风险，建议处理策略（fork/switch/reset），加载fish-trail skill执行深度治理 |

### 交互后更新

当本次交互产生实质性成果（代码变更、文档输出、决策结论等）时，调用`topic_update`更新当前topic的summary和status。

### 会话管理

fish-trail支持会话级追踪。会话（session）绑定外部平台的session ID或自动推断创建。

- **会话绑定**：在会话开始时调用`session_bind`绑定外部session_id和当前topic
- **事件追踪**：`topic_detect`传入`session_id`时，自动记录话题切换事件到session timeline
- **会话查询**：通过`session_list`按topic、时间、状态过滤，回答"昨天我们做了什么？"
- **会话恢复**：通过`session_resume`查找与特定topic关联的最近session，支持跨会话上下文继承

会话数据存储在`.petfish/fish-trail/sessions/`，与topic数据独立管理。

### 话题关系类型

检测到的关系类型决定上下文处理策略：

- **continue**：完全继承当前上下文
- **fork**：从当前topic分叉，继承部分上下文，创建子topic
- **switch**：切换到已有topic，加载该topic的Context Package
- **merge**：合并两个topic（需用户确认）
- **archive**：归档当前topic，冻结上下文
- **reset**：清空上下文，建立干净包
- **bridge**：两个topic间建立桥接，只继承交叉部分（需用户确认）

对merge、archive、bridge三种类型，检测置信度较低时必须提示用户确认，不得自动执行。

### 会话边界自动管理

fish-trail自动管理会话边界：

- `topic_detect`检测到archive或reset信号时，自动关闭关联session
- `session_bind`时自动清理不活跃超过24小时的session
- 使用`session_close`显式关闭session并附带summary
- `session_resume`返回resume context（session summary + timeline digest），支持跨会话上下文继承
- 新增`session_timeline`查看session时间线摘要
- 使用`session_query`按时间范围、topic、agent查询活动（回答"昨天我们做了什么？"）
- 使用`session_agents`查看agent-topic归属关系（哪个agent处理了哪个topic）
- 使用`topic_recommend`从topic图谱推荐关联topic

### MCP不可用时的降级行为

当context-state MCP server未启动、连接失败或调用超时时：

- 不报错，不阻塞正常工作
- 在回复中附带一行提示："⚠ fish-trail MCP未连接，话题治理未激活。"
- 跳过所有topic_detect和topic_update调用
- 每次会话最多提示一次，避免重复干扰

## 深度治理触发条件

以下情况自动加载`.opencode/skills/fish-trail/SKILL.md`执行完整5步工作流：

- topic_detect返回风险等级high
- 用户主动要求话题管理（"整理一下话题"、"切换到X"、"把这两个话题合并"等）
- 用户使用fish-trail相关关键词（topic、话题、上下文、污染、继承、隔离等）
<!-- END pack: fish-trail -->
