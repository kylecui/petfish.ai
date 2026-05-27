---
name: tco-operational-risk
description: 评估候选方案的TCO与运维风险，覆盖直接/隐性成本、买建混合路径、锁定风险、退出可行性与情景敏感因子。Use when the user says "TCO", "TCO评估", "total cost of ownership", "总拥有成本", "运维风险", "运营风险", "operational risk", "cost-risk analysis", "buy vs build", "lock-in risk", "exit plan", "1-3年可持续", or "scenario analysis".
compatibility: opencode
license: Apache-2.0
---

## 作用/Purpose

将采购决策从“功能是否可用”扩展到“长期是否可持续”，形成成本-风险一体化判断。该skill必须覆盖：
1) 直接成本与隐性集成/培训/运维成本；
2) 可靠性、扩展性与运营复杂度风险；
3) 切换成本、供应商锁定与退出路径可执行性。

输出用于支持最终采用建议中的经济性与可运营性结论。

---

## 触发场景/Trigger Scenarios

- 用户要求“总拥有成本评估 / TCO analysis / cost-risk analysis”
- 需要判断方案在1-3年周期是否可持续
- 需要比较“买、建、混合”方案的长期运维负担
- 采购评审需明确锁定风险与退出成本
- 合规与安全评审后，需要补齐经营与运维维度证据

---

## 输入/Input

- `risk-brief.md`
- `vendor-profile.md` / `source-profile.md`
- `security-risk.md`
- `compliance-check.md`
- cost assumptions（许可、算力、人力、支持、迁移）

---

## 输出/Output

- `tco-operational-risk.md`

---

## 工作流/Workflow

1. 定义分析周期与比较基线（当前方案、候选方案、替代方案）。
2. 估算直接成本：订阅/许可、调用量、基础设施、支持与合同附加项。
3. 估算实施与集成成本：开发改造、流程重塑、数据迁移、上线窗口影响。
4. 估算学习与运营成本：培训、值守、故障处理、审计与治理维护。
5. 评估可靠性与扩展风险：容量瓶颈、SLA偏差、多区域/多团队扩展难度。
6. 评估锁定与切换风险：接口耦合、数据可迁移性、替换周期、退出预案可执行性。
7. 形成成本-风险情景对比（乐观/基线/压力）并给出关键敏感因子。
8. 输出`tco-operational-risk.md`并移交adoption-recommendation用于最终裁决。

---

## 质量门禁/Quality Gates

- 必须同时覆盖直接成本与至少三类隐性成本（集成/培训/运维/切换）。
- 必须显式给出分析周期与关键假设，避免不可复现估算。
- 必须评估锁定风险与退出可行性，不得仅做短期成本比较。
- 必须给出至少一个压力场景下的成本与风险变化。
- 必须标注高不确定性参数及其对结论影响方向。
- 输出必须可映射到最终建议选项（Adopt/Pilot/Defer等）的经济约束条件。

---

## Gotchas/注意事项

- 不要把一次性采购价当成TCO，长期运营成本常是主要成本项。
- 不要忽略组织学习成本与流程改造成本，这些会决定落地速度。
- 不要假设锁定风险可忽略，需检验数据与接口的可迁移性。
- 不要只给单点估算，必须给出情景区间与敏感性说明。
- 不要将“低成本”直接等于“低风险”，应联动可靠性与合规成本看总风险。

---

## 关联资源

- 上游输入：`risk-research-brief`, `vendor-source-diligence`, `security-risk-review`, `compliance-check`
- 证据治理：`research-evidence-ledger`, `research-synthesis`
- 下游链路：`adoption-recommendation`
