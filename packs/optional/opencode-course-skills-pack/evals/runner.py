#!/usr/bin/env python3
"""Course pack evals runner.

Per scenario: qa_scan (subprocess) + expected-constraint validation +
pedagogy-rule checks + optional LLM judge -> report.md + exit code.

Modes:
  static  - qa_scan + constraint/pedagogy checks only (no API key needed)
  judge   - static + LLM-as-judge (requires JUDGE_API_URL/JUDGE_API_KEY)
  auto    - judge when configured, otherwise degrade to static (judge marked skip)

Exit codes: 0 = all scenarios pass, 1 = threshold not met / failures,
2 = configuration error.

Selftest: --selftest runs static mode against all scenarios and asserts
expect=="pass" scenarios pass and expect=="fail" scenarios fail.

Stdlib only; runnable via `uv run --no-project python evals/runner.py`.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path

EVALS_DIR = Path(__file__).resolve().parent
PACK_DIR = EVALS_DIR.parent
QA_SCAN = (
    PACK_DIR
    / ".opencode"
    / "skills"
    / "course-quality-assurance"
    / "scripts"
    / "qa_scan.py"
)
SCENARIOS_DIR = EVALS_DIR / "scenarios"
DEFAULT_REPORT = EVALS_DIR / "report.md"
DEFAULT_THRESHOLD = 4.0

# Import reusable helpers from qa_scan.py (single source of truth for
# module-file detection, hours parsing, lab counting, alias tables).
sys.path.insert(0, str(QA_SCAN.parent))
import qa_scan  # noqa: E402

sys.path.insert(0, str(EVALS_DIR))
import judge  # noqa: E402

BLOCKING_SEVERITIES = {"blocker", "major"}


def load_scenarios(scenarios_dir: Path) -> list[dict]:
    scenarios = []
    for path in sorted(scenarios_dir.glob("*.json")):
        scenarios.append(json.loads(path.read_text(encoding="utf-8")))
    return scenarios


def resolve_course_root(scenario: dict, outline_arg: str | None) -> Path:
    """Course root: --outline file (walk up to the dir containing docs/)
    or the scenario's golden fixture directory."""
    if outline_arg:
        outline = Path(outline_arg).resolve()
        if outline.is_dir():
            return outline
        for parent in [outline.parent, *outline.parents]:
            if (parent / "docs").is_dir():
                return parent
        raise RuntimeError(
            f"cannot locate course root (docs/ dir) above outline file: {outline}"
        )
    golden = scenario.get("golden")
    if not golden:
        raise RuntimeError(f"scenario {scenario.get('id')} has no 'golden' path")
    return (EVALS_DIR / golden).resolve()


def run_qa_scan(root: Path) -> dict:
    env = dict(os.environ, PYTHONIOENCODING="utf-8")
    proc = subprocess.run(
        [sys.executable, str(QA_SCAN), "--root", str(root), "--emit", "json"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=env,
    )
    if proc.returncode != 0:
        raise RuntimeError(f"qa_scan failed on {root}: {proc.stderr[:500]}")
    return json.loads(proc.stdout)


def _in_range(value: float, bounds: dict) -> bool:
    lo, hi = bounds.get("min"), bounds.get("max")
    if isinstance(lo, (int, float)) and value < float(lo):
        return False
    if isinstance(hi, (int, float)) and value > float(hi):
        return False
    return True


def check_constraints(root: Path, expected: dict) -> list[str]:
    """Validate expected_constraints against the actual course structure."""
    violations: list[str] = []
    outline_dir = root / "docs" / "01-outline"
    outline_files = qa_scan.md_files_under(outline_dir)
    outline_text = "\n".join(qa_scan.read_text(p) for p in outline_files)
    module_files = qa_scan.detect_module_files(outline_files)

    bounds = expected.get("module_count")
    if isinstance(bounds, dict):
        if not module_files:
            violations.append("no module files detected under docs/01-outline")
        elif not _in_range(len(module_files), bounds):
            violations.append(
                f"module count {len(module_files)} outside "
                f"[{bounds.get('min')}, {bounds.get('max')}]"
            )

    th = expected.get("total_hours")
    if isinstance(th, dict):
        hours = qa_scan.declared_total_hours(outline_text)
        if hours is None:
            violations.append("no total hours declared in outline")
        elif not _in_range(hours, th):
            violations.append(
                f"total hours {hours} outside [{th.get('min')}, {th.get('max')}]"
            )

    lr = expected.get("lab_ratio")
    if isinstance(lr, dict) and module_files:
        ratio = qa_scan.count_labs(root / "docs" / "03-labs") / len(module_files)
        if not _in_range(ratio, lr):
            violations.append(
                f"lab ratio {ratio:.2f} outside [{lr.get('min')}, {lr.get('max')}]"
            )

    for atype in expected.get("required_assessment_types", []):
        aliases = qa_scan.ASSESSMENT_ALIASES.get(str(atype), [str(atype)])
        if not any(re.search(re.escape(a), outline_text, flags=re.IGNORECASE) for a in aliases):
            violations.append(f"required assessment type '{atype}' not declared in outline")

    return violations


def check_pedagogy_rules(root: Path, rules: list[dict], expected: dict) -> list[dict]:
    """Check pedagogy rules. Returns per-rule results; unknown rule ids fail
    loudly (no silent green)."""
    outline_dir = root / "docs" / "01-outline"
    module_files = qa_scan.detect_module_files(qa_scan.md_files_under(outline_dir))
    results: list[dict] = []
    for rule in rules:
        rid = rule.get("id", "")
        desc = rule.get("description", rid)
        if rid == "module-objectives":
            missing = [
                p.name
                for p in module_files
                if not re.search(r"目标|objective", qa_scan.read_text(p), flags=re.IGNORECASE)
            ]
            ok = bool(module_files) and not missing
            detail = "all modules declare objectives" if ok else (
                "modules missing objectives: " + ", ".join(missing) if missing
                else "no module files found"
            )
        elif rid == "first-module-introduction":
            aliases = qa_scan.FIRST_MODULE_TYPE_ALIASES["introduction"]
            if module_files:
                first = module_files[0]
                haystack = (first.stem + "\n" + qa_scan.read_text(first)[:500]).lower()
                ok = any(a in haystack for a in aliases)
                detail = f"first module: {first.name}"
            else:
                ok, detail = False, "no module files found"
        elif rid == "lab-ratio-in-range":
            bounds = expected.get("lab_ratio", {"min": 0.2, "max": 0.6})
            if module_files:
                ratio = qa_scan.count_labs(root / "docs" / "03-labs") / len(module_files)
                ok = _in_range(ratio, bounds)
                detail = f"lab ratio {ratio:.2f} vs [{bounds.get('min')}, {bounds.get('max')}]"
            else:
                ok, detail = False, "no module files found"
        else:
            ok, detail = False, f"no checker implemented for rule id '{rid}'"
        results.append({"id": rid, "description": desc, "pass": ok, "detail": detail})
    return results


def outline_text_of(root: Path) -> str:
    files = qa_scan.md_files_under(root / "docs" / "01-outline")
    return "\n\n".join(qa_scan.read_text(p) for p in files)


def evaluate_scenario(
    scenario: dict, mode: str, threshold: float, outline_arg: str | None
) -> dict:
    root = resolve_course_root(scenario, outline_arg)
    qa = run_qa_scan(root)
    blocking = [i for i in qa["issues"] if i["severity"] in BLOCKING_SEVERITIES]

    expected = scenario.get("expected_constraints", {})
    constraint_violations = check_constraints(root, expected)
    rule_results = check_pedagogy_rules(
        root, scenario.get("pedagogy_rules", []), expected
    )
    rule_failures = [r for r in rule_results if not r["pass"]]

    static_pass = not blocking and not constraint_violations and not rule_failures

    judge_result: dict | None = None
    judge_status = "skipped"
    if mode == "judge":
        rules_text = [
            r.get("description", r.get("id", ""))
            for r in scenario.get("pedagogy_rules", [])
        ]
        judge_result = judge.judge_outline(
            scenario.get("brief", ""), outline_text_of(root), rules_text, threshold
        )
        judge_status = "pass" if judge_result["pass"] else "fail"

    overall_pass = static_pass and judge_status != "fail"
    return {
        "id": scenario.get("id"),
        "expect": scenario.get("expect", "pass"),
        "course_root": str(root),
        "qa": {"status": qa["status"], "score": qa["score"], "issues": qa["issues"]},
        "blocking_issues": blocking,
        "constraint_violations": constraint_violations,
        "pedagogy_rules": rule_results,
        "static_pass": static_pass,
        "judge_status": judge_status,
        "judge": judge_result,
        "pass": overall_pass,
    }


def render_report(results: list[dict], mode: str, threshold: float) -> str:
    lines = [
        "# Course Pack Evals Report",
        "",
        f"- mode: `{mode}`",
        f"- judge threshold: mean >= {threshold}",
        f"- judge prompt version: {judge.JUDGE_PROMPT_VERSION}",
        "",
        "| scenario | expect | qa score | static | judge | overall |",
        "|---|---|---|---|---|---|",
    ]
    for r in results:
        judge_cell = r["judge_status"]
        if r["judge"]:
            judge_cell = f"{r['judge_status']} (mean {r['judge']['mean']})"
        lines.append(
            f"| {r['id']} | {r['expect']} | {r['qa']['score']} | "
            f"{'pass' if r['static_pass'] else 'fail'} | {judge_cell} | "
            f"{'PASS' if r['pass'] else 'FAIL'} |"
        )
    for r in results:
        lines += ["", f"## {r['id']}", ""]
        if r["blocking_issues"]:
            lines.append("qa_scan blocking issues:")
            for i in r["blocking_issues"]:
                lines.append(f"- [{i['severity']}/{i['class']}] {i['file']}: {i['description']}")
        if r["constraint_violations"]:
            lines.append("constraint violations:")
            for v in r["constraint_violations"]:
                lines.append(f"- {v}")
        failed_rules = [x for x in r["pedagogy_rules"] if not x["pass"]]
        if failed_rules:
            lines.append("pedagogy rule failures:")
            for x in failed_rules:
                lines.append(f"- {x['id']} ({x['description']}): {x['detail']}")
        if r["judge"]:
            lines.append("judge scores:")
            for dim, score in r["judge"]["scores"].items():
                lines.append(f"- {dim}: {score}")
            lines.append(f"- mean: {r['judge']['mean']} (threshold {r['judge']['threshold']})")
        if not (r["blocking_issues"] or r["constraint_violations"] or failed_rules or r["judge"]):
            lines.append("no findings.")
    lines.append("")
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Course pack evals runner.")
    parser.add_argument("--mode", choices=["static", "judge", "auto"], default="auto")
    parser.add_argument("--outline", help="Evaluate scenarios against this outline "
                        "file (or course root dir) instead of golden fixtures.")
    parser.add_argument("--threshold", type=float, default=DEFAULT_THRESHOLD,
                        help="Judge pass threshold on rubric mean (default 4.0).")
    parser.add_argument("--scenarios-dir", default=str(SCENARIOS_DIR))
    parser.add_argument("--report", default=str(DEFAULT_REPORT))
    parser.add_argument("--selftest", action="store_true",
                        help="Static mode + assert expect fields (golden pass, "
                             "violations fail).")
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    mode = args.mode
    if args.selftest:
        mode = "static"
    elif mode == "auto":
        mode = "judge" if judge.have_judge_config() else "static"
        if mode == "static":
            print("auto mode: no JUDGE_API_KEY/JUDGE_API_URL, degraded to static "
                  "(judge items marked skip, not scored)")

    if mode == "judge" and not judge.have_judge_config():
        print("error: --mode judge requires JUDGE_API_URL and JUDGE_API_KEY",
              file=sys.stderr)
        return 2

    scenarios = load_scenarios(Path(args.scenarios_dir))
    if not scenarios:
        print(f"error: no scenarios in {args.scenarios_dir}", file=sys.stderr)
        return 2

    if args.selftest:
        runnable = scenarios
    else:
        # expect=="fail" scenarios are negative fixtures for selftest only;
        # running them in gate mode would always break the build.
        runnable = [s for s in scenarios if s.get("expect", "pass") == "pass"]
        skipped = [s["id"] for s in scenarios if s.get("expect") == "fail"]
        if skipped:
            print(f"skipping negative fixtures (selftest-only): {', '.join(skipped)}")

    results = [evaluate_scenario(s, mode, args.threshold, args.outline) for s in runnable]

    report_path = Path(args.report)
    report_path.write_text(render_report(results, mode, args.threshold), encoding="utf-8")
    print(f"report written: {report_path}")

    if args.selftest:
        failures = []
        for r in results:
            ok = r["pass"] if r["expect"] == "pass" else not r["pass"]
            status = "OK" if ok else "ASSERTION-FAIL"
            print(f"[selftest] {r['id']}: expect={r['expect']} actual="
                  f"{'pass' if r['pass'] else 'fail'} -> {status}")
            if not ok:
                failures.append(r["id"])
        if failures:
            print(f"selftest FAILED: {', '.join(failures)}")
            return 1
        print(f"selftest PASSED: {len(results)} scenarios behaved as expected")
        return 0

    failed = [r["id"] for r in results if not r["pass"]]
    for r in results:
        print(f"[{mode}] {r['id']}: {'PASS' if r['pass'] else 'FAIL'} "
              f"(qa score {r['qa']['score']}, judge {r['judge_status']})")
    if failed:
        print(f"evals FAILED: {', '.join(failed)}")
        return 1
    print(f"evals PASSED: {len(results)} scenarios")
    return 0


if __name__ == "__main__":
    sys.exit(main())
