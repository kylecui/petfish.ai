#!/usr/bin/env python3
"""Gateway atom classifiers — self-contained classify functions for validators.

Shipped with the skill (no external dependencies on benchmarks/).
Each function mirrors the logic in benchmarks/scripts/modules/ but is independently
maintained to ensure validators work in any installation context.

Functions:
    classify_failure_signal(entry) -> {predicted_signal, predicted_detect}
    classify_topic(entry)          -> {predicted_relation, predicted_risk}
    classify_skill_sense(entry)    -> {predicted_skill, predicted_detect}
    TRIGGERS                       -> pack keywords, imported from catalog_query.py
                                      (single source of truth; was a drifted local copy)
    domains_from_index(index)      -> extract domains map from skill-index.json content
"""
import re
from typing import Any

try:
    from catalog_query import TRIGGERS as _CATALOG_TRIGGERS
except Exception:  # pragma: no cover — catalog_query sits in the same scripts/ dir
    _CATALOG_TRIGGERS = {}

# ===========================================================================
# 1. Failure Signal Classifier (mirrors failure_signal_eval.py)
# ===========================================================================

def _has_any(text_lower: str, words: list[str]) -> bool:
    for w in words:
        if w.lower() in text_lower:
            return True
    return False

_SIGNAL_RULES = [
    {"signal": "ppt", "domain_words": ["PDF", "PPTX", "PPT", "幻灯片", "presentation", "slide"],
     "failure_words": ["无法", "cannot", "can't", "unable to", "tried to", "not supported", "corrupt", "失败", "fail", "error", "错误"],
     "extra_patterns": [re.compile(r"(open|read|parse|打开|读取|解析|access).*(PDF|PPTX|PPT|幻灯片)", re.IGNORECASE)]},
    {"signal": "deploy", "domain_words": ["deploy", "部署", "Docker", "上线"],
     "failure_words": ["fail", "失败", "error", "错误"], "extra_patterns": []},
    {"signal": "testdocs", "domain_words": ["测试用例", "test case", "test cases"],
     "failure_words": ["无法", "cannot", "can't", "unable to", "不确定", "需要", "need more"], "extra_patterns": []},
    {"signal": "research", "domain_words": ["来源", "evidence", "文献", "数据"],
     "failure_words": ["需要更多", "证据不足", "无法确认", "insufficient"], "extra_patterns": []},
    {"signal": "context", "domain_words": ["上下文", "context", "topic"],
     "failure_words": ["混乱", "污染", "冲突", "drift"], "extra_patterns": []},
]

def classify_failure_signal(entry: dict) -> dict[str, Any]:
    text = entry.get("previous_assistant_output", "")
    text_lower = text.lower()
    for rule in _SIGNAL_RULES:
        if _has_any(text_lower, rule["domain_words"]) and _has_any(text_lower, rule["failure_words"]):
            return {"predicted_signal": rule["signal"], "predicted_detect": True}
        for pattern in rule.get("extra_patterns", []):
            if pattern.search(text):
                return {"predicted_signal": rule["signal"], "predicted_detect": True}
    return {"predicted_signal": None, "predicted_detect": False}


# ===========================================================================
# 2. Topic Drift Classifier (mirrors gateway_eval.py)
# ===========================================================================

_RESET_KW = ["清空上下文", "reset the context", "重新开始", "start fresh", "重置", "reset context"]
_ARCHIVE_KW = ["归档", "archive"]
_SWITCH_KW = ["换个话题", "不说这个了", "话题转到", "先不管", "切换一下", "换个方向", "turn to", "switch to", "instead", "先不说", "不谈这个"]
_FORK_KW = ["基础上", "延伸出去", "扩展", "fork from", "基于这个", "从这个", "在此基础上"]
_CONTINUE_KW = ["继续", "接着", "接着上面的", "继续改", "OK继续", "continue with", "go on", "carry on", "接着刚才"]

def classify_topic(entry: dict) -> dict[str, Any]:
    msg = entry.get("user_message", "")
    msg_lower = msg.lower()
    for kw in _RESET_KW:
        if kw.lower() in msg_lower: return {"predicted_relation": "reset", "predicted_risk": "low"}
    for kw in _ARCHIVE_KW:
        if kw.lower() in msg_lower: return {"predicted_relation": "archive", "predicted_risk": "low"}
    for kw in _SWITCH_KW:
        if kw.lower() in msg_lower: return {"predicted_relation": "switch", "predicted_risk": "high"}
    for kw in _FORK_KW:
        if kw.lower() in msg_lower: return {"predicted_relation": "fork", "predicted_risk": "medium"}
    for kw in _CONTINUE_KW:
        if kw.lower() in msg_lower: return {"predicted_relation": "continue", "predicted_risk": "low"}
    return {"predicted_relation": "continue", "predicted_risk": "low"}


# ===========================================================================
# 3. Skill Sense Classifier (mirrors skill_sense_eval.py)
# ===========================================================================

# Single source of truth: catalog_query.py TRIGGERS (sibling import above).
# Key drift is a defect — reconcile catalog_query.py, not this file.
TRIGGERS: dict[str, list[str]] = _CATALOG_TRIGGERS

_CONTEXT_QUESTION_MARKERS = ["是什么意思", "是什么", "翻译", "translate", "解释一下", "define", "定义", "什么叫", "什么是"]
_NON_ACTION_COMPOUNDS = ["课程表", "考试", "课表"]

def classify_skill_sense(entry: dict) -> dict[str, Any]:
    msg = entry.get("user_message", "")
    msg_lower = msg.lower()
    if any(m.lower() in msg_lower for m in _CONTEXT_QUESTION_MARKERS):
        return {"predicted_skill": None, "predicted_detect": False}
    if any(c.lower() in msg_lower for c in _NON_ACTION_COMPOUNDS):
        return {"predicted_skill": None, "predicted_detect": False}
    for skill, keywords in TRIGGERS.items():
        for kw in keywords:
            if kw.lower() in msg_lower:
                return {"predicted_skill": skill, "predicted_detect": True}
    return {"predicted_skill": None, "predicted_detect": False}


def domains_from_index(index: dict) -> dict[str, list[str]]:
    """Extract a domains map ({alias: keywords}) from skill-index.json content.

    Mirrors companion-gateway.ts loadSkillDomains parsing: prefers the
    top-level "domains" map; falls back to aggregating per-skill triggers
    grouped by "domain"; returns {} for legacy formats (silent degradation).
    """
    out: dict[str, list[str]] = {}
    domains = index.get("domains")
    if isinstance(domains, dict):
        for alias, info in domains.items():
            kws = info.get("keywords") if isinstance(info, dict) else None
            if isinstance(kws, list) and kws:
                out[alias] = list(kws)
        return out
    skills = index.get("skills")
    if isinstance(skills, list):
        for s in skills:
            if (
                isinstance(s, dict)
                and s.get("domain")
                and isinstance(s.get("triggers"), list)
                and s["triggers"]
            ):
                out[s["domain"]] = out.get(s["domain"], []) + list(s["triggers"])
    return out
