#!/usr/bin/env python3
"""Reading-notes JSONL validator. Pure stdlib. Inspired by evidence_lint.py pattern.

Run: uv run python scripts/reading_notes_lint.py --input .petfish/notes/reading-notes.jsonl
"""
import argparse, json, re, sys
from pathlib import Path

NOTE_ID_RE = re.compile(r"^CN-\d{6}$")
FILE_TYPES = {"code", "doc", "config", "test"}
CONFIDENCE = {"high", "medium", "low"}
REQUIRED = ["note_id", "file_path", "file_type", "language", "summary", "confidence"]
RECOMMENDED = ["file_mtime", "file_size"]  # for staleness detection


def lint(path: Path) -> int:
    errors, warnings = [], []
    total = 0
    for line_no, raw in enumerate(path.open(encoding="utf-8"), 1):
        line = raw.strip()
        if not line:
            continue
        total += 1
        nid = "<unknown>"
        try:
            entry = json.loads(line)
        except json.JSONDecodeError as e:
            errors.append(f"line {line_no}: invalid JSON: {e}")
            continue
        if not isinstance(entry, dict):
            errors.append(f"line {line_no}: not a JSON object")
            continue
        nid = entry.get("note_id", "<missing>")
        for field in REQUIRED:
            if field not in entry or not str(entry.get(field, "")).strip():
                errors.append(f"line {line_no} [{nid}]: missing required field '{field}'")
        if not NOTE_ID_RE.match(str(entry.get("note_id", ""))):
            errors.append(f"line {line_no} [{nid}]: note_id must match CN-\\d{{6}}")
        if entry.get("file_type") not in FILE_TYPES:
            errors.append(f"line {line_no} [{nid}]: file_type must be one of {FILE_TYPES}")
        if entry.get("confidence") not in CONFIDENCE:
            errors.append(f"line {line_no} [{nid}]: confidence must be one of {CONFIDENCE}")
        if entry.get("file_type") == "code" and not entry.get("symbol"):
            warnings.append(f"line {line_no} [{nid}]: code file without 'symbol' field")
        if not entry.get("dependencies"):
            warnings.append(f"line {line_no} [{nid}]: no dependencies listed")
        for field in RECOMMENDED:
            if field not in entry:
                warnings.append(f"line {line_no} [{nid}]: missing recommended field '{field}' (needed for staleness detection)")

    print(f"Reading-notes lint: {total} entries, {len(errors)} errors, {len(warnings)} warnings")
    for e in errors:
        print(f"  ERROR  {e}")
    for w in warnings:
        print(f"  WARN   {w}")
    if errors:
        print(f"\nstatus: fail")
        return 1
    print(f"\nstatus: pass")
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Lint reading-notes JSONL")
    parser.add_argument("--input", required=True, type=Path, help="Path to reading-notes.jsonl")
    args = parser.parse_args()
    if not args.input.exists():
        print(f"File not found: {args.input}")
        sys.exit(1)
    sys.exit(lint(args.input))
