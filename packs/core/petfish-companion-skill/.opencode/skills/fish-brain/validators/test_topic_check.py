#!/usr/bin/env python3
"""Contract validator for step1-topic-check atom. Reuses gateway_eval.classify.

Run: uv run python validators/test_topic_check.py
"""
import json, sys
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SKILL_ROOT / "scripts"))
from gateway_classifiers import classify_topic as classify  # noqa: E402

FIXTURES = json.loads((SKILL_ROOT / "fixtures" / "step1-topic-check" / "fixtures.json").read_text(encoding="utf-8"))
VALID_RELATIONS = {"continue", "fork", "switch", "merge", "archive", "reset", "bridge"}
VALID_RISKS = {"low", "medium", "high"}
RISK_BY_RELATION = {"switch": "high", "fork": "medium", "continue": "low", "reset": "low", "archive": "low"}
failures = []


def check(name, cond, detail=""):
    print(f"  {'PASS' if cond else 'FAIL'}  {name}" + ("" if cond else f"  {detail}"))
    if not cond:
        failures.append(name)


def validate_output(output):
    v = []
    rel, risk = output.get("predicted_relation"), output.get("predicted_risk")
    if rel not in VALID_RELATIONS:
        v.append("invalid_relation")
    if risk not in VALID_RISKS:
        v.append("invalid_risk")
    if rel in RISK_BY_RELATION and RISK_BY_RELATION[rel] != risk:
        v.append("risk_relation_mismatch")
    return v


print(f"Validating atom: step1-topic-check v1\n")

print("[golden] classify() must return contract-specified correct output:")
for case in FIXTURES["golden"]:
    result = classify(case["input"])
    check(f"{case['id']} expect={case['expected']}", result == case["expected"], f"got {result}")

print("\n[known_bad] wrong_relation rejected:")
kb = FIXTURES["known_bad_wrong_relation"]
actual = classify(kb["input"])
check(f"{kb['id']} switch signal must classify as switch", actual["predicted_relation"] == "switch",
      f"classify returned {actual}")

print("\n[known_bad] invalid_risk rejected:")
kb = FIXTURES["known_bad_invalid_risk"]
check(f"{kb['id']} risk='critical' must be flagged", "invalid_risk" in validate_output(kb["bad_output"]))

print("\n[known_bad] risk_relation_mismatch rejected:")
kb = FIXTURES["known_bad_risk_relation_mismatch"]
check(f"{kb['id']} switch+low must be flagged", "risk_relation_mismatch" in validate_output(kb["bad_output"]))

print()
if failures:
    print(f"RESULT: {len(failures)} failure(s): {failures}"); sys.exit(1)
print("RESULT: all golden pass + all known-bad rejected. Admission gate: PASS")
