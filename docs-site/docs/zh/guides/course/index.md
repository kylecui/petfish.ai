---
title: 课程开发指南
description: 使用 PEtFiSh course skill pack 管理课程开发全生命周期的完整指南。
---

# 课程开发指南

**course** pack 提供了一套完整的 skills，用于从初始简报到最终发布的整个生命周期内构建、审阅和管理课程材料。

这个 pack 并没有将课程创建仅仅视为写字，而是强制执行讲师和学员材料之间的严格分离，在每个阶段保持质量门禁，并将工作构建为逻辑阶段，以防止最常见的课程开发失败：范围蔓延、受众污染和无纪律的发布。

这个 pack 弥合了“一堆草稿文件夹”和“专业管理的课程产品”之间的差距。无论你是构建一个为期 3 天的 Kubernetes 训练营，还是重构一个学期长度的大学课程，course pack 都能确保结构一致性、受众隔离和可追踪的质量决策。

```bash
# 安装 course pack (macOS / Linux)
curl -fsSL https://raw.githubusercontent.com/kylecui/petfish.ai/master/remote-install.sh | bash -s -- --pack course

# 安装 course pack (Windows PowerShell)
& ([scriptblock]::Create((irm https://raw.githubusercontent.com/kylecui/petfish.ai/master/remote-install.ps1))) -Pack course
```

---

## 概览

course pack 专为从“为这个新主题编写大纲”到“对整个课程进行最终质量控制检查”等任务而设计。它在保持结构一致性和确保清晰的受众边界方面表现出色。

### 包内包含什么

course pack 是模块化的。虽然 orchestrator 将一切联系在一起，但每个 skill 都是一个独立的工具，能够在其特定领域内执行深度操作。

| Skill | 目的 | 在流水线中的角色 |
|---|---|---|
| **`course-development-orchestrator`** | 将任务路由到正确的阶段和 skill。理解完整生命周期并在各阶段之间传递上下文。 | **Orchestrator** |
| **`course-directory-structure`** | 初始化、审计和修复目录布局。强制执行命名约定并检测放错位置的文件。 | **Governance** |
| **`development-plan-governance`** | 管理里程碑、变更日志、风险登记册和验收门禁。 | **Governance** |
| **`course-outline-design`** | 设计顶层教学大纲、模块拆分、学习目标和课时分配。 | **阶段 1: Outline** |
| **`course-content-authoring`** | 编写和重构章节内容。确保术语一致性和适当的过渡。 | **阶段 2: Content** |
| **`markdown-course-writing`** | 格式化并标准化 Markdown 输出。规范化术语，添加验证占位符。 | **阶段 2: Content** |
| **`course-lab-design`** | 创建练习、目标、环境说明、验证标准和答案。 | **阶段 3: Labs** |
| **`learner-materials`** | 生成面向学生的讲义、工作表、术语表和复习笔记。 | **阶段 4: Materials** |
| **`instructor-reference-materials`** | 生成讲师笔记、演讲要点、时间指导和答案。 | **阶段 4: Materials** |
| **`course-quality-assurance`** | 记录问题、检查完整性、审查一致性并对严重程度进行分类。 | **阶段 5: QA** |
| **`course-quality-control-reporting`** | 形成发布决策、结项报告和整改计划。 | **阶段 6: QC** |
| **`drawio-course-diagrams`** | 为架构和模块图生成基于 XML 的结构化 draw.io 图表。 | **Reference** |
| **`reference-document-review`** | 读取外部 PDF、文档、图片和网页。提取并规范化为课程输入。 | **Reference** |
| **`course-methodology-playbook`** | 打包以往项目中的可复用工作流、审阅启发式方法和约定。 | **Methodology** |
| **`skill-reference-discovery`** | 从外部 GitHub 仓库和资源中发现可复用的 agent skill 模式。 | **Methodology** |

### 何时使用此 Pack 与何时不使用

**在以下情况使用此 pack：**

- **构建综合课程：** 你需要制作结构化的培训课程、工作坊、训练营或具有明确学习目标和评估的多模块课程。
- **分离受众：** 你拥有的材料必须为讲师（答案、时间提示、交付风险）和学员（讲义、练习、术语表）以不同形式存在。
- **需要质量门禁：** 你需要一个正式的流程来发现问题 (QA)、做出决策 (QC) 并使发布具有可追溯性。
- **重构现有材料：** 你继承了一个杂乱无章的草稿文件夹，需要审计、分类并将其重新组织成标准结构。
- **从现有文档中提取课程材料：** 你拥有内部文档、会议记录或参考 PDF，需要将其提炼成可用于教学的内容。

**在以下情况不要使用此 pack：**

- **写博客文章或标准文档：** 请改用标准写作 skill 或 `petfish-style-rewriter` skill。
- **编写应用程序代码：** 此 pack 处理课程，而不是软件工程。
- **生成无结构内容：** 此 pack 期望并强制执行严格的目录层次结构。如果你想要自由写作，请使用通用工具。
- **运行单个快速审查：** 如果你只需要对一个文件进行语法检查，请使用直接编辑工具，而不是完整的 QA/QC 流水线。

---

## 课程开发流水线

该 pack 通过严格的流水线运行，旨在防止课程开发中最常见的失败模式：没有首先建立边界、结构或质量标准就直接跳到写正文。

如果你使用 orchestrator (`course-development-orchestrator`)，它会自动在这些阶段之间进行路由。如果你手动请求特定操作（例如“只写模块3的第2课”），agent 将直接加载相应的单个 skill。

```text
项目简报 (Project Brief)
    │
    ▼
[ 阶段 0: Setup ] ──► [ 阶段 1: Outline ] ──► [ 阶段 2: Content ]
                                                        │
                                                        ▼
[ 阶段 7: Release ] ◄── [ 阶段 6: QC ] ◄── [ 阶段 5: QA ] ◄── [ 阶段 4: Materials ] ◄── [ 阶段 3: Labs ]
```

### 上下文传递

每个阶段都会生成为下一个阶段提供输入的产物。大纲定义了模块和课时；内容创作引用该大纲以确保章节不会超过分配的时间。实验设计引用内容以确保练习与教授的内容相匹配。QA 引用之前的所有产物以检查一致性。这种紧密耦合确保了课程在内部是连贯的。

!!! warning "警告"
    流水线的存在是因为每个阶段都依赖于前一个阶段的输出。如果你直接从项目简报跳到内容创作，你不可避免地会产生与任何商定结构不一致、遗漏学习目标或不切实际地分配时间的章节。

---

## 快速开始

### 示例 1: 新项目初始化

如果你从头开始一个新课程项目：

=== "Prompt"

    ```text
    /course-init 我们正在构建一个关于“Kubernetes 简介”的新课程，
    面向具有 2 年以上经验的后端开发者。
    请设置项目目录并创建初始项目简报。
    ```

=== "预期行为"

    1. agent 加载 `course-directory-structure` 来引导标准目录树。
    2. 它创建所有 8 个文档目录（从 `docs/00-project` 到 `docs/07-qc`）以及 `assets/`、`references/`、`release/` 和 `archive/`。
    3. 它生成包含目标受众、先修要求和范围的 `docs/00-project/project-brief.md`。
    4. 它生成概述交付时间表的 `docs/00-project/milestone-plan.md`。
    5. 它在进入大纲阶段之前会请求批准。

### 示例 2: 接管现有项目

如果你继承了一个装满凌乱文件的文件夹：

=== "Prompt"

    ```text
    /course-audit 审查当前目录。这些文件很乱——草稿和最终版本混在一起，
    没有清晰的结构。在移动任何东西之前，给我一个重组计划。
    ```

=== "预期行为"

    1. agent 使用 `course-directory-structure` 扫描当前目录。
    2. 它按层级对每个文件进行分类：项目治理、大纲、内容、实验、学员材料、讲师材料、QA、QC、参考资料或归档。
    3. 它输出一个建议的映射表（例如，`draft-kubernetes.md` → `docs/02-content/01-module/01-lesson.md`）。
    4. 它标记无法自信分类的文件，并请求你的输入。
    5. 在执行任何文件移动之前，它**等待你的确认**。

### 示例 3: 完整流水线运行

如果你希望 agent 编排整个工作流：

=== "Prompt"

    ```text
    我们需要为 DevOps 工程师构建一个为期 2 天的“使用 GitHub Actions 进行 CI/CD”工作坊。
    端到端驱动此过程：大纲、内容、实验、材料，然后是 QA。
    ```

=== "预期行为"

    1. agent 加载 `course-development-orchestrator`。
    2. 它初始化目录结构并创建项目简报。
    3. 它起草带有模块划分和课时分配的教学大纲。
    4. 大纲批准后，它将每个模块扩展为章节内容。
    5. 它为每个动手模块设计实验练习。
    6. 它生成学员讲义和讲师指南。
    7. 它对整个包进行 QA 并记录发现的问题。

??? example "为什么将 QA 和 QC 分开？"
    course pack 严格将 **发现问题** (QA) 与 **决定如何处理这些问题** (QC) 分开。
    
    - **QA** 创建问题检查清单：“模块 3 引用了直到模块 5 才介绍的概念。”
    - **QC** 确定这些问题是否会阻碍发布：“这是一个严重度为 2 的问题。是接受风险并在带有已知限制的情况下发布，还是在发布前修复？”
    
    这种分离确保了问责制。QA 从不单方面决定“可以发布”。QC 从不说“我不知道有什么问题”。

---

## 阶段 0: 项目设置

在编写任何课程内容之前，项目需要清晰的边界。**orchestrator** 和 **directory-structure** skills 负责这项基础工作。

### 标准目录布局

该 pack 强制执行严格的目录层次结构，每个文件都有且只有一个正确的位置：

```text
docs/
  00-project/        # 项目简报、里程碑、风险登记册、变更日志
  01-outline/        # 教学大纲、模块划分、课时分配
  02-content/        # 实际课程文本（章节、课程）
  03-labs/           # 练习、演示、环境说明
  04-learner-pack/   # 面向学生的讲义、术语表、工作表
  05-instructor-pack/# 教师笔记、答案、时间提示
  06-qa/             # 审查检查清单、问题日志
  07-qc/             # 发布决策、结项报告
assets/              # 图片、图表、draw.io 文件、表格
references/          # 输入材料（PDF、记录、外部文档）
release/             # 稳定的、带有版本号的交付物
archive/             # 弃用的或被取代的内容
```

!!! warning "References 与 Release"
    `references/` 中的文件是 **输入**——在进入课程之前必须经过提炼、重写和改编的原始材料。它们绝不会被视为最终的课程内容。
    
    `release/` 中的文件是 **输出**——经过 QA 和 QC 的稳定、带版本号的交付物。草稿和进行中的工作绝不会进入此目录。

### 目录语义

每个目录对其包含的内容都有严格的边界：

| 目录 | 包含 | 不包含 |
|---|---|---|
| `00-project/` | 简报、里程碑、风险登记册 | 课程散文、课程内容 |
| `01-outline/` | 教学大纲、模块图、课时表 | 完整的章节文本、实验步骤 |
| `02-content/` | 章节文本、课程叙述 | QA 评论、发布决策 |
| `03-labs/` | 练习步骤、环境说明 | 仅供讲师使用的答案（这些应放入 `05-instructor-pack/`） |
| `04-learner-pack/` | 学生讲义、术语表 | 答案、讲师笔记、内部审查标记 |
| `05-instructor-pack/` | 教学笔记、答案、时间安排 | 面向学生的讲义 |
| `06-qa/` | 问题日志、完整性检查清单 | 整改措施（这些应放入 QC） |
| `07-qc/` | 发布决策、结项报告 | 原始问题发现（这是 QA 的工作） |

### 命名约定

pack 强制在所有文件中使用一致的命名：

- **目录和文件:** 小写的 `kebab-case`（例如 `01-module-intro/`, `lesson-02.md`）
- **有序内容:** 两位数数字前缀（例如 `01-`, `02-`, `03-`）
- **每个文件一个主题:** 每个 Markdown 文件恰好涵盖一节课、一个实验或一次审查
- **避免无意义的名称:** 切勿使用 `final`、`new`、`v2-latest` 或仅包含日期的名称

```text
# 好的命名
docs/02-content/01-module-kubernetes-basics/01-what-is-k8s.md
docs/03-labs/01-lab-deploy-pod/learner-guide.md
docs/06-qa/qa-review-round-01.md

# 坏的命名
docs/kubernetes-draft-final-v3.md
docs/lab-NEW.md
docs/review-notes-kyle.md
```

### 使用脚本引导

pack 包含用于自动目录初始化和审计的 Python 脚本：

=== "初始化新项目"

    ```bash
    uv run .opencode/skills/course-directory-structure/scripts/bootstrap_course_tree.py \
      --root . --mode full --with-placeholders
    ```
    
    这将创建完整的目录树，并在每个目录中包含占位符 `README.md` 文件，解释其用途。

=== "审计现有项目"

    ```bash
    uv run .opencode/skills/course-directory-structure/scripts/check_course_tree.py --root .
    ```
    
    这将扫描当前目录并报告缺失的目录、放错位置的文件以及违反命名约定的情况。

### 项目简报和里程碑

阶段 0 生成两个关键的治理文档：

**`docs/00-project/project-brief.md`** 应该定义：

- 目标受众和先修要求
- 课程范围和明确的排除项
- 交付形式（工作坊、训练营、自定进度等）
- 预期交付物
- 成功标准

**`docs/00-project/milestone-plan.md`** 应该定义：

- 阶段截止日期
- 每个阶段的交付物验收标准
- 风险登记册条目
- 变更控制流程

!!! tip "提示"
    课程开发中最常见的错误是直接跳入编写章节。如果没有项目简报，你就没有关于受众是谁、他们已经知道什么或“完成”是什么样子的共识。简报只需 15 分钟即可编写完成，却能节省数天的返工时间。

---

## 阶段 1: 大纲设计

在编写详细的正文之前，**`course-outline-design`** skill 会起草教学大纲。它确保学习目标正确映射到模块，并且课时分配对目标受众是现实的。

### Outline Skill 产生什么

正确构建的大纲包括：

- **模块划分:** 将主题逻辑分组为可教学的单元
- **学习目标:** 每个模块具体、可衡量的成果（使用布鲁姆分类法动词）
- **课时分配:** 每个模块的讲座、实验和讨论的现实时间预算
- **先修映射:** 哪些模块依赖于早期模块中的概念
- **学员收益声明:** 学生在完成每个模块后能做什么

### 示例 Prompts

=== "从头起草"

    ```text
    /course-outline 为面向后端开发者的为期 3 天的 Kubernetes 训练营起草一份教学大纲。
    第 1 天涵盖基础知识，第 2 天涵盖工作负载，第 3 天涵盖生产运维。
    ```

=== "重构现有大纲"

    ```text
    /course-outline 我们当前的大纲将 12 个模块挤在 2 天内。
    将其重构为切合实际的样子。在必要的地方进行删减或合并。
    告诉我你会删除什么以及原因。
    ```

=== "添加模块"

    ```text
    /course-outline 在网络和安全模块之间添加一个关于“使用 Istio 的服务网格”的新模块。
    调整课时分配以适应现有的 3 天限制。
    ```

### 课时分配纪律

大纲 skill 强制执行现实的时间预算。一个常见的失败模式是为一个需要 3 小时动手实验时间的主题分配 1 小时。该 skill 会交叉检查：

- 讲座时长 vs. 内容深度
- 实验时长 vs. 练习步骤数量
- 总时长 vs. 可用日历时间（考虑休息、设置、问答）

??? example "大纲输出示例"
    ```markdown
    # CI/CD with GitHub Actions — 课程大纲
    
    ## 模块 1: 基础 (3h)
    - **目标:** 解释 CI/CD 生命周期并指出 GitHub Actions 的适用位置。
    - 讲座: 1.5h | 实验: 1h | 讨论: 0.5h
    - 先修要求: Git 基础、熟悉命令行
    
    ## 模块 2: 工作流语法 (4h)
    - **目标:** 编写并调试多步 GitHub Actions 工作流。
    - 讲座: 1.5h | 实验: 2h | 讨论: 0.5h
    - 先修要求: 模块 1
    
    ## 模块 3: 高级模式 (4h)
    - **目标:** 实现矩阵构建、缓存和可重用工作流。
    - 讲座: 1.5h | 实验: 2h | 讨论: 0.5h
    - 先修要求: 模块 2
    ```

!!! info "信息"
    该 pack 强制执行一条严格的规则：**在大纲获得批准之前，切勿编写章节内容。** 如果你要求 agent 在大纲存在之前编写模块 3，它要么会拒绝，要么会先创建一个最小化的大纲。这防止了最昂贵的返工场景：在 QA 时才发现整个模块是多余的或顺序错误的。

---

## 阶段 2: 内容创作

大纲获得批准后，**`course-content-authoring`** 和 **`markdown-course-writing`** 会将大纲的要点扩展为可读的章节。

### Content Authoring 处理什么

内容 skill 生成：

- **章节叙述:** 遵循大纲学习目标的清晰解释
- **术语一致性:** 相同的概念在各章中决不会用不同的名称调用
- **过渡:** 每节课都会引用之前的内容并预览接下来的内容
- **示例和类比:** 与目标受众经验水平相匹配的具体说明
- **关键要点:** 每章末尾总结的学习要点

### Agent 强制执行的内容规则

Agent 被明确指示在创作过程中遵循以下规则：

1. **内容中无内部标记:** “TODO”、“TBD”、“稍后填写”绝不会出现在章节文件中。如果某些内容不完整，它将被记录为 `docs/06-qa/` 中的 QA 问题。
2. **无受众污染:** 仅供讲师使用的信息（答案、教学提示、时间提示）绝不会出现在内容文件中。它属于 `docs/05-instructor-pack/`。
3. **一致的格式:** 所有章节遵循相同的 Markdown 结构——标题级别、代码块语言、admonition 样式。
4. **来源归属:** 如果内容源自参考材料，则来源会记录在章节元数据中，而不是埋藏在散文中。

### 示例 Prompts

=== "编写章节"

    ```text
    /course-content 根据批准的大纲起草模块 1 第 2 课：“理解 Pods”。
    包括从第 1 课（集群架构）的过渡，并为第 3 课（Deployments）所需的概念做好铺垫。
    ```

=== "为受众重写"

    ```text
    /course-content 为非技术受众重写模块 2。当前版本假设了深厚的 Linux 知识。
    简化示例并添加更多类比。保持学习目标不变。
    ```

=== "扩展章节"

    ```text
    /course-content 模块 4 中的“网络”部分太单薄——只有 3 段。
    使用 ClusterIP、NodePort 和 LoadBalancer 服务的具体示例对其进行扩展。包含一个对比表。
    ```

### Markdown 格式标准

**`markdown-course-writing`** skill 强制所有课程文档保持一致的格式：

- **标题层次:** H1 为课程标题，H2 为主要部分，H3 为子部分。切勿跳过级别。
- **代码块:** 始终指定语言（` ```yaml `, ` ```bash `, ` ```python `）。切勿使用裸的三重反引号。
- **表格:** 使用 Markdown 表格进行比较和结构化数据。保持它们的可读性（不要出现 10 列的怪物）。
- **Admonitions:** 在课程内容中使用 MkDocs 样式的 admonitions 来表示警告、提示和注意。

??? example "示例"
    **好:** 结构化、具备受众意识、无内部标记
    ```markdown
    # 理解 Pods
    
    在上一节课中，我们探索了集群架构...
    
    ## 什么是 Pod？
    
    Pod 是 Kubernetes 中最小的可部署单元...
    
    ## Pod 生命周期
    
    Pods 经历几个阶段...
    
    ## 关键要点
    
    - Pod 包装一个或多个容器
    - Pod 按照设计是短暂的
    ```
    
    **坏:** 缺少过渡、有内部标记、格式不一致
    ```markdown
    # Pods
    
    TODO: add intro
    
    pods 是最小的单元。它们运行容器。
    
    (Kyle: 检查这对于 k8s 1.29 是否仍然准确)
    
    ## next steps
    稍后填写
    ```

---

## 阶段 3: 实验设计

实验需要学生可以毫无歧义地遵循的精确执行步骤。**`course-lab-design`** skill 创建的练习具有严格的结构，将学生看到的内容与讲师知道的内容分开。

### 实验结构

该 skill 产生的每个实验都包含这些组件：

| 组件 | 受众 | 描述 |
|---|---|---|
| **目标 (Objective)** | 双方 | 学生将完成什么 |
| **先修要求 (Prerequisites)** | 双方 | 开始之前必须完成的内容 |
| **环境 (Environment)** | 双方 | 所需的软件、硬件和配置 |
| **步骤 (Steps)** | 学员 | 编号的、明确的说明 |
| **验证 (Validation)** | 学员 | 如何验证每个步骤是否成功 |
| **答案 (Answer Key)** | 仅讲师 | 预期输出、常见错误、评分标准 |
| **故障排除 (Troubleshooting)** | 仅讲师 | 常见故障点及其解决方案 |
| **时间安排 (Timing)** | 仅讲师 | 每部分的预期持续时间 |

!!! danger "危险"
    实验 skill 强制严格分离面向学员和面向讲师的内容。答案、故障排除指南和时间估计**绝不会**放在学员指南文件中。这防止了在向学生分发材料时发生意外泄漏。
    
    - 学员指南: `docs/03-labs/01-lab-deploy-pod/learner-guide.md`
    - 讲师指南: `docs/05-instructor-pack/01-lab-deploy-pod-answers.md`

### 示例 Prompts

=== "设计实验"

    ```text
    /course-lab 为“部署你的第一个 Pod”创建一个实验练习。学生应该编写一个 Pod 清单，
    应用它，验证 Pod 正在运行，并查看其日志。为讲师包括常见故障点。
    ```

=== "添加验证步骤"

    ```text
    /course-lab 实验 3 练习缺少验证标准。
    在每个主要步骤之后添加明确的检查，以便学生知道他们是否成功。
    ```

=== "设计顶点项目"

    ```text
    /course-lab 为最后一天设计一个顶点项目 (Capstone project)。学生应使用课程中学到的所有知识
    部署一个多层应用程序（前端 + 后端 + 数据库）。包含评分标准。
    ```

### 环境规格

实验 skill 明确规定了环境要求。每个实验都会指定：

- **软件版本:** 工具的确切版本（例如，“kubectl v1.28+”，“Docker 24.x”）
- **硬件最低要求:** 实验环境的 CPU、RAM 和磁盘要求
- **网络要求:** 实验期间是否需要互联网访问
- **预配置资源:** 开始之前必须存在的任何云帐户、集群或数据库

??? example "示例"
    ```markdown
    ## 环境要求
    
    | 资源 | 要求 |
    |---|---|
    | Kubernetes 集群 | Minikube v1.32+ 或 kind v0.20+ |
    | kubectl | v1.28 或更高版本 |
    | Docker | 24.x (用于构建镜像) |
    | RAM | 至少可用 8 GB |
    | 磁盘 | 至少剩余 10 GB |
    | 互联网 | 必需 (用于拉取容器镜像) |
    
    ### 实验前设置
    1. 启动本地集群: `minikube start --memory=4096`
    2. 验证连接: `kubectl cluster-info`
    3. 创建实验命名空间: `kubectl create namespace lab-01`
    ```

---

## 阶段 4: 材料

课程交付需要为不同受众提供不同的视图。此阶段产生两套完全独立的材料。

### 学员材料

**`learner-materials`** skill 创建面向学生的资产：

- **讲义:** 每个模块关键概念的浓缩摘要
- **工作表:** 填空或简答练习以巩固知识
- **术语表:** 课程中使用的所有技术术语的定义
- **阅读材料包:** 课前准备材料和背景阅读
- **复习笔记:** 课后总结供复习

**关键规则：** 学员材料绝不能包含：

- 答案或解决方案
- 讲师时间提示或演讲笔记
- 内部审查评论或 QA 注解
- 草稿标记或“TODO”项目

### 讲师材料

**`instructor-reference-materials`** skill 创建面向教师的资产：

- **演讲要点:** 每个部分的建议谈话要点
- **时间指导:** 每个部分的预期持续时间以及缓冲建议
- **答案:** 所有练习和实验的完整解决方案
- **讨论提示:** 在关键时刻向班级提出的建议问题
- **演示提示:** 现场演示的分步说明
- **交付风险提醒:** 常见陷阱以及如何恢复（例如，“如果演示失败，请使用 `assets/demos/` 中的预录制备份”）

### 示例 Prompts

=== "生成学员包"

    ```text
    生成模块 1 的学生讲义。包含引入的所有术语的词汇表
    以及包含 5 个复习问题的工作表。
    ```

=== "生成讲师包"

    ```text
    生成模块 1 的讲师指南。包含演讲要点、每个部分的时间安排、
    工作表的答案，以及关于常见学生问题的注释。
    ```

=== "生成课前阅读"

    ```text
    为模块 3 创建课前阅读包。学生在到达时应
    具备对 YAML 语法和 Linux 文件权限的基础理解。
    ```

!!! tip "提示"
    在处理模块时，在同一会话中生成学员和讲师材料。这可确保讲师的答案与学员工作表问题完全匹配，并且时间估计考虑了实际练习的难度。

---

## 阶段 5: 质量保证 (QA)

**`course-quality-assurance`** skill 会寻找问题。它不去修复它们——它记录并附带严重性分类，以便阶段 6 (QC) 可以做出明智的发布决策。

### QA 检查什么

QA skill 系统性地审查：

| 检查类别 | 寻找什么 |
|---|---|
| **完整性** | 缺失的模块、空白部分、占位符文本 |
| **一致性** | 各章定义不同的术语、冲突的说明 |
| **准确性** | 无法编译的代码示例、过时的 CLI 标志、错误的版本号 |
| **受众污染** | 学员材料中的答案、内容文件中的讲师笔记 |
| **实验-内容对齐** | 引用尚未教授的概念的实验，或跳过已教授概念的实验 |
| **格式** | 损坏的 Markdown、不一致的标题级别、裸代码块 |
| **AI 痕迹 (AI slop)** | 通用填充文本、机器式过渡、无根据的最高级 |

### 严重性分类

QA 发现的每个问题都会被分类：

| 严重性 | 定义 | 发布影响 |
|---|---|---|
| **Critical (严重)** | 会误导学生的事实错误内容 | 阻碍发布 |
| **Major (主要)** | 缺失部分、损坏的实验、受众污染 | 阻碍发布 |
| **Minor (次要)** | 格式问题、拼写错误、措辞不清晰 | 不阻碍发布 |
| **Suggestion (建议)** | 潜在改进、样式建议 | 仅供参考 |

### 示例 Prompts

=== "完整 QA 审查"

    ```text
    /course-qa 审查完整的课程包。检查所有模块、实验和材料。
    记录发现的每个问题并进行严重性分类。
    ```

=== "目标 QA"

    ```text
    /course-qa 审查模块 3 及其相关的实验 3。重点关注
    实验步骤是否真正匹配章节中教授的内容。
    ```

=== "发布前 QA"

    ```text
    /course-qa 这是发布前的最终 QA 轮次。仅关注阻碍性问题——Critical 和 Major 级别。
    我们已经修复了第 1 轮中的次要格式问题。
    ```

### QA 输出格式

QA 发现会被写为 `docs/06-qa/` 下结构化的 Markdown：

```markdown
# QA 审查 — 第 1 轮

## 总结
- Critical: 2
- Major: 5
- Minor: 12
- Suggestion: 8

## 严重问题 (Critical Issues)

### QA-001: 实验 2 中错误的 kubectl 命令
- **位置:** docs/03-labs/02-lab-deployments/learner-guide.md, 第 47 行
- **描述:** `kubectl create deployment` 使用了已弃用的 `--generator` 标志
- **影响:** 学生会看到警告消息并可能会感到困惑
- **建议:** 替换为 `kubectl create deploy nginx --image=nginx:1.25`

### QA-002: 答案泄露在学员讲义中
- **位置:** docs/04-learner-pack/module-02-handout.md, 第 89 行
- **描述:** "预期输出" 部分包含完整解决方案
- **影响:** 学生在尝试练习之前就看到了答案
- **建议:** 移至 docs/05-instructor-pack/module-02-answers.md
```

!!! info "信息"
    QA skill 被明确指示**记录问题，而不是修复它们**。这确保你在内容被修复之前维护了错误情况的纸质轨迹。`content-crafter` agent 或 `course-content-authoring` skill 负责实际的修复。

---

## 阶段 6: 质量控制 (QC)

**`course-quality-control-reporting`** skill 做出发布决策。它审查 QA 发现，验证哪些问题已关闭，并生成正式报告。

### QC 决定什么

QC 准确回答四个问题：

1. **哪些问题已关闭？**（已验证修复）
2. **哪些问题被接受为已知风险？**（发布前不予修复）
3. **是否允许发布此版本？**（是/否/有条件）
4. **如果是有条件的，条件是什么？**（例如，“仅供内部预览发布”）

### 发布决策类型

| 决策 | 含义 |
|---|---|
| **Full Release (完整发布)** | 所有阻碍问题已关闭。准备好进行内外部发发。 |
| **Limited Release (有限发布)** | 接受某些已知问题。发布给受限受众（例如，内部预览、试点群组）。 |
| **Internal Trial (内部试验)** | 仍存在重大问题。仅供内部演练发布。 |
| **Blocked (已阻止)** | 存在未解决的严重问题。不能以任何形式发布。 |

### 示例 Prompts

=== "标准 QC"

    ```text
    /course-qc 检查最新的 QA 报告 (docs/06-qa/qa-review-round-02.md)。
    所有阻碍性问题都解决了吗？请给我一份发布建议。
    ```

=== "有条件发布"

    ```text
    /course-qc 我们还有 2 个剩余的主要问题。评估我们是否可以
    在下周为试点群组进行有限发布。
    ```

=== "发布就绪性"

    ```text
    /course-release-ready 检查所有 QA/QC 历史。我们是否可以清晰地将
    文件移入 release/v1.0/？
    ```

### QC 输出格式

QC 报告写入 `docs/07-qc/`：

```markdown
# QC 报告 — 2026-05-15

## 决策: LIMITED RELEASE (有限发布)

## 问题状态
| ID | 严重性 | 状态 | 备注 |
|---|---|---|---|
| QA-001 | Critical | ✅ Closed | 在 commit abc123 中修复 |
| QA-002 | Critical | ✅ Closed | 移至讲师包 |
| QA-003 | Major | ⚠️ Accepted | 已知限制，已在发布说明中记录 |
| QA-004 | Major | ✅ Closed | 已重写 |
| QA-005 | Major | ❌ Open | 推迟至 v1.1 |

## 条件
- 仅批准发布给内部试点群组
- 外部发布前必须解决 QA-005
- 修复 QA-005 后需要重新审查

## 审批人
课程开发负责人 (通过 QC 评审会)
```

---

## 阶段 7: 发布

一旦 QC 通过，文件就具备移入 `release/` 目录的资格。此目录仅包含稳定的、带版本号的交付物。

### 发布目录结构

```text
release/
  v1.0/
    learner-pack/      # 所有面向学生的材料
    instructor-pack/   # 所有面向教师的材料
    labs/              # 实验指南（仅限学员版）
    slides/            # 演示文稿文件（如适用）
    RELEASE-NOTES.md   # 此版本中的内容，已知问题
  v1.1-preview/
    ...
```

### 什么进入 Release

- ✅ 通过 QC 的最终课程内容
- ✅ 学员讲义和工作表
- ✅ 讲师指南和答案
- ✅ 实验指南（学员版）
- ✅ 包含已知问题的发布说明

### 什么不进入 Release

- ❌ QA 审查日志（保留在 `docs/06-qa/`）
- ❌ QC 决策报告（保留在 `docs/07-qc/`）
- ❌ 原始参考材料（保留在 `references/`）
- ❌ 草稿或进行中的文件
- ❌ 项目治理文件（简报、里程碑）

!!! warning "警告"
    如果你在发布的文件中发现拼写错误，**不要**直接在 `release/` 中编辑它。在 `docs/02-content/` 中编辑源文件，对修复运行 QA/QC，然后将更正后的版本复制到新的发布文件夹中（例如 `release/v1.0.1/`）。这保持了可追溯性。

---

## 参考材料

pack 包含了用于处理馈入课程流水线的外部输入的辅助 skills。

### 参考文档审查

**`reference-document-review`** skill 读取外部材料并将其转换为结构化的输入：

- **PDFs:** 提取关键内容、规范化格式、识别与教学相关的部分
- **DOCX/DOC:** 转换为保留结构的 Markdown
- **图片:** 为了可访问性描述图表和截图
- **网页:** 捕获和规范化网页内容并提供来源归属
- **会议记录:** 从混乱的笔记中提取教学要点和行动项

=== "处理 PDF"

    ```text
    /course-source-review 阅读随附的 Kubernetes 文档 PDF。
    提取与我们模块 3 (网络) 相关的部分，并将其格式化为
    课程输入笔记。
    ```

=== "综合多个来源"

    ```text
    /course-source-review 我们在 references/ 中有 3 份参考文档。
    比较它们对“Pod 安全标准”的覆盖范围，并产生一份适合我们
    内容创作阶段的综合材料。
    ```

!!! info "信息"
    参考材料处理会生成**中间产物**——提取的笔记、差距分析和重写建议。这些产物必须经过 `course-content-authoring` 进一步处理才能成为实际课程内容。绝不要将原始的参考提取内容直接提升到 `docs/02-content/`。

### 课程图表

**`drawio-course-diagrams`** skill 为以下内容生成基于 XML 的图表：

- 架构概览（例如，Kubernetes 集群拓扑）
- 模块依赖图
- 工作流图（例如，CI/CD 流水线阶段）
- 实验拓扑图
- 时间线可视化

输出为兼容 draw.io 的 XML，保存至 `assets/diagrams/`。

---

## 命令与 Agents

课程 pack 在 skills 本身之外提供了两层快速入口点。

### 命令 (Commands)

命令是高频工作流触发器。每个命令加载适当的 skill(s) 并应用正确的上下文：

| 命令 | 目的 | 加载的 Skills |
|---|---|---|
| `/course-init` | 初始化或接管项目 | `course-directory-structure`, `development-plan-governance` |
| `/course-audit` | 审计目录和文件位置 | `course-directory-structure` |
| `/course-outline` | 生成或重构教学大纲 | `course-outline-design` |
| `/course-content` | 编写或重写课程散文 | `course-content-authoring`, `markdown-course-writing` |
| `/course-lab` | 生成练习和演示 | `course-lab-design` |
| `/course-source-review` | 读取参考资料并提取材料 | `reference-document-review` |
| `/course-qa` | 运行 QA 审查周期 | `course-quality-assurance` |
| `/course-qc` | 制定 QC 发布决策 | `course-quality-control-reporting` |
| `/course-release-ready` | 检查文件是否可移至 `release/` | `course-quality-control-reporting` |
| `/course-methodize` | 从会话中提取可复用工作流 | `course-methodology-playbook` |

### Agents

Agents 提供基于角色的执行。每个 agent 具有特定的人设和严格的边界：

| Agent | 角色 | 关键约束 |
|---|---|---|
| **`curriculum-build`** | 主 Agent — 项目经理 + 负责人 | 可以委派给任何其他 agent |
| **`directory-curator`** | 管理文件树和命名约定 | 不编写课程内容 |
| **`outline-architect`** | 处理顶层结构和课时分配 | 不编写章节散文 |
| **`content-crafter`** | 编写和润色课程散文 | 不做结构性决策 |
| **`lab-designer`** | 构建练习和验证步骤 | 强制执行学员/讲师分离 |
| **`source-synthesizer`** | 提炼外部参考材料 | 不生成最终课程内容 |
| **`qa-auditor`** | 发现并记录问题 | **不直接编辑内容** |
| **`qc-gatekeeper`** | 批准或拒绝候选发布 | **不直接编辑内容** |

### 三层架构

course pack 运行在三个层次上：

```text
┌─────────────────────────────────────────┐
│  Commands (/course-init, /course-qa)    │  ← "如何快速触发工作流"
├─────────────────────────────────────────┤
│  Agents (qa-auditor, content-crafter)   │  ← "谁来做工作"
├─────────────────────────────────────────┤
│  Skills (course-quality-assurance, ...) │  ← "如何做工作"
└─────────────────────────────────────────┘
```

- **Skills** 定义了详细的程序和规则
- **Agents** 提供了带有访问特定 skills 权限的基于角色的人设
- **Commands** 是一次性加载正确的 agent + skill 组合的捷径入口点

---

## 质量门禁

pack 强制执行 7 个不同的质量门禁。每个门禁都有特定的标准，必须在进入下一个阶段之前满足这些标准。内容不应绕过这些门禁。

### 门禁 1: Project (项目) 门禁

在开始任何大纲工作之前：

- [ ] 在 `docs/00-project/project-brief.md` 中记录清晰的项目目标
- [ ] 目标受众和先修要求已定义
- [ ] 交付物边界明确（什么是范围内的，什么不是）
- [ ] 带有截止日期的里程碑计划
- [ ] 建立变更控制流程

### 门禁 2: Outline (大纲) 门禁

在内容创作开始之前：

- [ ] 具有逻辑顺序的模块划分
- [ ] 每个模块的学习目标（使用可衡量的动词）
- [ ] 每个模块的课时分配（讲座、实验、讨论）
- [ ] 模块之间的先修映射
- [ ] 每个模块的学员收益声明

### 门禁 3: Content (内容) 门禁

在开始实验设计之前：

- [ ] 章节结构稳定（无待处理的重大重构）
- [ ] 所有章节间的术语一致
- [ ] 章节之间没有相互矛盾
- [ ] 所有图、表和代码示例都存在并被引用
- [ ] 内容文件中没有残留的内部标记（"TODO"、"TBD"）

### 门禁 4: Lab (实验) 门禁

在开始材料生成之前：

- [ ] 每个实验都有明确的目标
- [ ] 指定了确切版本的环境要求
- [ ] 分步说明毫无歧义
- [ ] 在每个主要步骤之后都有验证标准
- [ ] 学员指南和讲师答案位于不同的文件中
- [ ] 为讲师记录了常见故障点

### 门禁 5: Materials (材料) 门禁

在开始 QA 之前：

- [ ] 学员包内绝对没有仅供讲师使用的信息
- [ ] 讲师包内包含所有练习的答案
- [ ] 讲师包包括时间估计和交付风险记录
- [ ] 所有链接、图片和交叉引用均可正确解析

### 门禁 6: QA 门禁

在开始 QC 之前：

- [ ] 记录带有严重性分类的发现问题列表
- [ ] 每个问题都有位置、描述和推荐修复方案
- [ ] 明确说明了 Critical 和 Major 问题的数量
- [ ] 没有遗留未分类的问题

### 门禁 7: QC 门禁

在发布之前：

- [ ] 每个 Critical 问题都已关闭（验证已修复）
- [ ] 每个 Major 问题要么已关闭，要么明确接受为已知风险
- [ ] 记录了正式发布决策（Full / Limited / Internal Trial / Blocked）
- [ ] 如果是有条件的发布，需明确说明条件
- [ ] 准备好发布说明并列出已知问题

---

## 接管现有项目

最常见的场景之一是继承了一个混乱的课程文件集合。该 pack 提供了一种结构化的方法：

### 第 1 步: 先审计，按兵不动

```text
/course-audit 扫描当前目录。将每个文件分类到它属于的层级
（project、outline、content、labs、learner、instructor、qa、qc、
reference、archive）。目前不要移动任何东西。
```

agent 生成分类表和建议的重组计划。

### 第 2 步: 审查计划

agent 的重组计划将：

- 将每个现有文件映射到其在标准结构中的正确目的地
- 标记可能属于多个位置的文件
- 识别似乎是重复项或过时版本的文件
- 建议应归档哪些文件

### 第 3 步: 经确认后执行

只有在你批准该计划后，agent 才会执行移动：

```text
计划看起来不错。执行重组，但不要碰“不确定”类别中的任何东西——把那些留给我来决定。
```

!!! warning "警告"
    当 agent 对文件的分类不确定时，它**不会猜测**。它会将文件标记为需由人工决策。这防止了因错误分类文件而造成的意外数据丢失。

---

## 处理大规模变更

pack 为何种变更被视为“大规模”并需要在实施前更新计划定义了特定触发器：

- 调整课程的整体目标受众或定位
- 更改模块顺序或合并/拆分模块
- 添加或删除整个实验练习
- 重构学员/讲师材料的边界
- 改变交付形式（例如，从 3 天的工作坊改为自定进度）

对于任何大规模变更：

1. 用变更理由更新 `docs/00-project/change-log.md`
2. 如果截止日期受影响，更新里程碑计划
3. 如果模块结构改变，更新教学大纲
4. **然后**继续修改内容

---

## 常见错误及如何避免

??? warning "警告"
    **错误:** 在没有项目简报或批准的大纲的情况下开始编写章节散文。
    
    **为什么会失败:** 没有商定的结构，你写出的内容将不符合任何共识愿景。在 QA 时，你会发现整个模块是多余的、顺序错误或面向了错误的受众水平。
    
    **修复:** 始终在阶段 2 (Content) 之前完成阶段 0 (Setup) 和阶段 1 (Outline)。

??? warning "警告"
    **错误:** 将讲师笔记、答案和学生讲义放在同一文档中。
    
    **为什么会失败:** 当你向学生分发材料时，不可避免地会忘记删除讲师笔记。学生在尝试练习之前就看到了答案。
    
    **修复:** 从第一天起就强制执行 `04-learner-pack/` 和 `05-instructor-pack/` 的拆分。切勿“为了方便”将它们合并。

??? warning "警告"
    **错误:** 收集了许多参考 PDF 和文档，但从未将它们提炼成实际课程材料。
    
    **为什么会失败:** 最终你的 `references/` 文件夹装满了“我们读过”但从未整合的材料。更糟的是，你直接将原始参考资料提取内容提升到内容目录中。
    
    **修复:** 每份参考文档必须经过 `reference-document-review` 生成结构化的提取笔记。然后，这些笔记输入到 `course-content-authoring` 中进行适当的课程整合。

??? warning "警告"
    **错误:** 运行 QA 以寻找问题，但从未运行 QC 做出发布决策。
    
    **为什么会失败:** 你有一个问题列表，但没有关于修复了哪些问题、接受了哪些问题以及该版本是否被批准发布的正式记录。这使项目处于永远的“快完成了”状态。
    
    **修复:** 每轮 QA 都必须紧随一轮产生正式发布决策的 QC。

??? warning "警告"
    **错误:** 在 `release/v1.0/module-01.md` 中发现一个错字并就地修复。
    
    **为什么会失败:** 你失去了可追溯性。发布目录应准确反映通过 QC 的内容。如果你直接编辑它，就不能确定该变更是否经过审查。
    
    **修复:** 在 `docs/02-content/` 中修复源文件，对修复运行 QA/QC，然后创建一个新的发布版本 (`release/v1.0.1/`)。

??? warning "警告"
    **错误:** 文件命名为 `kubernetes-draft-kyle-may15.md` 或 `final-FINAL-v2.md`。
    
    **为什么会失败:** 这些名字不携带任何结构信息。一周之内，没有人（包括你）能分辨哪个文件是最新的或它属于哪里。
    
    **修复:** 使用 pack 的命名约定：kebab-case、数字前缀、反映内容在课程结构中作用的描述性名称。

---

## 提示与最佳实践

??? tip "提示"
    不要要求 agent “写一个关于 Docker 的课程”。它将失败或产生浅显的结果。相反，引导它通过流水线：先大纲，再内容，然后实验。每个阶段都建立在前一个阶段的输出之上。

??? tip "提示"
    在继承文件时，始终优先使用 `/course-audit`。让 agent 在开始移动文件之前提出重组计划。这防止了意外的误分类。

??? tip "提示"
    设计实验时，立即强制拆分 `learner-guide.md` 和 `instructor-guide.md`。试图稍后将答案从说明中解耦既容易出错又耗时。

??? tip "提示"
    如果你有一份混乱的会议记录，不要把它转储到内容文件中。首先将它喂给 `source-synthesizer` agent 或 `reference-document-review` skill 以提取教学点。这会产生结构化笔记，处理起来容易得多。

??? tip "提示"
    `qa-auditor` agent 被明确指示**记录问题，而不是修复它们**。这确保在 `content-crafter` 进入修复文本之前，你保存了出错情况的纸质轨迹。绝不在一次传递中结合寻找和修复。

??? tip "提示"
    始终在发布目录中使用版本号或日期：`release/v1.0/`，`release/v1.1/`，`release/2026-06-pilot/`。绝不要直接在裸露的 `release/` 内部存放文件——那将无法追踪哪个版本被分发给了哪个受众。

??? tip "提示"
    如果你的请求跨越多个阶段（例如，“重构大纲然后重写模块 2-4”），请使用 orchestrator 而不是调用单个 skills。它能跨阶段保持上下文并确保遵守流水线顺序。

??? tip "提示"
    在完成主要的课程开发周期后，运行 `/course-methodize` 提取可复用的工作流、模板和经验教训。这构建了团队的机构知识，使得下一个课程的生产更快。

---

## Skill 参考

| Skill 名称 | 描述 | 触发词组 |
|---|---|---|
| `course-development-orchestrator` | 端到端驱动课程项目。 | "Course development", "manage curriculum", "drive the course project" |
| `course-directory-structure` | 创建并审计课程文件夹树。 | "Reorganize course files", "audit directory", "initialize project" |
| `development-plan-governance` | 管理里程碑、风险和计划。 | "Course development plan", "milestones", "change log" |
| `course-outline-design` | 创建教学大纲和模块图。 | "Course outline", "syllabus", "hour allocation", "module breakdown" |
| `course-content-authoring` | 将大纲扩展为章节散文。 | "Write chapter", "expand content", "draft module" |
| `markdown-course-writing` | 规范化格式和样式。 | "Format as markdown", "clean up course notes", "normalize terms" |
| `course-lab-design` | 设计练习和环境。 | "Create a lab", "hands-on exercise", "design a capstone" |
| `learner-materials` | 创建面向学生的阅读材料包。 | "Learner handouts", "student guide", "glossary", "worksheet" |
| `instructor-reference-materials` | 创建教学笔记和答案。 | "Teacher notes", "instructor guide", "answer key", "speaking points" |
| `course-quality-assurance` | 检查完整性并记录问题。 | "QA review", "check course quality", "find issues" |
| `course-quality-control-reporting` | 制定发布决策和报告。 | "QC report", "release readiness", "release decision" |
| `drawio-course-diagrams` | 生成用于 draw.io 的 XML 图表。 | "Course diagram", "draw.io architecture", "module map" |
| `reference-document-review` | 从输入材料中提取见解。 | "Read reference", "summarize notes", "extract from PDF" |
| `course-methodology-playbook` | 打包可复用的课程指南。 | "Extract methodology", "reusable workflow", "lessons learned" |
| `skill-reference-discovery` | 从外部资源中挖掘 skill 创意。 | "Find agent skills", "extract reusable patterns" |