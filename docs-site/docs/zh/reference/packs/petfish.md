# petfish

**工程写作风格套件 — 去AI味改写、AI腔检测、风格画像提取、中英文紧凑混排、学术写作拟人化**

| 字段 | 值 |
|---|---|
| 包名 | `petfish-style-skill` |
| 别名 | `petfish` |
| 版本 | 5.0.0 |
| 技能数 | 3 |
| 命令数 | 0 |
| 代理数 | 0 |
| 兼容性 | opencode |

## 技能列表

- [`de-ai-detector`](../skills/de-ai-detector.md) — Detect AI writing patterns in Chinese or English text. Use when the user asks to 检测AI味 / 检测AI痕迹 / 去AI检测 / AI写作检测, detect...
- [`petfish-style-rewriter`](../skills/petfish-style-rewriter.md) — Rewrite, polish, humanize, de-AI, or formalize Chinese or English technical, academic, business, course, proposal, paten...
- [`style-extractor`](../skills/style-extractor.md) — Extract personal writing style from samples to create a style profile. Analyzes sentence patterns, vocabulary preference...

## 安装

```bash
uv run https://raw.githubusercontent.com/kylecui/petfish.ai/master/install.py --pack petfish --detect
```
