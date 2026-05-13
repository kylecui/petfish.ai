---
name: product-decision-brief
description: 将用户研究、竞品分析与验证结果综合为go/no-go/pivot决策简报，提供可追溯结论与风险说明。Use when the user says "产品决策", "产品建议", "product decision", "go/no-go", "pivot", "决策简报", "decision brief", "should we build this", "管理层决策材料", "tradeoff", "收益风险权衡", or "替代方案对比".
compatibility: opencode
license: Apache-2.0
---

## 作用/Purpose

把多来源研究证据压缩为可执行管理决策，避免“材料很多但结论不清”。该skill必须做到：
1) 证据流整合与可信度分层；
2) 风险量化与备选方案对比；
3) 输出明确 go/no-go/pivot 建议。

输出面向决策会议，可直接进入执行或复核流程。

---

## 触发场景/Trigger Scenarios

- 用户要求“产品决策 / product decision / 决策简报”
- 需要给出 go/no-go/pivot 的结论建议
- 需要回答“should we build this”并展示证据链
- 需要将研究阶段成果汇总为管理层可读决策材料
- 需要比较主方案与替代路线的收益-风险权衡

---

## 输入/Input

- evidence ledger（证据台账与主张映射）
- user research（用户研究结论）
- competitor analysis（竞争格局与定位分析）
- validation results（验证实验结果与阈值达成情况）
- 可选：战略目标、财务边界、资源窗口

---

## 输出/Output

- `decision-brief.md`
- `evidence-summary.md`
- `risk-assessment.md`

---

## 工作流/Workflow

1. 按证据流汇总关键发现（用户、市场、验证、运营约束）。
2. 评估每类结论的置信度与证据完整性。
3. 识别并量化主要风险（概率、影响、可缓解性）。
4. 形成主推荐方案（go/no-go/pivot）并说明触发条件。
5. 给出至少一个备选路径，比较收益、成本与时效。
6. 呈现关键权衡（tradeoffs）与不做决策的代价。
7. 输出高层摘要，确保一页内可理解核心结论。
8. 标记需补证据项与下一轮决策检查点。

---

## 质量门禁/Quality Gates

- 推荐结论必须明确，不得使用模糊措辞替代决策。
- 每条关键主张必须可追溯到证据来源。
- 风险需量化（至少概率或影响等级），不可仅文字罗列。
- 必须提供至少一个替代方案并进行对比说明。
- 需显式标注结论置信度与当前证据盲区。

---

## Gotchas/注意事项

- 不要把“信息汇总”误作“决策建议”；必须给出方向。
- 不要隐藏反证，反证会直接影响置信度评估。
- 不要把短期可行性等同于长期战略匹配。
- 决策简报应让不同角色都能识别自己的行动项。
- 若证据不足，应建议延期决策而不是强行拍板。

---

## 关联资源

- None (standalone)
