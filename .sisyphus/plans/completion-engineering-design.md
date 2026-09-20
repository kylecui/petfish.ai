# PEtFiSh 完成工程（Completion Engineering）设计方案 v1.2

状态：已吸收Oracle评审（v1.1）+ Council五顾问审查（v1.2），待用户确认后实施
话题：topic_20260920_ce06

---

## 0. 评审记录

### v1.0 → v1.1（Oracle技术评审，2026-09-20）

裁决：Q1砍standard档两档制+机械触发；Q2不加第五态+verdict组合规则；Q3循环治理混合形态不建独立skill；Q4只读降级为logged-amendment；Q5 contract并入gate（3→2 skills）。
致命缺陷修补：gate调用无保障→gateway注入提前v1；verifier重跑谓词；触顶遗留禁入todo；契约TTL；trivial覆盖归零声明。

### v1.1 → v1.2（Council五顾问审查，2026-09-20）

五顾问收敛点（多视角独立撞出同一点，可信度最高）：
1. **入口洞**（Critic+Essence+Outsider）：契约创建/gate调用纯靠prompt，机械力全在中后段——F1/F2/F4的起源点防御最弱。要作弊的agent只需不写contract.json
2. **承诺-机制落差**（Critic+Outsider+Essence）："让Agent自主完成任务"兜不住，真实交付物是证据链+可见性；第一次绕过gate照样宣称done时反噬pack信任
3. **文件格式是持久资产**（Opportunity+Outsider+Critic）：contract/verdict是可commit、可进PR、可团队化的审计产物；平台官方hook追平后，契约格式+verifier隔离+ledger分流是与平台无关的残值
4. **狗粮先行**（Executor+Opportunity）：release流程shadow契约是第一个部署场景；9触点清单在v0.10.7已真实失败过一次=现成F1证据
5. **契约需外部锚**（Essence+Critic）：纯agent自拟契约并自评=循环论证；最便宜的Goodhart是伪造谓词（`echo ok`恒真）而非伪造证据

四项修订：①承诺降级（§3）②堵入口洞（§5.4 stub注入、§5.1外部锚+恒真拦截+相关性审查、§11场景7、§6 SKIPPED痕迹）③平台边界显式化（§3 OpenCode-only+触发词消毒）④切片重排序（§10 Executor四切片，A1为S4发布前置条件）。

---

## 1. 问题定义

| # | 失败模式 | 证据 |
|---|---------|------|
| F1 | 过早宣布完成 | Ordewell："模型对着编译不过的构建宣布成功" |
| F2 | 永不收尾（下一步/还可以做X） | Active-Plan Response Discipline纯prompt无法强制 |
| F3 | 无限循环（todo continuation hook对pending todo无限触发） | 200+事故（AGENTS.md Todo纪律） |
| F4 | 假完成/Goodharting | METR（o3改测试）；Anthropic（sys.exit(0)）；BAITBENCH（>50%作弊率） |
| F5 | 过早放弃（反向失败） | Codex #16900误杀健康子任务 |

## 2. 平台约束

1. 无输出拦截hook → 强制手段仅：system.transform注入 / 状态文件 / 子agent验证
2. 外部todo continuation hook不可修改 → 唯一杠杆是todo语义（blocked≠pending）
3. 不重复现有：retry guard / dispatch tracking / gateway契约循环 / Momus / release gate / session resume
4. 指令级控制近乎无效（METR）→ 机制隔离优先于行为劝导
5. **urgent模式明文"先绕过"**（v1.2新增）→ 流程必须定义与depth模式交互，绕过须留痕——绕过合法化恰发生在F1-F4高发区（截止压力）

## 3. 产品定位与承诺边界（v1.2新增）

- **定位**：重度自主任务用户的进阶pack（长任务/多文件/自主运行场景），非人人必装的基础设施
- **对外承诺（唯一允许的话术）**："任务宣称完成时，你拿到的是可复核的证据链，不是agent的一面之词；绕过流程会被记录可见。"
- **禁止的承诺**："让Agent一次对话自主完成任务"、"结构性消灭下一步"——机制兜不住（Council否决）
- **平台边界**：v1 OpenCode-only。强制力（gateway注入）依赖OpenCode plugin；其他7平台为建议级，安装页/描述必须注明，否则构成"卖出会退货的产品"
- **术语消毒**：对外文案（SKILL.md description、安装页）禁用内部黑话——
  - Goodhart → "agent为通过检查而作弊"
  - logged-amendment → "修改契约需留记录"
  - todo-hook接缝 → "遗留任务不得变成待办，防止无限循环"
  - 触发词禁用裸词`done`/`完成`（见§5.3）

## 4. 核心思想

**完成是契约，不是感觉。**
开工写契约（外部锚定+可验证谓词）→ 收尾必须过门（真实证据+信息隔离独立校验）→ 遗留强制分流。

v1.2诚实定位：这是**证据链与可见性系统**——提高绕过成本、让跳过事后可审计；不是硬执行系统（平台无输出拦截，硬执行不可能存在）。

## 5. Pack结构：2 skills + 1 L1 rules + gateway扩展

### 5.1 Skill: done-gate（契约阶段+门阶段+循环出口，三合一）

**Phase A — 契约（开工时）**

触发：非平凡任务（多步骤/多文件/意图动词场景）。

**外部锚定（v1.2新增，防循环论证）**：contract必须含`anchor`字段，引用可核查的外部来源——用户原始请求摘录 / Prometheus plan条目 / todo列表项。禁止纯agent自拟outcome；无锚时先向用户确认完成标准。

```json
{
  "revision": 1,
  "amendments": [],
  "critical": false,
  "anchor": {"type": "user_request | plan | todo", "ref": "用户原话摘录或plan路径"},
  "outcome": "结果导向的完成陈述",
  "constraints": ["不许动的文件/接口", "范围边界"],
  "verifications": [
    {"type": "command", "run": "uv run pytest -q", "expect": "exit 0"},
    {"type": "artifact", "path": "docs/api.md", "contains": "端点列表"},
    {"type": "judge", "criteria": "错误信息含修复指引而非裸stack trace"}
  ],
  "blocked_if": ["缺少部署凭证", "需要用户在A/B间选择"],
  "out_of_scope": ["性能优化", "其他端点同类问题"]
}
```

**契约修改 = logged-amendment制**：修改仅以amendment形式允许并记录理由，revision++；verdict引用其所依据的revision；首次gate失败后的契约放宽必须在verdict中向用户显式声明。

**档位判定（机械信号，禁用agent自判）**：

| 档位 | 条件（任一满足即升档） |
|-----|---------------------|
| predicates-only（默认） | 其余所有情况 |
| predicates+verifier | `git diff --stat`文件数≥3 OR 契约含judge类谓词 OR 创建时被标critical |

**Phase B — 门（宣称完成之前）**

1. 逐条执行verifications，证据=真实命令输出（exit code+关键行），artifact类读文件核对
2. **恒真谓词检查（v1.2新增，两档都执行）**：机械拦截`echo`/`true`/`exit 0`类恒真命令充当verifications——最便宜的作弊是伪造谓词而非伪造证据
3. verifier档：spawn fresh-context verifier subagent，只给contract+diff+证据（不给agent自我陈述）；职责=重跑全部command类谓词 + **谓词-意图相关性审查**（谓词通过但与outcome无关→NOT_DONE）
4. verdict组合优先级：
   1. 任一谓词fail → `NOT_DONE`（机械证据不可上诉）
   2. 谓词全过+verifier反对 → 降级`PARTIAL`（只能降不能升）
   3. 命中blocked_if → `BLOCKED_ON_USER`
   4. `VERIFIED_DONE` = 谓词全过 +（verifier档：VERIFIED）+ 无in-scope遗留
5. PARTIAL要求≥1条outcome级verification通过，否则`NOT_DONE(escalated)`
6. 写verdict.json + gateway trace行

**循环出口规则**：gate最多3轮且每轮必须收敛（remaining[]不得增加）；no-progress（2轮同因）→停+升级；verifier每任务最多1次（revision变更才可重跑）；后台子任务运行时不宣称完成。

### 5.2 Skill: done-ledger（遗留分流+todo-hook接缝）

| 遗留类型 | 去向 |
|---------|------|
| in-scope未完成（gate循环内） | 回done-gate Phase B继续 |
| gate触顶后的所有遗留 | backlog.md或对话明示，**永不进todo** |
| out-of-scope建议 | backlog.md，禁建todo |
| blocked-on-user | todo标completed+对话明示等待项 |

已知残余风险（v1.2诚实声明）：F2的典型形态是agent**从不宣称done**、只在行文里无限"还可以做X"——此时gate和ledger都不会被触发。§5.4的stub注入部分缓解（契约被创建后，开放契约提醒形成落盘压力），残余部分接受并记录。

### 5.3 L1 Rules: agents-rules/completion.md

- **触发词消毒（v1.2）**：禁用裸词`done`/`完成`作为独立触发词（开发者消息出现频率极高；本仓库有`合理`→`合理吗`误触发修复前科）。改用组合词："任务收尾"、"宣称完成之前"、"收尾检查"、"遗留分流"、"还有没有下一步"
- 短，引用skills不复述流程（防双真值漂移）
- 内容：todo语义（blocked≠pending）、gate与ledger调用指针、SKIPPED留痕规则指针

### 5.4 Gateway扩展（v1必含；3副本同步纪律不变，pack副本为唯一源，只push不rebind）

1. **开放契约提醒**：contract存在无verdict → 注入提醒
2. **意图动词stub注入（v1.2新增，堵入口洞）**：检测用户消息中的意图动词（实现/修复/交付/refactor/finish）→ session内无活跃契约时注入契约stub（**外部锚预填=用户消息摘录**），agent只需落盘确认。诚实标注：落盘仍是prompt级，但锚由gateway预填后伪造锚的成本显著提高
3. 轮次状态注入："gate rounds 2/3, last failure X"
4. 契约生命周期：closed/superseded状态，TTL默认14天，只提醒活跃契约
5. **SKIPPED痕迹注入（v1.2新增）**：检测到urgent模式或用户明确跳过流程时，注入"绕过须留痕"提醒

强制 vs 建议的诚实边界（v1.2更新）：
- **强制级（机制）**：轮次计数、状态持久化、backlog出口、verifier重跑+相关性审查、恒真谓词拦截、SKIPPED留痕规则
- **半强制**：stub注入（内容预填，落盘靠agent）
- **建议级**："说done前跑gate"本身

## 6. urgent模式交互（v1.2新增）

| 场景 | 行为 |
|---|---|
| depth=urgent | 契约降级为最小版（outcome+anchor+1条谓词），gate照跑但verifier档禁用 |
| 用户明说"别搞流程/直接做" | agent写`{"verdict":"SKIPPED","reason":...}`一行即合规；gateway记录；本session后续任务不再stub注入 |
| urgent下的完成宣称 | 不阻断，但verdict标记`skipped:true`，发布流程可统计绕过率 |

依据：绕过合法化不可避免（平台自己的模式要求先绕过），能做的是让绕过**可见可统计**，而非假装不存在。

## 7. 反Goodhart设计

| 威胁 | 对策 | 变化 |
|-----|------|-----|
| **假谓词（恒真命令）** | 恒真命令机械拦截+verifier相关性审查 | **v1.2新增** |
| 假证据 | verifier重跑command谓词；artifact亲自读文件 | keep |
| 骗verifier | 信息隔离（无自我陈述） | keep |
| 契约放水 | logged-amendment+revision引用+放宽须声明 | keep |
| **无锚自拟契约** | anchor字段外部锚定，禁纯自拟 | **v1.2新增** |
| 逃避gate | stub注入（预填锚）+开放契约提醒 | v1.2升级 |
| 绕过轮次上限 | 触顶后遗留禁入todo | keep |
| **静默绕过（urgent）** | SKIPPED痕迹可统计 | **v1.2新增** |

## 8. 覆盖边界（诚实声明）

- trivial任务（单文件typo级）不写契约、跳过gate——覆盖率按设计归零，不计入验收
- agent永不宣称done的F2形态：gate不触发、ledger不执行——stub注入部分缓解，残余接受并记录
- 模型侧激励偏差（宣布完成的训练倾向）只能缓解（证据要求），不能根治——本方案修的是框架缺口（完成定义未外化）和平台侧激励扭曲（continuation loop），模型侧偏差靠gate证据要求对冲（Council Essence定性）
- F5过早放弃：BLOCKED_ON_USER独立状态+async感知部分缓解

## 9. 状态文件

```
.petfish/done/<task-slug>/
  contract.json   # revision+amendments+critical+anchor
  verdict.json    # {verdict, revision, evidence[], remaining[], blocked_reason?, skipped?}
  backlog.md      # out-of-scope建议
```

verdict五值：`VERIFIED_DONE` / `NOT_DONE` / `PARTIAL` / `BLOCKED_ON_USER` / `SKIPPED`（v1.2新增，绕过留痕专用，不参与组合优先级）。

## 10. 实施切片（v1.2采纳Executor方案，替代触点正序；"狗粮→机制→发布"倒序）

| 片 | 内容 | 验收标准 | 量级 |
|---|---|---|---|
| **S1 第1周** | done-gate SKILL.md（predicates-only档+恒真拦截+外部锚）+ install.py两行注册（ALIASES 52行区/L1_PACK_MAP 1551行区）+ 本仓库狗粮2个真实任务（含release流程shadow契约：谓词=pre_release_check各项） | 场景1、5真实触发；**A1契约创建率开始记录**；`uv run install.py --pack done --target <tmp>`成功 | Quick |
| **S2 第1周末** | gateway扩展一次做完（3副本：提醒+stub注入+轮次+TTL+SKIPPED）+ L1 rules | 3副本diff空；只push不rebind；自愈测试（删`.petfish/done/`不崩） | Short |
| **S3 第2周** | done-ledger + verifier档（重跑+相关性审查）+ trigger evals | 场景2、4、7真实触发；evaluator正反用例通过；A2成本实测 | Short-Medium |
| **S4 狗粮数据达标后** | 剩余8触点（catalog/initializer/README/website/docs/zh/archive/market）+pre_release_check+release+对外文案（术语消毒后） | 触点搜索全命中；**前置条件：A1未证伪**；pre_release_check PASS | Medium |

**停止清单（v1不做）**：market注册、website/docs-site/README/zh/archive、多平台适配测试、Momus/Prometheus深度整合、第五态、输出拦截、独立循环skill（Oracle已否决不再讨论）。

**假设验证（Executor实验设计）**：
- **A1 agent会写契约**：S1狗粮2任务，**不给gateway提醒**，统计开工建契约率。证伪信号：任一任务未主动建契约 → stub注入提前到S1末合并
- **A2 verifier成本可接受**：S3对1次狗粮任务手动spawn verifier，实测tokens/耗时/误报。证伪信号：成本>任务本体50%或环境性误报 → verifier限critical档
- **A3 用户觉得值得**：v1内只有代理证据（狗粮期拦截有效性），真实验证留待发布后——诚实声明，不伪装

## 11. 自我验收（本pack自己的Done Contract）

1. 假完成案例（改代码不跑测试，非平凡任务）→ gate以NOT_DONE拦截
2. 伪造证据案例（verdict.json塞假输出）→ verifier重跑识破
3. blocked-on-user场景 → 全程无pending todo产生（200+事故回归）
4. gate触顶场景 → 遗留全进backlog，无todo泄漏
5. 契约放宽案例 → verdict显式声明amendment
6. trigger evals：消毒后触发词正反用例（done-gate按阶段区分）
7. **对抗性契约（v1.2新增）**：含恒真谓词的契约被拦截——predicates-only档机械检查与verifier档相关性审查双路径各测一次
8. **A1行为度量（v1.2新增）**：狗粮期契约创建率/过门率有记录，S4发布决策必须引用该数据

## 12. 与现有机制关系

不替代：retry guard / dispatch tracking / gateway契约循环(max_iterations=1) / Momus(计划评审) / release gate(发布边界) / session resume(跨会话)。
互补：Done Contract是Prometheus plan的下游细化（契约anchor可指向plan条目）；verifier复用oracle子agent模式；done-ledger结构化Todo纪律；gateway扩展复用companion-gateway注入模式。

## 13. v2+ backlog（v1.2新增，来自Opportunity挖掘）

- **跨pack契约registry**：deploy验证/release门/course QA/research证据共用契约schema。条件：核心schema冻结3谓词类型+code任务域证明后；对齐走SKILL.md指引层（文档级成本，有schema对齐纪律先例）
- **release流程shadow狗粮制度化**：S1起步，v2转正式（gate出verdict，人拍板→binding）
- **"Done is a contract"差异化叙事**进产品语言：竞品全停在harness层（hooks/loop模式不可分发不可审计），契约文件是可commit、可进PR、可团队化的资产；verdict可信度=护城河。条件：v1验证价值后再上，避免过度承诺
- **平台无关核心对冲**：契约格式+verifier隔离+ledger分流不依赖特定平台，对冲官方hook演进风险
