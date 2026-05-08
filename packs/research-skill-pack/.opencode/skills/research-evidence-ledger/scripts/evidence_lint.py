#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

EVIDENCE_ID_PATTERN = re.compile(r"^EV-\d+$")
ALLOWED_EVIDENCE_TYPES = {"EXTRACTED", "INFERRED", "AMBIGUOUS", "PROPOSED"}
ALLOWED_CONFIDENCE = {"high", "medium", "low"}


def _is_non_empty_string(value: Any) -> bool:
    return isinstance(value, str) and value.strip() != ""


def lint_evidence(input_path: Path) -> dict[str, Any]:
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
                evidence_id = "<unknown>"

                try:
                    entry = json.loads(line)
                except json.JSONDecodeError as exc:
                    errors.append(
                        {
                            "line": line_no,
                            "evidence_id": evidence_id,
                            "message": f"Invalid JSON: {exc.msg}",
                        }
                    )
                    continue

                if not isinstance(entry, dict):
                    errors.append(
                        {
                            "line": line_no,
                            "evidence_id": evidence_id,
                            "message": "Entry must be a JSON object.",
                        }
                    )
                    continue

                evidence_id_val = entry.get("evidence_id")
                if evidence_id_val is not None:
                    evidence_id = str(evidence_id_val)

                required_fields = [
                    "evidence_id",
                    "source_id",
                    "claim",
                    "evidence_type",
                    "confidence",
                ]
                for field in required_fields:
                    if field not in entry:
                        errors.append(
                            {
                                "line": line_no,
                                "evidence_id": evidence_id,
                                "message": f"Missing required field: {field}",
                            }
                        )

                if "evidence_id" in entry and (
                    not isinstance(evidence_id_val, str)
                    or not EVIDENCE_ID_PATTERN.match(evidence_id_val)
                ):
                    errors.append(
                        {
                            "line": line_no,
                            "evidence_id": evidence_id,
                            "message": "evidence_id must match pattern EV-XXXXXX (digits after EV-).",
                        }
                    )

                if "source_id" in entry and not _is_non_empty_string(
                    entry.get("source_id")
                ):
                    errors.append(
                        {
                            "line": line_no,
                            "evidence_id": evidence_id,
                            "message": "source_id must not be empty.",
                        }
                    )

                if "claim" in entry and not _is_non_empty_string(entry.get("claim")):
                    errors.append(
                        {
                            "line": line_no,
                            "evidence_id": evidence_id,
                            "message": "claim must not be empty.",
                        }
                    )

                evidence_type = entry.get("evidence_type")
                if "evidence_type" in entry and (
                    not isinstance(evidence_type, str)
                    or evidence_type not in ALLOWED_EVIDENCE_TYPES
                ):
                    errors.append(
                        {
                            "line": line_no,
                            "evidence_id": evidence_id,
                            "message": (
                                "evidence_type must be one of: "
                                + ", ".join(sorted(ALLOWED_EVIDENCE_TYPES))
                            ),
                        }
                    )

                if "confidence" in entry:
                    confidence = entry.get("confidence")
                    if (
                        not isinstance(confidence, str)
                        or confidence not in ALLOWED_CONFIDENCE
                    ):
                        errors.append(
                            {
                                "line": line_no,
                                "evidence_id": evidence_id,
                                "message": (
                                    "confidence must be one of: "
                                    + ", ".join(sorted(ALLOWED_CONFIDENCE))
                                ),
                            }
                        )

                if evidence_type == "INFERRED":
                    if not _is_non_empty_string(entry.get("notes")):
                        warnings.append(
                            {
                                "line": line_no,
                                "evidence_id": evidence_id,
                                "message": "INFERRED evidence should include reasoning in notes.",
                            }
                        )

                if evidence_type == "AMBIGUOUS":
                    contradicts = entry.get("contradicts")
                    if not isinstance(contradicts, list) or len(contradicts) == 0:
                        warnings.append(
                            {
                                "line": line_no,
                                "evidence_id": evidence_id,
                                "message": "AMBIGUOUS evidence should include non-empty contradicts array.",
                            }
                        )
    except FileNotFoundError:
        errors.append(
            {"line": 0, "evidence_id": "<input>", "message": "Input file not found."}
        )
    except OSError as exc:
        errors.append(
            {
                "line": 0,
                "evidence_id": "<input>",
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
        description="Validate evidence ledger JSONL entries."
    )
    parser.add_argument("--input", required=True, help="Path to evidence-ledger.jsonl")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    result = lint_evidence(Path(args.input))
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
