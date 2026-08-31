---
description: 设计课程测验/考试/题库，含题型、评分标准、难度分布与师生分离落盘（前置：已有课程提纲与目标ID）
---
请根据下面的要求设计或重构课程测评。

任务说明：
$ARGUMENTS

前置条件（缺失时先补齐，不要凭空出题）：
1. 课程提纲已存在于 `docs/01-outline/`，且课程目标有可引用的ID
2. 明确测评用途：形成性（课时/模块内）或总结性（模块边界/课程末）

执行要求：
1. 使用 `course-assessment-design` skill的9字段模式设计（目标绑定/题型/题干规范/答案与评分标准/题面/难度分布/时限/锚题/题库组织）
2. 每题绑定Bloom层级+课程目标ID；无目标绑定的题不进题库
3. 题面落盘 `docs/04-learner-pack/`；答案与评分标准落盘 `docs/05-instructor-pack/`（师生分离，混排即QA blocker）
4. 题库默认组织到 `docs/03-labs/assessments/<module>/`，每题携带 `objective_id / bloom_level / type / difficulty / anchor` 字段
5. 标注难度（易/中/难）、时限估算，跨场次复用题标记 `anchor: true`
6. 如只需大纲层的形成性/总结性配比规划，改用 `course-outline-design`；如要动手实验设计，改用 `course-lab-design`
