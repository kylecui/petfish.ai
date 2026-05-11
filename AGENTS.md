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

## Todo创建纪律（强制）

Todo系统追踪的是agent可自主完成的工作，不是用户决策或外部事件。

### 规则

- **禁止**创建包含外部阻塞条件的pending todo（如"用户确认后提交"、"审批后部署"、"等待反馈后修改"）
- **正确做法**：agent完成自身工作后立即标记completed，在回复文本中说明等待用户输入
- 仅在用户明确触发后再创建后续todo，不提前创建无法自主完成的todo

### 原因

自动化todo continuation hook会持续轮询未完成todo并触发agent继续工作。若todo含有agent无法满足的前置条件，将导致无限循环。此规则源自实际事故：一个"用户确认后提交"的todo触发了200+次无效continuation directive。

### 示例

```
# 错误 — 会导致无限循环
- [pending] 部署到生产环境
- [pending] 用户确认后提交代码    ← agent无法自主完成

# 正确 — 所有todo都可自主完成
- [completed] 部署到生产环境
- [completed] 准备提交（等待用户确认）  ← 标记completed，在回复中说明
# 用户确认后再创建新的todo：
- [pending] 提交代码并创建PR
```

---

## 新Pack引入检查清单（强制）

引入新的skill pack时，必须覆盖以下9个触点。遗漏任何一项将导致用户安装后功能缺失。

此清单源自v0.10.7/v0.10.8的教训：research pack在v0.9.0完成开发，但直到v0.10.7才被发现未接入安装流程，导致用户通过one-liner安装后无法获取该pack。

### 9个触点

| # | 触点 | 文件位置 | 说明 |
|---|------|---------|------|
| 1 | 本地安装器别名 | `install.ps1`, `install.sh` | 添加pack别名到安装器的pack映射表。本地安装器通过扫描`packs/`目录动态发现pack，但别名映射仍需手动注册 |
| 2 | 远程安装器ALL_PACKS数组 | `remote-install.ps1`, `remote-install.sh` | **必须手动添加**。远程安装器使用静态数组，不扫描目录 |
| 3 | Companion catalog PROFILES | `catalog_query.py` PROFILES dict | 将新pack加入相关profile（至少加入`comprehensive`） |
| 4 | project-initializer | `project-initializer/SKILL.md` + `init_project.py` | 在初始化向导中添加新profile或将pack关联到现有profile |
| 5 | README profile表 | `README.md` | 更新Pack列表、Profile → Auto-Install Mapping表 |
| 6 | 网站 | `website/index.html`, `website/pitch.html`, `website/blog.html` | 更新pack卡片、pack表格、pack计数 |
| 7 | 安装/升级指南 | `docs/agent-install.md`, `docs/agent-upgrade.md` | 更新安装示例和pack列表 |
| 8 | 中文翻译 | `docs/zh/README.md` | 同步更新中文版 |
| 9 | 归档文档 | `docs/archive/` 下相关文件 | 更新白皮书、介绍文档中的pack计数和列表 |

### 关键陷阱：本地 vs 远程安装器架构差异

- **本地安装器**（`install.ps1`, `install.sh`）：动态扫描`packs/`目录发现可用pack。新增pack目录后自动可见，但别名映射仍需注册。
- **远程安装器**（`remote-install.ps1`, `remote-install.sh`）：使用**硬编码的静态数组**（`$AllPacks` / `ALL_PACKS`）。新增pack必须手动添加到数组中，否则`--pack all`会静默跳过。

这一不对称是v0.10.7遗漏的根本原因。开发时使用本地安装器测试通过，但用户通过远程安装器安装时该pack不存在。

### 检查方法

引入新pack后，运行以下验证：

1. 在9个触点文件中搜索新pack名称，确认全部出现
2. 使用`--pack all`分别测试本地和远程安装器
3. 确认`/petfish catalog`能列出新pack
4. 确认`/initproject`的profile选择能关联到新pack

---

## Release检查清单（强制）

每次发布前，必须完成以下检查。

### 发布前

- [ ] 所有计划变更已合入`dev`分支
- [ ] `dev`分支测试通过（smoke test + trigger eval如适用）
- [ ] 如涉及新pack：已完成上述9触点检查清单
- [ ] 如涉及安装器变更：本地和远程安装器均已测试
- [ ] CHANGELOG已更新（如pack有独立CHANGELOG）
- [ ] README版本历史已更新
- [ ] 如涉及schema变更：已验证SKILL.md与schema字段名对齐

### 发布时

- [ ] 创建PR从`dev`合并到`master`
- [ ] PR合并后立即创建GitHub Release（`gh release create vX.Y.Z --target master`）
- [ ] Release notes包含变更要点
- [ ] Tag格式为语义化版本号（`vX.Y.Z`）

### 发布后

- [ ] 验证`gh release view --json tagName`返回正确的latest tag
- [ ] 使用远程安装器测试安装新版本
- [ ] 确认网站和文档中的版本信息一致

---

## Schema与SKILL.md对齐纪律（强制）

skill中如果同时存在JSON schema（`schemas/*.json`）和SKILL.md指令，两者的字段名、必填/可选标记、类型定义必须完全一致。

### 常见失败模式

- Schema中字段名为`search_queries`，SKILL.md中写成`queries` → 用户按SKILL.md填写后schema校验失败
- Schema标记某字段`required`，SKILL.md中未提及 → 用户遗漏必填字段
- Schema定义`enum`值列表，SKILL.md中的可选值不同 → 输出不一致

### 规则

1. 修改schema时，同步检查并更新SKILL.md中的对应描述
2. 修改SKILL.md中的字段描述时，同步检查schema是否需要更新
3. 新建skill时，如果包含schema，必须交叉验证字段名一致性
4. PR review时，schema变更必须附带SKILL.md的对应变更（反之亦然）

此规则源自#83、#82、#78三个issue的教训：多个research skill的schema与SKILL.md存在字段名不匹配，导致输出格式不一致。

---

## Description与Body触发词对齐纪律（强制）

Agent匹配skill时只读frontmatter `description`字段，body中的触发场景section对匹配不可见。因此description必须覆盖body中列出的触发关键词。

### 规则

1. 修改SKILL.md body中的触发词（触发场景、Trigger、Use this skill when等section）时，**必须**同步更新frontmatter description
2. 新建skill时，frontmatter description**必须**覆盖body触发词的≥80%
3. description长度不超过500字符，优先保留高频、高区分度的触发词
4. 中英文触发词都要覆盖——用户可能用中文或英文表达同一意图
5. PR review时，body触发词变更**必须**附带description的对应变更

### 自动化检查

- `skill-lint` 的 `lint_skill.py` 已内置 `trigger-coverage` 检查规则
- 覆盖率 <50% 报ERROR，50%-80% 报WARNING，≥80% 通过
- `quality-gate` 的 `run_gate.py` 在检测到trigger-coverage ERROR时，decision降级为CONDITIONAL

### 常见失败模式

- Body列出"帮我研究"、"仔细研究"等触发短语，但description中没有"研究"一词 → 用户输入"帮我研究一下"时skill不被匹配
- Body列出中文触发词但description只有英文 → 中文用户无法触发
- Body新增触发场景但忘记更新description → 新场景无法匹配

此规则源自Issue #91的教训：research-router的body列出了完整的触发场景，但description中缺少"研究"这个最基本的中文关键词，导致用户输入"帮我仔细研究一下XXX"时skill未被触发。经全量审计发现这是跨所有pack的系统性问题。

---

## 开发经验沉淀

### "一次全审一次全修" > 逐步修补

当变更涉及多个文件或多个触点时，先用系统性审计一次找出所有需要修改的位置，再统一修改。逐步修补容易遗漏，且每次遗漏都需要一个新的patch release。

v0.10.7遗漏了9个触点中的4个，v0.10.8通过并行审计一次性补齐。这说明：

- 第一次修改时投入额外时间做全面审计，总成本低于反复修补
- 对于跨文件变更，使用多个并行搜索覆盖不同角度比单次搜索更可靠
- 维护一个固定的检查清单（如上述9触点）比依赖记忆更可靠

### 研究范式 > 领域模板

设计skill时，按问题类型（learning、decision、risk）抽象，而不是按生活领域（travel、shopping）拆分。后者会导致skill爆炸且大量重复。领域差异通过轻量adapter层解决，而不是为每个领域建一套完整pipeline。

### 格式分离：JSONL给机器，Markdown给人

当同一份输出需要同时服务于后续pipeline处理和人类阅读时，不要试图用一种格式兼顾。JSONL用于结构化数据传递，Markdown用于人类可读的报告和文档。

---

## Pack-Specific Rules (On-Demand Loading)

When a task matches a pack domain, you MUST read the corresponding rules file
before proceeding. Use the Read tool on the listed path.

| Pack Domain | Trigger Signals | Rules File |
|-------------|----------------|------------|
| Course development | 课程, 教学, 大纲, 实验, QA/QC | `.opencode/agents-rules/course-skills.md` |
| Deployment & Ops | deploy, Docker, 部署, 回滚, 运维 | `.opencode/agents-rules/deploy-ops.md` |
| Writing style | 润色, 说人话, 去AI味, 风格 | `.opencode/agents-rules/petfish-style.md` |
| PEtFiSh companion | /petfish, skill创建, skill搜索 | `.opencode/agents-rules/petfish-companion.md` |
| Review/Calibration | 评审, review, critique, calibration | `.opencode/agents-rules/anti-sycophancy.md` |
| Topic governance | 话题治理, topic管理, 上下文污染 | `.opencode/agents-rules/fish-trail.md` |
| Research | 研究, 调研, 文献, evidence, 综述 | `.opencode/agents-rules/research.md` |

**Rules:**
1. If task clearly matches ONE pack → read that file immediately
2. If task matches MULTIPLE packs → read all matching files
3. If unsure → proceed without loading; load later if needed
4. Pack rules files are authoritative for their domain

---
