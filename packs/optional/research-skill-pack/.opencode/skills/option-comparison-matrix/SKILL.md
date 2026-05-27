---
name: option-comparison-matrix
description: 基于criteria对候选方案做矩阵比较，输出评分、证据链接、deal-breaker淘汰、证据缺口与敏感性检查。Use when the user says "方案对比", "comparison matrix", "打分表", "逐项对比", "scorecard", "打分比较", "option scoring", "横向评估", "deal-breaker", "淘汰规则", "加权排名", "sensitivity analysis", or "证据缺口".
compatibility: opencode
license: Apache-2.0
---

## 作用/Purpose

将候选方案比较过程从主观讨论转为证据化矩阵评估，沉淀可复审依据。该skill必须覆盖：
1) 方案-标准逐项评分；
2) 评分证据挂接与缺口标注；
3) 综合排名与敏感性观察。

输出应支持推荐决策与审计复盘，而不是口头结论。

---

## 触发场景/Trigger Scenarios

- 已有`criteria.md`，需要对多个选项进行统一比较
- 需要把“主观看法”转换成“证据+分数”
- 需要识别方案短板与补救空间
- 需要形成可共享的决策对比底稿
- 需要为`decision-recommendation`提供输入

---

## 输入/Input

- `criteria.md`
- option set（候选方案列表与基本信息）
- evidence inputs（测试结果、文档、案例、成本数据）
- 可选：权重敏感性假设、场景化约束

---

## 输出/Output

- `comparison-matrix.md`

---

## 工作流/Workflow

1. 读取`criteria.md`，锁定评分规则、权重与淘汰条件。
2. 整理候选方案信息，统一口径并补齐基础数据字段。
3. 对每个方案逐条标准评分，并绑定证据来源链接。
4. 检查deal-breaker触发情况，标注淘汰或条件通过状态。
5. 计算加权结果并输出排名，同时记录未覆盖证据缺口。
6. 进行简要敏感性检查，观察关键权重变化下排名稳定性。
7. 输出`comparison-matrix.md`并交接到`decision-recommendation`。

---

## 质量门禁/Quality Gates

- 每个评分项必须附证据或明确“证据缺失”标记。
- 评分计算过程必须可复算，不得出现黑箱步骤。
- deal-breaker判定必须先于总分排名执行。
- 至少识别1项关键数据缺口及其影响范围。
- 比较结果必须区分“事实评分”与“主观判断”。
- 输出必须能直接被推荐报告引用。

---

## Gotchas/注意事项

- 不要把估计值当成已验证事实，必须标注置信度。
- 不要在不同方案间使用不一致数据口径。
- 不要忽略证据缺失对排名可信度的影响。
- 不要把加权总分当成唯一结论，需保留条件说明。
- 不要跳过淘汰规则，防止不合格方案进入推荐。

---

## 关联资源

- `decision-criteria-builder`
- `decision-recommendation`
- `research-evidence-ledger`
- `research-citation-auditor`
