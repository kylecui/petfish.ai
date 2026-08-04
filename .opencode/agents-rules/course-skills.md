# 课程开发规则

## 核心原则

1. **项目边界优先**：先判断任务属于治理/提纲/正文/实验/资料/QA/QC/发布哪个阶段。
2. **提纲先于正文**：大范围调整时先更新提纲，再批量改正文。
3. **QA先于QC**：先发现问题，再闭环判定与发布建议。
4. **学员/教师资料严格分离**：答案、讲师提示不得泄露到学员材料。
5. **参考资料 ≠ 交付物**：`references/` 必须经提炼后才能进入 `docs/`。
6. **保留可追踪性**：重大调整必须留下计划、变更记录或QC结论。

## 默认目录结构

| 目录 | 用途 |
|------|------|
| `docs/00-project/` | 项目治理（brief, milestone, change-log） |
| `docs/01-outline/` | 总纲、模块图、课时分配 |
| `docs/02-content/` | 课程正文 |
| `docs/03-labs/` | 实验、演示、作业（学员版/答案版分离） |
| `docs/04-learner-pack/` | 学员资料（不含答案/讲师提示） |
| `docs/05-instructor-pack/` | 教师资料（含答案/讲解提示） |
| `docs/06-qa/` | QA记录（问题发现、分类、严重性） |
| `docs/07-qc/` | QC报告（问题状态、发布建议） |
| `references/` | 参考资料原件 |
| `release/` | 已通过QA/QC的稳定版本 |

## Skill路由

| 任务类型 | Skill |
|---------|-------|
| 项目统筹、跨阶段协调 | `course-development-orchestrator` |
| 目录初始化、结构审计 | `course-directory-structure` |
| 总纲、模块划分、课时分配 | `course-outline-design` |
| 正文编写、章节重写 | `course-content-authoring` |
| 实验设计、验收标准 | `course-lab-design` |
| 学员讲义、手册 | `learner-materials` |
| 教师讲义、答题参考 | `instructor-reference-materials` |
| 问题发现、审阅清单 | `course-quality-assurance` |
| 发布决策、QC报告 | `course-quality-control-reporting` |
| 参考资料研读 | `reference-document-review` |

**默认流程**：`course-development-orchestrator` → 专项skill → QA → QC → release

## 质量门禁（发布前必须通过）

**QA门禁**：记录了哪些问题、严重性、哪些必须在发布前关闭。

**QC门禁**：哪些问题已关闭、哪些接受风险延期、当前版本是否允许发布（正式/受限/内部试运行）。

**发布条件**：至少一轮QA + QC结论 + 学员/教师材料边界明确 + 无内部痕迹。

## 操作规则

**可直接修改**：纯排版格式、明显错字、明确归属的文件归位。

**先出建议再修改**：大规模重命名、跨目录搬迁、合并/拆分章节、调整实验验收口径。

**禁止事项**：
- 禁止将教师答案混入学员资料
- 禁止跳过QA/QC直接发布
- 禁止把 `references/` 直接当 `release/`
- 禁止大规模乱移文件（先审计，先建议）

## 目录工具

```bash
# 初始化目录
uv run .opencode/skills/course-directory-structure/scripts/bootstrap_course_tree.py --root . --mode full

# 审计结构
uv run .opencode/skills/course-directory-structure/scripts/check_course_tree.py --root .
```

## 一句话原则

先分层，后写作；先提纲，后正文；先QA，后QC；先结论可追踪，再进入发布。
