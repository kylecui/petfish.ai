# calibrate

**判断校准与多视角对抗式推理 — 反迎合决策校准（fish-calibrate）+ 五人顾问团多视角判断（council-thinking），在评审、方案评估、战略判断、产品定位、研究设计等复杂判断任务中降低迎合倾向、暴露盲点、删除弱观点、形成可执行结论**

| 字段 | 值 |
|---|---|
| 包名 | `judgment-calibration-pack` |
| 别名 | `calibrate` |
| 版本 | 0.3.0 |
| 技能数 | 2 |
| 命令数 | 0 |
| 代理数 | 0 |
| 兼容性 | opencode |

## 技能列表

- [`council-thinking`](../skills/council-thinking.md) — 五人顾问团多视角对抗式判断，用于方案评估、战略判断、产品定位、技术路线、研究设计等复杂决策。5个logical subagents（反对者/本质思考/机会挖掘/局外人/执行者）+Arbiter删除弱观点，输出可执行结论。比fish-cali...
- [`anti-sycophancy-calibration`](../skills/anti-sycophancy-calibration.md) — For 评审, 评价, 批判, review, critique, feedback, judgment, decision, evaluation, calibration, sycophancy, 迎合, 校准, 方案评估, code ...

## 安装

```bash
uv run https://raw.githubusercontent.com/kylecui/petfish.ai/master/install.py --pack calibrate --detect
```
