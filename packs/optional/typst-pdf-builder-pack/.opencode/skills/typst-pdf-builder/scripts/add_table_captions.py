#!/usr/bin/env python3
"""Add table captions to all tables in chapter Markdown files.

Discovers Ch*_*.md files in the given directory and appends a caption line
`**表N  标题**` after each table. The caption text is derived from the
table header cells. Run this script before `build_pdf.py` so that the build
step can later reformat the captions as per-chapter `表X.Y.` labels.

Usage:
    python add_table_captions.py --dir content
"""

import argparse
import os
import re
import sys
from pathlib import Path


def extract_caption(header_line: str) -> str:
    """Generate a caption string from a Markdown table header line."""
    cells = [c.strip() for c in header_line.split("|")]
    cells = [re.sub(r"\*\*|\*|`|#", "", c) for c in cells if c.strip()]
    if not cells:
        return "数据表"
    meaningful = [c for c in cells if len(c) > 1]
    if len(meaningful) >= 2:
        return f"{meaningful[0]}与{meaningful[1]}对照"
    elif len(meaningful) == 1:
        return f"{meaningful[0]}表"
    return "数据表"


def add_table_captions(filepath: Path) -> int:
    """Add captions to all tables in one Markdown file. Return number of captions added."""
    lines = filepath.read_text(encoding="utf-8").split("\n")
    result: list[str] = []
    table_num = 0
    in_code = False
    prev_was_table = False
    table_header: str | None = None

    for line in lines:
        stripped = line.strip()
        if stripped.startswith("```"):
            in_code = not in_code
            if prev_was_table and table_header:
                table_num += 1
                caption_text = extract_caption(table_header)
                caption = f"**表{table_num}.  {caption_text}**"
                if result and result[-1].strip() != "":
                    result.append("")
                result.append(caption)
                table_header = None
            prev_was_table = False
            result.append(line)
            continue

        if in_code:
            result.append(line)
            continue

        is_pipe = stripped.startswith("|") and stripped.endswith("|")
        is_sep = bool(re.match(r"^\|[\s\-:|]+$", stripped))

        if is_pipe and not is_sep and not prev_was_table:
            # New table starts; save header for caption after the table ends.
            table_header = stripped
            prev_was_table = True
        elif is_pipe or is_sep:
            prev_was_table = True
        else:
            # Non-table line; if we were inside a table, emit the caption now.
            if prev_was_table and table_header:
                table_num += 1
                caption_text = extract_caption(table_header)
                caption = f"**表{table_num}.  {caption_text}**"
                if result and result[-1].strip() != "":
                    result.append("")
                result.append(caption)
                result.append("")
                table_header = None
            prev_was_table = False

        result.append(line)

    # Handle table at end of file.
    if prev_was_table and table_header:
        table_num += 1
        caption_text = extract_caption(table_header)
        caption = f"**表{table_num}.  {caption_text}**"
        if result and result[-1].strip() != "":
            result.append("")
        result.append(caption)

    new_content = "\n".join(result)
    if new_content != "\n".join(lines):
        filepath.write_text(new_content, encoding="utf-8")
        return table_num
    return 0


def discover_chapter_files(directory: Path) -> list[Path]:
    """Return sorted Markdown chapter files matching Ch*_*.md."""
    return sorted(directory.glob("Ch*_*.md"))


def main() -> None:
    parser = argparse.ArgumentParser(description="Add table captions to Markdown chapter files")
    parser.add_argument(
        "--dir",
        type=Path,
        default=Path.cwd(),
        help="Directory containing Ch*_*.md files (default: current directory)",
    )
    args = parser.parse_args()

    if not args.dir.is_dir():
        print(f"ERROR directory not found: {args.dir}")
        sys.exit(1)

    total = 0
    for filepath in discover_chapter_files(args.dir):
        count = add_table_captions(filepath)
        print(f"  {filepath.name[:30]:<30} {count} tables")
        total += count
    print(f"\nTotal: {total} tables captioned")


if __name__ == "__main__":
    main()
