#!/usr/bin/env python3
"""
Skill Sense Evaluation Module

Simulates skill detection using the TRIGGERS keyword mapping from catalog_query.py.
Since eval cannot call the actual Companion Gateway, this module uses the same
keyword-to-pack mapping to approximate detection behavior.

Exposes:
    classify(entry: dict) -> dict
        Returns: {"predicted_skill": str | None, "predicted_detect": bool}

Detection logic:
    - Scan user_message for trigger keywords from each pack's TRIGGERS list
    - Match = return the corresponding skill name + detected=true
    - No match = return None + detected=false
    - Context-aware filtering: if a keyword appears in a non-skill context
      (e.g. "部署这个变量是什么意思"), it should NOT trigger detection.
      This is approximated by checking for question/translation markers.
"""

from typing import Any

# ---------------------------------------------------------------------------
# TRIGGERS mapping — mirrors packs/core/petfish-companion-skill/.../catalog_query.py
# ---------------------------------------------------------------------------

TRIGGERS: dict[str, list[str]] = {
    "deploy": [
        "部署", "上线", "deploy", "docker", "服务器", "运维", "回滚",
        "health check", "systemctl", "nginx", "ci/cd", "ci-cd", "pipeline",
    ],
    "course": [
        "课程", "教学", "大纲", "课时", "模块", "学员", "教师",
        "实验", "QA", "QC", "发布", "讲义", "outline", "syllabus",
        "course outline",
    ],
    "petfish": [
        "说人话", "润色", "去AI味", "风格", "改写", "rewrite", "polish", "humanize",
    ],
    "ppt": [
        "PPT", "幻灯片", "演示", "slide", "deck", "presentation", "PPTX",
    ],
    "testdocs": [
        "测试用例", "test case", "测试矩阵", "文档", "README",
        "usage docs", "API docs",
    ],
    "calibrate": [
        "评审", "评价", "批判", "review", "critique", "feedback",
        "judgment", "decision", "evaluation", "校准", "迎合", "sycophancy",
        "方案评估", "可行性分析", "code review", "这个想法怎么样",
        "你觉得呢", "对吗", "是不是",
    ],
    "research": [
        "研究", "帮我研究", "仔细研究", "调研", "文献", "literature",
        "research", "investigate", "来源", "证据", "evidence",
        "综述", "论文", "学术", "academic", "citation",
        "source verification", "市场分析", "竞品分析", "论文方向", "规划方案",
    ],
    "context": [
        "话题", "上下文", "topic", "context", "污染", "继承", "隔离",
        "话题切换", "话题治理", "context package", "topic detect", "contamination",
    ],
    "trust": [
        "skill trust", "skill安全", "治理", "可信度", "trust scan",
        "governance", "risk score", "redline",
    ],
}

# Patterns that indicate the user is ASKING ABOUT a concept, not requesting an action
# When these are present alongside a trigger keyword, we should NOT fire.
CONTEXT_QUESTION_MARKERS = [
    "是什么意思", "是什么", "翻译", "translate", "解释一下",
    "define", "定义", "什么叫", "什么是",
]

# Compound words that contain skill keywords but are used in non-skill contexts.
# e.g. "课程表" (class schedule) contains "课程" but is not a course dev request.
NON_ACTION_COMPOUNDS = [
    "课程表", "考试", "课表",
]


def _is_context_question(msg: str) -> bool:
    """Check if the message is asking about a concept rather than requesting action."""
    msg_lower = msg.lower()
    for marker in CONTEXT_QUESTION_MARKERS:
        if marker.lower() in msg_lower:
            return True
    return False


def _is_non_action_context(msg: str) -> bool:
    """Check if the message uses trigger keywords in a non-actionable context."""
    msg_lower = msg.lower()
    for compound in NON_ACTION_COMPOUNDS:
        if compound.lower() in msg_lower:
            return True
    return False


def classify(entry: dict) -> dict[str, Any]:
    """Classify a user message for skill detection.

    Args:
        entry: Dict with keys 'user_message', 'expected_skill', 'expected_detect'

    Returns:
        dict with 'predicted_skill' and 'predicted_detect'
    """
    msg: str = entry.get("user_message", "")
    msg_lower = msg.lower()

    # If the message is a context question or non-action context, don't detect any skill
    if _is_context_question(msg) or _is_non_action_context(msg):
        return {"predicted_skill": None, "predicted_detect": False}

    # Check each pack's trigger keywords
    for skill, keywords in TRIGGERS.items():
        for kw in keywords:
            if kw.lower() in msg_lower:
                return {"predicted_skill": skill, "predicted_detect": True}

    # No skill detected
    return {"predicted_skill": None, "predicted_detect": False}
