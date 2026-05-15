# Reflection Levels（反思层级）

fish-reflection采用三层模型，按信号强度和范围递进。

## 层级概览

| 层级 | 名称 | 触发条件 | 输出形式 | 输出位置 | 代价 |
|------|------|---------|---------|---------|------|
| L1 | 即时反思 | T1/T2自动触发 | 内联3-5行 | 当前对话 | 极低 |
| L2 | 任务复盘 | T3显式请求 | Markdown文件 | `.opencode/reflections/` | 低 |
| L3 | 指导文件 | T3 + 通用模式 | Guidance文件 | `.opencode/reflections/guidance/` | 中 |

## L1: 即时反思

**何时**：用户纠正后或连续失败2+次时，自动触发。

**格式**：

```
🪞 反思：[trigger]
根因：[root_cause]
预防：[prevention_rule]
```

**要求**：
- 紧跟修正动作之后，不打断工作流
- 3-5行内完成
- prevention_rule必须具体可执行
- 不写文件

**示例**：

```
🪞 反思：用户指出pack-manifest.json中skill_count为0，实际应为1
根因：手动编写manifest时未校验counts与skills数组长度一致
预防：写manifest后立即检查——skill_count == len(skills), command_count == len(commands), agent_count == len(agents)
```

## L2: 任务复盘

**何时**：用户显式请求复盘，且当前任务有多个失败-修正环节。

**输出模板**：

```markdown
# 任务复盘：[任务简述]

日期：[YYYY-MM-DD]

## 失败-修正链

| # | 触发 | 根因 | 修正动作 | 预防规则 |
|---|------|------|---------|---------|
| 1 | ... | ... | ... | ... |
| 2 | ... | ... | ... | ... |

## 关键教训

1. [从失败-修正链中提炼的教训]
2. [跨步骤的系统性问题]

## 建议沉淀

- scope: [file/project/universal]
- 建议写入AGENTS.md: [是/否，理由]
- Action State: [RECORD/PROCEED/其他]
```

**文件命名**：`YYYY-MM-DD-[kebab-case简述].md`

## L3: 指导文件

**何时**：用户显式请求 + 识别到跨任务/跨项目的通用模式。

**输出模板**：

```markdown
# 指导：[主题]

## 适用范围

[什么场景下适用此指导]

## 规则

1. [具体规则1]
2. [具体规则2]

## 反例

[违反此指导的真实案例]

## 来源

[从哪些反思/任务中归纳]
```

**要求**：
- 只有多次验证过的经验才升级为L3
- L3产出建议同步到AGENTS.md `开发经验沉淀`
- 文件放在 `.opencode/reflections/guidance/` 子目录

## 层级选择决策树

```
信号出现
  ├─ T1/T2 (自动检测) → L1
  └─ T3 (用户请求)
       ├─ 问单个问题 → L1
       ├─ 问整个任务 → L2
       └─ 要求写成通用规则 → L3
```
