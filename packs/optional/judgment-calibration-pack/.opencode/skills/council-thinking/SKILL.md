---
name: council-thinking
description: 五人顾问团多视角对抗式判断。用 Council 分析方案评估、战略判断、产品定位、技术路线、研究设计、课程设计、Presentation主线、逻辑审查、写作结构取舍、是否值得做、如何向客户/评审/老板表达等复杂判断。显式触发：用Council分析、五人顾问团审查、多视角评估、对抗式审查、不要迎合我。比 fish-calibrate 更深：5个logical subagents + Arbiter删除弱观点，输出可执行结论。/ Use Council for multi-perspective adversarial review of strategy, product positioning, tech roadmap, research design, course design, business analysis, logic checks, and how-to-communicate decisions. Triggers: "Council analysis", "five-advisor review", "multi-perspective evaluation", "adversarial review".
compatibility: opencode
metadata:
  version: "0.1.0"
  owner: "Petfish"
  author: "Petfish"
---

# Council Thinking

## Purpose

Council Thinking 是一个用于复杂判断的 **multi-perspective adversarial reasoning workflow**。它不是普通的多角色写作模板，而是一套带有冲突、筛选、仲裁和执行闭环的判断机制。

目标：

1. 减少单一视角造成的盲区。
2. 减少对用户观点的默认迎合。
3. 主动暴露逻辑漏洞和未经验证的假设。
4. 从本质、机会、外部感知和执行路径多维度重构问题。
5. 删除低价值观点，形成更硬、更清晰、更可执行的结论。

## Domain Rules

- 真正让 Council 成立的不是"五个人都说话"，而是最后的**仲裁、压缩和删弱观点机制**。
- 五个顾问是 **logical subagents**（逻辑子代理），不是戏剧化角色或必须真实存在的 agent 进程。
- 不允许五个顾问用不同的名字说同一件事；没有独立贡献的观点应删除。
- 不确定的信息必须明确说"我不知道"，并说明缺失什么、影响哪个判断、当前最稳妥的判断是什么。
- 最终结论不是五个观点的平均值，而是经过筛选后的判断。

## Triggers/Activation

### 默认适用

- 方案评估
- 战略判断
- 产品定位
- 技术路线选择
- 研究设计
- 课程设计
- Presentation 主线设计
- 商业分析
- 逻辑审查
- 写作结构取舍
- 是否值得做某件事
- 如何向客户、评审、老板或市场表达一个想法
- 需要"反迎合""挑错""风险审查"的问题

### 显式触发语

- 用 Council 分析。
- 不要迎合我，用五人顾问团审查。
- 用反对者、本质思考者、机会挖掘者、局外人、执行者五个角度判断。
- 用 Council 方法评估这个方案是否靠谱。
- 用多视角/对抗式方式审查这个方案。
- 五人顾问团，请审查这个判断。

### 不默认适用

- 简单事实问答
- 单句翻译
- 纯格式转换
- 纯代码生成
- 用户明确要求极简回答
- 用户只要求直接润色、改写或翻译
- 问题本身不涉及判断、取舍或决策

## Decision Points

1. **Quick vs Full mode**：用户只问"简单判断"或要求简洁时用快速模式；否则用完整模式。
2. **Delete weak points or keep them**：Arbiter 必须明确删除没有证据、无法行动、情绪支持或为了凑角色而产生的观点。
3. **Actionability first**：执行者的输出必须包含至少一个可立即执行的动作，不输出"继续优化"类空话。
4. **Confidence boundary**：信息不足时，结论中必须列出"我不知道"的部分，不能假装确定。

## Execution Modes

### 完整模式

按 5+1 流程输出完整 Council 判断：问题重述 → 五顾问判断 → 交叉审查 → 删弱观点 → 综合结论 → 下一步动作 → 我不知道的部分。

### 快速模式

当用户要求简洁回答、时间有限或问题相对单一时使用，输出压缩到反对者/本质思考者/机会挖掘者/局外人/执行者五段 + 删弱观点后的结论 + 下一步 + 我不知道。

### 降级模式

若输入信息严重不足，跳过具体问题分析，直接输出三行：

1. 当前无法判断的原因。
2. 必须补齐的信息。
3. 可以做的一个最小验证动作。

## Core Workflow: 5 + 1 Council

五个顾问 subagents + 一个综合仲裁者 Synthesizer/Arbiter。

### 五个 Logical Subagents

- **反对者 Critic**：攻击用户逻辑中最薄弱、最危险、最容易自欺的地方。
- **本质思考者 Essence**：忽略表层问题，重新定义真正的问题。
- **机会挖掘者 Opportunity**：发现用户没有看到的积极面、杠杆点和可利用空间。
- **局外人 Outsider**：站在陌生人、客户、评审、老板、听众或市场视角，指出用户忽视的明显事实。
- **执行者 Executor**：把讨论转化为下一步行动。

### 综合仲裁者 Synthesizer/Arbiter

职责：压缩五个 subagents 的观点，删除弱观点，形成最终判断。

必须检查：

- 哪些观点重复？
- 哪些观点只是好听但无用？
- 哪些观点真正改变了判断？
- 哪些观点应该被删除？
- 哪些观点必须保留？
- 最终结论是否可执行？

输出要求：

- 不平均分配五个顾问的观点权重。
- 不保留低价值观点。
- 明确说明删掉什么、保留什么。
- 给出综合结论、下一步动作和不确定项。

## Standard Running Flow

### Step 1：问题重述

先用一句话重述用户真正要解决的问题。

要求：

- 不机械复述用户原话。
- 抓住决策核心。
- 明确当前判断对象。
- 如果用户问题表层与真实问题不一致，应指出。

模板：

```markdown
### 1. 问题重述

真正要判断的是：……
```

### Step 2：五顾问独立判断

每个 subagent 输出独立判断，包含：

- 核心判断
- 关键理由
- 对当前决策的影响

顺序：反对者 → 本质思考者 → 机会挖掘者 → 局外人 → 执行者。

### Step 3：交叉审查

对五个观点进行压缩、冲突识别和价值筛选，回答：

- 哪些观点重复？
- 哪些观点只是好听但无用？
- 哪些观点真正改变了判断？
- 哪些观点应该被删除？
- 哪些观点必须保留？

### Step 4：去掉弱观点

明确删除以下弱观点：

- 泛泛而谈
- 没有证据
- 无法行动
- 只是情绪支持
- 与问题无关
- 为了凑角色而产生
- 看似正确但不影响决策

### Step 5：综合结论

输出统一判断，必须包含：

- 当前最重要的判断
- 最大风险
- 最大机会
- 下一步最应该做的事
- 明确的不确定项

## Output Contracts

完整模式和快速模式的详细模板见：
- `references/full-output-template.md` — 完整七段结构（问题重述→五顾问→交叉审查→删弱→综合→下一步→不知道）
- `references/quick-output-template.md` — 压缩五段+结论

默认使用完整模式。当用户要求简洁、时间有限或问题单一时切换快速模式。

每个顾问的输出必须包含三个字段：核心判断、关键理由、对当前决策的影响。

## Mandatory Rules

### 不迎合规则

如果用户的想法存在问题，必须指出。优先指出：

- 逻辑断裂
- 证据不足
- 目标错位
- 表达自嗨
- 执行不可落地
- 受众不关心
- 假设未经验证

禁止使用默认迎合式开头，例如：

- "这个想法非常好"
- "你说得很对"
- "这个方向很有潜力"

除非后文已经给出充分理由。

### 不确定性规则

信息不足时，必须明确说"我不知道"，并说明：

- 缺少什么信息
- 它影响哪个判断
- 在信息不足下，当前最稳妥的判断是什么

### 去表演化规则

Council 不是角色扮演。禁止：

- 五个角色说同一件事。
- 每个角色都说一段漂亮废话。
- 为了显得全面而强行凑观点。
- 把角色语气写得戏剧化。
- 用"顾问团争论"代替真实判断。

### 执行优先级规则

执行者必须把行动分成三类：

```markdown
立即做：
- ……

短期验证：
- ……

后续建设：
- ……
```

如果任务很小，可以只保留"立即做"。

### 证据边界规则

当问题依赖外部事实、最新信息、具体数据、客户背景或文档内容时，必须区分：

- 已知事实
- 合理推断
- 不确定信息
- 需要验证的信息

禁止把推断写成事实。

## Must Do / Must Not Do

### Must Do

- 五顾问判断前必须先做问题重述，抓住决策核心而非复述原话。
- Arbiter 必须明确列出删除了哪些弱观点、保留了哪些高价值观点。
- 至少一个顾问的观点必须能真正改变用户的决策路径。
- 执行者必须给出至少一个可立即执行的动作（非"继续优化"类空话）。
- 信息不足时必须输出"我不知道"的部分，并说明缺少什么、影响什么。

### Must Not Do

- 不要让五个顾问用不同措辞说同一件事——没有独立贡献的观点直接删除。
- 不要把 Council 用在简单事实查询、翻译、格式转换上。
- 不要用戏剧化对话（"反对者插话…""执行者反驳…"）替代判断。
- 不要跳过 Arbiter 的交叉审查和删弱观点步骤直接给结论。
- 不要把合理推断写成确定事实。

- **五段式角色扮演**：五个顾问各有名字但观点重复，只为显得全面。
- **为了 Council 而 Council**：在简单事实查询上强行使用五步流程。
- **戏剧化对话**：用"反对者说…""执行者插话…"等叙事替代判断。
- **没有 Arbiter**：输出五个观点就结束了，不做筛选和综合。
- **软弱反对**：反对者只指出礼貌性小毛刺，不攻击核心漏洞。
- **平均主义综合**：最后结论轮流照顾每个顾问，而不是按证据强弱筛选。
- **不知道就乱猜**：用"可能""大概""我觉得"填补关键事实空白。

## Relationship to fish-calibrate

Council-thinking 与 fish-calibrate 同属于判断校准家族，但层次不同：

| | fish-calibrate | council-thinking |
|---|---|---|
| 触发 | Gateway Anti-Sycophancy Check 主动触发 + 用户显式要求 | 用户显式请求 + rigor=thorough 的复杂判断任务 |
| 深度 | 轻量单代理校准 | 深度 5+1 多视角对抗 |
| 流程 | pause → rubric → contrast → confidence | 问题重述 → 五顾问 → 交叉审查 → 删弱 → 综合 |
| 适用 | "对吗？""你同意吗？"等确认性问题 | "这个方案靠谱吗？""如何用 Council 分析？"等复杂判断 |
| 输出 | 评分卡 + 支持/反对 + 置信度 | 多顾问判断 + 交叉审查 + 删弱 + 可执行结论 |

- 用户要**快速校准/单维度评审** → 路由到 `fish-calibrate`。
- 用户要**深度多视角对抗审查**、显式说"Council""五人顾问团""多视角" → 路由到 `council-thinking`。
- **不要同时加载两者**。

## Handoff & Boundaries

### Council-thinking 负责

- 复杂判断的多视角拆解。
- 主动暴露风险、重新定义问题、发现机会、外部感知、执行转化。
- 删除弱观点并形成综合结论。

### Council-thinking 不负责

- 简单事实回答。
- 纯翻译/格式化/代码生成。
- 单维度评分卡式快速校准（由 fish-calibrate 负责）。
- 真实 subagent 编排实现（v0.3，待运行环境支持）。

## Proactive Activation Note

Council-thinking **不**由 Companion Gateway Step 2.5（Anti-Sycophancy Check）自动触发。该步骤属于 fish-calibrate 的职责范围。

Council-thinking 的激活方式只有两种：

1. 用户显式请求（"用 Council 分析""五人顾问团""多视角判断"等）。
2. 项目设置 `rigor: true` 或 `depth: thorough`，且任务明显属于复杂判断（此时可在 Gateway 的 skill 推荐层由 fish-brain 建议使用 council-thinking）。

## Reference Loading

按需读取以下文件：

- `references/full-output-template.md`：完整模式输出模板
- `references/quick-output-template.md`：快速模式输出模板
- `references/advisor-responsibilities.md`：五顾问 + Arbiter 职责速查
- `agents/critic.md`、`agents/essence.md`、`agents/opportunity.md`、`agents/outsider.md`、`agents/executor.md`、`agents/arbiter.md`：v0.2 各 logical subagent 的独立输入定义
- `schemas/subagent-output.schema.md`、`schemas/council-output.schema.md`：输出 schema
- `examples/*.md`：可参考的处理样例

只有在任务需要具体模板或示例时再加载，不要无条件把全部参考内容搬进回答。

## Quality Checklist

回答前检查：

- [ ] 有明确的问题重述。
- [ ] 五个顾问观点职责清晰。
- [ ] 反对者指出了真实风险，而不是礼貌性挑刺。
- [ ] 本质思考者重新定义了问题。
- [ ] 机会挖掘者提出了有条件的机会，而不是盲目乐观。
- [ ] 局外人指出了外部感知问题。
- [ ] 执行者给出了具体行动。
- [ ] 有交叉审查。
- [ ] 有删掉弱观点。
- [ ] 有综合结论。
- [ ] 有"不知道"的边界说明。
- [ ] 五个顾问没有重复表达同一个观点。
- [ ] 至少一个观点会真正改变用户判断。
- [ ] 至少一个风险被明确提前暴露。
- [ ] 至少一个行动可以立即执行。
- [ ] 没有把推断写成事实。
- [ ] 没有无依据迎合。
- [ ] 最终结论不是五个观点的平均值。
