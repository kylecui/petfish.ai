#!/usr/bin/env python3
# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""Thin wrapper around the external trustskills CLI."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Wrap the external trustskills CLI for single-skill scans, "
            "root scans, manifest generation, and manifest verification."
        )
    )
    scope = parser.add_mutually_exclusive_group(required=True)
    scope.add_argument("--path", help="Path to a single skill directory")
    scope.add_argument("--root", help="Root containing multiple skill directories")
    parser.add_argument(
        "--detail", action="store_true", help="Enable detailed scan output"
    )
    parser.add_argument("--output", help="Write a Markdown report to this path")
    parser.add_argument("--policy", help="Path to custom policy YAML/JSON")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument(
        "--manifest", action="store_true", help="Generate manifest file(s)"
    )
    mode.add_argument(
        "--verify", action="store_true", help="Verify existing manifest file(s)"
    )
    parser.add_argument(
        "--json", action="store_true", help="Emit structured JSON output"
    )
    return parser.parse_args()


def emit(payload: dict[str, Any], as_json: bool) -> int:
    if as_json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return int(payload.get("exit_code", 0))

    if payload.get("stdout"):
        sys.stdout.write(str(payload["stdout"]))
        if not str(payload["stdout"]).endswith("\n"):
            sys.stdout.write("\n")
    if payload.get("stderr"):
        sys.stderr.write(str(payload["stderr"]))
        if not str(payload["stderr"]).endswith("\n"):
            sys.stderr.write("\n")
    return int(payload.get("exit_code", 0))


def resolve_runner() -> tuple[list[str] | None, str | None]:
    direct = shutil.which("trustskills")
    if direct:
        return [direct], "trustskills"

    uv = shutil.which("uv")
    if uv:
        probe = subprocess.run(
            [uv, "run", "trustskills", "--help"],
            capture_output=True,
            text=True,
            timeout=20,
            check=False,
        )
        if probe.returncode == 0:
            return [uv, "run", "trustskills"], "uv run trustskills"

    return None, None


def install_payload(exit_code: int = 2) -> dict[str, Any]:
    return {
        "ok": False,
        "installed": False,
        "exit_code": exit_code,
        "error": "trustskills CLI not found",
        "install_instructions": [
            "uv add trustskills",
            "uv pip install trustskills",
        ],
        "stdout": "",
        "stderr": (
            "trustskills CLI is not installed. Install it with 'uv add trustskills' "
            "or 'uv pip install trustskills'."
        ),
    }


def find_skill_dirs(root: Path) -> list[Path]:
    return sorted(
        candidate
        for candidate in root.iterdir()
        if candidate.is_dir() and (candidate / "SKILL.md").exists()
    )


def run_command(command: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        capture_output=True,
        text=True,
        timeout=120,
        check=False,
    )


def parse_summary_line(line: str) -> dict[str, Any] | None:
    line = line.strip()
    if not line:
        return None

    marker = " score="
    if marker not in line or " level=" not in line:
        return None

    left, remainder = line.split(marker, 1)
    score_part, level_part = remainder.split(" level=", 1)
    left_parts = left.split(maxsplit=1)
    if len(left_parts) != 2:
        return None

    symbol, name = left_parts
    try:
        score = float(score_part.strip())
    except ValueError:
        return None

    return {
        "symbol": symbol,
        "skill": name.strip(),
        "risk_score": score,
        "governance_level": level_part.strip(),
    }


def parse_detail_block(block: str) -> dict[str, Any]:
    result: dict[str, Any] = {
        "risk_scores": {},
        "redline_violations": [],
        "high_risk_indicators": [],
        "risk_surface": [],
    }
    section: str | None = None

    for raw_line in block.splitlines():
        line = raw_line.rstrip()
        stripped = line.strip()
        if not stripped or stripped == "=" * 60:
            continue
        if stripped == "Dimension Scores:":
            section = "dimensions"
            continue
        if stripped == "Redline Violations:":
            section = "redlines"
            continue
        if stripped == "High Risk Indicators:":
            section = "indicators"
            continue
        if stripped.startswith("Skill: "):
            result["skill"] = stripped.removeprefix("Skill: ").strip()
            section = None
            continue
        if stripped.startswith("Description: "):
            result["description"] = stripped.removeprefix("Description: ").strip()
            section = None
            continue
        if stripped.startswith("Version: "):
            result["version"] = stripped.removeprefix("Version: ").strip()
            section = None
            continue
        if stripped.startswith("Governance: "):
            governance = stripped.removeprefix("Governance: ").strip()
            parts = governance.split(maxsplit=1)
            if len(parts) == 2:
                result["symbol"] = parts[0]
                result["governance_level"] = parts[1]
            else:
                result["governance_level"] = governance
            section = None
            continue
        if stripped.startswith("Overall Risk Score: "):
            try:
                result["risk_score"] = float(
                    stripped.removeprefix("Overall Risk Score: ").strip()
                )
            except ValueError:
                result["risk_score"] = stripped.removeprefix(
                    "Overall Risk Score: "
                ).strip()
            section = None
            continue
        if stripped.startswith("Risk Surface: "):
            surface = stripped.removeprefix("Risk Surface: ").strip()
            result["risk_surface"] = [
                item.strip() for item in surface.split(",") if item.strip()
            ]
            section = None
            continue

        if section == "dimensions":
            parts = stripped.split()
            if len(parts) >= 2:
                key = parts[0]
                value = parts[-1]
                try:
                    result["risk_scores"][key] = float(value)
                except ValueError:
                    result["risk_scores"][key] = value
            continue

        if section == "redlines" and stripped.startswith("❌"):
            result["redline_violations"].append(stripped.removeprefix("❌").strip())
            continue

        if section == "indicators" and stripped.startswith("⚠"):
            result["high_risk_indicators"].append(stripped.removeprefix("⚠").strip())
            continue

    return result


def parse_scan_output(stdout: str, detail: bool) -> dict[str, Any]:
    if detail:
        blocks = [part for part in stdout.split("=" * 60) if part.strip()]
        parsed_blocks = [
            parse_detail_block(f"{'=' * 60}\n{part}\n{'=' * 60}") for part in blocks
        ]
        results = [block for block in parsed_blocks if block.get("skill")]
        scanned_count = len(results)
    else:
        results = []
        scanned_count = None
        for raw_line in stdout.splitlines():
            line = raw_line.strip()
            if line.startswith("Scanned ") and line.endswith(" skills."):
                parts = line.split()
                if len(parts) >= 2:
                    try:
                        scanned_count = int(parts[1])
                    except ValueError:
                        scanned_count = None
                continue
            parsed = parse_summary_line(raw_line)
            if parsed is not None:
                results.append(parsed)
        if scanned_count is None:
            scanned_count = len(results)

    return {
        "results": results,
        "scanned_count": scanned_count,
    }


def parse_manifest_generate_output(stdout: str) -> dict[str, Any]:
    generated_files: list[str] = []
    entries: list[dict[str, Any]] = []
    approval_status: str | None = None
    approval_required: bool | None = None
    generated_count: int | None = None

    for raw_line in stdout.splitlines():
        line = raw_line.rstrip()
        stripped = line.strip()
        if stripped.startswith("Generated: "):
            generated_files.append(stripped.removeprefix("Generated: ").strip())
            continue
        if stripped.startswith("Approval status: "):
            approval_status = stripped.removeprefix("Approval status: ").strip()
            continue
        if stripped.startswith("Approval required: "):
            approval_required = (
                stripped.removeprefix("Approval required: ").strip().lower() == "true"
            )
            continue
        if stripped.startswith("Generated manifests for ") and stripped.endswith(
            " skills."
        ):
            parts = stripped.split()
            if len(parts) >= 4:
                try:
                    generated_count = int(parts[3])
                except ValueError:
                    generated_count = None
            continue
        if stripped.startswith("✅") or stripped.startswith("⚠️"):
            parts = stripped.split()
            if len(parts) >= 2:
                status = " ".join(parts[1:])
                entries.append({"line": stripped, "status": status})

    return {
        "generated_files": generated_files,
        "approval_status": approval_status,
        "approval_required": approval_required,
        "generated_count": generated_count,
        "entries": entries,
    }


def parse_manifest_verify_output(stdout: str) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "errors": [],
        "warnings": [],
    }

    for index, raw_line in enumerate(stdout.splitlines()):
        stripped = raw_line.strip()
        if index == 0 and "— valid=" in stripped:
            left, valid_part = stripped.split("— valid=", 1)
            left_parts = left.split(maxsplit=1)
            if len(left_parts) == 2:
                payload["symbol"] = left_parts[0]
                payload["skill"] = left_parts[1].strip()
            payload["valid"] = valid_part.strip().lower() == "true"
            continue
        if stripped.startswith("content_hash: "):
            payload["content_hash"] = stripped.removeprefix("content_hash: ").strip()
            continue
        if stripped.startswith("package_hash: "):
            payload["package_hash"] = stripped.removeprefix("package_hash: ").strip()
            continue
        if stripped.startswith("approval: "):
            payload["approval"] = stripped.removeprefix("approval: ").strip()
            continue
        if stripped.startswith("drift: "):
            payload["drift"] = stripped.removeprefix("drift: ").strip()
            continue
        if stripped.startswith("ERROR: "):
            payload["errors"].append(stripped.removeprefix("ERROR: ").strip())
            continue
        if stripped.startswith("WARN: "):
            payload["warnings"].append(stripped.removeprefix("WARN: ").strip())

    return payload


def make_markdown_report(payload: dict[str, Any]) -> str:
    lines = ["# trustskills Wrapper Report", ""]
    lines.append(f"- Operation: `{payload.get('operation', 'unknown')}`")
    lines.append(f"- Scope: `{payload.get('scope', 'unknown')}`")
    lines.append(f"- Target: `{payload.get('target', '')}`")
    lines.append(f"- Exit code: `{payload.get('exit_code', 0)}`")
    lines.append("")

    results = payload.get("results")
    if isinstance(results, list) and results:
        lines.append("## Results")
        lines.append("")
        lines.append("| Skill | Score | Level |")
        lines.append("|---|---:|---|")
        for item in results:
            skill = item.get("skill", "")
            score = item.get("risk_score", "")
            level = item.get("governance_level", item.get("valid", ""))
            lines.append(f"| {skill} | {score} | {level} |")
        lines.append("")

    generated_files = payload.get("generated_files")
    if isinstance(generated_files, list) and generated_files:
        lines.append("## Generated Files")
        lines.append("")
        for item in generated_files:
            lines.append(f"- `{item}`")
        lines.append("")

    stdout = str(payload.get("stdout", "")).strip()
    if stdout:
        lines.append("## Raw Output")
        lines.append("")
        lines.append("```text")
        lines.append(stdout)
        lines.append("```")

    return "\n".join(lines).rstrip() + "\n"


def write_report(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(make_markdown_report(payload), encoding="utf-8")


def build_base_command(
    runner: list[str],
    policy: str | None,
    subcommand: str,
    target: Path,
    detail: bool,
) -> list[str]:
    command = list(runner)
    if policy:
        command.extend(["--policy", policy])
    command.extend([subcommand, str(target)])
    if detail:
        command.append("--detail")
    return command


def execute_single(
    runner: list[str],
    runner_name: str,
    args: argparse.Namespace,
    target: Path,
) -> dict[str, Any]:
    if args.verify:
        operation = "manifest_verify"
        command = build_base_command(runner, None, "manifest-verify", target, False)
        completed = run_command(command)
        parsed = parse_manifest_verify_output(completed.stdout)
    elif args.manifest:
        operation = "manifest_generate"
        command = build_base_command(
            runner, args.policy, "manifest-generate", target, False
        )
        completed = run_command(command)
        parsed = parse_manifest_generate_output(completed.stdout)
    else:
        operation = "scan"
        command = build_base_command(runner, args.policy, "scan", target, args.detail)
        completed = run_command(command)
        parsed = parse_scan_output(completed.stdout, args.detail)

    payload: dict[str, Any] = {
        "ok": completed.returncode == 0,
        "installed": True,
        "runner": runner_name,
        "operation": operation,
        "scope": "path",
        "target": str(target),
        "command": command,
        "exit_code": completed.returncode,
        "stdout": completed.stdout,
        "stderr": completed.stderr,
    }
    payload.update(parsed)

    if args.output:
        report_path = Path(args.output)
        write_report(report_path, payload)
        payload["report_path"] = str(report_path)

    return payload


def execute_root(
    runner: list[str],
    runner_name: str,
    args: argparse.Namespace,
    root: Path,
) -> dict[str, Any]:
    if args.verify:
        skill_dirs = find_skill_dirs(root)
        if not skill_dirs:
            return {
                "ok": False,
                "installed": True,
                "runner": runner_name,
                "operation": "manifest_verify",
                "scope": "root",
                "target": str(root),
                "command": [],
                "exit_code": 1,
                "stdout": "",
                "stderr": f"No skills found under {root}",
                "results": [],
                "scanned_count": 0,
            }

        results: list[dict[str, Any]] = []
        stdout_parts: list[str] = []
        stderr_parts: list[str] = []
        commands: list[list[str]] = []
        exit_code = 0
        for skill_dir in skill_dirs:
            command = build_base_command(
                runner, None, "manifest-verify", skill_dir, False
            )
            commands.append(command)
            completed = run_command(command)
            stdout_parts.append(completed.stdout.rstrip())
            if completed.stderr.strip():
                stderr_parts.append(completed.stderr.rstrip())
            parsed = parse_manifest_verify_output(completed.stdout)
            parsed["path"] = str(skill_dir)
            results.append(parsed)
            if completed.returncode != 0:
                exit_code = completed.returncode

        payload = {
            "ok": exit_code == 0,
            "installed": True,
            "runner": runner_name,
            "operation": "manifest_verify",
            "scope": "root",
            "target": str(root),
            "command": commands,
            "exit_code": exit_code,
            "stdout": "\n\n".join(part for part in stdout_parts if part),
            "stderr": "\n\n".join(part for part in stderr_parts if part),
            "results": results,
            "scanned_count": len(results),
        }
    elif args.manifest:
        command = build_base_command(
            runner, args.policy, "manifest-generate-all", root, False
        )
        completed = run_command(command)
        parsed = parse_manifest_generate_output(completed.stdout)
        payload = {
            "ok": completed.returncode == 0,
            "installed": True,
            "runner": runner_name,
            "operation": "manifest_generate",
            "scope": "root",
            "target": str(root),
            "command": command,
            "exit_code": completed.returncode,
            "stdout": completed.stdout,
            "stderr": completed.stderr,
        }
        payload.update(parsed)
    else:
        command = build_base_command(runner, args.policy, "scan-all", root, args.detail)
        completed = run_command(command)
        parsed = parse_scan_output(completed.stdout, args.detail)
        payload = {
            "ok": completed.returncode == 0,
            "installed": True,
            "runner": runner_name,
            "operation": "scan",
            "scope": "root",
            "target": str(root),
            "command": command,
            "exit_code": completed.returncode,
            "stdout": completed.stdout,
            "stderr": completed.stderr,
        }
        payload.update(parsed)
        if args.output:
            report_path = Path(args.output)
            if report_path.exists():
                payload["report_path"] = str(report_path)

    if args.output and "report_path" not in payload:
        report_path = Path(args.output)
        write_report(report_path, payload)
        payload["report_path"] = str(report_path)

    return payload


def main() -> int:
    args = parse_args()
    runner, runner_name = resolve_runner()
    if runner is None or runner_name is None:
        return emit(install_payload(), args.json)

    target = Path(args.path or args.root).resolve()
    if not target.exists() or not target.is_dir():
        payload = {
            "ok": False,
            "installed": True,
            "runner": runner_name,
            "exit_code": 1,
            "error": f"Target directory not found: {target}",
            "stdout": "",
            "stderr": f"Target directory not found: {target}",
        }
        return emit(payload, args.json)

    if args.path and not (target / "SKILL.md").exists():
        payload = {
            "ok": False,
            "installed": True,
            "runner": runner_name,
            "exit_code": 1,
            "error": f"SKILL.md not found under {target}",
            "stdout": "",
            "stderr": f"SKILL.md not found under {target}",
        }
        return emit(payload, args.json)

    if args.path:
        payload = execute_single(runner, runner_name, args, target)
    else:
        payload = execute_root(runner, runner_name, args, target)

    return emit(payload, args.json)


if __name__ == "__main__":
    sys.exit(main())
