# OpenCode课程开发Skills包

本包面向使用OpenCode进行课程开发的场景，采用符合OpenCode的 `.opencode/skills/<name>/SKILL.md` 目录结构。

## 技能列表

- course-development-orchestrator
- course-directory-structure
- markdown-course-writing
- drawio-course-diagrams
- reference-document-review
- development-plan-governance
- course-outline-design
- course-content-authoring
- course-lab-design
- learner-materials
- instructor-reference-materials
- course-quality-assurance
- course-quality-control-reporting
- course-methodology-playbook
- skill-reference-discovery

## 安装

建议把本包中的 `AGENTS.md` 放到项目根目录，再把 `.opencode/skills/` 复制到项目根目录。推荐形成：

```text
your-project/
├── AGENTS.md
└── .opencode/
    └── skills/
        ├── course-development-orchestrator/
        │   └── SKILL.md
        └── ...
```



## uv环境

本包现在默认采用 **uv管理的项目级Python虚拟环境** 来运行辅助脚本。项目根目录已附带 `pyproject.toml` 与 `.python-version`。

推荐先执行：

```bash
uv sync
```

之后统一使用 `uv run ...` 调用脚本，而不是直接调用系统 `python3`。详细说明见 `UV-USAGE.md`。

## AGENTS.md

本包现已附带一份项目级 `AGENTS.md` 模板，用于定义课程项目的全局协作规则、目录分层、质量门禁与发布要求。`SKILL.md` 负责专项能力，`AGENTS.md` 负责项目总规则。



## Commands/Agents

本包现已附带 `.opencode/commands/` 与 `.opencode/agents/`：

- `commands/`：提供高频工作流入口，如 `/course-init`、`/course-audit`、`/course-outline`、`/course-qa`
- `agents/`：提供角色化代理，如 `curriculum-build`、`outline-architect`、`qa-auditor`、`qc-gatekeeper`

推荐阅读：`COMMANDS-AND-AGENTS-GUIDE.md`

## 推荐目录

```text
docs/
  00-project/
  01-outline/
  02-content/
  03-labs/
  04-learner-pack/
  05-instructor-pack/
  06-qa/
  07-qc/
assets/
references/
release/
archive/
```

## 快速初始化

```bash
uv run .opencode/skills/course-directory-structure/scripts/bootstrap_course_tree.py --root . --mode full --with-placeholders
```

## 结构审计

```bash
uv run .opencode/skills/course-directory-structure/scripts/check_course_tree.py --root .
```

## QC报告生成

```bash
uv run .opencode/skills/course-quality-control-reporting/scripts/render_qc_report.py --input findings.json --output docs/07-qc/qc-report.md
```


## 本次增强

新增了以下内容：
- `COURSE-PROJECT-STRUCTURE-STANDARD.md`：课程项目标准目录与命名规范
- `HISTORY-TO-SKILLS-ROADMAP.md`：从历史讨论继续沉淀skills的路线图
-强化 `course-directory-structure`：
  -支持“初始化/审计/整理建议”三段式使用方式
  -增补目录整理检查单与结构策略说明
- `.opencode/commands/`：课程开发高频工作流命令入口
- `.opencode/agents/`：课程开发角色化代理定义
- `COMMANDS-AND-AGENTS-GUIDE.md`：commands与agents的关系、职责与推荐工作流

## 建议你下一步怎么用

1. 先把这套包复制到一个真实课程项目根目录
2. 运行目录初始化或审计脚本
3. 把你现有的课程文档放入 `docs/`、`references/`、`assets/`
4. 先用 `course-development-orchestrator` 驱动，再让专项skill接管
5. 每完成一轮高价值课程工作，就把方法、模板和gotchas反向沉淀回skills包
