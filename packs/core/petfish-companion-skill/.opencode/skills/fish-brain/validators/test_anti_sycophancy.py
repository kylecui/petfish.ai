#!/usr/bin/env python3
"""Detection-level validator for step2.5-anti-sycophancy atom.

NOTE: This validates DETECTION only (does the message contain evaluative keywords?).
Behavior-level validation (rubric quality, counter-argument sincerity) requires LLM
judgment and is deferred per the claim boundary. Reuses skill_sense_eval TRIGGERS['calibrate'].

Run: uv run python validators/test_anti_sycophancy.py
"""
import json, sys
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SKILL_ROOT / "scripts"))
from gateway_classifiers import TRIGGERS  # noqa: E402

FIXTURES = json.loads((SKILL_ROOT / "fixtures" / "step2.5-anti-sycophancy" / "fixtures.json").read_text(encoding="utf-8"))
EVAL_KEYWORDS = TRIGGERS["calibrate"]  # reuse the calibrate trigger keywords
failures = []


def check(name, cond, detail=""):
    print(f"  {'PASS' if cond else 'FAIL'}  {name}" + ("" if cond else f"  {detail}"))
    if not cond:
        failures.append(name)


def is_evaluative(msg):
    """Detection-level check: does the message contain evaluative keywords?"""
    msg_lower = msg.lower()
    return any(kw.lower() in msg_lower for kw in EVAL_KEYWORDS)


print(f"Validating atom: step2.5-anti-sycophancy v1 (detection-level only)\n")

print("[golden_detection] is_evaluative() classification:")
for case in FIXTURES["golden_detection"]:
    result = is_evaluative(case["input"]["user_message"])
    check(f"{case['id']} expect is_evaluative={case['expected']['is_evaluative']}",
          result == case["expected"]["is_evaluative"], f"got {result}")

print("\n[known_bad] over_trigger rejected:")
kb = FIXTURES["known_bad_over_trigger"]
result = is_evaluative(kb["input"]["user_message"])
check(f"{kb['id']} rename request must not be evaluative", result is False, "over-trigger!")

print("\n[known_bad] missed_evaluative rejected:")
kb = FIXTURES["known_bad_missed_eval"]
result = is_evaluative(kb["input"]["user_message"])
check(f"{kb['id']} '你觉得...合理吗' must be evaluative", result is True, "missed eval!")

print()
if failures:
    print(f"RESULT: {len(failures)} failure(s): {failures}"); sys.exit(1)
print("RESULT: detection-level admission gate: PASS (behavior-level deferred to llm_judge)")
