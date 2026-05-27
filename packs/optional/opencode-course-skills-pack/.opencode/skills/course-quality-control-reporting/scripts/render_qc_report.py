#!/usr/bin/env python3
"""Render a Markdown QC report from structured QA/QC JSON."""

import argparse
import json
from pathlib import Path

def parse_args():
    parser = argparse.ArgumentParser(
        description="Render a Markdown QC report from a JSON findings file."
    )
    parser.add_argument("--input", required=True, help="Input JSON file.")
    parser.add_argument("--output", required=True, help="Output Markdown file.")
    parser.add_argument(
        "--title",
        default="QC Report",
        help="Report title.",
    )
    return parser.parse_args()

def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))

def main():
    args = parse_args()
    src = Path(args.input).expanduser().resolve()
    dst = Path(args.output).expanduser().resolve()
    data = load_json(src)

    findings = data.get("findings", [])
    lines = [f"# {args.title}", "", "## Source QA baseline", ""]
    lines.append(f"- Source file: `{src.name}`")
    lines.append(f"- Total findings: {len(findings)}")
    lines.extend(["", "## Issue-by-issue status", ""])

    blocker_count = 0
    open_count = 0

    for idx, item in enumerate(findings, start=1):
        title = item.get("title", f"Finding {idx}")
        severity = item.get("severity", "unknown")
        status = item.get("status", "open")
        artifact = item.get("artifact", "unspecified")
        action = item.get("action", "No action recorded.")
        evidence = item.get("evidence", "No evidence recorded.")
        if severity == "blocker":
            blocker_count += 1
        if status not in {"verified", "fixed"}:
            open_count += 1

        lines.extend([
            f"### {idx}. {title}",
            f"- Severity: {severity}",
            f"- Status: {status}",
            f"- Artifact: {artifact}",
            f"- Action: {action}",
            f"- Evidence: {evidence}",
            "",
        ])

    lines.extend(["## Residual risks", ""])
    if blocker_count:
        lines.append(f"- Unresolved blocker-level items remain: {blocker_count}")
    else:
        lines.append("- No blocker-level items are recorded.")
    if open_count:
        lines.append(f"- Non-closed items remain: {open_count}")
    else:
        lines.append("- All items are closed or verified.")

    lines.extend(["", "## Release recommendation", ""])
    if blocker_count:
        lines.append("Release is **not recommended** until blocker items are resolved.")
    elif open_count:
        lines.append("Release can proceed only with explicit acceptance of residual risk.")
    else:
        lines.append("Release is recommended based on the current QC record.")

    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({
        "input": str(src),
        "output": str(dst),
        "findings": len(findings),
        "blockers": blocker_count,
        "non_closed": open_count
    }, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
