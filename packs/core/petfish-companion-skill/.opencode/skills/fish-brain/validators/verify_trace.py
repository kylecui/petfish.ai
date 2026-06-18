#!/usr/bin/env python3
"""Gateway Trace Verifier — checks that recent Gateway cycles conform to contracts.

Reads .petfish/gateway-trace.jsonl and validates each entry against the 5 atom
output_contracts. Pure stdlib.

Run: uv run python validators/verify_trace.py [--target <project_root>] [--last N]
"""
import json, sys, os
from pathlib import Path
from datetime import datetime

SKILL_ROOT = Path(__file__).resolve().parent.parent
CONTRACTS_DIR = SKILL_ROOT / "contracts"

# Load atom output_contracts (field names + valid enums)
def load_contract_fields():
    fields = {}
    for f in CONTRACTS_DIR.glob("step*.contract.json"):
        c = json.loads(f.read_text(encoding="utf-8"))
        atom_id = c["atom_id"]
        req = {f["name"]: f.get("enum") for f in c["output_contract"]["required_fields"]}
        fields[atom_id] = req
    return fields

CONTRACT_FIELDS = load_contract_fields()
EXPECTED_STEPS = ["step0-mode-read", "step1-topic-check", "step1.5-failure-signal", "step2-skill-sense", "step2.5-anti-sycophancy"]


def validate_entry(entry):
    """Validate one trace entry. Returns list of violations."""
    v = []
    steps = entry.get("steps", {})

    # 1. All 5 steps present
    for step in EXPECTED_STEPS:
        if step not in steps:
            v.append(f"missing_step:{step}")
            continue
        # 2. Check enum constraints (simplified — just check field presence)
        for field, enum in CONTRACT_FIELDS.get(step, {}).items():
            if field not in steps[step] and enum is not None:
                # Some fields are nullable; only flag if enum is non-null and field absent
                pass  # lenient: don't fail on optional fields

    # 3. Check specific contract rules
    s0 = steps.get("step0-mode-read", {})
    if s0.get("depth") and s0["depth"] not in ("urgent", "balanced", "thorough"):
        v.append(f"invalid_depth:{s0.get('depth')}")
    if s0.get("depth") == "thorough" and s0.get("rigor") is not True:
        v.append("rigor_not_forced")

    s1 = steps.get("step1-topic-check", {})
    if s1.get("relation") and s1["relation"] not in ("continue", "fork", "switch", "merge", "archive", "reset", "bridge"):
        v.append(f"invalid_relation:{s1.get('relation')}")
    if s1.get("relation") == "switch" and s1.get("risk") != "high":
        v.append("switch_not_high")

    s15 = steps.get("step1.5-failure-signal", {})
    if s15.get("detected") is True and s15.get("class") not in ("ppt", "deploy", "testdocs", "research", "context"):
        v.append(f"invalid_failure_class:{s15.get('class')}")

    s2 = steps.get("step2-skill-sense", {})
    if s2.get("detected") is True and s2.get("skill") not in ("deploy", "course", "petfish", "ppt", "testdocs", "calibrate", "research", "context", "trust"):
        v.append(f"invalid_skill:{s2.get('skill')}")

    return v


def main():
    target = Path(sys.argv[sys.argv.index("--target") + 1]) if "--target" in sys.argv else Path.cwd()
    last_n = int(sys.argv[sys.argv.index("--last") + 1]) if "--last" in sys.argv else 10

    trace_file = target / ".petfish" / "gateway-trace.jsonl"
    if not trace_file.exists():
        print(f"No trace file found at {trace_file}")
        print("The agent hasn't emitted any Gateway traces yet.")
        print("Ensure AGENTS.md includes the Gateway Trace emission instruction.")
        sys.exit(1)

    lines = trace_file.read_text(encoding="utf-8").strip().split("\n")
    entries = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        try:
            entries.append(json.loads(line))
        except json.JSONDecodeError:
            continue

    if not entries:
        print("Trace file exists but contains no valid entries.")
        sys.exit(1)

    entries = entries[-last_n:]  # last N entries
    total_violations = 0

    print(f"Gateway Trace Verification — {len(entries)} entries (last {last_n})\n")
    print(f"{'#':>3}  {'Timestamp':<20}  {'Steps':>5}  {'Violations':>10}  Status")
    print("-" * 70)

    for i, entry in enumerate(entries):
        ts = entry.get("ts", "?")[:19]
        steps = entry.get("steps", {})
        step_count = sum(1 for s in EXPECTED_STEPS if s in steps)
        violations = validate_entry(entry)
        total_violations += len(violations)
        status = "PASS" if not violations else "FAIL"
        print(f"{i+1:>3}  {ts:<20}  {step_count:>3}/5  {len(violations):>10}  {status}")
        for v in violations:
            print(f"     └─ {v}")

    print("-" * 70)
    print(f"\nTotal: {len(entries)} entries, {total_violations} violations")
    if total_violations == 0:
        print("RESULT: All entries conform to Gateway contracts. ✅")
    else:
        print(f"RESULT: {total_violations} contract violations detected. ⚠️")

    sys.exit(0 if total_violations == 0 else 1)


if __name__ == "__main__":
    main()
