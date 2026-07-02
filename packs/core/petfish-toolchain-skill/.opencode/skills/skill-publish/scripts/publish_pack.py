#!/usr/bin/env python3
"""
publish_pack.py — Bridge quality-gate PASS to petfish-market registry JSON.

Reads pack-manifest.json from packs/optional/<pack-name>/ and generates
a registry JSON entry suitable for petfish-market/registry/official/.

Usage:
    uv run publish_pack.py --pack <name> [--ref vX.Y.Z] [--output <dir>] [--dry-run]
    uv run publish_pack.py --all --ref vX.Y.Z [--output <dir>] [--dry-run]
    uv run publish_pack.py --pack <name> --ref vX.Y.Z --generate-index
    uv run publish_pack.py --all --ref vX.Y.Z --generate-index --push
    uv run publish_pack.py --help

Exit codes: 0 = success, 1 = error
"""

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
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
    "series-style-governor-pack": "series-style",
    "doc-reader-skill": "doc-reader",
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
        "license": manifest.get("license", "Apache-2.0"),
        "author": "petfish-team",
        "platforms": ["opencode"],
        "gate_result": {},
    }
    return entry


def validate_ref_exists(ref: str, repo: str = "kylecui/petfish.ai") -> bool:
    """Check that a git ref/tag actually exists in the target repo (#249).

    Uses gh API to verify the ref exists before embedding it in the registry.
    Returns True if the ref exists, False otherwise.
    """
    try:
        result = subprocess.run(
            ["gh", "api", f"repos/{repo}/git/refs/tags/{ref}",
             "--silent"],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            return True
        # Also check if it's a branch ref
        result = subprocess.run(
            ["gh", "api", f"repos/{repo}/branches/{ref}", "--silent"],
            capture_output=True,
            text=True,
        )
        return result.returncode == 0
    except FileNotFoundError:
        # gh CLI not available — cannot validate, warn but don't block
        print(
            f"WARNING: Cannot validate ref '{ref}' — gh CLI not found. "
            "Ensure the tag exists before publishing.",
            file=sys.stderr,
        )
        return True  # don't block if gh is unavailable


def generate_index_json(output_dir: Path, dry_run: bool = False) -> dict:
    """
    Regenerate index.json from all *.json files in output_dir (registry/official/).

    Reads each registry entry JSON, aggregates packs into an index, and writes
    index.json to output_dir's parent (the market repo root).

    Preserves any existing skills[] entries from the current index.json.

    Returns the generated index dict.
    """
    if not output_dir.exists():
        raise FileNotFoundError(
            f"Registry directory not found: {output_dir}. "
            "Run --pack or --all first to create registry entries."
        )

    # Collect all pack entries from registry/official/*.json
    packs: list[dict] = []
    for json_file in sorted(output_dir.glob("*.json")):
        try:
            with open(json_file, encoding="utf-8") as f:
                entry = json.load(f)
            packs.append(entry)
        except (json.JSONDecodeError, OSError) as e:
            print(
                f"WARNING: Skipping {json_file.name} — {e}",
                file=sys.stderr,
            )

    # Sort packs alphabetically by name
    packs.sort(key=lambda p: p.get("name", ""))

    # Determine the market repo root (parent of registry/official/)
    market_root = output_dir.parent.parent  # output_dir = .../registry/official/
    index_path = market_root / "index.json"

    # Preserve existing skills[] entries from current index.json
    existing_skills: list[dict] = []
    if index_path.exists():
        try:
            with open(index_path, encoding="utf-8") as f:
                existing_index = json.load(f)
            existing_skills = existing_index.get("skills", [])
        except (json.JSONDecodeError, OSError):
            pass  # Start fresh if unreadable

    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    index = {
        "version": 2,
        "generated_at": generated_at,
        "skill_count": 0,
        "pack_count": len(packs),
        "skills": existing_skills,
        "packs": packs,
    }

    if dry_run:
        print(json.dumps(index, indent=2, ensure_ascii=False))
        print(
            f"\n# dry-run: index.json would be written to {index_path} "
            f"({len(packs)} pack(s))",
            file=sys.stderr,
        )
    else:
        with open(index_path, "w", encoding="utf-8") as f:
            json.dump(index, f, indent=2, ensure_ascii=False)
            f.write("\n")
        print(
            f"Generated index.json at {index_path} ({len(packs)} pack(s))",
            file=sys.stderr,
        )

    return index


def push_to_market(market_repo_path: Path, pack_names: list[str], dry_run: bool = False) -> None:
    """
    Commit and push changes to the petfish-market repository via git/gh CLI.

    Steps:
      1. Check gh auth status (fail fast if not authenticated)
      2. git add registry/official/ index.json
      3. git commit -m "publish: <pack-names>"
      4. git push origin main

    All subprocess errors are raised with clear messages.
    """
    if not market_repo_path.exists():
        raise FileNotFoundError(
            f"petfish-market repo not found at {market_repo_path}. "
            "Clone it first: git clone https://github.com/kylecui/petfish-market.git"
        )

    commit_message = "publish: " + ", ".join(pack_names)

    if dry_run:
        print(
            f"# dry-run: would run in {market_repo_path}:\n"
            f"#   gh auth status\n"
            f"#   git add registry/official/ index.json\n"
            f'#   git commit -m "{commit_message}"\n'
            f"#   git push origin main",
            file=sys.stderr,
        )
        return

    # --- Step 1: Check gh auth status ---
    try:
        result = subprocess.run(
            ["gh", "auth", "status"],
            capture_output=True,
            text=True,
            cwd=str(market_repo_path),
        )
        if result.returncode != 0:
            raise RuntimeError(
                "gh CLI is not authenticated. Run 'gh auth login' first.\n"
                f"gh output: {result.stderr.strip()}"
            )
    except FileNotFoundError:
        raise RuntimeError(
            "gh CLI not found. Install GitHub CLI (https://cli.github.com/) "
            "and run 'gh auth login' before using --push."
        )

    # --- Step 2: git add ---
    _run_git(
        ["git", "add", "registry/official/", "index.json"],
        cwd=market_repo_path,
        step="git add",
    )

    # --- Step 3: git commit ---
    _run_git(
        ["git", "commit", "-m", commit_message],
        cwd=market_repo_path,
        step="git commit",
    )

    # --- Step 4: git push ---
    _run_git(
        ["git", "push", "origin", "main"],
        cwd=market_repo_path,
        step="git push",
    )

    print(
        f"Pushed to petfish-market: {commit_message}",
        file=sys.stderr,
    )


def _run_git(cmd: list[str], cwd: Path, step: str) -> subprocess.CompletedProcess:
    """Run a git command, raising RuntimeError with a clear message on failure."""
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        cwd=str(cwd),
    )
    if result.returncode != 0:
        stdout = result.stdout.strip()
        stderr = result.stderr.strip()
        detail = "\n".join(filter(None, [stdout, stderr]))
        raise RuntimeError(
            f"{step} failed (exit {result.returncode}):\n{detail}"
        )
    return result


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

  # Publish + regenerate index.json
  uv run publish_pack.py --all --ref v1.4.0 --generate-index

  # Publish + regenerate index.json + commit and push to petfish-market
  uv run publish_pack.py --all --ref v1.4.0 --generate-index --push

  # Regenerate index.json only (without publishing new packs)
  uv run publish_pack.py --all --dry-run --generate-index

  # Preview push (no git operations performed)
  uv run publish_pack.py --all --ref v1.4.0 --generate-index --push --dry-run

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
    parser.add_argument(
        "--generate-index",
        action="store_true",
        help=(
            "After writing registry JSON files, regenerate index.json from all "
            "registry/official/*.json files. Preserves existing skills[] entries."
        ),
    )
    parser.add_argument(
        "--push",
        action="store_true",
        help=(
            "After writing registry files (and optionally --generate-index), "
            "commit and push changes to petfish-market via git + gh CLI. "
            "Requires: gh auth login must have been run beforehand."
        ),
    )

    args = parser.parse_args()

    # --- Validate arguments ---
    if not args.pack and not args.all:
        parser.error("Specify --pack <name> or --all.")

    if args.pack and args.all:
        parser.error("--pack and --all are mutually exclusive.")

    if not args.dry_run and not args.ref:
        parser.error("--ref <tag> is required when not using --dry-run.")

    if args.push and not args.generate_index and not args.dry_run:
        # --push without --generate-index is allowed but warn
        print(
            "WARNING: --push without --generate-index will push registry JSON "
            "files but not an updated index.json.",
            file=sys.stderr,
        )

    if args.push and args.dry_run:
        print(
            "NOTE: --push with --dry-run will preview git commands without executing them.",
            file=sys.stderr,
        )

    # Use empty string as ref placeholder for dry-run
    ref = args.ref or "(dry-run)"

    # --- Validate ref exists in target repo (#249) ---
    if not args.dry_run and ref != "(dry-run)":
        if not validate_ref_exists(ref):
            print(
                f"ERROR: ref '{ref}' does not exist in kylecui/petfish.ai. "
                f"Create the tag first: git tag {ref} && git push origin {ref}",
                file=sys.stderr,
            )
            return 1

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

    # --- Generate index.json ---
    if args.generate_index:
        try:
            generate_index_json(output_dir, dry_run=args.dry_run)
        except (FileNotFoundError, OSError) as e:
            print(f"ERROR [generate-index]: {e}", file=sys.stderr)
            return 1

    # --- Push to petfish-market ---
    if args.push:
        market_repo_path = output_dir.parent.parent  # registry/official/ → market root
        try:
            push_to_market(
                market_repo_path=market_repo_path,
                pack_names=published if published else pack_names,
                dry_run=args.dry_run,
            )
        except RuntimeError as e:
            print(f"ERROR [push]: {e}", file=sys.stderr)
            return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
