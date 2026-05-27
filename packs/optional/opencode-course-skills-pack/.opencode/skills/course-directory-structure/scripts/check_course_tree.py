#!/usr/bin/env python3
"""Audit a course project tree against the standard structure."""

import argparse
import json
from pathlib import Path

REQUIRED_DIRS = [
    "docs/00-project",
    "docs/01-outline",
    "docs/02-content",
    "docs/03-labs",
]
RECOMMENDED_DIRS = [
    "docs/04-learner-pack",
    "docs/05-instructor-pack",
    "docs/06-qa",
    "docs/07-qc",
    "assets/drawio",
    "references/external",
    "release",
    "archive",
]

def parse_args():
    parser = argparse.ArgumentParser(description="Audit a course project directory tree.")
    parser.add_argument("--root", required=True, help="Target project root directory.")
    parser.add_argument("--emit", choices=["json", "text"], default="json")
    return parser.parse_args()

def main():
    args = parse_args()
    root = Path(args.root).expanduser().resolve()
    required_missing = [p for p in REQUIRED_DIRS if not (root / p).exists()]
    recommended_missing = [p for p in RECOMMENDED_DIRS if not (root / p).exists()]

    score = 100
    score -= len(required_missing) * 15
    score -= len(recommended_missing) * 5
    score = max(score, 0)

    payload = {
        "root": str(root),
        "required_missing": required_missing,
        "recommended_missing": recommended_missing,
        "score": score,
        "status": "pass" if not required_missing else "incomplete",
    }

    if args.emit == "json":
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(f"root: {root}")
        print(f"score: {score}")
        print(f"status: {payload['status']}")
        if required_missing:
            print("required missing:")
            for item in required_missing:
                print(f"  - {item}")
        if recommended_missing:
            print("recommended missing:")
            for item in recommended_missing:
                print(f"  - {item}")

if __name__ == "__main__":
    main()
