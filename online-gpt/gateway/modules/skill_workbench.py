"""Skill Workbench skeleton for PEtFiSh Companion GPT."""

from __future__ import annotations

from schemas import ModuleEnvelope, envelope


def design_skill(
    skill_goal: str,
    target_pack: str | None = None,
    platform: str = "opencode",
    safety_constraints: list[str] | None = None,
) -> ModuleEnvelope:
    """Return a skill contract skeleton, not final files."""

    normalized_name = _slug(skill_goal)[:48] or "new-skill"
    return envelope(
        module="skill_workbench",
        mode="dry_run",
        result_level="advice_only",
        data={
            "skill_goal": skill_goal,
            "suggested_name": normalized_name,
            "target_pack": target_pack or "community-or-project-pack",
            "platform": platform,
            "contract": {
                "purpose": skill_goal,
                "triggers": ["TODO: add precise positive trigger examples"],
                "non_triggers": ["TODO: add near-miss examples that should not activate the skill"],
                "inputs": ["TODO: user request and project context"],
                "outputs": ["TODO: artifact, plan, command, or review"],
                "safety_constraints": safety_constraints or [],
                "files": ["SKILL.md", "examples.md", "evals/trigger/*.json"],
                "quality_flow": ["lint", "audit", "trigger_eval", "quality_gate"],
            },
        },
        warnings=["This is a design contract only. File rendering should be a separate scoped action."],
    )


def _slug(text: str) -> str:
    allowed = []
    for ch in text.lower():
        if ch.isalnum():
            allowed.append(ch)
        elif ch in {" ", "-", "_", "/"}:
            allowed.append("-")
    slug = "".join(allowed).strip("-")
    while "--" in slug:
        slug = slug.replace("--", "-")
    return slug
