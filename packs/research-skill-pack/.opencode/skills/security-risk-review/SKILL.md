---
name: security-risk-review
description: 对候选方案执行安全风险评审，覆盖数据暴露、访问控制、密钥管理、供应链、执行越权、prompt injection与审计响应能力。Use when the user says "安全评审", "security risk review", "security risk assessment", "data security", "数据泄露风险", "access control review", "prompt injection", "tool abuse", "越权执行", "incident response", or "supply chain risk".
compatibility: opencode
license: Apache-2.0
---

## 作用/Purpose

对候选方案执行结构化安全风险研究，输出可追溯的风险条目与缓解建议。该skill必须覆盖：
1) 数据暴露面、身份与权限、密钥与凭据处理；
2) 供应链、执行与模型相关风险（含prompt injection）；
3) 审计可追溯性、隔离与事件响应准备度。

输出用于支持采购决策中的安全判断，不替代正式渗透测试或认证审计。

---

## 触发场景/Trigger Scenarios

- 用户要求“安全风险评审 / security review / security risk assessment”
- 需要评估候选工具是否会引入数据泄露与权限扩散风险
- 需要识别LLM/Agent链路中的prompt injection与执行越权风险
- 采购流程要求提交安全章节作为go/no-go输入
- 尽调完成后，需要补齐安全维度证据

---

## 输入/Input

- `risk-brief.md`
- `vendor-profile.md` 与 `source-profile.md`
- 架构与集成信息（接口、认证、网络、日志）
- 可选：现有安全基线、内部控制要求、历史事件记录

---

## 输出/Output

- `security-risk.md`

---

## 工作流/Workflow

1. 读取风险简报与尽调画像，锁定需优先审查的资产与攻击面。
2. 评估数据暴露路径：输入、处理、存储、传输、日志与备份。
3. 评估身份与访问控制：认证机制、授权粒度、最小权限与越权路径。
4. 评估密钥与敏感配置处理：存储、轮换、注入、审计与泄露恢复。
5. 评估供应链与执行风险：依赖来源、更新策略、执行沙箱、命令边界。
6. 评估模型特有风险：prompt injection、工具调用滥用、上下文污染、输出误导。
7. 评估审计与响应能力：可观测性、审计线索、告警、事件分级与处置流程。
8. 输出`security-risk.md`，按风险等级给出缓解措施并移交compliance-check与tco-operational-risk。

---

## 质量门禁/Quality Gates

- 必须覆盖数据、访问控制、密钥、供应链、执行、审计六大维度。
- 每条高风险必须包含触发条件、影响范围、缓解路径与残余风险。
- 必须区分“已验证事实”与“待验证假设”，避免混写。
- 必须给出至少一条与prompt injection或工具调用相关的专门检查结论。
- 必须明确哪些控制可在采购条件中落地，哪些需后续实施。
- 报告必须声明其为风险评审，不等同于正式安全审计认证。

---

## Gotchas/注意事项

- 不要把该输出描述为“正式安全审计”或“认证结论”。
- 不要只检查静态权限清单，必须覆盖运行时执行与调用链风险。
- 不要忽略日志与审计可追溯性，否则事件响应不可执行。
- 不要把“供应商承诺”直接等同于控制有效，需标注验证状态。
- 不要脱离业务场景给风险评级，关键路径资产应优先评估。

---

## 关联资源

- 上游输入：`risk-research-brief`, `vendor-source-diligence`
- 证据治理：`research-evidence-ledger`, `research-citation-auditor`
- 下游链路：`compliance-check`, `tco-operational-risk`, `adoption-recommendation`
