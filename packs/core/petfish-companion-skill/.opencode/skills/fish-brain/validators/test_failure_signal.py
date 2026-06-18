#!/usr/bin/env python3
"""Contract validator for step1.5-failure-signal atom.

Reuses the existing classify() from benchmarks/scripts/modules/failure_signal_eval.py
(no logic duplication). Tests two obligations per the paper §3.5 admission criteria:
  1. Golden fixtures: classify() returns the contract-specified correct output.
  2. Known-bad fixtures: the contract's output_contract REJECTS the violating output.

Pure stdlib, no test framework. Run: uv run python validators/test_failure_signal.py
"""
import json
import sys
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SKILL_ROOT / "scripts"))

from gateway_classifiers import classify_failure_signal as classify  # noqa: E402

CONTRACT = json.loads((SKILL_ROOT / "contracts" / "step1.5-failure-signal.contract.json").read_text(encoding="utf-8"))
FIXTURES = json.loads((SKILL_ROOT / "fixtures" / "step1.5-failure-signal" / "fixtures.json").read_text(encoding="utf-8"))

ADMISSIBLE = {"ppt", "deploy", "testdocs", "research", "context"}
failures = []


def check(name, condition, detail=""):
    if condition:
        print(f"  PASS  {name}")
    else:
        print(f"  FAIL  {name}  {detail}")
        failures.append(name)


def validate_output(output):
    v = []
    d, s = output.get("predicted_detect"), output.get("predicted_signal")
    if not isinstance(d, bool):
        v.append("detected_not_bool")
    if d and (s is None or s not in ADMISSIBLE):
        v.append("invalid_failure_class")
    if not d and s is not None:
        v.append("signal_without_detection")
    return v


print(f"Validating atom: {CONTRACT['atom_id']} {CONTRACT['version']}\n")

# Admission #2: golden passes
print("[golden] classify() must return contract-specified correct output:")
for case in FIXTURES["golden"]:
    result = classify(case["input"])
    check(f"{case['id']} expect={case['expected']}", result == case["expected"], f"got {result}")

# Admission #3: known-bad false_positive rejected
print("\n[known_bad] false_positive rejected:")
kb = FIXTURES["known_bad_false_positive"]
check(f"{kb['id']} no failure word in input → must not detect",
      classify(kb["input"])["predicted_detect"] is False, "false positive!")

# Admission #3: known-bad false_negative rejected
print("\n[known_bad] false_negative rejected:")
kb = FIXTURES["known_bad_false_negative"]
check(f"{kb['id']} clear PDF failure → must detect",
      classify(kb["input"])["predicted_detect"] is True, "false negative!")

# Admission #3: known-bad invalid_class rejected by output_contract
print("\n[known_bad] invalid_failure_class rejected:")
kb = FIXTURES["known_bad_invalid_class"]
v = validate_output(kb["bad_output"])
check(f"{kb['id']} failure_class='unknown' must be flagged",
      "invalid_failure_class" in v, f"violations={v}")

print()
if failures:
    print(f"RESULT: {len(failures)} failure(s): {failures}")
    sys.exit(1)
print("RESULT: all golden pass + all known-bad rejected. Admission gate: PASS")
