# OpenCode PPT Skills

本包提供两个面向OpenCode的PowerPoint/PPTX技能：

- `ppt-reader`：读取、抽取、审阅、总结PPTX。
- `ppt-writer`：创建、改写、生成、验证PPTX。

推荐放置位置：

```text
<your-project>/.opencode/skills/ppt-reader/SKILL.md
<your-project>/.opencode/skills/ppt-writer/SKILL.md
```

也可以放到全局目录：

```text
~/.config/opencode/skills/ppt-reader/SKILL.md
~/.config/opencode/skills/ppt-writer/SKILL.md
```

## 快速安装

在目标项目根目录执行：

```bash
cp -r .opencode/skills/ppt-reader <your-project>/.opencode/skills/
cp -r .opencode/skills/ppt-writer <your-project>/.opencode/skills/
```

或者直接把本包中的`.opencode`目录合并到你的项目根目录。

## 推荐权限配置

可在`opencode.json`中加入：

```json
{
  "permission": {
    "skill": {
      "ppt-reader": "allow",
      "ppt-writer": "allow"
    }
  }
}
```

## 环境依赖

必需：

- `uv`：运行内置Python脚本。

可选：

- LibreOffice：把PPTX渲染为PDF。
- Poppler：使用`pdftoppm`把PDF转为逐页图片。
- Node.js + PptxGenJS：当你需要更复杂的自定义页面布局时，可由agent临时使用。

## 验证

生成示例PPT：

```bash
cd .opencode/skills/ppt-writer
uv run scripts/build_deck.py assets/deck_spec_template.json --out /tmp/ppt-writer-demo.pptx
uv run scripts/qa_deck.py /tmp/ppt-writer-demo.pptx --out /tmp/ppt-writer-demo-qa.json
```

读取示例PPT：

```bash
cd .opencode/skills/ppt-reader
uv run scripts/pptx_extract.py /tmp/ppt-writer-demo.pptx --out /tmp/ppt-inventory.json --markdown /tmp/ppt-summary.md
```

## 设计原则

1. Reader和Writer分离，避免一个过大的PPT技能在所有相关任务中误触发。
2. Reader默认输出结构化inventory，避免只抽全文导致误读。
3. Writer默认先做brief和逐页计划，再生成PPTX。
4. 内置脚本使用`uv run`和PEP723声明依赖，便于OpenCode项目中直接执行。
5. 所有正式交付都应进行“生成→QA→修正→复验”。
