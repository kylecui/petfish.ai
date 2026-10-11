#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = []
# ///
"""Classify an OpenCode (oh-my-opencode) crash log snippet into the 4-class
taxonomy (pack: opencode-resilience-pack, skill: opencode-crash-taxonomy).

Classes:
  1  model resolution failure     (ProviderModelNotFoundError / Model not found)
  2  agent identity resolution    (Die(UnknownError: UnknownError) @ createUserMessage)
  3  storage layer failure        (SqliteError / disk is full / locked)
  4  quota / rate limit           (已达到 N 小时的使用上限 / HTTP 429 / bare UnknownError)

Precedence when several classes match: 3 > 2 > 1 > 4 (storage first — a full
disk or locked DB pollutes every other signal). Mixed matches are reported in
the "note" field.

Usage:
  uv run classify_crash.py <logfile>
  uv run classify_crash.py -            # read from stdin
  cat opencode.log | uv run classify_crash.py

Exit codes: 0 = analysis completed (even when class is null),
            2 = file or usage error.
Stdlib only; no network access; no writes.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

CLASS_NAMES = {
    1: "模型解析失败 (model resolution)",
    2: "agent 身份解析失败 (agent identity resolution)",
    3: "存储层故障 (storage layer)",
    4: "配额/限流 (quota or rate limit)",
}

CLASS_CONFIDENCE = {1: "high", 2: "high", 3: "high", 4: "medium"}

SUGGESTED_ACTIONS = {
    1: (
        "跑 opencode-session-doctor 的 preflight_model_audit.py 对账 "
        "provider 注册/认证；修正配置中的 provider/model 引用"
    ),
    2: (
        "提取 sessionID，走 opencode-session-doctor 的 session resume + "
        "重发 continuation 流程（单 session 最多重试 1 次）"
    ),
    3: (
        "检查磁盘 df；不要重试；转 incident 式止血；"
        "按 references/db-forensics.md 做只读取证"
    ),
    4: (
        "记录配额重置时间，挂起该 provider 的任务发射；"
        "回查 .data.message 确认内层文本（UnknownError 字面量不可信）"
    ),
}

# Precedence order: storage (3) and agent-identity (2) with createUserMessage
# context first, then model resolution (1), then quota (4).
PRECEDENCE = (3, 2, 1, 4)

PATTERNS = {
    1: [
        re.compile(r"ProviderModelNotFoundError"),
        re.compile(r"Model not found:\s*\S+/\S+"),
    ],
    2: [
        re.compile(r"Die\(UnknownError: UnknownError\)"),
        re.compile(r"UnknownError: UnknownError"),
    ],
    3: [
        re.compile(r"SqliteError"),
        re.compile(r"database or disk is full", re.IGNORECASE),
        re.compile(r"database is locked", re.IGNORECASE),
        re.compile(r"\bdisk is full\b", re.IGNORECASE),
    ],
    4: [
        re.compile(r"已达到.*?使用上限"),
        re.compile(r"HTTP 429"),
        re.compile(r"\bstatus(?:\s*code)?\s*429\b", re.IGNORECASE),
        re.compile(r"rate\s*limit", re.IGNORECASE),
        re.compile(r"usage\s*limit", re.IGNORECASE),
    ],
}

CREATE_USER_MESSAGE = re.compile(r"createUserMessage")
SESSION_ID = re.compile(r"\bses_[A-Za-z0-9_]+\b")
INNER_MESSAGE_JSON = re.compile(r'"message"\s*:\s*"((?:[^"\\]|\\.)*)"')
MAX_MATCHES = 10
MAX_MATCH_LINE = 200


def read_input(path_arg: str | None) -> str:
    if path_arg is None or path_arg == "-":
        return sys.stdin.read()
    path = Path(path_arg)
    if not path.is_file():
        raise FileNotFoundError(f"log file not found: {path}")
    return path.read_text(encoding="utf-8", errors="ignore")


def extract_inner_message(candidate_lines: list[str], full_text: str) -> str | None:
    for source in ("\n".join(candidate_lines), full_text):
        match = INNER_MESSAGE_JSON.search(source)
        if match:
            raw = match.group(1)
            try:
                return json.loads(f'"{raw}"')
            except (json.JSONDecodeError, ValueError):
                return raw
    return None


def classify(text: str) -> dict:
    lines = text.splitlines()
    matched: dict[int, list[str]] = {cls: [] for cls in PRECEDENCE}

    for line in lines:
        for cls, patterns in PATTERNS.items():
            if any(pattern.search(line) for pattern in patterns):
                matched[cls].append(line.strip()[:MAX_MATCH_LINE])

    has_create_user_message = bool(CREATE_USER_MESSAGE.search(text))

    # Class-2 signature is only meaningful with createUserMessage context.
    # A bare UnknownError without it drifts to class 4 (quota / provider stream).
    if matched[2] and not has_create_user_message:
        matched[4].extend(matched[2])
        matched[2] = []

    chosen = next((cls for cls in PRECEDENCE if matched[cls]), None)

    if chosen is None:
        return {
            "class": None,
            "name": None,
            "confidence": "low",
            "inner_message": extract_inner_message([], text),
            "suggested_action": (
                "未命中四类签名；扩大日志窗口（含 crash 前后各数分钟）"
                "或人工通读全文后按 references/crash-signatures.md 比对"
            ),
            "matches": [],
        }

    others = [cls for cls in PRECEDENCE if cls != chosen and matched[cls]]
    result: dict[str, object] = {
        "class": chosen,
        "name": CLASS_NAMES[chosen],
        "confidence": CLASS_CONFIDENCE[chosen],
        "inner_message": extract_inner_message(matched[chosen], text),
        "suggested_action": SUGGESTED_ACTIONS[chosen],
        "matches": matched[chosen][:MAX_MATCHES],
    }
    if others:
        result["note"] = f"mixed: also matched classes {others}"
    session_match = SESSION_ID.search("\n".join(matched[chosen])) or SESSION_ID.search(text)
    if session_match:
        result["session_id"] = session_match.group(0)
    return result


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Classify an OpenCode crash log snippet into the 4-class taxonomy."
    )
    parser.add_argument(
        "logfile",
        nargs="?",
        default=None,
        help="Path to log file; omit or use '-' to read from stdin.",
    )
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    try:
        text = read_input(args.logfile)
    except FileNotFoundError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    except OSError as exc:
        print(f"error: cannot read log file: {exc}", file=sys.stderr)
        return 2

    if not text.strip():
        print("error: empty log input", file=sys.stderr)
        return 2

    result = classify(text)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
