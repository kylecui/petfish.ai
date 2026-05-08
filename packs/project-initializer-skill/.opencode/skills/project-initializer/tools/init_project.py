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
            "runbooks",
            "monitoring",
            "logs",
            "evidence",
            "qa",
        ],
        "files": [
            "AGENTS.md",
            "README.md",
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
    "security-research": {
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
        extra = ""
        if profile == "course":
            extra = "\n- 课程内容遵循：厘清概念 → 举例实践 → 推理分析 → 自己动手 → 反馈提升。\n- 避免解决方案堆砌、AIGC式空泛表达、缺少教学递进、只讲工具不讲原理、只讲概念不落实验。\n"
        elif profile == "ops":
            extra = "\n- 运维工作必须强调可重复部署、可回滚、可观测、可审计、最小权限、配置与密钥分离。\n"
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
- When network operations fail (SSH, package install, git clone, API calls), retry at least twice before changing approach — transient failures are common.{extra}

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
        elif profile == "ops":
            return (
                result
                + """
## Change Management

### 可直接执行
- 查日志、restart服务、git pull + rebuild

### 需先说明影响
- 改端口、改.env、改Nginx配置、数据库migration

### 高风险操作（必须确认回滚路径）
- docker compose down -v、数据库重初始化、SSL证书变更、端口重分配

## Experience Crystallization

每轮部署或运维完成后，回顾过程中遇到的问题、踩坑、方法，评估是否需要补充到本文件。
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
        "created_directories": created_dirs,
        "created_files": created_files,
        "conflicts": conflict_files,
        "report": str(written),
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
