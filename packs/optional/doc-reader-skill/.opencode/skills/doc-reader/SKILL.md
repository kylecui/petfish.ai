---
name: doc-reader
description: Convert PDF/DOCX/XLSX/HTML/PPTX/EPUB to Markdown for reading, review, and extraction. Use when user needs to read documents, extract text from PDF, convert DOCX to markdown, extract spreadsheet content, or any non-Markdown document needs structured reading. Trigger for 读取文档, read document, PDF转markdown, DOCX内容, convert to markdown, 文档内容提取.
license: MIT
compatibility: opencode; requires uv for bundled Python script.
metadata:
  version: "1.0.0"
  scope: document-reading-conversion
  author: kylecui-skill-pack
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
| `input` | 是 | 输入文件路径 |
| `--output` | 否 | 输出Markdown文件路径；省略则输出到stdout |
| `--json` | 否 | 元数据JSON输出路径 |

**依赖**：通过PEP 723 inline metadata声明`markitdown[all]`，`uv run`自动安装。

## 常见陷阱

1. **markitdown不保留所有格式**：表格可能丢失复杂的合并单元格，嵌套列表可能扁平化。对于精确格式要求，转换后需人工核对。
2. **PPTX应优先使用ppt-reader做结构分析**：doc-reader只提取文本，不提供幻灯片顺序、媒体清单或版式信息。
3. **markitdown默认不做OCR**：扫描版PDF（纯图片PDF）只会产出极少文本。需要OCR时应使用专门的OCR工具。
4. **LLM图像描述不支持**：本skill不包含`--llm-model`标志。agent自身可以原生查看图片，无需通过markitdown做图像描述。
5. **大型PDF可能耗时较长**：markitdown逐页处理，100+页的PDF转换可能需要数十秒。

## 行为边界

### 必须做

- 转换前确认文件存在
- 保存转换结果到文件（使用`--output`），方便后续引用
- 对扫描版PDF明确提示OCR限制

### 不得做

- 不得将本skill用于文档分析和审阅（那是`reference-document-review`的职责）
- 不得添加OCR或LLM图像描述功能
- 不得在转换失败时静默返回空内容而不报错
- 不得将markitdown的原始输出当作完美转换结果——始终提醒用户可能丢失复杂格式
