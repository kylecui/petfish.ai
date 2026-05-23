#!/usr/bin/env python3
"""CI check: validate pack-name parity across all 4 installers and packs/ directory.

Ground truth = pack directory names under packs/ (e.g. "fish-trail", "fish-reflection-pack").
Installers reference packs by directory name in their ALL_PACKS/$AllPacks arrays.

Architectural difference:
- Remote installers (remote-install.sh/.ps1): use static ALL_PACKS/$AllPacks arrays
- Local installers (install.sh/.ps1): dynamically scan packs/ directory, use alias
  mappings for user-facing names

This script checks:
1. Remote installer arrays include ALL pack directory names from packs/
2. Remote installers don't have stale duplicate array declarations

Usage:
    python check_installer_parity.py [--packs-dir packs/] [--repo-root .]
"""
import argparse
import os
import re
import sys


def extract_last_bash_all_packs(filepath: str) -> tuple[set, int]:
    """Extract pack names from the LAST ALL_PACKS array in bash installer.

    Returns (pack_set, count_of_declarations).
    Multiple declarations = stale code bug.
    """
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    matches = list(re.finditer(r"ALL_PACKS\s*=\s*\(([^)]+)\)", content, re.DOTALL))
    if not matches:
        return set(), 0
    # Use the LAST declaration (PowerShell/bash: last wins)
    entries = matches[-1].group(1)
    packs = set(re.findall(r'"([^"]+)"', entries))
    return packs, len(matches)


def extract_last_ps1_all_packs(filepath: str) -> tuple[set, int]:
    """Extract pack names from the LAST $AllPacks array in PS1 installer.

    Returns (pack_set, count_of_declarations).
    Multiple declarations = stale code bug.
    """
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    matches = list(re.finditer(r"\$AllPacks\s*=\s*@\(([^)]+)\)", content, re.DOTALL))
    if not matches:
        return set(), 0
    entries = matches[-1].group(1)
    packs = set(re.findall(r'"([^"]+)"', entries))
    return packs, len(matches)


def get_pack_dir_names(packs_dir: str) -> set:
    """Get pack directory names from packs/ — the ground truth."""
    result = set()
    if not os.path.isdir(packs_dir):
        return result
    for entry in os.listdir(packs_dir):
        if os.path.isdir(os.path.join(packs_dir, entry)):
            result.add(entry)
    return result


def main():
    parser = argparse.ArgumentParser(description="Check installer pack-name parity")
    parser.add_argument("--packs-dir", default="packs", help="Path to packs/ directory")
    parser.add_argument("--repo-root", default=".", help="Repository root")
    args = parser.parse_args()

    repo_root = os.path.abspath(args.repo_root)
    packs_dir = os.path.join(repo_root, args.packs_dir)

    ground_truth = get_pack_dir_names(packs_dir)
    errors = []
    warnings = []

    print("=== Installer Pack-Name Parity Check ===\n")
    print(f"Ground truth: {len(ground_truth)} packs in {args.packs_dir}/")
    print(f"  {sorted(ground_truth)}\n")

    # Remote installers — must have ALL packs in their static arrays
    remote_installers = {
        "remote-install.sh": os.path.join(repo_root, "remote-install.sh"),
        "remote-install.ps1": os.path.join(repo_root, "remote-install.ps1"),
    }

    for name, filepath in remote_installers.items():
        if not os.path.exists(filepath):
            print(f"  SKIP {name}: file not found")
            continue

        if name.endswith(".sh"):
            packs_in_installer, decl_count = extract_last_bash_all_packs(filepath)
        else:
            packs_in_installer, decl_count = extract_last_ps1_all_packs(filepath)

        # Check for duplicate declarations (stale code)
        if decl_count > 1:
            errors.append(f"{name}: {decl_count} ALL_PACKS declarations (expected 1) — stale duplicate")

        # Check for packs in dir but not in installer
        missing = ground_truth - packs_in_installer
        extra = packs_in_installer - ground_truth

        if not missing and not extra and decl_count == 1:
            print(f"  OK: {name} ({len(packs_in_installer)} packs)")
        else:
            if missing:
                errors.append(f"{name}: missing packs {sorted(missing)}")
            if extra:
                warnings.append(f"{name}: extra entries not in packs/ dir: {sorted(extra)}")

    print()
    if warnings:
        for w in warnings:
            print(f"  WARN: {w}")

    if errors:
        print(f"\nFAIL: {len(errors)} parity issue(s):")
        for e in errors:
            print(f"  - {e}")
        sys.exit(1)
    else:
        print("PASS: All remote installers reference all packs (no duplicates, no missing).")
        sys.exit(0)


if __name__ == "__main__":
    main()
