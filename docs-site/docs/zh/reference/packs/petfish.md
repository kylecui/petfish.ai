# petfish

**工程写作风格改写 — 去AI味、说人话、AI腔检测与改写、中英文紧凑混排**

| 字段 | 值 |
|---|---|
| 包名 | `petfish-style-skill` |
| 别名 | `petfish` |
| 版本 | 4.0.1 |
| 技能数 | 1 |
| 命令数 | 0 |
| 代理数 | 0 |
| 兼容性 | opencode |

## 技能列表

- [`petfish-style-rewriter`](../skills/petfish-style-rewriter.md) — Rewrite, polish, humanize, simplify, de-AI, formalize, or express content in Petfish's writing style. It rewrites Chines...

## 安装

=== "PowerShell"

    ```powershell
    & ([scriptblock]::Create((irm https://raw.githubusercontent.com/kylecui/petfish.ai/master/remote-install.ps1))) -Pack "petfish"
    ```

=== "Bash"

    ```bash
    curl -fsSL https://raw.githubusercontent.com/kylecui/petfish.ai/master/remote-install.sh | bash -s -- --pack petfish
    ```
