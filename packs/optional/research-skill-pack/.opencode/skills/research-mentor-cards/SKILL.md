---
name: research-mentor-cards
description: 研究导师卡片：按研究阶段（Idea/证据/写作）提供分级建议卡——每张卡带认同度标注（共识≥3独立来源/有出处/有分歧两案并陈/内部实践），配合对抗式提问与阶段路由（接 scientific-gap-finder、research-evidence-ledger、scientific-paper-writer）。用于导师卡片、经验卡片、研究建议卡、论文写作建议、idea评估、mentor cards、advice cards、研究怎么做。Use when 需要分阶段方法论指导，或与上游导师技能做对照。
metadata:
  version: 1.0.0
  author: PEtFiSh
---

# Research Mentor Cards — 分级研究导师卡片

把研究方法论拆成**卡片**：每张卡一条可执行的做法，写明主张、原理、怎么用和出处，并标注**认同度**。卡片是"导师怎么建议"，证据是"研究发现了什么"——两者不混。

## 卡片解剖（七字段，缺一不发布）

```
### <ID> <标题>
- 主张: <一句话，可执行>
- 原理: <为什么这条做法有效>
- 怎么用: <触发时机 + 具体动作>
- 认同度: 共识 | 有出处 | 有分歧 | 内部实践
- 出处: <真实文献：作者 (年份) 标题——禁止编造>
- 适用阶段: idea | evidence | writing
- 对抗式提问: <导师会反问学生的那个问题>
```

## 认同度分级（诚实标注，宁降勿升）

| 级 | 含义 | 标准 |
|---|---|---|
| 共识 | 多个独立来源一致支持 | ≥3 个相互独立的出处 |
| 有出处 | 有明确文献支撑 | 1-2 个出处 |
| 有分歧 | 名家意见不一 | 两方立场+各自出处，都写 |
| 内部实践 | PEtFiSh 自身实践沉淀，无外部文献 | 标注"PEtFiSh 实践"，鼓励外部检验 |

**禁止**：把内部实践标成有出处；给出处编造期刊/卷期；用一张卡替代证据流程。

## 阶段路由（与 pack 现有流程衔接）

| 阶段 | 卡片 | 衔接的执行技能 |
|---|---|---|
| Idea | cards-idea.md（I系列） | scientific-gap-finder（找缺口）、research-insight-log（记灵感） |
| 证据 | cards-evidence.md（R系列） | research-evidence-ledger（证据账本）、research-synthesis（综合） |
| 写作 | cards-writing.md（W系列） | scientific-paper-writer（写论文）、research-quality-reviewer（审查） |

**顺序纪律**：先走 research-router 正常研究流程产出证据，再用卡片审视方法论——卡片不产出证据，只改进做法。

## 使用流程（含对抗式提问）

1. 判定当前阶段（idea / evidence / writing）→ 读对应卡组
2. 逐卡自问该卡的**对抗式提问**；答不上来的卡就是当前薄弱点
3. 把采纳的卡落到对应执行技能里（例：采纳 W02 → 在 scientific-paper-writer 的引言步骤应用 CARS 结构）
4. 有分歧的卡（如 I04）：两案并陈，由研究目标裁决，卡片不替你选

## 对照模式（上游导师技能）

想与 HKUSTDial/Supervisor-Skills、yinwu01/Ducktor 的原版博导经验卡对照时，走 `research-supervisor-bridge`（同 pack 姊妹 skill）——它处理许可证告知、运行时装载和逐能力对照表。上游内容为 CC BY-NC-SA 4.0，本 pack 不收录其任何内容。

## MUST DO

- 出处必须真实：只引用确定存在的作者+标题+年份；记不清就降级为内部实践
- 有分歧卡必须两案并陈，不得只写一方
- 每张卡带对抗式提问——没有提问的卡是清单不是导师

## MUST NOT DO

- 禁止编造/臆测出处（作者、年份、标题都不得猜）
- 禁止把卡片当作证据或引用素材进入研究报告（报告主张仍走 research-evidence-ledger）
- 禁止复制上游 Supervisor-Skills / Ducktor 的卡片内容——机制可参照，表达必须原创
