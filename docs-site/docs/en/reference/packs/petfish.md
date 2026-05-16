# petfish

**工程写作风格改写 — 去AI味、说人话、AI腔检测与改写、中英文紧凑混排**

| Field | Value |
|---|---|
| Pack name | `petfish-style-skill` |
| Alias | `petfish` |
| Version | 4.0.1 |
| Skills | 1 |
| Commands | 0 |
| Agents | 0 |
| Compatibility | opencode |

## Skills

- [`petfish-style-rewriter`](../skills/petfish-style-rewriter.md) — Rewrite, polish, humanize, simplify, de-AI, formalize, or express content in Petfish's writing style. It rewrites Chines...

## Install

=== "PowerShell"

    ```powershell
    & ([scriptblock]::Create((irm https://raw.githubusercontent.com/kylecui/petfish.ai/master/remote-install.ps1))) -Pack "petfish"
    ```

=== "Bash"

    ```bash
    curl -fsSL https://raw.githubusercontent.com/kylecui/petfish.ai/master/remote-install.sh | bash -s -- --pack petfish
    ```
