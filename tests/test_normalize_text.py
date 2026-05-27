"""Unit tests for normalize_text.py — Petfish text normalizer."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

# Load normalize_text.py as a module
_SCRIPT = Path(__file__).resolve().parents[1] / (
    "packs/optional/petfish-style-skill/.opencode/skills/fish-style/scripts/normalize_text.py"
)
_spec = importlib.util.spec_from_file_location("normalize_text", _SCRIPT)
nt = importlib.util.module_from_spec(_spec)
sys.modules["normalize_text"] = nt
_spec.loader.exec_module(nt)


# ---------------------------------------------------------------------------
# normalize_slash_groups
# ---------------------------------------------------------------------------


class TestNormalizeSlashGroups:
    def test_collapse_spaced_slashes(self):
        assert "API/CLI/SDK" in nt.normalize_slash_groups("API / CLI / SDK")

    def test_collapse_with_cjk_context(self):
        result = nt.normalize_slash_groups("根据 API / CLI / SDK / 配置文件生成文档")
        assert "API/CLI/SDK/配置文件" in result

    def test_cjk_slash_en(self):
        result = nt.normalize_slash_groups("配置文件 / API")
        assert "配置文件/API" in result

    def test_en_slash_cjk(self):
        result = nt.normalize_slash_groups("SDK / 配置文件")
        assert "SDK/配置文件" in result

    def test_ci_cd(self):
        result = nt.normalize_slash_groups("通过 CI / CD 流水线部署")
        assert "CI/CD" in result

    def test_already_compact(self):
        text = "API/CLI/SDK"
        assert nt.normalize_slash_groups(text) == text


# ---------------------------------------------------------------------------
# normalize_zh_en_spacing
# ---------------------------------------------------------------------------


class TestNormalizeZhEnSpacing:
    def test_removes_space_zh_en(self):
        result = nt.normalize_zh_en_spacing("使用 Git 提交")
        assert "使用Git提交" in result

    def test_preserves_code_fence_marker(self):
        # ``` lines are preserved; inner content lines get normalized
        # (per-line check, not block-level tracking)
        text = "```\n使用 Git 提交\n```"
        result = nt.normalize_zh_en_spacing(text)
        assert result.startswith("```")
        assert result.endswith("```")

    def test_preserves_indented_code(self):
        # 4-space indented lines are preserved (checks raw line, not stripped)
        text = "    使用 Git 提交"
        result = nt.normalize_zh_en_spacing(text)
        assert "使用 Git 提交" in result

    def test_number_spacing(self):
        result = nt.normalize_zh_en_spacing("超过 100 个")
        assert "超过100个" in result

    def test_percent_spacing(self):
        result = nt.normalize_zh_en_spacing("达到 99.9% 的")
        assert "99.9%" in result
        assert " 99.9%" not in result


# ---------------------------------------------------------------------------
# normalize_punctuation
# ---------------------------------------------------------------------------


class TestNormalizePunctuation:
    def test_collapse_spaces(self):
        assert "a b" == nt.normalize_punctuation("a  b").strip()

    def test_space_before_chinese_punct(self):
        result = nt.normalize_punctuation("文本 ，继续")
        assert "文本，继续" in result

    def test_space_inside_quotes(self):
        result = nt.normalize_punctuation("\u201c 内容 \u201d")
        assert "\u201c内容\u201d" in result

    def test_space_inside_parens(self):
        result = nt.normalize_punctuation("\uff08 内容 \uff09")
        assert "\uff08内容\uff09" in result


# ---------------------------------------------------------------------------
# normalize (full pipeline)
# ---------------------------------------------------------------------------


class TestNormalize:
    def test_full_pipeline(self):
        text = "使用 API / CLI / SDK 提交 ，完成。"
        result = nt.normalize(text)
        # Spaces around slashes should be gone
        assert "/" in result
        assert " / " not in result
        # Space before comma should be gone
        assert " ，" not in result

    def test_idempotent(self):
        text = "使用API/CLI/SDK提交，完成。"
        assert nt.normalize(nt.normalize(text)) == nt.normalize(text)

    def test_empty_string(self):
        assert nt.normalize("") == ""

    def test_pure_english(self):
        text = "This is pure English text."
        result = nt.normalize(text)
        assert "This is pure English text." == result.strip()

    def test_multiline_preserves_newlines(self):
        text = "第一行。\n\n第二行。"
        result = nt.normalize(text)
        assert "\n\n" in result
