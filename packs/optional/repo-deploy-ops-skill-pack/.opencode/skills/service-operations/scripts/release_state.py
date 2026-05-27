#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.11"
# ///
"""Maintain a lightweight deployment release-state file."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_state(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"current_release": None, "releases": []}
    return json.loads(path.read_text(encoding="utf-8"))


def save_state(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def get_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Maintain deployment release state as JSON.")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_init = sub.add_parser("init", help="Initialize state file")
    p_init.add_argument("--state", required=True)

    p_add = sub.add_parser("add", help="Add a release entry")
    p_add.add_argument("--state", required=True)
    p_add.add_argument("--release-id", required=True)
    p_add.add_argument("--version", default="")
    p_add.add_argument("--commit", default="")
    p_add.add_argument("--path", default="")
    p_add.add_argument("--notes", default="")

    p_promote = sub.add_parser("promote", help="Set current release")
    p_promote.add_argument("--state", required=True)
    p_promote.add_argument("--release-id", required=True)

    p_fail = sub.add_parser("fail", help="Mark release failed")
    p_fail.add_argument("--state", required=True)
    p_fail.add_argument("--release-id", required=True)
    p_fail.add_argument("--notes", default="")

    p_rollback = sub.add_parser("rollback", help="Mark rollback target as current")
    p_rollback.add_argument("--state", required=True)
    p_rollback.add_argument("--release-id", required=True)
    p_rollback.add_argument("--notes", default="")

    p_list = sub.add_parser("list", help="List releases")
    p_list.add_argument("--state", required=True)

    return parser


def main() -> int:
    parser = get_parser()
    args = parser.parse_args()
    state_path = Path(args.state)
    data = load_state(state_path)

    if args.cmd == "init":
        save_state(state_path, data)
        print(json.dumps(data, ensure_ascii=False, indent=2))
        return 0

    if args.cmd == "add":
        entry = {
            "release_id": args.release_id,
            "version": args.version,
            "commit": args.commit,
            "path": args.path,
            "notes": args.notes,
            "created_at": now(),
            "status": "added",
        }
        data.setdefault("releases", []).append(entry)
        save_state(state_path, data)
        print(json.dumps(entry, ensure_ascii=False, indent=2))
        return 0

    if args.cmd in {"promote", "fail", "rollback"}:
        found = None
        for item in data.get("releases", []):
            if item.get("release_id") == args.release_id:
                found = item
                break
        if found is None:
            print(json.dumps({"error": f"release not found: {args.release_id}"}))
            return 2
        if args.cmd == "promote":
            found["status"] = "current"
            found["promoted_at"] = now()
            data["current_release"] = args.release_id
        elif args.cmd == "fail":
            found["status"] = "failed"
            found["failed_at"] = now()
            found["notes"] = args.notes or found.get("notes", "")
        else:
            found["status"] = "rolled_back_to"
            found["rolled_back_at"] = now()
            found["notes"] = args.notes or found.get("notes", "")
            data["current_release"] = args.release_id
        save_state(state_path, data)
        print(json.dumps(found, ensure_ascii=False, indent=2))
        return 0

    if args.cmd == "list":
        print(json.dumps(data, ensure_ascii=False, indent=2))
        return 0

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
