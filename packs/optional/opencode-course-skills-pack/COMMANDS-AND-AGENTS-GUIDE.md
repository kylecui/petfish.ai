# OpenCode课程开发Commands/Agents使用指南

本文件用于说明本包新增的 `.opencode/commands/` 与 `.opencode/agents/` 的职责、关系与推荐用法。

## 设计思路

本包现在包含三层：

- `AGENTS.md`：项目级总规则
- `.opencode/skills/`：专项能力与可复用流程
- `.opencode/commands/` 与 `.opencode/agents/`：高频入口与角色分工

建议理解为：

- **skills** 解决“怎么做”
- **agents** 解决“由谁做”
- **commands** 解决“如何快速触发一类工作流”

---

## 目录结构

```text
.opencode/
├── agents/
│   ├── content-crafter.md
│   ├── curriculum-build.md
│   ├── directory-curator.md
│   ├── lab-designer.md
│   ├── outline-architect.md
│   ├── qa-auditor.md
│   ├── qc-gatekeeper.md
│   └── source-synthesizer.md
├── commands/
│   ├── course-audit.md
│   ├── course-content.md
│   ├── course-init.md
│   ├── course-lab.md
│   ├── course-methodize.md
│   ├── course-outline.md
│   ├── course-qa.md
│   ├── course-qc.md
│   ├── course-release-ready.md
│   └── course-source-review.md
└── skills/
    └── ...
```

---

## Agents说明

### curriculum-build
主代理。适合在你想让OpenCode作为“课程项目经理 + 主执行者”直接工作时使用。

### directory-curator
专管目录初始化、结构审计、归位与命名规范。

### outline-architect
专管课程总纲、模块设计、课时分配与章节骨架。

### content-crafter
专管课程正文编写与重写。

### lab-designer
专管实验、演示、作业与验收标准。

### source-synthesizer
专管参考资料阅读、归纳、适配与可用素材提炼。

### qa-auditor
只做QA审阅，不直接改文件。

### qc-gatekeeper
只做QC门禁与发布判断，不直接改文件。

---

## Commands说明

### /course-init
初始化或接管课程项目。

### /course-audit
审计当前目录、命名、资料归属和整理优先级。

### /course-outline
生成或重构课程提纲。

### /course-content
编写或重写课程正文。

### /course-lab
生成或改进实验、演示、作业。

### /course-source-review
阅读参考资料并提炼成课程可用结论。

### /course-qa
执行QA审阅。

### /course-qc
执行QC门禁判断。

### /course-release-ready
检查是否可以形成release版本。

### /course-methodize
把本轮经验反向沉淀回方法论与skills。

---

## 推荐工作流

### 新项目

1. `/course-init <课程主题与目标>`
2. `/course-outline <对象、目标、课时>`
3. `/course-content <模块或章节需求>`
4. `/course-lab <实验需求>`
5. `/course-qa <审阅范围>`
6. `/course-qc <发布候选范围>`
7. `/course-release-ready <版本说明>`

### 接手旧项目

1. `/course-audit <现状与问题>`
2. `/course-source-review <参考资料范围>`
3. `/course-outline <提纲重构需求>`
4. `/course-content <正文整理范围>`
5. `/course-qa <当前轮次>`
6. `/course-qc <发布判断>`

### 方法沉淀

完成一轮高价值工作后，执行：

```text
/course-methodize 本轮做了什么、哪些步骤反复出现、哪些模板值得固化
```

---

## 与AGENTS.md、skills的关系

- `AGENTS.md` 规定项目总规则
- `commands` 提供快捷入口
- `agents` 提供角色分工
- `skills` 提供可复用方法与模板

不要把这三层混成一层。更推荐的做法是：

-全局规则写进 `AGENTS.md`
-专项流程写进 `skills`
-高频工作流写成 `commands`
-专业角色拆成 `agents`


## uv运行约定

本包中的Python辅助脚本默认通过项目根目录的 `uv` 环境运行。涉及脚本的命令示例请统一写成 `uv run path/to/script.py ...`，不要再把系统 `python3` 作为默认入口。
