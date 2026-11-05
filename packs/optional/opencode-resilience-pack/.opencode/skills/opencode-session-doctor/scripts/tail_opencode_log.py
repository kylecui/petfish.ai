# /// script
# requires-python = ">=3.9"
# dependencies = []
# ///
"""Cross-platform follow-tail for the OpenCode log (session-doctor L2).

Replaces the platform-specific log-following pipelines that earlier runbooks
documented. Follows the log across rotation (reopens when the file is
replaced or shrinks), prints only lines matching a case-insensitive substring
(default: "prompt_async failed"), and supports a one-shot mode over the
existing file for triage.

Read-only. Stdlib only. Works on Windows / macOS / Linux under `uv run`.
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

DEFAULT_LOG = Path.home() / ".local" / "share" / "opencode" / "log" / "opencode.log"
DEFAULT_FILTER = "prompt_async failed"


def emit(line: str) -> None:
    sys.stdout.write(line if line.endswith("\n") else line + "\n")
    sys.stdout.flush()


def follow(path: Path, needle: str, interval: float) -> int:
    print(f"[tail_opencode_log] watching: {path}", file=sys.stderr)
    print(f"[tail_opencode_log] filter: {needle!r} (Ctrl-C to stop)", file=sys.stderr)
    handle = None
    position = 0
    identity = None
    try:
        while True:
            if handle is None:
                if not path.exists():
                    time.sleep(interval)
                    continue
                try:
                    handle = path.open("r", encoding="utf-8", errors="replace")
                    handle.seek(0, 2)  # start at end in follow mode
                    position = handle.tell()
                    identity = path.stat().st_size
                except OSError:
                    handle = None
                    time.sleep(interval)
                    continue
            try:
                size = path.stat().st_size
            except OSError:
                size = position
            if size < position:  # rotation or truncation: reopen from start
                handle.close()
                handle = None
                position = 0
                continue
            for line in handle.readlines():
                if needle.lower() in line.lower():
                    emit(line)
            position = handle.tell()
            time.sleep(interval)
    except KeyboardInterrupt:
        print("\n[tail_opencode_log] stopped", file=sys.stderr)
        return 0
    finally:
        if handle is not None:
            handle.close()
    return 0


def once(path: Path, needle: str) -> int:
    if not path.exists():
        print(
            f"ERROR: log not found at {path}\n"
            "Locate it via the opencode CLI or your process environment, "
            "then pass --log <path>.",
            file=sys.stderr,
        )
        return 2
    text = path.read_text(encoding="utf-8", errors="replace")
    hits = [line for line in text.splitlines() if needle.lower() in line.lower()]
    for line in hits:
        emit(line)
    print(f"\n[once] {len(hits)} matching line(s)", file=sys.stderr)
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Cross-platform filtered follow-tail of the OpenCode log."
    )
    parser.add_argument("--log", default=str(DEFAULT_LOG), help="log file path")
    parser.add_argument(
        "--filter", default=DEFAULT_FILTER, help="case-insensitive substring filter"
    )
    parser.add_argument(
        "--once",
        action="store_true",
        help="scan the existing file once and exit (triage mode)",
    )
    parser.add_argument(
        "--interval", type=float, default=1.0, help="poll interval seconds"
    )
    args = parser.parse_args(argv)
    path = Path(args.log).expanduser()
    if args.once:
        return once(path, args.filter)
    return follow(path, args.filter, args.interval)


if __name__ == "__main__":
    sys.exit(main())
