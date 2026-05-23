#!/usr/bin/env python3
"""CI check: validate pack-name parity across all 4 installers and packs/ directory.

Extracts pack names/aliases from each installer, compares against the packs/
directory, and reports discrepancies. Intended for CI pipelines.

Usage:
    python check_installer_parity.py [--packs-dir packs/]
"""
import argparse
import json
import os
import re
import sys


def extract_bash_packs(filepath: str) -> set:
    """Extract pack names from bash installer ALL_PACKS array."""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    m = re.search(r"ALL_PACKS\s*=\s*\(([^)]+)\)", content, re.DOTALL)
    if not m:
        return set()
    entries = m.group(1)
    return set(re.findall(r'"([^"]+)"', entries))


def extract_ps1_packs(filepath: str) -> set:
    """Extract pack names from PowerShell installer $AllPacks array."""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    m = re.search(r"\$AllPacks\s*=\s*@(\([^)]+\))", content, re.DOTALL)
    if not m:
        return set()
    entries = m.group(1)
    return set(re.findall(r'"([^"]+)"', entries))


def get_pack_dirs(packs_dir: str) -> set:
    """Get pack alias names from packs/ directory via pack-manifest.json."""
    result = set()
    if not os.path.isdir(packs_dir):
        return result
    for entry in os.listdir(packs_dir):
        pack_dir = os.path.join(packs_dir, entry)
        if not os.path.isdir(pack_dir):
            continue
        manifest_path = os.path.join(pack_dir, "pack-manifest.json")
        if os.path.exists(manifest_path):
            try:
                with open(manifest_path, "r", encoding="utf-8") as f:
                    manifest = json.load(f)
                alias = manifest.get("alias", "")
                if alias:
                    result.add(alias)
                result.add(entry)
            except (json.JSONDecodeError, OSError):
                result.add(entry)
        else:
            result.add(entry)
    return result


def main():
    parser = argparse.ArgumentParser(description="Check installer pack-name parity")
    parser.add_argument("--packs-dir", default="packs", help="Path to packs/ directory")
    parser.add_argument("--repo-root", default=".", help="Repository root")
    args = parser.parse_args()

    repo_root = os.path.abspath(args.repo_root)
    packs_dir = os.path.join(repo_root, args.packs_dir)

    installers = {
        "install.sh": os.path.join(repo_root, "install.sh"),
        "remote-install.sh": os.path.join(repo_root, "remote-install.sh"),
        "install.ps1": os.path.join(repo_root, "install.ps1"),
        "remote-install.ps1": os.path.join(repo_root, "remote-install.ps1"),
    }

    packs_from_dir = get_pack_dirs(packs_dir)
    errors = []

    print("=== Installer Pack-Name Parity Check ===\n")
    print(f"Ground truth: {len(packs_from_dir)} packs in {args.packs_dir}/")
    print(f"  {sorted(packs_from_dir)}\n")

    for name, filepath in installers.items():
        if not os.path.exists(filepath):
            print(f"  SKIP {name}: file not found")
            continue

        if name.endswith(".sh"):
            packs_in_installer = extract_bash_packs(filepath)
        else:
            packs_in_installer = extract_ps1_packs(filepath)

        missing = packs_from_dir - packs_in_installer
        extra = packs_in_installer - packs_from_dir

        if not missing and not extra:
            print(f"  OK: {name}")
        else:
            if missing:
                errors.append(f"{name}: missing packs {sorted(missing)}")
            if extra:
                print(f"  WARN {name}: extra entries: {sorted(extra)}")

    if errors:
        print(f"\nFAIL: {len(errors)} parity issue(s):")
        for e in errors:
            print(f"  - {e}")
        sys.exit(1)
    else:
        print("\nPASS: All installers reference all packs.")
        sys.exit(0)


if __name__ == "__main__":
    main()
