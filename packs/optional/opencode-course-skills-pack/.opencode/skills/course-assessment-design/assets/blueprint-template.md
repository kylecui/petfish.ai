# 测评蓝图模板（blueprint-template）

> 用法：设计新测评时复制填写；蓝图属教师侧资产。字段定义见SKILL.md，此处只留填写位。

## 测评蓝图

```markdown
# <测评名称>（范围：<module>/<lesson>）

## 1. 目标绑定
- 覆盖目标ID：<id, id, ...>
- Bloom分布：<层级×数量>

## 2. 题型与数量
- MCQ单选：<N>｜多选：<N>｜短答：<N>｜rubric评分项：<N>｜项目里程碑：<N>

## 3. 题干规范确认
- [ ] 单一考点　[ ] 干扰项可辩护　[ ] 情境化

## 4. 答案与评分标准
- 落盘路径：<05-instructor-pack/...>

## 5. 题面
- 落盘路径：<04-learner-pack/...>

## 6. 难度分布
- 易:中:难 = <x:y:z>（用途：<形成性/总结性>）

## 7. 时限
- 基准估算：<计算式>
- 发布时限：<T分钟>

## 8. 抽样复测锚题
- 锚题ID：<列表>

## 9. 题库组织
- 目录：<03-labs/assessments/.../>
- 组卷规则：<抽取方式>
```

## 题库条目（每题一文件）

```markdown
---
objective_id: <id>
bloom_level: <remember|understand|apply|analyze|evaluate|create>
type: <mcq|multi|short_answer|rubric_item|milestone>
difficulty: <easy|medium|hard>
anchor: <true|false>
---

## 题面（学员侧）

<题干/选项/任务>

## 评分（教师侧）

<答案/得分点/rubric/验收清单>

## 干扰项归因（选择题必填）

- <选项>：来自<误解>，错因<一句话>
```

## 填写示例（节选，Git入门课程）

```markdown
---
objective_id: OBJ-M2-03
bloom_level: understand
type: mcq
difficulty: medium
anchor: true
---

## 题面（学员侧）

同一条分支上，你和同事改了同一个文件的不同函数，合并时Git提示冲突。
以下哪个说法是正确的？

A. 冲突说明有人改错了代码，应回退后者的提交
B. Git会把两处修改自动拼接进文件，无需人工确认
C. 需要人工编辑冲突标记区，决定保留哪些改动后再标记解决
D. 只能删除整个分支重新开始

## 评分（教师侧）

正确答案：C。误选A/B/D各扣本题全部分数（单选无部分给分）。

## 干扰项归因（选择题必填）

- A：来自"冲突=错误"的误解——冲突是正常的并行开发现象，不是谁写错了
- B：来自"工具全自动"的误解——Git只在行级自动合并，同文件冲突必须人工裁决
- D：来自"怕搞坏仓库"的新手焦虑——实际冲突解决是常规操作，代价极低
```

组卷示例：从题库按 `objective_id × difficulty` 分层抽取，每个目标ID至少1题；锚题（anchor: true）连续两个批次复用，用于监控整体难度漂移。

