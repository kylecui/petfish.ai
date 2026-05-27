# fish-reflection反思Skill设计说明（评审版）

版本：v0.1  
状态：设计评审稿  
日期：2026-05-15  
适用范围：opencode项目级skills、Agent协作流程、复杂任务复盘与经验沉淀  
建议skill名称：`fish-reflection`

---

## 1.文档目的

本文档用于说明`fish-reflection`反思skill的设计思路、边界、触发条件、输出形式和落地结构，供多方评审讨论。

本设计基于一个核心判断：

> 反思skill不应被设计成“让Agent多想想”的泛化提示词，而应被设计成面向Agent协作过程的结构化自检、复盘与经验固化机制。

它的目标不是增加思考时间，而是减少重复返工；不是生成漂亮的反思文字，而是把一次任务中的失败、纠偏和经验压缩成后续Agent可以复用的规则、检查项和指导文件。

---

## 2.背景与问题

在与Agent长期协作时，我们经常遇到以下情况：

- Agent最终能完成任务，但中间经历了不必要的绕路。
- 用户已经给出约束，但Agent在后续执行中遗漏。
- Agent错误理解任务边界，把A任务做成B任务。
- 复杂任务多轮返工后，问题虽然解决，但经验没有沉淀。
- 同类问题在后续任务中再次出现，导致重复消耗时间。
- 工具调用、文件处理、代码修改、文档生成等任务中出现失败，但失败原因没有形成可复用预防规则。

因此，需要一个专门的元技能，帮助Agent在任务前、中、后进行结构化校准和复盘，将协作过程中的经验转化为项目知识资产。

---

## 3.设计定位

### 3.1一句话定位

`fish-reflection`是一个面向Agent协作过程的结构化自检、复盘与经验固化skill。

### 3.2核心公式

```text
fish-reflection = Agent自检 + 任务复盘 + 经验沉淀 + 下次预防
```

### 3.3设计目标

`fish-reflection`应帮助Agent完成以下工作：

1. 在复杂任务执行前，检查目标理解、任务边界、约束条件和必要验证动作。
2. 在任务执行中，识别路径漂移、约束遗漏、工具误用和证据不足。
3. 在任务失败、返工或用户纠错后，分析根因并给出修正动作。
4. 在发现可复用经验时，生成后续可引用的指导性文件。
5. 将重复出现的问题转化为Gotchas、检查项、模板或项目规则。

### 3.4非目标

`fish-reflection`不承担以下职责：

- 不面向用户个人心理反思。
- 不替代QA、代码审查、课程评审、研究笔记等专业skill。
- 不作为skills总调度器。
- 不在每个简单任务中自动触发。
- 不输出隐藏推理链。
- 不把失败简单归因于“信息不足”或“以后更小心”。

---

## 4.与相邻能力的区别

| 能力 | 主要关注点 | 与`fish-reflection`的区别 |
|---|---|---|
| QA skill | 当前输出是否符合标准 | QA关注结果质量；反思关注过程根因与下次预防 |
| Review skill | 当前方案是否合理 | Review偏成品评估；反思偏任务路径和经验沉淀 |
| Anti-sycophancy skill | 是否过度迎合用户 | 反迎合是特定风险；反思覆盖目标、证据、路径、工具、输出和经验 |
| Research note skill | 文献、资料、摘录和灵感记录 | 研究笔记沉淀内容素材；反思沉淀协作经验和预防规则 |
| Project QA | 项目级质量门禁 | 反思可以产生QA检查项，但不直接承担完整质量门禁 |

---

## 5.设计原则

### 5.1面向Agent协作

本skill主要服务Agent在工程协作、文档生成、项目初始化、技能开发、代码修改、研究规划等任务中的自检与复盘，而不是给用户做人生日志或心理反思。

### 5.2必须形成动作决策

每次反思都必须给出明确下一步动作，避免停留在“总结问题”层面。

### 5.3重大返工必须沉淀经验

只在聊天中说明“哪里错了”是不够的。只要某个问题有复现价值，就应沉淀为指导文件、Gotchas、检查项或模板。

### 5.4与其它skills弱耦合

`fish-reflection`可以建议后续使用某类skill，但不主动绑定或调度其它skill。这样可以避免上下文污染和耦合过重。

### 5.5不暴露隐藏思维链

反思输出应是可共享的分析摘要、判断依据和修正动作，而不是完整内部推理过程。

---

## 6.反思等级设计

`fish-reflection`采用四级反思模式。

### 6.1Level 0：静默自检

适用于简单任务或低风险任务。Agent仅进行内部快速检查，不输出反思内容，不生成文件。

检查问题：

```text
目标是否清楚？
是否需要读取文件、搜索、测试或运行工具？
是否存在明显风险？
是否可以直接回答？
```

输出：无。

### 6.2Level 1：即时反思

适用于任务中出现轻微不确定、路径变化、用户补充约束、输出前自检等场景。

典型输出：

```markdown
## 反思结论

- 当前判断：
- 可能风险：
- 修正动作：
- 继续方式：
```

适用场景：

- 用户追加约束。
- 任务目标发生变化。
- 已有输出可能偏离用户风格。
- 需要决定继续写、改写、搜索、验证或停止。
- Agent发现自己可能遗漏了上下文。

### 6.3Level 2：任务复盘

适用于明显返工、失败、用户纠错、工具报错、代码测试失败、文档质量不达标等场景。

典型输出：

```markdown
# 任务复盘

## 原始目标
## 实际过程
## 出现的问题
## 根因分析
## 修正动作
## 下次预防
## 可沉淀规则
```

Level 2可以直接在聊天中输出，也可以作为Level 3文件沉淀的前置材料。

### 6.4Level 3：指导文件沉淀

适用于具有复用价值的经验。此时反思不应只留在对话中，而应生成后续Agent可引用的项目知识文件。

推荐目录：

```text
docs/reflections/
├── README.md
├── 2026-05-15-skill-reflection-design.md
├── 2026-05-15-pdf-to-drawio-failure-review.md
└── 2026-05-15-opencode-config-path-gotchas.md
```

也可在opencode专用项目中使用：

```text
.opencode/reflections/
```

但更推荐`docs/reflections/`，因为反思文档是项目知识资产，不只是工具内部配置。

---

## 7.触发条件

### 7.1显式触发

当用户使用以下表达时，应触发：

```text
反思一下
复盘一下
哪里出了问题
为什么刚才做错了
下次怎么避免
总结经验
沉淀成规则
写成指导文档
```

### 7.2任务路径异常

出现以下情况时，应触发：

- Agent重复询问用户已经提供的信息。
- Agent忽略用户明确约束。
- 输出格式不符合要求。
- 工具使用明显不当。
- 把A任务做成B任务。
- 过早进入实现，未完成必要设计。
- 在缺少证据时给出确定性结论。

### 7.3多轮返工

出现以下情况时，应触发：

- 同一任务被用户纠正两次以上。
- 连续修改仍未满足目标。
- 方案多次被推翻。
- 用户指出“你又忽略了前面说过的要求”。

### 7.4工具或执行失败

出现以下情况时，应触发：

- 代码测试失败。
- 文件生成失败。
- 路径错误。
- 权限错误。
- 构建失败。
- PDF、Docx、PPT、图片等文档处理失败。
- Git、GitHub、部署、容器、脚本执行失败。

### 7.5高影响任务

以下任务即使未失败，也应考虑至少进行Level 1自检：

- 课程体系设计。
- skill包设计。
- 论文规划。
- 项目初始化。
- 架构设计。
- 安全方案。
- 正式对外材料。
- 需要交付给多方评审的文档。

### 7.6可沉淀经验出现

出现以下情况时，应触发Level 3：

- 发现一个常见坑。
- 形成一个新的检查项。
- 用户给出稳定偏好。
- 某类任务形成更优流程。
- 某个skill需要补充Gotchas。
- 某个失败可转化为后续预防规则。

---

## 8.动作状态设计

每次反思必须给出一个或多个动作状态。

```text
PROCEED   继续当前路径
REVISE    修改当前输出
VERIFY    需要搜索、测试、读取文件或运行验证
CLARIFY   必须向用户澄清
STOP      停止当前方向
RECORD    需要沉淀为指导文件
ESCALATE  建议转交更专门的skill或评审流程
```

示例：

```markdown
## 反思结论

状态：REVISE + RECORD

当前问题不是内容不足，而是任务边界发生变化：用户希望该skill主要服务Agent自检，而不是用户个人反思。因此需要重写skill定位，并把“经验沉淀文件”作为一级产物。

修正动作：
1. 将skill定位改为Agent协作自检与复盘。
2. 增加`docs/reflections/`输出规范。
3. 不建立与其它skills的硬依赖，只保留弱耦合接口。
```

---

## 9.核心检查维度

`fish-reflection`应围绕六个维度进行检查。

| 维度 | 核心问题 | 典型风险 |
|---|---|---|
| 目标 | 我是否理解了用户真正想要的结果？ | 做错题、过度扩展、遗漏隐含目标 |
| 约束 | 是否遗漏格式、风格、工具、时间、上下文、已有讨论？ | 重复问、格式不合规、忽略用户偏好 |
| 证据 | 当前结论是否有依据？是否需要引用、搜索、读取文件或测试？ | 编造、过度自信、未经验证 |
| 推理 | 是否存在跳步、偷换概念、迎合用户、单一路径依赖？ | 结论不稳、逻辑断裂 |
| 输出 | 当前输出是否可用、可执行、结构合理、符合用户风格？ | 看似完整但不可落地 |
| 沉淀 | 是否产生可复用规则、模板、Gotcha或eval case？ | 同类错误后续复现 |

---

## 10.输出产物设计

### 10.1即时反思

面向当前任务，短小直接，适合聊天中展示。

模板：

```markdown
## 即时反思

状态：[PROCEED/REVISE/VERIFY/CLARIFY/STOP/RECORD/ESCALATE]

### 当前判断
[一句话说明当前是否偏离目标]

### 主要风险
- [风险1]
- [风险2]

### 修正动作
1. [动作1]
2. [动作2]

### 是否需要沉淀
[是/否；若是，说明沉淀位置]
```

### 10.2任务复盘

面向失败、返工或复杂任务结束后的复盘。

模板：

```markdown
# 任务复盘：[标题]

## 1.原始目标
[用户最初希望完成什么]

## 2.实际过程
[任务如何推进，发生了哪些关键变化]

## 3.出现的问题
[表层问题，不急于归因]

## 4.根因分析
[导致问题的任务理解、流程、证据、工具或输出方面原因]

## 5.修正动作
[当前如何修正]

## 6.下次预防
[下次遇到同类任务时应提前做什么]

## 7.可沉淀规则
- [规则1]
- [规则2]

## 8.适用范围
[适用于哪些任务；不适用于哪些任务]
```

### 10.3反思卡片

反思卡片是最小经验沉淀单位。

模板：

```markdown
# Reflection Card: [标题]

## Context
这次问题出现在哪类任务中？

## Trigger
是什么信号表明需要反思？

## Symptom
表面问题是什么？

## Root Cause
根因是什么？

## Missed Signal
Agent本应提前注意到什么？

## Corrective Action
当前如何修正？

## Preventive Rule
下次遇到类似情况时应提前执行什么规则？

## Reusable Checklist
- [ ] 检查项1
- [ ] 检查项2
- [ ] 检查项3

## Scope
这条经验适用于哪些任务？不适用于哪些任务？
```

### 10.4指导文件

当问题具有项目级复用价值时，应生成指导文件。

推荐模板：

```markdown
# [主题]指导说明

## 1.适用场景
## 2.问题背景
## 3.常见错误
## 4.正确处理流程
## 5.检查清单
## 6.示例
## 7.关联文件或后续动作
```

---

## 11.建议skill目录结构

根据Agent Skills规范，一个skill目录至少包含`SKILL.md`，也可以包含`scripts/`、`references/`和`assets/`等可选目录。`SKILL.md`应包含YAML frontmatter和Markdown正文。

建议结构：

```text
fish-reflection/
├── SKILL.md
├── references/
│   ├── reflection-levels.md
│   ├── trigger-patterns.md
│   ├── reflection-rubric.md
│   └── anti-patterns.md
└── assets/
    ├── quick-reflection-template.md
    ├── task-postmortem-template.md
    ├── reflection-card-template.md
    ├── guidance-file-template.md
    └── lesson-card-template.md
```

第一版暂不建议加入`scripts/`。因为当前核心是流程、模板和判断规则。后续可以在以下情况下增加脚本：

- 自动生成反思文件名。
- 从复盘文件提取lesson cards。
- 检查反思文件是否包含必要字段。
- 将经验项追加到某个`gotchas.md`。
- 将反思记录转换为skill评估用例。

---

## 12.`SKILL.md`设计草案

### 12.1frontmatter草案

```yaml
---
name: fish-reflection
description: Use this skill when an agent needs structured self-check, reflection, task postmortem, error analysis, retry prevention, or lesson learned capture during complex agent collaboration. Trigger when the user asks for 反思, 复盘, 自检, 纠错, 总结经验, or when a task has failed, drifted, required repeated correction, or produced reusable lessons. This skill helps identify task misunderstanding, missed constraints, weak assumptions, evidence gaps, tool misuse, output-quality issues, and preventive rules. Do not use for every simple response.
compatibility: opencode; works as a lightweight meta-skill for agent self-check and project-level reflection records.
metadata:
  version: "0.1.0"
  family: fish
  type: meta-skill
---
```

### 12.2正文结构草案

```markdown
# fish-reflection

## Purpose
## When to Use
## When Not to Use
## Reflection Levels
## Decision States
## Quick Reflection Workflow
## Task Postmortem Workflow
## Guidance File Workflow
## Reflection Card Format
## Anti-patterns
## Output Rules
```

---

## 13.与其它skills的关系

本设计建议采用弱耦合机制。

### 13.1不做硬依赖

`fish-reflection`不应强制调用：

- `anti-sycophancy`
- `course-qa`
- `research-note`
- `code-review`
- `project-initializer`
- 其它专业skill

### 13.2只做建议性转交

当反思发现问题属于其它专业skill处理范围时，可以给出建议：

```markdown
建议后续动作：
- 当前问题属于课程质量控制，可交由课程QA类skill继续处理。
- 当前问题属于证据不足，应进入research或citation类流程。
- 当前问题属于用户偏好遗漏，应更新项目写作规范。
```

### 13.3原因

弱耦合的好处：

1. 避免一次反思加载过多上下文。
2. 避免`fish-reflection`变成总调度器。
3. 降低后续维护成本。
4. 保持其作为元认知工具的边界。

---

## 14.反模式

`fish-reflection`必须避免以下反模式：

1. 不要把反思写成自我辩解。
2. 不要把反思写成空泛总结。
3. 不要暴露完整隐藏推理链。
4. 不要每个简单任务都触发。
5. 不要只说“以后更小心”，必须给出可执行预防规则。
6. 不要把用户已经给出的约束再次作为问题追问。
7. 不要把所有失败都归因于信息不足。
8. 不要在没有证据的情况下编造根因。
9. 不要把反思变成QA报告；QA关注输出，反思关注过程与可复用经验。
10. 不要让反思阻塞任务推进；反思必须服务于下一步动作。

---

## 15.评审关注点

建议评审方重点讨论以下问题。

### 15.1定位是否准确

- 是否同意该skill主要面向Agent自检，而不是用户个人反思？
- 是否同意将“经验沉淀”作为一级目标？
- 是否同意其作为元技能，而不是业务技能？

### 15.2触发条件是否合理

- 当前触发条件是否过宽？
- 是否会导致过多任务触发反思，污染上下文？
- 是否还遗漏了某些高价值触发场景？

### 15.3输出结构是否可用

- Level 1即时反思是否足够轻量？
- Level 2任务复盘是否足以覆盖失败分析？
- Level 3指导文件是否适合长期引用？
- Reflection Card是否适合作为最小沉淀单位？

### 15.4目录结构是否合适

- 反思文件应放在`docs/reflections/`还是`.opencode/reflections/`？
- 是否需要同步生成`docs/gotchas.md`？
- 是否需要与`AGENTS.md`建立引用关系？

### 15.5是否需要脚本

第一版不含`scripts/`。评审方可讨论是否需要增加：

- `scripts/new_reflection.py`
- `scripts/extract_lessons.py`
- `scripts/validate_reflection.py`
- `scripts/update_gotchas.py`

---

## 16.建议落地路线

### 阶段一：设计确认

目标：

- 确认定位、边界、触发条件和输出模板。
- 确认目录结构。
- 确认第一版是否不包含脚本。

产物：

```text
fish-reflection-design.md
```

### 阶段二：生成第一版skill

目标：

- 生成`fish-reflection/SKILL.md`。
- 生成`references/`和`assets/`。
- 保持轻量可读。

产物：

```text
fish-reflection/
├── SKILL.md
├── references/
└── assets/
```

### 阶段三：真实任务试运行

选择3至5个真实任务进行测试：

1. 文档输出返工场景。
2. 代码或工具执行失败场景。
3. 用户纠偏场景。
4. 复杂设计任务输出前自检场景。
5. 可沉淀经验生成指导文件场景。

观察：

- 是否触发过多？
- 是否触发过少？
- 输出是否可执行？
- 反思是否真的减少后续返工？

### 阶段四：沉淀Gotchas和evals

根据真实任务结果，补充：

```text
references/anti-patterns.md
references/trigger-patterns.md
evals/evals.json
```

必要时增加脚本。

---

## 17.初步结论

`fish-reflection`的核心价值不是让Agent表达“我反思了”，而是把一次协作中的问题转化成后续可复用的工程经验。

它应当遵循以下五条铁律：

```text
1. 面向Agent协作，不面向心理反思。
2. 每次反思必须给出下一步动作。
3. 重大返工必须产出可复用经验。
4. 可沉淀经验应写入项目文件，而不只留在聊天上下文。
5. 与其它skills弱耦合，不做总调度器。
```

最终目标是：

> 把不可控的“多想想”，变成可触发、可检查、可沉淀、可复用的Agent协作自检机制。

---

## 18.参考依据

本设计参考了Agent Skills的结构规范、skill描述触发机制、渐进式披露原则、真实任务提炼方法、Gotchas沉淀方法和validation loop思想。

主要依据包括：

- Agent Skill目录结构与`SKILL.md`frontmatter规范。
- skill描述应明确说明“做什么”和“何时使用”，并避免过宽或过窄。
- 大型skill应通过`references/`和`assets/`进行渐进式披露。
- 高质量skill应从真实任务、纠偏、失败案例和项目约束中提炼。
- Agent犯错后被纠正的内容，适合沉淀为Gotchas。
- 多步骤任务应使用检查清单和validation loop减少遗漏。
