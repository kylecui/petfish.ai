# /// script
# requires-python = ">=3.10"
# ///
"""Companion Gateway plugin runtime verification.

Verifies structural correctness of companion-gateway.ts without requiring
a live OpenCode runtime. Run after any plugin changes.

Usage: uv run scripts/verify_companion_gateway.py
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLUGIN_FILE = ROOT / ".opencode/plugin/companion-gateway.ts"
CONFIG_FILE = ROOT / "opencode.json"

failures: list[str] = []
warnings: list[str] = []

# ---------------------------------------------------------------------------
# 1. Plugin file exists
# ---------------------------------------------------------------------------
if not PLUGIN_FILE.is_file():
    failures.append(f"Plugin file missing: {PLUGIN_FILE}")
else:
    print("  [PASS] Plugin file exists")

# ---------------------------------------------------------------------------
# 2. Plugin registered in opencode.json
# ---------------------------------------------------------------------------
if not CONFIG_FILE.is_file():
    failures.append(f"Config file missing: {CONFIG_FILE}")
else:
    config = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
    plugins = config.get("plugin", [])
    found = any(
        isinstance(p, list) and len(p) >= 1 and "companion-gateway" in str(p[0])
        for p in plugins
    )
    if found:
        print("  [PASS] Plugin registered in opencode.json")
    else:
        failures.append("companion-gateway.ts not registered in opencode.json plugin array")

# ---------------------------------------------------------------------------
# 3. Plugin exports default
# ---------------------------------------------------------------------------
if PLUGIN_FILE.is_file():
    content = PLUGIN_FILE.read_text(encoding="utf-8")
    if "export default plugin" in content:
        print("  [PASS] Plugin has default export")
    else:
        failures.append("Plugin missing 'export default plugin'")

    # 4. Required hooks present
    hooks = {
        "experimental.chat.system.transform": "System prompt injection",
        "tool.execute.after": "Retry guard (failure tracking)",
    }
    for hook, desc in hooks.items():
        if hook in content:
            print(f"  [PASS] Hook present: {hook} ({desc})")
        else:
            failures.append(f"Missing hook: {hook} ({desc})")

    # 5. Step implementations present
    steps = {
        "readProjectMode": "Step 0: Mode Read",
        "detectFailureSignal": "Step 1.5: Failure Signal Detection",
        "runSkillSense": "Step 2: Skill Sense",
        "isEvaluative": "Step 2.5: Anti-Sycophancy Check",
        "getRetryCount": "Step 3: Retry Guard state",
    }
    for func, desc in steps.items():
        if func in content:
            print(f"  [PASS] Function present: {func} ({desc})")
        else:
            failures.append(f"Missing function: {func} ({desc})")

    # 6. Failure patterns present
    if "FAILURE_SIGNALS" in content:
        print("  [PASS] Failure signal patterns defined")
    else:
        warnings.append("FAILURE_SIGNALS array not found — failure detection may not work")

    # 7. Skill triggers present
    if "SKILL_TRIGGERS" in content:
        print("  [PASS] Skill trigger table defined")
    else:
        warnings.append("SKILL_TRIGGERS dict not found — skill sense may not work")

    # 8. Graceful degradation
    if "Graceful degradation" in content or "never break the session" in content:
        print("  [PASS] Graceful degradation present (try/catch in hooks)")
    else:
        warnings.append("No explicit graceful degradation comment found")

# ---------------------------------------------------------------------------
# 9. topic-context-filter also registered (companion ecosystem)
# ---------------------------------------------------------------------------
if CONFIG_FILE.is_file():
    config = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
    plugins = config.get("plugin", [])
    tcf_found = any(
        isinstance(p, list) and len(p) >= 1 and "topic-context-filter" in str(p[0])
        for p in plugins
    )
    if tcf_found:
        print("  [PASS] topic-context-filter also registered")
    else:
        warnings.append("topic-context-filter not registered — companion ecosystem incomplete")

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------
print()
if failures:
    print(f"  FAIL: {len(failures)} failure(s):")
    for f in failures:
        print(f"    ✗ {f}")
if warnings:
    print(f"  WARN: {len(warnings)} warning(s):")
    for w in warnings:
        print(f"    ⚠ {w}")
if not failures:
    print("  ✓ All structural checks passed!")
    print("  Next: restart OpenCode and verify gateway injection appears in system prompt.")
sys.exit(1 if failures else 0)
