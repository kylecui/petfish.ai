---
name: vendor-source-diligence
description: 对供应商、开源项目与数据来源做尽调，评估身份与治理、SLA与支持、许可证兼容、bus factor、锁定与退出条件。Use when the user says "供应商尽调", "vendor due diligence", "source diligence", "开源风险", "open source risk", "数据源可信度", "SLA", "lock-in risk", "exit condition", or "source reliability".
compatibility: opencode
license: Apache-2.0
---

## 作用/Purpose

建立评估对象的来源可信度与供给稳定性画像，作为安全、合规与TCO评估前置输入。该skill必须覆盖：
1) 商业供应商身份、经营稳定性、服务与支持能力；
2) 开源项目维护健康度、治理结构、许可证与社区风险；
3) 数据来源的合法性、更新机制与可追溯性。

输出应可直接输入后续安全与合规审查，而不是停留在“网络口碑汇总”。

---

## 触发场景/Trigger Scenarios

- 用户要求“供应商尽调 / vendor due diligence / source diligence”
- 需要比较商业方案与开源替代方案的可持续性
- 需要判断数据源是否可信、是否可长期稳定供给
- 采购前需要核验支持承诺、SLA、锁定风险与退出条件
- 风险简报已完成，需进入链路第二阶段画像构建

---

## 输入/Input

- `risk-brief.md`（评估边界与决策门槛）
- vendor/source list（供应商、开源项目、数据源候选清单）
- 可用公开资料（官网、文档、仓库、公告、政策）
- 可选：采购历史、内部使用反馈、事故记录

---

## 输出/Output

- `vendor-profile.md`
- `source-profile.md`

---

## 工作流/Workflow

1. 基于`risk-brief.md`确定尽调范围、优先级与证据标准。
2. 区分对象类型：商业供应商、开源项目、数据来源，分别定义核验维度。
3. 对商业供应商核验身份、业务稳定性、服务承诺、支持模型与锁定条款。
4. 对开源项目核验维护活跃度、治理透明度、发布节奏、许可证兼容性与bus factor。
5. 对数据来源核验采集合法性、更新频率、来源追溯、偏差风险与中断风险。
6. 汇总安全与信誉轨迹：历史事件、响应表现、披露质量、整改信号。
7. 形成`vendor-profile.md`与`source-profile.md`，并明确传递给security-risk-review与compliance-check的重点问题。

---

## 质量门禁/Quality Gates

- 必须显式区分商业供应商与开源项目，不得套用同一评价框架。
- 每个候选对象至少给出身份/治理、稳定性、支持、锁定四类证据。
- 许可证信息必须明确版本与适用边界，不得只写“开源/商用可用”。
- 数据来源必须说明采集路径与可追溯性，不得仅引用二手转载。
- 必须标记高风险依赖点（单一维护者、单一云区、单一渠道等）。
- 输出必须列出移交给security与compliance环节的待核问题。

---

## Gotchas/注意事项

- 不要把开源项目当作“无供应商风险”，其维护与治理风险需单独建模。
- 不要将营销材料当作尽调证据，优先使用可验证事实。
- 不要忽略支持模型的真实可执行性（时区、响应SLA、升级路径）。
- 不要只看当前热度，需关注维护连续性与关键人依赖。
- 不要提前给采用结论，尽调输出是证据与风险画像而非裁决。

---

## 关联资源

- 上游输入：`risk-research-brief`, `research-source-discovery`
- 证据治理：`research-note-capture`, `research-evidence-ledger`
- 下游链路：`security-risk-review`, `compliance-check`, `tco-operational-risk`
