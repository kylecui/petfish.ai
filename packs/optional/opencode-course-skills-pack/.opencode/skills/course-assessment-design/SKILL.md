---
name: course-assessment-design
description: 设计课程测评与考核体系——出题、题库建设、quiz设计、试卷结构、难度分布、考试时限、评分标准与rubric评分量表。覆盖MCQ单选、多选、短答、rubric评分项、项目里程碑五种题型；每题绑定Bloom层级与课程目标ID；题面进learner-pack、答案与评分标准进instructor-pack（师生分离）。Use this skill when用户要求测评设计、assessment design、quiz、题库、question bank、考试、exam、出题、评分标准、评分细则。
license: Proprietary
compatibility: Designed for OpenCode. Assumes repo-local `.opencode/skills` discovery
  and standard read/edit/bash tools; optional scripts should run through a repo-local uv environment; requires uv and Python 3.11+.
metadata:
  pack: opencode-course-skills
  version: 1.0.0
  author: petfish-team
---

# 目的（Purpose）

设计可绑定教学目标、可评分、可复用的课程测评：quiz、单元测验、期末考试、rubric评分项与项目里程碑考核。

# 适用场景

- 测评设计、assessment、assessment design
- quiz、题库、question bank
- 考试、exam、出题
- 评分标准、评分细则、rubric
- 试卷结构、难度分布、考试时限规划

# 边界（不适用）

- 实验/动手环境设计 → `course-lab-design`
- 大纲层形成性/总结性配比规划 → `course-outline-design`（其 `references/assessment-planning.md`）

# 测评设计模式（9字段）

每套测评显式定义以下9个字段，缺项即设计未完成：

1. **目标绑定**：每题挂Bloom层级 + 课程目标ID（来自`docs/01-outline/`的可引用目标清单）。无目标ID的题不进题库。
2. **题型**（五种，各含规范）：
   - MCQ单选：4-5个选项，1个正确；干扰项必须来自真实误解，不是明显错误
   - 多选：2-3个正确项；部分给分规则显式声明（或全对才给分，二选一并写明）
   - 短答：预期答案要点化（3-5个得分点）；列出可接受的表述变体
   - rubric评分项：维度×等级矩阵，每格写行为锚点描述，禁用"好/中/差"空泛等级
   - 项目里程碑：可交付物 + 验收清单 + checkpoint时点
3. **题干规范**：单一考点（一题只考一件事）；无歧义干扰项（每个干扰项须可辩护为"为什么错"）；情境化（真实场景优先于抽象提问）
4. **答案与评分标准** → 写入 `docs/05-instructor-pack/`
5. **题面** → 写入 `docs/04-learner-pack/`（师生分离机制复用：与labs的学员版/教师版分离、04/05资料包分层同一套约定；题面与答案永不混排，混排即QA blocker）
6. **难度分布**：易:中:难配比建议——形成性5:3:2，总结性3:4:3；按目标Bloom层级校准，不为凑分布硬造偏题
7. **时限**：按题型基准耗时估算（MCQ约1-1.5分钟/题、短答3-5分钟、项目里程碑按天），总时限×1.5缓冲系数
8. **抽样复测题标记**：跨场次复用的锚题标记`anchor: true`，用于难度漂移检测与等值化；锚题不对外公开、不出现在learner-pack的练习卷中
9. **题库组织**：默认落盘 `docs/03-labs/assessments/<module>/`；每题一个可寻址文件，frontmatter携带`objective_id / bloom_level / type / difficulty / anchor`字段，供qa_scan与后续抽取组卷

# 评审检查（Review checks）

- 每题是否都能映射到至少一个课程目标ID？
- 干扰项是否来自真实误解（而非一眼假）？
- 难度分布是否与测评用途匹配（形成性 vs 总结性）？
- 题面与答案是否彻底分离（04 vs 05）？
- 锚题是否已标记且未泄露到learner-pack？

# 产出分层（Output split）

- `docs/04-learner-pack/`：题面（试卷/练习卷），不含答案与评分标准
- `docs/05-instructor-pack/`：答案、评分标准、rubric、难度标注、锚题索引

# Gotchas

- 不出"奖励背题"的题——答案不能由题干语法线索（"总是/从不"）推出
- 不用"以上都对/以上都不对"式选项
- 不把rubric写成空泛等级词——每格要有行为锚点
- 不让答案或评分标准出现在learner-pack（师生分离红线）
- 不为凑难度分布硬造偏题怪题

See:
- `assets/blueprint-template.md`（9字段蓝图 + 题库条目 + 填写示例，设计时复制使用）
- `references/item-quality-guide.md`（题目质量分析：P值/区分度/选项分析/锚题等值化，按需读取）
- `course-outline-design/references/assessment-planning.md`（大纲层配比与题型-目标匹配矩阵，按需读取）
- `course-content-authoring/references/pedagogy-compact.md`（Bloom动词表与检索练习/间隔原则，按需读取）
