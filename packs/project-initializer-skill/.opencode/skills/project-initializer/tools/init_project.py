#!/usr/bin/env python3
"""Safe project initializer for OpenCode/agent-friendly projects.

This script is intentionally non-interactive. Agents should perform user-facing
confirmation before invoking it with destructive options. By default it does not
overwrite existing files.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

PROFILES: Dict[str, Dict[str, object]] = {
    "minimal": {
        "dirs": [
            ".opencode/skills",
            ".opencode/agents",
            ".opencode/templates",
            "docs/decisions",
            "tasks",
            "references",
            "outputs",
            "qa",
        ],
        "files": [
            "AGENTS.md",
            "README.md",
            "docs/overview.md",
            "tasks/backlog.md",
            "tasks/roadmap.md",
            "qa/checklist.md",
            "qa/review-report-template.md",
            ".opencode/skills/manifest.md",
        ],
        "skills": ["project-initializer", "markdown-writer", "qa-reviewer"],
    },
    "course": {
        "dirs": [
            ".opencode/skills",
            ".opencode/agents",
            ".opencode/templates",
            "course/lesson-design",
            "course/slides",
            "course/labs",
            "course/student-materials",
            "course/teacher-guide",
            "course/assessments",
            "references",
            "figures",
            "outputs",
            "qa",
        ],
        "files": [
            "AGENTS.md",
            "README.md",
            "course/syllabus.md",
            "course/teaching-plan.md",
            "qa/course-quality-checklist.md",
            "qa/course-review-report.md",
            ".opencode/skills/manifest.md",
        ],
        "skills": [
            "markdown-writer",
            "course-designer",
            "lab-designer",
            "teacher-guide-writer",
            "qa-reviewer",
            "drawio-writer",
        ],
    },
    "code": {
        "dirs": [
            ".opencode/skills",
            ".opencode/agents",
            ".opencode/templates",
            "src",
            "tests",
            "scripts",
            "docs",
            "examples",
            "configs",
            "outputs",
            "qa",
        ],
        "files": [
            "AGENTS.md",
            "README.md",
            "pyproject.toml",
            "docs/architecture.md",
            "docs/api.md",
            "docs/development.md",
            "qa/code-review-checklist.md",
            "qa/test-plan.md",
            ".opencode/skills/manifest.md",
        ],
        "skills": [
            "repo-reader",
            "code-reviewer",
            "test-case-generator",
            "dev-env-manager",
            "documentation-writer",
            "qa-reviewer",
        ],
    },
    "ops": {
        "dirs": [
            ".opencode/skills",
            ".opencode/agents",
            ".opencode/templates",
            "deploy",
            "configs",
            "scripts",
            "issues",
            "runbooks",
            "monitoring",
            "logs",
            "evidence",
            "qa",
        ],
        "files": [
            "AGENTS.md",
            "README.md",
            "deploy/deployment-map.md",
            "runbooks/startup.md",
            "runbooks/shutdown.md",
            "runbooks/rollback.md",
            "runbooks/incident-response.md",
            "qa/deployment-checklist.md",
            "qa/operation-review.md",
            ".opencode/skills/manifest.md",
        ],
        "skills": [
            "deployment-operator",
            "runbook-writer",
            "config-reviewer",
            "incident-response-writer",
            "qa-reviewer",
        ],
    },
    "security": {
        "dirs": [
            ".opencode/skills",
            ".opencode/agents",
            ".opencode/templates",
            "threat-model",
            "experiments",
            "datasets",
            "evidence",
            "scripts",
            "reports",
            "references",
            "qa",
        ],
        "files": [
            "AGENTS.md",
            "README.md",
            "threat-model/overview.md",
            "experiments/experiment-plan.md",
            "qa/research-checklist.md",
            "qa/evidence-review.md",
            ".opencode/skills/manifest.md",
        ],
        "skills": [
            "threat-modeler",
            "evidence-organizer",
            "experiment-designer",
            "report-writer",
            "qa-reviewer",
        ],
    },
    "writing": {
        "dirs": [
            ".opencode/skills",
            ".opencode/agents",
            ".opencode/templates",
            "drafts",
            "outlines",
            "references",
            "figures",
            "reviews",
            "exports",
            "qa",
        ],
        "files": [
            "AGENTS.md",
            "README.md",
            "outlines/outline.md",
            "drafts/main.md",
            "qa/writing-quality-checklist.md",
            "qa/review-report.md",
            ".opencode/skills/manifest.md",
        ],
        "skills": [
            "markdown-writer",
            "strategic-writer",
            "citation-manager",
            "drawio-writer",
            "qa-reviewer",
        ],
    },
    "skills-package": {
        "dirs": [
            ".opencode/skills",
            ".opencode/agents",
            ".opencode/templates",
            "skills/project-initializer",
            "skills/markdown-writer",
            "skills/repo-reader",
            "skills/qa-reviewer",
            "skills/deployment-operator",
            "mcp",
            "docs",
            "tests",
            "qa",
        ],
        "files": [
            "AGENTS.md",
            "README.md",
            "mcp/README.md",
            "mcp/mcp-config.example.json",
            "mcp/connection-checklist.md",
            "docs/skill-design-guide.md",
            "docs/threat-model.md",
            "qa/skill-review-checklist.md",
            "qa/skill-security-checklist.md",
            ".opencode/skills/manifest.md",
        ],
        "skills": [
            "skill-writer",
            "skill-reviewer",
            "skill-threat-modeler",
            "mcp-config-writer",
            "qa-reviewer",
        ],
    },
    "research": {
        "dirs": [
            ".opencode/skills",
            ".opencode/agents",
            ".opencode/templates",
            "research",
            "research/briefs",
            "research/evidence",
            "research/outputs",
            "references",
            "qa",
        ],
        "files": [
            "AGENTS.md",
            "README.md",
            "research/briefs/README.md",
            "research/evidence/README.md",
            "research/outputs/README.md",
            "qa/research-checklist.md",
            ".opencode/skills/manifest.md",
        ],
        "skills": [
            "research-brief-framer",
            "evidence-collector",
            "report-writer",
            "qa-reviewer",
        ],
    },
    "comprehensive": {
        "dirs": [
            ".opencode/skills",
            ".opencode/agents",
            ".opencode/templates",
            "product",
            "course",
            "src",
            "tests",
            "deploy",
            "ops",
            "docs",
            "references",
            "experiments",
            "outputs",
            "qa",
        ],
        "files": [
            "AGENTS.md",
            "README.md",
            "docs/overview.md",
            "tasks/backlog.md",
            "tasks/roadmap.md",
            "qa/checklist.md",
            "qa/review-report-template.md",
            ".opencode/skills/manifest.md",
        ],
        "skills": [
            "project-initializer",
            "markdown-writer",
            "repo-reader",
            "course-designer",
            "code-reviewer",
            "deployment-operator",
            "qa-reviewer",
            "drawio-writer",
        ],
    },
}

DANGEROUS_NAMES = {
    "/",
    "",
    "C:\\",
    "C:/",
    "Windows",
    "System32",
    "Program Files",
    "Program Files (x86)",
    "etc",
    "usr",
    "bin",
    "sbin",
    "var",
    "opt",
}


def now() -> str:
    return dt.datetime.now(dt.timezone.utc).astimezone().isoformat(timespec="seconds")


def slugify(name: str) -> str:
    s = re.sub(r"[^A-Za-z0-9_]+", "_", name).strip("_").lower()
    return s or "project"


def is_dangerous(path: Path) -> bool:
    p = path.resolve()
    home = Path.home().resolve()
    if str(p) in {"/", str(home)}:
        return True
    if p.anchor and str(p) == p.anchor:
        return True
    if p.name in DANGEROUS_NAMES:
        return True
    parts = {part.lower() for part in p.parts}
    return "windows" in parts and "system32" in parts


def _render_ops_agents_md(title: str, directory_map: str, skills: List[str]) -> str:
    """Render a complete ops/deployment-specific AGENTS.md."""
    skills_list = chr(10).join(f"- {s}" for s in skills)
    return f"""# {title} — 运维项目规范

## 1. 项目概况

### 服务器清单

| 主机名/用途 | IP | OS | 规格 | SSH用户 |
|------------|----|----|------|---------|
| <!-- 填写 --> | | | | |

### 部署的服务

| 域名 | 项目/仓库 | 部署路径 | 技术栈 | 端口 |
|------|----------|---------|--------|------|
| <!-- 填写 --> | | | | |

### 端口分配概览

<!-- 记录已分配端口，避免冲突 -->

### SSL证书状态

| 域名 | 证书路径 | 到期时间 | 备注 |
|------|---------|---------|------|
| <!-- 填写 --> | | | |

## 2. 工作原则

### 2.1 优先级

1. 服务可用性优先——任何操作不可导致在线服务不可用
2. 先读文档后操作——先查阅runbooks和现有记录
3. 先分析后执行——先识别repo与主机状态，再制定方案
4. 最小变更——一次只改一件事，验证通过后再做下一步
5. 回滚先于部署——部署前必须确认回滚路径可用
6. 验证闭环——每次变更必须有验证步骤
7. 经验沉淀——每轮部署/运维后回顾，评估是否补充本文件

### 2.2 安全约束

- 密钥、token、密码不写入仓库文件
- 破坏性命令（rm -rf、drop、down -v）执行前必须确认范围和回滚路径
- 配置变更前先备份当前配置

### 2.3 Private Repo访问

Token注入和清除必须在同一命令链完成，不可分两次执行。详见 deployment-executor 的 `references/private-repo-access.md`。

### 2.4 通用约束

- 不操作其它仓库的内容（即使有权限），只能通过issues反馈
- 网络出现问题或可能是网络问题导致的中断（SSH无法连接、apt install失败、docker pull超时），至少重试两次再行调整
- 不要将安装到本地的skill/command/agent文件纳入版本控制——它们是安装器从skill源（packs）生成的派生产物，应在`.gitignore`中排除各平台的skill目录

## 3. 目录结构

```text
{directory_map}```

| 目录 | 用途 |
|------|------|
| deploy/ | 部署映射表、docker-compose文件、部署脚本 |
| configs/ | 按仓库分子目录的配置文件 |
| scripts/ | 运维脚本 |
| issues/ | 向上游仓库提交的issue记录和补丁跟踪 |
| runbooks/ | 操作手册（启动、停止、回滚、故障响应） |
| monitoring/ | 监控配置和告警规则 |
| logs/ | 日志样本和分析记录 |
| evidence/ | 部署验证截图、输出记录 |
| qa/ | 部署检查清单和运维审查 |

## 4. 技能路由

默认使用以下技能链路：

```
repo-runtime-discovery → target-host-readiness → deployment-executor
→ deployment-verifier → service-operations → incident-rollback
```

宽泛任务（"帮我把这个仓库部署起来"）优先启用 `repo-service-lifecycle` 作为总控。

推荐技能：

{skills_list}

## 5. 变更管理

### 5.1 可直接执行
- 查看日志、检查服务状态
- restart已有服务
- git pull + rebuild（无本地补丁冲突时）

### 5.2 需先说明影响
- 修改端口映射
- 修改.env或环境变量
- 修改Nginx配置
- 数据库migration

### 5.3 高风险操作（必须确认回滚路径）
- docker compose down -v（会丢数据卷）
- 数据库重初始化
- SSL证书变更
- 端口重分配
- 删除部署目录

## 6. 部署特殊注意事项

### 6.1 镜像源问题
- 海外服务器不使用中国镜像源
- 国内服务器按需配置镜像加速

### 6.2 端口冲突检查
- 部署前检查目标端口是否被占用：`ss -tlnp | grep <port>`
- 多服务共存时，维护端口分配表（见项目概况）

### 6.3 本地补丁管理
- 本地补丁必须记录在README中，分"Upstreamed Fixes"和"Deployment-Specific Patches"
- 使用python3修改YAML，不用sed
- 详见 deployment-executor 的 `references/local-patch-management.md`

## 7. 质量门禁

### 部署前检查
- [ ] 部署计划已形成
- [ ] 回滚路径已确认
- [ ] 目标端口无冲突
- [ ] 配置文件/密钥已就位
- [ ] 依赖/镜像可获取

### 部署后验证
- [ ] 服务进程/容器运行正常
- [ ] 健康检查端点返回正确
- [ ] 关键功能smoke test通过
- [ ] 日志无异常错误
- [ ] 反向代理/SSL正常

### 部署后清理
- [ ] 临时token已清除
- [ ] 构建缓存已清理（如需要）
- [ ] 旧版本保留用于回滚（不立即删除）
- [ ] 部署记录已更新

## 8. 禁止事项

- 禁止未经确认直接执行 `docker compose down -v`、`rm -rf` 等破坏性命令
- 禁止在未备份配置的情况下覆盖 `.env`、nginx配置、systemd unit
- 禁止将token、密钥、密码写入仓库文件或日志
- 禁止跳过验证步骤直接宣称部署完成
- 禁止操作其它仓库的代码（即使有权限），只能通过issues反馈
- 禁止在多服务共存环境中不检查端口冲突就部署

## 9. 远端仓库保护与Issue提交

- 发现上游仓库的bug或需要的改进，通过issue提交，不直接修改上游代码
- 本地补丁必须有对应的upstream issue记录
- Issue记录保存在 `issues/` 目录，格式：`<repo>-<issue-number>.md`

## 10. 关键参考文件

优先级从高到低：

1. 本 `AGENTS.md`
2. `deploy/` 下的部署映射和docker-compose文件
3. `runbooks/` 下的操作手册
4. `configs/` 下的配置文件
5. deployment-executor skill 的 `references/` 文档

## 11. 经验沉淀

每轮部署或运维完成后，回顾过程中遇到的问题、踩坑、方法，评估是否需要补充到本文件。
"""


def render_file(
    rel: str,
    profile: str,
    project_name: str,
    target: Path,
    skills: List[str],
    with_mcp: bool,
    with_uv: bool,
) -> str:
    title = project_name
    directory_map = f"Profile: {profile}\nTarget: {target}\n"
    if rel == "AGENTS.md":
        if profile == "ops":
            return _render_ops_agents_md(title, directory_map, skills)
        extra = ""
        if profile == "course":
            extra = "\n- 课程内容遵循：厘清概念 → 举例实践 → 推理分析 → 自己动手 → 反馈提升。\n- 避免解决方案堆砌、AIGC式空泛表达、缺少教学递进、只讲工具不讲原理、只讲概念不落实验。\n"
        elif profile == "security-research":
            extra = "\n- 安全研究必须具备合法授权、实验隔离、证据留存、可复现性和清晰风险边界。\n- 不生成、执行或协助未授权攻击操作。\n"
        elif profile == "writing":
            extra = "\n- 写作任务强调结构清晰、总分总叙事、术语一致、引用可追溯、输出可审阅版本。\n"
        elif profile == "skills-package":
            extra = "\n- Skill必须边界清晰、输入输出明确、不越权、不隐藏执行、不私自联网、不读取无关文件、不泄露敏感信息。\n"
        result = f"""# Project Agent Guide

## Project Goal

{title} is an AI-agent-friendly project workspace initialized with the `{profile}` profile.

## Project Type

{profile}

## Working Principles

- Understand the goal before acting.
- Propose a plan before large-scale edits.
- Do not overwrite existing files unless explicitly confirmed.
- Do not delete files unless explicitly requested.
- Leave notes for important changes.
- When code is involved, prefer adding or updating tests.
- When operations are involved, preserve rollback and auditability.
- Never write secrets, API keys, tokens, passwords, private keys, or production credentials into repository files.
- Do not operate on other repositories (even with access); raise issues instead.
- When network operations fail (SSH, package install, git clone, API calls), retry at least twice before changing approach — transient failures are common.
- Do not track installed skill/command/agent files in version control — they are derived from the skill source (packs) and regenerated by the installer. Add platform skill directories to `.gitignore`.{extra}

## Directory Map

```text
{directory_map}```

## Preferred Tools

- uv for Python project setup
- pytest for tests
- ruff for linting
- markdownlint for markdown checks
- drawio for architecture diagrams
- docker only when explicitly needed
- MCP filesystem server for controlled project access

## Skills

Recommended skills:

{chr(10).join(f"- {s}" for s in skills)}

## MCP

MCP configuration examples may be placed under `mcp/`. Use placeholders only. Do not commit real secrets.

## Quality Gates

- README explains project goal and usage.
- Tasks or roadmap exist.
- QA checklist exists.
- Generated outputs are separated from sources.
- Development projects have tests or a test plan.

## Do Not

- Do not write secrets.
- Do not hide shell commands.
- Do not overwrite user files silently.
- Do not mix temporary outputs into formal materials.
- Do not perform offensive security actions without explicit lawful authorization and isolated scope.
"""
        # Profile-specific trailing sections
        if profile == "code":
            return (
                result
                + """
## Development Gotchas

<!--
记录代码库中非代码自解释的约定、已知陷阱、关键设计约束。
规则：
- 每条必须是"违反会导致 bug，且代码本身无法自解释"的约束
- 上限 10 条；超过时审视哪些已通过代码改进不再需要
- 一次性排查过程不记录
-->

- 发现 `void this.xxx`、空方法体、`@ts-ignore` 等绕过模式时，视为架构缺陷而非有意设计，主动向用户报告
- 修改状态枚举时，同步更新转换守卫表；新增状态前确认调用方会设置它
- 新增平台适配器时，检查所有 IO 边界（消息发送、输出格式化、长度截断）是否有平台分发逻辑

## Architecture Decisions

<!--
重大技术选型和设计决策的简要记录。
格式：一句话结论 + 指向 docs/ 下完整 ADR 的链接（如有）。
-->

## Crystallization Triggers

经验沉淀不在每次 commit 后触发。以下时机评估是否有新 gotcha 需记录：

- 完成架构审查并修复问题后
- 修复了"看起来不是 bug 但其实是"的问题后
- 新增平台/适配器/集成点后
"""
            )
        return result
    if rel == "README.md":
        return f"""# {title}

## Overview

This project was initialized as a `{profile}` project for long-term collaboration between human maintainers and AI agents.

## Goals

- Define the project objective clearly.
- Keep source materials, generated outputs, tasks, and QA artifacts separated.
- Make future agent work auditable and reviewable.

## Directory Structure

See `AGENTS.md` and the generated initialization report.

## How to Use

1. Review `AGENTS.md`.
2. Fill in this README with concrete project goals.
3. Add tasks to `tasks/backlog.md` or the profile-specific task file.
4. Run the QA checklist before accepting generated outputs.

## Development Environment

{("Python development should use uv. See docs/development.md or setup instructions." if with_uv else "No development environment was created by default.")}

## Skills and Agents

Recommended skills are recorded in `.opencode/skills/manifest.md`.

## MCP Integration

{("MCP templates are available under mcp/." if with_mcp else "MCP templates were not requested during initialization.")}

## Quality Control

Use the QA checklist under `qa/` before merging, publishing, or delivering outputs.

## Next Steps

- Replace placeholder goals with real project objectives.
- Confirm the directory map.
- Add the first three actionable tasks.
"""
    if rel.endswith("manifest.md"):
        rows = "\n".join(
            f"| {s} | recommended | n/a | {now()} | profile:{profile} | not installed unless copied separately |"
            for s in skills
        )
        return (
            "# Skills Manifest\n\n| Skill | Source | Branch | Installed At | Purpose | Notes |\n|---|---|---|---|---|---|\n"
            + rows
            + "\n"
        )
    if rel == "pyproject.toml":
        pkg = slugify(project_name).replace("_", "-")
        mod = slugify(project_name)
        return f'''[project]\nname = "{pkg}"\nversion = "0.1.0"\ndescription = "{title}"\nrequires-python = ">=3.10"\ndependencies = []\n\n[tool.pytest.ini_options]\ntestpaths = ["tests"]\n\n[tool.ruff]\nline-length = 100\ntarget-version = "py310"\n\n[tool.ruff.lint]\nselect = ["E", "F", "I", "B"]\n\n[tool.mypy]\npython_version = "3.10"\nwarn_unused_configs = true\n'''
    if rel.endswith("mcp-config.example.json"):
        return (
            json.dumps(
                {
                    "mcpServers": {
                        "filesystem": {
                            "command": "npx",
                            "args": [
                                "-y",
                                "@modelcontextprotocol/server-filesystem",
                                "<PROJECT_DIR>",
                            ],
                        },
                        "custom-threat-intel": {
                            "command": "python",
                            "args": ["<PATH_TO_SERVER>/run_server.py"],
                            "env": {"THREATBOOK_API_KEY": "<YOUR_API_KEY>"},
                        },
                        "custom-node-mcp": {
                            "command": "node",
                            "args": ["<PATH_TO_SERVER>/index.js"],
                        },
                    }
                },
                ensure_ascii=False,
                indent=2,
            )
            + "\n"
        )
    if rel == "deploy/deployment-map.md":
        return f"""# Deployment Map

Generated for `{title}` using the `{profile}` profile.

## 仓库 → 部署路径映射

| 仓库 | 分支/Tag | 部署路径 | 部署方式 | 端口 | 备注 |
|------|---------|---------|---------|------|------|
| <!-- 填写 --> | | | | | |

## 本地补丁状态

### Upstreamed Fixes

| 修复内容 | Issue链接 | Upstream Commit | 日期 |
|---------|----------|-----------------|------|
| (暂无) | | | |

### Deployment-Specific Patches

| 修改内容 | 原因 | 影响文件 | 每次git pull后需重新apply |
|---------|------|---------|---------------------------|
| (暂无) | | | |
"""
    heading = Path(rel).stem.replace("-", " ").replace("_", " ").title()
    return f"# {heading}\n\nGenerated for `{title}` using the `{profile}` profile.\n\n## Purpose\n\nTODO: Fill in concrete content.\n"


def add_mcp_files(profile: Dict[str, object]) -> None:
    dirs = set(profile["dirs"])  # type: ignore[index]
    files = set(profile["files"])  # type: ignore[index]
    dirs.add("mcp")
    files.update({"mcp/README.md", "mcp/mcp-config.example.json", "mcp/connection-checklist.md"})
    profile["dirs"] = sorted(dirs)
    profile["files"] = sorted(files)


def write_file(path: Path, content: str, overwrite: bool, dry_run: bool) -> Tuple[str, Path]:
    if path.exists() and not overwrite:
        new_path = path.with_name(path.name + ".new")
        if new_path.exists():
            i = 1
            while path.with_name(path.name + f".new.{i}").exists():
                i += 1
            new_path = path.with_name(path.name + f".new.{i}")
        if not dry_run:
            new_path.write_text(content, encoding="utf-8")
        return "conflict_new", new_path
    if not dry_run:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    return "created" if not path.exists() else "overwritten", path


_GITIGNORE_SKILL_DIRS = """\
# Installed skills — derived from packs, regenerated by the installer.
# Source of truth is the skill pack repo; installed copies must not be tracked.
.opencode/skills/
.opencode/commands/
.opencode/agents/
.opencode/installed-packs.json
.claude/skills/
.claude/installed-packs.json
.cursor/skills/
.cursor/installed-packs.json
.github/skills/
.github/installed-packs.json
.windsurf/skills/
.windsurf/installed-packs.json
.agents/skills/
.agents/installed-packs.json
"""

_GITIGNORE_TEMPLATE = """\
# OS
Thumbs.db
Desktop.ini
.DS_Store

# Editors
.vscode/
.idea/
*.swp
*.swo

# Python
__pycache__/
*.pyc
.venv/
.uv/

{skill_dirs}
# PetFish local state
.petfish/
"""


def _render_gitignore() -> str:
    return _GITIGNORE_TEMPLATE.format(skill_dirs=_GITIGNORE_SKILL_DIRS)


def detect_environment(enabled: bool) -> Dict[str, str]:
    """Best-effort runtime environment detection.

    Returns version strings or "not found". If detection is disabled, values are
    reported as "not found" to keep report output stable and non-interactive.
    """
    result = {"uv": "not found", "python": "not found", "node": "not found"}
    if not enabled:
        return result

    checks = {
        "uv": [["uv", "--version"]],
        "python": [["python3", "--version"], ["python", "--version"]],
        "node": [["node", "--version"]],
    }

    for key, commands in checks.items():
        for command in commands:
            exe = command[0]
            if shutil.which(exe) is None:
                continue
            try:
                completed = subprocess.run(
                    command,
                    capture_output=True,
                    text=True,
                    timeout=5,
                    check=False,
                )
            except Exception:
                continue
            if completed.returncode == 0:
                output = (completed.stdout or completed.stderr or "").strip()
                if output:
                    result[key] = output
                    break
    return result


def run_git_initialization(
    target: Path, with_git: bool, no_git: bool, dry_run: bool
) -> Dict[str, object]:
    """Best-effort git initialization and initial commit.

    Never raises; failures are reported as warnings while overall initialization
    proceeds.
    """
    summary: Dict[str, object] = {
        "git_initialized": False,
        "git_committed": False,
        "notes": [],
    }
    notes = summary["notes"]
    assert isinstance(notes, list)

    git_dir = target / ".git"
    has_git_repo = git_dir.exists() and git_dir.is_dir()

    if no_git:
        notes.append("Git initialization explicitly skipped (--no-git)")
        return summary

    if not with_git:
        if has_git_repo:
            notes.append("Git repo already exists")
        else:
            notes.append("Git initialization not requested")
        return summary

    if has_git_repo:
        notes.append("Git repo already exists")
        return summary

    if dry_run:
        notes.append("Dry run: would run git init, git add ., and initial commit")
        return summary

    commands: List[Tuple[List[str], str]] = [
        (["git", "init"], "git init"),
        (["git", "add", "."], "git add ."),
        (
            [
                "git",
                "commit",
                "-m",
                "Initial commit (generated by PEtFiSh project-initializer)",
            ],
            "git commit",
        ),
    ]

    for cmd, label in commands:
        try:
            completed = subprocess.run(
                cmd,
                cwd=target,
                capture_output=True,
                text=True,
                check=False,
            )
        except Exception as exc:
            notes.append(f"WARNING: {label} failed: {exc}")
            return summary

        if completed.returncode != 0:
            stderr = (completed.stderr or "").strip()
            stdout = (completed.stdout or "").strip()
            detail = stderr or stdout or "unknown error"
            notes.append(f"WARNING: {label} failed: {detail}")
            return summary

        if label == "git init":
            summary["git_initialized"] = True
        if label == "git commit":
            summary["git_committed"] = True

    notes.append("Git repository initialized and initial commit created")
    return summary


def main(argv: List[str]) -> int:
    parser = argparse.ArgumentParser(
        description="Safely initialize an AI-agent-friendly project workspace."
    )
    parser.add_argument("--profile", choices=sorted(PROFILES), default="minimal")
    parser.add_argument("--target", default=".")
    parser.add_argument("--project-name", default=None)
    parser.add_argument(
        "--with-opencode",
        action="store_true",
        help="Include .opencode directories and manifest (included by most profiles).",
    )
    parser.add_argument("--with-mcp-template", action="store_true")
    parser.add_argument(
        "--with-uv",
        action="store_true",
        help="Generate uv development setup notes. Does not run uv.",
    )
    git_group = parser.add_mutually_exclusive_group()
    git_group.add_argument(
        "--with-git",
        action="store_true",
        help="Initialize git repository and create initial commit (best-effort).",
    )
    git_group.add_argument(
        "--no-git",
        action="store_true",
        help="Explicitly skip git initialization.",
    )
    parser.add_argument(
        "--detect-env",
        action="store_true",
        help="Detect uv/python/node versions and include them in the report.",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing files. Use only after user confirmation.",
    )
    parser.add_argument(
        "--no-overwrite",
        action="store_true",
        help="Do not overwrite existing files; conflicts create .new files.",
    )
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)

    target = Path(args.target).expanduser().resolve()
    if is_dangerous(target):
        print(f"ERROR: refusing to initialize dangerous target path: {target}", file=sys.stderr)
        return 2

    profile = dict(PROFILES[args.profile])
    if args.with_mcp_template:
        add_mcp_files(profile)

    project_name = args.project_name or target.name or "project"
    overwrite = bool(args.overwrite and not args.no_overwrite)
    env_info = detect_environment(enabled=args.detect_env)

    created_dirs: List[str] = []
    created_files: List[str] = []
    conflict_files: List[str] = []

    if not args.dry_run:
        target.mkdir(parents=True, exist_ok=True)

    for d in profile["dirs"]:  # type: ignore[index]
        p = target / str(d)
        if not p.exists():
            if not args.dry_run:
                p.mkdir(parents=True, exist_ok=True)
            created_dirs.append(str(p.relative_to(target)))

    # Generate .gitignore with platform skill exclusions
    gitignore_path = target / ".gitignore"
    if not gitignore_path.exists():
        gitignore_content = _render_gitignore()
        status, written = write_file(
            gitignore_path, gitignore_content, overwrite=False, dry_run=args.dry_run
        )
        if status == "conflict_new":
            conflict_files.append(str(written.relative_to(target)))
        else:
            created_files.append(str(written.relative_to(target)))

    skills = list(profile.get("skills", []))  # type: ignore[arg-type]
    for f in profile["files"]:  # type: ignore[index]
        rel = str(f)
        content = render_file(
            rel, args.profile, project_name, target, skills, args.with_mcp_template, args.with_uv
        )
        status, written = write_file(
            target / rel, content, overwrite=overwrite, dry_run=args.dry_run
        )
        if status == "conflict_new":
            conflict_files.append(str(written.relative_to(target)))
        else:
            created_files.append(str(written.relative_to(target)))

    git_result = run_git_initialization(
        target=target,
        with_git=bool(args.with_git),
        no_git=bool(args.no_git),
        dry_run=args.dry_run,
    )
    git_notes = git_result["notes"]
    assert isinstance(git_notes, list)

    report = f"""# Initialization Report

## Summary

Project `{project_name}` initialized with profile `{args.profile}`.

## Project Profile

- Target: `{target}`
- Profile: `{args.profile}`
- Dry run: `{args.dry_run}`
- Overwrite: `{overwrite}`
- MCP templates: `{args.with_mcp_template}`
- uv setup notes: `{args.with_uv}`
- Generated at: `{now()}`

## Created Directories

{chr(10).join(f"- {x}" for x in created_dirs) if created_dirs else "- None"}

## Created Files

{chr(10).join(f"- {x}" for x in created_files) if created_files else "- None"}

## Skipped Files

- Existing files were not overwritten unless `--overwrite` was set.

## Conflicts

{chr(10).join(f"- {x}" for x in conflict_files) if conflict_files else "- None"}

## Skills Installed

- This script records recommended skills in `.opencode/skills/manifest.md`; it does not download remote skills.

## MCP Templates Generated

- `{args.with_mcp_template}`

## Development Environment

- This script does not execute `uv` or other package managers.
- If needed, run: `uv init`, `uv add --dev pytest ruff`, `uv run pytest`, `uv run ruff check .`.

## Git Repository

- Git initialized: `{git_result["git_initialized"]}`
- Initial commit: `{git_result["git_committed"]}`
- Note:
{chr(10).join(f"  - {x}" for x in git_notes) if git_notes else "  - None"}

## Detected Environment

- uv: `{env_info["uv"]}`
- Python: `{env_info["python"]}`
- Node.js: `{env_info["node"]}`

## Risks and Warnings

- Review `.new` files and merge manually if conflicts were found.
- Do not commit secrets into MCP configuration or project files.

## Recommended Next Steps

1. Review `AGENTS.md` and `README.md`.
2. Fill in concrete project goals.
3. Add first tasks to backlog or roadmap.
4. Run the QA checklist before accepting outputs.
"""
    report_path = target / "initialization-report.md"
    status, written = write_file(report_path, report, overwrite=overwrite, dry_run=args.dry_run)
    if status == "conflict_new":
        conflict_files.append(str(written.relative_to(target)))
    else:
        created_files.append(str(written.relative_to(target)))

    result = {
        "target": str(target),
        "profile": args.profile,
        "dry_run": args.dry_run,
        "git": git_result,
        "environment": env_info,
        "created_directories": created_dirs,
        "created_files": created_files,
        "conflicts": conflict_files,
        "report": str(written),
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
