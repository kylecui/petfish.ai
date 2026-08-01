# style-governor

**系列文档风格一致性治理 — 提取风格画像、审计术语漂移与排版漂移、保守归一化改写，保留事实与作者意图**

| 字段 | 值 |
|---|---|
| 包名 | `series-style-governor-pack` |
| 别名 | `style-governor` |
| 版本 | 0.1.0 |
| 技能数 | 1 |
| 命令数 | 0 |
| 代理数 | 0 |
| 兼容性 | opencode |

## 技能列表

- [`series-style-governor`](../skills/series-style-governor.md) — 系列文档风格一致性治理。跨文档统一术语、命名、排版和叙事结构。从参考文件提取风格画像，审计目标文档，检测术语漂移和排版漂移，生成保守改写草稿。Use when writing a series of books, chapters, cou...

## 安装

```bash
uv run https://raw.githubusercontent.com/kylecui/petfish.ai/master/install.py --pack style-governor --detect
```
