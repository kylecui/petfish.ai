"""Install script validation — install.py is the sole installer.

Legacy shell installers (install.ps1, install.sh, remote-install.ps1, remote-install.sh)
were deleted in v2.0. This test validates install.py as the unified installer.
"""

from __future__ import annotations

import ast
import importlib.util
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
INSTALL_PY = REPO_ROOT / "install.py"

# Import catalog_query for alias reference
_CQ_SCRIPT = (
    REPO_ROOT
    / "packs/core/petfish-companion-skill/.opencode/skills/fish-brain/scripts/catalog_query.py"
)
_spec = importlib.util.spec_from_file_location("catalog_query_ref", _CQ_SCRIPT)
_cq = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_cq)
CANONICAL_ALIASES = set(_cq.ALIAS_MAP.keys())


# ---------------------------------------------------------------------------
# install.py existence and syntax
# ---------------------------------------------------------------------------


def test_install_py_exists():
    """install.py must exist as the sole installer."""
    assert INSTALL_PY.exists(), "install.py is missing — it is the only installer"


def test_install_py_valid_python():
    """install.py must be syntactically valid Python."""
    content = INSTALL_PY.read_text(encoding="utf-8")
    try:
        ast.parse(content)
    except SyntaxError as e:
        pytest.fail(f"install.py has syntax errors: {e}")


# ---------------------------------------------------------------------------
# Alias consistency: install.py must cover all canonical aliases
# ---------------------------------------------------------------------------


def test_install_py_alias_coverage():
    """install.py must contain all canonical pack aliases from catalog_query.py."""
    content = INSTALL_PY.read_text(encoding="utf-8")
    found = set()
    for alias in CANONICAL_ALIASES:
        # Check if alias appears as a string literal in install.py
        if f'"{alias}"' in content or f"'{alias}'" in content:
            found.add(alias)

    missing = CANONICAL_ALIASES - found
    assert not missing, (
        f"install.py missing aliases: {missing}. "
        f"Found: {sorted(found)}, Expected: {sorted(CANONICAL_ALIASES)}"
    )


# ---------------------------------------------------------------------------
# Legacy script absence (regression guard)
# ---------------------------------------------------------------------------

LEGACY_SCRIPTS = [
    "install.ps1",
    "install.sh",
    "remote-install.ps1",
    "remote-install.sh",
]


@pytest.mark.parametrize("script", LEGACY_SCRIPTS)
def test_legacy_script_absent(script):
    """Legacy shell installers must not exist (deleted in v2.0)."""
    assert not (REPO_ROOT / script).exists(), (
        f"{script} should have been deleted in v2.0 — install.py is the sole installer"
    )


# ---------------------------------------------------------------------------
# catalog_query upgrade command must emit install.py only
# ---------------------------------------------------------------------------


def test_upgrade_command_uses_install_py():
    """catalog_query --upgrade must emit install.py, not legacy scripts."""
    import subprocess

    result = subprocess.run(
        [sys.executable, str(_CQ_SCRIPT), "--upgrade", "--json"],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=str(REPO_ROOT),
    )
    import json

    data = json.loads(result.stdout)
    command = data.get("command", "")
    assert "install.py" in command, f"Upgrade command must use install.py: {command}"
    assert "remote-install" not in command, (
        f"Upgrade command must not reference deprecated scripts: {command}"
    )
