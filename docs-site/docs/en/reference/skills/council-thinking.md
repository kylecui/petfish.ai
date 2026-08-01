# council-thinking

> Pack: **calibrate**

五人顾问团多视角对抗式判断，用于方案评估、战略判断、产品定位、技术路线、研究设计等复杂决策。5个logical subagents（反对者/本质思考/机会挖掘/局外人/执行者）+Arbiter删除弱观点，输出可执行结论。比fish-calibrate更深。显式触发：用Council分析、五人顾问团审查、多视角评估、对抗式审查、不要迎合我。/ Council: multi-perspective adversarial review with 5 subagents + Arbiter. Triggers: "Council analysis", "five-advisor review", "adversarial review", "multi-perspective evaluation".

**Compatibility:** opencode

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
- 五个顾问是 **Council Members**。优先作为独立 subagent 执行（确保视角独立性）；运行环境不支持时降级为逻辑角色模拟。
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

## Execution Strategy

Council Thinking 有两种执行路径，**按优先级自动选择**：

### Path A: Subagent Orchestration（优先）

当运行环境支持 `task()` 或等价的 subagent 调用时（如 OpenCode），**必须**使用真实 subagent：

1. **主代理**执行 Step 1（问题重述），生成 Council 输入。
2. **并行启动 5 个独立 subagent**（`oracle` 类型，`run_in_background=true`），每个加载对应 agent prompt（`agents/critic.md` 等）：
   ```
   task(subagent_type="oracle", prompt=<critic_prompt + 用户问题>, run_in_background=true)
   task(subagent_type="oracle", prompt=<essence_prompt + 用户问题>, run_in_background=true)
   task(subagent_type="oracle", prompt=<opportunity_prompt + 用户问题>, run_in_background=true)

*... (320 more lines in full SKILL.md)*
