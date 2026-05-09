#!/usr/bin/env python3
"""PEtFiSh Quality Gate — skill发布门禁。

依次运行lint、security audit、metadata验证，生成综合报告并给出发布决策。

Usage:
    uv run scripts/run_gate.py --path <skill-directory>
    uv run scripts/run_gate.py --path <directory> --recursive
    uv run scripts/run_gate.py --path <skill-directory> --json
"""

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from datetime import datetime


def find_sibling_script(script_name: str) -> str | None:
    """Find a sibling skill's script relative to this script's location."""
    this_dir = Path(__file__).resolve().parent  # scripts/
    # this_dir.parent = quality-gate/, this_dir.parent.parent = skills/
    skills_dir = this_dir.parent.parent
    # Try: skills_dir / <skill-name> / scripts / <script>
    # e.g., skills_dir / skill-lint / scripts / lint_skill.py
    parts = script_name.split("/")
    if len(parts) == 2:
        candidate = skills_dir / parts[0] / "scripts" / parts[1]
    else:
        candidate = skills_dir / script_name
    return str(candidate) if candidate.exists() else None


def run_lint(skill_path: str) -> dict:
    """Run skill-lint and return results."""
    lint_script = find_sibling_script("skill-lint/lint_skill.py")
    if not lint_script:
        return {
            "score": -1,
            "passed": False,
            "error": "skill-lint script not found",
            "findings": [],
        }

    try:
        result = subprocess.run(
            [sys.executable, lint_script, "--path", skill_path, "--json"],
            capture_output=True,
            text=True,
            timeout=60,
        )
        if result.stdout.strip():
            data = json.loads(result.stdout.strip())
            score = data.get("score", 0)
            return {
                "score": score,
                "passed": score >= 80,
                "findings": data.get("findings", []),
                "raw": data,
            }
        else:
            return {
                "score": 0,
                "passed": False,
                "error": result.stderr.strip() or "lint failed",
                "findings": [],
            }
    except (subprocess.TimeoutExpired, json.JSONDecodeError, Exception) as e:
        return {"score": -1, "passed": False, "error": str(e), "findings": []}


def run_security_audit(skill_path: str) -> dict:
    """Run skill-security-auditor and return results."""
    audit_script = find_sibling_script("skill-security-auditor/audit_skill.py")
    if not audit_script:
        # Fallback: do basic inline security checks
        return run_basic_security_check(skill_path)

    try:
        result = subprocess.run(
            [sys.executable, audit_script, "--path", skill_path, "--json"],
            capture_output=True,
            text=True,
            timeout=60,
        )
        if result.returncode in (0, 1) and result.stdout.strip():
            data = json.loads(result.stdout.strip())
            # Unwrap auditor's results array if present
            if (
                "results" in data
                and isinstance(data["results"], list)
                and data["results"]
            ):
                skill_data = data["results"][0]
            else:
                skill_data = data
            risk_score = skill_data.get("risk_score", 1.0)
            summary = skill_data.get("summary", {})
            critical_count = summary.get("critical", 0)
            findings = skill_data.get("findings", [])
            return {
                "risk_score": risk_score,
                "passed": risk_score <= 0.5 and critical_count == 0,
                "critical_count": critical_count,
                "findings": findings,
                "raw": data,
            }
        else:
            return run_basic_security_check(skill_path)
    except (subprocess.TimeoutExpired, json.JSONDecodeError, Exception):
        return run_basic_security_check(skill_path)


DANGEROUS_PATTERNS = [
    (r"\brm\s+-rf\b", "CRITICAL", "Recursive force delete"),
    (r"\bcurl\b.*\|\s*bash\b", "CRITICAL", "Remote code execution via curl|bash"),
    (r"\beval\s*\(", "HIGH", "Dynamic eval execution"),
    (r"\bexec\s*\(", "HIGH", "Dynamic exec execution"),
    (r"\bos\.system\s*\(", "HIGH", "os.system call"),
    (r"shell\s*=\s*True", "MEDIUM", "subprocess with shell=True"),
    (r"\.env\b", "MEDIUM", "Potential .env file access"),
    (r"\.ssh\b", "HIGH", "Potential SSH key access"),
    (r"\bsudo\b", "HIGH", "Sudo command usage"),
    (r"\bchmod\s+777\b", "HIGH", "World-writable permissions"),
]


def run_basic_security_check(skill_path: str) -> dict:
    """Basic fallback security check when audit_skill.py is not available."""
    findings = []
    skill_dir = Path(skill_path)

    for fpath in skill_dir.rglob("*"):
        if not fpath.is_file():
            continue
        if fpath.suffix not in (".py", ".sh", ".ps1", ".md"):
            continue
        try:
            content = fpath.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue

        for pattern, severity, desc in DANGEROUS_PATTERNS:
            for match in re.finditer(pattern, content):
                line_num = content[: match.start()].count("\n") + 1
                findings.append(
                    {
                        "file": str(fpath.relative_to(skill_dir)),
                        "line": line_num,
                        "severity": severity,
                        "message": desc,
                        "match": match.group()[:50],
                    }
                )

    severity_weights = {"CRITICAL": 1.0, "HIGH": 0.6, "MEDIUM": 0.3, "LOW": 0.1}
    total_weight = sum(severity_weights.get(f["severity"], 0) for f in findings)
    risk_score = min(1.0, total_weight / 10)
    critical_count = sum(1 for f in findings if f["severity"] == "CRITICAL")

    return {
        "risk_score": round(risk_score, 2),
        "passed": risk_score <= 0.5 and critical_count == 0,
        "critical_count": critical_count,
        "findings": findings,
        "fallback": True,
    }


def validate_metadata(skill_path: str) -> dict:
    """Validate skill metadata (name, version, description)."""
    skill_md = Path(skill_path) / "SKILL.md"
    issues = []

    if not skill_md.exists():
        return {
            "passed": False,
            "issues": [{"severity": "ERROR", "message": "SKILL.md not found"}],
        }

    try:
        content = skill_md.read_text(encoding="utf-8")
    except Exception as e:
        return {
            "passed": False,
            "issues": [{"severity": "ERROR", "message": f"Cannot read SKILL.md: {e}"}],
        }

    # Extract frontmatter
    fm_match = re.match(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
    if not fm_match:
        issues.append({"severity": "ERROR", "message": "No frontmatter found"})
        return {"passed": False, "issues": issues}

    fm = fm_match.group(1)

    # Check name
    name_match = re.search(r"^name:\s*(.+)$", fm, re.MULTILINE)
    if not name_match:
        issues.append({"severity": "ERROR", "message": "Missing 'name' in frontmatter"})
    else:
        name = name_match.group(1).strip()
        if not re.match(r"^[a-z][a-z0-9-]*$", name):
            issues.append(
                {
                    "severity": "ERROR",
                    "message": f"Invalid name '{name}': must be lowercase kebab-case",
                }
            )
        if len(name) > 64:
            issues.append(
                {
                    "severity": "ERROR",
                    "message": f"Name too long ({len(name)} chars, max 64)",
                }
            )

    # Check description
    desc_match = re.search(
        r"^description:\s*[>|]?\s*\n((?:\s+.+\n)*)", fm, re.MULTILINE
    )
    if not desc_match:
        desc_match = re.search(r"^description:\s*(.+)$", fm, re.MULTILINE)
    if not desc_match:
        issues.append(
            {"severity": "ERROR", "message": "Missing 'description' in frontmatter"}
        )
    else:
        desc = desc_match.group(1).strip()
        if len(desc) > 1024:
            issues.append(
                {
                    "severity": "WARNING",
                    "message": f"Description too long ({len(desc)} chars, max 1024)",
                }
            )

    # Check version in metadata
    version_match = re.search(r"version:\s*(.+)$", fm, re.MULTILINE)
    if not version_match:
        issues.append(
            {"severity": "INFO", "message": "No version in metadata (recommended)"}
        )

    passed = all(i["severity"] != "ERROR" for i in issues)
    return {"passed": passed, "issues": issues}


def make_decision(
    lint_result: dict, security_result: dict, metadata_result: dict
) -> str:
    """Determine publish decision: PASS, CONDITIONAL, or FAIL."""
    if not metadata_result["passed"]:
        return "FAIL"
    if not lint_result["passed"]:
        return "FAIL"
    if security_result.get("critical_count", 0) > 0:
        return "FAIL"
    if security_result.get("risk_score", 1.0) > 0.5:
        return "FAIL"

    if security_result.get("risk_score", 1.0) > 0.3:
        return "CONDITIONAL"

    lint_score = lint_result.get("score", 0)
    if lint_score < 95:
        return "CONDITIONAL" if lint_score >= 80 else "FAIL"

    has_trigger_coverage_error = any(
        finding.get("type") == "trigger-coverage"
        and str(finding.get("severity", "")).lower() == "error"
        for finding in lint_result.get("findings", [])
        if isinstance(finding, dict)
    )
    if has_trigger_coverage_error:
        return "CONDITIONAL"

    return "PASS"


def gate_one_skill(
    skill_path: str, as_json: bool = False, fail_threshold: float = 0.5
) -> dict:
    """Run full quality gate on a single skill."""
    skill_name = Path(skill_path).name

    lint_result = run_lint(skill_path)
    security_result = run_security_audit(skill_path)
    metadata_result = validate_metadata(skill_path)
    decision = make_decision(lint_result, security_result, metadata_result)

    report = {
        "skill": skill_name,
        "path": str(skill_path),
        "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "lint": {
            "score": lint_result.get("score", -1),
            "passed": lint_result.get("passed", False),
            "error": lint_result.get("error"),
            "finding_count": len(lint_result.get("findings", [])),
        },
        "security": {
            "risk_score": security_result.get("risk_score", -1),
            "passed": security_result.get("passed", False),
            "critical_count": security_result.get("critical_count", 0),
            "finding_count": len(security_result.get("findings", [])),
            "fallback": security_result.get("fallback", False),
        },
        "metadata": {
            "passed": metadata_result["passed"],
            "issues": metadata_result["issues"],
        },
        "decision": decision,
    }

    if not as_json:
        print_report(report, lint_result, security_result, metadata_result)

    return report


def print_report(
    report: dict, lint_result: dict, security_result: dict, metadata_result: dict
):
    """Print formatted quality gate report."""
    d = report
    lint_icon = "✅" if d["lint"]["passed"] else "❌"
    sec_icon = "✅" if d["security"]["passed"] else "❌"
    meta_icon = "✅" if d["metadata"]["passed"] else "❌"

    decision_icon = {"PASS": "✅", "CONDITIONAL": "⚠️", "FAIL": "❌"}.get(
        d["decision"], "?"
    )

    print(f"""
┌──────────────────────────────────────────┐
│  ><(((^>  Quality Gate Report            │
├──────────────────────────────────────────┤
│  Skill:    {d["skill"]:<29}│
│  Date:     {d["date"]:<29}│
│                                          │
│  ① Lint:     {str(d["lint"]["score"]):<8}{lint_icon:<21}│
│  ② Security: {str(d["security"]["risk_score"]):<8}{sec_icon:<21}│
│  ③ Metadata: {"OK" if d["metadata"]["passed"] else "FAIL":<8}{meta_icon:<21}│
│                                          │
│  Decision:  {decision_icon} {d["decision"]:<26}│
└──────────────────────────────────────────┘""")

    # Print details
    if d["lint"].get("error"):
        print(f"\n  Lint error: {d['lint']['error']}")

    if lint_result.get("findings"):
        print(f"\n  Lint findings ({d['lint']['finding_count']}):")
        for f in lint_result["findings"][:10]:
            sev = f.get("severity", "INFO")
            msg = f.get("message", str(f))
            print(f"    [{sev}] {msg}")

    if security_result.get("findings"):
        print(f"\n  Security findings ({d['security']['finding_count']}):")
        for f in security_result["findings"][:10]:
            sev = f.get("severity", "INFO")
            msg = f.get("message", str(f))
            loc = f.get("file", "")
            line = f.get("line", "")
            loc_str = f" ({loc}:{line})" if loc else ""
            print(f"    [{sev}] {msg}{loc_str}")

    if metadata_result.get("issues"):
        print(f"\n  Metadata issues:")
        for i in metadata_result["issues"]:
            print(f"    [{i['severity']}] {i['message']}")

    if d["security"].get("fallback"):
        print(
            "\n  ⚠️  Security audit used fallback (basic checks only). Install skill-security-auditor for full audit."
        )

    print()


def find_skill_dirs(base_path: str) -> list[str]:
    """Find all skill directories under base_path."""
    base = Path(base_path)
    dirs = []
    for p in sorted(base.iterdir()):
        if p.is_dir() and (p / "SKILL.md").exists():
            dirs.append(str(p))
    return dirs


def main():
    parser = argparse.ArgumentParser(
        description="PEtFiSh Quality Gate — skill发布门禁",
        epilog="Example: uv run scripts/run_gate.py --path .opencode/skills/my-skill/",
    )
    parser.add_argument(
        "--path",
        required=True,
        help="Skill directory (or parent directory with --recursive)",
    )
    parser.add_argument(
        "--json", action="store_true", dest="as_json", help="Output as JSON"
    )
    parser.add_argument(
        "--recursive", action="store_true", help="Scan all skills in directory"
    )
    parser.add_argument(
        "--fail-threshold",
        type=float,
        default=0.5,
        help="Security risk score threshold for FAIL (default: 0.5)",
    )

    args = parser.parse_args()
    skill_path = os.path.abspath(args.path)

    if not os.path.isdir(skill_path):
        print(f"Error: '{skill_path}' is not a directory", file=sys.stderr)
        sys.exit(1)

    if args.recursive:
        skill_dirs = find_skill_dirs(skill_path)
        if not skill_dirs:
            print(f"No skills found in '{skill_path}'", file=sys.stderr)
            sys.exit(1)

        results = []
        for sd in skill_dirs:
            report = gate_one_skill(
                sd, as_json=args.as_json, fail_threshold=args.fail_threshold
            )
            results.append(report)

        if args.as_json:
            summary = {
                "total": len(results),
                "pass": sum(1 for r in results if r["decision"] == "PASS"),
                "conditional": sum(
                    1 for r in results if r["decision"] == "CONDITIONAL"
                ),
                "fail": sum(1 for r in results if r["decision"] == "FAIL"),
                "results": results,
            }
            print(json.dumps(summary, indent=2, ensure_ascii=False))
        else:
            # Print summary
            pass_count = sum(1 for r in results if r["decision"] == "PASS")
            cond_count = sum(1 for r in results if r["decision"] == "CONDITIONAL")
            fail_count = sum(1 for r in results if r["decision"] == "FAIL")
            print(f"\n{'=' * 42}")
            print(f"  Summary: {len(results)} skills scanned")
            print(
                f"  ✅ PASS: {pass_count}  ⚠️ CONDITIONAL: {cond_count}  ❌ FAIL: {fail_count}"
            )
            print(f"{'=' * 42}\n")

        any_fail = any(r["decision"] == "FAIL" for r in results)
        sys.exit(1 if any_fail else 0)
    else:
        # Single skill
        if not (Path(skill_path) / "SKILL.md").exists():
            print(f"Error: No SKILL.md found in '{skill_path}'", file=sys.stderr)
            sys.exit(1)

        report = gate_one_skill(
            skill_path, as_json=args.as_json, fail_threshold=args.fail_threshold
        )

        if args.as_json:
            print(json.dumps(report, indent=2, ensure_ascii=False))

        sys.exit(0 if report["decision"] != "FAIL" else 1)


if __name__ == "__main__":
    main()
