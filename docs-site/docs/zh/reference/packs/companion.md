# companion

**PEtFiSh常驻伙伴 — 感知/搜索/创建/审计/门禁/挖掘/优化/评测/追踪skill的全生命周期管理**

| 字段 | 值 |
|---|---|
| 包名 | `petfish-companion-skill` |
| 别名 | `companion` |
| 版本 | 1.1.0 |
| 技能数 | 10 |
| 命令数 | 1 |
| 代理数 | 0 |
| 兼容性 | opencode |

## 技能列表

- [`marketplace-connector`](../skills/marketplace-connector.md) — >
- [`petfish-companion`](../skills/petfish-companion.md) — >
- [`quality-gate`](../skills/quality-gate.md) — >
- [`repo-skill-miner`](../skills/repo-skill-miner.md) — >
- [`skill-author`](../skills/skill-author.md) — >
- [`skill-description-optimizer`](../skills/skill-description-optimizer.md) — >
- [`skill-lint`](../skills/skill-lint.md) — >
- [`skill-security-auditor`](../skills/skill-security-auditor.md) — >
- [`skill-trigger-evaluator`](../skills/skill-trigger-evaluator.md) — >
- [`skill-usage-tracker`](../skills/skill-usage-tracker.md) — >

## 安装

=== "PowerShell"

    ```powershell
    & ([scriptblock]::Create((irm https://raw.githubusercontent.com/kylecui/petfish.ai/master/remote-install.ps1))) -Pack "companion"
    ```

=== "Bash"

    ```bash
    curl -fsSL https://raw.githubusercontent.com/kylecui/petfish.ai/master/remote-install.sh | bash -s -- --pack companion
    ```
