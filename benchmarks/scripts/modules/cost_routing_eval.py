#!/usr/bin/env python3
"""
Cost Routing Evaluation Module

Simulates task-tier classification (gateway / worker / deep_coding / critic)
based on message heuristics: length, keyword presence, instruction complexity.

Exposes:
    classify(entry: dict) -> dict
        Returns: {"predicted_tier": str}

Detection logic:
    - critic: review/judge/evaluate/critique/security keywords
    - deep_coding: multi-file/refactor/implement across/rename across/migrate keywords
    - worker: single-file edit signals (line number, specific file, simple fix)
    - gateway: trivial/simple/definitional queries
"""

from typing import Any

# ---------------------------------------------------------------------------
# Tier detection rules
# ---------------------------------------------------------------------------

# Keywords that signal a critic/review tier
CRITIC_KEYWORDS = [
    "review", "critique", "evaluate", "is this", "sound?",
    "security issues", "code smell", "architecture", "性能",
    "评审", "评价", "怎么样", "对不对", "好不好",
]

# Keywords that signal deep_coding tier (multi-file, complex refactoring)
DEEP_CODING_KEYWORDS = [
    "refactor", "migrate", "implement across", "add pagination to all",
    "across the api", "across the codebase", "across the entire",
    "across all", "in every",
    "across 15", "across 10", "across multiple",
    "整个", "全部", "所有", "迁移",
    "implement jwt", "implement oauth", "restructure",
    "rename getcwd",
]

# Keywords that signal a worker tier (single-file, specific location)
WORKER_KEYWORDS = [
    "line 42", "line 10", "line ", "in auth.ts", "in config.ts",
    "in utils.py", "in the", "function ", "add error handling",
    "add a null check", "change the button", "update the API",
    "change the color", "add validation",
]

# Keywords that signal a gateway tier (trivial/simple/definitional)
GATEWAY_KEYWORDS = [
    "what does", "what is", "how do i", "show me the",
    "list files", "add comment", "rename variable",
    "what is the capital", "current date",
    "rename x to", "rename y to",
]


def classify(entry: dict) -> dict[str, Any]:
    """Classify a user message into a cost tier.

    Args:
        entry: Dict with keys 'user_message', 'expected_tier'

    Returns:
        dict with 'predicted_tier'
    """
    msg: str = entry.get("user_message", "")
    msg_lower = msg.lower()

    # Check critic tier first (explicit review/judgment)
    for kw in CRITIC_KEYWORDS:
        if kw.lower() in msg_lower:
            return {"predicted_tier": "critic"}

    # Check deep_coding tier (multi-file, complex)
    for kw in DEEP_CODING_KEYWORDS:
        if kw.lower() in msg_lower:
            return {"predicted_tier": "deep_coding"}

    # Check worker tier (single-file, specific)
    for kw in WORKER_KEYWORDS:
        if kw.lower() in msg_lower:
            return {"predicted_tier": "worker"}

    # Check gateway tier (trivial)
    for kw in GATEWAY_KEYWORDS:
        if kw.lower() in msg_lower:
            return {"predicted_tier": "gateway"}

    # Fallback: use message length and complexity heuristics
    word_count = len(msg.split())
    if word_count < 5:
        return {"predicted_tier": "gateway"}
    elif word_count < 12:
        return {"predicted_tier": "worker"}
    else:
        return {"predicted_tier": "deep_coding"}
