#!/usr/bin/env python3
"""
PEtFiSh Companion — Check Installed Packs

Reads installed-packs.json from the target project and reports:
  - Which packs are installed (with version and timestamp)
  - Which packs from the catalog are NOT installed
  - Optional: version comparison against latest in SKILL_builder

Usage:
  uv run check_installed.py --target /path/to/project
  uv run check_installed.py --target /path/to/project --platform claude
  uv run check_installed.py --target . --json
"""

import argparse
import json
import sys
from pathlib import Path
import platform as platform_mod

# Platform → registry file path (relative to project root)
PLATFORM_REGISTRY_PATHS = {
    "opencode": ".opencode/installed-packs.json",
    "claude": ".claude/installed-packs.json",
    "codex": ".agents/installed-packs.json",
    "cursor": ".cursor/installed-packs.json",
    "copilot": ".github/installed-packs.json",
    "windsurf": ".windsurf/installed-packs.json",
    "antigravity": ".agents/installed-packs.json",
    "universal": ".agents/installed-packs.json",
}

# Known aliases → pack names (keep in sync with install scripts)
KNOWN_PACKS = {
    "init": "project-initializer-skill",
    "companion": "petfish-companion-skill",
    "course": "opencode-course-skills-pack",
    "deploy": "repo-deploy-ops-skill-pack",
    "petfish": "petfish-style-skill",
    "ppt": "opencode-ppt-skills",
    "testdocs": "opencode-skill-pack-testcases-usage-docs",
    "calibrate": "anti-sycophancy-calibration-pack",
    "context": "context-router-skill",
    "trust": "trustskills-governance-pack",
}


def get_global_registry_paths() -> dict[str, Path]:
    """Build global registry paths per platform."""
    home = Path.home()
    return {
        "opencode": home / ".config/opencode/installed-packs.json",
        "claude": home / ".claude/installed-packs.json",
        "codex": home / ".codex/installed-packs.json",
        "cursor": home / ".cursor/installed-packs.json",
        "copilot": home / ".github/installed-packs.json",
        "windsurf": home / ".codeium/windsurf/installed-packs.json",
        "antigravity": home / ".gemini/antigravity/installed-packs.json",
        "universal": home / ".agents/installed-packs.json",
    }


def find_registry(target: Path, platform: str | None = None) -> Path | None:
    """Find installed-packs.json in the target project or global paths."""
    if platform:
        candidates = [PLATFORM_REGISTRY_PATHS.get(platform, "")]
    else:
        candidates = list(PLATFORM_REGISTRY_PATHS.values())

    # Deduplicate while preserving order
    seen = set()
    unique = []
    for c in candidates:
        if c and c not in seen:
            seen.add(c)
            unique.append(c)

    # Check project-level paths first
    for rel in unique:
        path = target / rel
        if path.exists():
            return path

    # Check global paths
    global_paths = get_global_registry_paths()
    if platform:
        # Only check the specified platform's global path
        global_candidate = global_paths.get(platform)
        if global_candidate and global_candidate.exists():
            return global_candidate
    else:
        # Check all global paths
        for global_path in global_paths.values():
            if global_path.exists():
                return global_path

    return None


def load_registry(path: Path) -> dict:
    """Load and return the installed-packs.json content."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        print(f"Error reading {path}: {e}", file=sys.stderr)
        return {}


def check(target: Path, platform: str | None = None, as_json: bool = False):
    """Check installed packs and report status."""
    registry_path = find_registry(target, platform)

    if not registry_path:
        if as_json:
            print(
                json.dumps(
                    {"error": "no registry found", "target": str(target)}, indent=2
                )
            )
        else:
            plat_hint = f" (platform: {platform})" if platform else ""
            print(f"No installed-packs.json found in {target}{plat_hint}")
            print("This project may not have any PEtFiSh packs installed yet.")
            print(f"\nLooked in: {', '.join(set(PLATFORM_REGISTRY_PATHS.values()))}")
        sys.exit(0)

    registry = load_registry(registry_path)
    installed = registry.get("packs", {})

    # Build status
    installed_list = []
    missing_list = []

    for alias, pack_name in KNOWN_PACKS.items():
        info = installed.get(pack_name)
        if info:
            installed_list.append(
                {
                    "alias": alias,
                    "pack": pack_name,
                    "version": info.get("version", "unknown"),
                    "installed_at": info.get("installed_at", "unknown"),
                }
            )
        else:
            missing_list.append({"alias": alias, "pack": pack_name})

    if as_json:
        print(
            json.dumps(
                {
                    "registry_path": str(registry_path),
                    "installed": installed_list,
                    "not_installed": missing_list,
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return

    # Pretty print
    print(f"Registry: {registry_path}\n")

    if installed_list:
        print("Installed packs:")
        for p in installed_list:
            print(f"  ✅ {p['alias'].ljust(12)} v{p['version']}  ({p['installed_at']})")
    else:
        print("No PEtFiSh packs installed.")

    if missing_list:
        print(f"\nAvailable (not installed):")
        for p in missing_list:
            print(f"  📦 {p['alias'].ljust(12)} {p['pack']}")

    print(f"\nTotal: {len(installed_list)} installed, {len(missing_list)} available")


def main():
    parser = argparse.ArgumentParser(description="PEtFiSh — Check Installed Packs")
    parser.add_argument(
        "--target", type=str, default=".", help="Target project path (default: .)"
    )
    parser.add_argument(
        "--platform",
        type=str,
        choices=list(PLATFORM_REGISTRY_PATHS.keys()),
        help="Limit search to specific platform registry",
    )
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    target = Path(args.target).resolve()
    if not target.exists():
        print(f"Target path does not exist: {target}", file=sys.stderr)
        sys.exit(1)

    check(target, platform=args.platform, as_json=args.json)


if __name__ == "__main__":
    main()
