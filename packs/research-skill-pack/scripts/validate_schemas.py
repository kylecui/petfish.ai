# /// script
# requires-python = ">=3.11"
# dependencies = ["jsonschema>=4.0"]
# ///

#!/usr/bin/env python3
"""Validate schema/example pairs in two directories."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from jsonschema import ValidationError, validate


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate *.schema.json files against matching *-example.json payloads."
    )
    parser.add_argument(
        "--schemas-dir",
        required=True,
        help="Directory containing *.schema.json files.",
    )
    parser.add_argument(
        "--examples-dir",
        required=True,
        help="Directory containing *-example.json files.",
    )
    return parser.parse_args()


def match_example_name(schema_name: str) -> str:
    # source-index.schema.json -> source-index-example.json
    return schema_name.replace(".schema.json", "-example.json")


def main() -> int:
    args = parse_args()
    schemas_dir = Path(args.schemas_dir).expanduser()
    examples_dir = Path(args.examples_dir).expanduser()

    results: list[dict[str, object]] = []
    any_fail = False

    schema_files = sorted(schemas_dir.glob("*.schema.json"))

    for schema_file in schema_files:
        example_name = match_example_name(schema_file.name)
        example_file = examples_dir / example_name
        entry: dict[str, object] = {
            "schema": str(schema_file),
            "example": str(example_file),
            "valid": False,
            "errors": [],
        }

        if not example_file.exists():
            entry["errors"] = [f"Example file not found: {example_file}"]
            any_fail = True
            results.append(entry)
            continue

        try:
            schema = json.loads(schema_file.read_text(encoding="utf-8"))
            example = json.loads(example_file.read_text(encoding="utf-8"))
            validate(instance=example, schema=schema)
            entry["valid"] = True
        except ValidationError as exc:
            entry["errors"] = [exc.message]
            any_fail = True
        except json.JSONDecodeError as exc:
            entry["errors"] = [f"JSON decode error: {exc}"]
            any_fail = True
        except Exception as exc:  # defensive non-interactive failure reporting
            entry["errors"] = [f"Unexpected error: {exc}"]
            any_fail = True

        results.append(entry)

    status = "fail" if any_fail else "pass"
    print(json.dumps({"status": status, "results": results}, ensure_ascii=False))
    return 1 if any_fail else 0


if __name__ == "__main__":
    raise SystemExit(main())
