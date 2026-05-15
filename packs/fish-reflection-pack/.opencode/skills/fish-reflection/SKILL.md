---
name: fish-reflection
description: 结构化反思与经验沉淀。Use when 反思, reflect, what went wrong, lessons learned, 复盘, 经验总结, 失败分析, root cause analysis, why did this fail, 返工原因, rework analysis, postmortem, 教训, takeaway, or when user corrects agent output, or when same operation fails 2+ times consecutively. Turns one-off corrections into reusable prevention rules and project knowledge assets via L1 instant reflection, L2 task debrief, and L3 guidance file generation.
compatibility: opencode
metadata:
  version: "0.1.0"
  owner: "Petfish"
---

# Fish Reflection — 结构化反思与经验沉淀

## Purpose

将Agent协作过程中的失败、纠偏和经验压缩成可复用的规则、检查项和指导文件。

核心公式：

```
反思 = 失败/纠偏信号 → 根因分析 → 预防规则 → 知识沉淀
```

目标不是"让Agent多想想"，而是减少重复返工。输出不是漂亮的反思文字，而是具体的预防规则。

## Triggers/Activation

### 三个触发条件（仅这三种，不扩展）

- **T1: 用户纠正/返工** — 先完成修正，然后内联L1
- **T2: 重复失败（2+次）** — 暂停，L1分析失败模式，再继续
- **T3: 显式请求** — 根据规模选择L1/L2/L3

**不触发**：首次调试、简单任务（typo/格式）、需求变更、外部因素失败。

完整的识别信号、排除信号、计数规则和边界判定见 `references/trigger-patterns.md`。

## Three-Level Model

### L1: 即时反思（Instant Reflection）

**触发**：T1或T2信号出现时。

**输出**：内联在修正/暂停后，3-5行：

```
🪞 反思：[trigger简述]
根因：[具体原因，1-2句]
预防：[具体规则，可执行]
```

**要求**：
- 不打断工作流，紧跟修正之后
- prevention_rule必须具体可执行，禁止"下次更仔细"
- 不写文件，仅内联输出

### L2: 任务复盘（Task Debrief）

**触发**：T3显式请求 + 当前任务有明显的失败-修正链。

**输出**：写入 `.opencode/reflections/` 目录，Markdown格式，包含：失败-修正链表格（#/触发/根因/修正动作/预防规则）、关键教训列表、沉淀建议（是否写入AGENTS.md + scope判定）。

**文件命名**：`YYYY-MM-DD-[简述].md`

### L3: 指导文件（Guidance File）

**触发**：T3显式请求 + 发现跨任务/跨项目的通用模式。

**输出**：独立文件写入 `.opencode/reflections/guidance/`，包含：适用范围、具体规则列表、反例说明、来源追溯。

**注意**：L3产出如有普遍价值，应建议沉淀到AGENTS.md `开发经验沉淀` section。

## Reflection Card（4字段）

每次反思的最小记录单元。格式规范、完整示例和质量评分标准见 `references/reflection-card-template.md`。

4个字段：`trigger`、`root_cause`、`prevention_rule`、`scope`（file/project/universal）。

## Action States

反思后输出以下动作之一：PROCEED（继续）、REVISE（修改方案）、VERIFY（额外验证）、CLARIFY（向用户确认）、STOP（暂停等待指示）、RECORD（写入反思文件）、ESCALATE（咨询Oracle）。

## Check Dimensions（仅L2/L3使用）

L2/L3时从6个维度检查：目标理解、约束遵守、证据依据、推理链路、输出规范、沉淀价值。

## Anti-Patterns（硬性禁止）

完整的10条反面模式、错误/正确示范见 `references/anti-patterns.md`。执行反思前必读该文件。

## Output Directory

```
.opencode/reflections/
├── 2026-05-15-installer-escape-fix.md    # L2 task debrief
├── 2026-05-10-schema-field-mismatch.md   # L2 task debrief
└── guidance/
    └── bash-embedded-python.md            # L3 guidance file
```

## Session Start Behavior

在session开始时，如果 `.opencode/reflections/` 目录存在且非空，扫描最近5个反思文件的prevention_rule，作为当前session的额外注意事项。不阻塞，不输出，静默加载。

## Relationship to AGENTS.md `开发经验沉淀`

- `开发经验沉淀` 是手动维护的、经过验证的通用经验
- `.opencode/reflections/` 是反思skill的自动产出，可能包含项目特定或尚未验证的经验
- 反思产出 → 验证有效 → scope=universal → 建议沉淀到 `开发经验沉淀`
- 反思skill不直接修改AGENTS.md，只建议

## Boundaries

- 反思skill是纯指令skill，v1不包含脚本
- 反思不替代调试——"怎么修bug"是调试，"为什么会犯这个bug"是反思
- 反思不替代QA——QA是系统性检查，反思是事件驱动的学习
- 反思不替代Oracle——复杂架构决策交给Oracle，反思只处理"为什么上次做错了"
- 反思不是always-on——只在三个触发条件满足时激活，不加入Companion Gateway
