---
name: scientific-gap-finder
description: 基于文献矩阵做research gap分析：识别真实gap vs 伪gap，绑定支撑与反例论文，评估novelty与可验证性，并产出贡献方向(contribution options)。Use when users ask “找gap/研究空白/research gap/identify gaps/贡献点/novelty/创新点定位”.
compatibility: opencode
license: Apache-2.0
---

## 作用/Purpose

基于已完成的文献矩阵进行研究空白识别，不靠直觉宣称“没人做过”。该skill聚焦三件事：
1) 识别并归类gap类型；
2) 将gap追溯到具体论文证据；
3) 为每个gap提出至少一个具可行性的潜在贡献方向。

输出应服务后续方法设计与实验规划，避免停留在“发现空白”的口号层。

---

## 触发场景/Trigger Scenarios

- 用户要求“找gap / identify gaps / 研究空白分析”
- 文献综述后需要确定贡献点与novelty定位
- 论文引言/贡献段落需要证据化支撑
- 团队需要判断某idea是实质创新还是重复工作
- 需要区分真实未解问题与工程未实现细节

---

## 输入/Input

- `literature-matrix.md`（必需）
- `literature-review.md`（推荐）
- 可选：evidence ledger、claim map、研究目标约束
- 可选：目标发表场景（学术论文/技术报告/系统原型）

---

## 输出/Output

- `research-gaps.md` — gap清单（类型、证据、边界、价值）
- `contribution-options.md` — 每个gap对应的候选贡献方向

---

## 工作流/Workflow

1. 审阅文献矩阵，提取问题、方法、评估、数据、系统落地信息。
2. 按 `gap-types.md` 进行候选gap分类（Problem/Method/Evaluation等）。
3. 对每个候选gap绑定支撑论文与反例论文，避免单边叙述。
4. 判断gap是否真实：区分“尚未解决”与“已解决但你未检索到”。
5. 识别伪gap信号（仅措辞差异、仅参数微调、仅换数据不换问题）。
6. 评估gap价值（理论价值、工程价值、可验证性、可复现性）。
7. 为每个真实gap提出至少一个潜在贡献路径。
8. 标注每条贡献路径的前提条件与验证需求。
9. 参考 `novelty-checklist.md` 做贡献可行性复核。

---

## 质量门禁/Quality Gates

- 每个gap必须追溯到文献矩阵中的具体论文条目。
- 必须区分真实gap与琐碎/伪gap，并给出判别理由。
- 每个gap至少提供一个潜在贡献方向（非口号）。
- 不允许仅用“没有看到相关工作”作为gap证据。
- 需显式记录反证或竞争解释，避免确认偏差。

---

## Gotchas/注意事项

- “论文少”不等于“研究空白”；可能只是检索不足。
- “方法名字不同”不等于“创新不同”；要比较机制与假设。
- 不要把工程实现难度误判为科学问题空白。
- 不要把局部场景成功扩展为通用问题已解决。
- gap分析应连接可验证贡献，否则无法进入方法设计阶段。

---

## 关联资源

- References: `gap-types.md`, `novelty-checklist.md`
