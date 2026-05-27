---
name: ppt-writer
description: Create/rewrite/restructure/update/validate/export PPT/PPTX decks (课件、提案、汇报、论文、技术方案). Trigger for 从Markdown/文档/纪要/旧PPT生成新deck, template/style unification, per-slide rewrite plans, build_deck + qa_deck workflow, visual QA, and iterative generate→QA→fix→re-verify delivery.
license: MIT
compatibility: opencode; requires uv for bundled Python scripts; optional LibreOffice and Poppler for visual QA; Node/PptxGenJS may be used for advanced custom layouts when available.
metadata:
  version: "1.0.0"
  scope: powerpoint-authoring-editing
  author: kylecui-skill-pack
---

# PPT Writer Skill

## 目标

把用户给出的材料、提纲、旧PPT或改版brief转化为结构清晰、可讲述、可审查、可迭代的PPTX文件。默认不是“把文字塞进幻灯片”，而是先做叙事结构和页面角色设计，再生成并验证。

适用任务：

- 从Markdown、文档、会议纪要、研究材料或用户提纲生成PPTX。
- 改写、重构、扩展、压缩已有PPT。
- 制作课程课件、客户提案、项目汇报、论文汇报、技术方案或战略汇报deck。
- 按模板或目标风格统一标题、结构、页面类型、视觉语言和讲述节奏。
- 对输出PPT进行内容QA和视觉QA。

不适用任务：

- 只读取PPT内容；使用`ppt-reader`。
- 海报、长文档或Word正文写作；使用对应文档类skill。
- 用户要求完全复刻商业模板但未提供授权模板文件时，不要臆造或复制受版权保护设计。

## 默认工作流

### 1. 先生成deck brief

在创建PPT前，先整理以下信息。如果用户没有提供，就根据任务上下文作合理默认，并在输出中说明：

- 受众：高管/客户/学员/评审/内部团队。
- 场景：课程讲解、销售提案、技术汇报、项目复盘、研究报告。
- 时长：5分钟、15分钟、45分钟、半天课程等。
- 目标：说服、教学、汇报、决策、留档。
- 风格：正式、战略、技术、课程、极简、视觉化。
- 页数：默认不超过用户可讲完的数量；宁可拆成结构清楚的少页，不要堆字。

### 2. 设计叙事结构

推荐结构：

- 战略/提案：背景 → 问题 → 判断 → 方案 → 路线图 → 交付/下一步。
- 技术方案：目标 → 约束 → 架构 → 关键机制 → 验证 → 风险 → 下一步。
- 课程课件：概念澄清 → 例子 → 推理分析 → 动手练习 → 反馈提升。
- 论文汇报：问题 → 相关工作缺口 → 方法 → 系统设计 → 实验 → 结论。

输出PPT前，先形成逐页计划：

```markdown
| 页码 | 页面角色 | 标题 | 关键信息 | 推荐版式 | 视觉元素 |
|---|---|---|---|---|---|
```

### 3. 选择生成方式

默认用内置Python脚本从结构化JSON生成基础PPTX：

```bash
uv run scripts/build_deck.py assets/deck_spec_template.json --out output/deck.pptx
```

如果需要复杂图形、精细模板适配、动态图表或高级布局，允许编写临时Python或PptxGenJS脚本，但必须保留可复现的源文件和输入spec。

### 4. 生成deck spec

使用`references/deck-spec-schema.md`中的结构。至少包含：

- `meta.title`
- `theme.primary / secondary / accent / background / text`
- `slides[]`
- 每页的`type`、`title`、`body`或`items`

### 5. 生成PPTX并做QA

```bash
uv run scripts/build_deck.py deck_spec.json --out output/deck.pptx
uv run scripts/qa_deck.py output/deck.pptx --expected-slides 10 --out output/qa.json
```

如用户关心排版或正式交付，必须做视觉QA：

```bash
uv run ../ppt-reader/scripts/render_slides.py output/deck.pptx --out output/rendered --resolution 150
```

然后逐页检查：

- 标题是否溢出或换行异常。
- 正文是否过密。
- 卡片、线条、图标是否对齐。
- 是否有低对比度文字。
- 是否残留占位符。
- 是否存在空页、错页序、重复页。

### 6. 修正与复验

不要在第一次生成后直接宣布完成。至少完成一次：生成 → QA → 修正 → 复验。

## 页面设计原则

- 每页只承担一个主要任务：定义、比较、解释、证明、转场、结论或行动。
- 标题应表达判断，不只是名词。例如“终端安全是AI环境中的必要安全域”，优于“终端安全”。
- 中文PPT避免无意义中英空格：写“Webhook挂载”“Git提交”，不要写“Webhook 挂载”“Git 提交”。
- 正文控制在可讲述范围内；复杂内容拆分为流程图、矩阵、对比表或备注。
- 不要全篇标题加项目符号。至少混合使用：章节页、两栏页、卡片页、流程页、矩阵页、结论页。
- 正式技术材料应保留证据链和术语准确性，避免营销化空话。

## 输出说明模板

```markdown
已生成PPTX：[文件路径]

同时保留：
- deck_spec.json：可复现的结构化输入
- qa.json：机械检查结果
- rendered/：逐页图片，如已做视觉QA

主要结构：
1. [章节]
2. [章节]

需要人工最终确认：
- [字体/模板/图片版权/客户名称/数据来源等]
```

## 质量检查清单

- [ ] deck spec与用户目标一致。
- [ ] 每页标题是完整判断或明确页面任务。
- [ ] 页序形成清晰的总-分-总或任务驱动结构。
- [ ] 没有残留TODO、XXXX、lorem ipsum、占位符。
- [ ] 没有空页或明显重复页。
- [ ] 文本密度适中，复杂内容已拆分。
- [ ] 视觉元素服务内容，不是装饰堆叠。
- [ ] 若源文件是旧PPT，已说明保留、删除、合并和新增内容。
- [ ] 若正式交付，已做视觉渲染检查。

## 脚本

- `scripts/build_deck.py`：从JSON deck spec生成PPTX。
- `scripts/qa_deck.py`：检查PPTX结构、页数、占位符、空页、缺失关系和外部链接。
- `assets/deck_spec_template.json`：可复制修改的最小deck spec。
- `references/deck-spec-schema.md`：deck spec字段说明。
- `references/visual-style-guide.md`：页面视觉与写作规范。
