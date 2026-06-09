"""Trust Gate module for PEtFiSh Companion GPT."""

from __future__ import annotations

import re
from typing import Iterable

from schemas import ModuleEnvelope, envelope

# Patterns are intentionally conservative and should be expanded through tests.
DESTRUCTIVE_PATTERNS = [
    r"\bdelete\b",
    r"\bremove\b",
    r"\buninstall\b",
    r"\breset\b",
    r"\bclean\b",
    r"删除",
    r"清空",
    r"卸载",
    r"重置",
]

SECRET_PATTERNS = [
    r"api[_-]?key",
    r"token",
    r"secret",
    r"password",
    r"private[_-]?key",
    r"凭证",
    r"密钥",
]

PUBLISH_PATTERNS = [
    r"\brelease\b",
    r"\bpublish\b",
    r"\btag\b",
    r"发布",
]

WRITE_PATTERNS = [
    r"\bwrite\b",
    r"\bcreate\b",
    r"\bupdate\b",
    r"\bmodify\b",
    r"写入",
    r"创建",
    r"修改",
]


def classify_action(action_text: str, target_runtime: str | None = None, paths: Iterable[str] | None = None) -> ModuleEnvelope:
    """Classify action risk before remote or local execution."""

    text = action_text.lower()
    risk = "read_only"
    decision = "allow"
    reasons = []

    if _matches(text, SECRET_PATTERNS):
        risk = "secret_sensitive"
        decision = "require_confirmation"
        reasons.append("Action text appears to involve secrets or credentials; values must be masked.")

    if _matches(text, PUBLISH_PATTERNS):
        risk = "publish_release"
        decision = "require_confirmation"
        reasons.append("Publish or release actions require release discipline and explicit approval.")

    if _matches(text, WRITE_PATTERNS):
        risk = "write_scoped"
        decision = "require_confirmation"
        reasons.append("Action may modify files or repository state.")

    if _matches(text, DESTRUCTIVE_PATTERNS):
        risk = "destructive"
        decision = "require_second_confirmation"
        reasons.append("Action may delete, reset, uninstall, or irreversibly alter state.")
        if not paths:
            decision = "deny"
            reasons.append("Destructive action has no explicit scoped path list.")

    return envelope(
        module="trust_gate",
        mode="dry_run",
        result_level="advice_only",
        data={
            "risk": risk,
            "decision": decision,
            "target_runtime": target_runtime,
            "paths": list(paths or []),
            "reasons": reasons or ["No obvious side-effect risk detected."],
        },
    )


def _matches(text: str, patterns: Iterable[str]) -> bool:
    return any(re.search(pattern, text, flags=re.IGNORECASE) for pattern in patterns)
