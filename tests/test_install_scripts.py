"""Install script validation — syntax checks + alias consistency."""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]

# Import catalog_query for alias reference
import importlib.util

_CQ_SCRIPT = (
    REPO_ROOT
    / "packs/core/petfish-companion-skill/.opencode/skills/petfish-companion/scripts/catalog_query.py"
)
_spec = importlib.util.spec_from_file_location("catalog_query_ref", _CQ_SCRIPT)
_cq = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_cq)
CANONICAL_ALIASES = set(_cq.ALIAS_MAP.keys())


# ---------------------------------------------------------------------------
# Script file existence
# ---------------------------------------------------------------------------

INSTALL_SCRIPTS = [
    "install.ps1",
    "install.sh",
    "remote-install.ps1",
    "remote-install.sh",
]


@pytest.mark.parametrize("script", INSTALL_SCRIPTS)
def test_script_exists(script):
    assert (REPO_ROOT / script).exists(), f"Missing install script: {script}"


# ---------------------------------------------------------------------------
# PowerShell syntax validation (Windows only)
# ---------------------------------------------------------------------------

PS_SCRIPTS = [s for s in INSTALL_SCRIPTS if s.endswith(".ps1")]


@pytest.mark.parametrize("script", PS_SCRIPTS)
@pytest.mark.skipif(
    sys.platform != "win32", reason="PowerShell syntax check on Windows only"
)
def test_ps1_syntax(script):
    path = REPO_ROOT / script
    result = subprocess.run(
        [
            "powershell",
            "-NoProfile",
            "-Command",
            f"$null = [System.Management.Automation.Language.Parser]::ParseFile('{path}', [ref]$null, [ref]$errors); $errors.Count",
        ],
        capture_output=True,
        text=True,
        timeout=30,
    )
    error_count = result.stdout.strip()
    assert error_count == "0", (
        f"{script} has {error_count} parse errors: {result.stderr}"
    )


# ---------------------------------------------------------------------------
# Bash syntax validation
# ---------------------------------------------------------------------------

BASH_SCRIPTS = [s for s in INSTALL_SCRIPTS if s.endswith(".sh")]


@pytest.mark.parametrize("script", BASH_SCRIPTS)
@pytest.mark.skipif(sys.platform == "win32", reason="bash -n on Unix only")
def test_bash_syntax(script):
    path = REPO_ROOT / script
    result = subprocess.run(
        ["bash", "-n", str(path)],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0, f"{script} has syntax errors: {result.stderr}"


# ---------------------------------------------------------------------------
# Alias consistency: extract aliases from scripts and compare to catalog
# ---------------------------------------------------------------------------


def _extract_ps1_aliases(path: Path) -> set[str]:
    """Extract pack alias strings from a PowerShell install script."""
    content = path.read_text(encoding="utf-8")
    aliases = set()
    # Match patterns like: "init" { ... } or "init" = "..."
    # In install.ps1, aliases appear in switch cases or hashtable keys
    for m in re.finditer(r'["\'](\w+)["\']\s*\{', content):
        candidate = m.group(1)
        if candidate.lower() in CANONICAL_ALIASES:
            aliases.add(candidate.lower())
    # Also check $AllPacks or similar array definitions
    for m in re.finditer(
        r'["\'](init|companion|course|deploy|petfish|ppt|testdocs|trust|calibrate|context|research)["\']',
        content,
    ):
        aliases.add(m.group(1).lower())
    return aliases


def _extract_bash_aliases(path: Path) -> set[str]:
    """Extract pack alias strings from a Bash install script."""
    content = path.read_text(encoding="utf-8")
    aliases = set()
    # Match associative array entries: [alias]="pack-name"
    for m in re.finditer(r'\[(\w+)\]="[\w-]+"', content):
        aliases.add(m.group(1).lower())
    # Match quoted alias strings
    for m in re.finditer(
        r'["\'](init|companion|course|deploy|petfish|ppt|testdocs|trust|calibrate|context|research)["\']',
        content,
    ):
        aliases.add(m.group(1).lower())
    # Match case patterns: alias) or "alias")
    for m in re.finditer(
        r"(?:^|\|)\s*(init|companion|course|deploy|petfish|ppt|testdocs|trust|calibrate|context|research)\s*\)",
        content,
        re.MULTILINE,
    ):
        aliases.add(m.group(1).lower())
    return aliases


@pytest.mark.parametrize("script", INSTALL_SCRIPTS)
def test_alias_consistency(script):
    """All canonical aliases from catalog_query.py should appear in each install script."""
    path = REPO_ROOT / script
    if script.endswith(".ps1"):
        found = _extract_ps1_aliases(path)
    else:
        found = _extract_bash_aliases(path)

    missing = CANONICAL_ALIASES - found
    assert not missing, (
        f"{script} missing aliases: {missing}. "
        f"Found: {sorted(found)}, Expected: {sorted(CANONICAL_ALIASES)}"
    )
