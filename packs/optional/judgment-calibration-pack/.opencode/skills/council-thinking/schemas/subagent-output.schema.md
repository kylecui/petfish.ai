# Subagent Output Schema

每个 Council Member（无论是真实 subagent 还是逻辑模拟）的输出必须遵循此 schema。

## Markdown Schema

```markdown
## <Subagent Name>

核心判断：
<one concise judgment>

关键理由：
- <reason 1>
- <reason 2>

对决策的影响：
<how this changes the user's decision>

我不知道：
- <what this subagent does not know>
```

## Field Descriptions

| Field | Required | Description |
|---|---|---|
| `核心判断` | Yes | 该 subagent 对用户问题的一句话判断。 |
| `关键理由` | Yes | 2-4 条支撑该判断的关键理由。 |
| `对决策的影响` | Yes | 这个判断会怎样改变用户的决策或下一步思考。 |
| `我不知道` | Yes | 该 subagent 无法确认的信息，以及这会影响哪个判断。 |

## Constraints

- 每个 subagent 必须输出独立判断，不能与其他 subagent 重复。
- 不确定信息必须放在"我不知道"下，不能用"可能""大概"混在核心判断里。
- 理由必须具体，不能是泛泛而谈。
- Critic 必须指出会改变结论的问题；Executor 必须给出具体行动。

## Example

```markdown
## 反对者 Critic

核心判断：
这个方案的核心假设"用户会主动上传数据"没有证据，存在关键反转风险。

关键理由：
- 现有客户访谈中没有提到主动上传行为。
- 上传成本（学习成本、信任成本、操作成本）被严重低估。
- 一旦用户不上传，后续所有分析链都会失效。

对决策的影响：
如果无法验证上传意愿，整个产品价值主张需要重写，优先做 MVE（最小验证实验）而不是继续完善上传后的分析功能。

我不知道：
- 是否有竞品已验证类似行为的数据。
- 目标客户群体对隐私的敏感度。
```
