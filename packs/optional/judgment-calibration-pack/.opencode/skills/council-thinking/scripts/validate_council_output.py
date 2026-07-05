# /// script
# requires-python = ">=3.10"
# ///
"""Validate that a Council Thinking output contains all required sections.

Usage:
    uv run validate_council_output.py <output.md>
    uv run validate_council_output.py <output.md> --mode quick

Exit codes:
    0 — all required sections present
    1 — missing required sections (details printed to stderr)
"""
import argparse
import re
import sys

FULL_MODE_SECTIONS = [
    ("问题重述", "Step 1: problem restatement"),
    ("反对者", "Critic advisor"),
    ("本质思考者", "Essence advisor"),
    ("机会挖掘者", "Opportunity advisor"),
    ("局外人", "Outsider advisor"),
    ("执行者", "Executor advisor"),
    ("交叉审查", "Step 3: cross-review"),
    ("去掉弱观点", "Step 4: weak-point removal"),
    ("综合结论", "Step 5: synthesis"),
    ("不知道", "Uncertainty boundary"),
]

QUICK_MODE_SECTIONS = [
    ("反对者", "Critic"),
    ("本质思考者", "Essence"),
    ("机会挖掘者", "Opportunity"),
    ("局外人", "Outsider"),
    ("执行者", "Executor"),
    ("结论", "Conclusion after weak-point removal"),
    ("下一步", "Next action"),
    ("不知道", "Uncertainty boundary"),
]


def validate(content: str, mode: str = "full") -> list[str]:
    """Return list of missing section names."""
    sections = FULL_MODE_SECTIONS if mode == "full" else QUICK_MODE_SECTIONS
    missing = []
    for keyword, label in sections:
        if keyword not in content:
            missing.append(f"{keyword} ({label})")
    return missing


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate Council Thinking output structure")
    parser.add_argument("file", help="Path to the Council output Markdown file")
    parser.add_argument("--mode", choices=["full", "quick"], default="full", help="Output mode to validate against")
    args = parser.parse_args()

    try:
        with open(args.file, encoding="utf-8") as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Error: file not found: {args.file}", file=sys.stderr)
        return 1

    missing = validate(content, args.mode)
    if missing:
        print(f"FAIL — {len(missing)} missing section(s) for {args.mode} mode:", file=sys.stderr)
        for m in missing:
            print(f"  - {m}", file=sys.stderr)
        return 1

    total = len(FULL_MODE_SECTIONS) if args.mode == "full" else len(QUICK_MODE_SECTIONS)
    print(f"PASS — all {total} required sections present ({args.mode} mode)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
