# council-thinking

> 包: **calibrate**

五人顾问团多视角对抗式判断。用 Council 分析方案评估、战略判断、产品定位、技术路线、研究设计、课程设计、Presentation主线、逻辑审查、写作结构取舍、是否值得做、如何向客户/评审/老板表达等复杂判断。显式触发：用Council分析、五人顾问团审查、多视角评估、对抗式审查、不要迎合我。比 fish-calibrate 更深：5个logical subagents + Arbiter删除弱观点，输出可执行结论。/ Use Council for multi-perspective adversarial review of strategy, product positioning, tech roadmap, research design, course design, business analysis, logic checks, and how-to-communicate decisions. Triggers: "Council analysis", "five-advisor review", "multi-perspective evaluation", "adversarial review".

**兼容性:** opencode

---

# Council Thinking

## 目的

Council Thinking 是一个用于复杂判断的 **multi-perspective adversarial reasoning workflow**。它不是普通的多角色写作模板，而是一套带有冲突、筛选、仲裁和执行闭环的判断机制。

目标：

1. 减少单一视角造成的盲区。
2. 减少对用户观点的默认迎合。
3. 主动暴露逻辑漏洞和未经验证的假设。
4. 从本质、机会、外部感知和执行路径多维度重构问题。
5. 删除低价值观点，形成更硬、更清晰、更可执行的结论。

## 触发/激活

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

## 核心工作流: 5 + 1 Council

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

## 执行模式

### 完整模式

按 5+1 流程输出完整 Council 判断：问题重述 → 五顾问判断 → 交叉审查 → 删弱观点 → 综合结论 → 下一步动作 → 我不知道的部分。

### 快速模式

当用户要求简洁回答、时间有限或问题相对单一时使用，输出压缩到反对者/本质思考者/机会挖掘者/局外人/执行者五段 + 删弱观点后的结论 + 下一步 + 我不知道。

### 降级模式

若输入信息严重不足，跳过具体问题分析，直接输出三行：

1. 当前无法判断的原因。
2. 必须补齐的信息。
3. 可以做的一个最小验证动作。

## 决策点

1. **Quick vs Full mode**：用户只问"简单判断"或要求简洁时用快速模式；否则用完整模式。
2. **Delete weak points or keep them**：Arbiter 必须明确删除没有证据、无法行动、情绪支持或为了凑角色而产生的观点。
3. **Actionability first**：执行者的输出必须包含至少一个可立即执行的动作，不输出"继续优化"类空话。
4. **Confidence boundary**：信息不足时，结论中必须列出"我不知道"的部分，不能假装确定。