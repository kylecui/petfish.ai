#!/usr/bin/env python3
"""Check GPT Builder short instructions for size and mandatory guardrails."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INSTRUCTIONS = ROOT / "instructions" / "petfish-companion.gpt-builder.instructions.md"
MAX_CHARS = 8000

MUST_INCLUDE = [
    "independent online companion runtime",
    "ChatGPT Project",
    "No local installation is required",
    "optional execution adapters",
    "P0 Standalone Mode",
    "P1 Gateway Mode",
    "P2 Adapter Mode",
    "boundary/regression only",
    "Never claim",
    "verified adapter result",
    "Never echo API keys",
    "platform=online",
    "semantic references",
    "11-execution-and-contracts.md",
    "executed and audit_logged are P2-only",
]

MUST_NOT_INCLUDE = [
    "I completely agree",
    "完全正确",
    "remote controller for OpenCode",
    "P2 is the primary",
    "local installation is required",
    "command ran",
    "installation completed",
    "audit_logged by default",
    "executed by default",
]

# Avoid putting large reference material into the GPT Builder Instructions field.
BLOAT_MARKERS = [
    "| Mode | Side effect |",
    "| Risk class | Examples |",
    "### direct_explanation",
    "### pack_recommendation",
    "### install_command",
    "### module_design",
    "### skill_workbench",
    "### executed_result_summary",
]


def main() -> int:
    if not INSTRUCTIONS.exists():
        print(f"missing file: {INSTRUCTIONS}", file=sys.stderr)
        return 1

    text = INSTRUCTIONS.read_text(encoding="utf-8")
    errors: list[str] = []

    if len(text) > MAX_CHARS:
        errors.append(f"too long: {len(text)} chars > {MAX_CHARS}")

    for needle in MUST_INCLUDE:
        if needle not in text:
            errors.append(f"missing required phrase: {needle}")

    lowered = text.lower()
    for needle in MUST_NOT_INCLUDE:
        if needle.lower() in lowered:
            errors.append(f"forbidden phrase present: {needle}")

    for marker in BLOAT_MARKERS:
        if marker in text:
            errors.append(f"knowledge/template bloat marker present: {marker}")

    if "actions/openapi.yaml" in text:
        errors.append("short instructions must not point to full openapi.yaml")

    if errors:
        print("GPT Builder instructions check failed:", file=sys.stderr)
        for err in errors:
            print(f"- {err}", file=sys.stderr)
        return 1

    print(f"GPT Builder instructions check passed ({len(text)} chars <= {MAX_CHARS})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
