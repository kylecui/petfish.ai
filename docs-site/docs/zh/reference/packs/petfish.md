# petfish

**工程写作风格套件 — 去AI味改写、AI腔检测、风格画像提取、中英文紧凑混排**

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

- [`petfish-style-rewriter`](../skills/petfish-style-rewriter.md) — 润色、说人话、去AI味、按Petfish风格改写中英文技术文本。
- [`de-ai-detector`](../skills/de-ai-detector.md) — 检测AI写作特征，评估AI腔风险。
- [`style-extractor`](../skills/style-extractor.md) — 从样本文本中提取风格画像（语调、结构、模式）。

## 安装

=== "PowerShell"

    ```powershell
    & ([scriptblock]::Create((irm https://raw.githubusercontent.com/kylecui/petfish.ai/master/remote-install.ps1))) -Pack "petfish"
    ```

=== "Bash"

    ```bash
    curl -fsSL https://raw.githubusercontent.com/kylecui/petfish.ai/master/remote-install.sh | bash -s -- --pack petfish
    ```
