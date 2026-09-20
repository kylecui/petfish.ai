---
name: done-gate
description: 任务收尾检查与交付验收门禁，把完成判定变成可复核的证据链。Use when 宣称完成之前、任务收尾、收尾检查、完成标准、交付检查、验收核对、完成判定, completion gate, done check, before declaring done, done contract, task wrap-up gate, verify before claiming done. 开工写契约（外部锚定+可验证谓词）；宣称完成之前过门：真实证据、恒真谓词拦截、独立校验重跑；verdict五值落盘，绕过须写SKIPPED留痕。多步骤多文件任务适用；trivial任务跳过。
compatibility: opencode
metadata:
  version: "1.0.0"
  author: "Petfish"
---

# Done Gate — 完成是契约，不是感觉

## Purpose

任务是"完成了"还是"感觉完成了"，区别在证据。done-gate在开工时把完成标准写成契约（可验证谓词+外部锚定），在宣称完成之前强制过门：真实证据、恒真谓词拦截、独立校验。产物是落盘的契约与裁决文件——可commit、可进PR、可跨session复核，不是agent的一面之词。

核心公式：

```
开工 = 写契约（外部锚定 + 可验证谓词）
收尾 = 过门（真实证据 + 独立校验）→ verdict落盘
```

## Triggers

触发短语：宣称完成之前、任务收尾、收尾检查、完成标准、交付检查、验收核对、完成判定、completion gate、done check、before declaring done、done contract、task wrap-up gate、verify before claiming done

触发判定只认上述组合词——裸词done与单独的完成二字因误报风险被消毒。

## State Files（状态文件）

```
.petfish/done/<task-slug>/
  contract.json   # 契约：revision + amendments + critical + anchor
  verdict.json    # 裁决：{verdict, revision, round, evidence[], remaining[], blocked_reason?, skipped?}
  backlog.md      # 遗留清单（done-ledger维护）
```

- task-slug：从用户请求或plan条目派生的小写短横线标识（如 `fix-login-timeout`）
- verdict五值：`VERIFIED_DONE` / `NOT_DONE` / `PARTIAL` / `BLOCKED_ON_USER` / `SKIPPED`。SKIPPED专用于绕过留痕，不参与组合优先级
- 契约有生命周期：closed/superseded状态，活跃契约默认14天过期，过期后不再提醒

## Phase A — 契约（开工时）

### 何时建契约

非平凡任务=多步骤、多文件、或用户消息含意图动词（实现/修复/交付/refactor/finish）。trivial任务（单文件typo级、纯问答、翻译排版）不建契约。

### 外部锚定（防循环论证）

contract必须含anchor字段，引用可核查的外部来源。禁止纯agent自拟outcome——自己出题自己判，等于没验。

| anchor.type | ref写法 |
|---|---|
| user_request | 用户原始请求的原文摘录 |
| plan | Prometheus plan文件路径+条目编号 |
| todo | todo列表项原文 |

无锚可用时，先向用户确认"做到什么程度算完成"，把答复摘录进anchor再开工。

### contract.json格式

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

字段全部必填：constraints/blocked_if/out_of_scope可为空数组；verifications至少1条。完整示例与anchor速查见 `references/contract-template.md`。落盘后立刻校验：

```bash
uv run .opencode/skills/done-gate/scripts/check_contract.py .petfish/done/<task-slug>/contract.json
```

### 修改契约需留记录（logged-amendment制）

- 修改只能以amendment形式追加并记录理由，revision递增；禁止静默改写既有内容
- verdict必须引用它依据的revision号
- 首次gate失败后的契约放宽（删谓词、降预期）必须在verdict中向用户显式声明

### 档位判定（机械信号，禁用agent自判）

| 档位 | 条件（任一满足即升档） |
|---|---|
| predicates-only（默认） | 其余所有情况 |
| predicates+verifier | `git diff --stat`文件数≥3，或契约含judge类谓词，或创建时被标critical |

## Phase B — 门（宣称完成之前）

对用户说出任务已完成之前，必须执行：

1. **逐条执行verifications**。command类：真实运行命令，证据=exit code+关键输出行；artifact类：亲自读文件核对contains；judge类：按criteria给出判断依据。禁止用记忆或推测充当证据
2. **恒真谓词检查（两档都执行）**：机械拦截`echo`/`true`/`exit`/`:`开头的恒真命令或空run充当谓词——最便宜的作弊是伪造谓词而不是伪造证据。check_contract.py在契约落盘时已拦截一次，过门时复核
3. **verifier档：独立校验**。spawn fresh-context verifier子agent，只给contract+diff+证据，不给agent自我陈述（信息隔离）。职责两条：
   - 重跑全部command类谓词（识别伪造证据）
   - 谓词-意图相关性审查：谓词通过但与outcome无关 → NOT_DONE
4. **verdict组合优先级**（从上到下，命中即停）：
   1. 任一谓词fail → `NOT_DONE`（机械证据不可上诉）
   2. 谓词全过+verifier反对 → 降级`PARTIAL`（只能降不能升）
   3. 命中blocked_if → `BLOCKED_ON_USER`
   4. `VERIFIED_DONE` = 谓词全过 +（verifier档：verifier裁决VERIFIED）+ 无in-scope遗留
5. PARTIAL要求至少1条outcome级verification通过，否则判`NOT_DONE`并在verdict标注escalated
6. 写verdict.json（含round、evidence、remaining），校验后向用户报告结果

### 循环出口规则

- gate最多3轮，每轮remaining[]必须收敛（不得增加）
- 连续2轮失败原因相同（no-progress）→ 停止重试，升级给用户
- verifier每任务最多1次；只有contract revision变更后才可重跑
- 后台子任务仍在运行时不宣称完成

## urgent模式与SKIPPED留痕

| 场景 | 行为 |
|---|---|
| depth=urgent | 契约降级为最小版（outcome+anchor+1条谓词），gate照跑，verifier档禁用 |
| 用户明说"别搞流程/直接做" | 写一行`{"verdict":"SKIPPED","reason":...}`即合规；gateway记录；本session后续任务不再注入契约stub |
| urgent下的完成宣称 | 不阻断，但verdict标`skipped:true`，发布流程可统计绕过率 |

绕过合法化不可避免（平台自己的urgent模式要求先绕过）。本pack做的是让绕过可见、可统计，而不是假装它不存在。

## 脚本：check_contract.py

```bash
# 校验契约：必填字段、anchor.ref非空、恒真谓词拦截（exit 1拒绝）
uv run .opencode/skills/done-gate/scripts/check_contract.py <contract.json>

# 追加校验裁决：verdict五值枚举、revision引用、round范围
uv run .opencode/skills/done-gate/scripts/check_contract.py <contract.json> --verdict <verdict.json>
```

stdlib实现，无网络。exit 0=通过，exit 1=校验失败，exit 2=文件或用法错误。

## Must do

- 契约落盘后立刻跑check_contract.py，FAIL即修再开工
- 每条evidence引用真实输出：命令原文+exit code+关键行
- verdict引用revision号；契约放宽必须向用户显式声明
- 触顶（3轮用尽）后交接待办给done-ledger分流，不自行续轮

## Must not do

- 禁止恒真谓词（echo/true/exit 0类）充当verification
- 禁止无锚自拟契约
- 禁止gate失败后静默放宽契约
- 禁止用"我觉得没问题"替代谓词执行结果
- 禁止在verifier反对时宣称VERIFIED_DONE
- 禁止在后台子任务未结束时宣称完成

## 与其他机制的关系

不替代：retry guard（重试纪律）、Momus（计划评审）、release gate（发布边界）、session resume（跨会话）。Done Contract是Prometheus plan的下游细化——anchor可指向plan条目。门的后续遗留分流交给done-ledger。
