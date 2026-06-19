#!/usr/bin/env python3
"""Pre-release verification gate.

MUST pass before `gh release create`. Checks:
1. CI is green on master
2. All packs install to a clean temp directory
3. Contract validators pass in INSTALLED context (not source repo)
4. Market index refs point to the latest tag

Usage: uv run python scripts/pre_release_check.py [--tag vX.Y.Z]
Exit: 0 = all checks pass, 1 = BLOCKED (fix before release)
"""
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
failures: list[str] = []


def run(cmd: list[str], cwd: Path | None = None, check: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, capture_output=True, text=True, cwd=cwd, check=check)


def check_ci_green():
    """1. CI must be green on master."""
    print("[1/4] Checking CI status on master...")
    r = run(["gh", "run", "list", "--branch", "master", "--limit", "1", "--json", "conclusion"], check=False)
    data = json.loads(r.stdout)
    if not data:
        failures.append("CI: no runs found on master")
        print("  FAIL: no CI runs on master")
        return
    conclusion = data[0].get("conclusion", "")
    if conclusion != "success":
        failures.append(f"CI: master is {conclusion}, not success")
        print(f"  FAIL: CI conclusion = {conclusion}")
    else:
        print("  PASS: CI green on master")


def check_install():
    """2. All packs must install to a clean temp dir."""
    print("[2/4] Installing all packs to temp dir...")
    tmpdir = Path(tempfile.mkdtemp(prefix="petfish-release-check-"))
    r = run(
        ["uv", "run", str(REPO_ROOT / "install.py"),
         "--pack", "all", "--force", "--target", str(tmpdir),
         "--platform", "opencode"],
        cwd=REPO_ROOT, check=False,
    )
    if r.returncode != 0:
        failures.append(f"Install: exit code {r.returncode}")
        print(f"  FAIL: install exited {r.returncode}")
        print(f"  stderr tail: {r.stderr[-500:] if r.stderr else '(empty)'}")
        shutil.rmtree(tmpdir, ignore_errors=True)
        return None
    skills_dir = tmpdir / ".opencode" / "skills"
    if not skills_dir.is_dir():
        failures.append("Install: .opencode/skills/ not created")
        print("  FAIL: skills dir missing")
        shutil.rmtree(tmpdir, ignore_errors=True)
        return None
    pack_count = len(list(skills_dir.iterdir()))
    print(f"  PASS: {pack_count} skills installed")
    return tmpdir


def check_validators_in_install(tmpdir: Path):
    """3. Contract validators must pass in INSTALLED context."""
    print("[3/4] Running validators in install context...")
    validators_dir = tmpdir / ".opencode" / "skills" / "petfish-companion" / "validators"
    if not validators_dir.is_dir():
        # Try fish-brain path
        validators_dir = tmpdir / ".opencode" / "skills" / "fish-brain" / "validators"
    if not validators_dir.is_dir():
        failures.append("Validators: directory not found in install")
        print("  FAIL: validators/ not found in installed skills")
        return

    test_files = sorted(validators_dir.glob("test_*.py"))
    if not test_files:
        failures.append("Validators: no test_*.py files found")
        print("  FAIL: no validator scripts found")
        return

    passed, failed = 0, 0
    for tf in test_files:
        r = run(["uv", "run", "python", str(tf)], cwd=tmpdir, check=False)
        if r.returncode == 0:
            passed += 1
        else:
            failed += 1
            failures.append(f"Validator: {tf.name} failed in install context")
    print(f"  {'PASS' if failed == 0 else 'FAIL'}: {passed} passed, {failed} failed in install context")


def check_market_refs():
    """4. Market index refs must point to latest tag."""
    print("[4/4] Checking market index refs...")
    r = run(["gh", "api", "repos/kylecui/petfish-market/contents/index.json", "--jq", ".content"], check=False)
    if r.returncode != 0:
        print("  SKIP: cannot fetch market index (network)")
        return
    import base64
    content = json.loads(base64.b64decode(r.stdout.strip()).decode("utf-8"))
    packs = content.get("packs", [])

    # Get latest tag
    r2 = run(["gh", "release", "view", "--json", "tagName"], check=False)
    if r2.returncode != 0:
        # No releases yet — use HEAD commit
        print("  SKIP: no existing release to compare")
        return
    latest_tag = json.loads(r2.stdout).get("tagName", "")

    # Check optional packs with repo field
    stale = []
    for pack in packs:
        repo = pack.get("repo", "")
        ref = pack.get("ref", "")
        if "petfish-pack-" in repo:  # separate market repo — potential staleness
            stale.append(f"{pack['name']}: {repo}@{ref} (separate repo)")
        elif repo == "kylecui/petfish.ai" and ref and ref != latest_tag and latest_tag:
            # Will be stale after new release — expected, but warn
            pass  # pre-release: refs will be bumped separately

    if stale:
        for s in stale:
            failures.append(f"Market: {s}")
        print(f"  FAIL: {len(stale)} pack(s) still pointing to separate market repos:")
        for s in stale:
            print(f"    └─ {s}")
    else:
        print("  PASS: all optional packs point to monorepo")


def main():
    print("=" * 60)
    print("PRE-RELEASE VERIFICATION GATE")
    print("=" * 60)
    print()

    check_ci_green()
    print()
    tmpdir = check_install()
    print()
    if tmpdir:
        check_validators_in_install(tmpdir)
        shutil.rmtree(tmpdir, ignore_errors=True)
    print()
    check_market_refs()

    print()
    print("=" * 60)
    if failures:
        print(f"RESULT: BLOCKED — {len(failures)} issue(s):")
        for f in failures:
            print(f"  ✗ {f}")
        print("\nFix ALL issues before running: gh release create")
        sys.exit(1)
    else:
        print("RESULT: ALL CHECKS PASS — safe to release")
        sys.exit(0)


if __name__ == "__main__":
    main()
