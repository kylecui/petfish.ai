"""Install command renderer for PEtFiSh Companion GPT."""

from __future__ import annotations

from typing import Iterable

from schemas import ModuleEnvelope, envelope

VALID_OPERATIONS = {"install", "upgrade", "uninstall"}


def render_install_command(
    packs: Iterable[str],
    platform: str,
    target: str = ".",
    scope: str = "project",
    operation: str = "install",
) -> ModuleEnvelope:
    """Render an install/upgrade/uninstall command without executing it."""

    pack_list = [p.strip() for p in packs if p.strip()]
    if not pack_list:
        return envelope(
            module="installer",
            ok=False,
            errors=["No packs were provided."],
            result_level="advice_only",
        )
    if operation not in VALID_OPERATIONS:
        return envelope(
            module="installer",
            ok=False,
            errors=[f"Unsupported operation: {operation}"],
            result_level="advice_only",
        )

    base = "uv run https://raw.githubusercontent.com/kylecui/petfish.ai/master/install.py"

    # Online runtime: no local install — packs are semantic references only.
    if platform == "online":
        return envelope(
            module="installer",
            mode="dry_run",
            result_level="advice_only",
            data={
                "operation": "semantic_only",
                "packs": pack_list,
                "platform": "online",
                "runtime": "chatgpt-project",
                "command": None,
                "explanation": (
                    "Online PEtFiSh projects do not require local installation. "
                    "Packs are referenced semantically through GPT Instructions and Knowledge. "
                    "If a local adapter is needed later, render a local install command with the appropriate --platform."
                ),
            },
            warnings=[
                "This is an online PEtFiSh project. No local files are modified.",
                "Packs are semantic references, not local installations.",
            ],
        )

    flags = [f"--pack {','.join(pack_list)}", f"--platform {platform}", f"--target {target}"]

    if scope == "global":
        flags.append("--global")
    if operation == "upgrade":
        flags.append("--force")
    if operation == "uninstall":
        flags.insert(0, "--uninstall")

    command = f"{base} {' '.join(flags)}"

    return envelope(
        module="installer",
        mode="dry_run",
        result_level="command_rendered",
        data={
            "operation": operation,
            "packs": pack_list,
            "platform": platform,
            "target": target,
            "scope": scope,
            "command": command,
            "expected_effects": [
                "Install or update platform-specific skill directories.",
                "Merge instruction fragments into the platform instruction file.",
                "Update local PEtFiSh registry metadata when supported.",
            ],
            "verify": _verification_hint(platform),
        },
        warnings=["This only renders a command. It does not execute locally."],
    )


def _verification_hint(platform: str) -> str:
    if platform == "opencode":
        return "ls .opencode/skills && test -f AGENTS.md"
    if platform == "claude":
        return "ls .claude/skills && test -f CLAUDE.md"
    if platform in {"codex", "antigravity", "universal"}:
        return "ls .agents/skills && test -f AGENTS.md"
    if platform == "cursor":
        return "ls .cursor/skills || ls .cursor/rules"
    if platform == "copilot":
        return "test -f .github/copilot-instructions.md"
    if platform == "windsurf":
        return "test -f .windsurfrules"
    return "Check the platform-specific skills directory and instruction file."
