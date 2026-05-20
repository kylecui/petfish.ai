#!/usr/bin/env python3
"""CI check: Verify all 4 installers reference every pack in packs/ directory.

Local installers (install.ps1, install.sh) use alias tables mapping to pack dirs.
Remote installers (remote-install.ps1, remote-install.sh) use hardcoded ALL_PACKS arrays.

This script ensures no pack is accidentally omitted from any installer.
Exits 0 on success, 1 on parity failure.

Usage:
    python scripts/check_installer_parity.py
    uv run scripts/check_installer_parity.py
"""

import os
import re
import sys
from pathlib import Path


def get_pack_dirs(repo_root: Path) -> set[str]:
    """Get all directory names under packs/."""
    packs_dir = repo_root / "packs"
    if not packs_dir.is_dir():
        print(f"ERROR: {packs_dir} not found")
        sys.exit(1)
    return {d.name for d in packs_dir.iterdir() if d.is_dir()}


def extract_remote_sh_packs(repo_root: Path) -> set[str]:
    """Extract pack names from remote-install.sh ALL_PACKS array."""
    content = (repo_root / "remote-install.sh").read_text(encoding="utf-8")
    # ALL_PACKS=("pack1" "pack2" ...)
    match = re.search(r"ALL_PACKS=\(([^)]+)\)", content)
    if not match:
        print("ERROR: Could not find ALL_PACKS in remote-install.sh")
        sys.exit(1)
    raw = match.group(1)
    return set(re.findall(r'"([^"]+)"', raw))


def extract_remote_ps1_packs(repo_root: Path) -> set[str]:
    """Extract pack names from remote-install.ps1 $AllPacks array (last definition wins)."""
    content = (repo_root / "remote-install.ps1").read_text(encoding="utf-8")
    # Find all $AllPacks = @(...) blocks — last one is authoritative
    matches = re.findall(r"\$AllPacks\s*=\s*@\((.*?)\)", content, re.DOTALL)
    if not matches:
        print("ERROR: Could not find $AllPacks in remote-install.ps1")
        sys.exit(1)
    raw = matches[-1]  # last definition wins
    return set(re.findall(r'"([^"]+)"', raw))


def extract_local_sh_packs(repo_root: Path) -> set[str]:
    """Extract pack directory names from install.sh alias associative array values."""
    content = (repo_root / "install.sh").read_text(encoding="utf-8")
    # Pattern: [alias]="pack-dir-name"
    return set(re.findall(r'\[\w[^\]]*\]="([^"]+)"', content))


def extract_local_ps1_packs(repo_root: Path) -> set[str]:
    """Extract pack directory names from install.ps1 $Aliases hashtable values."""
    content = (repo_root / "install.ps1").read_text(encoding="utf-8")
    # Find the $Aliases = @{ ... } block
    match = re.search(r"\$Aliases\s*=\s*@\{(.*?)\}", content, re.DOTALL)
    if not match:
        print("ERROR: Could not find $Aliases in install.ps1")
        sys.exit(1)
    raw = match.group(1)
    # Pattern: "alias" = "pack-dir-name"
    return set(re.findall(r'=\s*"([^"]+)"', raw))


def main():
    repo_root = Path(__file__).resolve().parent.parent
    pack_dirs = get_pack_dirs(repo_root)

    print(f"Ground truth: {len(pack_dirs)} packs in packs/")
    print(f"  {sorted(pack_dirs)}\n")

    checks = {
        "remote-install.sh (ALL_PACKS)": extract_remote_sh_packs(repo_root),
        "remote-install.ps1 ($AllPacks)": extract_remote_ps1_packs(repo_root),
        "install.sh (aliases)": extract_local_sh_packs(repo_root),
        "install.ps1 ($Aliases)": extract_local_ps1_packs(repo_root),
    }

    failed = False
    for name, installer_packs in checks.items():
        missing = pack_dirs - installer_packs
        extra = installer_packs - pack_dirs
        if missing:
            print(f"FAIL: {name} is MISSING: {sorted(missing)}")
            failed = True
        elif extra:
            # Extra entries aren't a failure (could be aliases) but worth noting
            print(f"OK:   {name} (note: {len(extra)} extra entries not in packs/)")
        else:
            print(f"OK:   {name}")

    print()
    if failed:
        print("RESULT: FAIL — installer parity broken. See above for missing packs.")
        sys.exit(1)
    else:
        print("RESULT: PASS — all installers reference all packs.")
        sys.exit(0)


if __name__ == "__main__":
    main()
