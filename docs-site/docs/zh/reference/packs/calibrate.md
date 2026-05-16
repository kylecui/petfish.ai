# calibrate

**反迎合决策校准 — 在评审、方案设计、代码审查等判断型任务中降低AI迎合倾向，通过中性化提问、评分卡、替代方案比较和置信度分离提升判断质量**

| 字段 | 值 |
|---|---|
| 包名 | `anti-sycophancy-calibration-pack` |
| 别名 | `calibrate` |
| 版本 | 0.1.1 |
| 技能数 | 1 |
| 命令数 | 0 |
| 代理数 | 0 |
| 兼容性 | opencode |

## 技能列表

- [`anti-sycophancy-calibration`](../skills/anti-sycophancy-calibration.md) — For 评审, 评价, 批判, review, critique, feedback, judgment, decision, evaluation, calibration, sycophancy, 迎合, 校准, 方案评估, code ...

## 安装

=== "PowerShell"

    ```powershell
    & ([scriptblock]::Create((irm https://raw.githubusercontent.com/kylecui/petfish.ai/master/remote-install.ps1))) -Pack "calibrate"
    ```

=== "Bash"

    ```bash
    curl -fsSL https://raw.githubusercontent.com/kylecui/petfish.ai/master/remote-install.sh | bash -s -- --pack calibrate
    ```
