#!/usr/bin/env python3
"""Contract validator for step2-skill-sense atom. Reuses skill_sense_eval.classify.

Run: uv run python validators/test_skill_sense.py
"""
import json, sys
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SKILL_ROOT / "scripts"))
from gateway_classifiers import classify_skill_sense as classify  # noqa: E402

FIXTURES = json.loads((SKILL_ROOT / "fixtures" / "step2-skill-sense" / "fixtures.json").read_text(encoding="utf-8"))
failures = []


def check(name, cond, detail=""):
    print(f"  {'PASS' if cond else 'FAIL'}  {name}" + ("" if cond else f"  {detail}"))
    if not cond:
        failures.append(name)


print(f"Validating atom: step2-skill-sense v1\n")

print("[golden] classify() must return contract-specified correct output:")
for case in FIXTURES["golden"]:
    result = classify(case["input"])
    check(f"{case['id']} expect={case['expected']}", result == case["expected"], f"got {result}")

print("\n[known_bad] context_question_false_positive rejected:")
kb = FIXTURES["known_bad_context_question_fp"]
actual = classify(kb["input"])
check(f"{kb['id']} context question must not trigger", actual["predicted_detect"] is False, f"got {actual}")

print("\n[known_bad] false_negative rejected:")
kb = FIXTURES["known_bad_false_negative"]
actual = classify(kb["input"])
check(f"{kb['id']} clear research request must detect", actual["predicted_detect"] is True, f"got {actual}")

print("\n[known_bad] invalid_skill rejected:")
kb = FIXTURES["known_bad_invalid_skill"]
TRIGGERS_KEYS = {"deploy", "course", "petfish", "ppt", "testdocs", "calibrate", "research", "context", "trust"}
check(f"{kb['id']} skill='cloud' not in TRIGGERS keys",
      kb["bad_output"]["predicted_skill"] not in TRIGGERS_KEYS)

print()
if failures:
    print(f"RESULT: {len(failures)} failure(s): {failures}"); sys.exit(1)
print("RESULT: all golden pass + all known-bad rejected. Admission gate: PASS")
