# petfish

**工程写作风格套件 — 去AI味改写、AI腔检测、风格画像提取、中英文紧凑混排**

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

- [`petfish-style-rewriter`](../skills/petfish-style-rewriter.md) — Rewrite, polish, humanize, simplify, de-AI, formalize, or express content in Petfish's writing style.
- [`de-ai-detector`](../skills/de-ai-detector.md) — Detect AI-like writing patterns and score AI slop risk before rewriting.
- [`style-extractor`](../skills/style-extractor.md) — Extract a writing style profile (voice, structure, patterns) from sample texts.

## Install

=== "PowerShell"

    ```powershell
    & ([scriptblock]::Create((irm https://raw.githubusercontent.com/kylecui/petfish.ai/master/remote-install.ps1))) -Pack "petfish"
    ```

=== "Bash"

    ```bash
    curl -fsSL https://raw.githubusercontent.com/kylecui/petfish.ai/master/remote-install.sh | bash -s -- --pack petfish
    ```
