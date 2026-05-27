#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = []
# ///
"""Static security audit for OpenCode-style skills."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path

SEVERITY_ORDER = {"info": 0, "low": 1, "medium": 2, "high": 3, "critical": 4}
SEVERITY_WEIGHTS = {
    "info": 0.0,
    "low": 0.1,
    "medium": 0.3,
    "high": 0.6,
    "critical": 1.0,
}
EXECUTABLE_FENCE_LANGS = {
    "bash",
    "sh",
    "shell",
    "zsh",
    "fish",
    "powershell",
    "ps1",
    "cmd",
    "bat",
    "python",
}


@dataclass
class Finding:
    severity: str
    category: str
    rule_id: str
    file: str
    line: int
    message: str
    remediation: str

    def to_dict(self) -> dict[str, object]:
        return {
            "severity": self.severity,
            "category": self.category,
            "rule_id": self.rule_id,
            "file": self.file,
            "line": self.line,
            "message": self.message,
            "remediation": self.remediation,
        }


@dataclass
class AuditResult:
    skill: str
    path: str
    risk_score: float
    fail_threshold: float
    verdict: str
    summary: dict[str, int]
    findings: list[Finding]

    def to_dict(self, minimum_severity: str) -> dict[str, object]:
        visible = filter_findings(self.findings, minimum_severity)
        return {
            "skill": self.skill,
            "path": self.path,
            "risk_score": self.risk_score,
            "fail_threshold": self.fail_threshold,
            "verdict": self.verdict,
            "summary": self.summary,
            "display_filter": minimum_severity,
            "displayed_findings": len(visible),
            "findings": [finding.to_dict() for finding in visible],
        }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Statically audit a skill directory for security risks. "
            "Scans SKILL.md, scripts/, references/, and tool-scope language."
        )
    )
    parser.add_argument("--path", required=True, help="Skill directory or skills root")
    parser.add_argument("--json", action="store_true", help="Emit JSON output")
    parser.add_argument(
        "--severity",
        choices=["critical", "high", "medium", "low", "all"],
        default="all",
        help="Minimum severity to display; 'all' includes info findings",
    )
    parser.add_argument(
        "--recursive",
        action="store_true",
        help="Scan all skills found below --path",
    )
    parser.add_argument(
        "--fail-threshold",
        type=float,
        default=0.5,
        help="Risk score threshold at or above which the audit fails",
    )
    return parser.parse_args()


def normalize_scalar(value: str) -> str:
    stripped = value.strip()
    if not stripped:
        return ""
    if (stripped.startswith('"') and stripped.endswith('"')) or (
        stripped.startswith("'") and stripped.endswith("'")
    ):
        return stripped[1:-1]
    return stripped


def extract_frontmatter(text: str) -> tuple[dict[str, object], str]:
    clean = text.lstrip("\ufeff")
    match = re.match(r"^---\s*\r?\n(.*?)\r?\n---\s*(?:\r?\n|$)", clean, re.S)
    if not match:
        return {}, clean

    block = match.group(1)
    body = clean[match.end() :]
    lines = block.splitlines()
    data: dict[str, object] = {}
    stack: list[tuple[int, dict[str, object]]] = [(0, data)]
    index = 0

    while index < len(lines):
        raw_line = lines[index]
        if not raw_line.strip() or raw_line.lstrip().startswith("#"):
            index += 1
            continue

        indent = len(raw_line) - len(raw_line.lstrip(" "))
        stripped = raw_line.strip()

        while len(stack) > 1 and indent < stack[-1][0]:
            stack.pop()

        if ":" not in stripped:
            index += 1
            continue

        key, raw_value = stripped.split(":", 1)
        key = key.strip()
        raw_value = raw_value.strip()
        parent = stack[-1][1]

        if raw_value in {">", "|"}:
            index += 1
            block_indent = None
            collected: list[str] = []
            while index < len(lines):
                next_line = lines[index]
                if not next_line.strip():
                    collected.append("")
                    index += 1
                    continue

                next_indent = len(next_line) - len(next_line.lstrip(" "))
                if next_indent <= indent and block_indent is None:
                    break
                if block_indent is None:
                    block_indent = next_indent
                if next_indent < block_indent:
                    break
                collected.append(next_line[block_indent:])
                index += 1

            if raw_value == ">":
                value = " ".join(part.strip() for part in collected if part.strip())
            else:
                value = "\n".join(collected).rstrip()
            parent[key] = value
            continue

        if raw_value == "":
            nested: dict[str, object] = {}
            parent[key] = nested
            stack.append((indent + 2, nested))
            index += 1
            continue

        parent[key] = normalize_scalar(raw_value)
        index += 1

    return data, body


def safe_read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return ""


def relative_display(path: Path) -> str:
    try:
        return os.path.relpath(path, Path.cwd())
    except ValueError:
        return str(path)


def count_summary(findings: list[Finding]) -> dict[str, int]:
    summary = {key: 0 for key in ["critical", "high", "medium", "low", "info"]}
    for finding in findings:
        summary[finding.severity] += 1
    return summary


def filter_findings(findings: list[Finding], minimum_severity: str) -> list[Finding]:
    if minimum_severity == "all":
        return sorted(findings, key=sort_key, reverse=True)
    threshold = SEVERITY_ORDER[minimum_severity]
    return sorted(
        [
            finding
            for finding in findings
            if SEVERITY_ORDER[finding.severity] >= threshold
        ],
        key=sort_key,
        reverse=True,
    )


def sort_key(finding: Finding) -> tuple[int, str, int, str]:
    return (
        SEVERITY_ORDER[finding.severity],
        finding.file,
        -finding.line,
        finding.rule_id,
    )


def calculate_risk_score(findings: list[Finding]) -> float:
    weighted_findings = [
        finding for finding in findings if SEVERITY_WEIGHTS[finding.severity] > 0
    ]
    if not weighted_findings:
        return 0.0
    total_weight = sum(
        SEVERITY_WEIGHTS[finding.severity] for finding in weighted_findings
    )
    normalized = total_weight / len(weighted_findings)
    return round(min(1.0, normalized), 2)


def add_finding(
    findings: list[Finding],
    severity: str,
    category: str,
    rule_id: str,
    file_path: Path,
    line: int,
    message: str,
    remediation: str,
) -> None:
    findings.append(
        Finding(
            severity=severity,
            category=category,
            rule_id=rule_id,
            file=relative_display(file_path),
            line=line,
            message=message,
            remediation=remediation,
        )
    )


def first_line_match(text: str, pattern: str, flags: int = 0) -> int:
    regex = re.compile(pattern, flags)
    for line_number, line in enumerate(text.splitlines(), start=1):
        if regex.search(line):
            return line_number
    return 1


def scan_skill_markdown(skill_path: Path, text: str, findings: list[Finding]) -> None:
    frontmatter, body = extract_frontmatter(text)
    description = str(frontmatter.get("description", ""))
    combined = f"{description}\n{body}"

    checks = [
        (
            r"(?i)ignore\s+(all\s+)?previous\s+instructions|disregard\s+earlier\s+instructions",
            "high",
            "prompt_injection",
            "PI001",
            "Instruction override language detected in SKILL.md.",
            "Remove override phrases and describe safe boundaries explicitly.",
        ),
        (
            r"(?i)reveal\s+(the\s+)?(system|developer|hidden)\s+prompt|print\s+environment\s+variables|dump\s+secrets",
            "critical",
            "prompt_injection",
            "PI002",
            "SKILL.md appears to request prompt or secret disclosure.",
            "Ban secret disclosure instructions and replace them with privacy-safe guidance.",
        ),
        (
            r"(?i)skip\s+approval|assume\s+approval|auto[- ]approve|without\s+confirmation|bypass\s+safeguards",
            "high",
            "prompt_injection",
            "PI003",
            "Approval bypass language detected in SKILL.md.",
            "Require explicit user confirmation for destructive, privileged, or networked actions.",
        ),
        (
            r"(?i)\b(any|all)\b.{0,30}\b(tools?|mcp|servers?)\b|unrestricted\s+(tools?|mcp|server)",
            "high",
            "mcp_tools",
            "MT001",
            "Overly broad tool or MCP scope detected in SKILL.md.",
            "List exact tools or servers and explain why each one is required.",
        ),
        (
            r"(?i)curl\b.{0,120}\|\s*(bash|sh)|wget\b.{0,120}\|\s*(bash|sh)|invoke-expression",
            "critical",
            "network",
            "NW001",
            "Remote download-and-execute pattern documented in SKILL.md.",
            "Split download from execution and require manual review before running fetched content.",
        ),
        (
            r"(?i)\brm\s+-rf\b|\bdd\s+if=|format-volume|diskpart|mkfs\b",
            "critical",
            "file_system",
            "FS001",
            "Destructive system command appears in SKILL.md.",
            "Remove destructive examples or mark them as forbidden patterns instead of recommended actions.",
        ),
        (
            r"(?i)\.env\b|\.ssh\b|id_rsa\b|api[_-]?key\b|access[_-]?token\b|bearer\b",
            "high",
            "credentials",
            "CR001",
            "Sensitive credential access language detected in SKILL.md.",
            "Avoid reading secret-bearing files or tokens unless the user explicitly provides a safe path and reason.",
        ),
    ]

    for pattern, severity, category, rule_id, message, remediation in checks:
        match = re.search(pattern, combined, re.I | re.S)
        if match:
            line = combined[: match.start()].count("\n") + 1
            add_finding(
                findings,
                severity,
                category,
                rule_id,
                skill_path,
                line,
                message,
                remediation,
            )

    if description:
        description_checks = [
            (
                r"(?i)ignore\s+previous\s+instructions|override\s+system",
                "high",
                "prompt_injection",
                "PI004",
                "Prompt injection signal detected in the frontmatter description.",
                "Keep the description limited to purpose, trigger phrases, and safe scope.",
            ),
            (
                r"(?i)any\s+tool|all\s+tools|any\s+mcp|all\s+servers",
                "high",
                "mcp_tools",
                "MT002",
                "Description requests overly broad tools or MCP access.",
                "Describe the minimum tools required instead of open-ended access.",
            ),
        ]
        for (
            pattern,
            severity,
            category,
            rule_id,
            message,
            remediation,
        ) in description_checks:
            match = re.search(pattern, description, re.I)
            if match:
                line = first_line_match(text, pattern, re.I)
                add_finding(
                    findings,
                    severity,
                    category,
                    rule_id,
                    skill_path,
                    line,
                    message,
                    remediation,
                )


def scan_python_script(script_path: Path, text: str, findings: list[Finding]) -> None:
    rules = [
        (
            r"shutil\.rmtree\s*\(",
            "high",
            "file_system",
            "FS101",
            "Recursive deletion helper found in Python script.",
            "Gate recursive deletion behind explicit allowlists and dry-run support.",
        ),
        (
            r"(?:os\.(?:remove|unlink)|Path\([^\n]+\)\.unlink|pathlib\.Path\([^\n]+\)\.unlink)\s*\(",
            "medium",
            "file_system",
            "FS102",
            "Direct file deletion found in Python script.",
            "Validate targets carefully and avoid deletion over broad path sets.",
        ),
        (
            r"subprocess\.(?:run|call|Popen)\s*\([^\n]*shell\s*=\s*True",
            "medium",
            "execution",
            "EX101",
            "subprocess shell=True usage found in Python script.",
            "Prefer argument arrays and shell=False unless shell mode is truly required and documented.",
        ),
        (
            r"(?<!\.)\b(?:eval|exec|compile)\s*\(",
            "high",
            "execution",
            "EX102",
            "Dynamic code execution function found in Python script.",
            "Replace dynamic execution with explicit parsing or dispatch logic.",
        ),
        (
            r"os\.system\s*\(",
            "high",
            "execution",
            "EX103",
            "os.system usage found in Python script.",
            "Replace os.system with subprocess.run using explicit argument lists.",
        ),
        (
            r"""(?x)
                os\.environ\s*\[\s*['"][^'"]*(?:SECRET|TOKEN|KEY|PASSWORD|CREDENTIAL)[^'"]*['"]\s*\]
              | os\.environ\.get\s*\(\s*['"][^'"]*(?:SECRET|TOKEN|KEY|PASSWORD|CREDENTIAL)[^'"]*['"]
              | os\.getenv\s*\(\s*['"][^'"]*(?:SECRET|TOKEN|KEY|PASSWORD|CREDENTIAL)[^'"]*['"]
              | keyring\.get_password
              | \.read_text\s*\([^\n]*(?:\.env|\.ssh|id_rsa|known_hosts|credentials)
              | open\s*\([^\n]*(?:\.env|\.ssh[/\\]|id_rsa|known_hosts)
              | Path\s*\([^\n]*(?:\.env|\.ssh[/\\]|id_rsa|known_hosts)
            """,
            "high",
            "credentials",
            "CR101",
            "Potential secret or credential access pattern found in Python script.",
            "Remove secret harvesting logic or require explicit, narrowly scoped user-provided inputs.",
        ),
        (
            r"requests\.(?:get|post|put|delete|patch)\s*\(|urllib\.request\.(?:urlopen|Request)\s*\(",
            "medium",
            "network",
            "NW101",
            "Network call found in Python script.",
            "Document the purpose, limit destinations, and avoid sending local content unless required.",
        ),
        (
            r"\b(chmod|chown)\b|os\.chmod\s*\(|os\.chown\s*\(",
            "high",
            "permissions",
            "PM101",
            "Permission or ownership change found in Python script.",
            "Use least privilege and avoid broad permission changes.",
        ),
        (
            r"\bsudo\b",
            "high",
            "permissions",
            "PM102",
            "sudo usage marker found in Python script.",
            "Require explicit approval and avoid embedding privileged command flows.",
        ),
        (
            r"[A-Za-z]:\\|/Users/|/home/|/etc/|/var/",
            "low",
            "file_system",
            "FS103",
            "Hardcoded absolute path found in Python script.",
            "Accept paths through CLI arguments or resolve them from the workspace root.",
        ),
    ]

    for pattern, severity, category, rule_id, message, remediation in rules:
        line = first_line_match(text, pattern, re.I)
        if re.search(pattern, text, re.I):
            add_finding(
                findings,
                severity,
                category,
                rule_id,
                script_path,
                line,
                message,
                remediation,
            )

    remote_fetch = re.search(
        r"requests\.(?:get|post)|urllib\.request\.(?:urlopen|Request)|curl\b|wget\b",
        text,
        re.I,
    )
    remote_exec = re.search(
        r"(?<!\.)\b(?:eval|exec|compile)\s*\(|subprocess\.(?:run|call|Popen)|os\.system\s*\(|invoke-expression|bash\s+-c|sh\s+-c",
        text,
        re.I,
    )
    if remote_fetch and remote_exec:
        line = first_line_match(
            text,
            r"requests\.(?:get|post)|urllib\.request\.(?:urlopen|Request)|curl\b|wget\b",
            re.I,
        )
        add_finding(
            findings,
            "critical",
            "network",
            "NW102",
            script_path,
            line,
            "Script combines remote fetch capability with execution primitives.",
            "Separate fetch from execution and require review plus integrity checks before running downloaded content.",
        )

    if re.search(r"\b(glob|rglob)\s*\(", text) and re.search(
        r"(?:os\.(?:remove|unlink)|Path\([^\n]+\)\.unlink|shutil\.rmtree)", text
    ):
        line = first_line_match(text, r"\b(glob|rglob)\s*\(")
        add_finding(
            findings,
            "medium",
            "file_system",
            "FS104",
            script_path,
            line,
            "Broad globbing is combined with deletion logic in the script.",
            "Separate discovery from deletion and narrow the target pattern before any mutation.",
        )

    if (
        not re.search(r"add_argument\s*\([^\n]*--help", text)
        and "ArgumentParser(" not in text
    ):
        add_finding(
            findings,
            "low",
            "execution",
            "EX104",
            script_path,
            1,
            "Python helper script does not appear to expose a CLI parser or help entry point.",
            "Use argparse so the script provides predictable --help output.",
        )

    if re.search(r"write_text\s*\(|open\s*\([^\n]*['\"]w['\"]", text) and not re.search(
        r"--dry-run|dry_run|dryrun", text, re.I
    ):
        line = first_line_match(text, r"write_text\s*\(|open\s*\([^\n]*['\"]w['\"]")
        add_finding(
            findings,
            "low",
            "permissions",
            "PM103",
            script_path,
            line,
            "Script writes files without an obvious dry-run mode.",
            "Consider adding a preview or dry-run option for risky write paths.",
        )


def scan_shell_like_script(
    script_path: Path, text: str, findings: list[Finding]
) -> None:
    rules = [
        (
            r"\brm\s+-rf\b|Remove-Item\s+.+-Recurse.+-Force",
            "critical",
            "file_system",
            "FS201",
            "Destructive delete command found in shell-like script.",
            "Remove destructive commands or require tightly scoped explicit confirmation.",
        ),
        (
            r"curl\b.{0,120}\|\s*(bash|sh)|wget\b.{0,120}\|\s*(bash|sh)|Invoke-Expression",
            "critical",
            "network",
            "NW201",
            "Remote download-and-execute pattern found in shell-like script.",
            "Download for inspection only and never pipe remote content directly into execution.",
        ),
        (
            r"\.env\b|\.ssh\b|id_rsa\b|known_hosts\b|token\b|secret\b|api[_-]?key\b",
            "high",
            "credentials",
            "CR201",
            "Potential secret or credential access pattern found in shell-like script.",
            "Remove secret access or require explicit user-provided safe inputs.",
        ),
        (
            r"\bsudo\b|Start-Process\s+.+-Verb\s+RunAs",
            "high",
            "permissions",
            "PM201",
            "Privileged execution pattern found in shell-like script.",
            "Require explicit approval and document why elevated access is necessary.",
        ),
        (
            r"\b(chmod\s+777|chown\b)",
            "high",
            "permissions",
            "PM202",
            "Broad permission or ownership change found in shell-like script.",
            "Use least-privilege permissions and avoid world-writable settings.",
        ),
        (
            r"[A-Za-z]:\\|/Users/|/home/|/etc/|/var/",
            "low",
            "file_system",
            "FS202",
            "Hardcoded absolute path found in shell-like script.",
            "Parameterize paths and resolve them relative to a chosen root.",
        ),
    ]

    for pattern, severity, category, rule_id, message, remediation in rules:
        line = first_line_match(text, pattern, re.I)
        if re.search(pattern, text, re.I | re.S):
            add_finding(
                findings,
                severity,
                category,
                rule_id,
                script_path,
                line,
                message,
                remediation,
            )

    if not re.search(r"--help|-h", text):
        add_finding(
            findings,
            "low",
            "execution",
            "EX201",
            script_path,
            1,
            "Shell-like helper script does not appear to document --help behavior.",
            "Add a help branch or usage banner so operators can inspect behavior safely.",
        )


def scan_scripts(skill_dir: Path, findings: list[Finding]) -> None:
    scripts_dir = skill_dir / "scripts"
    if not scripts_dir.is_dir():
        return

    for script_path in scripts_dir.rglob("*"):
        if not script_path.is_file():
            continue
        text = safe_read_text(script_path)
        suffix = script_path.suffix.lower()
        if suffix == ".py":
            scan_python_script(script_path, text, findings)
        elif suffix in {".sh", ".ps1", ".cmd", ".bat"}:
            scan_shell_like_script(script_path, text, findings)


def scan_references(skill_dir: Path, findings: list[Finding]) -> None:
    references_dir = skill_dir / "references"
    if not references_dir.is_dir():
        return

    for ref_path in references_dir.rglob("*"):
        if not ref_path.is_file():
            continue

        suffix = ref_path.suffix.lower()
        text = safe_read_text(ref_path)

        if suffix in {".sh", ".ps1", ".cmd", ".bat", ".exe"}:
            add_finding(
                findings,
                "high",
                "execution",
                "EX301",
                ref_path,
                1,
                "Executable content exists under references/.",
                "Move runnable helpers into scripts/ and keep references/ explanatory only.",
            )

        if suffix in {".md", ".txt", ".rst"}:
            fence_match = re.search(
                r"```\s*([A-Za-z0-9_-]+)([\s\S]*?)```",
                text,
                re.M,
            )
            if fence_match and fence_match.group(1).lower() in EXECUTABLE_FENCE_LANGS:
                line = text[: fence_match.start()].count("\n") + 1
                add_finding(
                    findings,
                    "medium",
                    "execution",
                    "EX302",
                    ref_path,
                    line,
                    "references/ contains an executable-language code fence.",
                    "Prefer prose guidance in references/ and keep runnable helpers inside scripts/.",
                )

            shebang_match = re.search(r"^#!", text, re.M)
            if shebang_match:
                line = text[: shebang_match.start()].count("\n") + 1
                add_finding(
                    findings,
                    "medium",
                    "execution",
                    "EX303",
                    ref_path,
                    line,
                    "references/ contains a shebang or executable header.",
                    "Remove executable payloads from references/ or relocate them to scripts/.",
                )


def audit_skill(skill_dir: Path, fail_threshold: float) -> AuditResult:
    findings: list[Finding] = []
    skill_md = skill_dir / "SKILL.md"

    if not skill_md.is_file():
        add_finding(
            findings,
            "critical",
            "prompt_injection",
            "PI999",
            skill_dir,
            1,
            "Skill directory does not contain SKILL.md.",
            "Add a valid SKILL.md before auditing the skill.",
        )
    else:
        scan_skill_markdown(skill_md, safe_read_text(skill_md), findings)

    scan_scripts(skill_dir, findings)
    scan_references(skill_dir, findings)

    risk_score = calculate_risk_score(findings)
    verdict = "FAIL" if risk_score >= fail_threshold else "PASS"
    return AuditResult(
        skill=skill_dir.name,
        path=str(skill_dir.resolve()),
        risk_score=risk_score,
        fail_threshold=round(fail_threshold, 2),
        verdict=verdict,
        summary=count_summary(findings),
        findings=sorted(findings, key=sort_key, reverse=True),
    )


def discover_skills(root: Path, recursive: bool) -> list[Path]:
    if recursive:
        skills = sorted({skill_md.parent for skill_md in root.rglob("SKILL.md")})
        return skills

    if (root / "SKILL.md").is_file():
        return [root]

    if root.name.lower() == "skill.md" and root.is_file():
        return [root.parent]

    raise ValueError(
        "--path must point to a skill directory unless --recursive is used"
    )


def print_text_report(results: list[AuditResult], minimum_severity: str) -> None:
    for index, result in enumerate(results, start=1):
        if index > 1:
            print()
            print("-" * 72)
            print()

        visible = filter_findings(result.findings, minimum_severity)
        print(f"Security Audit Report :: {result.skill}")
        print(f"Path: {result.path}")
        print(f"TrustSkills risk score: {result.risk_score:.2f}")
        print(f"Fail threshold: {result.fail_threshold:.2f}")
        print(f"Verdict: {result.verdict}")
        print(
            "Severity counts: "
            f"critical={result.summary['critical']} "
            f"high={result.summary['high']} "
            f"medium={result.summary['medium']} "
            f"low={result.summary['low']} "
            f"info={result.summary['info']}"
        )
        print(f"Showing findings: {minimum_severity}")

        if not visible:
            print("No findings at the selected severity filter.")
            continue

        print("Findings:")
        for finding in visible:
            location = f"{finding.file}:{finding.line}"
            print(
                f"- [{finding.severity.upper()}] {finding.rule_id} "
                f"({finding.category}) at {location}"
            )
            print(f"  Message: {finding.message}")
            print(f"  Remediation: {finding.remediation}")

    if len(results) > 1:
        passed = sum(1 for result in results if result.verdict == "PASS")
        failed = len(results) - passed
        print()
        print("Aggregate summary")
        print(f"Skills scanned: {len(results)}")
        print(f"PASS: {passed}")
        print(f"FAIL: {failed}")


def print_json_report(results: list[AuditResult], minimum_severity: str) -> None:
    payload = {
        "results": [result.to_dict(minimum_severity) for result in results],
        "aggregate": {
            "skills_scanned": len(results),
            "pass": sum(1 for result in results if result.verdict == "PASS"),
            "fail": sum(1 for result in results if result.verdict == "FAIL"),
        },
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))


def main() -> int:
    args = parse_args()
    root = Path(args.path).expanduser().resolve()

    if not root.exists():
        print(f"Error: path does not exist: {root}", file=sys.stderr)
        return 2

    if not 0.0 <= args.fail_threshold <= 1.0:
        print("Error: --fail-threshold must be between 0.0 and 1.0", file=sys.stderr)
        return 2

    try:
        skills = discover_skills(root, args.recursive)
    except ValueError as error:
        print(f"Error: {error}", file=sys.stderr)
        return 2

    if not skills:
        print("Error: no skills found to scan", file=sys.stderr)
        return 2

    results = [audit_skill(skill_dir, args.fail_threshold) for skill_dir in skills]

    if args.json:
        print_json_report(results, args.severity)
    else:
        print_text_report(results, args.severity)

    return 1 if any(result.verdict == "FAIL" for result in results) else 0


if __name__ == "__main__":
    raise SystemExit(main())
