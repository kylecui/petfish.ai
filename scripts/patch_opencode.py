#!/usr/bin/env python3
"""Check OpenCode lastUserMessage support and optionally apply a patched binary.

Background (#163):
  OpenCode's experimental.chat.system.transform hook only receives
  {sessionID, model} -- the user's message text is not exposed, preventing
  real-time topic detection. A 2-file patch (plugin types + request.ts)
  adds lastUserMessage to the hook input.

  Upstream PR: https://github.com/anomalyco/opencode/pull/28993

Default behavior (--check):
  Reports whether the installed OpenCode binary supports lastUserMessage.
  No files are modified. This is the safe, recommended mode.

Disk mode (the default) works without any patch -- it reads topic state
from the previous turn with a one-turn delay. Realtime mode requires
lastUserMessage support, which is not yet in stock OpenCode.

If you need realtime detection *now*, you have two options:
  1. Wait for the upstream PR to be merged (recommended)
  2. Build or download a patched binary (advanced, see --apply-unsigned-binary)

Usage:
  uv run scripts/patch_opencode.py                  # check status (default)
  uv run scripts/patch_opencode.py --check           # same as default
  uv run scripts/patch_opencode.py --restore         # restore original binary
  uv run scripts/patch_opencode.py --apply-unsigned-binary  # replace binary (DANGEROUS)

WARNING: --apply-unsigned-binary downloads an unsigned binary from a
personal GitHub fork and replaces your system OpenCode installation.
There is NO code signing, NO attestation, and NO chain of custody.
This binary will be overwritten on the next OpenCode upgrade.
Use at your own risk. The recommended path is to wait for upstream merge.
"""

from __future__ import annotations

import argparse
import json
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Optional

# Fork release URL pattern
FORK_REPO = "kylecui/opencode"
FORK_BRANCH = "feat/system-transform-lastUserMessage"
FORK_RELEASE_URL = f"https://github.com/{FORK_REPO}/releases"
UPSTREAM_PR_URL = "https://github.com/anomalyco/opencode/pull/28993"
UPSTREAM_ISSUE_URL = "https://github.com/anomalyco/opencode/issues/28992"

# State file location (relative to project root)
PATCH_STATE_FILENAME = "opencode-patch-state.json"


def get_system_id() -> str:
    """Return platform identifier for binary selection."""
    s = platform.system().lower()
    m = platform.machine().lower()
    if s == "darwin":
        arch = "arm64" if m == "arm64" else "x64"
        return f"macos-{arch}"
    elif s == "linux":
        return f"linux-x64"
    elif s == "windows":
        return "windows-x64"
    return f"{s}-{m}"


def find_opencode_binary() -> Optional[Path]:
    """Locate the installed OpenCode binary."""
    # Method 1: which/where
    try:
        result = subprocess.run(
            ["which", "opencode"] if platform.system() != "Windows" else ["where", "opencode"],
            capture_output=True, text=True, timeout=5,
        )
        if result.returncode == 0 and result.stdout.strip():
            return Path(result.stdout.strip().split("\n")[0])
    except Exception:
        pass

    # Method 2: common installation directories
    home = Path.home()
    candidates = []

    if platform.system() == "Windows":
        candidates.extend([
            Path(r"C:\ProgramData\chocolatey\bin\opencode.exe"),
            Path(os.environ.get("SCOOP", r"C:\Users\{}\scoop".format(os.environ.get("USERNAME", "")))) / "shims" / "opencode.exe",
            home / ".opencode" / "bin" / "opencode.exe",
        ])
    elif platform.system() == "Darwin":
        candidates.extend([
            home / ".opencode" / "bin" / "opencode",
            Path("/usr/local/bin/opencode"),
            Path("/opt/homebrew/bin/opencode"),
        ])
    else:  # Linux
        candidates.extend([
            home / ".opencode" / "bin" / "opencode",
            Path("/usr/local/bin/opencode"),
            home / ".local" / "bin" / "opencode",
        ])

    for candidate in candidates:
        if candidate.exists() and candidate.is_file():
            return candidate

    return None


def get_opencode_version(binary_path: Path) -> str:
    """Get the installed OpenCode version."""
    try:
        result = subprocess.run(
            [str(binary_path), "--version"],
            capture_output=True, text=True, timeout=10,
        )
        ver = result.stdout.strip() or result.stderr.strip()
        return ver or "unknown"
    except Exception:
        return "unknown"


def check_binary_has_patch(binary_path: Path) -> bool:
    """Check if the binary already contains the lastUserMessage patch.

    Searches for the string pattern that indicates the patched trigger call.
    """
    try:
        data = binary_path.read_bytes()
        # In patched builds, the trigger call includes lastUserMessage
        return b"lastUserMessage" in data and b"experimental.chat.system.transform" in data
    except Exception:
        return False


def find_fish_trail_dir() -> Optional[Path]:
    """Find the .petfish/fish-trail directory."""
    cwd = Path.cwd()
    for _ in range(5):
        candidate = cwd / ".petfish" / "fish-trail"
        if candidate.exists():
            return candidate
        parent = cwd.parent
        if parent == cwd:
            break
        cwd = parent

    default = Path.cwd() / ".petfish" / "fish-trail"
    default.mkdir(parents=True, exist_ok=True)
    return default


def read_patch_state(fish_trail_dir: Path) -> Optional[dict]:
    """Read patch state from disk."""
    state_file = fish_trail_dir / PATCH_STATE_FILENAME
    if state_file.exists():
        try:
            return json.loads(state_file.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            pass
    return None


def write_patch_state(fish_trail_dir: Path, state: dict) -> None:
    """Write patch state to disk."""
    state_file = fish_trail_dir / PATCH_STATE_FILENAME
    state_file.parent.mkdir(parents=True, exist_ok=True)
    state_file.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")


def download_patched_binary(version: str, system_id: str, target: Path) -> bool:
    """Attempt to download a pre-built patched binary from fork releases.

    Returns True if download was successful.
    """
    import urllib.request
    import urllib.error

    ext = ".exe" if platform.system() == "Windows" else ""
    asset_name = f"opencode-{system_id}{ext}"

    api_url = f"https://api.github.com/repos/{FORK_REPO}/releases/latest"
    try:
        req = urllib.request.Request(api_url, headers={"Accept": "application/vnd.github+json"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            release = json.loads(resp.read().decode("utf-8"))
    except (urllib.error.HTTPError, urllib.error.URLError) as e:
        print(f"  No pre-built patched binary available: {e}")
        print(f"  Check {FORK_RELEASE_URL} for available releases.")
        return False

    assets = release.get("assets", [])
    download_url = None
    for asset in assets:
        if asset.get("name", "").startswith("opencode-") and system_id in asset.get("name", ""):
            download_url = asset.get("browser_download_url")
            break

    if not download_url:
        print(f"  No matching asset for {asset_name} in release {release.get('tag_name', '?')}")
        print(f"  Available assets: {[a.get('name') for a in assets]}")
        return False

    print(f"  Downloading patched binary from {download_url}...")
    try:
        tmp_path = target.with_suffix(".tmp")
        urllib.request.urlretrieve(download_url, str(tmp_path))
        if platform.system() != "Windows":
            os.chmod(str(tmp_path), 0o755)
        tmp_path.rename(target)
        print(f"  Downloaded to {target}")
        return True
    except Exception as e:
        print(f"  Download failed: {e}")
        if tmp_path.exists():
            tmp_path.unlink()
        return False


def print_build_instructions() -> None:
    """Print instructions for building from source."""
    print()
    print("  === Build from source (advanced) ===")
    print()
    print("  If you need realtime detection before upstream merges the PR,")
    print("  you can build a patched OpenCode from source:")
    print()
    print(f"  1. git clone https://github.com/{FORK_REPO}.git")
    print(f"  2. cd opencode && git checkout {FORK_BRANCH}")
    print("  3. Install Bun: https://bun.sh")
    print("  4. bun install && bun run build")
    print("  5. Copy the built binary to your OpenCode installation path")
    print()
    print("  WARNING: This binary is unsigned and will be overwritten")
    print("  on the next OpenCode upgrade.")
    print()
    print(f"  Upstream PR (recommended): {UPSTREAM_PR_URL}")
    print(f"  Upstream issue: {UPSTREAM_ISSUE_URL}")


def do_check(binary_path: Optional[Path]) -> int:
    """Check mode: report current status without making changes."""
    print("=== OpenCode lastUserMessage Support ===")
    print()

    if not binary_path:
        print("  OpenCode binary: NOT FOUND")
        print("  Install OpenCode first: https://opencode.ai")
        return 1

    print(f"  Binary: {binary_path}")
    version = get_opencode_version(binary_path)
    print(f"  Version: {version}")

    has_patch = check_binary_has_patch(binary_path)
    print(f"  lastUserMessage supported: {'YES' if has_patch else 'NO'}")

    system_id = get_system_id()
    print(f"  Platform: {system_id}")

    fish_trail_dir = find_fish_trail_dir()
    if fish_trail_dir:
        state = read_patch_state(fish_trail_dir)
        if state:
            print(f"  Last checked: v{state.get('opencodeVersion', '?')}, "
                  f"lastUserMessage={'available' if state.get('lastUserMessageAvailable') else 'absent'}")
            if state.get("patchedBinaryVersion"):
                print(f"  Patched binary version: {state['patchedBinaryVersion']}")

    print()
    if has_patch:
        print("  Status: Realtime topic detection available.")
    else:
        print("  Status: Disk-mode only (one-turn delay). This is the expected default.")
        print()
        print("  PEtFiSh topic detection works in disk mode without any patch.")
        print("  Realtime mode requires OpenCode to pass lastUserMessage to the")
        print("  system.transform hook, which is not yet in stock OpenCode.")
        print()
        print(f"  Upstream PR: {UPSTREAM_PR_URL}")
        print(f"  Upstream issue: {UPSTREAM_ISSUE_URL}")
        print()
        print("  To apply an unsigned patched binary (NOT recommended):")
        print("    uv run scripts/patch_opencode.py --apply-unsigned-binary")
        print()
        print("  Or build from source (advanced):")
        print("    uv run scripts/patch_opencode.py --build-instructions")

    return 0


def do_apply(unsigned: bool, force: bool) -> int:
    """Apply the patch by downloading and replacing the binary."""
    if not unsigned:
        print("ERROR: Binary replacement requires --apply-unsigned-binary flag.")
        print()
        print("WARNING: This downloads an UNSIGNED binary from a personal GitHub fork")
        print("and replaces your system OpenCode installation. There is NO code signing,")
        print("NO attestation, and NO chain of custody. The binary will be overwritten")
        print("on the next OpenCode upgrade.")
        print()
        print("The recommended path is to wait for the upstream PR to be merged:")
        print(f"  {UPSTREAM_PR_URL}")
        print()
        print("If you understand the risks, re-run with --apply-unsigned-binary.")
        return 1

    binary_path = find_opencode_binary()
    if not binary_path:
        print("ERROR: OpenCode binary not found. Install OpenCode first.")
        return 1

    version = get_opencode_version(binary_path)
    has_patch = check_binary_has_patch(binary_path)
    fish_trail_dir = find_fish_trail_dir()

    print(f"OpenCode binary: {binary_path}")
    print(f"Version: {version}")
    print(f"Already patched: {has_patch}")
    print()

    if has_patch and not force:
        print("Already patched. Use --force with --apply-unsigned-binary to re-apply.")
        write_patch_state(fish_trail_dir, {
            "opencodeVersion": version,
            "lastUserMessageAvailable": True,
            "lastChecked": _now_iso(),
            "patchedBinaryVersion": version,
        })
        return 0

    # Explicit risk acknowledgment
    print("!!! WARNING !!!")
    print("You are about to replace your OpenCode binary with an UNSIGNED build")
    print("from a personal GitHub fork. This binary:")
    print("  - Has NO code signing or attestation")
    print("  - Will be OVERWRITTEN on the next OpenCode upgrade")
    print("  - May not match your current OpenCode version")
    print("  - Could introduce security risks")
    print()
    print(f"Upstream PR (recommended alternative): {UPSTREAM_PR_URL}")
    print()

    system_id = get_system_id()
    print(f"Platform: {system_id}")
    print(f"Looking for patched binary at {FORK_RELEASE_URL}...")

    # Backup original
    backup_path = binary_path.with_suffix(binary_path.suffix + ".petfish-bak")
    if not backup_path.exists():
        print(f"  Backing up original to {backup_path}...")
        shutil.copy2(str(binary_path), str(backup_path))
    else:
        print(f"  Backup already exists: {backup_path}")

    success = download_patched_binary(version, system_id, binary_path)
    if not success:
        print()
        print("Pre-built binary not available for your platform/version.")
        print_build_instructions()

        write_patch_state(fish_trail_dir, {
            "opencodeVersion": version,
            "lastUserMessageAvailable": False,
            "lastChecked": _now_iso(),
        })
        return 1

    write_patch_state(fish_trail_dir, {
        "opencodeVersion": version,
        "lastUserMessageAvailable": True,
        "lastChecked": _now_iso(),
        "patchedBinaryVersion": version,
    })
    print()
    print("Patch applied. Restart OpenCode to use realtime detection.")
    print("NOTE: This will be overwritten on the next OpenCode upgrade.")
    return 0


def do_restore(binary_path: Optional[Path]) -> int:
    """Restore the original binary from backup."""
    if not binary_path:
        print("ERROR: OpenCode binary not found.")
        return 1

    backup_path = binary_path.with_suffix(binary_path.suffix + ".petfish-bak")
    if not backup_path.exists():
        print(f"No backup found at {backup_path}")
        return 1

    print(f"Restoring original binary from {backup_path}...")
    shutil.copy2(str(backup_path), str(binary_path))
    print("Restored. You may delete the backup file manually.")

    fish_trail_dir = find_fish_trail_dir()
    if fish_trail_dir:
        write_patch_state(fish_trail_dir, {
            "opencodeVersion": get_opencode_version(binary_path),
            "lastUserMessageAvailable": False,
            "lastChecked": _now_iso(),
        })

    return 0


def _now_iso() -> str:
    """Return current ISO timestamp."""
    from datetime import datetime
    return datetime.now().isoformat()


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check OpenCode lastUserMessage support and optionally apply a patched binary",
    )
    parser.add_argument("--check", action="store_true",
                        help="Only check status, do not modify (default behavior)")
    parser.add_argument("--apply-unsigned-binary", action="store_true",
                        help="Replace OpenCode binary with unsigned patched build (DANGEROUS)")
    parser.add_argument("--restore", action="store_true",
                        help="Restore original binary from backup")
    parser.add_argument("--force", action="store_true",
                        help="Re-apply patch even if already patched (use with --apply-unsigned-binary)")
    parser.add_argument("--build-instructions", action="store_true",
                        help="Print instructions for building from source")
    args = parser.parse_args()

    binary_path = find_opencode_binary()

    if args.build_instructions:
        print_build_instructions()
        return 0
    elif args.restore:
        return do_restore(binary_path)
    elif args.apply_unsigned_binary:
        return do_apply(unsigned=True, force=args.force)
    else:
        # Default: check only
        return do_check(binary_path)


if __name__ == "__main__":
    sys.exit(main())
