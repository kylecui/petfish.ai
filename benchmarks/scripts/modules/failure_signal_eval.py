#!/usr/bin/env python3
"""
Failure Signal Detection Evaluation Module

Simulates the failure signal detection logic from catalog_query.py's
FAILURE_SIGNALS regex patterns.

Exposes:
    classify(entry: dict) -> dict
        Returns: {"predicted_signal": str | None, "predicted_detect": bool}

Detection logic:
    - Check for co-occurrence of failure keywords + domain keywords
    - Flexible word order (both "cannot open PDF" and "PDF cannot be opened")
    - Match = return the signal pack name + detected=true
    - No match = return None + detected=false
"""

import re
from typing import Any

# ---------------------------------------------------------------------------
# FAILURE_SIGNALS — keyword co-occurrence rules
# Each signal has: failure_words (negation/failure indicators) + domain_words
# A signal fires when BOTH a failure word AND a domain word are present.
# ---------------------------------------------------------------------------

FAILURE_WORDS = [
    "无法", "cannot", "can't", "unable to", "失败", "fail",
    "error", "错误", "不确定", "需要更多", "need more", "not supported",
    "corrupt", "tried to",
]

SIGNAL_RULES: list[dict[str, Any]] = [
    {
        "signal": "ppt",
        "domain_words": ["PDF", "PPTX", "PPT", "幻灯片", "presentation", "slide"],
        "failure_words": ["无法", "cannot", "can't", "unable to", "tried to",
                          "not supported", "corrupt", "失败", "fail", "error", "错误"],
        "extra_patterns": [
            re.compile(r"(open|read|parse|打开|读取|解析|access).*(PDF|PPTX|PPT|幻灯片)", re.IGNORECASE),
        ],
    },
    {
        "signal": "deploy",
        "domain_words": ["deploy", "部署", "Docker", "上线"],
        "failure_words": ["fail", "失败", "error", "错误"],
        "extra_patterns": [],
    },
    {
        "signal": "testdocs",
        "domain_words": ["测试用例", "test case", "test cases"],
        "failure_words": ["无法", "cannot", "can't", "unable to", "不确定",
                          "需要", "need more"],
        "extra_patterns": [],
    },
    {
        "signal": "research",
        "domain_words": ["来源", "evidence", "文献", "数据"],
        "failure_words": ["需要更多", "证据不足", "无法确认", "insufficient"],
        "extra_patterns": [],
    },
    {
        "signal": "context",
        "domain_words": ["上下文", "context", "topic"],
        "failure_words": ["混乱", "污染", "冲突", "drift"],
        "extra_patterns": [],
    },
]


def _has_any(text_lower: str, words: list[str]) -> bool:
    """Check if any keyword appears in text (case-insensitive)."""
    for w in words:
        if w.lower() in text_lower:
            return True
    return False


def classify(entry: dict) -> dict[str, Any]:
    """Classify previous assistant output for failure signals.

    Args:
        entry: Dict with keys 'previous_assistant_output', 'expected_signal',
               'expected_detect'

    Returns:
        dict with 'predicted_signal' and 'predicted_detect'
    """
    text: str = entry.get("previous_assistant_output", "")
    text_lower = text.lower()

    for rule in SIGNAL_RULES:
        # Check domain co-occurrence with failure
        has_domain = _has_any(text_lower, rule["domain_words"])
        has_failure = _has_any(text_lower, rule["failure_words"])

        if has_domain and has_failure:
            return {"predicted_signal": rule["signal"], "predicted_detect": True}

        # Check extra patterns (regex-based)
        for pattern in rule.get("extra_patterns", []):
            if pattern.search(text):
                return {"predicted_signal": rule["signal"], "predicted_detect": True}

    return {"predicted_signal": None, "predicted_detect": False}
