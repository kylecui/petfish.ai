---
name: experience-brief-framer
description: 定义体验或活动目标、参与者、约束、偏好与成功标准，形成可执行的活动研究简报。Use when the user says "活动策划", "event planning", "旅行规划", "trip planning", "体验设计", "experience design", "帮我安排", "help me organize", "会议策划", "工作坊", "团建", or "展览".
compatibility: opencode
license: Apache-2.0
metadata:
  version: "0.11.1"
  author: "petfish-team"
---

## 作用/Purpose

将模糊的体验或活动需求转化为结构化研究简报，明确目标、参与者、活动类型、约束条件、成功判据与交付清单。该skill必须覆盖：
1) 场景定义与目标边界；
2) 参与者画像与关键偏好；
3) 可执行研究输入，为后续场地研究与行程设计提供统一口径。

输出应能直接驱动后续链路，而不是停留在笼统需求描述。

---

## 触发场景/Trigger Scenarios

- 用户要求“活动策划 / event planning / 体验设计 / experience design”
- 需要先定义旅行、会议、工作坊、团建或展览的目标与范围
- 需要澄清时间、预算、地点、无障碍等约束条件
- 需要把“想做一次活动”转化为可研究、可执行的brief
- 需要为后续场地研究与日程规划建立一致输入

---

## 输入/Input

- 初始需求（活动目的、预期成果、目标受众）
- participants profile（人数、年龄层、能力差异、特殊需求）
- constraints（时间窗、预算上限、地理范围、可达性）
- preferences（活动风格、节奏、内容偏好、禁忌）
- 可选：历史活动复盘、组织政策、品牌或文化要求

---

## 输出/Output

- `experience-brief.md`

---

## 工作流/Workflow

1. 明确活动类型（travel/conference/workshop/team-building/exhibition）与主目标。
2. 定义参与者分层、人数结构与关键体验需求。
3. 梳理硬约束（时间、预算、地点、可达性）与软偏好（风格、节奏、内容）。
4. 识别成功标准：结果指标、体验指标、风险容忍度与验收口径。
5. 形成交付物清单与优先级，标注必须项与可选项。
6. 校验信息缺口，列出待确认问题与外部验证需求。
7. 生成`experience-brief.md`并显式作为`venue-destination-research`的输入基线。

---

## 质量门禁/Quality Gates

- 活动目标必须可度量，至少包含1项结果指标与1项体验指标。
- 参与者信息必须覆盖人数、画像分层和特殊需求。
- 约束条件必须区分硬约束与可协商约束。
- 成功标准与输出清单必须逐条对应，不得出现“目标无交付映射”。
- 至少识别3个关键不确定性并标注验证路径。
- brief中必须明确下一步链路入口为`venue-destination-research`。

---

## Gotchas/注意事项

- 不要把“组织者偏好”直接等同于“参与者真实需求”。
- 不要只写预算总额，应拆分固定成本与可变成本假设。
- 不要忽略无障碍、饮食限制、健康条件等边界需求。
- 不要把“活动氛围好”作为唯一成功标准，需配套可验证指标。
- 不要跳过信息缺口清单，否则后续场地与行程研究会反复返工。

---

## 关联资源

- `research-brief-framer`
- `research-source-discovery`
- `research-evidence-ledger`
- `venue-destination-research`
