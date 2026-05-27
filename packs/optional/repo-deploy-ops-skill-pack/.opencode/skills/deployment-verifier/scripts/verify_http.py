#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.11"
# ///
"""Run HTTP smoke checks from a JSON spec and emit JSON results."""

from __future__ import annotations

import argparse
import json
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any


def do_check(item: dict[str, Any]) -> dict[str, Any]:
    url = item["url"]
    timeout = float(item.get("timeout", 5))
    method = item.get("method", "GET").upper()
    headers = item.get("headers", {})
    expected_status = int(item.get("expected_status", 200))
    contains_text = item.get("contains_text")
    req = urllib.request.Request(url=url, method=method, headers=headers)
    started = time.time()
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body_bytes = resp.read()
            body = body_bytes.decode("utf-8", errors="ignore")
            status = getattr(resp, "status", None) or resp.getcode()
            ok = status == expected_status
            if contains_text is not None:
                ok = ok and (contains_text in body)
            return {
                "name": item.get("name", url),
                "url": url,
                "passed": ok,
                "status": status,
                "expected_status": expected_status,
                "contains_text": contains_text,
                "body_preview": body[:500],
                "elapsed_ms": int((time.time() - started) * 1000),
            }
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="ignore")
        return {
            "name": item.get("name", url),
            "url": url,
            "passed": False,
            "status": e.code,
            "expected_status": expected_status,
            "contains_text": contains_text,
            "body_preview": body[:500],
            "error": str(e),
            "elapsed_ms": int((time.time() - started) * 1000),
        }
    except Exception as e:
        return {
            "name": item.get("name", url),
            "url": url,
            "passed": False,
            "status": None,
            "expected_status": expected_status,
            "contains_text": contains_text,
            "body_preview": "",
            "error": str(e),
            "elapsed_ms": int((time.time() - started) * 1000),
        }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run HTTP smoke checks from JSON spec and emit JSON results."
    )
    parser.add_argument("--spec", required=True, help="Path to JSON spec file")
    parser.add_argument(
        "--output", default="-", help="Output file path or - for stdout"
    )
    args = parser.parse_args()

    spec = json.loads(Path(args.spec).read_text(encoding="utf-8"))
    checks = spec.get("checks", [])
    results = [do_check(item) for item in checks]
    passed = sum(1 for r in results if r["passed"])
    payload = {
        "summary": {
            "passed": passed,
            "failed": len(results) - passed,
            "total": len(results),
            "pass_rate": (passed / len(results)) if results else 1.0,
        },
        "results": results,
    }
    text = json.dumps(payload, ensure_ascii=False, indent=2)
    if args.output == "-":
        print(text)
    else:
        Path(args.output).write_text(text + "\n", encoding="utf-8")
    return 0 if passed == len(results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
