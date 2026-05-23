#!/usr/bin/env python3
"""Auto-patch OpenCode to pass lastUserMessage to system.transform hook.

Background (#163):
  OpenCode's experimental.chat.system.transform hook only receives
  {sessionID, model} — the user's message text is not exposed, preventing
  real-time topic detection. A 2-file patch (plugin types + request.ts)
  adds lastUserMessage to the hook input.

  Upstream PR: https://github.com/anomalyco/opencode/pull/28993
  Fork: https://github.com/kylecui/opencode/tree/feat/system-transform-lastUserMessage

This script:
  1. Detects the installed OpenCode binary and its version
  2. Checks if lastUserMessage is already supported (future upstream merge)
  3. If not supported, downloads a pre-built patched binary from our fork
  4. Backs up the original and replaces with the patched version
  5. Updates .petfish/fish-trail/opencode-patch-state.json

Usage:
  uv run scripts/patch_opencode.py [--check] [--restore] [--force]

Options:
  --check    Only check status, do not download or replace
  --restore  Restore the original binary from backup
  --force    Re-apply patch even if already patched

Platform support:
  - Windows (chocolatey, scoop, curl install)
  - macOS (brew, curl install)
  - Linux (brew, curl install, pacman)

NOTE: Pre-built patched binaries are provided on the fork's GitHub Releases.
If no release matches your platform/version, the script will print
instructions for building from source.
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
        # Read binary and search for the patched pattern
        # In patched builds, the trigger call includes lastUserMessage
        data = binary_path.read_bytes()
        # Look for the patched pattern: lastUserMessage in the system.transform context
        return b"lastUserMessage" in data and b"experimental.chat.system.transform" in data
    except Exception:
        return False


def find_fish_trail_dir() -> Optional[Path]:
    """Find the .petfish/fish-trail directory."""
    # Check current directory first, then parent directories
    cwd = Path.cwd()
    for _ in range(5):
        candidate = cwd / ".petfish" / "fish-trail"
        if candidate.exists():
            return candidate
        parent = cwd.parent
        if parent == cwd:
            break
        cwd = parent

    # Default: create in current directory
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

    # Try to find a matching release asset
    # Pattern: opencode-{system_id} (no extension on Unix, .exe on Windows)
    ext = ".exe" if platform.system() == "Windows" else ""
    asset_name = f"opencode-{system_id}{ext}"

    # Query GitHub API for latest release on the fork
    api_url = f"https://api.github.com/repos/{FORK_REPO}/releases/latest"
    try:
        req = urllib.request.Request(api_url, headers={"Accept": "application/vnd.github+json"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            release = json.loads(resp.read().decode("utf-8"))
    except (urllib.error.HTTPError, urllib.error.URLError) as e:
        print(f"  No pre-built patched binary available: {e}")
        print(f"  Check {FORK_RELEASE_URL} for available releases.")
        return False

    # Find matching asset
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

    # Download with progress
    print(f"  Downloading patched binary from {download_url}...")
    try:
        tmp_path = target.with_suffix(".tmp")
        urllib.request.urlretrieve(download_url, str(tmp_path))
        # Make executable on Unix
        if platform.system() != "Windows":
            os.chmod(str(tmp_path), 0o755)
        # Replace target
        tmp_path.rename(target)
        print(f"  Downloaded to {target}")
        return True
    except Exception as e:
        print(f"  Download failed: {e}")
        if tmp_path.exists():
            tmp_path.unlink()
        return False


def build_from_source(fish_trail_dir: Path) -> bool:
    """Print instructions for building from source."""
    print()
    print("  To build a patched OpenCode from source:")
    print(f"  1. git clone https://github.com/{FORK_REPO}.git")
    print(f"  2. cd opencode && git checkout {FORK_BRANCH}")
    print("  3. Install Bun: https://bun.sh")
    print("  4. bun install && bun run build")
    print("  5. Copy the built binary to your OpenCode installation path")
    print()
    print(f"  Or wait for upstream PR: {UPSTREAM_PR_URL}")
    return False


def do_check(binary_path: Optional[Path]) -> int:
    """Check mode: report current status without making changes."""
    print("=== OpenCode Patch Status ===")
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
            print(f"  Previous patch state: v{state.get('opencodeVersion', '?')}, "
                  f"lastUserMessage={'available' if state.get('lastUserMessageAvailable') else 'not available'}")
            if state.get("patchedBinaryVersion"):
                print(f"  Patched binary version: {state['patchedBinaryVersion']}")

    print()
    if has_patch:
        print("  Status: Patched — realtime topic detection available.")
    else:
        print("  Status: Stock — disk-mode only (one-turn delay).")
        print(f"  To enable realtime: uv run scripts/patch_opencode.py")
        print(f"  Upstream PR: {UPSTREAM_PR_URL}")

    return 0


def do_patch(binary_path: Optional[Path], force: bool) -> int:
    """Apply the patch by downloading and replacing the binary."""
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
        print("Already patched. Use --force to re-apply.")
        # Update state
        write_patch_state(fish_trail_dir, {
            "opencodeVersion": version,
            "lastUserMessageAvailable": True,
            "lastChecked": _now_iso(),
            "patchedBinaryVersion": version,
        })
        return 0

    # Try to download pre-built binary
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
        print("Pre-built binary not available. Falling back to source build instructions.")
        build_from_source(fish_trail_dir)

        # Update state to indicate we attempted but failed
        write_patch_state(fish_trail_dir, {
            "opencodeVersion": version,
            "lastUserMessageAvailable": False,
            "lastChecked": _now_iso(),
        })
        return 1

    # Update state
    write_patch_state(fish_trail_dir, {
        "opencodeVersion": version,
        "lastUserMessageAvailable": True,
        "lastChecked": _now_iso(),
        "patchedBinaryVersion": version,
    })
    print()
    print("Patch applied successfully. Restart OpenCode to use realtime detection.")
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

    # Update state
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
        description="Auto-patch OpenCode to enable lastUserMessage in system.transform hook",
    )
    parser.add_argument("--check", action="store_true", help="Only check status, do not modify")
    parser.add_argument("--restore", action="store_true", help="Restore original binary from backup")
    parser.add_argument("--force", action="store_true", help="Re-apply patch even if already patched")
    args = parser.parse_args()

    binary_path = find_opencode_binary()

    if args.check:
        return do_check(binary_path)
    elif args.restore:
        return do_restore(binary_path)
    else:
        return do_patch(binary_path, args.force)


if __name__ == "__main__":
    sys.exit(main())
