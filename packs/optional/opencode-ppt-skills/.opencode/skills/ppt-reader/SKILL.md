---
name: ppt-reader
description: Read/inspect/summarize/audit/compare PPT/PPTX, extract slide inventory (titles, structure, notes, comments, media, links), review templates/layout/placeholders/sensitive info, or produce rewrite briefs and per-slide action plans for ppt-writer. Trigger for 读取/总结/审阅/对比课件、提案、汇报材料 and visual QA requests.
license: MIT
compatibility: opencode; requires uv for bundled Python scripts; optional LibreOffice and Poppler for slide rendering.
metadata:
  version: "1.0.0"
  scope: powerpoint-reading-analysis
  author: kylecui-skill-pack
---

# PPT Reader Skill

## 目标

把PPT/PPTX从“不可控的二进制文件”转化为可审查、可引用、可改写的结构化材料。默认输出不是简单抽取全文，而是形成可继续加工的slide inventory。

适用任务：

- 读取、总结、审阅、对比PPT/PPTX。
- 从课件、提案、汇报材料中抽取大纲、讲解逻辑、章节结构、页标题、备注、图片占位和媒体清单。
- 为后续`ppt-writer`提供重写计划、改版建议、逐页修改清单。
- 检查模板、版式、残留占位符、外部链接、空页、备注内容和潜在敏感信息。

不适用任务：

- 从零创建新PPT；使用`ppt-writer`。
- 大规模批量转换文档；先编写专门批处理脚本或workflow。
- 对扫描图片中文字做高可靠OCR；仅在用户明确要求时再引入OCR工具。

## 默认工作流

1. 确认输入文件路径和目标产物。如果用户没有指定输出格式，默认输出Markdown摘要，并保留JSON结构化结果。
2. 先运行结构化抽取：

```bash
uv run scripts/pptx_extract.py input.pptx --out output/pptx_inventory.json --markdown output/pptx_summary.md
```

3. 读取输出JSON，形成以下分析：
   - 全局：文件名、页数、标题候选、是否含备注、是否含外部链接、是否有疑似占位符。
   - 逐页：页码、标题候选、正文要点、备注、图片/媒体、评论、异常。
   - 叙事结构：总-分-总、问题-分析-方案、背景-挑战-方法-验证等结构是否清晰。
   - 后续动作：哪些页需要合并、拆分、重写、补图、补数据、改标题。
4. 如果用户要求视觉审阅、模板审阅、排版问题或“看起来怎么样”，再渲染为图片：

```bash
uv run scripts/render_slides.py input.pptx --out output/rendered --resolution 150
```

5. 用渲染图做视觉检查：重叠、溢出、低对比度、过密、页边距不足、视觉元素缺失、字体不一致、图表无法读清。

## 输出格式建议

### 简短摘要

```markdown
# PPT读取摘要：[文件名]

## 一句话结论
[整体判断]

## 结构概览
| 页码 | 标题候选 | 主要内容 | 备注/媒体 | 问题 |
|---|---|---|---|---|

## 主要发现
1. [发现]
2. [发现]

## 后续建议
- [建议]
```

### 逐页审阅

```markdown
## Slide [N]：[标题候选]

- 内容：
- 备注：
- 媒体/图片：
- 版式观察：
- 风险或问题：
- 建议动作：保留 / 重写 / 拆分 / 合并 / 补图 / 删除
```

### 为ppt-writer准备的改版brief

```markdown
# PPT改版Brief

## 改版目标
[目标受众、交付场景、讲述时长、风格]

## 保留内容
[保留的页和信息]

## 重构结构
[新的章节和页序]

## 逐页改写计划
| 新页码 | 来源页 | 页面目的 | 关键信息 | 视觉建议 |
|---|---|---|---|---|
```

## 质量检查清单

- [ ] 页数、页序与用户问题一致。
- [ ] 备注和评论已单独标识，没有混入正文。
- [ ] 图片、媒体、图表、外部链接已列入清单。
- [ ] 没有把装饰性文本误判为正文重点。
- [ ] 对不可见或无法解析的内容说明不确定性。
- [ ] 涉及隐私、客户信息、商业机密时，只做必要摘录，不扩散全文。

## 常见陷阱

- 不要只抽取`a:t`文本就宣布完成。PPT的含义通常来自页序、版式、图片、备注和图表。
- 不要把母版页、页脚、日期、版权声明当作正文重点。
- 不要把渲染失败理解为PPT损坏；先检查LibreOffice、字体和外部依赖。
- 不要在未确认目标前直接重写PPT。先形成结构化inventory和改版brief。
- 对模板PPT，重点识别占位符和版式槽位；对内容PPT，重点识别叙事结构和证据链。

## 脚本

- `scripts/pptx_extract.py`：抽取PPTX结构、文本、备注、媒体、外部链接，输出JSON和Markdown。
- `scripts/render_slides.py`：调用LibreOffice和Poppler把PPTX渲染为逐页图片，用于视觉QA。
