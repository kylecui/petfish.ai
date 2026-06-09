"""Catalog module for PEtFiSh Companion GPT."""

from __future__ import annotations

from typing import Dict, List

from schemas import ModuleEnvelope, envelope

CORE_PACKS: Dict[str, str] = {
    "init": "Project initializer and /initproject wizard",
    "companion": "Companion Gateway, /petfish, fish-brain, fish-market",
    "petfish": "Writing style and rewrite guidance",
    "toolchain": "Skill lifecycle pipeline",
}

OPTIONAL_PACKS: Dict[str, str] = {
    "course": "Course outline, content, labs, QA, and QC workflows",
    "testdocs": "Test case and usage documentation workflows",
    "deploy": "Deployment, CI/CD, health check, rollback, and ops workflows",
    "ppt": "Slide and presentation workflows",
    "calibrate": "Anti-sycophancy review and decision calibration",
    "context": "Topic governance, context isolation, and contamination scoring",
    "trust": "Skill trust governance and policy checks",
    "research": "Evidence-backed scientific, product, and planning research",
    "reflect": "Structured reflection and corrective actions",
    "doc-reader": "Document-to-Markdown conversion and reading",
}

TRIGGERS: Dict[str, List[str]] = {
    "deploy": ["deploy", "docker", "ci", "cd", "rollback", "health check", "部署", "回滚"],
    "course": ["course", "teaching", "lab", "课程", "教学", "实验"],
    "ppt": ["ppt", "slide", "presentation", "幻灯片", "演示"],
    "testdocs": ["test", "test case", "测试", "测试用例", "usage doc"],
    "research": ["research", "literature", "evidence", "论文", "文献", "调研", "证据"],
    "context": ["context", "topic", "drift", "上下文", "话题", "污染"],
    "trust": ["trust", "policy", "audit", "dangerous", "安全", "审计", "危险"],
    "doc-reader": ["pdf", "docx", "xlsx", "pptx", "markdown", "文档", "读取"],
}


def search_catalog(query: str, platform: str | None = None) -> ModuleEnvelope:
    """Search packs by alias, description, and trigger words."""

    needle = query.lower()
    all_packs = {**CORE_PACKS, **OPTIONAL_PACKS}
    matches = []
    for alias, purpose in all_packs.items():
        trigger_hit = any(needle in t.lower() or t.lower() in needle for t in TRIGGERS.get(alias, []))
        if needle in alias.lower() or needle in purpose.lower() or trigger_hit:
            matches.append(
                {
                    "alias": alias,
                    "purpose": purpose,
                    "kind": "core" if alias in CORE_PACKS else "optional",
                    "platform": platform,
                }
            )

    return envelope(
        module="catalog",
        result_level="advice_only",
        data={"query": query, "matches": matches},
        warnings=[] if matches else ["No exact catalog match; use project profiling or market search."],
    )


def get_profile_packs(profile: str) -> List[str]:
    profiles = {
        "minimal": ["context", "petfish"],
        "course": ["context", "course", "doc-reader", "petfish"],
        "code": ["context", "deploy", "petfish", "testdocs"],
        "ops": ["context", "deploy", "petfish"],
        "security": ["context", "deploy", "petfish", "testdocs", "trust"],
        "research": ["context", "doc-reader", "petfish", "research"],
        "writing": ["context", "petfish", "ppt"],
        "skills-package": ["context", "petfish", "testdocs"],
        "comprehensive": [
            "context",
            "course",
            "deploy",
            "doc-reader",
            "petfish",
            "ppt",
            "testdocs",
            "trust",
            "research",
            "reflect",
        ],
    }
    return profiles.get(profile, [])
