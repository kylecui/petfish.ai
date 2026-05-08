#!/usr/bin/env python3
"""Manage source-index.jsonl entries (add/update/list)."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


SOURCE_ID_RE = re.compile(r"^SRC-\d{6}$")
ALLOWED_SOURCE_TYPES = {
    "official-doc",
    "paper",
    "report",
    "website",
    "code-repo",
    "interview",
    "internal-doc",
    "dataset",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Add, update, or list source-index.jsonl."
    )
    parser.add_argument("--file", required=True, help="Path to source-index.jsonl")

    op_group = parser.add_mutually_exclusive_group(required=False)
    op_group.add_argument("--add", help="JSON string for new source entry")
    op_group.add_argument(
        "--update", help="JSON string with source_id and fields to update"
    )

    parser.add_argument("--list", action="store_true", help="List all entries")
    return parser.parse_args()


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


def validate_source_payload(payload: dict) -> tuple[bool, str | None]:
    source_id = payload.get("source_id")
    source_type = payload.get("source_type")

    if not isinstance(source_id, str) or not SOURCE_ID_RE.match(source_id):
        return False, "Invalid source_id. Expected format SRC-XXXXXX."
    if not isinstance(source_type, str) or source_type not in ALLOWED_SOURCE_TYPES:
        return (
            False,
            "Invalid source_type. Must be one of: "
            + ", ".join(sorted(ALLOWED_SOURCE_TYPES)),
        )
    return True, None


def error(action: str, message: str, code: int = 1) -> int:
    print(
        json.dumps(
            {"status": "error", "action": action, "error": message}, ensure_ascii=False
        )
    )
    return code


def main() -> int:
    args = parse_args()
    path = Path(args.file).expanduser()

    requested = sum(
        1 for flag in [args.add is not None, args.update is not None, args.list] if flag
    )
    if requested != 1:
        return error(
            "unknown", "Exactly one action is required: --add, --update, or --list"
        )

    try:
        rows = read_jsonl(path)
    except Exception as exc:
        return error("unknown", f"Failed reading JSONL: {exc}")

    if args.list:
        print(
            json.dumps(
                {
                    "status": "ok",
                    "action": "list",
                    "count": len(rows),
                    "entries": rows,
                },
                ensure_ascii=False,
            )
        )
        return 0

    if args.add is not None:
        action = "add"
        try:
            payload = json.loads(args.add)
        except json.JSONDecodeError as exc:
            return error(action, f"Invalid JSON for --add: {exc}")
        if not isinstance(payload, dict):
            return error(action, "--add payload must be a JSON object")

        valid, message = validate_source_payload(payload)
        if not valid:
            return error(action, message or "Invalid payload")

        source_id = payload["source_id"]
        if any(r.get("source_id") == source_id for r in rows):
            return error(action, f"source_id already exists: {source_id}")

        rows.append(payload)
        try:
            write_jsonl(path, rows)
        except Exception as exc:
            return error(action, f"Failed writing JSONL: {exc}")

        print(
            json.dumps(
                {
                    "status": "ok",
                    "action": "add",
                    "source_id": source_id,
                    "count": len(rows),
                },
                ensure_ascii=False,
            )
        )
        return 0

    action = "update"
    try:
        payload = json.loads(args.update)
    except json.JSONDecodeError as exc:
        return error(action, f"Invalid JSON for --update: {exc}")
    if not isinstance(payload, dict):
        return error(action, "--update payload must be a JSON object")

    source_id = payload.get("source_id")
    if not isinstance(source_id, str) or not SOURCE_ID_RE.match(source_id):
        return error(action, "Invalid source_id in --update. Expected SRC-XXXXXX")

    update_fields = {k: v for k, v in payload.items() if k != "source_id"}
    if not update_fields:
        return error(
            action, "--update payload must include at least one field besides source_id"
        )
    if (
        "source_type" in update_fields
        and update_fields["source_type"] not in ALLOWED_SOURCE_TYPES
    ):
        return error(
            action,
            "Invalid source_type. Must be one of: "
            + ", ".join(sorted(ALLOWED_SOURCE_TYPES)),
        )

    found = False
    for row in rows:
        if row.get("source_id") == source_id:
            row.update(update_fields)
            found = True
            break

    if not found:
        return error(action, f"source_id not found: {source_id}")

    try:
        write_jsonl(path, rows)
    except Exception as exc:
        return error(action, f"Failed writing JSONL: {exc}")

    print(
        json.dumps(
            {
                "status": "ok",
                "action": "update",
                "source_id": source_id,
                "updated_fields": sorted(update_fields.keys()),
                "count": len(rows),
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
