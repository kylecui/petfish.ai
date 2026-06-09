"""Project profiler for PEtFiSh Companion GPT."""

from __future__ import annotations

from typing import Iterable, Set

from schemas import ModuleEnvelope, envelope


def profile_project(
    project_description: str,
    platform: str = "opencode",
    requested_domains: Iterable[str] | None = None,
    constraints: Iterable[str] | None = None,
) -> ModuleEnvelope:
    """Infer a profile and pack set from project intent."""

    text = " ".join([project_description, " ".join(requested_domains or []), " ".join(constraints or [])]).lower()
    packs: Set[str] = {"context", "petfish"}
    profile = "minimal"
    reasons = ["context protects topic continuity for online/local cooperation", "petfish keeps writing and interaction style consistent"]

    # Online code review project → review-online profile.
    if _is_online_review_project(text, platform):
        packs = {"companion", "context", "petfish", "testdocs", "trust"}
        optional_packs = ["calibrate", "deploy"]
        has_deploy_scope = any(k in text for k in [
            "docker", "ci", "ci/cd", "cd", "ops", "rollback", "运维", "部署",
            "生产", "production", "release", "deployment",
        ])
        reasons = [
            "companion runs Companion Gateway before substantive review work",
            "context isolates PRs, modules, and review threads",
            "petfish keeps review writing precise and actionable",
            "testdocs reasons about tests, coverage, and acceptance cases",
            "trust classifies risky changes and policy boundaries",
        ]
        if has_deploy_scope:
            reasons.append("deploy recommended for CI/CD/release/ops scope")
        else:
            reasons.append("deploy is optional unless CI/CD, release, or operations scope is present")
        return envelope(
            module="profiler",
            mode="dry_run",
            result_level="advice_only",
            data={
                "project_description": project_description,
                "platform": "online",
                "runtime": {
                    "kind": "online",
                    "surface": "chatgpt-project",
                    "local_adapter": "none",
                    "filesystem": "unavailable",
                    "execution_truth_default": "advice_only",
                },
                "recommended_profile": "review-online",
                "packs": sorted(packs),
                "optional_packs": optional_packs,
                "reasons": reasons,
                "assumptions": [
                    "No local filesystem, repository, IDE, CLI, git history, or test runner access is assumed.",
                    "Only uploaded or pasted artifacts are reviewable.",
                    "Local execution requires a verified adapter.",
                    "Deploy is optional unless CI/CD, release, or operations scope is present.",
                ],
            },
    )

    # ---- generic profile classification ----

    if any(k in text for k in ["security", "安全", "audit", "policy", "trust", "remote", "遥控", "执行"]):
        packs.add("trust")
        packs.add("deploy")
        packs.add("testdocs")
        reasons.append("trust is required for security-sensitive or remote-control workflows")
        reasons.append("deploy covers CI/CD, health check, rollback, and ops workflows")
        reasons.append("testdocs covers test cases and usage documentation")
        profile = "security"

    if any(k in text for k in ["deploy", "docker", "ci", "cd", "ops", "运维", "部署", "回滚"]):
        packs.add("deploy")
        reasons.append("deploy covers CI/CD, health check, rollback, and ops workflows")
        profile = "ops" if profile == "minimal" else profile

    if any(k in text for k in ["test", "测试", "test case", "usage doc", "用例"]):
        packs.add("testdocs")
        reasons.append("testdocs covers test cases and usage documentation")
        profile = "code" if profile == "minimal" else profile

    if any(k in text for k in ["research", "literature", "evidence", "论文", "文献", "调研"]):
        packs.add("research")
        packs.add("doc-reader")
        reasons.append("research and doc-reader support evidence-backed research and source ingestion")
        profile = "research" if profile == "minimal" else profile

    if any(k in text for k in ["ppt", "slide", "presentation", "演示", "幻灯片"]):
        packs.add("ppt")
        reasons.append("ppt supports presentation and slide workflows")
        profile = "writing" if profile == "minimal" else profile

    if any(k in text for k in ["course", "teaching", "lab", "课程", "教学", "实验"]):
        packs.add("course")
        packs.add("doc-reader")
        reasons.append("course supports courseware, labs, QA, and QC workflows")
        profile = "course" if profile == "minimal" else profile

    if len(packs) >= 8:
        profile = "comprehensive"

    return envelope(
        module="profiler",
        mode="dry_run",
        result_level="advice_only",
        data={
            "project_description": project_description,
            "platform": platform,
            "recommended_profile": profile,
            "packs": sorted(packs),
            "reasons": reasons,
            "assumptions": [
                "Profile is inferred from text and should be refined with repository inspection when available.",
                "This module recommends a minimal sufficient pack set instead of blindly choosing comprehensive.",
            ],
        },
    )


def _is_online_review_project(text: str, platform: str | None) -> bool:
    """Detect online code review project requests."""
    online = platform == "online" or any(k in text for k in [
        "chatgpt project", "chatgpt-only", "online project", "在线项目", "只在 chatgpt",
    ])
    review = any(k in text for k in [
        "review", "code review", "pr", "pull request", "diff", "审查", "代码审查", "评审",
    ])
    return online and review
