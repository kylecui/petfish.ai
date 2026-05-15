# trust

**Skill安全治理引擎 — 基于行为分析的skill可信度评估、风险评分与治理决策**

| Field | Value |
|---|---|
| Pack name | `trustskills-governance-pack` |
| Alias | `trust` |
| Version | 0.1.1 |
| Skills | 1 |
| Commands | 0 |
| Agents | 0 |
| Compatibility | opencode |

## Skills

- [`skill-trust-governance`](../skills/skill-trust-governance.md) — Skill trust/governance requests: skill trust, skill安全, 治理, 可信度, trust scan, risk score, redline check, pre-publish trust...

## Install

=== "PowerShell"

    ```powershell
    & ([scriptblock]::Create((irm https://raw.githubusercontent.com/kylecui/petfish.ai/master/remote-install.ps1))) -Pack "trust"
    ```

=== "Bash"

    ```bash
    curl -fsSL https://raw.githubusercontent.com/kylecui/petfish.ai/master/remote-install.sh | bash -s -- --pack trust
    ```
