---
name: learning-resource-discovery
description: 按学习目标发现、筛选并排序学习资源，覆盖官方文档、教材、论文、教程、课程、代码仓库、实验与基准。Use when the user says "学习资源", "learning resources", "资料推荐", "resource discovery", "推荐书籍", "resource list", "课程推荐", "教程", "入门到进阶", "beginner to advanced", "资源可信度", "资源更新频率", "resource ranking", or "学什么材料".
compatibility: opencode
license: Apache-2.0
---

## 作用/Purpose

围绕学习简报执行系统化资源发现与证据化筛选，形成可追溯资源清单与索引。该skill必须覆盖：
1) 多类型资源采集与分类；
2) 质量、相关性、难度与时效评估；
3) 面向学习路径的排序与缺口识别。

输出应支持后续路径设计与阶段任务配置，而不是“链接堆砌”。

---

## 触发场景/Trigger Scenarios

- 已有学习目标，需要系统搜集学习资料
- 需要区分入门、进阶、实战、前沿等资源层次
- 需要判断资源可信度、更新频率与适配度
- 需要产出可复用的资源索引而非一次性列表
- 需要为`learning-path-designer`提供可执行输入

---

## 输入/Input

- `learning-brief.md`（目标能力、基线、时间与产出要求）
- scope and constraints（主题边界、时间预算、语言偏好）
- resource preferences（偏好形式：文档/视频/代码/论文）
- 可选：已有候选资源与历史踩坑记录

---

## 输出/Output

- `resource-list.md`
- `resource-index.jsonl`

---

## 工作流/Workflow

1. 读取`learning-brief.md`，提取能力目标、约束与资源需求画像。
2. 按资源类型建立检索池：官方文档、教材、论文、教程、课程、仓库、实验、讲座、基准。
3. 执行初筛：去重、可访问性检查、明显低质与过时内容剔除。
4. 执行复筛：相关性、难度匹配、可信度、维护活跃度与实践价值评分。
5. 形成分层排序（基础/进阶/专项/实践），并标注适用人群与先修要求。
6. 识别关键缺口（如缺练习、缺真实案例、缺系统教材）并提出补齐建议。
7. 输出`resource-list.md`与`resource-index.jsonl`，并交接到`learning-path-designer`。

---

## 质量门禁/Quality Gates

- 每类核心资源至少应有候选项，缺失类型必须说明原因。
- 所有入选资源必须包含来源信息与访问路径。
- 评分维度必须统一，避免不同资源不可比。
- 资源难度分层必须与学习者基线一致。
- 至少标注1项高质量实践型资源（代码、实验或benchmark）。
- 至少识别1项资源缺口并给出补齐策略。

---

## Gotchas/注意事项

- 不要只按热度推荐，需优先保证与目标能力匹配。
- 不要忽视时效性，过时资料会误导学习路径。
- 不要将营销型内容当作高可信资源。
- 不要只给单一资源形态，需兼顾理论与实践。
- 不要省略筛选口径，否则结果不可复审。

---

## 关联资源

- `learning-goal-framer`
- `learning-path-designer`
- `research-source-discovery`
- `research-evidence-ledger`
