#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = []
# ///
"""Scaffold a new skill directory.

Usage:
  uv run generate_skill.py --name my-skill --type automation --output ./my-skills/
  uv run generate_skill.py --name my-skill --profile writing --trigger "help me write,compose text" --output .
  uv run generate_skill.py --name my-skill --mode new-skill --with-quality-gate --output .
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import textwrap

NAME_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
SKILL_TYPES = (
    "automation", "workflow", "knowledge",
    "writing", "review", "research", "project", "hybrid",
)
_DESCRIPTIONS = {
    "automation": "Automate {p} tasks with repeatable scripts. Use when the user asks to run, scaffold, validate, or troubleshoot {p} through a command-driven workflow.",
    "workflow": "Guide a structured {p} workflow from intake to handoff. Use when the user asks for {p} planning, execution, review, or repeatable process support.",
    "knowledge": "Apply {p} guidance and explain the key rules or tradeoffs. Use when the user needs {p} expertise, standards, or best-practice recommendations.",
    "writing": "Produce and refine {p} text with clear structure and style. Use when the user asks to draft, rewrite, polish, or structure {p} content.",
    "review": "Assess and evaluate {p} against defined criteria. Use when the user asks to review, critique, score, or audit {p} output.",
    "research": "Research {p} systematically with evidence and sources. Use when the user asks to investigate, survey, analyze, or report on {p}.",
    "project": "Manage {p} project lifecycle from scoping to handoff. Use when the user asks to plan, track, coordinate, or deliver {p} work.",
    "hybrid": "Combine multiple capabilities for {p} tasks. Use when the user needs {p} support that spans workflow, knowledge, and execution.",
}
_ROLES = {
    "automation": "automation specialist. Execute the task through a repeatable script-backed workflow and return clear results.",
    "workflow": "workflow specialist. Guide the task from intake through execution with a clear, auditable process.",
    "knowledge": "knowledge specialist. Apply domain rules, explain tradeoffs, and adapt guidance to the local context.",
    "writing": "writing specialist. Produce clear, structured text through iterative drafting and revision.",
    "review": "review/assessment specialist. Evaluate work against explicit criteria and produce structured findings.",
    "research": "research specialist. Investigate questions systematically with traceable evidence.",
    "project": "project management specialist. Drive work from scoping through handoff with clear milestones.",
    "hybrid": "multi-capability specialist. This skill combines multiple types. See capability_profile below for type mix.",
}
_WORKFLOWS = {
    "automation": "1. Confirm the target, inputs, and expected output.\n2. Inspect local files or config before running automation.\n3. Run the helper script in `scripts/` or the project-native command.\n4. Summarize the result, failures, and next action.",
    "workflow": "1. Clarify the request and identify missing context.\n2. Inspect the relevant files, configs, or references.\n3. Execute the workflow in ordered steps.\n4. Return the result, risks, and next step.",
    "knowledge": "1. Identify the decision or question.\n2. Read local project rules before giving guidance.\n3. Apply the most relevant principles.\n4. Return a recommendation with reasoning and limits.",
    "writing": "1. **Intake**: clarify purpose, audience, tone, and length.\n2. **Draft**: produce an initial structured draft.\n3. **Review**: check clarity, coherence, completeness, and style.\n4. **Revise**: address issues and refine wording.\n5. **Deliver**: output the final version with change notes.",
    "review": "1. **Define rubric**: identify or confirm evaluation criteria and weights.\n2. **Inspect**: read the target artifact thoroughly.\n3. **Classify findings**: group issues by severity and category.\n4. **Produce report**: output findings with evidence and recommendations.",
    "research": "1. **Frame question**: define the research question and scope.\n2. **Discover sources**: find relevant materials and register them.\n3. **Extract evidence**: capture key excerpts with source attribution.\n4. **Synthesize**: cluster findings, identify gaps and contradictions.\n5. **Report**: deliver structured conclusions with evidence links.",
    "project": "1. **Assess scope**: clarify goals, constraints, and stakeholders.\n2. **Plan**: break work into tasks with owners, dependencies, and dates.\n3. **Execute**: track progress, surface blockers, adjust plan.\n4. **Verify**: confirm deliverables meet acceptance criteria.\n5. **Handoff**: produce closure summary and transition notes.",
    "hybrid": "1. Identify which capability the user needs.\n2. Route to the matching sub-workflow.\n3. Execute the sub-workflow from that type's template.\n4. Integrate results across capabilities if needed.\n5. Return unified output.",
}
_MUST_DO = {
    "automation": "- validate inputs before execution\n- fail with clear error messages\n- keep the workflow repeatable",
    "workflow": "- keep the workflow explicit\n- cite concrete evidence when relevant\n- surface important assumptions",
    "knowledge": "- align advice with project context\n- explain important tradeoffs\n- distinguish rules from recommendations",
    "writing": "- confirm audience and tone before drafting\n- preserve factual accuracy and source attribution\n- deliver complete sections, no placeholder text",
    "review": "- define criteria before judging\n- cite specific locations for each finding\n- provide at least one positive observation",
    "research": "- distinguish facts from inferences\n- record search strategy for reproducibility\n- flag contradictory sources",
    "project": "- surface blockers early\n- keep scope changes visible and logged\n- produce verifiable deliverables",
    "hybrid": "- declare which capability is active for each step\n- keep sub-workflows independent and composable\n- surface handoff points between capabilities",
}
_MUST_NOT = {
    "automation": "- do not hardcode machine-specific paths\n- do not hide command failures\n- do not change unrelated files",
    "workflow": "- do not skip key steps silently\n- do not invent facts\n- do not expand scope without saying so",
    "knowledge": "- do not ignore local conventions\n- do not overstate certainty\n- do not turn the skill into a long reference dump",
    "writing": "- do not add rhetorical filler or slogans\n- do not change the user's intended meaning\n- do not output unreviewed first drafts",
    "review": "- do not give vague praise without evidence\n- do not skip criteria that pass\n- do not conflate personal preference with defect",
    "research": "- do not treat model knowledge as research evidence\n- do not skip source attribution\n- do not present hypotheses as confirmed findings",
    "project": "- do not proceed without scope confirmation\n- do not hide schedule risk\n- do not close milestones without acceptance",
    "hybrid": "- do not blend workflows into one ambiguous process\n- do not skip routing when user intent is unclear\n- do not assume a single type covers all cases",
}
_EXTRA_SECTIONS = {
    "automation": "\n## Tool usage\n\n- Read relevant config or input files first.\n- Use `scripts/run_task.py` for repeatable execution.\n- Prefer relative paths and explicit arguments.\n\n## Output\n\n- command or script used\n- result summary\n- changed or affected paths\n- follow-up action if needed",
    "workflow": "\n## Tool usage\n\n- Read the local source of truth before acting.\n- Use references for reusable checklists or decision rules.\n- Keep outputs structured and easy to review.\n\n## Output\n\n- summary\n- findings or actions taken\n- assumptions\n- next step",
    "knowledge": "\n## Tool usage\n\n- Read local docs, specs, or examples first.\n- Use `references/` for detailed rules and examples.\n- Keep the main answer concise and decision-oriented.\n\n## Output\n\n- recommendation\n- reasoning\n- rules applied\n- caveats",
    "writing": "\n## Output Contract\n\n- structured text matching the requested format\n- change summary listing key revisions\n- word count or length check if applicable",
    "review": "\n## Output Contract\n\n- rubric or criteria used\n- findings grouped by severity\n- specific evidence for each finding\n- actionable recommendations",
    "research": "\n## Output Contract\n\n- research question with scope boundaries\n- source list with authority and freshness ratings\n- key findings linked to evidence IDs\n- confidence level and limitations",
    "project": "\n## Output Contract\n\n- milestone plan with dependencies\n- status summary with blockers\n- risk register updates\n- handoff or closure notes",
    "hybrid": "\n## capability_profile\n\n- primary_type: [TODO: set in SKILL.md]\n- secondary_types: [TODO: set in SKILL.md]\n\n## Output Contract\n\n- [TODO: define per capability mix]",
}


def validate_name(name: str) -> None:
    if not name:
        raise ValueError("Skill name is required.")
    if len(name) > 64:
        raise ValueError("Skill name must be 64 characters or fewer.")
    if not NAME_PATTERN.fullmatch(name):
        raise ValueError("Skill name must use lowercase letters, numbers, and single hyphens only.")


def validate_description(description: str) -> None:
    if not description or not description.strip():
        raise ValueError("Description must be non-empty.")
    if len(description) > 1024:
        raise ValueError("Description must be 1024 characters or fewer.")


def title_from_name(name: str) -> str:
    return " ".join(part.capitalize() for part in name.split("-"))


def default_description(name: str, skill_type: str) -> str:
    return _DESCRIPTIONS[skill_type].format(p=name.replace("-", " "))


def render_skill_md(name: str, skill_type: str, description: str,
                    output_contract: str = "", handoff: str = "") -> str:
    title = title_from_name(name)
    role = _ROLES[skill_type]
    wf = _WORKFLOWS[skill_type]
    md = _MUST_DO[skill_type]
    must_not = _MUST_NOT[skill_type]
    extra = _EXTRA_SECTIONS.get(skill_type, "")
    body = f"# {title}\n\n## Role\n\nYou are the `{name}` {role}\n\n## Workflow\n\n{wf}\n{extra}\n\n## Must do\n\n{md}\n\n## Must not do\n\n{must_not}"
    if output_contract and "## Output Contract" not in body:
        body += f"\n\n## Output Contract\n\n{output_contract}\n"
    if handoff and "## Handoff & Boundaries" not in body:
        body += f"\n\n## Handoff & Boundaries\n\n{handoff}\n"
    fm = f"---\nname: {name}\ndescription: {description}\nmetadata:\n  version: 0.1.0\n  author: your-team\n---"
    return f"{fm}\n\n{body}\n"


def render_automation_script(name: str) -> str:
    title = title_from_name(name)
    return textwrap.dedent(f"""\
        #!/usr/bin/env python3
        # /// script
        # requires-python = ">=3.9"
        # dependencies = []
        # ///
        \"\"\"Placeholder automation entrypoint for {name}.\"\"\"

        from __future__ import annotations
        import argparse, sys

        def build_parser() -> argparse.ArgumentParser:
            parser = argparse.ArgumentParser(description="Run the {title} helper workflow.")
            parser.add_argument("--target", default=".", help="Target path or resource.")
            return parser

        def main() -> int:
            args = build_parser().parse_args()
            if not args.target:
                build_parser().error("--target must not be empty.")
            print(f"TODO: implement {name} automation for {{args.target}}")
            return 0

        if __name__ == "__main__":
            try:
                raise SystemExit(main())
            except KeyboardInterrupt:
                print("Interrupted.", file=sys.stderr)
                raise SystemExit(130)
    """) + "\n"


def render_evals(name: str, triggers: list[str] | None = None,
                 non_triggers: list[str] | None = None) -> str:
    evals: list[dict] = []
    if triggers:
        for i, prompt in enumerate(triggers, 1):
            evals.append({"id": f"trigger-{i:03d}", "prompt": prompt, "should_trigger": True,
                "expected_output": f"Activates {name} workflow and produces expected output.",
                "assertions": ["Response follows the defined workflow stages.", "Response includes the required output sections."]})
    if non_triggers:
        for i, prompt in enumerate(non_triggers, 1):
            evals.append({"id": f"no-trigger-{i:03d}", "prompt": prompt, "should_trigger": False,
                "expected_output": f"Does not activate {name}'s workflow.",
                "assertions": [f"Response does not follow {name}'s main workflow.", f"Response does not produce {name}'s output contract."]})
    if not triggers and not non_triggers:
        evals.append({"id": "trigger-primary-task",
            "prompt": f"[TODO: describe the most obvious user request that should activate {name}]",
            "should_trigger": True, "expected_output": f"[TODO: what {name} should produce]",
            "assertions": ["[TODO: assertion about workflow followed]", "[TODO: assertion about required output included]"]})
        evals.append({"id": "no-trigger-adjacent",
            "prompt": "[TODO: describe a similar task that belongs to another skill]",
            "should_trigger": False, "expected_output": f"Does not activate {name}'s workflow.",
            "assertions": [f"Response does not follow {name}'s main workflow.", f"Response does not produce {name}'s output contract."]})
    return json.dumps({"skill_name": name, "version": "0.1.0", "evals": evals}, ensure_ascii=False, indent=2) + "\n"


def render_handoff_md(owns: str = "", does_not_own: str = "") -> str:
    o = owns or "[TODO: list responsibilities within scope]"
    d = does_not_own or "[TODO: list responsibilities for other skills]"
    return f"# Handoff & Boundaries\n\n## This skill owns\n{o}\n\n## This skill does not own\n{d}\n\n## Adjacent skills\n[TODO: list related skills and their scope]\n\n## Composition rules\n[TODO: how this skill composes with adjacent skills]\n"


_QUALITY_GATE = "# Authoring Quality Gate\n\n## Structural\n- [ ] Name valid and matches directory\n- [ ] Directory structure complete\n\n## Frontmatter\n- [ ] Description under 1024 chars with what/when/boundary\n\n## SKILL.md Body\n- [ ] Under 500 lines\n- [ ] Has Role, Activation, Workflow, Output Contract, Must Do/Must Not Do\n- [ ] Has Handoff & Boundaries\n\n## Evals\n- [ ] At least 3 should-trigger, 2 should-not-trigger\n- [ ] Each eval has 2+ assertions\n"


def write_text(path: str, content: str) -> None:
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(content)


def scaffold_skill(
    name: str, skill_type: str, description: str, output_dir: str, *,
    mode: str = "new-skill", triggers: list[str] | None = None,
    non_triggers: list[str] | None = None, output_contract: str = "",
    handoff: str = "", with_assets: bool = False, with_evals: bool = True,
    with_quality_gate: bool = False,
) -> dict:
    base_dir = os.path.abspath(output_dir)
    os.makedirs(base_dir, exist_ok=True)
    skill_dir = os.path.join(base_dir, name)
    dirs = {k: os.path.join(skill_dir, k) for k in ("references", "scripts", "assets", "evals")}

    if mode in ("new-skill", "extract-from-workflow"):
        if os.path.exists(skill_dir):
            raise FileExistsError(f"Target skill directory already exists: {skill_dir}")
        for d in (skill_dir, *dirs.values()):
            os.makedirs(d, exist_ok=False)
    else:
        # improve-existing-skill, add-evals, refactor-boundaries — target must exist
        if not os.path.exists(skill_dir):
            raise FileNotFoundError(f"Target skill directory does not exist: {skill_dir}")
        for d in dirs.values():
            os.makedirs(d, exist_ok=True)

    created = []
    assumptions = []
    warnings = []
    next_steps = []

    p = os.path.join(skill_dir, "SKILL.md")
    write_text(p, render_skill_md(name, skill_type, description, output_contract, handoff))
    created.append(p)

    if with_evals:
        p = os.path.join(dirs["evals"], "evals.json")
        write_text(p, render_evals(name, triggers, non_triggers))
        created.append(p)
        if not triggers and not non_triggers:
            warnings.append("Evals contain TODO stubs. Fill in before release.")
            next_steps.append("Fill in eval TODOs with real trigger/non-trigger prompts")
        if triggers and len(triggers) < 3:
            warnings.append(f"Only {len(triggers)} should-trigger evals. Recommended: >= 3.")
        if non_triggers and len(non_triggers) < 2:
            warnings.append(f"Only {len(non_triggers)} should-not-trigger evals. Recommended: >= 2.")
        next_steps.append("Run trigger evaluator to validate eval coverage")

    if mode == "new-skill" or handoff:
        p = os.path.join(dirs["references"], "handoff-boundaries.md")
        write_text(p, render_handoff_md())
        created.append(p)

    if with_quality_gate:
        p = os.path.join(dirs["references"], "quality-gate.md")
        write_text(p, _QUALITY_GATE)
        created.append(p)

    if with_assets:
        p = os.path.join(dirs["assets"], "README.md")
        write_text(p, f"# {title_from_name(name)} Assets\n\nPlace diagrams, templates, or static resources here.\n")
        created.append(p)

    if skill_type == "automation":
        p = os.path.join(dirs["scripts"], "run_task.py")
        write_text(p, render_automation_script(name))
        created.append(p)

    if description == default_description(name, skill_type):
        assumptions.append("Description auto-generated from name and type")
        next_steps.append("Write a custom description in SKILL.md frontmatter")
    next_steps.append("Run skill-lint to validate the scaffold")
    if with_evals and triggers:
        next_steps.append("Expand assertions beyond the default two per eval")

    def _rel(p: str) -> str:
        try:
            return os.path.relpath(p, os.getcwd())
        except ValueError:
            return p

    return {
        "name": name, "type": skill_type, "mode": mode, "root": _rel(skill_dir),
        "created_files": [_rel(p) for p in created],
        "created_directories": [_rel(d) for d in (skill_dir, *dirs.values())],
        "validation_warnings": warnings, "assumptions": assumptions, "recommended_next": next_steps,
    }


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Scaffold a new skill directory.")
    p.add_argument("--name", required=True, help="Skill name (<=64 chars, lowercase, hyphens).")
    p.add_argument("--type", dest="skill_type", choices=SKILL_TYPES, help="Skill type.")
    p.add_argument("--profile", dest="profile", choices=SKILL_TYPES, help="Skill profile (synonym for --type).")
    p.add_argument("--mode", default="new-skill", choices=["new-skill", "improve-existing", "add-evals", "refactor"], help="Generation mode.")
    p.add_argument("--description", help="Optional skill description.")
    p.add_argument("--output", default=".", help="Output directory.")
    p.add_argument("--trigger", default="", help="Comma-separated should-trigger prompts.")
    p.add_argument("--non-trigger", default="", help="Comma-separated should-not-trigger prompts.")
    p.add_argument("--output-contract", default="", help="Description of expected output.")
    p.add_argument("--handoff", default="", help="Description of handoff boundaries.")
    p.add_argument("--with-assets", action="store_true", help="Generate template assets.")
    p.add_argument("--with-evals", action="store_true", default=True, help="Generate evals (default).")
    p.add_argument("--no-evals", dest="with_evals", action="store_false", help="Skip eval generation.")
    p.add_argument("--with-quality-gate", action="store_true", help="Generate references/quality-gate.md.")
    p.add_argument("--json", action="store_true", help="Print result as JSON.")
    return p


def main() -> int:
    args = build_parser().parse_args()
    resolved_type = args.profile or args.skill_type
    if not resolved_type:
        build_parser().error("Either --type or --profile is required.")
    try:
        validate_name(args.name)
        desc = args.description or default_description(args.name, resolved_type)
        validate_description(desc)
        triggers = [t.strip() for t in args.trigger.split(",") if t.strip()] or None
        non_triggers = [t.strip() for t in args.non_trigger.split(",") if t.strip()] or None
        result = scaffold_skill(args.name, resolved_type, desc, args.output,
            mode=args.mode, triggers=triggers, non_triggers=non_triggers,
            output_contract=args.output_contract, handoff=args.handoff,
            with_assets=args.with_assets, with_evals=args.with_evals,
            with_quality_gate=args.with_quality_gate)
    except (ValueError, FileExistsError, OSError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    print(f"Created skill scaffold:\n- name: {result['name']}\n- type: {result['type']}\n- mode: {result['mode']}")
    print(f"- root: {result['root']}")
    for label, items in [("directories", result["created_directories"]), ("files", result["created_files"])]:
        print(f"- {label}:")
        for i in items:
            print(f"  - {i}")
    for label, items in [("warnings", result["validation_warnings"]), ("assumptions", result["assumptions"]), ("recommended next steps", result["recommended_next"])]:
        if items:
            print(f"- {label}:")
            for i in items:
                print(f"  - {i}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
