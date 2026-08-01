# reference-document-review

> Pack: **course**

Read, normalize, compare, extract, or convert reference materials in PDF,

**Compatibility:** Designed for OpenCode. Assumes repo-local `.opencode/skills` discovery

---

# Purpose

Turn heterogeneous reference material into structured course-development inputs.

# Default intake workflow

1. Identify each source and its role:
   - authoritative source
   - rough draft
   - supporting example
   - visual reference
   - conflicting reference
2. Extract the useful material:
   - objectives
   - concepts
   - terminology
   - data points
   - examples
   - diagrams/tables
3. Normalize the extracted content into a course-ready note.
4. Flag uncertainty, OCR risk, or contradiction.
5. Route the cleaned result into the next relevant artifact.

# Review modes

- summary
- structured extraction
- comparison/diff
- lesson-input conversion
- issue spotting
- terminology normalization

# Expected output

When reading references for course work, prefer this structure:

```markdown
# Source Review

## Source inventory
## Key extracted points
## Reusable course material
## Conflicts / uncertainties
## Suggested downstream artifact
```

# Source handling rules

- Keep source facts separate from your suggestions.
- Preserve citations or file attribution when available.
- If a scan or image is ambiguous, mark it instead of guessing.
- When multiple references disagree, present the disagreement explicitly.

# Format handling

对于非Markdown格式的参考资料（PDF、DOCX、XLSX、HTML、PPTX等），优先使用 `doc-reader` skill将其转为Markdown后再进行审阅：

```bash
uv run <doc-reader-path>/scripts/doc_to_markdown.py input.pdf --output temp/review.md
```

然后在Markdown基础上执行审阅workflow。

对于PPTX，优先使用 `ppt-reader` 获取结构化inventory，再用 `doc-reader` 补充全文（含表格和图表文字）。

当 `doc-reader` 未安装时，回退到agent原生文件读取能力，但应明确提示转换质量可能不稳定。

# Common source-specific defaults

- PDF: capture title, section structure, tables, and figures.
- DOC/DOCX: preserve editorial structure and tracked-intent where obvious.
- Markdown: preserve heading logic and embedded code blocks.
- Image: extract visible text, diagram meaning, and any labels that influence course design.

# Gotchas

- Do not silently merge conflicting source statements.
- Do not treat a marketing deck as authoritative technical truth.
- Do not rewrite source intent too early; first extract, then reinterpret.
- Do not discard appendices if they contain definitions or lab constraints.

*... (2 more lines in full SKILL.md)*
