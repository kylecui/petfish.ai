#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = []
# ///
"""Validate done-contract and verdict files for the completion-engineering pack.

Checks:
  1. contract.json — required fields present, anchor externally referenced and
     non-empty, tautology predicates rejected (echo/true/exit/':' commands or
     empty runs always pass and verify nothing).
  2. verdict.json — verdict value within the 5-value enum, revision cited,
     round within the 3-round gate exit limit.

Usage:
  uv run check_contract.py <contract.json>
  uv run check_contract.py <contract.json> --verdict <verdict.json>

Exit codes: 0 = valid, 1 = validation failed, 2 = file or usage error.
Stdlib only; no network access.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import TypeGuard

REQUIRED_CONTRACT_FIELDS = (
    "revision",
    "anchor",
    "outcome",
    "constraints",
    "verifications",
    "blocked_if",
    "out_of_scope",
)
ANCHOR_TYPES = {"user_request", "plan", "todo"}
VERIFICATION_TYPES = {"command", "artifact", "judge"}
VALID_VERDICTS = {
    "VERIFIED_DONE",
    "NOT_DONE",
    "PARTIAL",
    "BLOCKED_ON_USER",
    "SKIPPED",
}
# An always-true command predicate: shell no-ops that succeed regardless of
# the actual work. ':' needs no trailing word boundary (it is never followed
# by a word char in this idiom), while echo/true/exit must match as words.
TAUTOLOGY_RUN = re.compile(r"^\s*(?:(?:echo|true|exit)\b|:)")
MAX_GATE_ROUNDS = 3


class Validation:
    """Collects error messages; ok when the list stays empty."""

    def __init__(self) -> None:
        self.errors: list[str] = []

    def error(self, message: str) -> None:
        self.errors.append(message)

    @property
    def ok(self) -> bool:
        return not self.errors

    def report(self, label: str) -> int:
        if self.errors:
            print(f"FAIL: {label} ({len(self.errors)} error(s)):")
            for message in self.errors:
                print(f"  - {message}")
            return 1
        print(f"OK: {label}")
        return 0


def load_json(path: Path) -> tuple[object | None, str | None]:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        return None, f"cannot read {path}: {exc}"
    try:
        return json.loads(text), None
    except json.JSONDecodeError as exc:
        return None, f"invalid JSON in {path}: {exc}"


def is_int(value: object) -> TypeGuard[int]:
    return isinstance(value, int) and not isinstance(value, bool)


def validate_contract(data: object, validation: Validation) -> None:
    if not isinstance(data, dict):
        validation.error("contract root must be a JSON object")
        return

    for field in REQUIRED_CONTRACT_FIELDS:
        if field not in data:
            validation.error(f"missing required field: {field}")

    if "revision" in data and (not is_int(data["revision"]) or data["revision"] < 1):
        validation.error("revision must be an integer >= 1")

    if "outcome" in data and (
        not isinstance(data["outcome"], str) or not data["outcome"].strip()
    ):
        validation.error("outcome must be a non-empty string")

    for field in ("constraints", "blocked_if", "out_of_scope"):
        if field in data and not isinstance(data[field], list):
            validation.error(f"{field} must be an array")

    if "critical" in data and not isinstance(data["critical"], bool):
        validation.error("critical must be a boolean")

    if "anchor" in data:
        anchor = data["anchor"]
        if not isinstance(anchor, dict):
            validation.error("anchor must be an object with type and ref")
        else:
            if anchor.get("type") not in ANCHOR_TYPES:
                allowed = ", ".join(sorted(ANCHOR_TYPES))
                validation.error(f"anchor.type must be one of: {allowed}")
            anchor_ref = anchor.get("ref")
            if not isinstance(anchor_ref, str) or not anchor_ref.strip():
                validation.error(
                    "anchor.ref must be a non-empty string "
                    "(external anchor required: quote the user request, "
                    "plan entry, or todo item; self-invented outcomes are rejected)"
                )

    if "verifications" in data:
        verifications = data["verifications"]
        if not isinstance(verifications, list) or not verifications:
            validation.error(
                "verifications must be a non-empty array (at least 1 predicate)"
            )
        else:
            for index, item in enumerate(verifications):
                _validate_verification(index, item, validation)

    if "amendments" in data and data["amendments"] is not None:
        amendments = data["amendments"]
        if not isinstance(amendments, list):
            validation.error("amendments must be an array")
        else:
            for index, item in enumerate(amendments):
                if not isinstance(item, dict) or not str(
                    item.get("reason", "")
                ).strip():
                    validation.error(
                        f"amendments[{index}]: contract changes must record a reason"
                    )


def _validate_verification(
    index: int, item: object, validation: Validation
) -> None:
    label = f"verifications[{index}]"
    if not isinstance(item, dict):
        validation.error(f"{label}: must be an object")
        return

    vtype = item.get("type")
    if vtype not in VERIFICATION_TYPES:
        allowed = ", ".join(sorted(VERIFICATION_TYPES))
        validation.error(f"{label}: type must be one of: {allowed}")
        return

    if vtype == "command":
        run = item.get("run")
        if not isinstance(run, str) or not run.strip():
            validation.error(f"{label}: command predicate has an empty run")
        elif TAUTOLOGY_RUN.match(run):
            validation.error(
                f"{label}: tautology predicate rejected (run={run!r}) — "
                "always-true commands (echo/true/exit/':') verify nothing; "
                "write a predicate that can actually fail"
            )
    elif vtype == "artifact":
        path = item.get("path")
        if not isinstance(path, str) or not path.strip():
            validation.error(f"{label}: artifact predicate requires a non-empty path")
    elif vtype == "judge":
        criteria = item.get("criteria")
        if not isinstance(criteria, str) or not criteria.strip():
            validation.error(f"{label}: judge predicate requires a non-empty criteria")


def validate_verdict(data: object, validation: Validation) -> None:
    if not isinstance(data, dict):
        validation.error("verdict root must be a JSON object")
        return

    verdict = data.get("verdict")
    if verdict not in VALID_VERDICTS:
        allowed = ", ".join(sorted(VALID_VERDICTS))
        validation.error(f"verdict must be one of: {allowed} (got {verdict!r})")

    revision = data.get("revision")
    if not is_int(revision) or revision < 1:
        validation.error(
            "revision must be an integer >= 1 "
            "(a verdict must cite the contract revision it is based on)"
        )

    for field in ("evidence", "remaining"):
        if field in data and not isinstance(data[field], list):
            validation.error(f"{field} must be an array")

    if "round" in data and data["round"] is not None:
        round_no = data["round"]
        if not is_int(round_no) or not 1 <= round_no <= MAX_GATE_ROUNDS:
            validation.error(
                f"round must be an integer in [1, {MAX_GATE_ROUNDS}] "
                "(the gate exits after 3 rounds)"
            )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate done-contract and verdict files "
        "(completion-engineering pack)."
    )
    parser.add_argument("contract", nargs="?", help="path to contract.json")
    parser.add_argument(
        "--verdict", help="path to verdict.json (validated in addition)"
    )
    args = parser.parse_args()
    if not args.contract and not args.verdict:
        parser.error("provide a contract.json path and/or --verdict verdict.json")
    return args


def main() -> int:
    args = parse_args()
    exit_code = 0

    if args.contract:
        path = Path(args.contract)
        data, error = load_json(path)
        if error:
            print(f"FAIL: {error}")
            return 2
        validation = Validation()
        validate_contract(data, validation)
        exit_code = max(exit_code, validation.report(f"contract {path}"))

    if args.verdict:
        path = Path(args.verdict)
        data, error = load_json(path)
        if error:
            print(f"FAIL: {error}")
            return 2
        validation = Validation()
        validate_verdict(data, validation)
        exit_code = max(exit_code, validation.report(f"verdict {path}"))

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
