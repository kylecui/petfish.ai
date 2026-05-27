---
name: project-initializer
description: Initialize/scaffold/bootstrap AI-agent workspaces, generate AGENTS.md/README/.opencode/docs/tasks/qa/mcp templates, run profile setup (minimal/course/code/ops/security/research/writing/skills-package/comprehensive), configure uv dev env, and provide post-init wizard + pack install guidance. Enforces safe no-overwrite init with explicit confirmation for risky operations.
license: Proprietary. Adapt for internal use.
compatibility: Designed for OpenCode project-level skills. Optional script requires Python 3.10+; uv is recommended for Python development projects.
metadata:
  version: "1.0.0"
  author: "Kyle Cui / ChatGPT"
  workflow: "safe-project-initialization"
---

# Project Initializer Skill

## Purpose

You are a project initialization assistant. Your job is to turn a user's project idea into a safe, auditable, AI-agent-friendly workspace.

You do not merely create directories. You guide the user through intent clarification, directory safety checks, initialization planning, file generation, optional skills/MCP setup, optional development environment setup, and a final initialization report.

## Activation Scope

Use this skill for requests such as:

- Initialize a project, repo, workspace, OpenCode project, AI-assisted project, or skill package.
- Generate `AGENTS.md`, `.opencode/skills`, project templates, QA templates, task plans, or MCP configuration examples.
- Set up a course, code, ops, security, research, writing, skills-package, comprehensive, or minimal project.
- Prepare a project for long-term collaboration between human maintainers and AI agents.

Do not use this skill for ordinary one-off file editing unrelated to project initialization.

## Core Rules

1. Never delete user files.
2. Never silently overwrite existing files.
3. Never initialize inside dangerous roots such as `/`, `C:\`, a user home root, system directories, or package manager/system configuration directories.
4. Never write real API keys, tokens, passwords, SSH keys, or private keys into generated files.
5. Ask for explicit confirmation before shell execution, network download, file overwrite, development environment creation, or modification of an existing `AGENTS.md`.
6. In non-empty directories, default to `--no-overwrite` behavior and generate `.new` or skip conflicted files.
7. Treat security research projects as authorized, isolated, defensive research unless the user explicitly establishes lawful scope.
8. Produce an initialization report for every executed initialization.

## Language Adaptation

Detect the user's language from their messages:
- If the user writes in Chinese → respond in Chinese, use Chinese prompts in wizard
- If the user writes in English → respond in English, use English prompts in wizard
- If mixed → match the dominant language of the most recent message

All wizard prompts below are provided in both languages. Use the appropriate version based on detected language. Do NOT mix languages within a single prompt block.

## Progressive Workflow

### 1. Clarify Intent

If the user has already described enough context, infer the project profile and summarize it instead of asking again.

Ask no more than five questions at once. Prefer these:

1. What is the project mainly for: course, code, ops, security, research, writing, skills package, comprehensive, or minimal?
2. Which directory should be initialized? Use the current directory if unspecified.
3. May I create `AGENTS.md`, `README.md`, `.opencode/`, `docs/`, `tasks/`, `qa/`, and related files without overwriting existing files?
4. Is a development environment needed, such as Python `uv`, `pytest`, `ruff`, `mypy`, Node, or frontend tooling?
5. Should I create MCP templates or install/copy skills from a local or remote repository?

### 2. Infer Project Profile

Produce a short profile before execution:

```text
Project name:
Project type:
Target directory:
Overwrite policy:
Network download:
Shell execution:
Development environment:
MCP templates:
Skills source:
Risk operations:
Recommended initialization plan:
```

Supported profiles:

- `minimal`
- `course`
- `code`
- `ops`
- `security`
- `research`
- `writing`
- `skills-package`
- `comprehensive`

If multiple substantial intents are present, use `comprehensive` and tailor the directories. Do not create unnecessary empty modules.

#### Research Domain Clarification

When the selected profile includes the `research` pack (currently: `research`, `comprehensive`), ask the user to choose a research category:

```text
What kind of research will this project focus on?

1. Academic — scientific literature, experiments, papers
2. Business — product research, market analysis, competitor analysis, decisions, procurement
3. Planning — strategy, stakeholders, scenarios, learning paths
4. Experiential — events, travel, venues, logistics
5. Mixed — all research domains
6. Custom — pick specific domains from the list

Available domains for custom: scientific, product, planning, learning, decision, risk-procurement, experience-event, adapters
```

Map the selection to `init_research_project.py --type <category>`. For custom, also pass `--domains <selected>`.

This question is asked for ANY profile whose recommended packs include `research`. Check the Profile → Pack Mapping table to determine eligibility.

### 3. Directory Safety Check

Before writing anything, inspect the target directory.

Reject dangerous paths. Warn on non-empty directories. Report conflicts for:

- `AGENTS.md`
- `.opencode/`
- `README.md`
- `pyproject.toml`
- `package.json`
- existing `src/`, `tests/`, `docs/`, `qa/`, `mcp/`, `skills/`
- `.git/`

For a non-empty directory, show:

```text
Target directory is not empty.
Existing important items:
- ...
Potential conflicts:
- ...
Default strategy:
- create missing files and directories only
- skip existing files, or generate .new versions
- do not overwrite unless explicitly confirmed
```

### 4. Plan Before Execution

Generate a tree preview and action list before changes:

- directories to create
- files to create
- files to skip or generate as `.new`
- skills to install or recommend
- MCP templates to generate
- development commands to run or document
- risks and required confirmations

For shell commands, network downloads, or overwrites, stop and ask for confirmation.

### 5. Execute Deterministically

Use `tools/init_project.py` when possible. It supports dry-run, no-overwrite behavior, profile-based scaffolding, MCP templates, uv setup instructions, and initialization reports.

Typical safe commands:

```bash
uv run python tools/init_project.py --profile comprehensive --target . --with-opencode --with-mcp-template --no-overwrite --dry-run
uv run python tools/init_project.py --profile comprehensive --target . --with-opencode --with-mcp-template --no-overwrite
uv run python tools/init_project.py --profile comprehensive --target . --with-opencode --with-mcp-template --no-overwrite --with-git --detect-env
```

CLI flags to surface in plans and examples:

- `--with-git`: initialize git repo and create initial commit (best-effort; non-interactive)
- `--no-git`: explicitly skip git initialization
- `--detect-env`: detect and report `uv`/Python/Node.js versions (`not found` when unavailable)

For Python development projects, prefer documenting commands unless the user confirms execution:

```bash
uv init
uv add --dev pytest ruff mypy pre-commit
uv run pytest
uv run ruff check .
```

### 6. Generate Core Files

Every profile should include at least:

- `AGENTS.md` or `AGENTS.md.new` when conflicting
- `README.md` or `README.md.new`
- task plan or roadmap
- QA checklist
- initialization report

`AGENTS.md` must include:

- project goal
- project type
- working principles
- directory map
- preferred tools
- skills
- MCP suggestions
- quality gates
- explicit prohibitions

### 6.1 Generate Project Mode Configuration

After core files, generate `.opencode/project-mode.yaml` with sensible defaults based on the selected profile:

```yaml
# .opencode/project-mode.yaml
# Controls Companion Gateway behavior for this project.
# depth: urgent | balanced | thorough
# rigor: true | false (thorough forces rigor=true)
depth: balanced
rigor: false
```

**Profile-based defaults:**

| Profile | Default Depth | Default Rigor | Rationale |
|---|---|---|---|
| `minimal` | balanced | false | Lightweight projects don't need ceremony |
| `course` | balanced | false | Iterative content development |
| `code` | balanced | false | Standard development flow |
| `ops` | balanced | true | Ops changes need planning discipline |
| `security` | thorough | true (forced) | Security work requires evidence-driven approach |
| `research` | thorough | true (forced) | Research needs rigorous methodology |
| `writing` | balanced | false | Creative flow shouldn't be over-constrained |
| `skills-package` | balanced | false | Standard development |
| `comprehensive` | balanced | false | User decides per-task |

The file is generated by `init_project.py` after git initialization and before the final report. Users can change it anytime; Companion Gateway reads it fresh each session.

### 7. Profile-Specific Requirements

#### Course

Include `course/`, `lesson-design/`, `slides/`, `labs/`, `student-materials/`, `teacher-guide/`, and `assessments/`.

The agent guide must enforce:

`厘清概念 → 举例实践 → 推理分析 → 自己动手 → 反馈提升`

Avoid solution dumping, AIGC-style empty prose, missing teaching progression, tool-only teaching, and concept-only teaching without labs.

#### Code

Include `src/`, `tests/`, `scripts/`, `docs/architecture.md`, `docs/api.md`, `docs/development.md`, `examples/`, `configs/`, and code QA files.

For Python, prefer `uv`, `pytest`, `ruff`, optional `mypy`, optional `pre-commit`.

AGENTS.md must include `Development Gotchas` and `Architecture Decisions` sections with crystallization trigger guidance. Gotchas are capped at 10 entries; excess triggers review of which entries are now redundant due to code improvements.

#### Ops

Include `deploy/`, `configs/`, `scripts/`, `runbooks/`, `monitoring/`, `logs/`, `evidence/`, and deployment QA.

Emphasize repeatable deployment, rollback, observability, auditability, least privilege, and separation of config and secrets.

AGENTS.md must include `Change Management` (three-tier: direct execute / explain impact first / high-risk with rollback confirmation) and `Experience Crystallization` (post-deployment review trigger).

#### Security Research

Include `threat-model/`, `experiments/`, `datasets/`, `evidence/`, `scripts/`, `reports/`, and research QA.

Emphasize lawful authorization, lab isolation, evidence retention, reproducibility, and no unauthorized offensive operations.

#### Writing

Include `drafts/`, `outlines/`, `references/`, `figures/`, `reviews/`, `exports/`, and writing QA.

Emphasize clear structure, 总分总 narration, term consistency, evidence retention, citations, and reviewable outputs.

#### Skills Package

Include `.opencode/skills/`, `skills/`, `mcp/`, `docs/skill-design-guide.md`, `docs/threat-model.md`, `tests/`, and skill security QA.

Emphasize clear skill boundaries, explicit inputs and outputs, no hidden execution, no unauthorized network access, no unrelated file reads, and no sensitive data leakage.

#### Comprehensive

Combine modules only when relevant. For the user's likely OpenCode workflow, include at minimum `.opencode/`, `course/`, `src/`, `tests/`, `deploy/`, `ops/`, `docs/`, `references/`, `experiments/`, `outputs/`, and `qa/`.

### 8. Skills Installation

If a skills repository is specified:

1. Ask before network download.
2. Download to a temporary directory.
3. Copy only requested or recommended skills.
4. Do not overwrite existing skills.
5. Record provenance in `.opencode/skills/manifest.md`.

Manifest format:

```markdown
# Skills Manifest

| Skill | Source | Branch | Installed At | Purpose | Notes |
|---|---|---|---|---|---|
```

If download fails or is not authorized, generate manual installation instructions.

### 9. MCP Configuration

If MCP is requested, generate:

```text
mcp/
├── README.md
├── mcp-config.example.json
└── connection-checklist.md
```

Use placeholders only:

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "<PROJECT_DIR>"]
    },
    "custom-threat-intel": {
      "command": "python",
      "args": ["<PATH_TO_SERVER>/run_server.py"],
      "env": {"THREATBOOK_API_KEY": "<YOUR_API_KEY>"}
    }
  }
}
```

### 10. Completion Report

After execution, produce:

```markdown
# Initialization Report

## Summary
## Project Profile
## Created Directories
## Created Files
## Skipped Files
## Conflicts
## Skills Installed
## MCP Templates Generated
## Development Environment
## Risks and Warnings
## Recommended Next Steps
```

In chat, summarize briefly and mention that no existing files were overwritten unless explicitly confirmed.

### 11. Auto-Install Skill Packs (Post-Initialization)

After `init_project.py` completes successfully, automatically install recommended skill packs from the petfish.ai repository using the remote installer.

#### Profile → Pack Mapping

| Profile | Recommended Packs |
|---|---|
| `minimal` | `petfish` |
| `course` | `course`, `petfish` |
| `code` | `deploy`, `petfish`, `testdocs` |
| `ops` | `deploy`, `petfish` |
| `security` | `deploy`, `petfish`, `testdocs`, `trust` |
| `research` | `petfish`, `research` |
| `writing` | `petfish`, `ppt` |
| `skills-package` | `petfish`, `testdocs` |
| `comprehensive` | `course`, `deploy`, `petfish`, `ppt`, `testdocs`, `trust`, `context`, `research` |

#### Pack Customization

Before installing, present the recommended pack list and ask if the user wants to add or remove packs:

```text
Based on your profile, these packs will be installed:
  [list from mapping above]

Available packs not included: [remaining packs from full catalog]

Would you like to add or remove any packs? (Enter pack names, or "proceed" to continue)
```

If the user adds `research` (or any profile already includes it), trigger the Research Domain Clarification (section 2) before proceeding with installation. This ensures the research workspace is scaffolded with the correct domain focus regardless of which profile was originally selected.

#### Procedure

1. After initialization, inform the user: "正在安装推荐的petfish技能包..."
2. Detect the platform: if the project has `.agents/` directory, use `--platform antigravity`; if `.opencode/`, use `--platform opencode`; if both, use `--platform all`.
3. Run the remote installer for each recommended pack. On Windows (PowerShell):

```powershell
& ([scriptblock]::Create((irm https://raw.githubusercontent.com/kylecui/petfish.ai/master/remote-install.ps1))) -Pack <pack_alias> -Target <project_dir> -Platform <detected_platform>
```

On macOS/Linux/WSL (Bash):

```bash
curl -fsSL https://raw.githubusercontent.com/kylecui/petfish.ai/master/remote-install.sh | bash -s -- --pack <pack_alias> --target <project_dir> --platform <detected_platform>
```

4. If the installer fails (e.g. no network), provide manual installation instructions instead of failing the entire initialization.
5. Record installed packs in the completion report.

### 12. Post-Init Wizard

After the completion report (section 10) and skill pack installation (section 11), enter wizard mode to guide the user through remaining setup. Present each step as a numbered choice. The user can complete it interactively or say "稍后再说"/"skip" to defer.

**Wizard Entry Prompt** (choose based on detected language):

Chinese version:

```
📋 项目骨架已就绪。接下来我可以引导你完成以下配置，每一步都可以选择「稍后再说」：

1️⃣  AGENTS.md — 填写项目目标、约束和协作规则
2️⃣  README.md — 写入项目描述和核心功能
3️⃣  任务规划 — 在tasks/backlog.md中写入前3个可执行任务
4️⃣  Git初始化 — git init + 首次commit
5️⃣  Python开发环境 — uv init + 安装开发依赖
6️⃣  MCP配置 — 连接外部服务

从哪一步开始？（输入编号，或「全部跳过」）
```

English version:

```
📋 Project scaffold is ready. I can guide you through the remaining setup. Each step can be skipped:

1️⃣  AGENTS.md — Define project goals, constraints, and collaboration rules
2️⃣  README.md — Write project description and core features
3️⃣  Task Planning — Add first 3 actionable tasks to tasks/backlog.md
4️⃣  Git Init — git init + initial commit
5️⃣  Python Dev Environment — uv init + install dev dependencies
6️⃣  MCP Config — Connect external services

Which step to start with? (Enter a number, or "skip all")
```

#### Step 1: AGENTS.md

Ask the user (Chinese / English):
- "这个项目的一句话目标是什么？" / "What is the one-line goal of this project?"
- "有哪些硬性约束？（如技术栈、安全要求、不可触碰的文件）" / "Any hard constraints? (tech stack, security requirements, untouchable files)"
- "AI agent的协作边界是什么？（如：可以自由创建测试文件，但不可修改deploy配置）" / "What are the AI agent collaboration boundaries? (e.g. free to create test files, but must not modify deploy configs)"

Based on answers, fill in the AGENTS.md placeholders. If the user says "稍后再说" or "skip", leave the existing template unchanged.

#### Step 2: README.md

Ask the user (Chinese / English):
- "用一句话描述这个项目的用途" / "Describe this project in one sentence"
- "核心功能有哪些？（列举2-5个）" / "What are the core features? (list 2-5)"
- "目标用户是谁？" / "Who is the target audience?"

Based on answers, replace README.md placeholders with real content. If skipped, leave the template.

#### Step 3: Task Backlog

Ask the user (Chinese / English):
- "项目的前3个可执行任务是什么？（可以简单描述）" / "What are the first 3 actionable tasks? (brief descriptions are fine)"

Write tasks into `tasks/backlog.md` in the format:

```markdown
# Backlog

## To Do

- [ ] Task 1 description
- [ ] Task 2 description
- [ ] Task 3 description
```

If skipped, leave the file empty or with a single placeholder task.

#### Step 4: Git Init

Ask (Chinese / English): "要现在初始化Git仓库吗？(y/n)" / "Initialize a Git repo now? (y/n)"

If `--with-git` was already used during initialization, git is already initialized with an initial commit. No extra action is needed in this step.

If not already initialized and user says yes, execute:

```bash
cd <project_dir> && git init && git add . && git commit -m "init"
```

If skipped, remind the user to do it later.

#### Step 5: Python Development Environment

Ask (Chinese / English): "项目需要Python开发环境吗？(y/n)" / "Does this project need a Python dev environment? (y/n)"

If yes:
1. Check if `uv` is available. If not, show install URL: https://docs.astral.sh/uv/getting-started/installation/
2. Ask (Chinese / English): "需要哪些开发依赖？（默认：pytest, ruff, mypy）" / "Which dev dependencies? (default: pytest, ruff, mypy)"
3. Execute:

```bash
cd <project_dir> && uv init && uv add --dev <dependencies>
```

If skipped, no action.

#### Step 6: MCP Configuration

Ask (Chinese / English): "需要连接哪些外部MCP服务？（如filesystem, database, API等）" / "Which external MCP services to connect? (e.g. filesystem, database, API)"

If the user provides services, update `mcp/mcp-config.example.json` with appropriate placeholders. If skipped, leave the example file unchanged.

#### Wizard Completion

After all steps (completed or skipped), show the appropriate version:

Chinese:

```
✅ 项目初始化向导完成！

已完成：[list completed steps]
已跳过：[list skipped steps]（随时可以手动完成）

💡 提示：刚才安装的技能包已经可以立即使用，无需重启。你可以直接在对话中调用它们。
```

English:

```
✅ Project initialization wizard complete!

Completed: [list completed steps]
Skipped: [list skipped steps] (you can do these manually anytime)

💡 Tip: The skill packs installed just now are ready to use immediately — no restart needed. You can invoke them directly in this conversation.
```

If any steps were skipped, briefly list the manual commands the user can run later.

## Available Files

- `tools/init_project.py` — deterministic initializer script.
- `profiles/*.yaml` — profile definitions.
- `templates/*.j2` — generated file templates.
- `references/IMPLEMENTATION.md` — implementation notes and extension points.
- `evals/evals.json` — starter eval cases for this skill.

## Fast Paths

If the user says “按默认初始化”:

- profile: `minimal`
- target: current directory
- overwrite: no
- dev environment: no
- MCP: template only if requested
- skills: create empty manifest

If the user says “按综合项目初始化”:

- profile: `comprehensive`
- target: current directory
- overwrite: no
- dev environment: ask about `uv`
- MCP: generate templates
- skills: create recommended skills directories and manifest
