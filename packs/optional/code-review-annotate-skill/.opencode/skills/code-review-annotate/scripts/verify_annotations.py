# /// script
# requires-python = ">=3.9"
# dependencies = []
# ///
"""Zero-deletion gate for the code-review-annotate pipeline (SKILL.md section 5).

Checks, in order:
1. git diff --numstat: every changed file must have deletions == 0 (only
   comment lines may be added).
2. Added lines must not risk -Werror=comment: a `/*` opened inside a `//`
   line comment, or a line containing two or more `/*` sequences.
3. Remaining TODO-ANNOTATE markers are counted (sweep target: 0).

Read-only: invokes `git diff` via subprocess with an argument list (no
shell), never mutates files, never touches the network.

Exit codes: 0 = gate passed; 1 = violations found; 2 = usage/Environment
error (not a git repo, git missing).
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

MARKER = "TODO-ANNOTATE"


def run_git(args: list[str], cwd: Path) -> str:
    proc = subprocess.run(
        ["git", *args],
        cwd=str(cwd),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if proc.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} failed: {proc.stderr.strip()}")
    return proc.stdout


def parse_numstat(out: str) -> list[dict]:
    rows = []
    for line in out.splitlines():
        if not line.strip():
            continue
        parts = line.split("\t")
        if len(parts) != 3:
            continue
        ins, dele, path = parts
        rows.append(
            {
                "path": path,
                "insertions": ins,
                "deletions": dele,
                "binary": ins == "-" or dele == "-",
            }
        )
    return rows


def scan_added_lines(diff_text: str) -> tuple[list[str], int]:
    """Return (comment-risk lines, TODO-ANNOTATE count) across added lines."""
    risky: list[str] = []
    todos = 0
    for line in diff_text.splitlines():
        if not line.startswith("+") or line.startswith("+++"):
            continue
        body = line[1:]
        if MARKER in body:
            todos += 1
        stripped = body.lstrip()
        if stripped.startswith("//") and "/*" in body:
            risky.append(line)
        elif body.count("/*") >= 2:
            risky.append(line)
    return risky, todos


def scan_working_tree(paths: list[Path], root: Path) -> int:
    """Count remaining TODO-ANNOTATE markers in the given files on disk."""
    count = 0
    for p in paths:
        target = p if p.is_absolute() else root / p
        if target.is_file():
            try:
                count += target.read_text(encoding="utf-8", errors="replace").count(
                    MARKER
                )
            except OSError:
                continue
    return count


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Zero-deletion gate: verify an annotation run only added comments."
    )
    parser.add_argument(
        "--paths",
        nargs="*",
        default=None,
        help="Limit the check to these files (default: all uncommitted changes)",
    )
    parser.add_argument(
        "--root",
        default=".",
        help="Repository root (default: current directory)",
    )
    parser.add_argument(
        "--json", action="store_true", help="Emit machine-readable JSON report"
    )
    args = parser.parse_args(argv)

    root = Path(args.root).resolve()
    if not (root / ".git").exists():
        print(f"ERROR: {root} is not a git repository", file=sys.stderr)
        return 2

    path_args = ["--"] + args.paths if args.paths else []
    try:
        numstat = parse_numstat(run_git(["diff", "--numstat", *path_args], root))
        diff_text = run_git(["diff", "-U0", *path_args], root)
    except RuntimeError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    deleted_files = [r for r in numstat if not r["binary"] and r["deletions"] != "0"]
    risky, todos_in_diff = scan_added_lines(diff_text)
    watch = (
        [Path(p) for p in args.paths]
        if args.paths
        else [root / r["path"] for r in numstat]
    )
    todos_on_disk = scan_working_tree(watch, root)

    clean = not deleted_files and not risky

    if args.json:
        print(
            json.dumps(
                {
                    "gate": "PASS" if clean else "FAIL",
                    "files_checked": len(numstat),
                    "deletion_violations": deleted_files,
                    "comment_risk_lines": risky,
                    "todo_annotate_in_diff": todos_in_diff,
                    "todo_annotate_on_disk": todos_on_disk,
                },
                ensure_ascii=False,
                indent=2,
            )
        )
    else:
        print(f"files checked: {len(numstat)}")
        for row in numstat:
            flag = "OK " if row["deletions"] == "0" or row["binary"] else "DEL"
            print(f"  [{flag}] {row['path']}  +{row['insertions']} -{row['deletions']}")
        if deleted_files:
            print(f"\nVIOLATION: {len(deleted_files)} file(s) with deletions > 0:")
            for row in deleted_files:
                print(f"  - {row['path']} ({row['deletions']} deleted lines)")
            print("  Likely cause: an edit replaced an existing comment line.")
        if risky:
            print(f"\nCOMMENT RISK ({len(risky)} line(s), -Werror=comment):")
            for line in risky[:10]:
                print(f"  {line}")
        print(
            f"\nTODO-ANNOTATE: {todos_in_diff} in diff, "
            f"{todos_on_disk} remaining on disk (sweep target: 0)"
        )
        print("GATE:", "PASS" if clean else "FAIL")

    return 0 if clean else 1


if __name__ == "__main__":
    sys.exit(main())
