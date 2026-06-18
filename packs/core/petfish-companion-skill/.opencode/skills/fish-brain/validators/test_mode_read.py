#!/usr/bin/env python3
"""Contract validator for step0-mode-read atom. Pure stdlib.

Run: uv run python validators/test_mode_read.py
"""
import json, sys
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parent.parent
FIXTURES = json.loads((SKILL_ROOT / "fixtures" / "step0-mode-read" / "fixtures.json").read_text(encoding="utf-8"))
VALID_DEPTHS = {"urgent", "balanced", "thorough"}
failures = []


def check(name, cond, detail=""):
    print(f"  {'PASS' if cond else 'FAIL'}  {name}" + ("" if cond else f"  {detail}"))
    if not cond:
        failures.append(name)


def read_mode(yaml_content):
    """The atom's mechanism: read depth/rigor, coerce thorough→rigor=true."""
    if yaml_content is None:
        return {"depth": "balanced", "rigor": False}
    depth = yaml_content.get("depth", "balanced")
    rigor = yaml_content.get("rigor", False)
    if depth == "thorough":
        rigor = True
    return {"depth": depth, "rigor": rigor}


def validate_output(output):
    """Check output against output_contract."""
    v = []
    if output.get("depth") not in VALID_DEPTHS:
        v.append("invalid_depth")
    if not isinstance(output.get("rigor"), bool):
        v.append("rigor_not_bool")
    if output.get("depth") == "thorough" and output.get("rigor") is not True:
        v.append("rigor_not_forced")
    return v


print(f"Validating atom: step0-mode-read v1\n")

print("[golden] read_mode() must return contract-specified correct output:")
for case in FIXTURES["golden"]:
    result = read_mode(case["input"])
    check(f"{case['id']} expect={case['expected']}", result == case["expected"], f"got {result}")

print("\n[known_bad] invalid_depth rejected:")
kb = FIXTURES["known_bad_invalid_depth"]
check(f"{kb['id']} depth='fast' must be flagged", "invalid_depth" in validate_output(kb["bad_output"]))

print("\n[known_bad] thorough_without_rigor rejected:")
kb = FIXTURES["known_bad_thorough_without_rigor"]
check(f"{kb['id']} thorough+rigor=false must be flagged", "rigor_not_forced" in validate_output(kb["bad_output"]))

print("\n[known_bad] rigor_not_bool rejected:")
kb = FIXTURES["known_bad_rigor_not_bool"]
check(f"{kb['id']} rigor='yes' must be flagged", "rigor_not_bool" in validate_output(kb["bad_output"]))

print()
if failures:
    print(f"RESULT: {len(failures)} failure(s): {failures}"); sys.exit(1)
print("RESULT: all golden pass + all known-bad rejected. Admission gate: PASS")
