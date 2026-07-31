# PEtFiSh 项目开发纪律

本节定义项目级开发规则，所有agent和人工操作必须遵守。

---

## Companion Gateway（每条消息强制执行）

> 胖鱼是你的AI伙伴。伙伴的意思是：每一轮交互都在。

**以下流程在处理用户消息之前强制执行，无例外。**

### Step 0: Mode Read（项目模式）

每次session首条消息时，读取 `.opencode/project-mode.yaml`（如存在）：

```yaml
# .opencode/project-mode.yaml
depth: balanced       # urgent | balanced | thorough
rigor: false          # true | false (forced true when depth=thorough)
```

**Depth行为修改：**

| Depth | Bug处理 | 依赖问题 | 搜索策略 | 失败响应 |
|---|---|---|---|---|
| urgent | 先绕过，记TODO | 用替代方案 | 第一个可信结果 | 快速修→继续 |
| balanced | 正常调试流程 | 理解基础后修复 | 2-3来源 | 标准流程 |
| thorough | 必须找根因 | 全影响分析 | 多源交叉验证 | 证据驱动修复 |

**Session内切换（不写文件）：**

用户说以下关键词时，在当前session内切换模式（下次session自动恢复文件配置）：

- urgent: "紧急", "urgent", "快速", "先凑合", "workaround", "临时方案"
- balanced: "正常", "balanced", "标准流程"
- thorough: "仔细", "thorough", "root cause", "根因", "彻底"
- rigor on: "严谨", "rigor", "严格", "先计划", "plan first", "谨慎"
- rigor off: "快做", "直接做", "skip plan", "不用计划"

**文件不存在时**：默认 `depth: balanced, rigor: false`，不阻塞。

### Step 1: Topic Check（话题归属）

Topic context由 `system-prompt-context-inject` 插件自动注入到system prompt的cached prefix中。每轮交互时，从注入的 `## Active Topic Context` 块读取当前话题状态，无需调用MCP工具。

根据注入的topic context判断：

| 话题状态 | 行为 |
|---------|------|
| low risk (继续当前话题) | 静默继续 |
| medium risk (话题偏移) | 回复开头一行说明上下文继承范围 |
| high risk (跨领域大幅切换) | 暂停正常处理，向用户说明话题变更风险，建议fork/switch/reset |

**MCP不可用时**：插件注入仍可用（来自磁盘缓存），仅MCP工具调用不可用。每次会话最多提示一次"⚠ fish-trail MCP未连接"。

### Step 1.5: Failure Signal Detection (Tier 0)

扫描**上一轮assistant回复**和工具错误输出，检测已知失败模式。命中时推荐可解决该问题的skill/MCP。

**触发条件（全部满足）：**

1. 上一轮assistant明确承认无法完成（"无法"、"cannot"、"I don't have access"）或工具返回已知错误模式
2. 存在一个已知skill/MCP可以解决该类失败
3. 该信号本session未推荐过（去重）
4. 对应skill/pack未安装

**信号 → Skill 映射：**

| 失败模式 | 匹配正则 | 推荐Pack |
|---------|---------|---------|
| PDF/PPTX读取失败 | `无法(打开\|读取\|解析).*(PDF\|PPTX\|PPT\|幻灯片)` | ppt |
| 部署/Docker失败 | `(deploy\|部署\|Docker).*(fail\|失败\|error\|错误)` | deploy |
| 测试生成困难 | `(测试用例\|test case).*(无法\|不确定\|需要).*生成` | testdocs |
| 研究深度不足 | `(需要更多\|证据不足\|无法确认).*(来源\|evidence\|文献)` | research |
| 上下文污染 | `(上下文\|context).*(混乱\|污染\|冲突\|drift)` | context |

**输出格式：**
```
💡 检测到上轮失败信号 — <pack>-skill 可以处理此类问题。安装: /petfish install <pack>
```

**实现位置：** `catalog_query.py --check-failures "<上轮assistant文本片段>"`

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

### Step 2.6: Reading-Notes Check（阅读笔记检查）

当任务涉及阅读项目文件时，先查阅读笔记，避免重复阅读：

1. grep `.petfish/notes/reading-notes.jsonl` 找 `file_path`
2. 找到笔记 → stat文件比对 `file_mtime`+`file_size`：
   - mtime和size匹配 → 用笔记summary，跳过重读
   - 不匹配 → 文件已改，重读并更新笔记
3. 无笔记 → 正常读，读完后追加笔记（含mtime+size）

详见fish-brain SKILL.md Section 10。

### Step 3: Proceed（正常处理）

完成 Step 1-2.6 后，先输出Gateway Trace（可观测性），再进入正常任务处理流程。

#### Gateway Trace（始终输出，非debug-only）

每轮回复的最开头，输出一行结构化trace，让用户确认Gateway各步确实执行：

```
🐟 [trace] step0=balanced/false | step1=continue/low | step1.5=- | step2=- | step2.5=non-eval | step2.6=notes:0/3 | violations=0
```

- `step0=depth/rigor` — 模式读取
- `step1=relation/risk` — 话题检测
- `step1.5=failure_class` 或 `-`（无信号）
- `step2=skill` 或 `-`（无缺口）
- `step2.5=eval` 或 `non-eval`
- `step2.6=notes:hit/total`（本session命中笔记数/总笔记数）
- `violations=N`（0=正常）

同时追加结构化JSON到 `.petfish/gateway-trace.jsonl`（一行一条）：

```json
{"ts":"ISO-8601","steps":{"step0-mode-read":{"depth":"balanced","rigor":false},"step1-topic-check":{"relation":"continue","risk":"low"},"step1.5-failure-signal":{"detected":false,"class":null},"step2-skill-sense":{"detected":false,"skill":null},"step2.5-anti-sycophancy":{"evaluative":false}},"violations":[]}
```

用户可随时验证：
```bash
uv run .opencode/skills/petfish-companion/validators/verify_trace.py --last 10
```

### Step 2.5: Anti-Sycophancy Check（反迎合检查）

在回答评价性问题（"好吗?", "对吗?", "is this right?", "what do you think?"）之前：

1. **暂停**。不要立即同意。
2. 定义"好"在此语境下的含义（rubric-first）。
3. 找到至少**一个**提案可能错误的原因。
4. 然后再形成结论。

如果真诚努力后找不到反论 → 同意是合理的。
如果跳过此步骤 → 你在迎合用户。

**主动性等级（与Rigor绑定）：**

| Rigor | Anti-Sycophancy Level |
|---|---|
| off | 仅对显式评价性问题（"好吗?", "对吗?"） |
| on | 也对隐式寻求认可 + 技术断言进行检查 |

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

## Rigor Mode（严谨模式）

当 `.opencode/project-mode.yaml` 设置 `rigor: true`（或 `depth: thorough` 自动强制 rigor）时，以下规则生效：

### Before Implementation

- 对3+步骤或涉及3+文件的任务，写一份简要计划到 `.sisyphus/plans/` 说明：做什么、为什么、涉及哪些文件、可能出什么问题
- 对上述任务：invoke Momus on the plan file（`task(subagent_type="Momus - Plan Critic", load_skills=[], run_in_background=true, prompt=".sisyphus/plans/<plan-filename>.md")`）
- **Blocking** — MUST wait for Momus result before implementing. No exceptions.
- On [ACCEPT]: proceed
- On [REJECT]: fix blocking issues in plan, re-submit
- On [CONDITIONAL]: proceed but address noted concerns

### During Implementation

- State assumptions explicitly before acting on them
- If an assumption is unverified, verify it (read file, check docs) before proceeding
- Never batch multiple uncertain changes — one verified step at a time

### After Implementation

- Run verification beyond just lsp_diagnostics:
  - Does the change actually solve the stated problem?
  - Are there edge cases the implementation misses?
  - Would a skeptical reviewer approve this?

### Rigor Threshold

Only the full plan+Momus flow applies to tasks with **3+ steps or 3+ files**. Simpler tasks still get the "state assumptions" and "verify after" discipline but skip the formal plan file.

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

## 命令输出完整性纪律（强制）

### 规则

- **禁止**在bash命令中使用管道截断原始输出（`| grep`、`| tail -N`、`| head -N`、`| awk '{print}'`、`| sed -n`等）
- 所有命令必须直接执行，获取完整stdout+stderr
- 如果需要搜索输出中的特定内容：
  1. 先运行命令，让工具获取完整输出
  2. 输出过大时工具会自动截断并写入临时文件，用Read/Grep工具在该文件中搜索
  3. 不在命令层面通过管道提前过滤

### 原因

管道截断在三个层面破坏agent的诊断能力：

1. **信息丢失**：构建错误通常在输出开头，`| tail -20`直接丢弃。agent看到"最后20行看起来正常"就报告成功，实际编译失败。
2. **退出码失效**：管道链`cmd | grep`中，`grep`无匹配返回exit 1，掩盖了`cmd`本身的成功；反过来`cmd`失败但`grep`碰巧匹配，则掩盖了失败。
3. **循环反复**：agent看不到真实输出，无法定位问题，只能反复运行同一命令（`make`→`make`→`make`），每次都因相同原因失败却看不出来。

这不是token节约问题——工具已内置输出大小限制和文件写入机制。管道截断绕过了这些保护，在agent和真实输出之间插入了不可靠的滤镜。

此规则源自Claude Code Issue #39945的教训：`node generate-files.js 2>&1 | tail -3`，脚本崩溃但最后3行正常，agent误判为成功。

### 允许的管道

以下管道模式不违反本规则，因为它们不截断原始输出：

- `cmd 2>&1` — 合并stdout/stderr（不截断）
- `cmd > file 2>&1` — 重定向到文件（完整保存后再分析）
- `cmd1 && cmd2` — 链式执行（各自独立输出）

### 禁止的管道模式

| 模式 | 替代方案 |
|------|---------|
| `make \| tail -20` | `make`（完整输出），再用Read/Grep搜索 |
| `npm test \| grep PASS` | `npm test`（完整输出），再用Grep搜索 |
| `docker logs \| grep error` | `docker logs`（完整输出），再用Grep搜索 |
| `kubectl get \| awk '{print $1}'` | `kubectl get`（完整输出），再提取特定列 |

### 示例

**错误 — 管道截断导致误判成功：**

```bash
# Agent运行: make | tail -5
# 输出: 5行看似正常的编译信息
# Agent结论: "编译成功"
# 实际: 第3行已有error，但被tail丢弃
```

**正确 — 完整输出后分析：**

```bash
# Agent运行: make
# 工具获取完整输出（可能截断并写入临时文件）
# Agent用Grep搜索"error:"或"FAIL"
# Agent定位到第3行error并修复
```

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

## Active-Plan Response Discipline（强制）

当存在活跃计划（≥1个todo处于`in_progress`或`pending`状态）时，agent输出必须聚焦于计划执行，禁止主动发散。

### 激活条件（全部满足时生效）

1. ≥1个todo item处于`in_progress`或`pending`
2. 用户当前消息**不是**在询问选项/建议
3. 当前任务**不是**评价性/探索性任务

### 停用触发（任一满足时约束解除）

- 所有todo已`completed`或`cancelled`
- 用户明确询问"还能做什么?"、"what else?"、"options?"
- Agent被阻塞，需要用户决策
- 任务本身是评价性的（review、critique、"你觉得呢?"）

### 禁止的输出模式（激活时）

- "I can also..." / "我还可以..."
- "如果你想，我还可以做以下N件事"
- 未经请求的选项菜单或编号建议列表
- 不在当前计划中的投机性相邻工作
- "Would you also like me to..." / "要不要我顺便..."
- "此外，我还能..."

### 允许的输出模式（激活时）

- 任务完成摘要（做了什么）
- 阻塞描述（什么阻止了进展）
- 来自计划的下一步行动（不是发明的）
- 被阻塞时的一个澄清问题
- 当前todo项的状态更新

### 违反后果

违反此规则等同于偏离计划执行。companion-gateway插件会在系统提示中注入偏差提醒，但当前OpenCode插件API不支持输出拦截（无`chat.response.transform` hook），因此最终合规性仍取决于模型自觉遵循AGENTS.md指令。

---

## 实施纪律（最小代码原则，强制）

以下两条原则在实施任何任务时强制执行。

### 原则一：先读后写

阅读、查找、改写内容或代码时，优先通过**阅读**发现关键点并直接修改，而非写脚本/代码/shell命令来查找或替换。

### 原则二：代码最小化六问

必须使用shell命令、脚本或代码时（已有定稿的设计方案除外），先依次回答以下问题，从上到下满足即停：

0. **既有skills能做到么？** 能→按skills做。
1. **一定需要这个脚本么？** 没有能不能做？能→不写脚本/代码/命令。
2. **标准库能实现么？** 能→用标准库。
3. **平台原生能做到么？** 能→原生。
4. **现成依赖能做到么？** 能→复用。
5. **一行能做到么？** 能→一行命令。
6. **写最少量的代码完成任务。**

此纪律同步写入随pack分发的 `packs/core/petfish-companion-skill/AGENTS.md`，确保用户侧agent同样遵循。

---

## 新Pack引入检查清单（强制）

引入新的skill pack时，必须覆盖以下9个触点。遗漏任何一项将导致用户安装后功能缺失。

此清单源自v0.10.7/v0.10.8的教训：research pack在v0.9.0完成开发，但直到v0.10.7才被发现未接入安装流程，导致用户通过one-liner安装后无法获取该pack。

### 9个触点

> **v1.4更新**：可选pack需额外在petfish-market注册（触点#10）。核心pack（`packs/core/`）随仓库直接分发，可选pack（`packs/optional/`）通过petfish-market分发。

| # | 触点 | 文件位置 | 说明 |
|---|------|---------|------|
| 1 | 本地安装器别名 | `install.py` + `install.ps1`, `install.sh` | 添加pack别名到安装器的ALIASES映射表。`install.py`（统一Python安装器）为首选；shell安装器为遗留兼容 |
| 2 | 远程安装器ALL_PACKS数组 | `remote-install.ps1`, `remote-install.sh` | **遗留**。`install.py` 通过 petfish-market 动态解析可选pack，无需静态数组 |
| 3 | Companion catalog PROFILES | `catalog_query.py` PROFILES dict | 将新pack加入相关profile（至少加入`comprehensive`） |
| 4 | project-initializer | `project-initializer/SKILL.md` + `init_project.py` | 在初始化向导中添加新profile或将pack关联到现有profile |
| 5 | README profile表 | `README.md` | 更新Pack列表、Profile → Auto-Install Mapping表 |
| 6 | 网站 | `website/index.html`, `website/pitch.html`, `website/blog.html` | 更新pack卡片、pack表格、pack计数 |
| 7 | 安装/升级指南 | `docs/agent-install.md`, `docs/agent-upgrade.md` | 更新安装示例和pack列表 |
| 8 | 中文翻译 | `docs/zh/README.md` | 同步更新中文版 |
| 9 | 归档文档 | `docs/archive/` 下相关文件 | 更新白皮书、介绍文档中的pack计数和列表 |
| 10 | petfish-market注册（v1.4新增，仅可选pack） | `petfish-market/registry/official/` + `petfish-market/index.json` | 可选pack必须注册到market的官方目录并更新`index.json` |

### 关键陷阱：本地 vs 远程安装器架构差异

- **统一Python安装器**（`install.py`，首选）：通过 `uv run` 远程执行，PEP 723 inline script自动引导，内置镜像回退（`ghfast.top` → `ghproxy.com`），通过 petfish-market 动态解析可选 pack。
- **本地安装器**（`install.ps1`, `install.sh`）：动态扫描`packs/core/`和`packs/optional/`目录发现可用pack。新增pack目录后自动可见，但别名映射仍需注册。
- **远程安装器**（`remote-install.ps1`, `remote-install.sh`，遗留）：使用**硬编码的静态数组**（`$AllPacks` / `ALL_PACKS`）。新增pack必须手动添加到数组中，否则`--pack all`会静默跳过。
- **v1.4市场分发**：可选pack（`packs/optional/`）通过petfish-market分发，`install.py` 和远程安装器通过`query_market_index()` / `Query-MarketIndex`自动解析。核心pack（`packs/core/`）仍直接从petfish.ai仓库下载。

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

### 发布前 — 自动化门禁（BLOCKING）

**`gh release create`之前必须运行预发布验证脚本，输出FAIL则禁止release：**

```bash
uv run python scripts/pre_release_check.py
```

脚本检查：
1. CI在master上是success（红=禁止release）
2. 所有pack能安装到干净临时目录
3. 契约验证器在**安装上下文**通过（非源码仓库）
4. 市场索引指向monorepo（非stale独立仓库）

**此规则无例外。脚本FAIL时修复问题，不要绕过。**

### 发布前 — 手动检查

- [ ] 所有计划变更已合入`dev`分支
- [ ] `dev`分支测试通过（smoke test + trigger eval如适用）
- [ ] 如涉及新pack：已完成上述9触点检查清单
- [ ] 如涉及安装器变更：本地和远程安装器均已测试
- [ ] CHANGELOG已更新（如pack有独立CHANGELOG）
- [ ] README版本历史已更新
- [ ] 如涉及schema变更：已验证SKILL.md与schema字段名对齐
- [ ] 所有修复的GitHub issue在release notes中用 `Closes #N` 引用

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

### bash内嵌Python用`chr()`代替转义字面量

当Python代码运行在bash双引号字符串内（`python3 -c "..."`）时，反斜杠转义会跨层叠加：源文件 → bash双引号解释 → Python解释。每一层将反斜杠数量减半，而SSH或PowerShell代理还会引入额外的转义层。使用`chr(92)`表示反斜杠、`chr(47)`表示正斜杠，而不是字面转义序列。`chr()`在Python运行时求值，对所有shell转义层免疫。

这个教训花了两个patch release（v0.11.10、v0.11.11）才解决issue #123。

### 通过用户的实际通道测试

v0.11.10的修复通过PowerShell SSH会话测试，看起来正确，但PowerShell自身的转义层掩盖了bash的真实行为。用户在原生Linux bash上运行时仍然报错。

规则：bash脚本必须在真实bash环境中测试，PowerShell脚本在真实PowerShell中测试。不要通过代理shell测试另一种shell的行为——中间层会吞掉或改变转义字符，产生误导性的"通过"结果。

### 安装器同步变更

项目有 `install.py`（统一Python安装器，首选）和 4个遗留安装器（`install.sh`、`install.ps1`、`remote-install.sh`、`remote-install.ps1`）。`install.py` 是主要维护对象，逻辑变更优先确保 `install.py` 正确。遗留安装器按需同步，但功能语义必须一致。

v0.11.9（uninstall功能）和v0.11.10/v0.11.11（rstrip修复）都涉及4个安装器的同步变更。遗漏任何一个会导致用户通过不同安装方式得到不一致的行为。

### v1.4市场优先分发：核心pack vs 可选pack的触点差异

v1.4将packs/拆分为`packs/core/`（4个）和`packs/optional/`（9个）。核心pack随仓库直接分发，可选pack通过petfish-market分发。这引入了一个新的关键触点（#10：petfish-market注册），并改变了触点#1和#2的语义：

- **触点#1（本地安装器）**：新增pack时需同时更新扫描路径（`packs/core/`或`packs/optional/`）
- **触点#2（远程安装器）**：可选pack不再需要手动添加到`ALL_PACKS`静态数组——远程安装器通过`query_market_index()`自动解析market索引
- **触点#10（新增）**：可选pack必须在petfish-market的`registry/official/`目录创建条目，并更新`index.json`

核心pack与可选pack的触点数量不同：核心pack覆盖#1-#9，可选pack额外需覆盖#10。

### OpenAPI schema与handler签名的drift检测

当HTTP服务同时维护OpenAPI schema和Python handler代码时，schema中声明的参数与handler实际接受的参数可能产生漂移（drift）。典型表现：GPT Actions发送schema中定义的参数，但handler不接受，导致`TypeError`。

v1.4.6的online-gpt gateway发现2处drift（`runtime`和`risk_sensitive`字段）。根本原因是schema和handler代码独立维护，没有自动对齐机制。

规则：

- 每次修改OpenAPI schema时，必须同步检查对应handler的函数签名
- 每次修改handler函数签名时，必须同步检查OpenAPI schema
- 使用`check_schema_drift.py`做自动检测，不要依赖手动比对
- 短期方案：dispatch层加allowlist filter（`inspect.signature`），未知字段进warnings而非TypeError
- 长期方案：从OpenAPI schema自动生成handler签名校验

### 批量同类文件替换优先用本地脚本

当需要跨10+文件做同类替换（如退役一种安装命令、统一一种术语）时，优先写一个本地替换脚本（sed/python），而不是派多个分布式agent各自处理不同文件。

原因：分布式agent的网络依赖没有fallback。当外部资源不可用时（证书错误、超时），agent只能失败，导致大量重试和浪费。21个文件的命令迁移中，4个子agent因证书错误被取消，所有工作需要重做。

本地脚本的优点：无网络依赖、可预览（dry-run）、可grep验证、一次性完成。

### 变更后验证相邻路径

修复一个endpoint/handler后，必须同时验证同一dispatch层级的所有sibling endpoint，不能只验证修好的那一个。

v1.4.6修复了`routeCompanionRequest`的dispatch问题，本地smoke test只测了这一个operation。部署后发现`suggestPacks`因相同根因（`profile_project`不接受`risk_sensitive`）返回500，但这个operation在修复时没有被打到测试里。

规则：改了N个handler中的1个，smoke test要跑全部N个。

### 在安装上下文验证，不在源码仓库验证

v1.8.0-v1.9.0的交付失败根因：验证器在源码仓库能跑（有benchmarks/scripts/modules/），在用户安装后崩溃（没有这个目录）。6个release声称"全部修复"，实际0-3个到达用户。

规则：`gh release create`前必须运行 `uv run python scripts/pre_release_check.py`。脚本在干净临时目录安装所有pack，在**安装上下文**运行验证器。FAIL=禁止release。

此教训源自v1.8.0-v1.9.0的交付失败：代码在源码仓库但用户从市场仓库拿，两者之间没有同步。与v0.10.7/v0.10.8的9触点遗漏是同一类问题。

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

<!-- BEGIN pack: doc-reader-skill -->
# Doc Reader Skill Pack Rules

This pack provides unified document-to-Markdown conversion for reading, review, and extraction.

## Skill Routing (强制)

### Rules

1. When the user wants to **read, extract text from, or convert** a non-Markdown document (PDF, DOCX, XLSX, HTML, EPUB) to Markdown, **MUST** route to `doc-reader`.
2. When the user needs **structured text content** from a document (tables, paragraphs, lists), **MUST** use `doc-reader` to convert first, then read the Markdown output.
3. For **PPTX files**: use `ppt-reader` for structural inventory (slide order, media, comments, layout), use `doc-reader` for full text extraction including tables and charts. Use both for complete PPTX understanding.
4. When the user provides a document and asks to **review, summarize, or extract key points**, use `doc-reader` for conversion, then apply `reference-document-review` for analysis. Do NOT treat conversion as analysis.

### Conflict Resolution

- "Read this PDF and summarize": route `doc-reader` (convert) → agent reads output → summarize. Conversion and analysis are separate steps.
- "Extract the tables from this DOCX": route `doc-reader` with `--json` for metadata, then read the Markdown output.
- "Read this PPTX": route `ppt-reader` first for structure, then `doc-reader` for full text if structural inventory is insufficient.
- "Convert this document to Markdown": route `doc-reader` only. No analysis needed.
- When `reference-document-review` is also installed: `doc-reader` handles conversion, `reference-document-review` handles analysis and extraction into course inputs. Do not merge these responsibilities.

## doc-reader Workflow

1. Identify input file and format (PDF, DOCX, XLSX, HTML, EPUB, etc.)
2. Run conversion:
   ```bash
   uv run scripts/doc_to_markdown.py input.pdf --output output.md
   ```
3. Read the converted Markdown output
4. Optionally extract structured metadata:
   ```bash
   uv run scripts/doc_to_markdown.py input.pdf --output output.md --json metadata.json
   ```

## Behavioral Rules

- Always convert before reading. Do NOT attempt to interpret binary file contents directly.
- Preserve the conversion output as a file when the user needs to review or cite it later. Use `--output` flag.
- For scanned PDFs, warn the user that markitdown does NOT perform OCR by default; text extraction will be minimal.
- For PPTX, always recommend `ppt-reader` for structural analysis first if structure matters (slide order, media inventory, layout issues).
- Do NOT attempt LLM-based image description through this skill. The agent can view images natively.

## Output Format

**doc-reader** outputs:
1. Markdown file — converted text content from the source document
2. (Optional) JSON metadata — `{source_file, source_ext, text_length, title_guess}`
<!-- END pack: doc-reader-skill -->

<!-- BEGIN pack: opencode-ppt-skills -->
# PPT Skills Pack Rules

This pack provides PPTX reading and writing capabilities for course slides, proposals, reports, and technical decks.

## Skill Routing (强制)

### Rules

1. When the user wants to **read, inspect, summarize, audit, or compare** a PPT/PPTX file, **MUST** route to `ppt-reader`. Do NOT route to `ppt-writer`.
2. When the user wants to **create, rewrite, restructure, update, or export** a PPT/PPTX deck, **MUST** route to `ppt-writer`. Do NOT route to `ppt-reader`.
3. When the user provides a Markdown outline, document, meeting notes, or old PPT and asks to generate a new deck, **MUST** route to `ppt-writer`.
4. When the user asks for a "rewrite brief" or "per-slide action plan" as input for a future writing task, **MUST** route to `ppt-reader` (produces the brief), then `ppt-writer` (executes it).
5. When the user asks for visual QA of a generated deck, **MUST** use `ppt-writer`'s `qa_deck.py` step — do NOT treat this as a `ppt-reader` task.

### Conflict Resolution

- "Read and then rewrite" requests: route `ppt-reader` first to produce inventory + rewrite brief, then `ppt-writer` to execute. Do not merge into a single step.
- "Summarize the slides" = `ppt-reader`. "Update the slides" = `ppt-writer`.
- When ambiguous, ask: is the primary output a **report about** the deck (`ppt-reader`) or **a new deck** (`ppt-writer`)?

## ppt-reader Workflow

1. Extract slide inventory → `pptx_inventory.json` (titles, layout, notes, comments, media, links)
2. Produce Markdown summary of structure and content
3. Flag: missing placeholders, sensitive info, broken links, layout inconsistencies
4. Optionally produce a rewrite brief / per-slide action plan for `ppt-writer`

## ppt-writer Workflow

1. Receive input: Markdown / doc / outline / old PPTX / rewrite brief
2. Build narrative structure and page plan
3. Run `build_deck.py` to generate PPTX
4. Run `qa_deck.py` to verify output
5. Fix issues found in QA
6. Re-verify until QA passes
7. Deliver final PPTX

## Behavioral Rules

- Never skip the `qa_deck.py` step after `build_deck.py`. Generate → QA → fix → re-verify is mandatory.
- `ppt-reader` output (inventory JSON + Markdown summary) must be saved before passing to `ppt-writer`.
- Template and style unification must be applied consistently across all slides in a deck.
- Do not mix reading and writing in a single tool invocation.
- LibreOffice and Poppler are optional dependencies for visual QA; if unavailable, note the limitation and proceed with structural QA only.

## Output Format

**ppt-reader** outputs:
1. `pptx_inventory.json` — structured slide inventory
2. Markdown summary — human-readable structure and content overview
3. (Optional) Rewrite brief — per-slide action plan

**ppt-writer** outputs:
1. Generated `.pptx` file
2. QA report — issues found and fixed
3. Delivery summary — slide count, template used, known limitations
<!-- END pack: opencode-ppt-skills -->

<!-- BEGIN pack: opencode-skill-pack-testcases-usage-docs -->
# Test Cases & Usage Docs Skill Pack Rules

This pack provides two complementary skills: generating test cases from real project code, and generating usage documentation from real project capabilities.

## Skill Routing (强制)

### Rules

1. When the user asks to generate **test cases, test strategy, test matrix, or test plan** from a project, **MUST** route to `generate-test-cases`. Do NOT route to `generate-usage-docs`.
2. When the user asks to generate **README, Quick Start, API docs, CLI docs, FAQ, or troubleshooting guides** from a project, **MUST** route to `generate-usage-docs`. Do NOT route to `generate-test-cases`.
3. Both skills require a **project inventory step first**: run `uv run scripts/project_inventory.py .` before generating artifacts. Do not skip this step.
4. When the user asks for both tests and docs in the same request, run `generate-test-cases` and `generate-usage-docs` sequentially (inventory once, then both generation steps). Do not merge them into a single pass.
5. Both skills operate on **real project code and design docs** — do not generate generic/template artifacts without first reading the actual project.

### Conflict Resolution

- "Write tests for this project" = `generate-test-cases`.
- "Document this project" = `generate-usage-docs`.
- "Help me ship this project" (ambiguous) → ask whether the priority is test coverage or user-facing documentation, then route accordingly.
- If the user provides a design doc or spec as input, both skills can use it — but route based on the desired output type (tests vs docs).

## generate-test-cases Workflow

1. Run project inventory: `uv run scripts/project_inventory.py .`
2. Build traceability map: capabilities → test targets
3. Generate layered test artifacts:
   - Test strategy (scope, risk areas, coverage goals)
   - Test matrix (feature × scenario × priority)
   - Test cases (input, expected output, pass/fail criteria)
4. Output to `tests/` or designated output directory

## generate-usage-docs Workflow

1. Run project inventory: `uv run scripts/project_inventory.py .`
2. Identify target audience (end user / developer / operator)
3. Identify project capabilities (CLI, API, config, integrations)
4. Build doc set:
   - README (overview, install, quick start)
   - API / CLI reference
   - FAQ and troubleshooting
5. Output to `docs/` or designated output directory

## Behavioral Rules

- Always run project inventory before generating any artifact. Do not generate from assumptions.
- Test cases must be traceable to specific project capabilities identified in the inventory.
- Usage docs must reflect actual project behavior, not generic boilerplate.
- If the project inventory reveals missing or ambiguous capabilities, flag them before generating — do not silently fill gaps with invented behavior.
- Generated test cases must include: input, expected output, and pass/fail criteria. Vague test descriptions are not acceptable.
- Generated docs must include: at least one working example per capability documented.

## Output Format

**generate-test-cases** outputs:
1. Test strategy document — scope, risk areas, coverage goals
2. Test matrix — feature × scenario × priority table
3. Test case files — structured cases with input/output/criteria

**generate-usage-docs** outputs:
1. README — overview, install, quick start
2. Reference docs — API / CLI / config
3. FAQ / Troubleshooting — common issues and resolutions
<!-- END pack: opencode-skill-pack-testcases-usage-docs -->

<!-- BEGIN pack: trustskills-governance-pack -->
# Trust Skills Governance Pack Rules

This pack provides skill trust scanning, governance level assignment, and manifest generation/verification for PEtFiSh skill packs.

## Skill Routing (强制)

### Rules

1. When the user asks to **scan skills for trust, safety, or governance issues**, **MUST** route to `skill-trust-governance`.
2. When the user asks to **generate or verify a trust manifest** for a skill or pack, **MUST** route to `skill-trust-governance`.
3. When the user asks to **assign or review governance levels** (allow / allow_with_ask / sandbox_required / manual_review_required / deny) for skills, **MUST** route to `skill-trust-governance`.
4. When the user asks to **redline** a skill (flag it as requiring manual review or denial), **MUST** route to `skill-trust-governance`.
5. The entrypoint for all trust operations is: `uv run .opencode/skills/skill-trust-governance/scripts/trust_scan.py`. Do not invoke `trustskills` CLI directly without going through this entrypoint.

### Conflict Resolution

- Trust governance vs security audit: `skill-trust-governance` handles **governance classification and manifest management** (what level of trust to grant a skill). `skill-security-auditor` handles **vulnerability and risk scanning** (what security risks a skill poses). They are complementary — run security audit first, then use findings to inform governance level assignment.
- When the user asks to "check if a skill is safe to install", route to `skill-security-auditor` for risk findings, then `skill-trust-governance` for governance decision.
- When the user asks to "publish a skill", the governance manifest must be generated by `skill-trust-governance` before the `quality-gate` publish flow.

## Governance Levels

| Level | Meaning | Agent Behavior |
|---|---|---|
| `allow` | Trusted, no restrictions | Execute without prompting |
| `allow_with_ask` | Trusted but requires confirmation for sensitive actions | Prompt user before sensitive operations |
| `sandbox_required` | Must run in isolated environment | Do not execute outside sandbox |
| `manual_review_required` | Flagged for human review before use | Block execution, notify user |
| `deny` | Rejected, must not be used | Refuse to load or execute |

## trust_scan.py Modes

- **scan**: Analyze a skill directory and produce a trust report
- **manifest**: Generate a signed trust manifest for a skill
- **verify**: Verify an existing trust manifest against current skill content
- **redline**: Flag a skill at `manual_review_required` or `deny` level

## Behavioral Rules

- Never assign `allow` governance level without completing a full scan. Partial scans must result in `manual_review_required` at minimum.
- Trust manifests must be regenerated whenever skill content changes. Stale manifests are treated as `manual_review_required`.
- `deny`-level skills must not be loaded, executed, or referenced in routing rules.
- When a scan finds issues, report them with the specific governance level recommendation and the reason. Do not silently downgrade to `allow`.
- Governance decisions must be logged with: skill path, scan timestamp, findings summary, assigned level, and agent ID.

## Output Format

**scan** output:
1. Trust report — findings per skill file, risk signals detected
2. Recommended governance level with justification

**manifest** output:
1. Signed trust manifest file (saved alongside skill)
2. Manifest summary — skill path, level, timestamp, hash

**verify** output:
1. Verification result: PASS / FAIL / STALE
2. If FAIL or STALE: diff of what changed and recommended action

**redline** output:
1. Updated governance level in manifest
2. Redline reason and required remediation steps before level can be upgraded
<!-- END pack: trustskills-governance-pack -->
