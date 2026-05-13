---
name: adoption-recommendation
description: 基于风险采购证据链给出最终采用建议，区分evidence sufficiency与verdict，并定义Adopt/Control/Pilot/Defer/Reject路径、缓解措施、复审与回滚。Use when the user says "采用建议", "引入建议", "adoption recommendation", "adopt or reject", "go/no-go", "should we proceed", "final decision", "pilot only", "need more evidence", "是否上线", or "最终裁决".
compatibility: opencode
license: Apache-2.0
---

## 作用/Purpose

整合风险、尽调、安全、合规与TCO证据，形成可执行且可追溯的最终采用建议。该skill必须覆盖：
1) 结论选项（Adopt / Adopt with Controls / Pilot Only / Defer / Reject / Need More Evidence）；
2) 决策条件、风险缓解、替代方案与验证路径；
3) 决策日志与后续复盘触发条件。

输出应服务管理层或评审委员会决策，不应是无条件主观推荐。

---

## 触发场景/Trigger Scenarios

- 用户要求“最终建议 / recommendation / go-no-go decision”
- 风险采购链路已完成，需要形成统一决策版本
- 需要给出“能不能上、在什么条件下上、失败怎么收敛”
- 评审会前需要标准化结论、控制措施与后续验证计划
- 需要记录决策依据与证据充分性状态

---

## 输入/Input

- `risk-brief.md`
- `vendor-profile.md` 与 `source-profile.md`
- `security-risk.md`
- `compliance-check.md`
- `tco-operational-risk.md`
- 可选：组织优先级、预算边界、上线时间窗口

---

## 输出/Output

- `adoption-recommendation.md`

---

## 工作流/Workflow

1. 汇总全链路证据并核验完整性，标记证据充分与证据缺口项。
2. 对关键风险进行分层：不可接受、可缓释、可监控、可延期。
3. 评估约束匹配度：安全控制、合规要求、成本边界、运营能力。
4. 比较可选路径：直接采用、附条件采用、试点、延后、拒绝、补证后再议。
5. 选择建议结论并绑定触发条件、前置控制与责任分工。
6. 定义验证计划：上线前验证、试点指标、失败回滚与复审时间点。
7. 记录决策日志：证据来源、关键假设、未决事项、复盘条件。
8. 输出`adoption-recommendation.md`，明确“证据充分性判断”与“最终裁决”是两个独立字段。

---

## 质量门禁/Quality Gates

- 报告必须包含六种标准结论选项之一，不得输出含糊结论。
- 必须分别给出“evidence sufficiency（证据充分性）”与“verdict（裁决）”。
- 每项高风险必须映射到具体控制措施与责任人/责任角色。
- 必须提供至少一个可执行替代路径，而非单一路径推荐。
- 必须定义验证与复审机制，包括时间点、指标与触发条件。
- 决策日志必须可追溯至上游输出文件与关键证据条目。

---

## Gotchas/注意事项

- 不要把“证据不足”直接等于“拒绝”，应区分Need More Evidence与Reject。
- 不要在无控制措施时给出Adopt，条件不成立时结论应降级。
- 不要省略替代方案，否则管理层无法比较机会成本。
- 不要把建议写成一次性结论，必须包含复审与回滚机制。
- 不要混淆事实、推断与建议，结论必须可追溯到证据链。

---

## 关联资源

- 上游链路：`risk-research-brief` → `vendor-source-diligence` → `security-risk-review` → `compliance-check` → `tco-operational-risk`
- 证据治理：`research-evidence-ledger`, `research-synthesis`, `research-quality-reviewer`
- 决策对齐：`decision-criteria-builder`, `decision-recommendation`
