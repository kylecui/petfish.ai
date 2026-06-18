#!/usr/bin/env python3
"""Macro composition validator for gateway-macro contract.

Tests cross-step carried obligations and sequence integrity (paper Stage 7p v2 lesson).
Pure stdlib.

Run: uv run python validators/test_macro_composition.py
"""
import json, sys
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parent.parent
FIXTURES = json.loads((SKILL_ROOT / "fixtures" / "gateway-macro" / "fixtures.json").read_text(encoding="utf-8"))
EXPECTED_SEQUENCE = ["step0-mode-read", "step1-topic-check", "step1.5-failure-signal", "step2-skill-sense", "step2.5-anti-sycophancy"]
failures = []


def check(name, cond, detail=""):
    print(f"  {'PASS' if cond else 'FAIL'}  {name}" + ("" if cond else f"  {detail}"))
    if not cond:
        failures.append(name)


def validate_composition(atom_outputs):
    """Check sequence integrity + carried obligations. Returns violations list."""
    v = []

    # 1. Sequence check: all 5 atoms present in order
    present = list(atom_outputs.keys())
    if present != EXPECTED_SEQUENCE:
        missing = set(EXPECTED_SEQUENCE) - set(present)
        extra = set(present) - set(EXPECTED_SEQUENCE)
        if missing:
            v.append({"type": "skipped_step", "detail": f"missing: {missing}"})
        if extra:
            v.append({"type": "unexpected_step", "detail": f"extra: {extra}"})
        if present != EXPECTED_SEQUENCE and not missing and not extra:
            v.append({"type": "wrong_order", "detail": f"got {present}"})

    # 2. Carried obligation: step1.5.recommended_pack must not duplicate step2.predicted_skill
    s15 = atom_outputs.get("step1.5-failure-signal", {})
    s2 = atom_outputs.get("step2-skill-sense", {})
    if s15.get("recommended_pack") and s15.get("recommended_pack") == s2.get("predicted_skill"):
        v.append({"type": "duplicate_recommendation", "detail": f"both recommend '{s15['recommended_pack']}'"})

    # 3. Carried obligation: step0.rigor=false → step2.5 should not over-trigger
    #    (if step2.5 says evaluative=true but there's no evaluative content, and rigor=false, flag it)
    #    This is a heuristic check — we can't verify content, only flag structural inconsistency
    s0 = atom_outputs.get("step0-mode-read", {})
    s25 = atom_outputs.get("step2.5-anti-sycophancy", {})
    # Only flag if we have explicit data: rigor=false AND is_evaluative=true with no calibrate skill detected
    if s0.get("rigor") is False and s25.get("is_evaluative") is True:
        if s2.get("predicted_skill") != "calibrate":
            v.append({"type": "obligation_lost", "detail": "rigor=false but is_evaluative=true without calibrate trigger"})

    return v


print(f"Validating atom: gateway-macro v1\n")

print("[golden] composition must have no violations:")
for case in FIXTURES["golden"]:
    violations = validate_composition(case["atom_outputs"])
    expected_violations = case["expected"]["violations"]
    check(f"{case['id']} expect 0 violations",
          len(violations) == 0 and len(expected_violations) == 0,
          f"got {len(violations)} violations: {violations}")

print("\n[known_bad] duplicate_recommendation detected:")
kb = FIXTURES["known_bad_duplicate_recommendation"]
v = validate_composition(kb["atom_outputs"])
types = [x["type"] for x in v]
check(f"{kb['id']} duplicate must be flagged", "duplicate_recommendation" in types, f"got {types}")

print("\n[known_bad] skipped_step detected:")
kb = FIXTURES["known_bad_skipped_step"]
v = validate_composition(kb["atom_outputs"])
types = [x["type"] for x in v]
check(f"{kb['id']} missing step must be flagged", "skipped_step" in types, f"got {types}")

print("\n[known_bad] obligation_lost detected:")
kb = FIXTURES["known_bad_obligation_lost"]
v = validate_composition(kb["atom_outputs"])
types = [x["type"] for x in v]
check(f"{kb['id']} lost obligation must be flagged", "obligation_lost" in types, f"got {types}")

print()
if failures:
    print(f"RESULT: {len(failures)} failure(s): {failures}"); sys.exit(1)
print("RESULT: all golden pass + all known-bad rejected. Macro admission gate: PASS")
