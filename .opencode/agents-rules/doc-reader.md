# Doc Reader Skill Pack Rules

This pack provides unified document-to-Markdown conversion for reading, review, and extraction.

## Skill Routing (强制)

### Rules

1. When the user wants to **read, extract text from, or convert** a non-Markdown document (PDF, DOCX, XLSX, HTML, EPUB) to Markdown, **MUST** route to `doc-reader`.
2. When the user needs **structured text content** from a document (tables, paragraphs, lists), **MUST** use `doc-reader` to convert first, then read the Markdown output.
3. For **PPTX files**: use `ppt-reader` for structural inventory (slide order, media, comments, layout), use `doc-reader` for full text extraction including tables and charts. Use both for complete PPTX understanding.
4. When the user provides a document and asks to **review, summarize, or extract key points**, use `doc-reader` for conversion, then apply `reference-document-review` for analysis. Do NOT treat conversion as analysis.

### Conflict Resolution

- "Read this PDF and summarize": route `doc-reader` (convert) → agent reads output → summarize. Conversion and analysis are separate steps.
- "Extract the tables from this DOCX": route `doc-reader` with `--json` for metadata, then read the Markdown output.
- "Read this PPTX": route `ppt-reader` first for structure, then `doc-reader` for full text if structural inventory is insufficient.
- "Convert this document to Markdown": route `doc-reader` only. No analysis needed.
- When `reference-document-review` is also installed: `doc-reader` handles conversion, `reference-document-review` handles analysis and extraction into course inputs. Do not merge these responsibilities.

## doc-reader Workflow

1. Identify input file and format (PDF, DOCX, XLSX, HTML, EPUB, etc.)
2. Run conversion: `uv run scripts/doc_to_markdown.py input.pdf --output output.md`
3. Read the converted Markdown output
4. Optionally extract structured metadata: `uv run scripts/doc_to_markdown.py input.pdf --output output.md --json metadata.json`

## Behavioral Rules

- Always convert before reading. Do NOT attempt to interpret binary file contents directly.
- Preserve the conversion output as a file when the user needs to review or cite it later. Use `--output` flag.
- For scanned PDFs, warn the user that markitdown does NOT perform OCR by default; text extraction will be minimal.
- For PPTX, always recommend `ppt-reader` for structural analysis first if structure matters.
- Do NOT attempt LLM-based image description through this skill. The agent can view images natively.
