# calibrate

**反迎合决策校准 — 在评审、方案设计、代码审查等判断型任务中降低AI迎合倾向，通过中性化提问、评分卡、替代方案比较和置信度分离提升判断质量**

| Field | Value |
|---|---|
| Pack name | `anti-sycophancy-calibration-pack` |
| Alias | `calibrate` |
| Version | 0.1.1 |
| Skills | 1 |
| Commands | 0 |
| Agents | 0 |
| Compatibility | opencode |

## Skills

- [`anti-sycophancy-calibration`](../skills/anti-sycophancy-calibration.md) — For 评审, 评价, 批判, review, critique, feedback, judgment, decision, evaluation, calibration, sycophancy, 迎合, 校准, 方案评估, code ...

## Install

=== "PowerShell"

    ```powershell
    & ([scriptblock]::Create((irm https://raw.githubusercontent.com/kylecui/petfish.ai/master/remote-install.ps1))) -Pack "calibrate"
    ```

=== "Bash"

    ```bash
    curl -fsSL https://raw.githubusercontent.com/kylecui/petfish.ai/master/remote-install.sh | bash -s -- --pack calibrate
    ```
