# Review Roaster Pack Rules

本pack提供一个将技术review报告改写为有梗但可追溯的吐槽大会摘要的skill。

## Skill路由（强制）

### 必须遵守的路由规则

1. 用户说"吐槽版"、"吐槽大会"、"写个吐槽"、"犀利版review"、"毒舌版"、"脱口秀版"、"roast session"、"roast this"、"give me the roast"、"make it funny"、"entertaining review"时，**必须**路由到 `review-roaster` skill
2. **前置条件**：项目中已存在至少一份完成态review报告（通常位于`reports/`），且报告内含可引用的事实证据。如前置条件不满足，先返回缺失项，不生成吐槽稿
3. 每条吐槽**必须**保留证据引用（格式：`(证据来源: reports/xxx.md:行号)`），不得为搞笑而捏造事实
4. 输出**必须**包含"说句公道话"环节，提取positive findings并保留证据

### 冲突解决

- 当吐槽意图与正式review意图并存时（如"帮我review并写个吐槽版"），先走正式review流程，完成后再加载 `review-roaster`
- 当用户请求"帮我review"但没有吐槽相关触发词时，不启用本skill
- 建议与 `anti-sycophancy-calibration` 组合使用，确保正式review先于吐槽

## 辣度等级

- `mild`：温和调侃，适合项目方可见版本
- `roast`（默认）：犀利吐槽，标准脱口秀节奏
- `nuclear`：高强度内部娱乐版，仍必须遵守证据与伦理边界

## 组合示例

- `anti-sycophancy-calibration + review-roaster`：先做反迎合校准的正式review，再转为吐槽版
- `review-roaster`（单独使用）：已有正式review报告，直接生成吐槽摘要
