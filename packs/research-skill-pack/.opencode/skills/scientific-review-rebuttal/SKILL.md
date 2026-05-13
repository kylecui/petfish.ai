---
name: scientific-review-rebuttal
description: 论文投稿前自查与审稿回复(rebuttal)：执行novelty/soundness/evaluation/presentation/reproducibility/ethics六维检查，分类reviewer comments并生成point-by-point回复与revision plan。Use when users ask “审稿自查/self-review/reviewer comments/rebuttal/审稿意见/回复审稿人/pre-submission check/paper review”.
compatibility: opencode
license: Apache-2.0
---

## 作用/Purpose

在投稿前进行系统化自查，提前暴露“会被审稿人打回”的高风险问题；在收到审稿意见后，生成有证据、可执行、非对抗性的逐条回复与修订策略。

---

## 触发场景/Trigger Scenarios

- 论文初稿完成，需要submission前质量体检
- 收到reviewer comments，需要组织point-by-point rebuttal
- 团队内部pre-review，要求结构化问题清单和修订优先级
- 需要判断争议点应“反驳”还是“承认并修订”

---

## 输入/Input

- paper draft（含图表与附录说明）
- evidence ledger与claim map
- experiment与统计结果
- reviewer comments（可选，rebuttal场景必需）
- 可选：目标会议审稿标准与格式要求

---

## 输出/Output

- `self-review-report.md`（六维自查报告）
- `risk-priority-list.md`（问题严重性与修订优先级）
- `rebuttal-draft.md`（逐条回复草稿）
- `revision-plan.md`（承诺修订与证据补充计划）

---

## 工作流/Workflow

1. **执行六维自查** — novelty、soundness、evaluation、presentation、reproducibility、ethics
2. **映射主张风险** — 检查每条核心主张是否存在证据缺口或外推过度
3. **审查复现与伦理声明** — 明确代码、数据、参数、双重用途或偏见风险
4. **分类审稿意见** — factual error / misunderstanding / valid criticism / scope disagreement / style preference
5. **生成逐条回复** — 先确认理解，再给证据或修订动作，避免情绪化对抗
6. **形成修订计划** — 给出可执行改动、位置、责任与截止时间

---

## 质量门禁/Quality Gates

- self-review必须覆盖六维：novelty、soundness、evaluation、presentation、reproducibility、ethics
- rebuttal必须先对每条comment完成分类，再进入响应
- 任何对reviewer观点的反驳都必须提供证据；不得无证据直接否定

---

## Gotchas/注意事项

- 不要把“审稿人没读懂”当作默认前提；先检查文本是否确实含糊
- 不要在rebuttal里引入论文中不存在的新主张
- 不要承诺无法在camera-ready前完成的重大实验
- 不要用强硬语气掩盖证据不足，审稿回复首先是事实协商
- 自查报告应可执行，不能只是泛泛评分

---

## 关联资源

- References: `references/self-review-checklist.md`, `references/rebuttal-strategy.md`
