# PEtFiSh Companion Rules

本项目已安装胖鱼PEtFiSh伙伴skill。

## Skill路由（强制）

### 必须遵守的路由规则

1. 用户说"/petfish"或任何petfish子命令时，**必须**路由到 `fish-brain` skill处理
2. 用户需要创建新skill时，**必须**使用 `skill-author`；需要验证skill质量时，**必须**使用 `skill-lint`
3. 用户需要搜索外部skill或MCP server时，**必须**使用 `fish-market`
4. 用户需要发布skill时，**必须**使用 `quality-gate` 运行完整发布门禁（lint+security→决策）
5. 用户需要从仓库挖掘skill候选时，**必须**使用 `repo-skill-miner`
6. 用户需要安全审计skill时，**必须**使用 `skill-security-auditor`
7. 用户需要发布pack到市场时，**必须**使用 `skill-publish`（在 `quality-gate` PASS 之后）

### Pack分类（v1.4）

- **Core packs** (4): companion, toolchain, init, context — 直接从 petfish.ai 安装，不可发布到市场
- **Optional packs** (9): research, course, deploy, ppt, testdocs, petfish, calibrate, trust, reflect — 通过 petfish-market 发布和分发

Optional pack 的安装路由经过 petfish-market index.json；用户无需关心内部路由差异。

### 冲突解决

- 当用户同时涉及skill创建和质量检查时，先创建（`skill-author`），后检查（`skill-lint` → `quality-gate`）
- 当用户请求"搜索skill"时，区分：搜索外部市场用 `fish-market`，搜索已安装skill用 `fish-brain`

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
| 研究/调研/文献/证据/综述 | research | `/petfish install research` |

当用户需要创建新skill、搜索外部skill、或验证skill质量时，使用companion内置的skill-author、fish-market、skill-lint。

每次会话对同一pack最多主动推荐1次。

### 能力缺口自动检测（Tier 2：未知领域）

当上面的Tier 1白名单未命中时，判断用户消息是否暗示了一个**当前环境无法满足的能力需求**。

**触发条件 — 必须同时满足全部：**

1. 用户的请求涉及一个具体的活动、场景或任务（而非泛泛闲聊）
2. 该任务超出了agent内置能力（代码、文件、git、搜索、通用推理）
3. 当前已安装的skill也无法覆盖（检查已安装skill列表）

**排除条件（不触发）：**
- 普通编码、项目管理、git操作、文件整理
- 通用问答（解释概念、分析代码、给建议）
- 对话管理（"继续"、"停"、"换个方向"）
- 已安装skill明确覆盖的领域

**触发时行为：**
1. 推断用户需求最相关的英文关键词
2. 主动运行 fish-market（即 /petfish search <关键词>）搜索跨市场skill和MCP server
3. 根据搜索结果：
   - **找到匹配skill** → 推荐安装并提供命令
   - **找到相似但不完全匹配** → 展示结果，建议参考这些skill用 skill-author 手动创建
   - **完全找不到** → 建议用 repo-skill-miner 从相关GitHub仓库挖掘，或用 skill-author 从零创建

**示例：**
- "我想参加吐槽大会" → 触发 → 搜索 "roast comedy event planning"
- "帮我发个邮件通知团队" → 触发 → 搜索 "email notification"
- "帮我画一个甘特图" → 触发 → 搜索 "gantt chart"
- "帮我查一下这个API的rate limit" → 不触发（agent原生能力）

**行为约束：**
- 每次会话对同一类缺口最多提示1次
- 不自动安装，只推荐和展示搜索结果
- 用户拒绝后不再重复

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
- `/petfish upgrade` — 显示升级命令
- `/petfish uninstall <alias>` — 显示卸载命令（需本地安装器）

## 行为边界

- 不自动安装skill，只推荐并提供命令
- 不修改用户项目文件
- 用户拒绝后本次会话不再重复推荐

## 实施纪律（最小代码原则）

以下两条原则在实施任何任务时强制执行，适用于所有agent工作，不限于PEtFiSh开发。

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

## 契约驱动行为（Contract-Driven Behavior）

胖鱼Gateway的每一步都是机制原子（Mechanism Atom），有显式契约、测试用例和验证器。当Gateway行为异常时：

1. 读对应atom的 `contracts/step*.contract.json`，定位 `output_contract.blocked_outputs`
2. 运行 `validators/test_*.py` 验证当前行为
3. 如验证失败，按 `repair_strategy.on_violation` 执行修复循环（max 1 iteration）
4. 修复后添加known-bad fixture，确保回归覆盖

契约文件位于skill目录下的 `contracts/`、`fixtures/`、`validators/`。详见 `references/contract-methodology.md`。

### Gateway Trace（可观测性，始终输出）

每轮回复最开头输出一行结构化trace，让用户确认Gateway各步确实执行：

```
🐟 [trace] step0=balanced/false | step1=continue/low | step1.5=- | step2=- | step2.5=non-eval | violations=0
```

同时追加JSON到 `.petfish/gateway-trace.jsonl`。验证命令：
```bash
uv run <skills_dir>/fish-brain/validators/verify_trace.py --last 10
```
