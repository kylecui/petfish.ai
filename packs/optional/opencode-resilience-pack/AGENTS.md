# OpenCode Resilience Pack

本pack提供 OpenCode（oh-my-opencode 发行版）长任务韧性能力：crash 四分类诊断 + 三层守护（发射前校验 / 运行时 watchdog / 治理钩子）。全部只读分析，恢复动作受限且留痕。

本pack包含2个skills：

- `opencode-crash-taxonomy`：知识/诊断型。给定 opencode.log 片段，按四类签名分类 crash（模型解析 / agent 身份解析 / 存储层 / 配额限流），输出置信度与建议动作，附只读 DB 取证 playbook。
- `opencode-session-doctor`：行动/程序型。L1 起并行任务前跑 preflight 模型对账并阻断坏引用；L2 watchdog 盯 `prompt_async failed` 并按类分诊（仅 agent 解析类允许自动恢复，单 session 最多 1 次）；L3 配置编辑保护与事故后复盘。

## Skill路由（强制）

### 必须遵守的路由规则

1. 用户贴 crash 日志求分析、问"UnknownError / 模型解析失败 / SqliteError / 使用上限怎么查"时，**必须**路由到 `opencode-crash-taxonomy`
2. 起并行/后台任务前校验配置、问"后台任务 watchdog / session 自动恢复 / 模型对账"时，**必须**路由到 `opencode-session-doctor`
3. watchdog 检出 crash 后：分类与深取证交 `opencode-crash-taxonomy`；恢复动作交 `opencode-session-doctor`——先诊断后恢复，不跳步
4. 任何对 opencode.db 的操作**必须**只读；写操作必须人工确认，agent 不得自行执行

### 冲突解决

- 与普通代码调试冲突时：仅当故障发生在 OpenCode 运行层（opencode.log / session / provider 解析）才启用本pack；项目自身代码的 pytest 失败等不触发
- 与 deploy pack 冲突时：本pack管 OpenCode 自身的崩溃与恢复，不管用户服务的部署运维

## 触发词边界

禁用裸词 `done` / `完成` 作为触发词。本pack触发词为组合词：session crash、crash 分析、UnknownError、prompt_async failed、模型解析失败、贴日志、后台任务老是失败、SqliteError、使用上限、起并行任务前、pre-flight、发射前校验、session doctor、模型解析对账、后台任务 watchdog、自动恢复、并行任务校验、session resume、quota suspended。

## 行为规则

- 分类只信签名+内层文本：`UnknownError: UnknownError` 字面量是 NamedError 类名，真实原因在 `.data.message`，禁止凭外层签名直接断言根因
- DB 取证一律只读：`message.data` 是 JSON 列用 json_extract 提取；event 表无时间列，陈旧度经 aggregate_id → session → MAX(message.time_created) 两跳推导
- 引用上游 issue（anomalyco/opencode #54256/#42507/#47158/#46111/#54172/#33356）时必须标注快照日期 2026-10-10——上游结论会漂移
- L2 自动恢复仅对 agent 解析类启用，单 session 最多重试 1 次；存储层故障不重试，直接止血升级
- 不自动重启 opencode 服务，只提示
- 事故后触发 fish-reflection L2 复盘，沉淀 prevention_rule

具体流程不复述——`opencode-crash-taxonomy` 与 `opencode-session-doctor` 的 SKILL.md 是唯一真值源。
