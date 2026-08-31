# 计划：动态技能挖掘与加载（项目1主体）

> 状态：草案 → Council已审 → **Momus ACCEPT（2026-08-31，引用全量复核通过）**
> 前置：`.sisyphus/plans/skill-machinery-foundation-fixes.md`（P0，F1/F2/F3为本文P1/P2的前置）
> 核心研究依据：
> - OpenCode平台（`anomalyco/opencode` @10765ff2 源码验证）：skill路径session静态（InstanceState/ScopedCache，mid-session新增不可见，需重启）；`experimental.chat.system.transform`每LLM调用触发（本仓库companion-gateway.ts为生产级证明）；MCP支持运行时注册（HTTP `POST /mcp`）+`ToolListChangedNotification`即时刷新；`cfg.skills.urls`启动期远程拉取
> - OpenMAIC技能系统模式（REVIEW §2.4 + skills.ts/skill-preload.ts）：发现块（name/desc/location，23技能仅3-5KB）+ `read`工具按需取正文 + 预算（3技能/60KB共享/首个必收）+ hash去重（readProvesCoverage）+ 路径限制在技能目录内

## 1. 核心洞察与架构

**动态加载不需要"动态注册skill"——把skill内容作为工具返回值按需送达即可绕过session静态缓存。** 指令以tool-result形式进入对话上下文，不受InstanceState限制。

```
用户输入
  │
  ▼
【索引层】skill-index.json扩容（installed|market|community|vault四源）
  companion-gateway经system.transform注入发现块：
  "可用vault_fetch按需加载：<top-3 name+一行desc>"（预算≤1.5K token，仅triggers匹配项）
  │ 能力缺口命中且本地无？
  ▼
【取载层】skill-vault MCP server（启动注册、内容动态）
  vault_index / vault_fetch(name) / vault_stage(来源) / vault_install(name)
  fetch带hash去重（同session同skill只全文返回一次）+ 60KB单skill预算
  → 本session立即可用（正文作为tool result），无需重启
  │ 市场与社区都没有合适的？
  ▼
【挖掘层】repo-skill-miner语义化：脚本退为信号收集器，
  LLM挖掘judgment由task()派生的挖掘agent执行 → skill-author脚手架 → vault
```

## 2. 目标与成功标准

- **目标**：用户提问新领域 → 相关skill在≤2轮对话内可用并实际生效；不装百个pack也能拥有百个pack的能力面。
- **成功标准**：
  1. 干净项目（仅companion）问"帮我办一场研讨会"→ agent经发现块提示→`vault_fetch(conference-adapter)`→按其SKILL.md工作→产出物符合该skill规范
  2. 同一skill二次fetch返回短响应（hash去重生效），session额外token开销≤1.5K/轮
  3. GitHub repo URL输入→staged可用skill全程人工介入0次，耗时≤5分钟（P2末验收）
  4. 跨平台：同一MCP server在Claude Code平台同样可用（MCP协议天然跨平台）

## 3. 分阶段任务

### P1 动态加载MVP（前置F3完成，预计2-3天）

**P1.1 skill-vault MCP server**
- 位置：`packs/core/petfish-companion-skill/.opencode/mcp/skill-vault/server.py`（companion pack分发，manifest+example.json注册，复用v3.2.0修好的注册链）
- 工具四件：
  - `vault_index(filter?)`：返回vault+可达市场skill的name/desc/source（轻量，无正文）
  - `vault_fetch(name)`：返回SKILL.md正文+文件树清单；单skill 60KB截断标记；`.petfish/skill-vault/state.json`记hash，同session重复fetch返回"已加载(hash)+增量文件列表"
  - `vault_stage(source)`：从白名单域（github.com/raw.githubusercontent.com/petfish-market）下载单skill到`.opencode/skill-vault/<name>/`；**安全**：域白名单+单skill大小上限（2MB）+zip-slip路径逃逸校验+落地后skill-lint快速校验（ERROR即拒收）
  - `vault_install(name)`：vault→`.opencode/skills/`复制+skill-index重生成+registry更新（复用F2的skill粒度安装逻辑）→返回"下session原生可用"提示
- 复用：marketplace_search.py的镜像回退逻辑（ghfast→ghproxy）平移到下载路径

**P1.2 发现块注入**
- `companion-gateway.ts`（+lib/plugin副本）：system.transform内，若step2 Skill Sense命中缺口且skill-index.json中存在非installed的可匹配项→注入一行发现块（top-3，格式：name+desc首行）
- 预算硬顶：发现块≤1.5K token，超限截断到top-1
- 不做OpenMAIC式"首条消息预载"（我们无首消息前钩子，agent驱动即可）

**P1.3 分发触点**
- companion pack：mcp/新增 + `opencode.example.json` mcp条目 + manifest contents + 版本bump（漂移门禁强制）
- 9触点核对：#1/#3/#5/#7（安装器别名不变/README/docs提及vault）

**P1验证**
- 契约测试：vault server单测（hash去重/截断/路径逃逸用例）+ gateway注入用例（有缺口/无缺口/预算截断三fixture）
- 端到端场景验收（成功标准1、2）

### P2 自动挖掘链（前置F1/F2完成，预计3-5天）

**P2.1 缺口→自动搜索（semi-auto设计）**
- gateway Tier2命中→注入指令："运行`uv run <skills_dir>/fish-market/scripts/marketplace_search.py --query <推断关键词> --json`并将命中项vault_stage"
- 决策依据：plugin内嵌网络调用（bun fetch）在TS侧重复实现搜索逻辑且难测试；agent执行脚本可复用既有Python实现+结构化JSON消费——**semi-auto（agent按注入指令执行）是可靠性最优先解**

**P2.2 搜索→staging→可见闭环**
- agent执行vault_stage→skill-index重生成→下一轮system.transform发现块自然出现新skill→fetch→使用
- `/petfish load <name|关键词>`命令：搜索+staging+（可选--install）一条龙（fish-brain命令面板扩展）

**P2.3 vault→持久安装**
- `vault_install`落地（F2逻辑复用）；`/petfish load --install`直通

**P2验证**
- 三场景端到端：市场命中直接staging / 市场未命中→社区 / 两者皆无→提示挖掘链

### P3 挖掘语义化+网络效应（5天+，可独立排期）

- **mine_repo语义化**：`derive_candidates`的6个硬编码模板退役为fallback；主路径改为SKILL.md指导挖掘agent（task(unspecified-high, load_skills=[repo-skill-miner, skill-author])）读repo关键文件→产候选→直接进skill-author脚手架生成vault skill；脚本保留signal收集（collect_signals/detect_domains）
- **挖掘质量evals**：3-5个golden repos（含OpenMAIC本身——23个course skills是现成答案集）
- **市场侧触发词**：publish时为市场pack生成默认triggers（从description抽取关键词），补齐F3留下的市场侧空白
- **community注册表播种**：首批3-5个真实社区pack收录
- **usage统计回路**：vault_fetch/install事件写入`.opencode/skill-usage.json`（复用skill-usage-tracker格式）→市场热度数据

## 4. 风险与缓解

| 风险 | 缓解 |
|---|---|
| system.transform注入体积失控 | 硬预算1.5K token+仅top-3+无缺口不注入（零开销常态） |
| 下载安全（任意URL/恶意skill内容） | 域白名单+大小上限+zip-slip校验+落地skill-lint快速门禁+skill-security-auditor可选深审 |
| experimental hook API变动 | gateway已有契约测试框架，注入行为挂回归用例；hook失效时降级为AGENTS.md指令层（现状行为） |
| MCP server启动失败静默 | 注册前`uv run server.py --selftest`自检；失败降级为无vault提示 |
| skill正文质量参差（市场/社区来源） | fetch返回体带lint分数与来源标签，agent可先验后用；--trust-scan机制复用 |
| 与Claude Code等平台的skill机制语义冲突 | vault是MCP层叠加，不修改平台原生skill目录（vault_install才写原生目录） |

## 5. 边界（不做）

- 不做OpenCode平台级skill热加载（那是上游`anomalyco/opencode`的事，watch其进展）
- 不做vault内skill的版本管理/依赖解析（fetch即最新，install后归install.py管）
- 不做自动安装付费/私有市场源（白名单域先行，扩展留接口）
- 不替换现有pack安装体系（vault是补充层，installed优先级永远最高）

## 6. Council审查记录（5+1，2026-08-31）

工作流依据：本仓库`agents-rules/anti-sycophancy.md`的council-thinking规范。

| 顾问 | 判断 | 裁决 |
|---|---|---|
| 反对者 | P1上MCP server是否过度工程？plugin tool(bun)更轻。且"mid-session POST /mcp注册"实际无人调用——用户不curl，agent无此工具；真实动态性来自server**内部数据**而非注册时机 | **部分采纳**：保留MCP（决定性理由：复用Python生态的搜索/下载/镜像回退逻辑+跨平台），但**修正定位**：P1是"启动注册+内容动态"；mid-session注册从能力主张降级为P3可选实验。已改写§1 |
| 本质思考者 | 真正解决的是"发现成本"——用户不知道skill存在。top-3注入的匹配质量是全链路瓶颈，地基计划的F3必须最先完成 | **采纳**：已在§3标注P1前置=F3；依赖图见地基计划§3 |
| 机会挖掘者 | vault_fetch返回体可带安装命令提示，agent用完即装形成增长回路；每次fetch记usage反哺市场热度 | **采纳一半**：安装提示进P1.1返回体格式；usage统计列P3（原计划已有） |
| 局外人 | hash去重OpenMAIC是runtime内存态，我们用`.petfish/skill-vault/state.json`落盘——session边界怎么定义？文件何时清理？ | **采纳**：state.json按session id分键，gateway session.id可用；会话结束不主动清理（体积小），保留7天过期字段；已补入P1.1 |
| 执行者 | P1.1动工前先固化两份半页设计：vault目录布局+state.json schema+四工具的JSON返回格式——避免返工 | **采纳**：P1.1首个任务=设计快照写入本计划附录（实施时补） |
| 仲裁结论 | 删0条全采纳（反对者部分采纳）；关键修正：MVP定位从"动态注册"改为"启动注册+内容动态"，诚实反映平台事实 | 已整合 |

## 7. 待Momus裁决项

1. P1的MCP路线 vs 更轻的plugin tool路线（反对者意见的残留分歧）
2. semi-auto挖掘链（agent执行脚本）vs plugin内嵌全自动的取舍
3. `.opencode/skill-vault/`作为staging目录的location（vs `.petfish/skill-vault/`——前者会被平台扫描吗？需确认OpenCode skill发现路径不包含它）

## 8. 我不知道的部分

- OpenCode `cfg.skills.urls`与vault机制是否冲突（urls拉取的缓存目录与vault目录是否重叠）——实施P1前实验确认
- 市场pack的skill在无triggers数据下，description匹配的实际召回质量——P1末做10用例小样本评测
- vault_fetch正文进入上下文后的实际token消耗分布（60KB预算是否需下调）——P1验收时实测

## 附录A：P1设计快照（实施前固化，Council执行者建议）

### A.1 目录布局

```
.opencode/skill-vault/        # staged skills（项目级）
  <skill-name>/
    SKILL.md
    ...技能文件树
.petfish/skill-vault/
  state.json                  # fetch去重状态（单active槽，7天过期）
```

vault放`.opencode/`而非`.petfish/`：`.petfish/`语义是运行时状态且已被gitignore惯例覆盖；vault是"待转正技能"。Momus待裁决#3确认：OpenCode skill发现只扫`.opencode/skills/`，vault不会被误扫。

### A.2 state.json schema（简化：单active会话槽）

```json
{"active": {"fetched": {"<skill>": {"sha256": "...", "ts": "..."}}, "expires": "<ISO+7d>"}}
```

### A.3 四工具返回格式

- `vault_index(filter?)` → `{"skills": [{"name","description","source": "vault|market|community|installed","pack"}], "total"}`
- `vault_fetch(name)` → 首次 `{"name","sha256","content":"<SKILL.md全文≤60KB>","truncated","files"}`；同会话重复 `{"name","sha256","already_loaded":true,"files"}`
- `vault_stage(source)` → `{"name","staged":true,"path","lint":{"errors","warnings"|"skipped":true}}`（lint ERROR即拒收删除）
- `vault_install(name)` → `{"name","installed":true,"restart_required":true,"index_regenerated":true}`

### A.4 P1边界（vault_stage源类型）

P1的stage支持：raw GitHub URL（指向SKILL.md）+ 本地路径。市场pack tarball级staging归P2（搜索→staging闭环）——单skill粒度先跑通全链路。镜像回退：raw.githubusercontent失败→ghfast.top→ghproxy.com。

### A.5 安全参数

域白名单（raw.githubusercontent.com/github.com/ghfast.top/ghproxy.com）；单skill≤2MB；SKILL.md返回截断60KB；zip-slip用resolve后前缀校验；lint快检可导入lint_skill.py则跑ERROR级，否则skip标注。
