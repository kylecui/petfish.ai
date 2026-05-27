#!/usr/bin/env python3
"""
PEtFiSh Companion — Check Installed Packs

Reads installed-packs.json from the target project and reports:
  - Which packs are installed (with version and timestamp)
  - Which packs from the catalog are NOT installed
  - Optional: version comparison against latest in petfish.ai

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
from urllib import error as urllib_error
from urllib import request as urllib_request

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
    "context": "fish-trail",
    "research": "research-skill-pack",
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


def compare_semver(installed: str, source: str) -> str:
    """Compare semver strings. Returns 'same', 'newer', 'older', or 'unknown'.

    'newer' means source is newer than installed (update available).
    'older' means installed is newer than source.
    """

    def _parse(v: str) -> list[int] | None:
        if not isinstance(v, str) or not v.strip():
            return None
        parts = v.strip().split(".")
        parsed = []
        for part in parts:
            if not part.isdigit():
                return None
            parsed.append(int(part))
        return parsed

    installed_parts = _parse(installed)
    source_parts = _parse(source)
    if installed_parts is None or source_parts is None:
        return "unknown"

    width = max(len(installed_parts), len(source_parts))
    installed_parts.extend([0] * (width - len(installed_parts)))
    source_parts.extend([0] * (width - len(source_parts)))

    for idx in range(width):
        if source_parts[idx] > installed_parts[idx]:
            return "newer"
        if source_parts[idx] < installed_parts[idx]:
            return "older"
    return "same"


def _fetch_json(url: str, timeout: int = 10) -> dict:
    req = urllib_request.Request(
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "petfish-companion-check-updates",
        },
    )
    with urllib_request.urlopen(req, timeout=timeout) as resp:
        data = resp.read()
    return json.loads(data.decode("utf-8"))


def check_updates(
    target: Path,
    platform: str | None = None,
    as_json: bool = False,
    repo: str = "kylecui/petfish.ai",
):
    """Check update availability for installed packs from latest GitHub release."""
    registry_path = find_registry(target, platform)
    if not registry_path:
        error_msg = "no registry found"
        if as_json:
            print(
                json.dumps(
                    {
                        "latest_release": None,
                        "updates": [],
                        "up_to_date": [],
                        "errors": [error_msg],
                    },
                    ensure_ascii=False,
                    indent=2,
                )
            )
        else:
            print(f"⚠️ Could not check updates: {error_msg}")
        return

    registry = load_registry(registry_path)
    installed = registry.get("packs", {})

    updates = []
    up_to_date = []
    errors = []

    try:
        release_meta = _fetch_json(
            f"https://api.github.com/repos/{repo}/releases/latest", timeout=10
        )
        latest_tag = str(release_meta.get("tag_name", "")).strip()
        if not latest_tag:
            raise ValueError("latest release tag not found")
    except (
        urllib_error.URLError,
        urllib_error.HTTPError,
        TimeoutError,
        OSError,
        ValueError,
        json.JSONDecodeError,
    ) as exc:
        message = str(exc)
        if as_json:
            print(
                json.dumps(
                    {
                        "latest_release": None,
                        "updates": [],
                        "up_to_date": [],
                        "errors": [message],
                    },
                    ensure_ascii=False,
                    indent=2,
                )
            )
        else:
            print(f"⚠️ Could not check updates: {message}")
        return

    for alias, pack_name in KNOWN_PACKS.items():
        info = installed.get(pack_name)
        if not isinstance(info, dict):
            continue

        installed_version = str(info.get("version", "unknown"))
        manifest_url = (
            f"https://raw.githubusercontent.com/{repo}/{latest_tag}/packs/"
            f"{pack_name}/pack-manifest.json"
        )

        try:
            manifest = _fetch_json(manifest_url, timeout=10)
            source_version = str(manifest.get("version", "unknown"))
        except (
            urllib_error.URLError,
            urllib_error.HTTPError,
            TimeoutError,
            OSError,
            json.JSONDecodeError,
            ValueError,
        ) as exc:
            errors.append(f"{alias}: {exc}")
            continue

        comparison = compare_semver(installed_version, source_version)
        row = {
            "alias": alias,
            "pack": pack_name,
            "installed": installed_version,
            "available": source_version,
        }
        if comparison == "newer":
            updates.append(row)
        else:
            up_to_date.append(row)

    if as_json:
        print(
            json.dumps(
                {
                    "latest_release": latest_tag,
                    "updates": updates,
                    "up_to_date": up_to_date,
                    "errors": errors,
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return

    if updates:
        for row in updates:
            print(f"⬆️  {row['alias']} {row['installed']} → {row['available']}")
    elif errors and not up_to_date:
        print(f"⚠️ Could not check updates: {errors[0]}")
    else:
        print(f"✅ All packs are up to date (latest release: {latest_tag})")

    if errors and (updates or up_to_date):
        print(f"⚠️ Could not check updates: {errors[0]}")


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
    parser.add_argument(
        "--check-updates",
        action="store_true",
        help="Check available updates from latest GitHub release",
    )
    parser.add_argument(
        "--repo",
        type=str,
        default="kylecui/petfish.ai",
        help="GitHub repo in owner/name format (default: kylecui/petfish.ai)",
    )
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    target = Path(args.target).resolve()
    if not target.exists():
        print(f"Target path does not exist: {target}", file=sys.stderr)
        sys.exit(1)

    if args.check_updates:
        check_updates(
            target,
            platform=args.platform,
            as_json=args.json,
            repo=args.repo,
        )
    else:
        check(target, platform=args.platform, as_json=args.json)


if __name__ == "__main__":
    main()
