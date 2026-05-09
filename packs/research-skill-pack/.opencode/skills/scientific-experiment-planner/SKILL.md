---
name: scientific-experiment-planner
description: 科学实验设计与验证规划：围绕可检验假设、变量、baseline、ablation、评价指标、统计检验与复现要求生成experiment plan，回答“如何评估贡献”。Use when users ask “实验设计/experiment plan/实验方案/baseline/ablation/评价指标/metrics design/how to evaluate/benchmark plan”.
compatibility: opencode
license: Apache-2.0
---

## 作用/Purpose

将研究想法转化为可验证、可复现、可审查的实验方案。该skill重点解决“如何证明贡献成立”而非“如何描述方法”，确保实验设计与论文主张一一对应。

---

## 触发场景/Trigger Scenarios

- 用户提出“怎么评估这个方法/系统”的问题，需要完整实验方案
- 需要明确 baseline、ablation、指标与统计检验，避免拍脑袋评估
- 需要从方法说明进入验证落地（实验步骤、数据集/工作负载、复现条件）
- 需要提前识别有效性威胁，减少投稿时“evaluation weak”的风险

---

## 输入/Input

- research brief（研究目标、主张、约束）
- methodology/design 草案（方法机制、预期贡献）
- 可用资源（算力、时间、数据、实验环境）
- 可选：evidence ledger、相关论文基线列表

---

## 输出/Output

- `experiment-plan.md`（主实验计划）
- `benchmark-plan.md`（基线与基准设计）
- `ablation-plan.md`（消融实验设计）
- `validity-threats.md`（有效性威胁与缓解策略）

---

## 工作流/Workflow

1. **定义可检验假设** — 将贡献声明改写为可证伪、可量化的假设
2. **确定变量结构** — 列出自变量、因变量、控制变量，避免隐含自由度
3. **选择有意义baseline** — 选择当前主流、强基线与简单基线，解释公平性设置
4. **设计评价指标** — 指标必须直接回应主张（性能、准确率、开销、鲁棒性等）
5. **选择数据集/工作负载** — 说明代表性、覆盖范围与边界条件
6. **设计ablation** — 每次移除一个贡献要素，验证其独立贡献
7. **确定统计检验** — 按数据类型与样本量选择合适检验并报告效应量
8. **定义复现要求** — 固定版本、随机种子、环境说明、运行脚本与报告格式
9. **输出有效性威胁** — 至少覆盖内部、外部、构念、结论四类中的关键风险

---

## 质量门禁/Quality Gates

- 必须至少包含 **1条可检验假设**
- 必须至少指定 **1个baseline**
- 指标必须与主张匹配（不允许“主张A、指标测B”）
- ablation必须至少隔离 **1个明确贡献**
- 必须识别 **≥2项有效性威胁** 并给出缓解策略

---

## Gotchas/注意事项

- 不要用 strawman baseline 伪造优势
- 不要把“更多实验”误当作“更强证据”，关键是实验与主张的对应关系
- 不要把统计显著性当作工程显著性，需同时报告效应量和实际影响
- 不要忽略失败结果与负面样本，它们通常决定结论边界
- 复现要求必须可执行，不能停留在“代码将开源”口号

---

## 关联资源

- References: `references/experiment-design-guide.md`, `references/benchmark-and-ablation-guide.md`
- Assets: `assets/experiment-plan-template.md`
