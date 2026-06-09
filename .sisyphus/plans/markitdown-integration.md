# Markitdown Integration Plan

## Problem

当前项目中文档→Markdown转换能力分散且有限：

| Skill | 格式 | 方式 | 限制 |
|-------|------|------|------|
| `ppt-reader` | PPTX/PPTM | 手写XML解析（327行） | 无表格、无图表、无LLM图片描述 |
| `reference-document-review` | PDF/DOCX/Image等 | 无脚本，纯靠agent读文件 | agent无法直接读PDF二进制；DOCX无结构化处理 |

**核心问题**：没有一个统一的文档→Markdown转换层。agent面对PDF/DOCX时只能靠`look_at`做粗略提取，丢失大量结构信息。

## Solution

引入 [microsoft/markitdown](https://github.com/microsoft/markitdown)（141K stars, MIT）作为统一的文档→Markdown转换引擎。

**不替代** `pptx_extract.py`——它提供结构化inventory（slide index、media list、comments、issues），这是markitdown不提供的。两者互补。

## New Skill: `doc-reader`

### 定位

通用文档读取skill，作为所有文档格式→Markdown的统一入口。

### 支持格式

通过markitdown：PDF, PPTX, DOCX, XLS/XLSX, HTML, Images (EXIF+OCR), Audio (转录), EPUB, ZIP (递归), YouTube URLs

### 与现有skill的关系

```
doc-reader (新增, 通用文档→Markdown)
  ├── 被 reference-document-review 调用（读参考资料）
  ├── 被 ppt-reader 调用（补充表格/图表文本抽取）
  └── 可被任何skill独立调用（读任意文档）

ppt-reader (保留, PPTX结构化分析)
  ├── pptx_extract.py → 保留（JSON inventory: slide order, media, comments, issues）
  └── 新增: 调用 doc-reader 补充表格/图表文本

reference-document-review (保留, 课程参考资料提炼)
  └── 内部工作流改为: 先调 doc-reader 转 Markdown → 再做结构化审阅
```

### 目录结构

```
packs/optional/opencode-ppt-skills/.opencode/skills/doc-reader/
├── SKILL.md                    # skill定义
├── scripts/
│   └── doc_to_markdown.py      # markitdown封装脚本
└── references/
    └── format-capabilities.md  # 各格式的处理能力说明
```

### doc_to_markdown.py 设计

```python
# PEP 723 inline metadata
# /// script
# requires-python = ">=3.10"
# dependencies = ["markitdown[all]"]
# ///

"""Convert any document to Markdown using markitdown.

Usage:
  uv run scripts/doc_to_markdown.py input.pdf --out output.md
  uv run scripts/doc_to_markdown.py input.pptx --out output.md --json meta.json
  uv run scripts/doc_to_markdown.py input.docx --out output.md --formats
"""

import argparse
import json
import sys
from pathlib import Path
from markitdown import MarkItDown

def convert(path: Path, llm_client=None, llm_model=None) -> dict:
    md = MarkItDown(
        enable_plugins=True,
        llm_client=llm_client,
        llm_model=llm_model,
    )
    result = md.convert(str(path))
    return {
        "file": str(path),
        "suffix": path.suffix.lower(),
        "title": result.title or "",
        "text_content": result.text_content,
    }

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("--out", type=Path, help="Output markdown file")
    parser.add_argument("--json", type=Path, help="Output metadata JSON")
    parser.add_argument("--formats", action="store_true", help="List supported formats")
    args = parser.parse_args()

    if args.formats:
        print("Supported: PDF, PPTX, DOCX, XLS, XLSX, HTML, Images, Audio, EPUB, ZIP")
        return 0

    data = convert(args.input)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(data["text_content"], encoding="utf-8")
    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    if not args.out:
        print(data["text_content"])
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
```

### SKILL.md 核心内容

```markdown
---
name: doc-reader
description: >-
  Convert any document (PDF, PPTX, DOCX, XLS, HTML, images, audio, EPUB)
  to Markdown for LLM consumption. Trigger for 读取文档, read PDF,
  convert DOCX, extract text, 文档转Markdown, 读文件内容.
license: MIT
compatibility: opencode; requires uv; markitdown[all] auto-installed via PEP 723.
metadata:
  version: "1.0.0"
  scope: document-to-markdown-conversion
---

# Doc Reader Skill

## Purpose
Unified document-to-markdown conversion using microsoft/markitdown.

## When to use
- Any skill needs to read a non-Markdown file
- reference-document-review needs to extract from PDF/DOCX
- ppt-reader needs to supplement table/chart text
- User asks to read/extract/convert a document

## Default workflow
1. Run: `uv run scripts/doc_to_markdown.py <input> --out <output.md>`
2. Read the generated Markdown
3. Proceed with domain-specific analysis

## Limitations
- markitdown focuses on text extraction, not layout fidelity
- Tables may lose complex formatting
- Images in PDF/PPTX: text only; for visual analysis use render_slides.py + look_at
- No support for legacy .ppt format (use LibreOffice to convert first)
```

## ppt-reader Enhancement

### 改造 `pptx_extract.py`

新增 `--markitdown` flag，调用markitdown补充文本：

```bash
# 现有（保留）
uv run scripts/pptx_extract.py input.pptx --out inventory.json --markdown summary.md

# 新增：同时生成markitdown版Markdown，补充表格/图表文本
uv run scripts/pptx_extract.py input.pptx --out inventory.json --markdown summary.md --markitdown enriched.md
```

实现方式：在 `pptx_extract.py` 的 `main()` 中加一个 `--markitdown` flag，当指定时调用 `doc_to_markdown.py` 或直接 `from markitdown import MarkItDown`。

### ppt-reader SKILL.md 更新

工作流增加第2.5步：

```
2. 运行结构化抽取（现有）
3. [新增] 运行 markitdown 补充抽取：表格、图表文本、嵌入对象
4. 合并两份结果：用 inventory JSON 的结构 + markitdown 的丰富文本
5. 形成分析（现有）
```

## reference-document-review Enhancement

### 改造工作流

当前工作流是纯prompt指导，没有脚本支持。改为：

```
1. 识别输入文件格式
2. [新增] 对非Markdown文件，调用 doc-reader 转为 Markdown
3. 基于转换后的Markdown做结构化审阅（现有逻辑）
4. 输出审阅结果（现有逻辑）
```

SKILL.md 的 `Common source-specific defaults` section 更新为引用 doc-reader：

```markdown
- PDF/DOCX/XLSX/Image: 先用 doc-reader (markitdown) 转为Markdown，再做审阅
- Markdown: 直接审阅
- PPTX: 用 ppt-reader 做结构化inventory，用 doc-reader 补充文本
```

## Implementation Steps

### Phase 1: doc-reader skill 创建（新skill）

| # | Task | Files |
|---|------|-------|
| 1 | 创建 doc-reader skill 目录 | `packs/optional/opencode-ppt-skills/.opencode/skills/doc-reader/` |
| 2 | 编写 `doc_to_markdown.py` | `doc-reader/scripts/doc_to_markdown.py` |
| 3 | 编写 SKILL.md | `doc-reader/SKILL.md` |
| 4 | 编写 format-capabilities.md | `doc-reader/references/format-capabilities.md` |
| 5 | 测试：PDF/DOCX/PPTX/XLSX/Image各一个 | 本地验证 |

### Phase 2: ppt-reader 增强

| # | Task | Files |
|---|------|-------|
| 6 | pptx_extract.py 加 `--markitdown` flag | `ppt-reader/scripts/pptx_extract.py` |
| 7 | ppt-reader SKILL.md 更新工作流 | `ppt-reader/SKILL.md` |
| 8 | 测试：对比纯XML vs XML+markitdown输出 | 本地验证 |

### Phase 3: reference-document-review 增强

| # | Task | Files |
|---|------|-------|
| 9 | 更新 SKILL.md 引用 doc-reader | `reference-document-review/SKILL.md` |
| 10 | 测试：PDF→Markdown→审阅全流程 | 本地验证 |

### Phase 4: 发布

| # | Task | Notes |
|---|------|-------|
| 11 | 9触点检查清单 | 注册到安装器、catalog、README等 |
| 12 | lint + security audit | quality-gate |
| 13 | 创建PR + release | v1.4.17 或 v1.5.0（取决于scope） |

## Risk Assessment

| Risk | Likelihood | Mitigation |
|------|-----------|------------|
| markitdown依赖体积大 | Medium | 用PEP 723 `dependencies = ["markitdown[all]"]`，uv按需下载 |
| markitdown PPTX输出不如pptx_extract.py | Low | 两者互补，不替代 |
| markitdown Python版本要求 | Low | 要求3.10+，与现有skill一致 |
| 新skill触发冲突（doc-reader vs ppt-reader） | Medium | description明确分工：doc-reader=通用转换，ppt-reader=PPTX结构化分析 |
| markitdown升级breaking change | Low | lock version in PEP 723: `dependencies = ["markitdown>=0.1,<0.2"]` |

## Decision Points

1. **doc-reader放哪个pack？**
   - Option A: 放 `opencode-ppt-skills` pack（复用现有pack基础设施）
   - Option B: 新建独立pack `opencode-doc-skills`
   - **推荐 Option A**：doc-reader 是 ppt-reader 的通用化扩展，逻辑上属于同一pack。pack可以改名但不需要。

2. **LLM图片描述是否默认开启？**
   - Option A: 默认不开启（需要用户配置llm_client）
   - Option B: 默认开启（自动检测环境变量中的API key）
   - **推荐 Option A**：避免意外产生API费用。用户需要时显式传入。

3. **版本号**
   - 如果只改ppt pack内部 → v1.4.17 (patch)
   - 如果新建独立pack → v1.5.0 (minor)
   - **待Phase 1完成后决定**
