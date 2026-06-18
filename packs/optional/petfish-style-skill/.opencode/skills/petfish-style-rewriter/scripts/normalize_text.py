#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = []
# ///
"""Normalize Petfish-style Chinese-English technical writing.

Handles:
- Heading spacing normalization (section numbers, Chinese ordinals, fullwidth spaces)
- Punctuation cleanup
- Chinese-English compact spacing

Usage:
  uv run scripts/normalize_text.py --text "接入层支持 Webhook 挂载。"
  uv run scripts/normalize_text.py --file input.md --output output.md
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

CJK = r"\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff"

# English token: letters/digits/underscore/hyphen/dot but NOT slash (slash handled separately)
EN_TOKEN = r"[A-Za-z][A-Za-z0-9_.*+-]*"
# Backtick-wrapped code identifiers: `execute_change`, `action`, `api_key`, etc.
BT_TOKEN = r"`[^`]+`"


def normalize_slash_groups(text: str) -> str:
    """Collapse spaced slash-separated English terms adjacent to Chinese.

    Handles patterns like:
      "根据 API / CLI / SDK / 配置文件生成文档"
      → "根据API/CLI/SDK/配置文件生成文档"

      "支持 HTTP / HTTPS / WebSocket 协议"
      → "支持HTTP/HTTPS/WebSocket协议"

      "通过 CI / CD 流水线部署"
      → "通过CI/CD流水线部署"
    """
    # Step 1: Collapse "EN / EN / EN" → "EN/EN/EN" (remove spaces around slashes between English tokens)
    # Use a broader token that includes already-collapsed slashes for iterative merging
    EN_SLASH_TOKEN = rf"(?:{EN_TOKEN})(?:/{EN_TOKEN})*"
    prev = None
    while prev != text:
        prev = text
        text = re.sub(
            rf"({EN_SLASH_TOKEN})\s*/\s*({EN_TOKEN})",
            r"\1/\2",
            text,
        )

    # Step 2: Collapse slash between EN-slash-group and CJK: "SDK / 配置文件" → "SDK/配置文件"
    EN_SLASH_GROUP = rf"(?:{EN_TOKEN})(?:/{EN_TOKEN})*"
    text = re.sub(
        rf"({EN_SLASH_GROUP})\s*/\s*([{CJK}])",
        r"\1/\2",
        text,
    )
    # And CJK / EN: "配置文件 / API" → "配置文件/API"
    text = re.sub(
        rf"([{CJK}])\s*/\s*({EN_SLASH_GROUP})",
        r"\1/\2",
        text,
    )

    # Step 3: Remove space between CJK and adjacent EN/slash-group, and vice versa
    # CJK + space(s) + EN-slash-group
    text = re.sub(
        rf"([{CJK}])\s+((?:{EN_TOKEN})(?:/{EN_TOKEN})*)",
        r"\1\2",
        text,
    )
    # EN-slash-group + space(s) + CJK
    text = re.sub(
        rf"((?:{EN_TOKEN})(?:/{EN_TOKEN})*)\s+([{CJK}])",
        r"\1\2",
        text,
    )
    return text


def normalize_zh_en_spacing(text: str) -> str:
    """Remove unnecessary spaces between Chinese and English technical terms."""
    # Process line by line to preserve markdown structure
    lines = text.split("\n")
    result_lines = []
    for line in lines:
        # Skip code blocks and markdown headings with only English
        stripped = line.strip()
        if stripped.startswith("```") or line.startswith("    "):
            result_lines.append(line)
            continue

        # Apply slash group normalization first (before general CJK-EN rules)
        line = normalize_slash_groups(line)

        # General: Chinese + spaces + English token → compact
        line = re.sub(rf"([{CJK}])\s+({EN_TOKEN})", r"\1\2", line)
        # General: English token + spaces + Chinese → compact
        line = re.sub(rf"({EN_TOKEN})\s+([{CJK}])", r"\1\2", line)
        # Backtick: Chinese + spaces + backtick token → compact
        line = re.sub(rf"([{CJK}])\s+({BT_TOKEN})", r"\1\2", line)
        # Backtick: backtick token + spaces + Chinese → compact
        line = re.sub(rf"({BT_TOKEN})\s+([{CJK}])", r"\1\2", line)
        # Chinese + spaces + number + common unit/percent → compact
        line = re.sub(rf"([{CJK}])\s+(\d+(?:\.\d+)?%?)", r"\1\2", line)
        line = re.sub(rf"(\d+(?:\.\d+)?)\s+([{CJK}])", r"\1\2", line)

        result_lines.append(line)

    return "\n".join(result_lines)


def normalize_punctuation(text: str) -> str:
    """Apply conservative punctuation and whitespace cleanup."""
    # Collapse repeated spaces but preserve newlines and indentation roughly.
    text = re.sub(r"[ \t]+", " ", text)
    # Remove spaces before Chinese punctuation.
    text = re.sub(r"\s+([，。；：！？、])", r"\1", text)
    # Remove spaces after opening Chinese quotation/bracket and before closing ones.
    text = re.sub("([\u201c\u2018\uff08\u300a\u3010])\\s+", r"\1", text)
    text = re.sub("\\s+([\u201d\u2019\uff09\u300b\u3011])", r"\1", text)
    return text


def normalize_headings(text: str) -> str:
    """Fix heading spacing issues in Markdown files.

    Handles:
    1. Number+Chinese without space: "### 1.1威胁数据" → "### 1.1 威胁数据"
    2. Chinese ordinal+text without space: "## 第一部分AI基础" → "## 第一部分 AI基础"
    3. Fullwidth space U+3000 in headings → halfwidth space
    """

    # Fix: section number (1.1, 1.1.1, etc.) + Chinese/paren without space
    text = re.sub(
        rf'^(#{{2,4}}\s+\d+(?:\.\d+)+)([\u4e00-\u9fff(（])',
        r'\1 \2',
        text,
        flags=re.MULTILINE,
    )

    # Fix: Chinese ordinal (第X节/部分/章/篇/模块/单元) + text without space
    text = re.sub(
        rf'^(#{{2,4}}\s+(?:第[一二三四五六七八九十百零]+(?:节|部分|章|篇|模块|单元)))([\u4e00-\u9fffA-Za-z0-9(（])',
        r'\1 \2',
        text,
        flags=re.MULTILINE,
    )

    # Fix: fullwidth space U+3000 → halfwidth in headings
    def replace_fullwidth(match: re.Match) -> str:
        return match.group(0).replace('\u3000', ' ')
    text = re.sub(r'^#{1,6}\s+.*', replace_fullwidth, text, flags=re.MULTILINE)

    return text


def normalize(text: str) -> str:
    text = normalize_punctuation(text)
    text = normalize_zh_en_spacing(text)
    # Headings last: section number + Chinese spacing is a specific override
    # that must come after the general zh-en spacing rule (which would
    # otherwise collapse the intentional space after section numbers).
    text = normalize_headings(text)
    return text


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Normalize Petfish-style Chinese-English technical text."
    )
    src = parser.add_mutually_exclusive_group(required=True)
    src.add_argument("--text", help="Input text to normalize")
    src.add_argument("--file", help="Input file path")
    parser.add_argument("--output", help="Optional output file path")
    args = parser.parse_args()

    if args.file:
        content = Path(args.file).read_text(encoding="utf-8")
    else:
        content = args.text

    result = normalize(content)

    if args.output:
        Path(args.output).write_text(result, encoding="utf-8")
    else:
        print(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
