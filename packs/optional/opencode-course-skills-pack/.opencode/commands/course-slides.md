---
description: 把课程正文lesson.md转成课件幻灯片：slide outline JSON → ppt-writer build_deck → qa_deck，产出slides/<lesson>.pptx（ppt pack未装时优雅降级）
---
请把指定的课程正文（lesson.md）转化为课件幻灯片。

目标课程文件与要求：
$ARGUMENTS

前置条件：
1. 课程正文已存在于 `docs/02-content/<module>/`（含目标/示例/练习/时长标记的结构化lesson.md）
2. ppt pack已安装：检查 `.opencode/skills/ppt-writer/SKILL.md` 是否存在

工作流：

1. **能力检测（先于一切）**：若 `.opencode/skills/ppt-writer/` 不存在，向用户提示安装命令 `/petfish install ppt` 后停止——**不硬失败、不臆造替代渲染方案**；其余前置检查照常报告
2. **读取lesson**：解析lesson.md结构（标题/要点/示例/练习/小结/时长预算）
3. **生成slide outline JSON**：每个lesson一节，保存到 `docs/02-content/<module>/slides/<lesson>.outline.json`，字段：
   - `title`：节标题（沿用lesson标题）
   - `points`：要点，≤5条（每条≤15字，从正文提炼，不整段搬运）
   - `visual`：图示建议（流程图/对比表/代码块/架构图/无需图示）
   - `speaker_notes`：讲者备注（该页具体讲解提示、时间预算、互动点；不写"讲解本页"这类空话）
4. **转换为deck spec**：把outline JSON映射为ppt-writer的deck spec结构（`meta.title` / `theme.*` / `slides[]`，每页`type`/`title`/`body`或`items`；schema见ppt-writer的 `references/deck-spec-schema.md`）
5. **构建PPTX**：在ppt-writer skill目录下执行 `uv run scripts/build_deck.py <spec.json> --out docs/02-content/<module>/slides/<lesson>.pptx`
6. **QA验证**：`uv run scripts/qa_deck.py <pptx> --out <qa.json>`；发现问题→修复→重建→复验，直到QA通过（生成→QA→修复→复验为强制闭环，不得跳过qa_deck）
7. **报告**：输出文件路径、页数、QA结论与遗留限制

要求：
- 每页要点≤5条，超出的拆页或裁剪
- 产出路径固定：`docs/02-content/<module>/slides/<lesson>.pptx`
- outline JSON是course pack与ppt pack之间的松耦合接口文件，单独落盘保存（不内联进命令输出即焚）
- 讲者备注含时长预算，与lesson.md的时长标记对齐
