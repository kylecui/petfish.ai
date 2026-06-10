"""Companion Kernel router for PEtFiSh Companion GPT.

The router preserves core PEtFiSh semantics first, then adds online runtime
routing. Platform names such as OpenCode, Codex, or Antigravity should not by
themselves force remote execution routing; they often appear in install,
profile, or skill requests.
"""

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
    runtime: dict | None = None,
    project_profile: str | None = None,
    mode: dict | None = None,
) -> ModuleEnvelope:
    """Route a user request to a deterministic module hint."""

    text = user_message.lower()
    installed = set(installed_packs or [])
    mode = mode or {"depth": "balanced", "rigor": False}

    # Normalize runtime: detect online project requests and override platform.
    if _is_online_project_request(text):
        platform = "online"

    # Apply runtime context when provided.
    if runtime and runtime.get("kind") == "online":
        platform = "online"

    if _has_trust_boundary(text):
        trust = classify_action(user_message, target_runtime=platform)
        response_contract = "critical_review" if _is_evaluative(text) else (
            "remote_execution_preview" if _is_remote_request(text) else "direct_explanation"
        )
        return envelope(
            module="kernel",
            mode="dry_run",
            result_level="advice_only",
            data={
                "intent": "trust_classify",
                "topic_risk": "low",
                "required_modules": ["trust_gate"],
                "action_policy": trust["data"].get("decision"),
                "response_contract": response_contract,
                "trust_gate": trust["data"],
                "mode": mode,
            },
        )

    # Evaluative questions (anti-sycophancy) take priority over install/skill routing.
    # Ensures "is this approach right?" → critical_review, not install/skill.
    if _is_evaluative(text):
        # Build context-appropriate review data
        review_data: dict = {
            "intent": "critical_review",
            "required_modules": ["companion_identity"],
            "response_contract": "critical_review",
            "anti_sycophancy_required": True,
            "active_context": active_context,
            "installed_packs": sorted(installed),
            "project_profile": project_profile,
            "mode": mode,
            "review_dimensions": ["criteria", "counterargument", "conclusion"],
        }
        # Identity questions: affirm independent online companion runtime
        if any(k in text for k in ["是什么", "什么是", "who is", "identity", "companion gpt"]):
            review_data["system_identity"] = {
                "name": "PEtFiSh Companion GPT",
                "type": "independent online companion runtime (独立在线伴侣运行时)",
                "requires_opencode": False,
                "requires_ide": False,
                "operating_modes": ["Standalone (P0)", "Gateway (P1)", "Adapter (P2, deferred)"],
                "source_of_truth": "Core PEtFiSh (petfish.ai)",
            }
        # Remote/trust boundary questions: include safety context
        if any(k in text for k in ["控制", "远程", "执行", "可以", "能不能"]):
            review_data["safety_boundary"] = {
                "remote_execution": "preview-only, requires Trust Gate + user approval",
                "direct_control": False,
                "local_execution_claim": "prohibited unless verified adapter confirms",
                "trust_gate_required": True,
            }
        return envelope(
            module="kernel",
            mode="dry_run",
            result_level="advice_only",
            data=review_data,
        )

    if _is_install_request(text):
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

    if _is_skill_request(text):
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

    if _is_catalog_request(text):
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

    if _is_remote_request(text):
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

    evaluation_triggers = ["好吗", "对吗", "是否", "是不是", "worth", "good", "feasible", "evaluate", "评价"]
    anti_sycophancy = any(k in text for k in evaluation_triggers)
    return envelope(
        module="kernel",
        mode="dry_run",
        result_level="advice_only",
        data={
            "intent": "direct_explanation",
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


def _has_trust_boundary(text: str) -> bool:
    trust_terms = [
        "delete",
        "删除",
        "uninstall",
        "reset",
        "清空",
        "覆盖",
        "token",
        "secret",
        "密钥",
        "password",
        "凭证",
    ]
    return any(k in text for k in trust_terms)


def _is_evaluative(text: str) -> bool:
    """Detect questions that require critical review rather than direct routing."""
    evaluative = [
        "好吗", "对吗", "是否", "是不是", "能不能", "可否",
        "是否可以", "是否替代", "该不该", "是否值得",
        "worth", "good", "feasible", "evaluate", "评价",
    ]
    return any(k in text for k in evaluative)


def _is_install_request(text: str) -> bool:
    return any(k in text for k in [
        "install", "安装", "upgrade", "升级", "profile",
        "pack", "初始化", "initproject",
        "装什么", "应装什么", "装哪个",
        "装 context", "装 petfish",
    ])


def _is_skill_request(text: str) -> bool:
    # Avoid false positive when "skills" refers to platform directory paths
    if any(k in text for k in ["放在哪里", "在哪里", "目录", "路径", "directory"]):
        return False
    return any(k in text for k in ["skill", "技能", "触发", "trigger", "skill.md"])


def _is_catalog_request(text: str) -> bool:
    return any(k in text for k in ["search", "查找", "catalog", "市场", "market", "list packs", "pack 列表"])


def _is_remote_request(text: str) -> bool:
    remote_terms = ["remote", "遥控", "远程", "local daemon", "本地 daemon", "本地执行"]
    execute_terms = ["执行", "run", "execute", "preview", "预览", "daemon"]
    return any(k in text for k in remote_terms) or (
        any(agent in text for agent in ["opencode", "codex", "antigravity"]) and any(k in text for k in execute_terms)
    )


def _is_online_project_request(text: str) -> bool:
    """Detect requests that explicitly target ChatGPT Project / online runtime."""
    return any(k in text for k in [
        "chatgpt project",
        "chatgpt-only",
        "hosted chat",
        "online project",
        "online runtime",
        "在线项目",
        "在线 runtime",
        "只在 chatgpt",
        "不依赖本地",
        "无本地 adapter",
        "无本地适配器",
        "chatgpt 项目",
    ])
