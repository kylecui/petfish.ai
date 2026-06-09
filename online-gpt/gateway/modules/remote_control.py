"""Remote-control module skeleton for PEtFiSh Companion GPT.

The execution endpoint is intentionally disabled until a trusted local daemon,
approval mechanism, and audit sink are connected.
"""

from __future__ import annotations

from schemas import ModuleEnvelope, envelope
from modules.trust_gate import classify_action


def preview_remote_execution(target_runtime: str, task: str, project_alias: str | None = None) -> ModuleEnvelope:
    """Preview remote/local execution without side effects."""

    trust = classify_action(task, target_runtime=target_runtime)
    return envelope(
        module="remote_control",
        mode="preview_only",
        result_level="previewed",
        data={
            "target_runtime": target_runtime,
            "project_alias": project_alias,
            "task": task,
            "trust_gate": trust["data"],
            "proposed_flow": [
                "compile intent",
                "classify risk",
                "preview command/task payload",
                "request approval if needed",
                "execute through local daemon only when enabled",
                "capture logs and summarize result",
            ],
        },
        warnings=["Remote preview has no side effects. Execution adapter is separate."],
    )


def execute_remote_command(target_runtime: str, task: str, approval_token: str, project_alias: str | None = None) -> ModuleEnvelope:
    """Disabled execution placeholder preserving the final endpoint contract."""

    return envelope(
        module="remote_control",
        ok=False,
        mode="disabled",
        result_level="previewed",
        data={
            "target_runtime": target_runtime,
            "project_alias": project_alias,
            "task": task,
            "approval_token_received": bool(approval_token),
        },
        warnings=["Remote execution endpoint is defined but disabled until a trusted adapter is connected."],
        errors=["remote_execute_disabled"],
    )
