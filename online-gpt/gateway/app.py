"""Stdlib-only smoke dispatcher for PEtFiSh Online Gateway skeleton."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Dict

GATEWAY_DIR = Path(__file__).resolve().parent
if str(GATEWAY_DIR) not in sys.path:
    sys.path.insert(0, str(GATEWAY_DIR))

from router import route_companion_request  # noqa: E402
from modules.catalog import search_catalog  # noqa: E402
from modules.installer import render_install_command  # noqa: E402
from modules.profiler import profile_project  # noqa: E402
from modules.remote_control import execute_remote_command, preview_remote_execution  # noqa: E402
from modules.skill_workbench import design_skill  # noqa: E402
from modules.trust_gate import classify_action  # noqa: E402


def dispatch(action: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    """Dispatch a local smoke action using the same names as OpenAPI operations."""

    if action == "routeCompanionRequest":
        return route_companion_request(**payload)
    if action == "searchCatalog":
        return search_catalog(**payload)
    if action == "renderInstallCommand":
        return render_install_command(**payload)
    if action == "profileProject":
        return profile_project(**payload)
    if action == "designSkill":
        return design_skill(**payload)
    if action == "classifyActionRisk":
        return classify_action(**payload)
    if action == "previewRemoteExecution":
        return preview_remote_execution(**payload)
    if action == "executeRemoteCommand":
        return execute_remote_command(**payload)
    raise ValueError(f"Unknown action: {action}")


def _demo() -> None:
    samples = [
        (
            "routeCompanionRequest",
            {
                "user_message": "我要在 OpenCode 安装一个 security profile，并支持远程执行预览",
                "platform": "opencode",
            },
        ),
        (
            "profileProject",
            {
                "project_description": "AI security research project with PPT, docs, trust policy, and deployment scripts",
                "platform": "opencode",
            },
        ),
        (
            "renderInstallCommand",
            {
                "packs": ["context", "deploy", "petfish", "testdocs", "trust"],
                "platform": "opencode",
                "target": ".",
            },
        ),
        (
            "classifyActionRisk",
            {
                "action_text": "rm -rf .opencode/skills without listing files first",
                "target_runtime": "opencode",
            },
        ),
        (
            "previewRemoteExecution",
            {
                "target_runtime": "opencode",
                "project_alias": "petfish.ai",
                "task": "run skill gate for online-gpt",
            },
        ),
    ]
    for action, payload in samples:
        print(f"\n## {action}")
        print(json.dumps(dispatch(action, payload), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    _demo()
