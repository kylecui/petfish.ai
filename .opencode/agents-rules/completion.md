# Completion Engineering Pack (done)

本pack提供完成工程能力：任务宣称完成时给出可复核的证据链，而非agent的一面之词。核心是2个skill（done-gate、done-ledger），本文件只做路由，不复述流程。

## Skill路由（强制）

### 必须遵守的路由规则

1. 涉及完成标准、收尾检查、交付检查、遗留分流、验收类任务时，**必须**路由到 `done-gate`（契约+门）或 `done-ledger`（遗留分流）
2. 非平凡任务（多步骤/多文件）开工时，**必须**先按 `done-gate` 建立完成契约（外部锚+可验证谓词）
3. 宣称完成之前，**必须**过 `done-gate` 门：逐条执行verifications、记录真实证据、写verdict
4. gate触顶或out-of-scope的建议出现时，**必须**用 `done-ledger` 分流遗留项

### 冲突解决

- trivial任务（单文件typo级）不建契约、不过gate，直接做
- urgent模式下契约降级为最小版，gate照跑但verifier档禁用；用户明确跳过流程时按SKIPPED留痕规则处理
- 完成工程不替代QA/QC、release gate等既有门禁，是其上游的任务级收尾

## Todo语义（防无限循环）

- 被用户阻塞的工作（blocked-on-user）**永不**作为pending todo存在——todo标completed + 在回复文本中显式说明等待项
- gate触顶后的遗留项进backlog.md或对话明示，**永不**进todo（todo continuation hook会对pending todo无限触发）

## SKIPPED留痕

- urgent模式或用户明确跳过流程时：写`{"verdict":"SKIPPED","reason":...}`一行即合规，不留静默绕过——具体见 `done-gate` SKILL.md的urgent模式交互章节

## 触发词边界

禁用裸词`done`/`完成`作为触发词（开发者消息高频词，有`合理`→`合理吗`误触发前科）。只用组合词："完成标准"、"收尾检查"、"宣称完成"、"交付检查"、"遗留分流"、"还有下一步"、"验收一个任务"、"completion gate"、"done check"、"leftover triage"。
