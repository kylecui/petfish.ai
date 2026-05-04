#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = []
# ///
"""Scaffold a new skill directory.

Usage:
  uv run generate_skill.py --name my-skill --type automation --output ./my-skills/
  uv run generate_skill.py --name code-reviewer --type workflow --description "Review code for quality" --output .
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import textwrap

NAME_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
SKILL_TYPES = ("automation", "workflow", "knowledge")


def validate_name(name: str) -> None:
    if not name:
        raise ValueError("Skill name is required.")
    if len(name) > 64:
        raise ValueError("Skill name must be 64 characters or fewer.")
    if not NAME_PATTERN.fullmatch(name):
        raise ValueError(
            "Skill name must use lowercase letters, numbers, and single hyphens only."
        )


def validate_description(description: str) -> None:
    if not description or not description.strip():
        raise ValueError("Description must be non-empty.")
    if len(description) > 1024:
        raise ValueError("Description must be 1024 characters or fewer.")


def title_from_name(name: str) -> str:
    return " ".join(part.capitalize() for part in name.split("-"))


def default_description(name: str, skill_type: str) -> str:
    phrase = name.replace("-", " ")
    descriptions = {
        "automation": (
            f"Automate {phrase} tasks with repeatable scripts. Use when the user "
            f"asks to run, scaffold, validate, or troubleshoot {phrase} through "
            "a command-driven workflow."
        ),
        "workflow": (
            f"Guide a structured {phrase} workflow from intake to handoff. Use "
            f"when the user asks for {phrase} planning, execution, review, or "
            "repeatable process support."
        ),
        "knowledge": (
            f"Apply {phrase} guidance and explain the key rules or tradeoffs. Use "
            f"when the user needs {phrase} expertise, standards, or best-practice "
            "recommendations."
        ),
    }
    return descriptions[skill_type]


def render_skill_md(name: str, skill_type: str, description: str) -> str:
    title = title_from_name(name)
    body = {
        "automation": textwrap.dedent(
            f"""
            # {title}

            ## Role

            You are the `{name}` automation specialist. Execute the task through a
            repeatable script-backed workflow and return clear results.

            ## When to use

            - The user wants `{name}` run reliably.
            - The task benefits from a repeatable command or helper script.
            - Validation or troubleshooting needs concrete command output.

            ## Workflow

            1. Confirm the target, inputs, and expected output.
            2. Inspect local files or config before running automation.
            3. Run the helper script in `scripts/` or the project-native command.
            4. Summarize the result, failures, and next action.

            ## Tool usage

            - Read relevant config or input files first.
            - Use `scripts/run_task.py` for repeatable execution.
            - Prefer relative paths and explicit arguments.

            ## Output

            - command or script used
            - result summary
            - changed or affected paths
            - follow-up action if needed

            ## Must do

            - validate inputs before execution
            - fail with clear error messages
            - keep the workflow repeatable

            ## Must not do

            - do not hardcode machine-specific paths
            - do not hide command failures
            - do not change unrelated files
            """
        ).strip(),
        "workflow": textwrap.dedent(
            f"""
            # {title}

            ## Role

            You are the `{name}` workflow specialist. Guide the task from intake
            through execution with a clear, auditable process.

            ## Intake

            Gather:

            - goal
            - scope
            - constraints
            - expected output

            ## Workflow

            1. Clarify the request and identify missing context.
            2. Inspect the relevant files, configs, or references.
            3. Execute the workflow in ordered steps.
            4. Return the result, risks, and next step.

            ## Tool usage

            - Read the local source of truth before acting.
            - Use references for reusable checklists or decision rules.
            - Keep outputs structured and easy to review.

            ## Output

            - summary
            - findings or actions taken
            - assumptions
            - next step

            ## Must do

            - keep the workflow explicit
            - cite concrete evidence when relevant
            - surface important assumptions

            ## Must not do

            - do not skip key steps silently
            - do not invent facts
            - do not expand scope without saying so
            """
        ).strip(),
        "knowledge": textwrap.dedent(
            f"""
            # {title}

            ## Role

            You are the `{name}` knowledge specialist. Apply domain rules,
            explain tradeoffs, and adapt guidance to the local context.

            ## When to use

            - The user needs expert guidance in this domain.
            - The task depends on standards, heuristics, or best practices.
            - A decision needs explanation, not just execution.

            ## Workflow

            1. Identify the decision or question.
            2. Read local project rules before giving guidance.
            3. Apply the most relevant principles.
            4. Return a recommendation with reasoning and limits.

            ## Tool usage

            - Read local docs, specs, or examples first.
            - Use `references/` for detailed rules and examples.
            - Keep the main answer concise and decision-oriented.

            ## Output

            - recommendation
            - reasoning
            - rules applied
            - caveats

            ## Must do

            - align advice with project context
            - explain important tradeoffs
            - distinguish rules from recommendations

            ## Must not do

            - do not ignore local conventions
            - do not overstate certainty
            - do not turn the skill into a long reference dump
            """
        ).strip(),
    }[skill_type]
    frontmatter = (
        f"---\n"
        f"name: {name}\n"
        f"description: {description}\n"
        f"metadata:\n"
        f"  version: 0.1.0\n"
        f"  author: your-team\n"
        f"---"
    )
    return f"{frontmatter}\n\n{body}\n"


def render_automation_script(name: str) -> str:
    title = title_from_name(name)
    return (
        textwrap.dedent(
            f"""
        #!/usr/bin/env python3
        # /// script
        # requires-python = ">=3.9"
        # dependencies = []
        # ///
        \"\"\"Placeholder automation entrypoint for {name}.\"\"\"

        from __future__ import annotations

        import argparse
        import sys


        def build_parser() -> argparse.ArgumentParser:
            parser = argparse.ArgumentParser(
                description="Run the {title} helper workflow."
            )
            parser.add_argument(
                "--target",
                default=".",
                help="Target path or resource for this automation.",
            )
            return parser


        def main() -> int:
            parser = build_parser()
            args = parser.parse_args()

            if not args.target:
                parser.error("--target must not be empty.")

            print(f"TODO: implement {name} automation for {{args.target}}")
            return 0


        if __name__ == "__main__":
            try:
                raise SystemExit(main())
            except KeyboardInterrupt:
                print("Interrupted.", file=sys.stderr)
                raise SystemExit(130)
        """
        ).strip()
        + "\n"
    )


def render_evals(name: str) -> str:
    payload = {
        "skill_name": name,
        "version": "0.1.0",
        "evals": [],
    }
    return json.dumps(payload, ensure_ascii=False, indent=2) + "\n"


def write_text(path: str, content: str) -> None:
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(content)


def scaffold_skill(
    name: str, skill_type: str, description: str, output_dir: str
) -> dict:
    base_dir = os.path.abspath(output_dir)
    os.makedirs(base_dir, exist_ok=True)

    skill_dir = os.path.join(base_dir, name)
    if os.path.exists(skill_dir):
        raise FileExistsError(f"Target skill directory already exists: {skill_dir}")

    references_dir = os.path.join(skill_dir, "references")
    scripts_dir = os.path.join(skill_dir, "scripts")
    assets_dir = os.path.join(skill_dir, "assets")
    evals_dir = os.path.join(skill_dir, "evals")

    for directory in (skill_dir, references_dir, scripts_dir, assets_dir, evals_dir):
        os.makedirs(directory, exist_ok=False)

    created_files = []

    skill_md_path = os.path.join(skill_dir, "SKILL.md")
    write_text(skill_md_path, render_skill_md(name, skill_type, description))
    created_files.append(skill_md_path)

    evals_path = os.path.join(evals_dir, "evals.json")
    write_text(evals_path, render_evals(name))
    created_files.append(evals_path)

    if skill_type == "automation":
        script_path = os.path.join(scripts_dir, "run_task.py")
        write_text(script_path, render_automation_script(name))
        created_files.append(script_path)

    return {
        "name": name,
        "type": skill_type,
        "root": skill_dir,
        "created_files": [os.path.relpath(path, os.getcwd()) for path in created_files],
        "created_directories": [
            os.path.relpath(path, os.getcwd())
            for path in (skill_dir, references_dir, scripts_dir, assets_dir, evals_dir)
        ],
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Scaffold a new skill directory.")
    parser.add_argument(
        "--name",
        required=True,
        help="Skill name. Must be <=64 chars and use lowercase letters, numbers, and hyphens.",
    )
    parser.add_argument(
        "--type",
        required=True,
        choices=SKILL_TYPES,
        help="Skill type: automation, workflow, or knowledge.",
    )
    parser.add_argument(
        "--description",
        help="Optional skill description. Must describe what the skill does and when to use it.",
    )
    parser.add_argument(
        "--output",
        default=".",
        help="Output directory where the skill directory will be created.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print the scaffold result as JSON.",
    )
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    try:
        validate_name(args.name)
        description = args.description or default_description(args.name, args.type)
        validate_description(description)
        result = scaffold_skill(args.name, args.type, description, args.output)
    except (ValueError, FileExistsError, OSError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0

    print("Created skill scaffold:")
    print(f"- name: {result['name']}")
    print(f"- type: {result['type']}")
    print(f"- root: {os.path.relpath(result['root'], os.getcwd())}")
    print("- directories:")
    for path in result["created_directories"]:
        print(f"  - {path}")
    print("- files:")
    for path in result["created_files"]:
        print(f"  - {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
