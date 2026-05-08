#!/usr/bin/env python3
"""Record/list literature access attempts in JSONL format."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


WORK_ID_RE = re.compile(r"^WORK-\d{6}$")
REQUIRED_ATTEMPT_KEYS = {
    "source_type",
    "url_or_path",
    "version_type",
    "result",
    "selected",
    "reason",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Add access attempts to access-attempts.jsonl or list all records."
    )
    parser.add_argument("--file", required=True, help="Path to access-attempts.jsonl")
    parser.add_argument("--work-id", help="Work ID in format WORK-XXXXXX")
    parser.add_argument("--title", help="Work title (required for new records)")
    parser.add_argument(
        "--add-attempt",
        action="append",
        default=[],
        help=(
            "Attempt JSON object. Can be passed multiple times. "
            "Required keys: source_type,url_or_path,version_type,result,selected,reason"
        ),
    )
    parser.add_argument("--list", action="store_true", help="List all records")
    return parser.parse_args()


def error(action: str, message: str, code: int = 1) -> int:
    print(
        json.dumps(
            {"status": "error", "action": action, "error": message}, ensure_ascii=False
        )
    )
    return code


def read_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    rows: list[dict] = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line:
            continue
        rows.append(json.loads(line))
    return rows


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def parse_attempt(raw: str) -> tuple[dict | None, str | None]:
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        return None, f"Invalid attempt JSON: {exc}"
    if not isinstance(payload, dict):
        return None, "Attempt payload must be a JSON object"

    missing = sorted(REQUIRED_ATTEMPT_KEYS - set(payload.keys()))
    if missing:
        return None, f"Attempt missing required keys: {', '.join(missing)}"
    return payload, None


def main() -> int:
    args = parse_args()
    path = Path(args.file).expanduser()

    if args.list and args.add_attempt:
        return error("list", "--list cannot be combined with --add-attempt")

    try:
        rows = read_jsonl(path)
    except Exception as exc:
        return error("unknown", f"Failed reading JSONL: {exc}")

    if args.list:
        print(
            json.dumps(
                {"status": "ok", "action": "list", "count": len(rows), "records": rows},
                ensure_ascii=False,
            )
        )
        return 0

    if not args.add_attempt:
        return error("add", "Use --add-attempt (or --list)")
    if not args.work_id:
        return error("add", "--work-id is required when using --add-attempt")
    if not WORK_ID_RE.match(args.work_id):
        return error("add", "Invalid --work-id format. Expected WORK-XXXXXX")

    attempts: list[dict] = []
    for raw in args.add_attempt:
        attempt, msg = parse_attempt(raw)
        if msg:
            return error("add", msg)
        attempts.append(attempt or {})

    record_index = next(
        (i for i, r in enumerate(rows) if r.get("work_id") == args.work_id), None
    )

    if record_index is None:
        if not args.title:
            return error("add", "--title is required for new records")
        new_record = {
            "work_id": args.work_id,
            "title": args.title,
            "attempts": attempts,
        }
        rows.append(new_record)
        attempts_count = len(new_record["attempts"])
    else:
        record = rows[record_index]
        if "attempts" not in record or not isinstance(record.get("attempts"), list):
            record["attempts"] = []
        if args.title and "title" not in record:
            record["title"] = args.title
        record["attempts"].extend(attempts)
        attempts_count = len(record["attempts"])

    try:
        write_jsonl(path, rows)
    except Exception as exc:
        return error("add", f"Failed writing JSONL: {exc}")

    print(
        json.dumps(
            {
                "status": "ok",
                "action": "add",
                "work_id": args.work_id,
                "attempts_count": attempts_count,
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
