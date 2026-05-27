# 课程项目标准目录与命名规范

## 1. 目标

本规范用于统一基于OpenCode的课程开发项目目录，使课程策划、内容编写、实验设计、学员资料、教师资料、QA、QC与正式交付物有明确边界，降低文件散落、命名混乱、版本混淆和资料泄漏的风险。

## 2. 推荐目录树

```text
.opencode/
  skills/
docs/
  00-project/
    project-brief.md
    milestone-plan.md
    risk-register.md
    change-log.md
  01-outline/
    course-overview.md
    syllabus.md
    module-map.md
  02-content/
    01-module-01/
      01-lesson-01.md
      02-lesson-02.md
    02-module-02/
  03-labs/
    01-lab-01/
      learner-guide.md
      instructor-key.md
      environment-notes.md
    02-lab-02/
  04-learner-pack/
    learner-handbook.md
    glossary.md
    recap-sheet.md
  05-instructor-pack/
    instructor-guide.md
    delivery-notes.md
    answer-key-index.md
  06-qa/
    qa-plan.md
    qa-checklist.md
    qa-review-round-01.md
  07-qc/
    qc-report-round-01.md
    release-decision.md
assets/
  drawio/
  images/
  tables/
references/
  external/
  internal/
release/
  v0.1/
  v1.0/
archive/
  superseded/
  abandoned/
```

## 3. 分层原则

### 3.1 `docs/00-project/`
放项目治理类材料，不放具体教学内容。包括项目目标、范围、计划、风险、里程碑、变更记录。

### 3.2 `docs/01-outline/`
放课程顶层结构，不放展开后的章节正文。包括课程定位、学员画像、模块划分、课时分配、先修要求、考核与实验映射。

### 3.3 `docs/02-content/`
放课程正文。建议按“模块/章节/课时”组织，而不是按作者、日期或随意主题组织。

### 3.4 `docs/03-labs/`
放实验与演示材料。学员操作手册和教师答案必须分离；环境说明与教学目标也要分离。

### 3.5 `docs/04-learner-pack/`
放纯学员材料，要求剔除答案、讲师提示、内部审阅痕迹和QA/QC讨论内容。

### 3.6 `docs/05-instructor-pack/`
放教师讲解提示、答题参考、时间控制建议、常见问题和课堂风险提示。

### 3.7 `docs/06-qa/`
放质量保证过程材料。强调“发现问题”，而不是“悄悄修改”。

### 3.8 `docs/07-qc/`
放质量控制和闭环结果。强调“问题如何被处理、是否关闭、是否允许发布”。

### 3.9 `assets/`
放被多个文档引用的静态资源，不把核心正文写进assets。

### 3.10 `references/`
放外部参考和内部参考，不与交付正文混放。

### 3.11 `release/`
放对外或阶段性交付的稳定版本，不放零散草稿。

### 3.12 `archive/`
放已废弃、被替代或不再继续维护的内容。不要把仍在使用但“比较旧”的正式材料误扔进归档。

## 4. 命名规范

-目录和文件优先使用小写kebab-case
-有顺序的目录和文件使用两位数字前缀
-一个文件只承载一个主主题
-学员文件名称中避免出现 `answer`、`internal`、`review`
-教师文件名称中建议显式带上 `instructor`、`key`、`notes`
- QA/QC文件建议带轮次或日期，例如：
  - `qa-review-round-01.md`
  - `qc-report-2026-04-16.md`

## 5. 目录整理规则

### 5.1可直接归位的情况
以下情况可以直接整理：
-文件名与用途高度明确
-目录中存在唯一合理目标位置
-文件未体现明显的多人协作冲突
-文件不是外部系统生成且路径被其他系统强依赖

### 5.2应先报告、再整理的情况
以下情况应优先出整理建议，而不是直接移动：
-文件名模糊，如 `final.md`、`new2.md`、`修改版.docx`
-一个文件可能同时属于多个模块
-文件被多处链接引用
-学员版和教师版内容混在一个文件中
- QA/QC批注混在正式正文中

## 6. 最小可发布目录要求

若要进入首次可发布评审，至少应具备：
- `docs/00-project/`
- `docs/01-outline/`
- `docs/02-content/`
- `docs/03-labs/`
- `docs/06-qa/`
- `docs/07-qc/`
- `release/`

## 7. 建议工作流

1. 先创建标准目录树
2. 再放入现有材料
3. 做一次结构审计
4. 输出整理建议
5. 再做移动和重命名
6. 做QA
7. 生成QC报告
8. 形成 `release/` 版本

## 8. 常见错误

-用日期驱动整个课程目录，而不是用课程结构驱动
-学员资料、教师资料和QA文件混在一起
-把“参考资料收集”误当成“课程内容完成”
-只有内容文件，没有项目、QA、QC和发布层
-归档目录变成第二个工作目录
