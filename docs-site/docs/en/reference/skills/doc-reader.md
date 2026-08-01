# doc-reader

> Pack: **doc-reader**

Convert PDF/DOCX/XLSX/HTML/PPTX/EPUB to Markdown for reading, review, and extraction. Use when user needs to read documents, extract text from PDF, convert DOCX to markdown, extract spreadsheet content, or any non-Markdown document needs structured reading. Trigger for 读取文档, read document, PDF转markdown, DOCX内容, convert to markdown, 文档内容提取.

**Compatibility:** opencode; requires uv for bundled Python script.

---

# Doc Reader Skill

## 目标

将任意文档转为可读取的Markdown文本，使用[markitdown](https://github.com/microsoft/markitdown)作为转换引擎。让agent能够像读取Markdown一样读取PDF、DOCX、XLSX等二进制格式文档。

## 支持格式

| 格式 | 扩展名 | 提取内容 |
|---|---|---|
| PDF | `.pdf` | 文本段落（基于pdfminer.six，非OCR） |
| Word | `.docx` | 段落、表格、列表 |
| Excel | `.xlsx`, `.xls` | 每个Sheet转为Markdown表格 |
| PowerPoint | `.pptx` | 每页幻灯片文本和表格 |
| HTML | `.html`, `.htm` | 正文内容 |
| EPUB | `.epub` | 电子书文本 |
| 图片 | `.jpg`, `.png` 等 | EXIF元数据 |
| 音频 | `.mp3`, `.wav` 等 | 文件元数据 |
| ZIP | `.zip` | 递归处理内部文件 |

## 默认工作流

1. **识别输入文件和格式**：确认文件路径存在，根据扩展名判断格式。
2. **运行转换**：

```bash
uv run scripts/doc_to_markdown.py input.pdf --output output.md
```

3. **读取转换后的Markdown**：用Read工具读取`output.md`。
4. **（可选）提取结构化元数据**：

```bash
uv run scripts/doc_to_markdown.py input.pdf --output output.md --json metadata.json
```

元数据JSON结构：

```json
{
  "source_file": "input.pdf",
  "source_ext": ".pdf",
  "text_length": 12345,
  "title_guess": "Extracted or guessed title"
}
```

## 与ppt-reader的关系

对于PPTX文件，两个skill提供互补能力：

| 需求 | 使用 |
|---|---|
| 幻灯片顺序、版式、媒体清单、备注、评论 | `ppt-reader` |
| 全文提取（含表格和图表中的文字） | `doc-reader` |
| 完整理解PPTX | 先`ppt-reader`获取结构，再`doc-reader`提取全文 |

## 脚本

### `scripts/doc_to_markdown.py`

markitdown的薄wrapper，约70行。

**用法**：

```bash
# 转换并保存到文件
uv run scripts/doc_to_markdown.py input.pdf --output output.md

# 输出到stdout
uv run scripts/doc_to_markdown.py input.docx

# 同时输出元数据JSON
uv run scripts/doc_to_markdown.py input.xlsx --output output.md --json meta.json
```

**参数**：

| 参数 | 必需 | 说明 |
|---|---|---|

*... (28 more lines in full SKILL.md)*
