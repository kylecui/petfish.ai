#!/usr/bin/env python3
"""
Gateway Topic Drift Evaluation Module

Simulates topic_detect classification using keyword-based heuristics.
Since eval cannot call the actual topic_detect MCP, this module approximates
the detection logic with keyword patterns that mirror the MCP's behavior.

Exposes:
    classify(entry: dict) -> dict
        Returns: {"predicted_relation": str, "predicted_risk": str}

Detection logic:
    - Archive/reset keywords → archive or reset, risk=low
    - Switch keywords (换话题, switch, 不说这个了) → switch, risk=high
    - Fork keywords (基础上, 延伸, 扩展, fork) → fork, risk=medium
    - Continue keywords (继续, 接着, 接着上面的, continue) → continue, risk=low
    - Default → continue, risk=low
"""

from typing import Any

# ---------------------------------------------------------------------------
# Keyword patterns for each relation type
# ---------------------------------------------------------------------------

RESET_KEYWORDS = [
    "清空上下文", "reset the context", "重新开始", "start fresh",
    "重置", "reset context",
]

ARCHIVE_KEYWORDS = [
    "归档", "archive",
]

SWITCH_KEYWORDS = [
    "换个话题", "不说这个了", "话题转到", "先不管",
    "切换一下", "换个方向", "turn to", "switch to",
    "instead", "先不说", "不谈这个",
]

FORK_KEYWORDS = [
    "基础上", "延伸出去", "扩展", "fork from",
    "基于这个", "从这个", "在此基础上",
]

CONTINUE_KEYWORDS = [
    "继续", "接着", "接着上面的", "继续改", "OK继续",
    "continue with", "go on", "carry on", "接着刚才",
]


def classify(entry: dict) -> dict[str, Any]:
    """Classify a user message by relation and risk level.

    Args:
        entry: Dict with keys 'user_message'

    Returns:
        dict with 'predicted_relation' and 'predicted_risk'
    """
    msg: str = entry.get("user_message", "")
    msg_lower = msg.lower()

    # Check for reset first (strongest signal)
    for kw in RESET_KEYWORDS:
        if kw.lower() in msg_lower:
            return {"predicted_relation": "reset", "predicted_risk": "low"}

    # Check for archive
    for kw in ARCHIVE_KEYWORDS:
        if kw.lower() in msg_lower:
            return {"predicted_relation": "archive", "predicted_risk": "low"}

    # Check for switch
    for kw in SWITCH_KEYWORDS:
        if kw.lower() in msg_lower:
            return {"predicted_relation": "switch", "predicted_risk": "high"}

    # Check for fork
    for kw in FORK_KEYWORDS:
        if kw.lower() in msg_lower:
            return {"predicted_relation": "fork", "predicted_risk": "medium"}

    # Check for continue
    for kw in CONTINUE_KEYWORDS:
        if kw.lower() in msg_lower:
            return {"predicted_relation": "continue", "predicted_risk": "low"}

    # Default: assume continue
    return {"predicted_relation": "continue", "predicted_risk": "low"}
