#!/usr/bin/env python3
"""Gateway atom classifiers — self-contained classify functions for validators.

Shipped with the skill (no external dependencies on benchmarks/).
Each function mirrors the logic in benchmarks/scripts/modules/ but is independently
maintained to ensure validators work in any installation context.

Functions:
    classify_failure_signal(entry) -> {predicted_signal, predicted_detect}
    classify_topic(entry)          -> {predicted_relation, predicted_risk}
    classify_skill_sense(entry)    -> {predicted_skill, predicted_detect}
    TRIGGERS                       -> dict of pack keywords (for anti-sycophancy detection)
"""
import re
from typing import Any

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

TRIGGERS: dict[str, list[str]] = {
    "deploy": ["部署", "上线", "deploy", "docker", "服务器", "运维", "回滚", "health check", "systemctl", "nginx", "ci/cd", "ci-cd", "pipeline"],
    "course": ["课程", "教学", "大纲", "课时", "模块", "学员", "教师", "实验", "QA", "QC", "发布", "讲义", "outline", "syllabus", "course outline"],
    "petfish": ["说人话", "润色", "去AI味", "风格", "改写", "rewrite", "polish", "humanize"],
    "ppt": ["PPT", "幻灯片", "演示", "slide", "deck", "presentation", "PPTX"],
    "testdocs": ["测试用例", "test case", "测试矩阵", "文档", "README", "usage docs", "API docs"],
    "calibrate": ["评审", "评价", "批判", "review", "critique", "feedback", "judgment", "decision", "evaluation", "校准", "迎合", "sycophancy", "方案评估", "可行性分析", "code review", "这个想法怎么样", "你觉得呢", "对吗", "是不是", "好吗", "合理吗", "你觉得"],
    "research": ["研究", "帮我研究", "仔细研究", "调研", "文献", "literature", "research", "investigate", "来源", "证据", "evidence", "综述", "论文", "学术", "academic", "citation", "source verification", "市场分析", "竞品分析", "论文方向", "规划方案"],
    "context": ["话题", "上下文", "topic", "context", "污染", "继承", "隔离", "话题切换", "话题治理", "context package", "topic detect", "contamination"],
    "trust": ["skill trust", "skill安全", "治理", "可信度", "trust scan", "governance", "risk score", "redline"],
}

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
