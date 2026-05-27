#!/usr/bin/env python3
"""Local smoke runner for research-skill-pack.

Exercises the full research pipeline on seeded fixture data:
  init workspace → validate workspace → lint evidence → quality-gate report

Usage:
uv run packs/optional/research-skill-pack/scripts/run_smoke.py
uv run packs/optional/research-skill-pack/scripts/run_smoke.py --fixtures path/to/fixtures
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
import tempfile
from pathlib import Path
from subprocess import PIPE, run as subprocess_run

PACK_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = PACK_ROOT / "scripts"
SKILLS_DIR = PACK_ROOT / ".opencode" / "skills"
DEFAULT_FIXTURES = PACK_ROOT / "tests" / "fixtures" / "smoke-workspace"


def _run_script(script: Path, args: list[str], label: str) -> dict:
    """Run a Python script and return parsed JSON output."""
    cmd = [sys.executable, str(script)] + args
    result = subprocess_run(cmd, capture_output=True, text=True, timeout=30)
    try:
        output = json.loads(result.stdout)
    except (json.JSONDecodeError, ValueError):
        output = {"raw_stdout": result.stdout, "raw_stderr": result.stderr}
    return {
        "step": label,
        "returncode": result.returncode,
        "output": output,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run research pack smoke test.")
    parser.add_argument(
        "--fixtures",
        default=str(DEFAULT_FIXTURES),
        help="Path to seeded fixture workspace (default: tests/fixtures/smoke-workspace).",
    )
    parser.add_argument(
        "--keep-tmp",
        action="store_true",
        help="Keep the temporary workspace after the run.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    fixtures = Path(args.fixtures).resolve()

    if not fixtures.is_dir():
        print(
            json.dumps({"status": "fail", "error": f"Fixtures not found: {fixtures}"})
        )
        return 1

    # Copy fixtures to a temp dir so scripts can modify freely
    tmp_dir = Path(tempfile.mkdtemp(prefix="research-smoke-"))
    workspace = tmp_dir / "workspace"
    shutil.copytree(fixtures, workspace)

    results: list[dict] = []
    any_fail = False

    # Step 1: Validate workspace structure
    results.append(
        _run_script(
            SCRIPTS_DIR / "validate_research_workspace.py",
            ["--root", str(workspace)],
            "validate-workspace",
        )
    )
    if results[-1]["returncode"] != 0:
        any_fail = True

    # Step 2: Validate schemas against examples
    results.append(
        _run_script(
            SCRIPTS_DIR / "validate_schemas.py",
            [
                "--schemas-dir",
                str(PACK_ROOT / "schemas"),
                "--examples-dir",
                str(PACK_ROOT / "schemas" / "examples"),
            ],
            "validate-schemas",
        )
    )
    if results[-1]["returncode"] != 0:
        any_fail = True

    # Step 3: Lint evidence ledger
    evidence_file = workspace / "03_evidence" / "evidence-ledger.jsonl"
    results.append(
        _run_script(
            SKILLS_DIR / "research-evidence-ledger" / "scripts" / "evidence_lint.py",
            ["--input", str(evidence_file)],
            "lint-evidence",
        )
    )
    if results[-1]["returncode"] != 0:
        any_fail = True

    # Step 4: Lint excerpt notes
    notes_file = workspace / "02_notes" / "excerpt-notes.jsonl"
    results.append(
        _run_script(
            SKILLS_DIR / "research-note-capture" / "scripts" / "note_lint.py",
            ["--input", str(notes_file)],
            "lint-notes",
        )
    )
    if results[-1]["returncode"] != 0:
        any_fail = True

    # Step 5: Quality-gate report against evidence
    report_file = workspace / "06_outputs" / "report.md"
    results.append(
        _run_script(
            SKILLS_DIR
            / "research-quality-reviewer"
            / "scripts"
            / "report_quality_gate.py",
            ["--report", str(report_file), "--ledger", str(evidence_file)],
            "quality-gate",
        )
    )
    if results[-1]["returncode"] != 0:
        any_fail = True

    # Cleanup
    if not args.keep_tmp:
        shutil.rmtree(tmp_dir, ignore_errors=True)

    status = "fail" if any_fail else "pass"
    summary = {
        "status": status,
        "steps": len(results),
        "passed": sum(1 for r in results if r["returncode"] == 0),
        "failed": sum(1 for r in results if r["returncode"] != 0),
        "results": results,
    }

    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 1 if any_fail else 0


if __name__ == "__main__":
    raise SystemExit(main())
