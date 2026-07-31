#!/usr/bin/env python3
"""Batch export draw.io diagrams to PNG for the PDF build pipeline.

This script walks a source directory (typically diagrams-source/), finds all
.drawio files, and exports them as PNG using the draw.io desktop CLI. The
output directory structure mirrors the source structure, preserving the
M0-M9 (or m0-m9) module naming convention.

Usage:
    python export_drawio.py --source-dir diagrams-source --output-dir diagrams-export

Requires:
    draw.io desktop CLI (draw.io.exe on Windows).
"""

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

# Export parameters used by the textbook pipeline.
EXPORT_FORMAT = "png"
EXPORT_SCALE = 2
EXPORT_BORDER = 20


def find_drawio_cli() -> Path | None:
    """Auto-detect the draw.io CLI executable on Windows."""
    # Respect an explicit environment override.
    env_path = os.environ.get("DRAWIO_CLI")
    if env_path:
        candidate = Path(env_path)
        if candidate.exists():
            return candidate

    # Common Windows installation locations.
    candidates = [
        Path.home() / "AppData" / "Local" / "Programs" / "draw.io" / "draw.io.exe",
        Path(os.environ.get("LOCALAPPDATA", "")) / "Programs" / "draw.io" / "draw.io.exe",
        Path("C:") / "Program Files" / "draw.io" / "draw.io.exe",
        Path("C:") / "Program Files (x86)" / "draw.io" / "draw.io.exe",
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate

    # Fallback: search PATH for the executable name.
    exe_name = "draw.io.exe"
    found = shutil.which(exe_name)
    if found:
        return Path(found)

    return None


def export_file(drawio_exe: Path, source: Path, target: Path) -> bool:
    """Export a single .drawio file to PNG. Return True on success."""
    target.parent.mkdir(parents=True, exist_ok=True)

    cmd = [
        str(drawio_exe),
        "--export",
        "--format", EXPORT_FORMAT,
        "--scale", str(EXPORT_SCALE),
        "--border", str(EXPORT_BORDER),
        "--output", str(target),
        str(source),
    ]

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=120,
            creationflags=0x08000000,  # CREATE_NO_WINDOW on Windows
        )
        if result.returncode == 0:
            print(f"  OK {source} -> {target}")
            return True
        else:
            print(f"  FAIL {source}")
            for line in (result.stdout + result.stderr).split("\n"):
                if line.strip():
                    print(f"     {line}")
            return False
    except subprocess.TimeoutExpired:
        print(f"  TIMEOUT {source}")
        return False
    except Exception as exc:  # noqa: BLE001
        print(f"  ERROR {source}: {exc}")
        return False


def main() -> None:
    parser = argparse.ArgumentParser(description="Batch export draw.io diagrams to PNG")
    parser.add_argument(
        "--source-dir",
        type=Path,
        required=True,
        help="Directory containing .drawio source files (e.g. diagrams-source)",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        required=True,
        help="Directory for exported PNG files (e.g. diagrams-export)",
    )
    parser.add_argument(
        "--drawio-exe",
        type=Path,
        default=None,
        help="Path to draw.io CLI executable (default: auto-detect)",
    )
    args = parser.parse_args()

    if not args.source_dir.is_dir():
        print(f"ERROR source directory not found: {args.source_dir}")
        sys.exit(1)

    drawio_exe = args.drawio_exe or find_drawio_cli()
    if drawio_exe is None or not drawio_exe.exists():
        print("ERROR draw.io CLI not found.")
        print("Install draw.io desktop, set DRAWIO_CLI, or pass --drawio-exe.")
        sys.exit(1)

    sources = sorted(args.source_dir.rglob("*.drawio"))
    if not sources:
        print(f"No .drawio files found under {args.source_dir}")
        sys.exit(0)

    print(f"Exporting {len(sources)} diagram(s) from {args.source_dir}")
    successes = 0
    failures = 0

    for source in sources:
        relative = source.relative_to(args.source_dir)
        target = args.output_dir / relative.with_suffix(".png")
        if export_file(drawio_exe, source, target):
            successes += 1
        else:
            failures += 1

    print(f"\nDone: {successes} succeeded, {failures} failed")
    if failures:
        sys.exit(1)


if __name__ == "__main__":
    main()
    sys.stdout.flush()
    sys.stderr.flush()
    os._exit(0)  # Avoid Windows pipe-cleanup hangs.
