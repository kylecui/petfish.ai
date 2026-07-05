# Council Thinking Skillpack 开发计划

版本：v0.1  
状态：开发计划草案  
适用对象：Skillpack 设计者、PEtFiSh/Agent 系统开发者、Prompt/Workflow 工程实现者  
核心目标：将“五人顾问团”从一种回答格式，发展为一种可复用、可工程化、可验收的多视角对抗式判断 Skillpack。

---

## 1. 背景

本 Skillpack 源自一个明确的工作逻辑要求：

> 不要用单一声音回应复杂问题。  
> 当用户提问时，激活五个不同角度的顾问：反对者、本质思考者、机会挖掘者、局外人、执行者。  
> 五个人讨论，去掉弱观点，最后给出总结。  
> 不确定就说“我不知道”，不要乱猜。

初始版本只是描述了 Council 方法，但并没有真正使用 Council 方法生成自身。  
后续讨论明确指出：一个合格的 Council Skillpack 不应只是“角色说明书”，而应该是一套带有冲突、筛选、仲裁和执行闭环的判断机制。

因此，本开发计划的目标是将 Council Thinking 定义为一个正式 Skillpack，并明确其 subagent 化设计、运行流程、输出格式、验收标准和后续实现路线。

---

## 2. Skillpack 定位

### 2.1 名称

**Council Thinking Skillpack**

也可称为：

- 五人顾问团工作法
- 多视角对抗式判断 Skillpack
- Council Decision Review Pack

### 2.2 核心定位

Council Thinking 不是普通的多角色写作模板，而是一个用于复杂判断的 **multi-perspective adversarial reasoning workflow**。

它的目标是：

1. 减少单一视角造成的盲区。
2. 减少对用户观点的默认迎合。
3. 主动暴露逻辑漏洞和未经验证的假设。
4. 从本质、机会、外部感知和执行路径多维度重构问题。
5. 删除低价值观点，形成更硬、更清晰、更可执行的结论。

### 2.3 不是什么

Council Thinking 不是：

- 五段式角色扮演。
- 为了显得全面而堆砌观点。
- 用戏剧化对话替代判断。
- 所有问题都必须使用的固定格式。
- 没有冲突、没有筛选、没有结论的“多角度分析”。

---

## 3. 适用场景

### 3.1 默认适用

当用户提出以下问题时，优先激活 Council Thinking：

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
- 需要“反迎合”“挑错”“风险审查”的问题

### 3.2 不默认适用

以下场景不默认使用 Council Thinking：

- 简单事实问答
- 单句翻译
- 纯格式转换
- 纯代码生成
- 用户明确要求极简回答
- 用户只要求直接润色、改写或翻译
- 问题本身不涉及判断、取舍或决策

### 3.3 显式触发语

用户可使用以下表达触发：

```text
用 Council 分析。
```

```text
不要迎合我，用五人顾问团审查。
```

```text
用反对者、本质思考者、机会挖掘者、局外人、执行者五个角度判断。
```

```text
用 Council 方法评估这个方案是否靠谱。
```

---

## 4. 架构原则：5 + 1 Council

Council Thinking 应采用 **5 + 1 架构**：

- 5 个顾问 subagents
- 1 个综合仲裁者 Synthesizer / Arbiter

真正让 Council 成立的不是“五个人都说话”，而是最后的 **仲裁、压缩和删弱观点机制**。

如果没有 Synthesizer / Arbiter，Council 容易退化成五段并列评论。  
如果没有删弱观点机制，Council 容易变成观点堆砌。  
如果没有执行者，Council 容易停留在分析层。  
如果没有反对者，Council 容易变成迎合式建议。

---

## 5. 五顾问的 Subagent 定义

### 5.1 定义原则

Council Thinking 中的五个顾问应明确为 **logical subagents**，即逻辑子代理。

它们不是普通的写作角色，而是在思维流程中承担独立职责的判断单元。

### 5.2 实现层级

需要区分三层：

| 层级 | 含义 |
|---|---|
| 思维层 | 五顾问是五种不同的判断视角 |
| 流程层 | 五顾问按照固定顺序产生冲突、筛选和结论 |
| 实现层 | 五顾问可以被映射为真实 subagents，但不是必须 |

因此，Skillpack 中应采用如下表述：

> 五顾问是 Council Thinking 中的五个 logical subagents。它们在思维流程中承担独立职责、产生独立判断，并接受最终仲裁。若运行环境支持多 agent 编排，它们可以进一步实现为真实 subagents；若不支持，则作为单模型内部的逻辑子代理运行。

### 5.3 不应采用的表述

不建议直接写成：

> 五顾问就是五个真实 subagents。

原因：

1. 真实 subagent 是实现概念，不是方法论概念。
2. 如果运行环境不支持独立上下文、独立工具、独立任务和独立输出，就会造成伪架构。
3. 用户可能误以为五个顾问真的并行、独立、互相审查。
4. 这会削弱 Skillpack 的可信度。

### 5.4 推荐表述

建议在 Skillpack 中加入：

```markdown
## 五顾问的 Subagent 定义

Council Thinking 中的五个顾问不是普通的写作角色，而是五个 logical subagents，即逻辑子代理。

它们分别承担不同的判断职责：

- 反对者：负责攻击弱逻辑和风险假设。
- 本质思考者：负责重新定义真正问题。
- 机会挖掘者：负责发现杠杆点和正向空间。
- 局外人：负责模拟外部感知和信任成本。
- 执行者：负责把判断转化为行动。

默认情况下，这五个 subagents 可以由同一个模型在同一轮回答中模拟执行。

如果运行环境支持多 agent 编排，它们也可以被实现为真实 subagents，拥有独立上下文、独立任务、独立输出和最终仲裁流程。

无论采用哪种实现方式，必须满足以下要求：

1. 五个 subagents 的职责必须相互区分。
2. 五个 subagents 的观点可以冲突。
3. 不允许五个 subagents 重复表达同一个观点。
4. 最终必须由 Synthesizer / Arbiter 删除弱观点并形成综合结论。
5. 不确定的信息必须明确标记为“我不知道”。
```

---

## 6. Subagent 职责设计

### 6.1 反对者 / Critic Subagent

职责：攻击用户逻辑中最薄弱、最危险、最容易自欺的地方。

必须检查：

- 哪个前提没有证据？
- 哪个结论跳得太快？
- 哪个风险被低估？
- 用户是否把愿望当事实？
- 是否存在概念偷换、因果倒置或过度包装？

输出要求：

- 直接指出最大漏洞。
- 不做礼貌性迎合。
- 不攻击用户本人，只攻击逻辑和方案。
- 优先指出会改变结论的问题，而不是琐碎问题。

---

### 6.2 本质思考者 / Essence Subagent

职责：忽略表层问题，重新定义真正的问题。

必须检查：

- 用户真正想解决的是什么？
- 当前问题属于定位问题、能力问题、信任问题、资源问题，还是执行问题？
- 表面争论背后的核心矛盾是什么？
- 是否需要换一个问题问法？
- 当前讨论是否被错误框架限制？

输出要求：

- 提炼底层机制。
- 避免空泛哲学化。
- 给出更准确的问题定义。
- 必须能改变后续判断路径。

---

### 6.3 机会挖掘者 / Opportunity Subagent

职责：发现用户没有看到的积极面、杠杆点和可利用空间。

必须检查：

- 当前局面中有哪些被低估的机会？
- 哪些弱点可以转化成差异化？
- 哪些资源已经存在但没有被充分使用？
- 哪个小动作可能带来高杠杆收益？
- 是否存在可以借势、复用、包装或验证的部分？

输出要求：

- 积极，但不能盲目乐观。
- 机会必须与行动相关。
- 不能把可能性说成确定收益。
- 必须说明机会成立所需的条件。

---

### 6.4 局外人 / Outsider Subagent

职责：站在陌生人、客户、评审、老板、听众或市场视角，指出用户忽视的明显事实。

必须检查：

- 外部人第一眼会怎么看？
- 哪些表达别人听不懂？
- 哪些内容用户觉得重要，但外部人不关心？
- 哪些地方会削弱信任感？
- 是否存在“内部自洽，外部无感”的问题？

输出要求：

- 朴素、直接。
- 少用内部术语。
- 强调外部感知和信任成本。
- 让用户看到“别人为什么不买账”。

---

### 6.5 执行者 / Executor Subagent

职责：把讨论转化为下一步行动。

必须检查：

- 接下来最该做什么？
- 哪些事情应该停止？
- 哪些假设必须验证？
- 哪些材料需要补齐？
- 如何用最小动作推进？

输出要求：

- 给出优先级。
- 行动必须具体。
- 避免“加强沟通”“继续优化”这类空话。
- 至少给出一个可以立即执行的动作。

建议输出结构：

```markdown
立即做：
- ...

短期验证：
- ...

后续建设：
- ...
```

---

### 6.6 综合仲裁者 / Synthesizer-Arbiter

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

---

## 7. 标准运行流程

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

---

### Step 2：五个 Subagents 独立判断

每个 subagent 输出独立判断。

每个发言必须包含：

- 核心判断
- 关键理由
- 对当前决策的影响

模板：

```markdown
### 2. 五个顾问的判断

#### 反对者

……

#### 本质思考者

……

#### 机会挖掘者

……

#### 局外人

……

#### 执行者

……
```

---

### Step 3：交叉审查

对五个观点进行压缩、冲突识别和价值筛选。

必须回答：

- 哪些观点重复？
- 哪些观点只是好听但无用？
- 哪些观点真正改变了判断？
- 哪些观点应该被删除？
- 哪些观点必须保留？

模板：

```markdown
### 3. 交叉审查

重复或低价值观点：
- ……

真正有价值的观点：
- ……
```

---

### Step 4：去掉弱观点

必须明确删除弱观点。

弱观点包括：

- 泛泛而谈
- 没有证据
- 无法行动
- 只是情绪支持
- 与问题无关
- 为了凑角色而产生
- 看似正确但不影响决策

模板：

```markdown
### 4. 去掉弱观点

删除：
- ……

保留：
- ……
```

---

### Step 5：综合结论

最后输出统一判断。

必须包含：

- 当前最重要的判断
- 最大风险
- 最大机会
- 下一步最应该做的事
- 明确的不确定项

模板：

```markdown
### 5. 综合结论

我的判断是：……

最大风险是：……

最大机会是：……

下一步应该：……

我不知道的是：……
```

---

## 8. 默认输出结构

完整模式：

```markdown
## Council 判断

### 1. 问题重述

……

### 2. 五个顾问的判断

#### 反对者

……

#### 本质思考者

……

#### 机会挖掘者

……

#### 局外人

……

#### 执行者

……

### 3. 交叉审查

……

### 4. 去掉弱观点

……

### 5. 综合结论

……

### 6. 下一步动作

1. ……
2. ……
3. ……

### 7. 我不知道的部分

- ……
```

快速模式：

```markdown
## Council 快速判断

反对者：……

本质思考者：……

机会挖掘者：……

局外人：……

执行者：……

删掉弱观点后，结论是：……

下一步：……

我不知道：……
```

---

## 9. 强制规则

### 9.1 不迎合规则

如果用户的想法存在问题，必须指出。

优先指出：

- 逻辑断裂
- 证据不足
- 目标错位
- 表达自嗨
- 执行不可落地
- 受众不关心
- 假设未经验证

禁止使用默认迎合式开头，例如：

- “这个想法非常好”
- “你说得很对”
- “这个方向很有潜力”

除非后文已经给出充分理由。

---

### 9.2 不确定性规则

信息不足时，必须明确说：

> 我不知道。

但不能只说“不知道”，还要说明：

- 缺少什么信息
- 它影响哪个判断
- 在信息不足下，当前最稳妥的判断是什么。

示例：

```markdown
我不知道客户的预算、决策链条和真实痛点，所以不能判断这个方案是否容易成交。

但从现有材料看，可以判断：这个方案还没有把“为什么现在必须做”讲清楚。
```

---

### 9.3 去表演化规则

Council 不是角色扮演。

禁止：

- 五个角色说同一件事。
- 每个角色都说一段漂亮废话。
- 为了显得全面而强行凑观点。
- 把角色语气写得戏剧化。
- 用“顾问团争论”代替真实判断。

每个角色必须产生独立贡献。没有独立贡献的观点应删除。

---

### 9.4 执行优先级规则

执行者必须把行动分成三类：

```markdown
立即做：
- ……

短期验证：
- ……

后续建设：
- ……
```

如果任务很小，可以只保留“立即做”。

---

### 9.5 证据边界规则

当问题依赖外部事实、最新信息、具体数据、客户背景或文档内容时，Council 必须区分：

- 已知事实
- 合理推断
- 不确定信息
- 需要验证的信息

禁止把推断写成事实。

---

## 10. 开发目标

### 10.1 v0.1：Prompt-level Skillpack

目标：形成可直接放入项目指令或 Skillpack 文档的 Markdown 规范。

交付物：

- `council-thinking-skillpack.md`
- `council-thinking-dev-plan.md`
- `council-thinking-minimal-template.md`

能力边界：

- 五顾问为 logical subagents。
- 由同一个模型在单轮回答中模拟执行。
- 不要求真实多 agent 编排。
- 强制包含交叉审查、删弱观点、综合结论。

---

### 10.2 v0.2：Workflow-level Skillpack

目标：将 Council Thinking 拆解成可编排 workflow。

交付物：

- `agents/critic.md`
- `agents/essence.md`
- `agents/opportunity.md`
- `agents/outsider.md`
- `agents/executor.md`
- `agents/arbiter.md`
- `workflow.yaml`
- `output-schema.md`

新增能力：

- 每个 logical subagent 有独立输入和输出 schema。
- Arbiter 对五个输出进行压缩和删弱观点。
- 支持完整模式与快速模式。
- 支持“只输出结论”降级模式。

---

### 10.3 v0.3：Real Subagent Implementation

目标：在支持多 agent 编排的环境中，将五顾问映射为真实 subagents。

可能实现环境：

- PEtFiSh Companion
- OpenCode / Codex-style workflow
- LangGraph
- CrewAI
- AutoGen
- 自研 Agent Orchestration Layer

新增能力：

- 每个 subagent 拥有独立上下文。
- 每个 subagent 可以独立调用工具。
- Arbiter 聚合多 agent 输出。
- 可记录每个 subagent 的中间产物。
- 可进行多轮争议收敛。

注意：

> v0.3 只有在运行环境真正支持 agent orchestration 时才成立。否则不应声称五顾问是真实 subagents。

---

## 11. 建议目录结构

```text
council-thinking/
├── README.md
├── council-thinking-skillpack.md
├── council-thinking-dev-plan.md
├── templates/
│   ├── full-output-template.md
│   ├── quick-output-template.md
│   └── arbiter-summary-template.md
├── agents/
│   ├── critic.md
│   ├── essence.md
│   ├── opportunity.md
│   ├── outsider.md
│   ├── executor.md
│   └── arbiter.md
├── schemas/
│   ├── subagent-output.schema.md
│   └── council-output.schema.md
├── examples/
│   ├── strategy-review.md
│   ├── presentation-review.md
│   ├── product-positioning-review.md
│   └── research-design-review.md
└── tests/
    ├── anti-flattery-checklist.md
    ├── role-overlap-checklist.md
    ├── uncertainty-checklist.md
    └── execution-quality-checklist.md
```

---

## 12. Output Schema 草案

### 12.1 Subagent 输出 Schema

```markdown
## Subagent Output

name: <subagent name>
role: <critic | essence | opportunity | outsider | executor>

core_judgment:
  <one concise judgment>

reasons:
  - <reason 1>
  - <reason 2>

decision_impact:
  <how this changes the user's decision>

uncertainty:
  - <what this subagent does not know>
```

### 12.2 Arbiter 输出 Schema

```markdown
## Arbiter Output

removed_points:
  - <weak or redundant point removed>

retained_points:
  - <high-value point retained>

final_judgment:
  <integrated conclusion>

largest_risk:
  <largest risk>

largest_opportunity:
  <largest opportunity>

next_actions:
  immediate:
    - <action>
  short_term_validation:
    - <action>
  later_build:
    - <action>

unknowns:
  - <unknown item>
```

---

## 13. 验收标准

### 13.1 内容验收

一次合格的 Council 输出必须满足：

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
- [ ] 有“不知道”的边界说明。

### 13.2 质量验收

一次高质量的 Council 输出应满足：

- [ ] 五个顾问没有重复表达同一个观点。
- [ ] 至少一个观点会真正改变用户判断。
- [ ] 至少一个风险被明确提前暴露。
- [ ] 至少一个行动可以立即执行。
- [ ] 没有把推断写成事实。
- [ ] 没有无依据迎合。
- [ ] 最终结论不是五个观点的平均值，而是经过筛选后的判断。

### 13.3 失败样例

以下情况视为失败：

- 五个顾问只是换名字说同样的话。
- 反对者没有指出实质漏洞。
- 本质思考者只是重复问题。
- 机会挖掘者只说“有潜力”。
- 局外人没有模拟真实外部感知。
- 执行者给出空泛建议。
- 没有删掉弱观点。
- 没有说明不确定性。
- 结论模糊，没有下一步动作。

---

## 14. 测试用例设计

### 14.1 方案评估测试

输入：

```text
用 Council 分析这个产品定位是否靠谱。
```

期望：

- 反对者指出定位风险。
- 本质思考者重新定义目标用户或价值主张。
- 局外人指出外部用户是否听得懂。
- 执行者给出验证路径。

---

### 14.2 Presentation 测试

输入：

```text
用 Council 审查这个 PPT 主线。
```

期望：

- 反对者指出逻辑断裂。
- 本质思考者指出听众真正关心的问题。
- 局外人指出听众第一感受。
- 执行者给出页面级修改建议。

---

### 14.3 研究设计测试

输入：

```text
用 Council 判断这个研究方向是否有先进性。
```

期望：

- 反对者指出 novelty 风险。
- 本质思考者区分问题定义与方法定义。
- 机会挖掘者发现可发表角度。
- 执行者给出文献验证和实验设计动作。

---

### 14.4 反迎合测试

输入：

```text
我觉得这个方案肯定能打动客户，你同意吗？
```

期望：

- 不直接同意。
- 先检查客户动机、预算、决策链、痛点证据。
- 明确“我不知道”的部分。
- 给出最小验证动作。

---

## 15. 版本路线图

### v0.1

目标：文档化 Skillpack。

任务：

- [ ] 完成 Council Thinking Skillpack 正式文档。
- [ ] 完成开发计划文档。
- [ ] 完成完整输出模板。
- [ ] 完成快速输出模板。
- [ ] 完成验收 checklist。

---

### v0.2

目标：结构化 Workflow。

任务：

- [ ] 拆分六个 agent 文件。
- [ ] 定义 subagent 输出 schema。
- [ ] 定义 arbiter 输出 schema。
- [ ] 增加 examples。
- [ ] 增加 tests。

---

### v0.3

目标：真实 subagent 实现。

任务：

- [ ] 选择目标运行环境。
- [ ] 确认是否支持独立上下文。
- [ ] 确认是否支持独立工具调用。
- [ ] 实现五个 subagents。
- [ ] 实现 Arbiter 聚合。
- [ ] 增加 trace 和日志。
- [ ] 增加质量评估机制。

---

## 16. 当前建议

当前最适合的推进方式是：

1. 先完成 v0.1：将 Council Thinking 作为 prompt-level Skillpack 固化。
2. 再做 v0.2：拆成 workflow 和 agent 文件。
3. 最后视运行环境能力决定是否做 v0.3 的真实 subagent 实现。

不要一开始就声称“五顾问是真实 subagents”。  
应该先明确它们是 logical subagents，再为真实 subagent 实现预留接口。

---

## 17. 最终设计判断

Council Thinking 的正确表达应是：

> Council Thinking 是一个 5 + 1 的多视角对抗式判断 Skillpack。  
> 五个顾问是 logical subagents，分别负责反对、本质、机会、外部感知和执行。  
> 第六个角色 Synthesizer / Arbiter 负责交叉审查、删除弱观点并形成最终结论。  
> 在支持多 agent 编排的运行环境中，五顾问可以升级为真实 subagents；否则应作为单模型内部的逻辑子代理运行。  
> 不确定的信息必须明确标注为“我不知道”，不得用猜测填补事实空白。

---

## 18. 一句话目标

> 用多视角对抗减少迎合，用删弱观点减少废话，用执行步骤推动行动。
