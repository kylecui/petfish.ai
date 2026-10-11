# OpenCode Resilience Pack Rules

本pack提供OpenCode崩溃诊断与长任务韧性能力（2个skill，均为自包含只读工具）。

## Skill路由（强制）

1. 涉及崩溃分析、UnknownError、模型解析失败、后台任务崩溃、crash log、看日志时，**必须**路由到 `opencode-crash-taxonomy` skill（4类崩溃签名分类）
2. 涉及发射前校验、pre-flight、并行任务校验、watchdog、session恢复、prompt_async failed时，**必须**路由到 `opencode-session-doctor` skill
3. 涉及事后复盘与教训沉淀时，交棒给 `fish-reflection`

## 行为边界

- **0写操作**：两个skill均为只读诊断工具，不修改opencode.db、不写配置、不发网络请求
- **单session重试≤1**：watchdog对同一崩溃类别最多自动重试1次，随后交还用户决策
- 诊断结论必须标注证据来源（日志行号/配置文件路径），不凭空断言根因
