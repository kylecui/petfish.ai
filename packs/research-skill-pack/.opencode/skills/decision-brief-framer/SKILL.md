---
name: decision-brief-framer
description: 将模糊决策请求转化为结构化决策简报，明确决策问题、备选项、决策人、约束、偏好、must-have、nice-to-have与一票否决项。Use when the user says "决策简报", "decision brief", "怎么选", "which option", "go/no-go", "取舍", "拍板", "是否上线", "是否采购", or "该不该".
compatibility: opencode
license: Apache-2.0
---

## 作用/Purpose

在做比较和推荐前先统一问题定义，避免“比较很细、问题不清”。该skill必须覆盖：
1) 决策问题与场景范围定义；
2) 约束、偏好与底线条件结构化；
3) 后续标准构建的输入固化。

输出应成为决策链路的唯一问题基线，而不是会议纪要式描述。

---

## 触发场景/Trigger Scenarios

- 用户要求“怎么选/选哪个/是否上线/是否采购”
- 需要把讨论从观点对撞转成结构化决策问题
- 需要明确决策人、时限和责任边界
- 需要区分必须满足项与偏好项
- 需要为后续`decision-criteria-builder`准备输入

---

## 输入/Input

- decision intent（问题背景、目标结果、时限）
- known options（已知候选方案或候选范围）
- decision owner and stakeholders（拍板人、参与方）
- constraints and preferences（预算、合规、性能、偏好）

---

## 输出/Output

- `decision-brief.md`

---

## 工作流/Workflow

1. 定义决策问题与业务场景，排除不在当前决策窗口内的问题。
2. 明确决策人、参与角色、时间边界与责任归属。
3. 收集并整理已知备选项，标注信息完整度与待补数据。
4. 梳理约束条件：预算、时间、法规、技术、组织依赖。
5. 区分must-have、nice-to-have与deal-breaker，并给出可验证定义。
6. 明确决策输出形式（go/no-go、rank、条件通过）与生效条件。
7. 生成`decision-brief.md`，并交接到`decision-criteria-builder`。

---

## 质量门禁/Quality Gates

- 决策问题必须单一明确，避免多个问题混写。
- 决策人和最终责任归属必须显式记录。
- 已知备选项必须列出来源与当前信息缺口。
- must-have与nice-to-have边界必须可检验。
- deal-breaker必须具有“一票否决”可执行规则。
- 输出必须包含后续标准构建所需字段。

---

## Gotchas/注意事项

- 不要在问题未定义清楚前直接进入打分比较。
- 不要把个人偏好伪装成must-have。
- 不要遗漏决策时限，否则流程会无限延长。
- 不要忽略信息缺口，需标注“已知/未知”边界。
- 不要将多个不同层级决策混在同一简报中。

---

## 关联资源

- `decision-criteria-builder`
- `research-brief-framer`
- `research-evidence-ledger`
- `product-decision-brief`
