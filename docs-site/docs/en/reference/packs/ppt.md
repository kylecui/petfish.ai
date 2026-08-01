# ppt

**PPT设计与制作 — 读取/生成PPTX、Slide QA、视觉渲染**

| Field | Value |
|---|---|
| Pack name | `opencode-ppt-skills` |
| Alias | `ppt` |
| Version | 1.0.1 |
| Skills | 2 |
| Commands | 0 |
| Agents | 0 |
| Compatibility | opencode |

## Skills

- [`ppt-reader`](../skills/ppt-reader.md) — Read/inspect/summarize/audit/compare PPT/PPTX, extract slide inventory (titles, structure, notes, comments, media, links...
- [`ppt-writer`](../skills/ppt-writer.md) — Create/rewrite/restructure/update/validate/export PPT/PPTX decks (课件、提案、汇报、论文、技术方案). Trigger for 从Markdown/文档/纪要/旧PPT生成新...

## Install

```bash
uv run https://raw.githubusercontent.com/kylecui/petfish.ai/master/install.py --pack ppt --detect
```
