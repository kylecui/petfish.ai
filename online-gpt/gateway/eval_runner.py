"""Lightweight eval runner for PEtFiSh Online Gateway skeleton.

This runner validates deterministic gateway routing and boundary metadata. It does
not evaluate final GPT prose.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, List

GATEWAY_DIR = Path(__file__).resolve().parent
if str(GATEWAY_DIR) not in sys.path:
    sys.path.insert(0, str(GATEWAY_DIR))

from router import route_companion_request  # noqa: E402


def load_cases(root: Path) -> List[Dict[str, Any]]:
    cases: List[Dict[str, Any]] = []
    for path in sorted(root.rglob("*.jsonl")):
        with path.open("r", encoding="utf-8") as fh:
            for line_no, line in enumerate(fh, start=1):
                line = line.strip()
                if not line:
                    continue
                case = json.loads(line)
                case["_path"] = str(path)
                case["_line"] = line_no
                cases.append(case)
    return cases


def flatten_values(obj: Any) -> str:
    return json.dumps(obj, ensure_ascii=False, sort_keys=True)


def case_passes(case: Dict[str, Any]) -> tuple[bool, List[str]]:
    output = route_companion_request(case["input"], platform=_infer_platform(case["input"]))
    text = flatten_values(output)
    errors: List[str] = []

    expected_route = case.get("expected_route")
    if expected_route and expected_route not in text:
        errors.append(f"expected_route not found: {expected_route}")

    for needle in case.get("must_include", []):
        if needle not in text:
            errors.append(f"must_include not found: {needle}")

    for needle in case.get("must_not_include", []):
        if needle in text:
            errors.append(f"must_not_include found: {needle}")

    return not errors, errors


def _infer_platform(text: str) -> str:
    lowered = text.lower()
    for platform in ["opencode", "codex", "antigravity", "claude", "cursor", "copilot", "windsurf"]:
        if platform in lowered:
            return platform
    if "openCode" in text:
        return "opencode"
    return "opencode"


def run(root: Path) -> int:
    cases = load_cases(root)
    if not cases:
        print(f"No eval cases found under {root}")
        return 1

    failed = 0
    for case in cases:
        ok, errors = case_passes(case)
        label = "PASS" if ok else "FAIL"
        print(f"[{label}] {case.get('id', '<missing-id>')} ({case['_path']}:{case['_line']})")
        for error in errors:
            print(f"  - {error}")
        if not ok:
            failed += 1

    print(f"\nTotal: {len(cases)} | Passed: {len(cases) - failed} | Failed: {failed}")
    return 0 if failed == 0 else 2


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run online-gpt gateway evals.")
    parser.add_argument("root", nargs="?", default="online-gpt/evals", help="Eval root directory")
    args = parser.parse_args(list(argv) if argv is not None else None)
    return run(Path(args.root))


if __name__ == "__main__":
    raise SystemExit(main())
