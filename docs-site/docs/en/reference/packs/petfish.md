# petfish

**工程写作风格套件 — 去AI味改写、AI腔检测、风格画像提取、中英文紧凑混排、学术写作拟人化**

| Field | Value |
|---|---|
| Pack name | `petfish-style-skill` |
| Alias | `petfish` |
| Version | 5.0.0 |
| Skills | 3 |
| Commands | 0 |
| Agents | 0 |
| Compatibility | opencode |

## Skills

- [`de-ai-detector`](../skills/de-ai-detector.md) — Detect AI writing patterns in Chinese or English text. Use when the user asks to 检测AI味 / 检测AI痕迹 / 去AI检测 / AI写作检测, detect...
- [`petfish-style-rewriter`](../skills/petfish-style-rewriter.md) — Rewrite, polish, humanize, de-AI, or formalize Chinese or English technical, academic, business, course, proposal, paten...
- [`style-extractor`](../skills/style-extractor.md) — Extract personal writing style from samples to create a style profile. Analyzes sentence patterns, vocabulary preference...

## Install

```bash
uv run https://raw.githubusercontent.com/kylecui/petfish.ai/master/install.py --pack petfish --detect
```
