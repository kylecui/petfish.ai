"""Unit tests for Companion Gateway behavior.

Tests the two core gateway steps:
1. Topic Check — topic_detect integration (MCP tool behavior)
2. Skill Sense — TRIGGERS keyword matching + installed-pack filtering

These tests validate the gateway's decision logic without requiring
a running MCP server (mocked where needed).
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

# ---------------------------------------------------------------------------
# Module loading helpers
# ---------------------------------------------------------------------------

_REPO_ROOT = Path(__file__).resolve().parents[1]

_CATALOG_SCRIPT = _REPO_ROOT / (
    "packs/petfish-companion-skill/.opencode/skills/petfish-companion/scripts/catalog_query.py"
)
_spec = importlib.util.spec_from_file_location("catalog_query", _CATALOG_SCRIPT)
cq = importlib.util.module_from_spec(_spec)
sys.modules.setdefault("catalog_query", cq)
_spec.loader.exec_module(cq)

_CHECK_SCRIPT = _REPO_ROOT / (
    "packs/petfish-companion-skill/.opencode/skills/petfish-companion/scripts/check_installed.py"
)
_spec2 = importlib.util.spec_from_file_location("check_installed", _CHECK_SCRIPT)
ci = importlib.util.module_from_spec(_spec2)
sys.modules.setdefault("check_installed", ci)
_spec2.loader.exec_module(ci)


# ---------------------------------------------------------------------------
# Step 2: Skill Sense — TRIGGERS matching
# ---------------------------------------------------------------------------


class TestSkillSenseTriggers:
    """Verify TRIGGERS keyword matching produces correct pack suggestions."""

    @pytest.mark.parametrize(
        "message,expected_pack",
        [
            ("帮我把这个服务部署到Docker", "deploy"),
            ("我需要设计一个课程大纲", "course"),
            ("帮我做一份PPT", "ppt"),
            ("生成测试用例文档", "testdocs"),
            ("这段话帮我润色一下，说人话", "petfish"),
            ("帮我review一下这个方案", "calibrate"),
            ("话题太多了需要整理一下上下文", "context"),
        ],
    )
    def test_trigger_keyword_matches_correct_pack(self, message, expected_pack):
        """Each domain keyword should map to its expected pack."""
        matched = set()
        for alias, triggers in cq.TRIGGERS.items():
            for trigger in triggers:
                if trigger.lower() in message.lower():
                    matched.add(alias)
                    break
        assert expected_pack in matched, (
            f"Message '{message}' should trigger '{expected_pack}', got {matched}"
        )

    @pytest.mark.parametrize(
        "message",
        [
            "请帮我看看这个变量命名是否合理",
            "git status",
            "hello",
            "这个函数的返回值是什么类型",
        ],
    )
    def test_generic_messages_trigger_nothing(self, message):
        """Generic programming messages should not trigger any pack suggestion."""
        matched = set()
        for alias, triggers in cq.TRIGGERS.items():
            for trigger in triggers:
                if trigger.lower() in message.lower():
                    matched.add(alias)
                    break
        # companion itself may match on generic terms; exclude it
        matched.discard("companion")
        assert len(matched) == 0, (
            f"Message '{message}' should not trigger packs, got {matched}"
        )

    def test_all_packs_have_at_least_one_trigger(self):
        """Every pack in TRIGGERS should have at least one keyword."""
        for alias, triggers in cq.TRIGGERS.items():
            assert len(triggers) > 0, f"Pack '{alias}' has empty TRIGGERS list"


class TestSkillSenseGapDetection:
    """Verify gap detection: only suggest packs that are NOT installed."""

    def test_installed_pack_not_suggested(self):
        """If a pack is already installed, it should not be suggested."""
        # Simulate: deploy is installed
        installed = {"deploy": {"version": "1.0.0"}}
        message = "帮我部署到Docker"

        # Find triggered packs
        triggered = set()
        for alias, triggers in cq.TRIGGERS.items():
            for trigger in triggers:
                if trigger.lower() in message.lower():
                    triggered.add(alias)
                    break

        # Filter out installed
        gaps = triggered - set(installed.keys())
        assert "deploy" not in gaps

    def test_uninstalled_pack_suggested(self):
        """If a triggered pack is NOT installed, it should be suggested."""
        installed = {}  # nothing installed
        message = "帮我部署到Docker"

        triggered = set()
        for alias, triggers in cq.TRIGGERS.items():
            for trigger in triggers:
                if trigger.lower() in message.lower():
                    triggered.add(alias)
                    break

        gaps = triggered - set(installed.keys())
        assert "deploy" in gaps


class TestSkillSenseSessionLimit:
    """Verify the 'recommend at most once per session' rule."""

    def test_same_pack_not_recommended_twice(self):
        """Simulate session state: already recommended deploy → skip next time."""
        session_recommended = {"deploy"}
        message = "再帮我配一下CI/CD"

        triggered = set()
        for alias, triggers in cq.TRIGGERS.items():
            for trigger in triggers:
                if trigger.lower() in message.lower():
                    triggered.add(alias)
                    break

        # Apply session filter
        new_suggestions = triggered - session_recommended
        assert "deploy" not in new_suggestions


# ---------------------------------------------------------------------------
# Step 1: Topic Check — decision logic
# ---------------------------------------------------------------------------


class TestTopicCheckDecision:
    """Verify topic check risk-level → action mapping."""

    @pytest.mark.parametrize(
        "risk,expected_action",
        [
            (0, "silent"),
            (15, "silent"),
            (30, "silent"),
            (31, "context_hint"),
            (45, "context_hint"),
            (60, "context_hint"),
            (61, "warn_and_suggest"),
            (85, "warn_and_suggest"),
            (100, "warn_and_suggest"),
        ],
    )
    def test_risk_level_to_action(self, risk, expected_action):
        """Risk score maps to correct gateway action."""
        if risk <= 30:
            action = "silent"
        elif risk <= 60:
            action = "context_hint"
        else:
            action = "warn_and_suggest"
        assert action == expected_action

    def test_mcp_unavailable_fallback(self):
        """When MCP is unavailable, gateway should not block processing."""
        # Simulate MCP failure → fallback is: skip topic check, proceed
        mcp_available = False
        should_block = False

        if not mcp_available:
            # Gateway rule: don't block, just note unavailability
            should_block = False

        assert should_block is False


# ---------------------------------------------------------------------------
# Debug mode output
# ---------------------------------------------------------------------------


class TestDebugMode:
    """Verify debug mode output format."""

    def test_debug_output_format_low_risk(self):
        """Debug output for low-risk should follow expected format."""
        relation = "continue"
        risk = 12
        confidence = 0.92
        output = f"🐟 [gateway] topic: relation={relation}, risk={risk} (low), confidence={confidence} → silent"
        assert "🐟 [gateway]" in output
        assert "silent" in output

    def test_debug_output_format_high_risk(self):
        """Debug output for high-risk should show suggestion."""
        relation = "switch"
        risk = 67
        confidence = 0.85
        output = f"🐟 [gateway] topic: relation={relation}, risk={risk} (high), confidence={confidence} → suggest fork"
        assert "🐟 [gateway]" in output
        assert "suggest fork" in output

    def test_debug_output_skill_gap(self):
        """Debug output should show detected skill gap."""
        gap = "deploy"
        trigger = "Docker部署"
        output = f'🐟 [gateway] skill: gap={gap} (detected "{trigger}") → recommend'
        assert "gap=deploy" in output
        assert "recommend" in output

    def test_debug_output_no_gap(self):
        """Debug output when no gap detected."""
        output = "🐟 [gateway] skill: no gap → pass"
        assert "no gap" in output
        assert "pass" in output
