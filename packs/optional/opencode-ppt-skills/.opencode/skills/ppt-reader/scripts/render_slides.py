# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""Render PPTX slides to images using LibreOffice and Poppler.

Usage:
  uv run scripts/render_slides.py input.pptx --out rendered --resolution 150
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


def require_cmd(cmd: str) -> str:
    found = shutil.which(cmd)
    if not found:
        raise RuntimeError(f"Required command not found: {cmd}. Install it or skip visual rendering.")
    return found


def run(cmd: list[str]) -> None:
    proc = subprocess.run(cmd, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if proc.returncode != 0:
        raise RuntimeError(f"Command failed: {' '.join(cmd)}\nSTDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Render PPTX to per-slide JPG images.")
    parser.add_argument("input", type=Path, help="Input .pptx file")
    parser.add_argument("--out", type=Path, required=True, help="Output directory for rendered images")
    parser.add_argument("--resolution", type=int, default=150, help="DPI for pdftoppm, default 150")
    args = parser.parse_args()

    try:
        if not args.input.exists():
            raise FileNotFoundError(f"Input file not found: {args.input}")
        soffice = require_cmd("soffice")
        pdftoppm = require_cmd("pdftoppm")
        args.out.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            run([soffice, "--headless", "--convert-to", "pdf", "--outdir", str(tmp), str(args.input.resolve())])
            pdfs = list(tmp.glob("*.pdf"))
            if not pdfs:
                raise RuntimeError("LibreOffice did not produce a PDF file.")
            prefix = args.out / "slide"
            run([pdftoppm, "-jpeg", "-r", str(args.resolution), str(pdfs[0]), str(prefix)])
        images = sorted(str(p) for p in args.out.glob("slide-*.jpg"))
        manifest = {"input": str(args.input), "resolution": args.resolution, "images": images}
        (args.out / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
        print(json.dumps(manifest, ensure_ascii=False, indent=2))
        return 0
    except Exception as exc:  # noqa: BLE001
        print(f"Error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
