---
name: risk-research-brief
description: 明确评估对象、采用场景、风险边界与决策要求，形成可执行的风险采购研究简报。Use when the user says "风险评估", "risk assessment", "工具评估", "tool evaluation", "供应商评估", "vendor evaluation", "该不该用", "是否值得引入", "should we adopt", "要不要引入", or "采购评估".
compatibility: opencode
license: Apache-2.0
---

## 作用/Purpose

将“是否引入某工具/供应商/数据源”的模糊问题，转化为结构化风险采购研究任务。该skill必须覆盖：
1) 评估对象、采用场景与业务关键性；
2) 风险边界（数据、部署、权限、合规、成本）与风险偏好；
3) 明确后续链路输入，驱动尽调、安全、合规、TCO与最终建议。

输出应作为整条Risk-Procurement链路的起点，而不是笼统背景说明。

---

## 触发场景/Trigger Scenarios

- 用户提出“要不要引入这个工具/平台/供应商”
- 需要先定义评估范围再开展“vendor due diligence / security review / compliance check”
- 业务方要求澄清“数据会不会出域、风险边界在哪、决策需要什么证据”
- 团队需统一风险口径与决策标准，避免各环节各自假设
- 需要形成后续研究链路的统一输入基线

---

## 输入/Input

- candidate target（产品、模型服务、SaaS、开源项目或数据源）
- adoption scenario（业务流程、用户角色、关键任务）
- data profile（数据类型、敏感级别、体量与生命周期）
- deployment mode（SaaS/私有化/混合、网络边界、地区）
- risk appetite（可接受风险、不可触碰红线）
- required decision（go/no-go/pilot与时间窗口）

---

## 输出/Output

- `risk-brief.md`

---

## 工作流/Workflow

1. 定义评估对象与替代对象，明确本次决策边界与不在范围项。
2. 拆解采用场景：业务关键路径、失败影响、可降级策略。
3. 标注数据与关键资产：数据敏感度、驻留要求、权限面、日志要求。
4. 明确部署模式与运行约束：网络拓扑、身份体系、环境隔离、上线节奏。
5. 设定风险偏好与决策门槛：必须满足项、可缓释项、可延期项。
6. 形成研究任务拆分并映射链路：vendor-source-diligence → security-risk-review → compliance-check → tco-operational-risk。
7. 输出风险研究简报，定义最终adoption-recommendation所需证据清单。

---

## 质量门禁/Quality Gates

- `risk-brief.md`必须明确“评估对象、场景、边界、决策问题”四要素。
- 必须区分“in-scope / out-of-scope”，避免隐式扩大评估范围。
- 必须标注数据敏感度与关键资产，不得只写业务描述。
- 必须定义至少3类风险边界（安全/合规/成本/运维中的任意三类以上）。
- 必须明确风险偏好与不可接受红线，而非仅列风险清单。
- 必须给出后续链路的输入要求与交付顺序。

---

## Gotchas/注意事项

- 不要把“技术可用”误当成“可被采购与可被治理”。
- 不要忽略失败场景与业务降级方案，否则风险评级失真。
- 不要把部署模式写成默认值，必须绑定具体环境约束。
- 不要在简报阶段给最终结论，先锁定问题定义与证据需求。
- 不要遗漏替代方案，否则后续TCO与建议会失去对照基线。

---

## 关联资源

- 上游基础：`research-brief-framer`, `research-source-discovery`
- 证据治理：`research-evidence-ledger`, `research-synthesis`
- 下游链路：`vendor-source-diligence` → `security-risk-review` → `compliance-check` → `tco-operational-risk` → `adoption-recommendation`
