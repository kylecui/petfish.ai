# 参考来源与取舍说明

## 参考来源

- Agent Skills通用规范：采用`SKILL.md`前置YAML frontmatter，并使用`name`、`description`、`license`、`compatibility`、`metadata`等字段。
- OpenCode技能发现机制：技能放置在`.opencode/skills/<name>/SKILL.md`，也兼容全局OpenCode、Claude和Agents目录。
- 官方PPTX skill思路：PPTX任务应覆盖读取、抽取、模板编辑、从零创建、QA验证；读取可用文本抽取和视觉缩略图，写作应重视视觉设计和验证闭环。
- Skill创建最佳实践：保持技能边界清晰、SKILL.md不过度膨胀、复杂内容放入`references/`，脚本放入`scripts/`，使用eval迭代触发与输出质量。

## 我们的改造

官方PPTX skill是一个覆盖读、写、编辑、合并、拆分的统一大技能。它适合通用生产环境，但对OpenCode项目而言可能过宽，容易在简单读取任务中加载大量写作/编辑指导，也容易在写作任务中混入读取审计逻辑。因此本包拆成：

- `ppt-reader`：只处理PPT输入理解、结构化抽取、审阅、总结和改版brief。
- `ppt-writer`：只处理PPT输出、改写、生成、结构化deck spec和QA闭环。

这种拆法更符合OpenCode中按项目、按任务加载技能的方式，也便于后续加入课程开发、提案写作、技术汇报等上层skills。

## 为什么使用uv与Python脚本

用户在OpenCode项目中偏好`uv`虚拟环境。脚本采用PEP723内联依赖声明，agent可以直接运行：

```bash
uv run scripts/build_deck.py deck_spec.json --out output.pptx
```

这避免了在每个项目中维护额外`requirements.txt`，也降低了技能安装成本。

## 没有直接复制官方代码

本包只吸收流程和设计思想，没有复制官方PPTX skill中的脚本或专有内容。内置脚本是从OpenXML/Python-pptx基本能力重新实现的轻量版本，适合作为OpenCode项目技能的基础能力。
