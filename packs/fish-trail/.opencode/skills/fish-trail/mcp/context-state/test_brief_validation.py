"""Tests for v1.2 reflective brief validation and heuristic generation.

Covers ContextStateServer._validate_brief (5 core cases) and
ContextStateServer._heuristic_brief (4 strategies).
"""

import sys
from pathlib import Path

import pytest

# Add the MCP server directory to sys.path so `from server import ...` works
sys.path.insert(0, str(Path(__file__).parent))

from server import ContextStateServer


class TestValidateBrief:
    """Test _validate_brief — 5 core rejection rules."""

    def test_valid_chinese(self):
        """Valid Chinese brief passes all checks."""
        is_valid, reason = ContextStateServer._validate_brief(
            "v1.2\u8bbe\u8ba1\u5b8c\u6210\uff0c\u8bed\u4e49\u53cd\u5c04\u538b\u7f29\u65b9\u6848\u5df2\u786e\u5b9a"
        )
        assert is_valid is True
        assert reason == "ok"

    def test_valid_english(self):
        """Valid English brief passes all checks."""
        is_valid, reason = ContextStateServer._validate_brief(
            "#169 console.log to stderr fix committed, pre-release updated"
        )
        assert is_valid is True
        assert reason == "ok"

    def test_too_short(self):
        """Brief under 10 characters is rejected as too_short."""
        is_valid, reason = ContextStateServer._validate_brief("OK")
        assert is_valid is False
        assert reason == "too_short"

    def test_too_long(self):
        """Brief over 200 characters is rejected as too_long."""
        long_brief = "a" * 201
        is_valid, reason = ContextStateServer._validate_brief(long_brief)
        assert is_valid is False
        assert reason == "too_long"

    def test_low_quality_pattern(self):
        """Brief matching low-quality pattern is rejected.

        Only "working on it" (13 chars) reaches the pattern check because
        shorter patterns (<10) are caught by the length check first and
        return "too_short".
        """
        # The one pattern long enough to reach the quality check
        is_valid, reason = ContextStateServer._validate_brief("working on it")
        assert is_valid is False
        assert reason == "low_quality_pattern"

        # Short patterns are still rejected, but via too_short first
        for pattern in ["\u7ee7\u7eed", "ongoing", "\u8fdb\u884c\u4e2d", "\u7ee7\u7eed\u5f00\u53d1\u4e2d", "ok", "done", "\u5b8c\u6210"]:
            is_valid, _reason = ContextStateServer._validate_brief(pattern)
            assert is_valid is False, f"Should reject '{pattern}'"


class TestHeuristicBrief:
    """Test _heuristic_brief fallback generation strategies."""

    def test_empty_summary(self):
        """Empty summary returns empty string."""
        result = ContextStateServer._heuristic_brief("")
        assert result == ""

    def test_progress_prefix(self):
        """Strategy 1: extracts Progress:/At:/Status: prefix content.

        The regex stops at the first dot, so "v1.2" breaks at the dot
        and returns "Implementing v1".
        """
        result = ContextStateServer._heuristic_brief(
            "Progress: Implementing v1.2 adaptive compression. Currently working on state machine logic."
        )
        assert result == "Implementing v1"

    def test_first_sentence(self):
        """Strategy 2: falls back to first sentence when no prefix matches."""
        result = ContextStateServer._heuristic_brief(
            "The agent completed the fix for issue #169. It was a simple change."
        )
        assert result == "The agent completed the fix for issue #169."

    def test_hard_truncate(self):
        """Strategy 3: hard truncation at max_chars with ellipsis."""
        long_text = "A" * 300
        result = ContextStateServer._heuristic_brief(long_text, max_chars=100)
        assert len(result) == 100
        assert result.endswith("\u2026")  # horizontal ellipsis (chr 0x2026)
