#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

INSIGHT_ID_PATTERN = re.compile(r"^INS-\d+$")
ALLOWED_INSIGHT_TYPES = {
    "analogy",
    "hypothesis",
    "research-question",
    "method-idea",
    "experiment-idea",
    "product-opportunity",
    "planning-judgment",
    "contradiction",
    "terminology",
    "writing-angle",
}
ALLOWED_STATUS = {"open", "validated", "rejected", "merged"}


def _is_non_empty_string(value: Any) -> bool:
    return isinstance(value, str) and value.strip() != ""


def lint_insights(input_path: Path) -> dict[str, Any]:
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
                insight_id = "<unknown>"

                try:
                    entry = json.loads(line)
                except json.JSONDecodeError as exc:
                    errors.append(
                        {
                            "line": line_no,
                            "insight_id": insight_id,
                            "message": f"Invalid JSON: {exc.msg}",
                        }
                    )
                    continue

                if not isinstance(entry, dict):
                    errors.append(
                        {
                            "line": line_no,
                            "insight_id": insight_id,
                            "message": "Entry must be a JSON object.",
                        }
                    )
                    continue

                insight_id_val = entry.get("insight_id")
                if insight_id_val is not None:
                    insight_id = str(insight_id_val)

                required_fields = [
                    "insight_id",
                    "title",
                    "insight_type",
                    "content",
                    "trigger",
                    "potential_value",
                    "needs_validation",
                    "status",
                ]
                for field in required_fields:
                    if field not in entry:
                        errors.append(
                            {
                                "line": line_no,
                                "insight_id": insight_id,
                                "message": f"Missing required field: {field}",
                            }
                        )

                if "insight_id" in entry and (
                    not isinstance(insight_id_val, str)
                    or not INSIGHT_ID_PATTERN.match(insight_id_val)
                ):
                    errors.append(
                        {
                            "line": line_no,
                            "insight_id": insight_id,
                            "message": "insight_id must match pattern INS-XXXXXX (digits after INS-).",
                        }
                    )

                if "title" in entry and not _is_non_empty_string(entry.get("title")):
                    errors.append(
                        {
                            "line": line_no,
                            "insight_id": insight_id,
                            "message": "title must not be empty.",
                        }
                    )

                if "insight_type" in entry:
                    insight_type = entry.get("insight_type")
                    if (
                        not isinstance(insight_type, str)
                        or insight_type not in ALLOWED_INSIGHT_TYPES
                    ):
                        errors.append(
                            {
                                "line": line_no,
                                "insight_id": insight_id,
                                "message": (
                                    "insight_type must be one of: "
                                    + ", ".join(sorted(ALLOWED_INSIGHT_TYPES))
                                ),
                            }
                        )

                if "trigger" in entry:
                    trigger = entry.get("trigger")
                    if not isinstance(trigger, dict):
                        errors.append(
                            {
                                "line": line_no,
                                "insight_id": insight_id,
                                "message": "trigger must be an object.",
                            }
                        )
                    else:
                        has_source_ids = (
                            isinstance(trigger.get("source_ids"), list)
                            and len(trigger.get("source_ids", [])) > 0
                        )
                        has_note_ids = (
                            isinstance(trigger.get("note_ids"), list)
                            and len(trigger.get("note_ids", [])) > 0
                        )
                        has_context = _is_non_empty_string(trigger.get("context"))
                        if not (has_source_ids or has_note_ids or has_context):
                            errors.append(
                                {
                                    "line": line_no,
                                    "insight_id": insight_id,
                                    "message": (
                                        "trigger must include at least one of source_ids, note_ids, or context."
                                    ),
                                }
                            )

                if "needs_validation" in entry:
                    needs_validation = entry.get("needs_validation")
                    if (
                        not isinstance(needs_validation, list)
                        or len(needs_validation) == 0
                    ):
                        errors.append(
                            {
                                "line": line_no,
                                "insight_id": insight_id,
                                "message": "needs_validation must be a non-empty list.",
                            }
                        )

                if "status" in entry:
                    status_val = entry.get("status")
                    if (
                        not isinstance(status_val, str)
                        or status_val not in ALLOWED_STATUS
                    ):
                        errors.append(
                            {
                                "line": line_no,
                                "insight_id": insight_id,
                                "message": f"status must be one of: {', '.join(sorted(ALLOWED_STATUS))}",
                            }
                        )
    except FileNotFoundError:
        errors.append(
            {"line": 0, "insight_id": "<input>", "message": "Input file not found."}
        )
    except OSError as exc:
        errors.append(
            {
                "line": 0,
                "insight_id": "<input>",
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
    parser = argparse.ArgumentParser(description="Validate insight log JSONL entries.")
    parser.add_argument("--input", required=True, help="Path to insight-log.jsonl")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    result = lint_insights(Path(args.input))
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
