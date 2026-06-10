#!/usr/bin/env python3
"""Full gateway smoke test — schema drift pre-check + all endpoints.

Usage:
  python3 smoke_full.py [--base-url http://127.0.0.1:8787] [--api-key KEY]
  python3 smoke_full.py --skip-drift  # skip Phase 0 drift check
"""
import json
import os
import subprocess
import sys
import urllib.request
import urllib.error
import argparse


def post(url: str, body: dict, api_key: str) -> dict:
    data = json.dumps(body).encode()
    req = urllib.request.Request(url, data=data, headers={
        "Content-Type": "application/json",
        "X-API-Key": api_key,
    }, method="POST")
    resp = urllib.request.urlopen(req, timeout=15)
    return json.loads(resp.read())


def get(url: str) -> dict:
    req = urllib.request.Request(url, method="GET")
    resp = urllib.request.urlopen(req, timeout=10)
    return json.loads(resp.read())


def run_drift_check() -> dict:
    """Phase 0: Run check_schema_drift.py and return summary."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    drift_script = os.path.join(script_dir, "check_schema_drift.py")

    if not os.path.exists(drift_script):
        return {"status": "SKIP", "reason": "check_schema_drift.py not found"}

    try:
        result = subprocess.run(
            [sys.executable, drift_script, "--json"],
            capture_output=True, text=True, timeout=30,
        )
        if result.returncode != 0 and not result.stdout.strip():
            return {"status": "ERROR", "reason": result.stderr.strip()[:200]}

        data = json.loads(result.stdout.strip())
        summary = data.get("summary", {})
        drift_count = summary.get("drift", 0)
        total = summary.get("total", 0)

        return {
            "status": "DRIFT" if drift_count > 0 else "OK",
            "total": total,
            "match": summary.get("match", 0),
            "drift": drift_count,
            "drift_ops": summary.get("drift_operations", []),
            "detail": data,
        }
    except (subprocess.TimeoutExpired, json.JSONDecodeError, Exception) as e:
        return {"status": "ERROR", "reason": str(e)[:200]}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default="http://127.0.0.1:8787")
    parser.add_argument("--api-key", default="")
    parser.add_argument("--skip-drift", action="store_true", help="Skip Phase 0 schema drift check")
    args = parser.parse_args()

    base = args.base_url.rstrip("/")
    key = args.api_key
    passed = 0
    failed = 0

    # ── Phase 0: Schema drift pre-check ──
    if not args.skip_drift:
        print("Phase 0: Schema drift check")
        drift = run_drift_check()
        if drift["status"] == "SKIP":
            print(f"  SKIP  drift script not found")
        elif drift["status"] == "ERROR":
            print(f"  WARN  drift check error: {drift['reason']}")
        elif drift["status"] == "DRIFT":
            print(f"  WARN  {drift['drift']}/{drift['total']} operations have drift: {drift['drift_ops']}")
            print(f"        HTTP tests will proceed — fix drift before release")
        else:
            print(f"  OK    {drift['match']}/{drift['total']} operations match")
        print()

    # ── Phase 1: Endpoint tests ──
    print("Phase 1: Endpoint smoke tests")

    tests = [
        # --- GET endpoints ---
        {
            "name": "healthz",
            "method": "GET",
            "path": "/healthz",
            "check": lambda r: r.get("ok") is True,
        },
        {
            "name": "v1/health",
            "method": "GET",
            "path": "/v1/health",
            "check": lambda r: r.get("ok") is True and r.get("service") == "petfish-online-gateway",
        },
        {
            "name": "v1/version",
            "method": "GET",
            "path": "/v1/version",
            "check": lambda r: "version" in r and "service" in r,
        },

        # --- POST endpoints: normal payloads ---
        {
            "name": "routeCompanionRequest (basic)",
            "method": "POST",
            "path": "/v1/kernel/route",
            "body": {
                "user_message": "hello",
                "platform": "opencode",
            },
            "check": lambda r: r.get("ok") is True and r.get("module") == "router",
        },
        {
            "name": "suggestPacks (basic)",
            "method": "POST",
            "path": "/v1/catalog/suggest",
            "body": {
                "project_description": "A Python web API with FastAPI",
                "platform": "opencode",
            },
            "check": lambda r: r.get("ok") is True and "packs" in r.get("data", {}),
        },
        {
            "name": "renderInstallCommand",
            "method": "POST",
            "path": "/v1/install/render",
            "body": {
                "packs": ["petfish"],
                "platform": "opencode",
                "target": ".",
            },
            "check": lambda r: r.get("ok") is True and "command" in r.get("data", {}),
        },
        {
            "name": "profileProject",
            "method": "POST",
            "path": "/v1/project/profile",
            "body": {
                "project_description": "A course development project",
                "platform": "opencode",
            },
            "check": lambda r: r.get("ok") is True and "recommended_profile" in r.get("data", {}),
        },
        {
            "name": "classifyActionRisk",
            "method": "POST",
            "path": "/v1/trust/classify",
            "body": {
                "action_text": "review a file",
                "target_runtime": "opencode",
            },
            "check": lambda r: r.get("ok") is True,
        },

        # --- Schema drift: extra fields should not cause TypeError ---
        {
            "name": "routeCompanionRequest + runtime + risk_sensitive",
            "method": "POST",
            "path": "/v1/kernel/route",
            "body": {
                "user_message": "hello",
                "platform": "opencode",
                "runtime": {"kind": "online"},
                "risk_sensitive": True,
            },
            "check": lambda r: r.get("ok") is True,
        },
        {
            "name": "suggestPacks + risk_sensitive",
            "method": "POST",
            "path": "/v1/catalog/suggest",
            "body": {
                "project_description": "A Python web API with FastAPI",
                "platform": "opencode",
                "risk_sensitive": True,
            },
            "check": lambda r: r.get("ok") is True,
        },

        # --- Online runtime ---
        {
            "name": "routeCompanionRequest (online runtime)",
            "method": "POST",
            "path": "/v1/kernel/route",
            "body": {
                "user_message": "Help me set up a ChatGPT Project",
                "platform": "online",
                "runtime": {"kind": "online"},
            },
            "check": lambda r: r.get("ok") is True and r.get("data", {}).get("platform") == "online",
        },
    ]

    for t in tests:
        url = base + t["path"]
        try:
            if t["method"] == "GET":
                result = get(url)
            else:
                if not key:
                    print(f"  SKIP {t['name']} (no --api-key)")
                    continue
                result = post(url, t["body"], key)

            ok = t["check"](result)
            if ok:
                passed += 1
                print(f"  PASS  {t['name']}")
            else:
                failed += 1
                print(f"  FAIL  {t['name']}  check failed  ok={result.get('ok')} errors={result.get('errors')} warnings={result.get('warnings')}")
        except urllib.error.HTTPError as e:
            body_text = e.read().decode()[:200]
            failed += 1
            print(f"  FAIL  {t['name']}  HTTP {e.code}: {body_text}")
        except Exception as e:
            failed += 1
            print(f"  FAIL  {t['name']}  exception: {e}")

    print(f"\nResults: {passed} passed, {failed} failed, {passed + failed} total")
    return 1 if failed > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
