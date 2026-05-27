#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

NOTE_ID_PATTERN = re.compile(r"^NOTE-\d+$")


def _is_non_empty_string(value: Any) -> bool:
    return isinstance(value, str) and value.strip() != ""


def lint_notes(input_path: Path) -> dict[str, Any]:
    errors: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = []
    total_entries = 0

    try:
        with input_path.open("r", encoding="utf-8") as f:
            for line_no, raw_line in enumerate(f, start=1):
                line = raw_line.strip()
                if not line:
                    continue

                total_entries += 1
                note_id: str | None = None

                try:
                    entry = json.loads(line)
                except json.JSONDecodeError as exc:
                    errors.append(
                        {
                            "line": line_no,
                            "note_id": "<unknown>",
                            "message": f"Invalid JSON: {exc.msg}",
                        }
                    )
                    continue

                if not isinstance(entry, dict):
                    errors.append(
                        {
                            "line": line_no,
                            "note_id": "<unknown>",
                            "message": "Entry must be a JSON object.",
                        }
                    )
                    continue

                note_id_val = entry.get("note_id")
                note_id = str(note_id_val) if note_id_val is not None else "<unknown>"

                required_fields = ["note_id", "source_id", "original_text", "location"]
                for field in required_fields:
                    if field not in entry:
                        errors.append(
                            {
                                "line": line_no,
                                "note_id": note_id,
                                "message": f"Missing required field: {field}",
                            }
                        )

                if "note_id" in entry and (
                    not isinstance(note_id_val, str)
                    or not NOTE_ID_PATTERN.match(note_id_val)
                ):
                    errors.append(
                        {
                            "line": line_no,
                            "note_id": note_id,
                            "message": "note_id must match pattern NOTE-XXXXXX (digits after NOTE-).",
                        }
                    )

                if "source_id" in entry and not _is_non_empty_string(
                    entry.get("source_id")
                ):
                    errors.append(
                        {
                            "line": line_no,
                            "note_id": note_id,
                            "message": "source_id must not be empty.",
                        }
                    )

                if "original_text" in entry and not _is_non_empty_string(
                    entry.get("original_text")
                ):
                    errors.append(
                        {
                            "line": line_no,
                            "note_id": note_id,
                            "message": "original_text must not be empty.",
                        }
                    )

                if "location" in entry:
                    location = entry.get("location")
                    if not isinstance(location, dict) or len(location) == 0:
                        errors.append(
                            {
                                "line": line_no,
                                "note_id": note_id,
                                "message": "location must be an object with at least one key.",
                            }
                        )

                if not _is_non_empty_string(entry.get("paraphrase")):
                    warnings.append(
                        {
                            "line": line_no,
                            "note_id": note_id,
                            "message": "paraphrase is missing or empty.",
                        }
                    )

                if not _is_non_empty_string(entry.get("why_it_matters")):
                    warnings.append(
                        {
                            "line": line_no,
                            "note_id": note_id,
                            "message": "why_it_matters is missing or empty.",
                        }
                    )
    except FileNotFoundError:
        errors.append(
            {"line": 0, "note_id": "<input>", "message": "Input file not found."}
        )
    except OSError as exc:
        errors.append(
            {
                "line": 0,
                "note_id": "<input>",
                "message": f"Unable to read input file: {exc}",
            }
        )

    status = "fail" if errors else "pass"
    return {
        "status": status,
        "total_entries": total_entries,
        "errors": errors,
        "warnings": warnings,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate excerpt notes JSONL entries."
    )
    parser.add_argument("--input", required=True, help="Path to excerpt-notes.jsonl")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    result = lint_notes(Path(args.input))
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
