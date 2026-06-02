# Doc Reader Skill

本包提供一个面向OpenCode的统一文档读取技能：

- `doc-reader`：将PDF/DOCX/XLSX/HTML/PPTX/EPUB等文档转为Markdown，便于读取、审阅和内容提取。

基于 [markitdown](https://github.com/microsoft/markitdown)（MIT，141K+ stars）作为转换引擎。

推荐放置位置：

```text
<your-project>/.opencode/skills/doc-reader/SKILL.md
```

也可以放到全局目录：

```text
~/.config/opencode/skills/doc-reader/SKILL.md
```

## 快速安装

```powershell
& ([scriptblock]::Create((irm https://raw.githubusercontent.com/kylecui/petfish.ai/master/remote-install.ps1))) -Pack doc-reader
```

```bash
curl -fsSL https://raw.githubusercontent.com/kylecui/petfish.ai/master/remote-install.sh | bash -s -- --pack doc-reader
```

## 环境依赖

必需：

- `uv`：运行内置Python脚本，自动通过PEP 723安装`markitdown[all]`依赖。

## 使用示例

将PDF转为Markdown并保存：

```bash
cd .opencode/skills/doc-reader
uv run scripts/doc_to_markdown.py report.pdf --output report.md
```

同时输出元数据：

```bash
uv run scripts/doc_to_markdown.py report.pdf --output report.md --json report-meta.json
```

直接输出到终端：

```bash
uv run scripts/doc_to_markdown.py spreadsheet.xlsx
```

## 支持格式

| 格式 | 扩展名 | 说明 |
|---|---|---|
| PDF | `.pdf` | 基于pdfminer.six提取文本（非OCR） |
| Word | `.docx` | 提取段落、表格、列表 |
| Excel | `.xlsx`, `.xls` | 每个Sheet转为Markdown表格 |
| PowerPoint | `.pptx` | 提取每页文本和表格 |
| HTML | `.html`, `.htm` | 提取正文内容 |
| EPUB | `.epub` | 提取电子书文本 |
| 图片 | `.jpg`, `.png` 等 | 仅提取EXIF元数据 |
| 音频 | `.mp3`, `.wav` 等 | 仅提取文件元数据 |
| ZIP | `.zip` | 递归处理内部文件 |

## 与ppt-reader的关系

- `ppt-reader`：提供PPTX结构化清单（幻灯片顺序、媒体、备注、评论、版式）。
- `doc-reader`：提供PPTX全文提取（含表格和图表中的文字）。
- 完整理解PPTX建议两者配合使用。

## 设计原则

1. 单一职责：只做文档转Markdown，不做分析和审阅。
2. PEP 723 inline metadata：`uv run`自动安装依赖，不污染项目环境。
3. 轻量wrapper：脚本仅~70行，核心逻辑委托给markitdown。
4. 明确边界：不包含OCR、LLM图像描述等超出markitdown能力的功能。
