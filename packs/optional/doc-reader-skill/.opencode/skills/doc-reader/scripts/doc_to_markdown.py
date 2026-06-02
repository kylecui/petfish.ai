#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["markitdown[all]"]
# ///
"""doc_to_markdown.py — Convert documents to Markdown using markitdown.

A thin wrapper around markitdown that converts PDF, DOCX, XLSX, HTML,
PPTX, EPUB, and other formats to Markdown text.

Usage:
    uv run doc_to_markdown.py input.pdf --output output.md
    uv run doc_to_markdown.py input.docx
    uv run doc_to_markdown.py input.xlsx --output out.md --json meta.json
"""

import argparse
import json
import sys
from pathlib import Path


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Convert documents to Markdown using markitdown.",
    )
    parser.add_argument(
        "input",
        type=Path,
        help="Path to the input file (PDF, DOCX, XLSX, HTML, EPUB, etc.)",
    )
    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        default=None,
        help="Output Markdown file path. Defaults to stdout.",
    )
    parser.add_argument(
        "--json",
        "-j",
        type=Path,
        default=None,
        metavar="METADATA_PATH",
        help="Write structured metadata JSON to this path.",
    )
    return parser.parse_args()


def guess_title(text: str, source: str) -> str:
    """Extract a title guess from the first non-empty line or fall back to filename."""
    for line in text.splitlines():
        stripped = line.strip()
        if stripped:
            # Remove leading markdown heading markers
            cleaned = stripped.lstrip("#").strip()
            if cleaned:
                return cleaned[:200]
    return Path(source).stem


def main() -> None:
    """Entry point: convert document to Markdown."""
    args = parse_args()

    # Validate input file exists
    if not args.input.is_file():
        print(f"Error: input file not found: {args.input}", file=sys.stderr)
        sys.exit(1)

    # Import markitdown (deferred so --help works without the dependency)
    try:
        from markitdown import MarkItDown  # type: ignore[import-untyped]
    except ImportError:
        print(
            "Error: markitdown is not installed. "
            "Run this script with 'uv run' to auto-install dependencies.",
            file=sys.stderr,
        )
        sys.exit(1)

    # Convert
    try:
        result = MarkItDown().convert(str(args.input))
    except Exception as exc:
        print(f"Error converting {args.input}: {exc}", file=sys.stderr)
        sys.exit(1)

    text_content = result.text_content

    # Write Markdown output
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text_content, encoding="utf-8")
        print(f"Written: {args.output} ({len(text_content)} chars)", file=sys.stderr)
    else:
        print(text_content)

    # Write metadata JSON if requested
    if args.json:
        metadata = {
            "source_file": str(args.input),
            "source_ext": args.input.suffix.lower(),
            "text_length": len(text_content),
            "title_guess": guess_title(text_content, str(args.input)),
        }
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(
            json.dumps(metadata, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        print(f"Metadata: {args.json}", file=sys.stderr)


if __name__ == "__main__":
    main()
