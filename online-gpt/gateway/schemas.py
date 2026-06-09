"""Shared schemas and helpers for PEtFiSh Online Gateway skeleton.

This module deliberately uses stdlib-only Python so it can be smoke-tested in the
repository without installing web framework dependencies.
"""

from __future__ import annotations

from typing import Any, Dict, List, Literal, TypedDict

Platform = Literal[
    "opencode",
    "claude",
    "codex",
    "cursor",
    "copilot",
    "windsurf",
    "antigravity",
    "universal",
]

ResultLevel = Literal[
    "advice_only",
    "command_rendered",
    "dry_run",
    "previewed",
    "executed",
    "audit_logged",
]

Decision = Literal[
    "allow",
    "preview_only",
    "require_confirmation",
    "require_second_confirmation",
    "deny",
]


class ModuleEnvelope(TypedDict):
    ok: bool
    module: str
    mode: str
    result_level: ResultLevel
    data: Dict[str, Any]
    warnings: List[str]
    errors: List[str]
    audit: Dict[str, Any]


def envelope(
    *,
    module: str,
    data: Dict[str, Any] | None = None,
    ok: bool = True,
    mode: str = "dry_run",
    result_level: ResultLevel = "dry_run",
    warnings: List[str] | None = None,
    errors: List[str] | None = None,
    audit: Dict[str, Any] | None = None,
) -> ModuleEnvelope:
    """Create a standard module response envelope."""

    return {
        "ok": ok,
        "module": module,
        "mode": mode,
        "result_level": result_level,
        "data": data or {},
        "warnings": warnings or [],
        "errors": errors or [],
        "audit": audit or {},
    }
