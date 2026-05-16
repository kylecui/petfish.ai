# ppt

**PPT设计与制作 — 读取/生成PPTX、Slide QA、视觉渲染**

| 字段 | 值 |
|---|---|
| 包名 | `opencode-ppt-skills` |
| 别名 | `ppt` |
| 版本 | 1.0.1 |
| 技能数 | 2 |
| 命令数 | 0 |
| 代理数 | 0 |
| 兼容性 | opencode |

## 技能列表

- [`ppt-reader`](../skills/ppt-reader.md) — Read/inspect/summarize/audit/compare PPT/PPTX, extract slide inventory (titles, structure, notes, comments, media, links...
- [`ppt-writer`](../skills/ppt-writer.md) — Create/rewrite/restructure/update/validate/export PPT/PPTX decks (课件、提案、汇报、论文、技术方案). Trigger for 从Markdown/文档/纪要/旧PPT生成新...

## 安装

=== "PowerShell"

    ```powershell
    & ([scriptblock]::Create((irm https://raw.githubusercontent.com/kylecui/petfish.ai/master/remote-install.ps1))) -Pack "ppt"
    ```

=== "Bash"

    ```bash
    curl -fsSL https://raw.githubusercontent.com/kylecui/petfish.ai/master/remote-install.sh | bash -s -- --pack ppt
    ```
