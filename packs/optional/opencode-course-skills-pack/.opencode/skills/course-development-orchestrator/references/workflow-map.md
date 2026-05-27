# 课程开发工作流映射

## 主工作流
1. 项目初始化与目录搭建
2. 开发计划与里程碑
3. 课程大纲/章节树
4. 章节内容
5. 实验/练习
6. 学员资料
7. 教师参考资料
8. QA审核
9. QC整改与发布报告

## 路由建议
-任务宽泛、跨多个工作流：`course-development-orchestrator`
-需要统一目录、命名、归档：`course-directory-structure`
-需要把参考材料读成课程输入：`reference-document-review`
-需要可复用Markdown产出：`markdown-course-writing`
-需要图示、流程图、架构图：`drawio-course-diagrams`

## 课程项目核心产物
- `00-project/`：项目总说明、术语表、里程碑
- `01-outline/`：课程总纲、章节树、课时分配
- `02-content/`：各章正文
- `03-labs/`：实验说明、答案、环境要求
- `04-learner-pack/`：学员讲义、预习材料、作业
- `05-instructor-pack/`：讲师讲稿、答疑点、答案
- `06-qa/`：核查记录、问题清单
- `07-qc/`：整改记录、发布报告
