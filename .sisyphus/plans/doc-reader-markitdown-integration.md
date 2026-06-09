# Plan: doc-reader skill + markitdown integration

## Problem

当前文档处理能力分散且不完整：

1. **ppt-reader** 的 `pptx_extract.py` 是手写XML解析器（327行），覆盖文本/备注/媒体/评论，但不支持表格内容、图表文字、LLM图片描述
2. **reference-document-review** 没有任何脚本，完全依赖agent原生能力读取文件——遇到PDF/DOCX/XLSX时效果不稳定
3. 没有统一的"文档→Markdown"转换层，每个skill各做各的

## Solution

引入 [microsoft/markitdown](https://github.com/microsoft/markitdown) 作为统一的文档→Markdown转换引擎，同时新建一个 `doc-reader` skill 作为跨pack共享的文档读取基础设施。

## Architecture

```
doc-reader (新skill，独立pack或归入toolchain)
  │
  ├─ scripts/doc_to_markdown.py  ← markitdown wrapper
  │     --input <file>           (PDF/DOCX/XLSX/HTML/PPTX...)
  │     --output <markdown>      (输出Markdown)
  │     --json <structured>      (可选，输出结构化JSON)
  │     --llm-model <model>      (可选，LLM图片描述)
  │
  └─ 依赖: markitdown[all] 或按需 markitdown[pdf,docx,pptx,xlsx]

ppt-reader (改造)
  │
  ├─ scripts/pptx_extract.py     ← 保留，用于结构化inventory
  │     新增 --markitdown flag    ← 补充markitdown的文本/表格抽取
  │
  ├─ scripts/render_slides.py    ← 保留不变
  │
  └─ SKILL.md 更新：workflow加入markitdown补充抽取步骤

reference-document-review (改造)
  │
  └─ SKILL.md 更新：新增"先用doc-reader转Markdown，再做审阅"的默认步骤
```

## Scope

### In scope

| # | Task | Pack | Effort |
|---|------|------|--------|
| 1 | 新建 `doc-reader` skill | 新pack或归入toolchain | M |
| 2 | 编写 `doc_to_markdown.py` wrapper | doc-reader | S |
| 3 | 改造 `pptx_extract.py` 加 `--markitdown` flag | ppt | S |
| 4 | 更新 `ppt-reader` SKILL.md | ppt | S |
| 5 | 更新 `reference-document-review` SKILL.md | course | S |
| 6 | lint + gate 验证 | all | S |

### Out of scope

- `ppt-writer` 的 `build_deck.py` / `qa_deck.py` — 不涉及读取
- Azure Document Intelligence / Content Understanding 集成 — 后续考虑
- markitdown OCR plugin — 后续考虑
- 新pack的petfish-market注册 — 等#6验证通过后单独做

## Detailed Design

### Task 1-2: doc-reader skill + doc_to_markdown.py

**位置**: `packs/optional/doc-reader-skill/` (新optional pack)

**SKILL.md 核心内容**:
- Trigger: "读取文档", "read document", "PDF转markdown", "DOCX内容", "读取PPTX", "convert to markdown"
- 默认workflow: `uv run scripts/doc_to_markdown.py <input> --output <md> [--json <json>]`
- 支持格式: PDF, DOCX, XLS/XLSX, PPTX, HTML, EPUB, 图片(EXIF+OCR via plugin), 音频(metadata+transcription via plugin), ZIP(递归)
- 可选LLM图片描述: `--llm-model gpt-4o` (需要配置OpenAI client)
- 输出: 纯Markdown (主要) + 可选JSON (元数据: 格式、页数、标题等)

**doc_to_markdown.py 设计**:
```python
# PEP 723 inline metadata
# /// script
# requires-python = ">=3.10"
# dependencies = ["markitdown[all]"]
# ///

# 核心逻辑:
# 1. 用 markitdown.MarkItDown().convert(input) 得到 Markdown
# 2. 可选: 提取元数据(格式、标题、页数等)写入JSON
# 3. 输出到 --output 或 stdout
```

约 60-80 行代码，主要是一个markitdown的thin wrapper + 元数据提取 + CLI参数解析。

### Task 3: pptx_extract.py --markitdown flag

**改造点**: 在 `pptx_extract.py` 的 `extract()` 函数末尾，新增一个可选步骤：

```python
def extract(path, use_markitdown=False):
    # ... 现有逻辑不变 ...
    
    if use_markitdown:
        try:
            from markitdown import MarkItDown
            md = MarkItDown()
            result = md.convert(str(path))
            data["markitdown_text"] = result.text_content
            # 表格、图表中的文字会被markitdown抽取，
            # 补充到现有paragraphs中不覆盖的结构化数据
        except ImportError:
            # markitdown未安装时静默跳过，不影响现有功能
            pass
    
    return data
```

**设计原则**: 
- `--markitdown` 是可选flag，不改变现有零依赖行为
- markitdown的文本补充到 `data["markitdown_text"]`，不覆盖 `paragraphs`
- 未安装markitdown时静默降级

### Task 4: ppt-reader SKILL.md 更新

新增workflow步骤（在现有step 2和step 3之间）：

```
2.5 (可选) 如果需要更完整的文本抽取（特别是表格、图表中的文字）：
     uv run scripts/pptx_extract.py input.pptx --out output/inventory.json --markitdown
     这会额外输出 markitdown_text 字段，包含表格和图表中被原文抽取遗漏的文字。
```

### Task 5: reference-document-review SKILL.md 更新

新增"格式处理"section：

```
# Format handling

对于非Markdown格式的参考资料（PDF、DOCX、XLSX、HTML、PPTX等），
优先使用 doc-reader skill 将其转为Markdown后再进行审阅：

  uv run <doc-reader-path>/scripts/doc_to_markdown.py input.pdf --output temp/review.md

然后在Markdown基础上执行审阅workflow。

对于PPTX，优先使用 ppt-reader 获取结构化inventory，再用 doc-reader 补充全文。
```

## Files to Create/Modify

| File | Action | Pack |
|------|--------|------|
| `packs/optional/doc-reader-skill/.opencode/skills/doc-reader/SKILL.md` | CREATE | doc-reader |
| `packs/optional/doc-reader-skill/.opencode/skills/doc-reader/scripts/doc_to_markdown.py` | CREATE | doc-reader |
| `packs/optional/doc-reader-skill/pack-manifest.json` | CREATE | doc-reader |
| `packs/optional/doc-reader-skill/AGENTS.md` | CREATE | doc-reader |
| `packs/optional/opencode-ppt-skills/.opencode/skills/ppt-reader/scripts/pptx_extract.py` | MODIFY | ppt |
| `packs/optional/opencode-ppt-skills/.opencode/skills/ppt-reader/SKILL.md` | MODIFY | ppt |
| `packs/optional/opencode-course-skills-pack/.opencode/skills/reference-document-review/SKILL.md` | MODIFY | course |

## Risks

| Risk | Mitigation |
|------|-----------|
| markitdown依赖过重 | PEP 723 inline metadata，`uv run`自动管理，不污染项目环境 |
| markitdown的PPTX输出丢失结构化信息 | pptx_extract.py保留不变，markitdown作为补充而非替代 |
| doc-reader作为新pack需要注册到installer和market | Task 6验证通过后按9触点清单注册，可做单独PR |
| markitdown对中文PPTX的表格支持不完善 | 渐进增强，先测试再决定是否作为默认 |

## Open Questions (需用户确认)

1. **doc-reader是独立optional pack还是归入现有pack？**
   - 独立pack：更灵活，可以单独安装，但多一个pack维护
   - 归入toolchain：文档处理是通用工具，toolchain已有skill lifecycle工具
   - 归入companion：文档读取是最基础的能力
   - **建议：独立optional pack**，因为文档读取是一个独立的领域，不只服务于skill lifecycle

2. **是否需要支持markitdown的LLM图片描述？**
   - 需要传入 `llm_client` + `llm_model`
   - 在opencode环境下，agent自己就能看图片，可能不需要这个
   - **建议：先不支持，后续有需求再加**

3. **pack命名确认？**
   - `doc-reader` 还是 `doc-to-markdown` 还是 `document-reader`？
   - **建议：`doc-reader`**，与 `ppt-reader` 命名一致
