# calibrate

**Judgment Calibration Pack — 在评审、方案设计、代码审查等判断型任务中降低AI迎合倾向，通过中性化提问、评分卡、替代方案比较和置信度分离提升判断质量；并通过多方对抗性推理（5+1模型）发现盲点、审视假设、增强判断稳健性**

| Field | Value |
|---|---|
| Pack name | `judgment-calibration-pack` |
| Alias | `calibrate` |
| Version | 0.2.0 |
| Skills | 2 |
| Commands | 0 |
| Agents | 0 |
| Compatibility | opencode |

## Skills

- [`anti-sycophancy-calibration`](../skills/anti-sycophancy-calibration.md) — For 评审, 评价, 批判, review, critique, feedback, judgment, decision, evaluation, calibration, sycophancy, 迎合, 校准, 方案评估, code ...
- [`council-thinking`](../skills/council-thinking.md) — 多方对抗性推理（5+1模型）：通过构建5个对抗性视角（支持、反对、实用、保守、创新）+1个综合视角，发现判断盲点、审视隐含假设、增强决策稳健性。适用于战略决策、架构评审、产品规划、技术选型等高风险判断场景。

## Install

=== "PowerShell"

    ```powershell
    & ([scriptblock]::Create((irm https://raw.githubusercontent.com/kylecui/petfish.ai/master/remote-install.ps1))) -Pack "calibrate"
    ```

=== "Bash"

    ```bash
    curl -fsSL https://raw.githubusercontent.com/kylecui/petfish.ai/master/remote-install.sh | bash -s -- --pack calibrate
    ```
