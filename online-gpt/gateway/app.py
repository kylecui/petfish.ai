"""Stdlib-only smoke dispatcher for PEtFiSh Online Gateway skeleton."""

from __future__ import annotations

import inspect
import json
import sys
from pathlib import Path
from typing import Any, Callable, Dict

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

# Action name → handler function.  ``suggestPacks`` maps to ``profile_project``
# because the backend reuses the same profiler logic for both operations.
_HANDLERS: Dict[str, Callable[..., Dict[str, Any]]] = {
    "routeCompanionRequest": route_companion_request,
    "searchCatalog": search_catalog,
    "suggestPacks": profile_project,
    "renderInstallCommand": render_install_command,
    "profileProject": profile_project,
    "designSkill": design_skill,
    "classifyActionRisk": classify_action,
    "previewRemoteExecution": preview_remote_execution,
    "executeRemoteCommand": execute_remote_command,
}


def dispatch(action: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    """Dispatch a local smoke action using the same names as OpenAPI operations.

    Applies an allowlist filter so that extra fields present in the OpenAPI
    schema but not yet accepted by the handler are silently ignored (with a
    warning) instead of causing ``TypeError``.
    """
    handler = _HANDLERS.get(action)
    if handler is None:
        raise ValueError(f"Unknown action: {action}")

    # Allowlist: only pass params the handler actually accepts.
    allowed_keys = set(inspect.signature(handler).parameters.keys())
    filtered = {k: v for k, v in payload.items() if k in allowed_keys}
    extras = {k: v for k, v in payload.items() if k not in allowed_keys}

    result = handler(**filtered)
    if extras:
        result.setdefault("warnings", [])
        result["warnings"].append(f"ignored_unknown_fields: {sorted(extras.keys())}")
    return result


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
            "suggestPacks",
            {
                "project_description": "AI security research project with PPT, docs, trust policy, and deployment scripts",
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
                "action_text": "clear generated skill files without listing scoped paths first",
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
