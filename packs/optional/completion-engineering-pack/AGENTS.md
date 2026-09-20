# Completion Engineering Pack

任务宣称完成时，用户拿到的是可复核的证据链，不是agent的一面之词；绕过流程会被记录可见。

本pack包含2个skills：

- `done-gate`：开工写完成契约（外部锚定+可验证谓词），宣称完成之前过门（真实证据+恒真谓词拦截+独立校验），verdict五值落盘。
- `done-ledger`：任务收尾后的遗留分流——范围内回gate、范围外进backlog、等用户的明示等待。

## Skill路由（强制）

### 必须遵守的路由规则

1. 非平凡任务（多步骤、多文件、或用户消息含实现/修复/交付等意图动词）开工时，**必须**用 `done-gate` 建完成契约：外部锚定（anchor引用用户原话/plan条目/todo项）+可验证谓词，落盘到 `.petfish/done/<task-slug>/contract.json`
2. 宣称完成之前（任务收尾、交付检查、验收核对时），**必须**用 `done-gate` 过门：逐条执行谓词、真实证据、独立校验，verdict落盘
3. 任务收尾后出现遗留（用户问"还有没有下一步"、需要收尾整理）时，**必须**用 `done-ledger` 分流
4. 用户明确跳过流程或depth=urgent绕过门时，**必须**让done-gate写SKIPPED verdict留痕

### 冲突解决

- 开工定义完成标准、过门判定 → `done-gate`；门后的遗留去向 → `done-ledger`。先gate后ledger
- 单文件typo级trivial任务：不建契约、不跑门、不分流（覆盖率按设计归零）
- 简单问答、翻译、排版不触发本pack

## Todo语义（强制）

- **blocked不等于pending**：等待用户的项，对应todo一律标completed，并在回复中明示等待内容与恢复条件——禁止留pending todo触发平台的自动继续机制（历史事故：200+次无效循环）
- **gate触顶后的遗留永不进todo**：3轮用尽后的所有遗留只进backlog.md或对话明示，禁止转成新todo
- 范围外建议禁建todo，记backlog即收工

## 触发词纪律

只用组合词触发：任务收尾、宣称完成之前、收尾检查、完成标准、交付检查、验收、遗留分流、还有没有下一步。**禁止**用裸词done或单独的"完成"二字做触发判定——开发者消息高频词，误触发前科见本仓库"合理"→"合理吗"修复。

## 行为规则

- 完成判定看谓词与证据，不看agent自我感觉
- 修改契约需留记录：以amendment追加并记理由，revision递增；verdict引用revision号；契约放宽必须向用户显式声明
- verdict五值（VERIFIED_DONE/NOT_DONE/PARTIAL/BLOCKED_ON_USER/SKIPPED）落盘到 `.petfish/done/<task-slug>/verdict.json`，契约与裁决是可commit、可进PR的审计资产
- 后台子任务运行时不宣称完成

具体流程不复述——`done-gate` 与 `done-ledger` 的SKILL.md是唯一真值源。
