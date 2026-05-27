---
name: learning-progress-reviewer
description: 对学习执行结果进行阶段化成效复盘，评估概念理解、操作能力、迁移表现与下一步纠偏方向。Use when the user says "学习进度", "learning progress", "阶段检查", "学习效果", "掌握程度", "复盘", "里程碑达成", "milestone review", "Concept/Procedure/Transfer", "Next Step", "学习评估", "能力诊断", "薄弱点", "纠偏", "学习成效", "阶段复盘", "学习决策", or "达标判断".
compatibility: opencode
license: Apache-2.0
metadata:
  version: "0.11.1"
  author: "petfish-team"
---

## 作用/Purpose

将学习过程数据与里程碑达成情况转化为结构化评估，输出可执行改进建议。该skill必须覆盖：
1) Concept/Procedure/Transfer三层能力诊断；
2) Output质量与里程碑达成度评估；
3) Weakness定位与Next Step纠偏计划。

输出应形成可追踪复盘结论，而不是主观“学得还行”。

---

## 触发场景/Trigger Scenarios

- 已执行练习计划，需要阶段性复盘学习成效
- 需要判断是否达到学习路径里程碑
- 需要识别薄弱点并安排下一阶段纠偏
- 需要输出可交付的学习评估文档
- 需要在继续投入前做学习效果决策

---

## 输入/Input

- practice execution results（任务完成记录、得分、失败日志）
- learning milestones（来自`learning-path.md`的阶段目标）
- produced artifacts（代码、笔记、实验报告、演示材料）
- 可选：导师反馈、同伴评审、时间投入统计

---

## 输出/Output

- `progress-review.md`

---

## 工作流/Workflow

1. 汇总阶段执行数据，校验任务完成率与里程碑覆盖率。
2. 评估Concept维度：关键概念是否理解、是否能准确解释。
3. 评估Procedure维度：标准流程是否可独立复现、错误率如何。
4. 评估Transfer维度：能否迁移到新场景并产出有效结果。
5. 评估Output维度：交付物质量、完整性与可复用程度。
6. 汇总Weakness与风险信号，制定Next Step（补学/重练/进阶）计划。
7. 生成`progress-review.md`，并标注本链路为最终评估步骤，必要时回流到`learning-practice-planner`。

---

## 质量门禁/Quality Gates

- 必须覆盖Concept/Procedure/Transfer/Output/Weakness/Next Step六个维度。
- 每个维度至少包含1条证据（任务结果、产出或反馈）。
- 必须给出阶段完成率（%）与里程碑达成状态（达成/部分/未达成）。
- 至少识别2个具体薄弱点，且每个薄弱点有对应改进动作。
- Next Step必须包含时间窗口与验收标准。
- 结论中不得使用无依据评级；主判断需附证据引用。

---

## Gotchas/注意事项

- 不要只看完成数量，不看产出质量与迁移能力。
- 不要把“花了很多时间”当作“学习有效”的证据。
- 不要忽略失败样本，失败记录是关键诊断输入。
- 不要给空泛建议（如“继续努力”），需具体到动作。
- 不要一次复盘覆盖过长周期，建议按阶段滚动评估。

---

## 关联资源

- `learning-practice-planner`
- `learning-path-designer`
- `learning-goal-framer`
- `decision-recommendation`
