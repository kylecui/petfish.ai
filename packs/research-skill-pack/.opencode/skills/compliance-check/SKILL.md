---
name: compliance-check
description: 对候选方案开展合规风险研究，覆盖隐私、数据驻留/跨境传输、许可证与合同条款、政策匹配与法务待确认项。Use when the user says "合规评估", "合规检查", "compliance check", "compliance risk", "法规风险评估", "隐私风险", "data residency", "cross-border transfer", "license compliance", "license review", "DPA", "合同条款", or "policy fit".
compatibility: opencode
license: Apache-2.0
---

## 作用/Purpose

围绕采购与采用决策，识别并结构化记录合规相关风险与待确认事项。该skill必须覆盖：
1) 隐私、数据驻留、跨境传输与行业监管约束；
2) 许可证、合同条款、知识产权与出口管制边界；
3) 与内部采购政策和控制流程的匹配性。

输出是合规风险研究材料，不提供法律意见或法律结论。

---

## 触发场景/Trigger Scenarios

- 用户提出“合规检查 / compliance check / 法规风险评估”
- 方案涉及个人信息、敏感数据或跨境处理
- 采购流程要求核验license、合同条款与政策符合性
- 需要判断行业监管约束对方案上线的影响
- 安全评审后需补齐合规可行性判断

---

## 输入/Input

- `risk-brief.md`
- `vendor-profile.md` 与 `source-profile.md`
- `security-risk.md`
- applicable policies（内部采购政策、数据分类与外部监管要求）
- 可选：合同草案、DPA条款、license文本

---

## 输出/Output

- `compliance-check.md`

---

## 工作流/Workflow

1. 基于风险简报与安全评审，确定需要覆盖的法规与政策边界。
2. 盘点数据要素与流转路径，标注驻留地、处理地、传输路径与跨境节点。
3. 审查隐私与数据处理条款：目的限制、保存期限、删除权与可审计性。
4. 审查许可证与合同条款：授权范围、再分发限制、赔偿责任、终止与退出条款。
5. 审查行业与地域监管要求：特定行业规范、出口控制、第三方处理限制。
6. 对照内部采购政策，标记符合项、缺口项、需审批豁免项与补充控制项。
7. 输出`compliance-check.md`，区分已确认事实、待法律/采购确认事项，并移交tco-operational-risk与adoption-recommendation。

---

## 质量门禁/Quality Gates

- 报告必须声明“本输出为合规风险研究，不构成法律意见”。
- 必须覆盖隐私、数据驻留/跨境、许可证/合同、政策匹配四类核心维度。
- 每项高风险必须给出触发条件、潜在后果与建议控制措施。
- 必须区分“政策不满足”与“信息不足待确认”，不得混同为同一结论。
- 涉及license时必须明确许可类型与适用条件，不得模糊描述。
- 必须给出需要法务/采购/数据治理参与确认的事项清单。

---

## Gotchas/注意事项

- 不要把本skill输出包装成法律意见书或合规认证结论。
- 不要忽略跨境与驻留细节，区域差异会直接影响可上线性。
- 不要只看主合同，附录条款、DPA与数据处理补充协议同样关键。
- 不要将“供应商声明合规”视为充分证据，需记录验证状态与缺口。
- 不要跳过内部采购政策映射，否则结论难以执行。

---

## 关联资源

- 上游输入：`risk-research-brief`, `vendor-source-diligence`, `security-risk-review`
- 证据治理：`research-evidence-ledger`, `research-quality-reviewer`
- 下游链路：`tco-operational-risk`, `adoption-recommendation`
