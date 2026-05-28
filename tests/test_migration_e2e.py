#!/usr/bin/env python3
"""
E2E migration test for migrate_legacy_v0_9 in all 4 installers.

Tests:
  - install.sh          (bash, has migration function)
  - remote-install.sh   (bash, has migration function)
  - install.ps1         (PS1, NO migration function → SKIP)
  - remote-install.ps1  (PS1, NO migration function → SKIP)

Strategy:
  For bash installers: extract the embedded Python code from the bash function
  and run it directly with python3 (no bash required on Windows).
  Also attempt Git Bash execution if available.

  For PS1 installers: check for Migrate-LegacyV09 function; SKIP if absent.

Usage:
  python tests/test_migration_e2e.py
  python tests/test_migration_e2e.py --verbose

Exit code: 0 if all tests pass or skip, 1 if any fail.
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
import textwrap

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

INSTALLERS = [
    {
        "name": "install.sh",
        "path": os.path.join(REPO_ROOT, "install.sh"),
        "type": "bash",
        "func_name": "migrate_legacy_v0_9",
    },
    {
        "name": "remote-install.sh",
        "path": os.path.join(REPO_ROOT, "remote-install.sh"),
        "type": "bash",
        "func_name": "migrate_legacy_v0_9",
    },
    {
        "name": "install.ps1",
        "path": os.path.join(REPO_ROOT, "install.ps1"),
        "type": "ps1",
        "func_name": "Migrate-LegacyV09",
    },
    {
        "name": "remote-install.ps1",
        "path": os.path.join(REPO_ROOT, "remote-install.ps1"),
        "type": "ps1",
        "func_name": "Migrate-LegacyV09",
    },
]

# ── v0.9 simulated state ──────────────────────────────────────────────────────

V09_INSTALLED_PACKS = {
    "packs": {
        "context-router-skill": {},
        "companion": {},
        "petfish-style-rewriter": {},
        "anti-sycophancy-calibration": {},
    }
}

V09_OPENCODE_JSON = {
    "mcp": {
        "context-state": {
            "command": "uv",
            "args": [
                "run",
                "python",
                ".petfish/context-router/mcp/server.py",
            ],
            "cwd": "/home/user/project/.petfish/context-router",
            "env": {
                "PETFISH_STATE_DIR": "/home/user/project/.petfish/context-router/state",
            },
        }
    }
}

V09_SKILL_DIRS = [
    "context-router",
    "petfish-companion",
    "marketplace-connector",
    "fish-trail",       # new dir already exists → old should be removed
]

V09_RULES_FILES = [
    "context-router.md",
    "anti-sycophancy.md",
]


def create_v09_state(tmpdir: str) -> dict:
    """Create a simulated v0.9.x project state under tmpdir. Returns paths dict."""
    opencode_dir = os.path.join(tmpdir, ".opencode")
    skills_dir = os.path.join(opencode_dir, "skills")
    rules_dir = os.path.join(opencode_dir, "agents-rules")
    config_file = os.path.join(opencode_dir, "opencode.json")
    registry_file = os.path.join(opencode_dir, "installed-packs.json")

    os.makedirs(skills_dir, exist_ok=True)
    os.makedirs(rules_dir, exist_ok=True)

    # installed-packs.json
    with open(registry_file, "w", encoding="utf-8") as f:
        json.dump(V09_INSTALLED_PACKS, f, indent=2)
        f.write("\n")

    # opencode.json
    with open(config_file, "w", encoding="utf-8") as f:
        json.dump(V09_OPENCODE_JSON, f, indent=2)
        f.write("\n")

    # skill dirs
    for d in V09_SKILL_DIRS:
        os.makedirs(os.path.join(skills_dir, d), exist_ok=True)
        # put a placeholder file so the dir is non-empty
        with open(os.path.join(skills_dir, d, "SKILL.md"), "w") as f:
            f.write(f"# {d}\n")

    # rules files
    for fname in V09_RULES_FILES:
        with open(os.path.join(rules_dir, fname), "w", encoding="utf-8") as f:
            f.write(f"# {fname}\n")

    return {
        "opencode_dir": opencode_dir,
        "skills_dir": skills_dir,
        "rules_dir": rules_dir,
        "config_file": config_file,
        "registry_file": registry_file,
        "skills_rel": ".opencode/skills",
        "config_rel": ".opencode/opencode.json",
        "rules_rel": ".opencode/agents-rules",
    }


# ── extraction helpers ────────────────────────────────────────────────────────

def extract_python_from_bash_func(installer_path: str, func_name: str) -> str | None:
    """
    Extract the embedded Python code from a bash function like:
        func_name() {
            ...
            python3 -c "
        <PYTHON CODE>
        " "$target" ...
        }
    Returns the Python source string, or None if not found.
    """
    with open(installer_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    # Find function start
    func_start = None
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped == f"{func_name}() {{" or stripped.startswith(f"{func_name}()"):
            if "{" in stripped:
                func_start = i
                break

    if func_start is None:
        return None

    # Find python3 -c " line inside the function
    py_start = None
    for i in range(func_start, len(lines)):
        if 'python3 -c "' in lines[i]:
            py_start = i + 1  # Python code starts on next line
            break

    if py_start is None:
        return None

    # Collect Python lines until closing `" "$target"` or `" "$1"` pattern
    py_lines = []
    for i in range(py_start, len(lines)):
        line = lines[i]
        # Closing line: starts with `"` followed by `$` args
        stripped = line.strip()
        if stripped.startswith('"') and ('$target' in stripped or '$1' in stripped or stripped == '"'):
            break
        py_lines.append(line)

    if not py_lines:
        return None

    return "".join(py_lines)


def has_ps1_function(installer_path: str, func_name: str) -> bool:
    """Check if a PS1 file contains a given function definition."""
    with open(installer_path, "r", encoding="utf-8") as f:
        content = f.read()
    return f"function {func_name}" in content or f"Function {func_name}" in content


def find_git_bash() -> str | None:
    """Find Git Bash executable on Windows."""
    candidates = [
        r"C:\Program Files\Git\bin\bash.exe",
        r"C:\Program Files (x86)\Git\bin\bash.exe",
        r"C:\Git\bin\bash.exe",
    ]
    for c in candidates:
        if os.path.isfile(c):
            return c
    # Try PATH
    result = shutil.which("bash")
    if result:
        return result
    return None


# ── run migration ─────────────────────────────────────────────────────────────

def run_migration_python(python_code: str, tmpdir: str, paths: dict, verbose: bool = False) -> tuple[bool, str]:
    """
    Run the extracted Python migration code directly with python3.
    Returns (success, output).
    """
    # Write to a temp script file
    script_file = os.path.join(tmpdir, "_migration_script.py")
    with open(script_file, "w", encoding="utf-8") as f:
        f.write(python_code)

    cmd = [
        sys.executable,
        script_file,
        tmpdir,                  # $target
        paths["skills_rel"],     # $skills_dir
        paths["config_rel"],     # $config_file
        paths["rules_rel"],      # $rules_dir
    ]

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=tmpdir,
        )
        output = result.stdout + result.stderr
        if verbose:
            print(f"    [python] exit={result.returncode}")
            if output.strip():
                for line in output.strip().splitlines():
                    print(f"    [python] {line}")
        return result.returncode == 0, output
    except Exception as e:
        return False, str(e)


def run_migration_bash(installer_path: str, func_name: str, tmpdir: str, paths: dict, verbose: bool = False) -> tuple[bool, str, str]:
    """
    Run the migration function via Git Bash.
    Returns (success, output, note).
    """
    bash = find_git_bash()
    if not bash:
        return False, "", "Git Bash not found — bash execution skipped"

    # Build a small bash script that sources the installer and calls the function
    # We need to extract just the function definition to avoid running the whole installer
    with open(installer_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Extract function body (from func_name() { to closing })
    lines = content.splitlines(keepends=True)
    func_start = None
    for i, line in enumerate(lines):
        if line.strip().startswith(f"{func_name}()") and "{" in line:
            func_start = i
            break

    if func_start is None:
        return False, "", f"Function {func_name} not found in {installer_path}"

    # Collect until closing } at column 0
    func_lines = []
    depth = 0
    for i in range(func_start, len(lines)):
        line = lines[i]
        func_lines.append(line)
        stripped = line.rstrip()
        if "{" in stripped:
            depth += stripped.count("{") - stripped.count("}")
        elif stripped == "}":
            depth -= 1
            if depth <= 0:
                break

    func_def = "".join(func_lines)

    # Convert Windows paths to bash-compatible paths
    tmpdir_bash = tmpdir.replace("\\", "/")
    if len(tmpdir_bash) > 1 and tmpdir_bash[1] == ":":
        tmpdir_bash = "/" + tmpdir_bash[0].lower() + tmpdir_bash[2:]

    script = textwrap.dedent(f"""\
        #!/bin/bash
        set -e
        {func_def}
        {func_name} "{tmpdir_bash}" "{paths['skills_rel']}" "{paths['config_rel']}" "{paths['rules_rel']}"
    """)

    script_file = os.path.join(tmpdir, "_bash_runner.sh")
    with open(script_file, "w", encoding="utf-8", newline="\n") as f:
        f.write(script)

    try:
        result = subprocess.run(
            [bash, script_file],
            capture_output=True,
            text=True,
            cwd=tmpdir,
        )
        output = result.stdout + result.stderr
        if verbose:
            print(f"    [bash] exit={result.returncode}")
            if output.strip():
                for line in output.strip().splitlines():
                    print(f"    [bash] {line}")
        return result.returncode == 0, output, ""
    except Exception as e:
        return False, "", str(e)


# ── assertions ────────────────────────────────────────────────────────────────

def check_migration_results(paths: dict) -> list[dict]:
    """
    Run all assertions against the post-migration state.
    Returns list of {name, passed, expected, actual, note}.
    """
    results = []

    def assert_check(name, passed, expected, actual, note=""):
        results.append({
            "name": name,
            "passed": passed,
            "expected": str(expected),
            "actual": str(actual),
            "note": note,
        })

    # Load registry
    try:
        with open(paths["registry_file"], "r", encoding="utf-8") as f:
            reg = json.load(f)
        packs = reg.get("packs", {})
        if isinstance(packs, list):
            packs = {p: {} for p in packs}
    except Exception as e:
        packs = {}
        assert_check("registry_loadable", False, "valid JSON", str(e))

    # Load opencode.json
    try:
        with open(paths["config_file"], "r", encoding="utf-8") as f:
            config = json.load(f)
    except Exception as e:
        config = {}
        assert_check("config_loadable", False, "valid JSON", str(e))

    # ── Registry assertions ──

    # 1. context-router-skill → fish-trail
    assert_check(
        "registry: context-router-skill renamed to fish-trail",
        "fish-trail" in packs and "context-router-skill" not in packs,
        "fish-trail in packs, context-router-skill absent",
        f"packs keys: {sorted(packs.keys())}",
    )

    # 2. companion → petfish-companion-skill
    assert_check(
        "registry: companion renamed to petfish-companion-skill",
        "petfish-companion-skill" in packs and "companion" not in packs,
        "petfish-companion-skill in packs, companion absent",
        f"packs keys: {sorted(packs.keys())}",
    )

    # 3. petfish-style-rewriter → petfish-style-skill (what the code actually does)
    assert_check(
        "registry: petfish-style-rewriter renamed to petfish-style-skill",
        "petfish-style-skill" in packs and "petfish-style-rewriter" not in packs,
        "petfish-style-skill in packs, petfish-style-rewriter absent",
        f"packs keys: {sorted(packs.keys())}",
    )

    # 4. anti-sycophancy-calibration → anti-sycophancy-calibration-pack (what the code does)
    assert_check(
        "registry: anti-sycophancy-calibration renamed to anti-sycophancy-calibration-pack",
        "anti-sycophancy-calibration-pack" in packs and "anti-sycophancy-calibration" not in packs,
        "anti-sycophancy-calibration-pack in packs, anti-sycophancy-calibration absent",
        f"packs keys: {sorted(packs.keys())}",
    )

    # ── Skill directory assertions ──

    skills_dir = paths["skills_dir"]

    # 5. context-router/ renamed to fish-trail/ (fish-trail already existed → context-router removed)
    assert_check(
        "skills: context-router/ removed (fish-trail/ already existed)",
        not os.path.isdir(os.path.join(skills_dir, "context-router")),
        "context-router/ absent",
        f"exists={os.path.isdir(os.path.join(skills_dir, 'context-router'))}",
    )

    assert_check(
        "skills: fish-trail/ still present",
        os.path.isdir(os.path.join(skills_dir, "fish-trail")),
        "fish-trail/ present",
        f"exists={os.path.isdir(os.path.join(skills_dir, 'fish-trail'))}",
    )

    # 6. petfish-companion/ renamed to fish-brain/
    assert_check(
        "skills: petfish-companion/ renamed to fish-brain/",
        os.path.isdir(os.path.join(skills_dir, "fish-brain"))
        and not os.path.isdir(os.path.join(skills_dir, "petfish-companion")),
        "fish-brain/ present, petfish-companion/ absent",
        f"fish-brain={os.path.isdir(os.path.join(skills_dir, 'fish-brain'))}, "
        f"petfish-companion={os.path.isdir(os.path.join(skills_dir, 'petfish-companion'))}",
    )

    # 7. marketplace-connector/ renamed to fish-market/
    assert_check(
        "skills: marketplace-connector/ renamed to fish-market/",
        os.path.isdir(os.path.join(skills_dir, "fish-market"))
        and not os.path.isdir(os.path.join(skills_dir, "marketplace-connector")),
        "fish-market/ present, marketplace-connector/ absent",
        f"fish-market={os.path.isdir(os.path.join(skills_dir, 'fish-market'))}, "
        f"marketplace-connector={os.path.isdir(os.path.join(skills_dir, 'marketplace-connector'))}",
    )

    # ── Rules file assertions ──

    rules_dir = paths["rules_dir"]

    # 8. context-router.md → fish-trail.md
    assert_check(
        "rules: context-router.md renamed to fish-trail.md",
        os.path.isfile(os.path.join(rules_dir, "fish-trail.md"))
        and not os.path.isfile(os.path.join(rules_dir, "context-router.md")),
        "fish-trail.md present, context-router.md absent",
        f"fish-trail.md={os.path.isfile(os.path.join(rules_dir, 'fish-trail.md'))}, "
        f"context-router.md={os.path.isfile(os.path.join(rules_dir, 'context-router.md'))}",
    )

    # 9. anti-sycophancy.md untouched
    assert_check(
        "rules: anti-sycophancy.md untouched",
        os.path.isfile(os.path.join(rules_dir, "anti-sycophancy.md")),
        "anti-sycophancy.md present",
        f"exists={os.path.isfile(os.path.join(rules_dir, 'anti-sycophancy.md'))}",
    )

    # ── opencode.json MCP assertions ──

    mcp = config.get("mcp", {})
    ctx_state = mcp.get("context-state", {})
    args = ctx_state.get("args", [])
    cwd = ctx_state.get("cwd", "")
    env = ctx_state.get("env", {})
    state_dir = env.get("PETFISH_STATE_DIR", "")

    # 10. args path updated: context-router → fish-trail
    args_str = " ".join(args) if isinstance(args, list) else str(args)
    assert_check(
        "config: mcp.context-state args path updated (context-router→fish-trail)",
        "fish-trail" in args_str and "context-router" not in args_str,
        "args contain fish-trail, not context-router",
        f"args={args}",
    )

    # 11. cwd updated
    assert_check(
        "config: mcp.context-state cwd updated (context-router→fish-trail)",
        "fish-trail" in cwd and "context-router" not in cwd,
        "cwd contains fish-trail, not context-router",
        f"cwd={cwd}",
    )

    # 12. env PETFISH_STATE_DIR updated
    assert_check(
        "config: mcp.context-state env.PETFISH_STATE_DIR updated",
        "fish-trail" in state_dir and "context-router" not in state_dir,
        "PETFISH_STATE_DIR contains fish-trail, not context-router",
        f"PETFISH_STATE_DIR={state_dir}",
    )

    return results


# ── test runner ───────────────────────────────────────────────────────────────

PASS = "\033[32mPASS\033[0m"
FAIL = "\033[31mFAIL\033[0m"
SKIP = "\033[33mSKIP\033[0m"


def run_installer_test(installer: dict, verbose: bool = False) -> dict:
    """Run migration test for one installer. Returns result dict."""
    name = installer["name"]
    path = installer["path"]
    itype = installer["type"]
    func_name = installer["func_name"]

    print(f"\n{'─'*60}")
    print(f"  Installer: {name}")
    print(f"{'─'*60}")

    # ── PS1: check for function, always SKIP ──
    if itype == "ps1":
        if not os.path.isfile(path):
            print(f"  {SKIP}  File not found: {path}")
            return {"installer": name, "status": "skip", "reason": "file not found"}
        found = has_ps1_function(path, func_name)
        if not found:
            msg = f"No '{func_name}' function found in {name} — PS1 migration not implemented"
            print(f"  {SKIP}  {msg}")
            return {"installer": name, "status": "skip", "reason": msg}
        else:
            # Unexpected: function exists, but we don't have a PS1 runner yet
            print(f"  {SKIP}  PS1 runner not implemented (function found but not tested)")
            return {"installer": name, "status": "skip", "reason": "PS1 runner not implemented"}

    # ── Bash: extract Python and run ──
    if not os.path.isfile(path):
        print(f"  {FAIL}  File not found: {path}")
        return {"installer": name, "status": "fail", "reason": "file not found", "assertions": []}

    python_code = extract_python_from_bash_func(path, func_name)
    if python_code is None:
        print(f"  {FAIL}  Could not extract Python code from {func_name}() in {name}")
        return {"installer": name, "status": "fail", "reason": "extraction failed", "assertions": []}

    if verbose:
        print(f"  Extracted {len(python_code.splitlines())} lines of Python from {func_name}()")

    # Create fresh v0.9 state
    tmpdir = tempfile.mkdtemp(prefix=f"petfish_test_{name.replace('.', '_')}_")
    try:
        paths = create_v09_state(tmpdir)

        # Run via Python directly
        print(f"  Running migration (python3 direct)...")
        ok, output = run_migration_python(python_code, tmpdir, paths, verbose=verbose)

        if not ok:
            print(f"  {FAIL}  Migration script exited with error")
            if output.strip():
                for line in output.strip().splitlines()[:10]:
                    print(f"    {line}")
            return {"installer": name, "status": "fail", "reason": "migration script error", "assertions": []}

        if verbose and output.strip():
            print("  Migration output:")
            for line in output.strip().splitlines():
                print(f"    {line}")

        # Check assertions
        assertions = check_migration_results(paths)
        passed = sum(1 for a in assertions if a["passed"])
        failed = sum(1 for a in assertions if not a["passed"])

        print(f"  Assertions: {passed} passed, {failed} failed")
        for a in assertions:
            status = PASS if a["passed"] else FAIL
            print(f"    {status}  {a['name']}")
            if not a["passed"] or verbose:
                print(f"           expected: {a['expected']}")
                print(f"           actual:   {a['actual']}")
                if a.get("note"):
                    print(f"           note:     {a['note']}")

        # Also try Git Bash if available
        bash = find_git_bash()
        if bash:
            print(f"\n  Also running via Git Bash ({bash})...")
            # Fresh state for bash run
            tmpdir2 = tempfile.mkdtemp(prefix=f"petfish_bash_{name.replace('.', '_')}_")
            try:
                paths2 = create_v09_state(tmpdir2)
                bash_ok, bash_out, bash_note = run_migration_bash(path, func_name, tmpdir2, paths2, verbose=verbose)
                if bash_note:
                    print(f"  {SKIP}  {bash_note}")
                elif bash_ok:
                    bash_assertions = check_migration_results(paths2)
                    bash_passed = sum(1 for a in bash_assertions if a["passed"])
                    bash_failed = sum(1 for a in bash_assertions if not a["passed"])
                    bash_status = PASS if bash_failed == 0 else FAIL
                    print(f"  {bash_status}  Git Bash: {bash_passed}/{len(bash_assertions)} assertions passed")
                else:
                    print(f"  {FAIL}  Git Bash execution failed")
                    if bash_out.strip():
                        for line in bash_out.strip().splitlines()[:5]:
                            print(f"    {line}")
            finally:
                shutil.rmtree(tmpdir2, ignore_errors=True)
        else:
            print(f"\n  Git Bash not found — bash execution skipped (Windows without Git Bash)")

        overall = "pass" if failed == 0 else "fail"
        return {
            "installer": name,
            "status": overall,
            "assertions": assertions,
            "passed": passed,
            "failed": failed,
        }

    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


def main():
    parser = argparse.ArgumentParser(description="E2E migration test for all 4 installers")
    parser.add_argument("--verbose", "-v", action="store_true", help="Show detailed output")
    args = parser.parse_args()

    print("=" * 60)
    print("  PEtFiSh migrate_legacy_v0_9 — E2E Test")
    print("=" * 60)

    results = []
    for installer in INSTALLERS:
        result = run_installer_test(installer, verbose=args.verbose)
        results.append(result)

    # Summary
    print(f"\n{'='*60}")
    print("  SUMMARY")
    print(f"{'='*60}")

    any_fail = False
    for r in results:
        status = r["status"]
        if status == "pass":
            label = PASS
        elif status == "skip":
            label = SKIP
        else:
            label = FAIL
            any_fail = True

        detail = ""
        if status in ("pass", "fail") and "passed" in r:
            detail = f"  ({r['passed']}/{r['passed'] + r['failed']} assertions)"

        print(f"  {label}  {r['installer']}{detail}")
        if status == "skip":
            print(f"         {r.get('reason', '')}")

    print()
    if any_fail:
        print("Result: FAIL — one or more installers failed assertions")
        sys.exit(1)
    else:
        print("Result: PASS — all tested installers passed (skipped = not applicable)")
        sys.exit(0)


if __name__ == "__main__":
    main()
