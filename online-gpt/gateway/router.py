"""Companion Kernel router for PEtFiSh Companion GPT."""

from __future__ import annotations

from typing import Iterable

from schemas import ModuleEnvelope, envelope
from modules.catalog import search_catalog
from modules.installer import render_install_command
from modules.profiler import profile_project
from modules.remote_control import preview_remote_execution
from modules.skill_workbench import design_skill
from modules.trust_gate import classify_action


def route_companion_request(
    user_message: str,
    active_context: str | None = None,
    installed_packs: Iterable[str] | None = None,
    platform: str = "opencode",
    project_profile: str | None = None,
    mode: dict | None = None,
) -> ModuleEnvelope:
    """Route a user request to a deterministic module hint."""

    text = user_message.lower()
    installed = set(installed_packs or [])
    mode = mode or {"depth": "balanced", "rigor": False}

    if any(k in text for k in ["rm -rf", "delete", "删除", "uninstall", "reset --hard", "token", "secret", "密钥"]):
        trust = classify_action(user_message, target_runtime=platform)
        return envelope(
            module="kernel",
            mode="dry_run",
            result_level="advice_only",
            data={
                "intent": "trust_classify",
                "topic_risk": "low",
                "required_modules": ["trust_gate"],
                "action_policy": trust["data"].get("decision"),
                "response_contract": "remote_execution_preview" if "remote" in text else "direct_explanation",
                "trust_gate": trust["data"],
                "mode": mode,
            },
        )

    if any(k in text for k in ["remote", "遥控", "执行", "opencode", "codex", "antigravity"]):
        if any(k in text for k in ["执行", "run", "execute", "remote"]):
            preview = preview_remote_execution(platform, user_message)
            return envelope(
                module="kernel",
                mode="preview_only",
                result_level="previewed",
                data={
                    "intent": "remote_preview",
                    "required_modules": ["remote_control", "trust_gate"],
                    "response_contract": "remote_execution_preview",
                    "preview": preview["data"],
                    "mode": mode,
                },
                warnings=preview["warnings"],
            )

    if any(k in text for k in ["install", "安装", "upgrade", "升级", "profile", "pack"]):
        prof = profile_project(user_message, platform=platform)
        packs = prof["data"].get("packs", ["context", "petfish"])
        cmd = render_install_command(packs, platform=platform)
        return envelope(
            module="kernel",
            mode="dry_run",
            result_level="command_rendered",
            data={
                "intent": "install_plan",
                "required_modules": ["profiler", "catalog", "installer"],
                "recommended_packs": packs,
                "response_contract": "pack_recommendation",
                "profile": prof["data"],
                "install": cmd["data"],
                "installed_packs": sorted(installed),
                "mode": mode,
            },
            warnings=cmd["warnings"],
        )

    if any(k in text for k in ["skill", "技能", "pack", "触发", "trigger"]):
        skill = design_skill(user_message, platform=platform)
        return envelope(
            module="kernel",
            mode="dry_run",
            result_level="advice_only",
            data={
                "intent": "skill_design",
                "required_modules": ["skill_workbench"],
                "response_contract": "skill_workbench",
                "skill": skill["data"],
                "mode": mode,
            },
            warnings=skill["warnings"],
        )

    if any(k in text for k in ["search", "查找", "catalog", "市场", "market"]):
        catalog = search_catalog(user_message, platform=platform)
        return envelope(
            module="kernel",
            mode="dry_run",
            result_level="advice_only",
            data={
                "intent": "catalog_search",
                "required_modules": ["catalog"],
                "response_contract": "direct_explanation",
                "catalog": catalog["data"],
                "mode": mode,
            },
            warnings=catalog["warnings"],
        )

    evaluation_triggers = ["好吗", "对吗", "是否", "是不是", "worth", "good", "feasible", "evaluate", "评价"]
    anti_sycophancy = any(k in text for k in evaluation_triggers)
    return envelope(
        module="kernel",
        mode="dry_run",
        result_level="advice_only",
        data={
            "intent": "general_or_review",
            "topic_risk": "low",
            "required_modules": ["companion_identity"],
            "response_contract": "critical_review" if anti_sycophancy else "direct_explanation",
            "anti_sycophancy_required": anti_sycophancy,
            "active_context": active_context,
            "installed_packs": sorted(installed),
            "project_profile": project_profile,
            "mode": mode,
        },
    )
