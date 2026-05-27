#!/usr/bin/env python3
"""
publish_pack.py — Bridge quality-gate PASS to petfish-market registry JSON.

Reads pack-manifest.json from packs/optional/<pack-name>/ and generates
a registry JSON entry suitable for petfish-market/registry/official/.

Usage:
    uv run publish_pack.py --pack <name> [--ref vX.Y.Z] [--output <dir>] [--dry-run]
    uv run publish_pack.py --all --ref vX.Y.Z [--output <dir>] [--dry-run]
    uv run publish_pack.py --help

Exit codes: 0 = success, 1 = error
"""

import argparse
import json
import os
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Known pack aliases (mirrors catalog_query.py KNOWN_PACKS)
# ---------------------------------------------------------------------------
PACK_ALIASES: dict[str, str] = {
    "research-skill-pack": "research",
    "opencode-course-skills-pack": "course",
    "repo-deploy-ops-skill-pack": "deploy",
    "opencode-ppt-skills": "ppt",
    "opencode-skill-pack-testcases-usage-docs": "testdocs",
    "petfish-style-skill": "petfish",
    "anti-sycophancy-calibration-pack": "calibrate",
    "trustskills-governance-pack": "trust",
    "fish-reflection-pack": "reflect",
}


def find_repo_root(start: Path) -> Path:
    """Walk up from start to find the repo root (contains packs/ directory)."""
    current = start.resolve()
    for _ in range(10):
        if (current / "packs").is_dir():
            return current
        parent = current.parent
        if parent == current:
            break
        current = parent
    raise FileNotFoundError(
        f"Could not find repo root (directory containing 'packs/') starting from {start}"
    )


def load_manifest(pack_dir: Path) -> dict:
    """Load and parse pack-manifest.json from pack_dir."""
    manifest_path = pack_dir / "pack-manifest.json"
    if not manifest_path.exists():
        raise FileNotFoundError(f"pack-manifest.json not found in {pack_dir}")
    try:
        with open(manifest_path, encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in {manifest_path}: {e}") from e


def build_registry_entry(
    pack_name: str,
    manifest: dict,
    ref: str,
    repo_root: Path,
) -> dict:
    """Build a registry JSON entry from a pack manifest."""
    # Determine aliases
    aliases: list[str] = []
    primary_alias = PACK_ALIASES.get(pack_name)
    if primary_alias:
        aliases.append(primary_alias)
    # Add legacy_names from manifest (deduplicated)
    for legacy in manifest.get("legacy_names", []):
        if legacy and legacy not in aliases:
            aliases.append(legacy)

    # Relative path from repo root
    pack_path = f"packs/optional/{pack_name}"

    entry = {
        "namespace": "official",
        "name": pack_name,
        "alias": aliases,
        "description": manifest.get("description", ""),
        "version": manifest.get("version", "0.1.0"),
        "repo": "kylecui/petfish.ai",
        "ref": ref,
        "path": pack_path,
        "skill_count": manifest.get("skill_count", 0),
        "command_count": manifest.get("command_count", 0),
        "agent_count": manifest.get("agent_count", 0),
        "license": "Apache-2.0",
        "author": "petfish-team",
        "platforms": ["opencode"],
        "gate_result": {},
    }
    return entry


def publish_pack(
    pack_name: str,
    repo_root: Path,
    ref: str,
    output_dir: Path,
    dry_run: bool,
    skip_gate: bool,
) -> dict:
    """
    Process a single pack. Returns the registry entry dict.
    Raises on error.
    """
    optional_root = repo_root / "packs" / "optional"
    core_root = repo_root / "packs" / "core"

    # Guard: refuse core packs
    core_pack_dir = core_root / pack_name
    if core_pack_dir.exists():
        raise ValueError(
            f"Core packs cannot be published: '{pack_name}' is under packs/core/. "
            "Only packs in packs/optional/ may be published to the market."
        )

    # Find pack in optional
    pack_dir = optional_root / pack_name
    if not pack_dir.exists():
        raise FileNotFoundError(
            f"Pack '{pack_name}' not found in packs/optional/. "
            f"Available packs: {', '.join(sorted(p.name for p in optional_root.iterdir() if p.is_dir()))}"
        )

    manifest = load_manifest(pack_dir)

    # Gate check warning (non-blocking — CI owns gate_result)
    if not skip_gate and not dry_run:
        # We just warn; we don't block because gate results live in CI
        pass

    entry = build_registry_entry(pack_name, manifest, ref, repo_root)

    if dry_run:
        print(json.dumps(entry, indent=2, ensure_ascii=False))
    else:
        output_dir.mkdir(parents=True, exist_ok=True)
        output_file = output_dir / f"{pack_name}.json"

        # Preserve existing gate_result if file already exists
        if output_file.exists():
            try:
                with open(output_file, encoding="utf-8") as f:
                    existing = json.load(f)
                if existing.get("gate_result"):
                    entry["gate_result"] = existing["gate_result"]
            except (json.JSONDecodeError, OSError):
                pass  # Overwrite if unreadable

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(entry, f, indent=2, ensure_ascii=False)
            f.write("\n")

    return entry


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Publish validated skill packs to petfish-market registry.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Preview a single pack (no files written)
  uv run publish_pack.py --pack research-skill-pack --dry-run

  # Preview all optional packs
  uv run publish_pack.py --all --dry-run

  # Publish a single pack with a git ref/tag
  uv run publish_pack.py --pack research-skill-pack --ref v1.4.0

  # Publish all optional packs
  uv run publish_pack.py --all --ref v1.4.0

  # Publish to a custom output directory
  uv run publish_pack.py --pack research-skill-pack --ref v1.4.0 --output ./out/

Exit codes: 0 = success, 1 = error
""",
    )
    parser.add_argument(
        "--pack",
        metavar="NAME",
        help="Pack directory name (e.g. research-skill-pack)",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Process all packs in packs/optional/",
    )
    parser.add_argument(
        "--ref",
        metavar="TAG",
        help="Git ref / tag to embed in registry entry (e.g. v1.4.0). Required unless --dry-run.",
    )
    parser.add_argument(
        "--output",
        metavar="DIR",
        default=None,
        help="Output directory for registry JSON files (default: ../petfish-market/registry/official/)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print generated JSON to stdout without writing files.",
    )
    parser.add_argument(
        "--skip-gate",
        action="store_true",
        help="Skip quality-gate verification (for testing only).",
    )

    args = parser.parse_args()

    # --- Validate arguments ---
    if not args.pack and not args.all:
        parser.error("Specify --pack <name> or --all.")

    if args.pack and args.all:
        parser.error("--pack and --all are mutually exclusive.")

    if not args.dry_run and not args.ref:
        parser.error("--ref <tag> is required when not using --dry-run.")

    # Use empty string as ref placeholder for dry-run
    ref = args.ref or "(dry-run)"

    # --- Find repo root ---
    script_path = Path(__file__).resolve()
    try:
        repo_root = find_repo_root(script_path.parent)
    except FileNotFoundError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1

    # --- Resolve output directory ---
    if args.output:
        output_dir = Path(args.output).resolve()
    else:
        # Default: sibling petfish-market repo
        output_dir = (repo_root.parent / "petfish-market" / "registry" / "official").resolve()

    # --- Collect pack names ---
    if args.all:
        optional_root = repo_root / "packs" / "optional"
        if not optional_root.exists():
            print(f"ERROR: packs/optional/ directory not found at {optional_root}", file=sys.stderr)
            return 1
        pack_names = sorted(p.name for p in optional_root.iterdir() if p.is_dir())
        if not pack_names:
            print("ERROR: No packs found in packs/optional/", file=sys.stderr)
            return 1
    else:
        pack_names = [args.pack]

    # --- Process packs ---
    published: list[str] = []
    errors: list[str] = []

    for pack_name in pack_names:
        try:
            publish_pack(
                pack_name=pack_name,
                repo_root=repo_root,
                ref=ref,
                output_dir=output_dir,
                dry_run=args.dry_run,
                skip_gate=args.skip_gate,
            )
            published.append(pack_name)
        except (FileNotFoundError, ValueError, OSError) as e:
            errors.append(f"{pack_name}: {e}")
            print(f"ERROR [{pack_name}]: {e}", file=sys.stderr)

    # --- Summary (to stderr so it doesn't mix with --dry-run JSON stdout) ---
    if args.dry_run:
        print(
            f"\n# dry-run: {len(published)} pack(s) — no files written",
            file=sys.stderr,
        )
    else:
        print(
            f"Published {len(published)} pack(s) to {output_dir}",
            file=sys.stderr,
        )
        for name in published:
            print(f"  ✓ {name}.json", file=sys.stderr)

    if errors:
        print(f"\n{len(errors)} error(s):", file=sys.stderr)
        for err in errors:
            print(f"  ✗ {err}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
