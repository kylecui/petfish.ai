#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# ///
#
# PEtFiSh Unified Python Installer
# Replaces install.sh, install.ps1, remote-install.sh, remote-install.ps1
#
# Usage:
#   uv run install.py --pack course --target .
#   uv run install.py --pack all --detect
#   uv run install.py --list
#   uv run install.py --pack init --global --force
#

import argparse
import json
import os
import platform
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

# ---------------------------------------------------------------------------
# UTF-8 setup
# ---------------------------------------------------------------------------
if sys.stdout:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
if sys.stderr:
    try:
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass
os.environ.setdefault("PYTHONIOENCODING", "utf-8")

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
SCRIPT_ROOT = Path(__file__).resolve().parent

ALIASES: dict[str, str] = {
    "course": "opencode-course-skills-pack",
    "testdocs": "opencode-skill-pack-testcases-usage-docs",
    "deploy": "repo-deploy-ops-skill-pack",
    "petfish": "petfish-style-skill",
    "companion": "petfish-companion-skill",
    "ppt": "opencode-ppt-skills",
    "init": "project-initializer-skill",
    "trust": "trustskills-governance-pack",
    "fish-guard": "trustskills-governance-pack",
    "calibrate": "judgment-calibration-pack",
    "context": "fish-trail",
    "research": "research-skill-pack",
    "reflect": "fish-reflection-pack",
    "fish-init": "project-initializer-skill",
    "fish-core": "petfish-companion-skill",
    "fish-course": "opencode-course-skills-pack",
    "fish-testdocs": "opencode-skill-pack-testcases-usage-docs",
    "fish-deploy": "repo-deploy-ops-skill-pack",
    "fish-style": "petfish-style-skill",
    "fish-slides": "opencode-ppt-skills",
    "fish-calibrate": "judgment-calibration-pack",
    "council-thinking": "judgment-calibration-pack",
    "fish-trail": "fish-trail",
    "fish-research": "research-skill-pack",
    "fish-reflect": "fish-reflection-pack",
    "fish-brain": "petfish-companion-skill",
    "toolchain": "petfish-toolchain-skill",
    "series-style": "series-style-governor-pack",
    "doc-reader": "doc-reader-skill",
}

CORE_PACKS = {
    "project-initializer-skill",
    "petfish-companion-skill",
    "petfish-toolchain-skill",
    "fish-trail",
}

CORE_ALIASES = {"init", "companion", "toolchain", "fish-trail"}

# ---------------------------------------------------------------------------
# Phase 3: Distribution constants
# ---------------------------------------------------------------------------
MARKET_INDEX_URL = (
    "https://raw.githubusercontent.com/kylecui/petfish-market/main/index.json"
)
MIRROR_PREFIXES = [
    "",
    "https://ghfast.top/https://",
    "https://mirror.ghproxy.com/https://",
]
REPO_TARBALL_URL = "https://github.com/{owner}/{repo}/tarball/{ref}"
REPO_ARCHIVE_URL = (
    "https://github.com/{owner}/{repo}/archive/refs/heads/{ref}.tar.gz"
)

# Module-level staging state for market/community downloads
_market_meta: dict[str, dict] = {}  # pack_name → market metadata dict
_market_pack_dirs: dict[str, Path] = {}  # pack_name → extracted staging Path
_community_staging_dir: tempfile.TemporaryDirectory | None = None
_market_staging_dir: tempfile.TemporaryDirectory | None = None
_core_repo_staging_dir: tempfile.TemporaryDirectory | None = None
_core_repo_extracted: Path | None = None  # cached extraction root


def _get_community_staging() -> Path:
    """Return (creating if needed) the community staging directory."""
    global _community_staging_dir
    if _community_staging_dir is None:
        _community_staging_dir = tempfile.TemporaryDirectory(prefix="petfish-community-")
    return Path(_community_staging_dir.name)


def _get_market_staging() -> Path:
    """Return (creating if needed) the market staging directory."""
    global _market_staging_dir
    if _market_staging_dir is None:
        _market_staging_dir = tempfile.TemporaryDirectory(prefix="petfish-market-")
    return Path(_market_staging_dir.name)


def _cleanup_staging():
    """Clean up all staging temp directories."""
    global _community_staging_dir, _market_staging_dir, _core_repo_staging_dir
    if _community_staging_dir is not None:
        try:
            _community_staging_dir.cleanup()
        except Exception:
            pass
        _community_staging_dir = None
    if _market_staging_dir is not None:
        try:
            _market_staging_dir.cleanup()
        except Exception:
            pass
        _market_staging_dir = None
    if _core_repo_staging_dir is not None:
        try:
            _core_repo_staging_dir.cleanup()
        except Exception:
            pass
        _core_repo_staging_dir = None


def _ensure_core_repo_extracted(github_token: str | None = None) -> Path | None:
    """Download and extract the kylecui/petfish.ai repo once.
    Returns the root of the extracted repo (containing packs/core/ etc.),
    or None on failure. Cached for the lifetime of the process."""
    global _core_repo_staging_dir, _core_repo_extracted
    if _core_repo_extracted is not None and _core_repo_extracted.is_dir():
        return _core_repo_extracted

    _core_repo_staging_dir = tempfile.TemporaryDirectory(prefix="petfish-core-")
    staging = Path(_core_repo_staging_dir.name)
    tarball_url = REPO_ARCHIVE_URL.format(
        owner="kylecui", repo="petfish.ai", ref="master"
    )
    log("[core] Downloading petfish.ai repo for core packs...")

    dl_ok = False
    if download_tarball(tarball_url, staging, github_token=github_token):
        # Find the extracted directory (GitHub tarballs extract to owner-repo-ref/)
        for child in staging.iterdir():
            if child.is_dir() and child.name != "archive.tar.gz":
                _core_repo_extracted = child
                dl_ok = True
                break

    if not dl_ok:
        # Fall back to git clone
        log("[core] Tarball download failed, falling back to git clone...")
        clone_dest = staging / "petfish-ai-clone"
        clone_url = "https://github.com/kylecui/petfish.ai.git"
        if download_git_clone(clone_url, clone_dest, ref="master", github_token=github_token):
            _core_repo_extracted = clone_dest
            dl_ok = True

    if not dl_ok:
        log_warn("[core] Failed to download petfish.ai repo for core packs")
        _core_repo_staging_dir.cleanup()
        _core_repo_staging_dir = None
        return None

    return _core_repo_extracted


def find_core_pack_remote(
    pack_name: str, github_token: str | None = None
) -> Path | None:
    """Find a core pack by downloading the petfish.ai repo.
    Returns the pack directory path or None."""
    repo_root = _ensure_core_repo_extracted(github_token=github_token)
    if repo_root is None:
        return None
    for subdir in ("core", "optional"):
        candidate = repo_root / "packs" / subdir / pack_name
        if candidate.is_dir():
            return candidate
    return None
HARDCODED_PLATFORMS: dict = {
    "platforms": {
        "opencode": {
            "display_name": "OpenCode",
            "project": {
                "skills_dir": ".opencode/skills",
                "commands_dir": ".opencode/commands",
                "agents_dir": ".opencode/agents",
                "config_file": "opencode.json",
                "instructions_file": "AGENTS.md",
                "rules_dir": None,
            },
            "global": {
                "skills_dir": "~/.config/opencode/skills",
                "commands_dir": "~/.config/opencode/commands",
                "agents_dir": None,
                "config_file": None,
                "instructions_file": None,
            },
            "skill_format": "SKILL.md",
            "detect_markers": [".opencode", "opencode.json"],
            "instructions_merge_strategy": "marker_based",
            "notes": "Primary development platform for PEtFiSh.",
        },
        "claude": {
            "display_name": "Claude Code",
            "project": {
                "skills_dir": ".claude/skills",
                "commands_dir": ".claude/commands",
                "agents_dir": ".claude/agents",
                "config_file": ".claude/settings.json",
                "instructions_file": "CLAUDE.md",
                "rules_dir": ".claude/rules",
            },
            "global": {
                "skills_dir": "~/.claude/skills",
                "commands_dir": "~/.claude/commands",
                "agents_dir": "~/.claude/agents",
                "config_file": "~/.claude/settings.json",
                "instructions_file": "~/.claude/CLAUDE.md",
            },
            "skill_format": "SKILL.md",
            "detect_markers": [".claude", "CLAUDE.md"],
            "instructions_merge_strategy": "marker_based",
            "instructions_translation": {
                "source": "AGENTS.md",
                "target": "CLAUDE.md",
                "method": "rename_with_header",
            },
            "notes": "SKILL.md format is fully compatible with OpenCode.",
        },
        "codex": {
            "display_name": "Codex",
            "project": {
                "skills_dir": ".agents/skills",
                "commands_dir": None,
                "agents_dir": ".codex/agents",
                "config_file": ".codex/config.toml",
                "instructions_file": "AGENTS.md",
                "rules_dir": None,
            },
            "global": {
                "skills_dir": "~/.agents/skills",
                "commands_dir": None,
                "agents_dir": "~/.codex/agents",
                "config_file": "~/.codex/config.toml",
                "instructions_file": "~/.codex/AGENTS.md",
            },
            "skill_format": "SKILL.md",
            "detect_markers": [".codex"],
            "instructions_merge_strategy": "marker_based",
            "notes": "Uses AGENTS.md natively.",
        },
        "cursor": {
            "display_name": "Cursor",
            "project": {
                "skills_dir": ".cursor/skills",
                "commands_dir": None,
                "agents_dir": None,
                "config_file": None,
                "instructions_file": None,
                "rules_dir": ".cursor/rules",
            },
            "global": {
                "skills_dir": None,
                "commands_dir": None,
                "agents_dir": None,
                "config_file": None,
                "instructions_file": None,
            },
            "skill_format": "SKILL.md",
            "detect_markers": [".cursor", ".cursorrules"],
            "instructions_merge_strategy": "mdc_rules",
            "instructions_translation": {
                "source": "AGENTS.md",
                "target": ".cursor/rules/petfish-agents.mdc",
                "method": "wrap_as_mdc",
            },
            "condense": {"max_tokens": 8000},
            "notes": "Supports SKILL.md natively.",
        },
        "copilot": {
            "display_name": "GitHub Copilot",
            "project": {
                "skills_dir": ".github/skills",
                "commands_dir": None,
                "agents_dir": None,
                "config_file": None,
                "instructions_file": ".github/copilot-instructions.md",
                "rules_dir": ".github/instructions",
            },
            "global": {
                "skills_dir": None,
                "commands_dir": None,
                "agents_dir": None,
                "config_file": None,
                "instructions_file": None,
            },
            "skill_format": "SKILL.md",
            "detect_markers": [".github/copilot-instructions.md", ".github/skills"],
            "instructions_merge_strategy": "marker_based",
            "instructions_translation": {
                "source": "AGENTS.md",
                "target": ".github/copilot-instructions.md",
                "method": "rename_with_header",
            },
            "notes": "Supports SKILL.md under .github/skills/.",
        },
        "windsurf": {
            "display_name": "Windsurf",
            "project": {
                "skills_dir": ".windsurf/skills",
                "commands_dir": None,
                "agents_dir": None,
                "config_file": None,
                "instructions_file": ".windsurfrules",
                "rules_dir": ".windsurf/rules",
            },
            "global": {
                "skills_dir": None,
                "commands_dir": None,
                "agents_dir": None,
                "config_file": "~/.codeium/windsurf/config.json",
                "instructions_file": "~/.codeium/windsurf/memories/global_rules.md",
            },
            "skill_format": "SKILL.md",
            "detect_markers": [".windsurf", ".windsurfrules"],
            "instructions_merge_strategy": "marker_based",
            "instructions_translation": {
                "source": "AGENTS.md",
                "target": ".windsurfrules",
                "method": "rename_with_header",
            },
            "condense": {"max_tokens": 6000},
            "notes": "Supports SKILL.md under .windsurf/skills/.",
        },
        "antigravity": {
            "display_name": "Antigravity",
            "project": {
                "skills_dir": ".agents/skills",
                "commands_dir": ".agents/workflows",
                "agents_dir": ".agents/rules",
                "config_file": None,
                "instructions_file": "AGENTS.md",
                "rules_dir": None,
            },
            "global": {
                "skills_dir": "~/.gemini/antigravity/skills",
                "commands_dir": "~/.gemini/antigravity/workflows",
                "agents_dir": None,
                "config_file": None,
                "instructions_file": None,
            },
            "skill_format": "SKILL.md",
            "detect_markers": [".agents", "GEMINI.md"],
            "instructions_merge_strategy": "marker_based",
            "notes": "Google Gemini-based platform.",
        },
        "universal": {
            "display_name": "Universal (cross-platform)",
            "project": {
                "skills_dir": ".agents/skills",
                "commands_dir": None,
                "agents_dir": None,
                "config_file": None,
                "instructions_file": "AGENTS.md",
                "rules_dir": None,
            },
            "global": {
                "skills_dir": "~/.agents/skills",
                "commands_dir": None,
                "agents_dir": None,
                "config_file": None,
                "instructions_file": None,
            },
            "skill_format": "SKILL.md",
            "detect_markers": [],
            "instructions_merge_strategy": "marker_based",
            "notes": "Fallback cross-platform path.",
        },
    },
    "platform_groups": {
        "all": ["opencode", "claude", "codex", "cursor", "copilot", "windsurf", "antigravity"],
        "primary": ["opencode", "claude", "codex"],
        "ide": ["cursor", "copilot", "windsurf"],
        "cli": ["opencode", "claude", "codex", "antigravity"],
    },
}


# ---------------------------------------------------------------------------
# Color output helpers
# ---------------------------------------------------------------------------
def _is_tty():
    """Check if stdout is a TTY."""
    try:
        return hasattr(sys.stdout, "isatty") and sys.stdout.isatty()
    except Exception:
        return False


_TTY = _is_tty()


def _c(code: str, text: str) -> str:
    if _TTY:
        return f"\033[{code}m{text}\033[0m"
    return text


def green(text: str) -> str:
    return _c("32", text)


def yellow(text: str) -> str:
    return _c("33", text)


def red(text: str) -> str:
    return _c("31", text)


def bold(text: str) -> str:
    return _c("1", text)


def log(msg: str):
    """Print to stderr (action log)."""
    print(f"  {msg}", file=sys.stderr)


def log_success(msg: str):
    log(green(f"+ {msg}"))


def log_warn(msg: str):
    log(yellow(f"! {msg}"))


def log_error(msg: str):
    print(f"  {red(f'ERROR: {msg}')}", file=sys.stderr)


def banner(msg: str):
    print(f"[胖鱼 PEtFiSh] {msg}", file=sys.stderr)


# ---------------------------------------------------------------------------
# Platforms data loading
# ---------------------------------------------------------------------------
def load_platforms() -> dict:
    """Load platforms.json, with hardcoded fallback."""
    p = SCRIPT_ROOT / "platforms.json"
    if p.is_file():
        try:
            return json.loads(p.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as exc:
            log_warn(f"Failed to parse platforms.json: {exc}; using hardcoded fallback")
    return HARDCODED_PLATFORMS


# ---------------------------------------------------------------------------
# Platform detection
# ---------------------------------------------------------------------------
def detect_platform(target: Path, platforms_data: dict) -> str:
    """Detect platform from target directory markers. Returns platform name."""
    plats = platforms_data.get("platforms", {})
    for plat_name, plat_info in plats.items():
        markers = plat_info.get("detect_markers", [])
        for marker in markers:
            if (target / marker).exists():
                return plat_name
    return "universal"


def resolve_platform_name(name: str, platforms_data: dict) -> list[str]:
    """Resolve a platform name or group to a list of platform names."""
    groups = platforms_data.get("platform_groups", {})
    if name in groups:
        return groups[name]
    plats = platforms_data.get("platforms", {})
    if name in plats:
        return [name]
    log_error(f"Unknown platform: {name}")
    sys.exit(1)


def get_platform_dirs(
    plat_name: str, platforms_data: dict, use_global: bool, target: Path
) -> dict:
    """Get platform-specific directory mappings (absolute paths)."""
    plats = platforms_data.get("platforms", {})
    plat = plats.get(plat_name)
    if plat is None:
        return {}
    mode = "global" if use_global else "project"
    dirs = plat.get(mode, {})
    resolved = {}
    for key, rel in dirs.items():
        if rel is None:
            resolved[key] = None
        elif rel.startswith("~/"):
            expanded = Path(rel).expanduser()
            resolved[key] = expanded
        else:
            resolved[key] = target / rel
    return resolved


# ---------------------------------------------------------------------------
# Pack resolution
# ---------------------------------------------------------------------------
def resolve_pack_alias(name: str) -> str:
    """Resolve a pack alias to its canonical name."""
    if name in ALIASES:
        return ALIASES[name]
    return name


def is_core_pack(pack_name: str) -> bool:
    """Check if a pack is a core pack."""
    return pack_name in CORE_PACKS


def find_pack_dir(pack_name: str) -> Path | None:
    """Find a pack directory under packs/core/ or packs/optional/."""
    for subdir in ("core", "optional"):
        candidate = SCRIPT_ROOT / "packs" / subdir / pack_name
        if candidate.is_dir():
            return candidate
    return None


def find_all_packs() -> list[str]:
    """Find all available packs in packs/core/ and packs/optional/."""
    packs = []
    for subdir in ("core", "optional"):
        base = SCRIPT_ROOT / "packs" / subdir
        if base.is_dir():
            for child in sorted(base.iterdir()):
                if child.is_dir() and (child / "pack-manifest.json").is_file():
                    packs.append(child.name)
    return packs


# ---------------------------------------------------------------------------
# Phase 3: Network helpers
# ---------------------------------------------------------------------------
def fetch_url_with_mirrors(
    url: str, timeout: int = 30, github_token: str | None = None
) -> bytes | None:
    """Try URL directly, then via mirrors. Return response body bytes."""
    headers: dict[str, str] = {}
    if github_token:
        headers["Authorization"] = f"token {github_token}"

    for prefix in MIRROR_PREFIXES:
        full_url = f"{prefix}{url}"
        try:
            req = Request(full_url, headers=headers)
            with urlopen(req, timeout=timeout) as resp:
                return resp.read()
        except (URLError, HTTPError, OSError):
            continue
    return None


# ---------------------------------------------------------------------------
# Phase 3: Market index query
# ---------------------------------------------------------------------------
def query_market_index(
    pack_alias: str, github_token: str | None = None
) -> dict | None:
    """Query petfish-market index.json for optional pack metadata.
    Returns matching pack dict or None."""
    raw = fetch_url_with_mirrors(MARKET_INDEX_URL, timeout=10, github_token=github_token)
    if raw is None:
        return None
    try:
        data = json.loads(raw)
    except (json.JSONDecodeError, ValueError):
        return None

    for pack in data.get("packs", []):
        aliases = pack.get("alias", []) or pack.get("aliases", []) or []
        if isinstance(aliases, str):
            aliases = [aliases]
        if pack_alias in aliases or pack.get("name") == pack_alias:
            return pack
    return None


# ---------------------------------------------------------------------------
# Phase 3: Tarball download with retry
# ---------------------------------------------------------------------------
def download_tarball(
    url: str,
    dest_dir: Path,
    github_token: str | None = None,
    max_retries: int = 3,
) -> bool:
    """Download and extract a GitHub tarball. Returns True on success."""
    import io

    headers: dict[str, str] = {}
    if github_token:
        headers["Authorization"] = f"token {github_token}"

    dest_dir.mkdir(parents=True, exist_ok=True)
    archive_path = dest_dir / "archive.tar.gz"

    for attempt in range(1, max_retries + 1):
        try:
            req = Request(url, headers=headers)
            with urlopen(req, timeout=30) as resp:
                if resp.status == 200:
                    archive_path.write_bytes(resp.read())
                    break
                else:
                    log_warn(f"HTTP {resp.status} downloading tarball")
                    if resp.status in (429, 403) and attempt < max_retries:
                        wait = 2 ** attempt
                        log(f"Rate limited, retrying in {wait}s... (attempt {attempt}/{max_retries})")
                        time.sleep(wait)
                        archive_path.unlink(missing_ok=True)
                        continue
                    return False
        except HTTPError as e:
            if e.code in (429, 403) and attempt < max_retries:
                wait = 2 ** attempt
                log(f"Rate limited (HTTP {e.code}), retrying in {wait}s... (attempt {attempt}/{max_retries})")
                time.sleep(wait)
                archive_path.unlink(missing_ok=True)
                continue
            log_warn(f"HTTP error downloading tarball: {e}")
            return False
        except (URLError, OSError) as e:
            log_warn(f"Network error downloading tarball: {e}")
            return False
    else:
        return False

    # Extract tarball
    if not archive_path.is_file():
        return False
    try:
        with tarfile.open(archive_path, "r:gz") as tf:
            tf.extractall(dest_dir)
        archive_path.unlink(missing_ok=True)
        return True
    except (tarfile.TarError, OSError) as e:
        log_warn(f"Failed to extract tarball: {e}")
        archive_path.unlink(missing_ok=True)
        return False


# ---------------------------------------------------------------------------
# Phase 3: Git clone fallback
# ---------------------------------------------------------------------------
def download_git_clone(
    repo_url: str,
    dest_dir: Path,
    ref: str | None = None,
    github_token: str | None = None,
    max_retries: int = 3,
) -> bool:
    """Fall back to git clone when tarball fails. Returns True on success."""
    # Embed token in URL if provided
    clone_url = repo_url
    if github_token and "github.com" in repo_url:
        clone_url = repo_url.replace("https://", f"https://{github_token}@")

    cmd = ["git", "clone", "--depth", "1"]
    if ref:
        cmd += ["--branch", ref]
    cmd += [clone_url, str(dest_dir)]

    for attempt in range(1, max_retries + 1):
        try:
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=120
            )
            if result.returncode == 0:
                return True
            if attempt < max_retries:
                wait = 2 ** attempt
                log(f"git clone failed, retrying in {wait}s... (attempt {attempt}/{max_retries})")
                time.sleep(wait)
                if dest_dir.is_dir():
                    shutil.rmtree(dest_dir, ignore_errors=True)
        except (subprocess.TimeoutExpired, OSError) as e:
            if attempt < max_retries:
                wait = 2 ** attempt
                log(f"git clone error: {e}, retrying in {wait}s... (attempt {attempt}/{max_retries})")
                time.sleep(wait)
                if dest_dir.is_dir():
                    shutil.rmtree(dest_dir, ignore_errors=True)
            else:
                log_warn(f"git clone failed after {max_retries} attempts: {e}")
                return False
    return False


# ---------------------------------------------------------------------------
# Phase 3: Community pack download
# ---------------------------------------------------------------------------
def _parse_community_spec(spec: str) -> tuple[str, str, str | None]:
    """Parse 'community/owner/repo[/ref]' → (owner, repo, ref|None)."""
    parts = spec.split("/")
    if len(parts) < 3 or parts[0] != "community":
        return ("", "", None)
    owner = parts[1]
    repo = parts[2]
    ref = parts[3] if len(parts) >= 4 else None
    return (owner, repo, ref)


def download_community_pack(
    spec: str, github_token: str | None = None
) -> tuple[str, Path] | None:
    """Download a community skill from GitHub.
    Returns (pack_dir_name, staging_path) or None on failure."""
    owner, repo, ref = _parse_community_spec(spec)
    if not owner or not repo:
        log_error(f"Invalid community pack spec '{spec}'. Expected: community/<owner>/<repo>[/<ref>]")
        return None

    pack_dir_name = f"community--{owner}--{repo}"
    staging = _get_community_staging()
    staged_pack = staging / pack_dir_name

    if staged_pack.is_dir():
        # Already downloaded in this run
        return (pack_dir_name, staged_pack)

    github_ref = ref or "main"
    tarball_url = REPO_ARCHIVE_URL.format(owner=owner, repo=repo, ref=github_ref)
    log(f"[community] Downloading {owner}/{repo} (ref: {github_ref})...")

    dl_tmp = Path(tempfile.mkdtemp(prefix="petfish-dl-"))
    dl_ok = False

    # Try tarball download first
    if download_tarball(tarball_url, dl_tmp, github_token=github_token):
        # Find extracted directory
        extracted = None
        for child in dl_tmp.iterdir():
            if child.is_dir() and child.name != "archive.tar.gz":
                extracted = child
                break
        if extracted:
            shutil.move(str(extracted), str(staged_pack))
            dl_ok = True
        else:
            log_warn("Failed to extract community pack tarball")

    if not dl_ok:
        # Fall back to git clone
        log("[community] Tarball download failed, falling back to git clone...")
        clone_url = f"https://github.com/{owner}/{repo}.git"
        if download_git_clone(clone_url, staged_pack, ref=ref, github_token=github_token):
            dl_ok = True
        else:
            log_error(f"Failed to download community pack {owner}/{repo}")
            shutil.rmtree(dl_tmp, ignore_errors=True)
            return None

    shutil.rmtree(dl_tmp, ignore_errors=True)

    # Validate: must have .opencode/ directory
    if not (staged_pack / ".opencode").is_dir():
        log_error(f"Community pack {owner}/{repo} has no .opencode/ directory. Not a valid skill pack.")
        shutil.rmtree(staged_pack, ignore_errors=True)
        return None

    # Check for at least one of skills/, commands/, agents/
    has_content = (
        (staged_pack / ".opencode" / "skills").is_dir()
        or (staged_pack / ".opencode" / "commands").is_dir()
        or (staged_pack / ".opencode" / "agents").is_dir()
    )
    if not has_content:
        log_error(f"Community pack {owner}/{repo} .opencode/ has no skills/, commands/, or agents/. Not a valid skill pack.")
        shutil.rmtree(staged_pack, ignore_errors=True)
        return None

    # Generate a minimal pack-manifest.json if missing
    manifest_file = staged_pack / "pack-manifest.json"
    if not manifest_file.is_file():
        skills = []
        commands = []
        agents = []
        skills_path = staged_pack / ".opencode" / "skills"
        if skills_path.is_dir():
            skills = sorted(d.name for d in skills_path.iterdir() if d.is_dir())
        commands_path = staged_pack / ".opencode" / "commands"
        if commands_path.is_dir():
            commands = sorted(f.name for f in commands_path.iterdir() if f.is_file())
        agents_path = staged_pack / ".opencode" / "agents"
        if agents_path.is_dir():
            agents = sorted(d.name for d in agents_path.iterdir() if d.is_dir())
        auto_manifest = {
            "name": pack_dir_name,
            "version": "0.0.0",
            "description": f"Community pack from {owner}/{repo}",
            "skills": skills,
            "commands": commands,
            "agents": agents,
            "skill_count": len(skills),
            "command_count": len(commands),
            "agent_count": len(agents),
        }
        manifest_file.write_text(
            json.dumps(auto_manifest, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )

    return (pack_dir_name, staged_pack)


# ---------------------------------------------------------------------------
# Phase 3: Market pack download
# ---------------------------------------------------------------------------
def download_market_pack(
    pack_name: str, github_token: str | None = None
) -> Path | None:
    """Download an optional pack from a market-sourced external repo.
    Returns the extracted root dir or None."""
    meta = _market_meta.get(pack_name)
    if not meta:
        return None

    repo = meta.get("repo", "")
    ref = meta.get("ref", "main")
    if not repo:
        return None

    # Dedup: check if same repo+ref already downloaded
    for existing_name, existing_dir in _market_pack_dirs.items():
        existing_meta = _market_meta.get(existing_name, {})
        if existing_meta.get("repo") == repo and existing_meta.get("ref", "main") == ref:
            _market_pack_dirs[pack_name] = existing_dir
            return existing_dir

    log(f"[market] Downloading {pack_name} from {repo}@{ref}...")
    staging = _get_market_staging()
    tarball_url = REPO_TARBALL_URL.format(
        owner=repo.split("/")[0], repo=repo.split("/")[-1], ref=ref
    )
    dl_tmp = Path(tempfile.mkdtemp(prefix="petfish-market-dl-"))

    dl_ok = False
    extracted_dir = None

    if download_tarball(tarball_url, dl_tmp, github_token=github_token):
        # Find extracted directory
        for child in dl_tmp.iterdir():
            if child.is_dir() and child.name != "archive.tar.gz":
                extracted_dir = child
                break
        if extracted_dir:
            dl_ok = True

    if not dl_ok:
        # Fall back to git clone
        log("[market] Tarball download failed, falling back to git clone...")
        clone_url = f"https://github.com/{repo}.git"
        clone_dest = dl_tmp / "clone"
        if download_git_clone(clone_url, clone_dest, ref=ref, github_token=github_token):
            extracted_dir = clone_dest
            dl_ok = True

    if not dl_ok or extracted_dir is None:
        log_warn(f"Failed to download {pack_name} from {repo}@{ref}")
        shutil.rmtree(dl_tmp, ignore_errors=True)
        return None

    # Move to staging
    staging_dest = staging / extracted_dir.name
    if extracted_dir != staging_dest:
        if staging_dest.is_dir():
            shutil.rmtree(staging_dest, ignore_errors=True)
        shutil.move(str(extracted_dir), str(staging_dest))

    _market_pack_dirs[pack_name] = staging_dest
    return staging_dest


# ---------------------------------------------------------------------------
# Phase 3: Enhanced pack directory resolution
# ---------------------------------------------------------------------------
def find_pack_dir_enhanced(
    pack_name: str,
    offline: bool = False,
    github_token: str | None = None,
) -> Path | None:
    """Find pack directory with market fallback for optional packs.
    1. Check community staging
    2. Check local packs/core/ and packs/optional/
    3. If not offline and not core, query market and download
    """
    # Community packs are in community staging
    if pack_name.startswith("community--"):
        staging = _get_community_staging()
        candidate = staging / pack_name
        if candidate.is_dir():
            return candidate
        return None

    # Local packs
    for subdir in ("core", "optional"):
        candidate = SCRIPT_ROOT / "packs" / subdir / pack_name
        if candidate.is_dir():
            return candidate

    # Offline: no network fallback
    if offline:
        return None

    # Core packs: try downloading the petfish.ai repo if no local packs/ dir
    if is_core_pack(pack_name):
        log(f"[core] Pack '{pack_name}' not found locally, downloading from petfish.ai repo...")
        return find_core_pack_remote(pack_name, github_token=github_token)

    # Try market for optional packs
    meta = query_market_index(pack_name, github_token=github_token)
    if meta:
        _market_meta[pack_name] = meta
        staging = download_market_pack(pack_name, github_token=github_token)
        if staging:
            # Resolve the actual pack dir within the extracted archive
            meta_path = meta.get("path", "")
            if meta_path:
                pack_path = staging / meta_path
                if pack_path.is_dir():
                    if pack_path.name == ".opencode":
                        return pack_path.parent
                    return pack_path
            # Walk the extracted tree for the pack dir name
            for child in staging.rglob(pack_name):
                if child.is_dir() and (child / ".opencode").is_dir():
                    return child
                if child.is_dir() and (child / "pack-manifest.json").is_file():
                    return child
            # Return staging root itself if it has .opencode
            if (staging / ".opencode").is_dir():
                return staging
            return staging

    return None


def resolve_pack_names(raw: str) -> list[str]:
    """Resolve comma-separated pack specifiers to canonical names."""
    tokens = [t.strip() for t in raw.split(",") if t.strip()]
    if not tokens:
        return []
    if len(tokens) == 1 and tokens[0] == "all":
        local_packs = find_all_packs()
        if local_packs:
            # Also query market index for packs not available locally
            # (e.g. typst-pdf-builder lives in a separate repo)
            try:
                raw = fetch_url_with_mirrors(MARKET_INDEX_URL, timeout=10)
                if raw:
                    data = json.loads(raw)
                    for pack in data.get("packs", []):
                        name = pack.get("name")
                        if name and name not in local_packs:
                            local_packs.append(name)
            except Exception:
                pass  # Offline or market unavailable — use local packs only
            return local_packs
        # Remote mode: no local packs/ dir (SCRIPT_ROOT is temp dir with only the
        # downloaded script). Download core repo + query market index to discover
        # all available packs.
        result: list[str] = []
        core_root = _ensure_core_repo_extracted()
        if core_root:
            for subdir in ("core", "optional"):
                base = core_root / "packs" / subdir
                if base.is_dir():
                    for child in sorted(base.iterdir()):
                        if child.is_dir() and (child / "pack-manifest.json").is_file():
                            result.append(child.name)
        # Also query market index for optional packs (may include packs not in
        # the core repo snapshot, or community packs)
        raw = fetch_url_with_mirrors(MARKET_INDEX_URL, timeout=10)
        if raw:
            try:
                data = json.loads(raw)
                for pack in data.get("packs", []):
                    name = pack.get("name")
                    if name and name not in result:
                        result.append(name)
            except (json.JSONDecodeError, ValueError):
                pass
        return result
    result = []
    for token in tokens:
        if token.startswith("community/"):
            # Community packs are handled by download_community_pack
            # We keep the original spec as the identifier
            result.append(token)
            continue
        canonical = resolve_pack_alias(token)
        result.append(canonical)
    return result


# ---------------------------------------------------------------------------
# Pack manifest
# ---------------------------------------------------------------------------
def load_manifest(pack_dir: Path) -> dict | None:
    """Load pack-manifest.json from a pack directory."""
    mf = pack_dir / "pack-manifest.json"
    if not mf.is_file():
        return None
    try:
        return json.loads(mf.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


# ---------------------------------------------------------------------------
# Version comparison
# ---------------------------------------------------------------------------
def parse_semver(version_str: str) -> tuple[int, int, int]:
    """Parse a semver string like '1.2.3'."""
    m = re.match(r"(\d+)\.(\d+)\.(\d+)", version_str or "0.0.0")
    if m:
        return (int(m.group(1)), int(m.group(2)), int(m.group(3)))
    return (0, 0, 0)


def compare_versions(
    installed_ver: str | None,
    source_ver: str,
    legacy_names: list[str] | None,
    registry: dict,
) -> str:
    """Compare installed vs source version.
    Returns: 'same', 'newer', 'not-installed', 'unknown'.
    """
    # Check all possible names (current + legacy)
    names_to_check = []
    if legacy_names:
        names_to_check = list(legacy_names)
    # The canonical name is checked separately

    # Check if canonical name is in registry
    if installed_ver is not None:
        inst = parse_semver(installed_ver)
        src = parse_semver(source_ver)
        if inst == src:
            return "same"
        if src > inst:
            return "newer"
        return "same"  # installed is newer

    # Check legacy names in registry
    if legacy_names:
        for ln in legacy_names:
            entry = registry.get("packs", {}).get(ln)
            if isinstance(entry, dict):
                iv = entry.get("version")
                if iv:
                    inst = parse_semver(iv)
                    src = parse_semver(source_ver)
                    if inst == src:
                        return "same"
                    if src > inst:
                        return "newer"
                    return "same"

    return "not-installed"


# ---------------------------------------------------------------------------
# Registry (installed-packs.json)
# ---------------------------------------------------------------------------

# Known pack renames: old_name → new_name (#207)
# Stale registry keys from old names are cleaned up on load.
PACK_RENAMES = {
    "series-style-governor": "series-style-governor-pack",
}

# Known skill directory renames (#241): old_skill → new_skill
# Legacy global dirs cause stale Codex thread entries after upgrade.
LEGACY_SKILL_DIRS = {
    "petfish-companion": "fish-brain",
    "marketplace-connector": "fish-market",
    "context-router-skill": "fish-trail",
}


def detect_legacy_global_skills(plat_dirs: dict) -> list[tuple[str, str, str]]:
    """Check global skill dirs for legacy skill names (#241).

    Returns list of (legacy_name, new_name, found_path) tuples.
    """
    found = []
    # Check common global skill roots
    global_roots = []
    home = Path.home()
    for pattern in [".agents/skills", ".codex/skills", ".opencode/skills", ".config/opencode/skills"]:
        global_roots.append(home / pattern)
    # Also check platform-specific global dir if provided
    skills_dir = plat_dirs.get("skills_dir", "")
    if skills_dir:
        p = Path(skills_dir)
        # Only check parent if it looks like a global path (not project-local)
        if ".opencode" not in str(p) and "agents" not in str(p).split(p.anchor):
            pass  # skip project-local

    for root in global_roots:
        if not root.is_dir():
            continue
        for legacy_name, new_name in LEGACY_SKILL_DIRS.items():
            legacy_path = root / legacy_name
            if legacy_path.is_dir():
                found.append((legacy_name, new_name, str(legacy_path)))
    return found


def find_registry_path(target: Path, plat_dirs: dict) -> Path:
    """Determine the installed-packs.json path."""
    skills_dir = plat_dirs.get("skills_dir")
    if skills_dir:
        reg_dir = Path(skills_dir).parent if skills_dir else target / ".opencode"
        return reg_dir / "installed-packs.json"
    return target / ".opencode" / "installed-packs.json"


def load_registry(reg_path: Path) -> dict:
    """Load and normalize the registry file."""
    if not reg_path.is_file():
        return {"packs": {}, "version": "2.0"}
    try:
        data = json.loads(reg_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {"packs": {}, "version": "2.0"}

    packs = data.get("packs")
    if packs is None:
        data["packs"] = {}
    elif isinstance(packs, list):
        # Normalize old array format to dict
        normalized = {}
        for p in packs:
            if isinstance(p, str):
                normalized[p] = {}
            elif isinstance(p, dict):
                name = p.get("name", "")
                if name:
                    normalized[name] = p
        data["packs"] = normalized
    elif not isinstance(packs, dict):
        data["packs"] = {}

    data.setdefault("version", "2.0")
    return data


def save_registry(reg_path: Path, registry: dict):
    """Save registry file (with stale rename cleanup — #207)."""
    reg_path.parent.mkdir(parents=True, exist_ok=True)
    packs = registry.get("packs", {})
    for old_name, new_name in PACK_RENAMES.items():
        if old_name in packs and new_name in packs:
            del packs[old_name]
    reg_path.write_text(
        json.dumps(registry, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def update_registry(
    registry: dict,
    pack_name: str,
    manifest: dict,
    installed_skills: list[str],
    installed_commands: list[str],
    installed_agents: list[str],
):
    """Update registry entry for a pack."""
    now = datetime.now(timezone.utc).isoformat()
    entry = {
        "installed_at": now,
        "version": manifest.get("version", "0.0.0"),
        "skills": installed_skills,
        "commands": installed_commands,
        "agents": installed_agents,
        "skill_count": manifest.get("skill_count", len(installed_skills)),
        "command_count": manifest.get("command_count", len(installed_commands)),
        "agent_count": manifest.get("agent_count", len(installed_agents)),
        "description": manifest.get("description", ""),
    }
    registry["packs"][pack_name] = entry


# ---------------------------------------------------------------------------
# File copy operations
# ---------------------------------------------------------------------------
def copy_skill(src_dir: Path, dest_dir: Path, force: bool) -> bool:
    """Copy a single skill directory. Returns True if copied."""
    if dest_dir.exists() and not force:
        return False
    if not src_dir.is_dir():
        return False
    try:
        shutil.copytree(src_dir, dest_dir, dirs_exist_ok=True)
        return True
    except OSError:
        return False


def copy_command(src_file: Path, dest_dir: Path, force: bool) -> bool:
    """Copy a single command file. Returns True if copied."""
    if not src_file.is_file():
        return False
    dest_file = dest_dir / src_file.name
    if dest_file.exists() and not force:
        return False
    try:
        dest_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src_file, dest_file)
        return True
    except OSError:
        return False


def install_pack_files(
    pack_dir: Path,
    target: Path,
    plat_dirs: dict,
    force: bool,
    manifest: dict,
) -> tuple[list[str], list[str], list[str]]:
    """Install skill/command/agent files from pack to target.
    Returns (installed_skills, installed_commands, installed_agents).
    """
    installed_skills = []
    installed_commands = []
    installed_agents = []

    skills_dir = plat_dirs.get("skills_dir")
    commands_dir = plat_dirs.get("commands_dir")
    agents_dir = plat_dirs.get("agents_dir")

    # Source paths inside the pack
    pack_opencode = pack_dir / ".opencode"
    pack_skills = pack_opencode / "skills"
    pack_commands = pack_opencode / "commands"
    pack_agents = pack_opencode / "agents"

    # Copy skills
    if skills_dir and pack_skills.is_dir():
        skill_names = manifest.get("skills", [])
        for skill_entry in skill_names:
            # Skills can be specified as strings ("skill-name") or dicts
            # ({"name": "skill-name", "path": "."}) in pack-manifest.json
            if isinstance(skill_entry, dict):
                skill_name = skill_entry.get("name", "")
            else:
                skill_name = skill_entry
            if not skill_name or not isinstance(skill_name, str):
                continue
            src = pack_skills / skill_name
            if not src.is_dir():
                # Try to find it as a subdirectory
                continue
            dest = Path(skills_dir) / skill_name
            if copy_skill(src, dest, force):
                # Log the SKILL.md file
                skill_md = dest / "SKILL.md"
                if skill_md.is_file():
                    rel = skill_md.relative_to(target) if str(dest).startswith(str(target)) else dest
                    log_success(str(rel) if str(dest).startswith(str(target)) else f"{dest}/SKILL.md")
                else:
                    log_success(f"{dest}")
                installed_skills.append(skill_name)
            else:
                if dest.exists():
                    log_warn(f"Skills/{skill_name} already exists (use --force to overwrite)")

    # Copy commands
    if commands_dir and pack_commands.is_dir():
        command_names = manifest.get("commands", [])
        for cmd_entry in command_names:
            # Commands can be specified as strings or dicts (same as skills)
            if isinstance(cmd_entry, dict):
                cmd_name = cmd_entry.get("name", "")
            else:
                cmd_name = cmd_entry
            if not cmd_name or not isinstance(cmd_name, str):
                continue
            # Commands may be stored as .md files (without leading /)
            cmd_file = pack_commands / f"{cmd_name}.md"
            if not cmd_file.is_file():
                cmd_file = pack_commands / cmd_name
            if cmd_file.is_file():
                dest_dir_path = Path(commands_dir)
                if copy_command(cmd_file, dest_dir_path, force):
                    rel = dest_dir_path / cmd_file.name
                    log_success(str(rel))
                    installed_commands.append(cmd_name)
                else:
                    log_warn(f"Command {cmd_name} already exists (use --force)")

    # Copy agents
    if agents_dir and pack_agents.is_dir():
        agent_names = manifest.get("agents", [])
        for agent_entry in agent_names:
            # Agents can be specified as strings or dicts (same as skills)
            if isinstance(agent_entry, dict):
                agent_name = agent_entry.get("name", "")
            else:
                agent_name = agent_entry
            if not agent_name or not isinstance(agent_name, str):
                continue
            src = pack_agents / agent_name
            if not src.is_dir():
                continue
            dest = Path(agents_dir) / agent_name
            if copy_skill(src, dest, force):
                log_success(str(dest))
                installed_agents.append(agent_name)
            else:
                if dest.exists():
                    log_warn(f"Agent {agent_name} already exists (use --force)")

    return installed_skills, installed_commands, installed_agents


# ---------------------------------------------------------------------------
# Phase 2: AGENTS.md marker merge
# ---------------------------------------------------------------------------
L1_PACK_MAP: dict[str, str] = {
    "opencode-course-skills-pack": "course-skills.md",
    "repo-deploy-ops-skill-pack": "deploy-ops.md",
    "petfish-style-skill": "petfish-style.md",
    "petfish-companion-skill": "petfish-companion.md",
    "petfish-toolchain-skill": "petfish-companion.md",  # shares same rules file
    "judgment-calibration-pack": "anti-sycophancy.md",
    "fish-trail": "fish-trail.md",
    "research-skill-pack": "research.md",
    "fish-reflection-pack": "fish-reflection.md",
    "series-style-governor-pack": "series-style-governor.md",
}


def merge_agents_md(
    src_file: Path, dst_file: Path, pack_name: str, force: bool, manifest: dict | None = None
) -> str:
    """Merge pack AGENTS.md into target AGENTS.md using marker sections.
    Returns: 'created', 'exists', 'updated', or 'merged'"""
    begin_marker = f"<!-- BEGIN pack: {pack_name} -->"
    end_marker = f"<!-- END pack: {pack_name} -->"

    src_content = src_file.read_text(encoding="utf-8")
    # Strip existing markers from source if present (safety net)
    src_content = src_content.replace(begin_marker + "\n", "").replace(begin_marker, "")
    src_content = src_content.replace(end_marker + "\n", "").replace(end_marker, "")
    src_content = src_content.strip()

    wrapped = f"{begin_marker}\n{src_content}\n{end_marker}"

    # If dst doesn't exist: create
    if not dst_file.is_file():
        dst_file.parent.mkdir(parents=True, exist_ok=True)
        dst_file.write_text(wrapped + "\n", encoding="utf-8")
        return "created"

    dst_text = dst_file.read_text(encoding="utf-8")

    # Collect legacy names from manifest
    legacy_names: list[str] = []
    if manifest and isinstance(manifest.get("legacy_names"), list):
        legacy_names = manifest["legacy_names"]

    # Check if current marker OR any legacy marker exists in dst
    found_current = begin_marker in dst_text
    found_legacy = False
    for ln in legacy_names:
        if f"<!-- BEGIN pack: {ln} -->" in dst_text:
            found_legacy = True
            break

    if found_current or found_legacy:
        if not force:
            return "exists"

        # Replace current name and all legacy name sections
        all_names = [pack_name] + legacy_names
        first_pos = len(dst_text)
        found_any = False

        for name in all_names:
            bm = re.escape(f"<!-- BEGIN pack: {name} -->")
            em = re.escape(f"<!-- END pack: {name} -->")
            pattern = bm + r".*?" + em
            matches = list(re.finditer(pattern, dst_text, flags=re.DOTALL))
            if matches:
                if matches[0].start() < first_pos:
                    first_pos = matches[0].start()
                found_any = True
                dst_text = re.sub(pattern, "", dst_text, flags=re.DOTALL)

        if found_any:
            dst_text = dst_text.strip()
            first_pos = min(first_pos, len(dst_text))
            dst_text = (
                dst_text[:first_pos].rstrip()
                + "\n\n"
                + wrapped
                + "\n\n"
                + dst_text[first_pos:].lstrip()
            )

        # Clean up 3+ blank lines → 2 blank lines
        dst_text = re.sub(r"\n{3,}", "\n\n", dst_text).strip() + "\n"
        dst_file.write_text(dst_text, encoding="utf-8")
        return "updated"

    # Not found: append
    dst_file.write_text(dst_text.rstrip() + f"\n\n{wrapped}\n", encoding="utf-8")
    return "merged"


# ---------------------------------------------------------------------------
# Phase 2: Write L1 rules file
# ---------------------------------------------------------------------------
def write_pack_rules_file(src_file: Path, target: Path, pack_name: str):
    """Write AGENTS.md content (stripped of markers) to .opencode/agents-rules/."""
    l1_name = L1_PACK_MAP.get(pack_name)
    if not l1_name:
        return

    rules_dir = target / ".opencode" / "agents-rules"
    rules_dir.mkdir(parents=True, exist_ok=True)

    content = src_file.read_text(encoding="utf-8")
    # Strip BEGIN/END markers for any possible pack name
    content = re.sub(r"^<!-- BEGIN pack: .+? -->$\n?", "", content, flags=re.MULTILINE)
    content = re.sub(r"^<!-- END pack: .+? -->$\n?", "", content, flags=re.MULTILINE)
    content = content.strip() + "\n"

    rules_file = rules_dir / l1_name
    # Backup existing rules file before overwriting
    if rules_file.is_file():
        ts = datetime.now().strftime("%Y%m%d%H%M%S")
        shutil.copy2(rules_file, rules_dir / f"{l1_name}.{ts}.bak")

    rules_file.write_text(content, encoding="utf-8")
    log_success(f".opencode/agents-rules/{l1_name}")


# ---------------------------------------------------------------------------
# Phase 2: Deploy extra agents-rules from pack's .opencode/agents-rules/
# ---------------------------------------------------------------------------
def deploy_extra_agents_rules(pack_opencode: Path, target: Path):
    """Copy pack's .opencode/agents-rules/*.md files to target."""
    src_rules = pack_opencode / "agents-rules"
    if not src_rules.is_dir():
        return
    dst_rules = target / ".opencode" / "agents-rules"
    dst_rules.mkdir(parents=True, exist_ok=True)
    for f in src_rules.glob("*.md"):
        if f.is_file():
            shutil.copy2(f, dst_rules / f.name)
            log_success(f".opencode/agents-rules/{f.name}")


# ---------------------------------------------------------------------------
# Phase 2: Plugin deployment
# ---------------------------------------------------------------------------
def install_plugin_files(source_root: Path, target: Path):
    """Deploy lib/plugin/*.ts to target/.opencode/plugin/ (skip topic-detector.ts).

    In remote mode (uv run https://...), source_root (SCRIPT_ROOT) is a temp dir
    without lib/plugin/. Fall back to the extracted core repo which has lib/plugin/.
    """
    src_plugin_dir = source_root / "lib" / "plugin"
    if not src_plugin_dir.is_dir():
        # Remote mode: SCRIPT_ROOT has no lib/plugin/, use extracted core repo
        if _core_repo_extracted is not None and (_core_repo_extracted / "lib" / "plugin").is_dir():
            src_plugin_dir = _core_repo_extracted / "lib" / "plugin"
        else:
            return
    dst_plugin_dir = target / ".opencode" / "plugin"
    dst_plugin_dir.mkdir(parents=True, exist_ok=True)

    for src in src_plugin_dir.glob("*.ts"):
        if not src.is_file():
            continue
        # topic-detector.ts is inlined into system-prompt-context-inject.ts (#160/#161)
        # and must NOT be deployed as a standalone plugin (causes constructor crash)
        if src.name == "topic-detector.ts":
            continue
        shutil.copy2(src, dst_plugin_dir / src.name)
        log_success(f".opencode/plugin/{src.name}")


def register_plugin_in_config(config_file: Path):
    """Register plugin tuples in opencode.json (idempotent)."""
    if not config_file.is_file():
        return

    with open(config_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    if "plugin" not in data:
        data["plugin"] = []

    plugins_to_register = [
        [".opencode/plugin/system-prompt-rules.ts", {"mode": "all"}],
        [".opencode/plugin/system-prompt-context-inject.ts", {"maxTopics": 5, "maxSummaryLen": 200}],
    ]

    changed = False
    for plugin_tuple in plugins_to_register:
        plugin_path = plugin_tuple[0]
        already_exists = any(
            isinstance(entry, list) and len(entry) >= 1 and entry[0] == plugin_path
            for entry in data["plugin"]
        )
        if not already_exists:
            data["plugin"].append(plugin_tuple)
            changed = True

    if changed:
        with open(config_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            f.write("\n")
        log_success("opencode.json (plugins registered)")


# ---------------------------------------------------------------------------
# Phase 2: opencode.json deep merge
# ---------------------------------------------------------------------------
def merge_opencode_json(
    src_file: Path, dst_file: Path, force: bool, skills_dir: str = ".opencode/skills"
) -> str:
    """Deep merge opencode.example.json into opencode.json.
    Returns: 'created', 'merged'"""
    with open(src_file, "r", encoding="utf-8") as f:
        src = json.load(f)

    # Replace .opencode/skills/ with actual skills_dir path
    normalized = skills_dir.rstrip("/\\") or ".opencode/skills"
    # Normalize to forward slashes for JSON
    normalized_fwd = normalized.replace("\\", "/")
    src_str = json.dumps(src, ensure_ascii=False)
    src_str = src_str.replace(".opencode/skills/", normalized_fwd + "/")
    src = json.loads(src_str)

    if not dst_file.is_file():
        dst_file.parent.mkdir(parents=True, exist_ok=True)
        with open(dst_file, "w", encoding="utf-8") as f:
            json.dump(src, f, indent=2, ensure_ascii=False)
            f.write("\n")
        return "created"

    with open(dst_file, "r", encoding="utf-8") as f:
        dst = json.load(f)

    ATOMIC_L2 = {"mcp"}

    def deep_merge(s, d, force_flag, parent_key=""):
        for k, v in s.items():
            if k not in d:
                d[k] = v
            elif parent_key in ATOMIC_L2 and force_flag:
                d[k] = v
            elif isinstance(v, dict) and isinstance(d[k], dict):
                deep_merge(v, d[k], force_flag, parent_key=k)
            elif force_flag:
                d[k] = v

    deep_merge(src, dst, force)
    with open(dst_file, "w", encoding="utf-8") as f:
        json.dump(dst, f, indent=2, ensure_ascii=False)
        f.write("\n")
    return "merged"


# ---------------------------------------------------------------------------
# Phase 2: MCP server deployment
# ---------------------------------------------------------------------------
def deploy_mcp_servers(pack_opencode: Path, target: Path):
    """Copy pack's .opencode/mcp/*/ directories to target/.opencode/mcp/*/."""
    src_mcp = pack_opencode / "mcp"
    if not src_mcp.is_dir():
        return
    dst_mcp = target / ".opencode" / "mcp"
    dst_mcp.mkdir(parents=True, exist_ok=True)
    for mcp_dir in src_mcp.iterdir():
        if mcp_dir.is_dir():
            target_dir = dst_mcp / mcp_dir.name
            target_dir.mkdir(parents=True, exist_ok=True)
            for item in mcp_dir.iterdir():
                if item.is_file():
                    shutil.copy2(item, target_dir / item.name)
                elif item.is_dir():
                    dst_sub = target_dir / item.name
                    if dst_sub.is_dir():
                        shutil.rmtree(dst_sub)
                    shutil.copytree(item, dst_sub)
            log_success(f".opencode/mcp/{mcp_dir.name}/")


# ---------------------------------------------------------------------------
# Phase 2: Instruction translation for secondary platforms
# ---------------------------------------------------------------------------
PLATFORM_HEADERS: dict[str, str] = {
    "claude": "# CLAUDE.md — PEtFiSh Agent Instructions\n\n> Auto-generated from AGENTS.md by PEtFiSh installer.\n\n",
    "codex": "# AGENTS.md — PEtFiSh Agent Instructions\n\n> Auto-generated from AGENTS.md by PEtFiSh installer.\n\n",
    "copilot": "# GitHub Copilot Instructions — PEtFiSh Agent Instructions\n\n> Auto-generated from AGENTS.md by PEtFiSh installer.\n\n",
    "windsurf": "# Windsurf Rules — PEtFiSh Agent Instructions\n\n> Auto-generated from AGENTS.md by PEtFiSh installer.\n\n",
}


def translate_rename_with_header(src_content: str, platform_name: str) -> str:
    """Prepend platform-specific header and copy content."""
    header = PLATFORM_HEADERS.get(platform_name, "")
    return header + src_content


def translate_wrap_as_mdc(src_content: str) -> str:
    """Wrap content in Cursor .mdc format."""
    return f"---\ndescription: PEtFiSh Agent Instructions\nalwaysApply: true\n---\n\n{src_content}\n"


def condense_content(content: str, max_tokens: int) -> str:
    """Approximate token counting (1 token ≈ 4 chars) and trim if needed."""
    max_chars = max_tokens * 4
    if len(content) <= max_chars:
        return content
    return content[:max_chars] + "\n\n... (content truncated to fit token limit)"


def translate_instructions(
    src_agents: Path, target: Path, platform_name: str, platforms_data: dict, force: bool
):
    """Translate AGENTS.md instructions for secondary platforms."""
    plat_info = platforms_data.get("platforms", {}).get(platform_name, {})
    translation = plat_info.get("instructions_translation")
    if not translation:
        return

    if not src_agents.is_file():
        return

    src_content = src_agents.read_text(encoding="utf-8")
    method = translation.get("method", "")
    target_rel = translation.get("target", "")

    if not target_rel or not method:
        return

    dst_file = target / target_rel

    if method == "rename_with_header":
        translated = translate_rename_with_header(src_content, platform_name)
    elif method == "wrap_as_mdc":
        translated = translate_wrap_as_mdc(src_content)
    else:
        return

    # Apply condensation if platform has token limit
    condense_cfg = plat_info.get("condense")
    if condense_cfg:
        max_tokens = condense_cfg.get("max_tokens", 0)
        if max_tokens > 0:
            translated = condense_content(translated, max_tokens)

    # Use marker-based merge for the translated content
    # For secondary platforms, we write the translated AGENTS.md content using markers
    if not dst_file.is_file():
        dst_file.parent.mkdir(parents=True, exist_ok=True)
        dst_file.write_text(translated, encoding="utf-8")
        log_success(f"{target_rel} (created)")
    elif force:
        dst_file.write_text(translated, encoding="utf-8")
        log_success(f"{target_rel} (updated)")
    else:
        log_warn(f"{target_rel} already exists (use --force to update)")


# ---------------------------------------------------------------------------
# List packs
# ---------------------------------------------------------------------------
def list_packs(offline: bool = False, github_token: str | None = None):
    """List all available packs."""
    packs = find_all_packs()

    # Remote mode: no local packs/ dir. Try downloading core repo to discover
    # core packs before falling through to market index query.
    if not packs and not offline:
        core_root = _ensure_core_repo_extracted(github_token=github_token)
        if core_root:
            for subdir in ("core", "optional"):
                base = core_root / "packs" / subdir
                if base.is_dir():
                    for child in sorted(base.iterdir()):
                        if child.is_dir() and (child / "pack-manifest.json").is_file():
                            if child.name not in packs:
                                packs.append(child.name)

    # When online, also query market for packs not present locally
    market_packs: list[dict] = []
    if not offline:
        raw = fetch_url_with_mirrors(MARKET_INDEX_URL, timeout=10, github_token=github_token)
        if raw:
            try:
                data = json.loads(raw)
                for pack in data.get("packs", []):
                    if pack.get("name") not in packs:
                        market_packs.append(pack)
            except (json.JSONDecodeError, ValueError):
                pass

    if not packs and not market_packs:
        banner("No packs found. Are you running from a cloned repo?")
        return

    total = len(packs) + len(market_packs)
    banner(f"Available packs ({total}):")
    for pack_name in packs:
        pack_dir = find_pack_dir(pack_name)
        manifest = load_manifest(pack_dir) if pack_dir else None
        version = manifest.get("version", "?") if manifest else "?"
        desc = manifest.get("description", "") if manifest else ""
        # Find alias
        alias = ""
        for a, n in ALIASES.items():
            if n == pack_name and not a.startswith("fish-"):
                alias = f" (alias: {a})"
                break
        core_tag = " [core]" if is_core_pack(pack_name) else ""
        print(f"  {bold(pack_name)}{core_tag} v{version}{alias}")
        if desc:
            print(f"    {desc[:80]}")

    for pack in market_packs:
        name = pack.get("name", "?")
        version = pack.get("version", "?")
        aliases = pack.get("alias", []) or pack.get("aliases", []) or []
        if isinstance(aliases, str):
            aliases = [aliases]
        alias_str = f" (alias: {', '.join(aliases)})" if aliases else ""
        print(f"  {bold(name)} [remote] v{version}{alias_str}")
        desc = pack.get("description", "")
        if desc:
            print(f"    {desc[:80]}")


# ---------------------------------------------------------------------------
# Platform detection display
# ---------------------------------------------------------------------------
def show_detection(target: Path, platforms_data: dict):
    """Detect and display platform for target."""
    detected = detect_platform(target, platforms_data)
    display = platforms_data.get("platforms", {}).get(detected, {}).get(
        "display_name", detected
    )
    banner(f"Detected platform: {display} ({detected})")
    plat_dirs = get_platform_dirs(detected, platforms_data, False, target)
    print(f"  Skills:    {plat_dirs.get('skills_dir', 'N/A')}")
    print(f"  Commands:  {plat_dirs.get('commands_dir', 'N/A')}")
    print(f"  Agents:    {plat_dirs.get('agents_dir', 'N/A')}")
    print(f"  Config:    {plat_dirs.get('config_file', 'N/A')}")
    print(f"  Rules:     {plat_dirs.get('rules_dir', 'N/A')}")


# ---------------------------------------------------------------------------
# Core install pipeline
# ---------------------------------------------------------------------------
def install_single_pack(
    pack_name: str,
    target: Path,
    plat_dirs: dict,
    force: bool,
    reg_path: Path,
    registry: dict,
    plat_name: str = "opencode",
    platforms_data: dict | None = None,
    use_global: bool = False,
    offline: bool = False,
    github_token: str | None = None,
) -> bool:
    """Install a single pack. Returns True on success."""
    # Find pack directory (with market fallback)
    pack_dir = find_pack_dir_enhanced(pack_name, offline=offline, github_token=github_token)
    if pack_dir is None:
        # Check if it's a remote-only pack
        packs_root = SCRIPT_ROOT / "packs"
        if not packs_root.is_dir():
            log_error("No packs/ directory found and remote download failed.")
            return False
        log_error(f"Pack not found: {pack_name}")
        return False

    # Load manifest
    manifest = load_manifest(pack_dir)
    if manifest is None:
        log_error(f"No pack-manifest.json in {pack_dir}")
        return False

    source_ver = manifest.get("version", "0.0.0")
    legacy_names = manifest.get("legacy_names", [])

    # Check installed version
    existing = registry.get("packs", {}).get(pack_name)
    installed_ver = existing.get("version") if isinstance(existing, dict) else None
    ver_status = compare_versions(installed_ver, source_ver, legacy_names, registry)

    if ver_status == "same" and not force:
        log_warn(f"{pack_name} v{source_ver} already installed (use --force to reinstall)")
        return True  # Not an error

    if ver_status == "newer":
        log_warn(f"{pack_name}: upgrading {installed_ver} -> {source_ver}")
        force = True  # Auto-force on upgrade

    # Perform installation
    banner(f"Installing {pack_name} v{source_ver} ...")

    pack_opencode = pack_dir / ".opencode"
    is_opencode = plat_name == "opencode"
    is_l1_pack = pack_name in L1_PACK_MAP
    skills_dir = plat_dirs.get("skills_dir")

    # Step 1: Copy skills/agents/commands (existing Phase 0+1)
    installed_skills, installed_commands, installed_agents = install_pack_files(
        pack_dir, target, plat_dirs, force, manifest
    )

    # Step 2: Write L1 rules file (opencode platform only, for L1 packs)
    if is_opencode and is_l1_pack and not use_global:
        agents_src = pack_dir / "AGENTS.md"
        if agents_src.is_file():
            write_pack_rules_file(agents_src, target, pack_name)

        # Deploy extra agents-rules files from the pack
        deploy_extra_agents_rules(pack_opencode, target)

        # Install plugin files (idempotent, runs for each L1 pack)
        # Plugin registration in config deferred until after opencode.json merge (Step 5)
        install_plugin_files(SCRIPT_ROOT, target)

    # Step 3: Deploy MCP servers
    if is_opencode and not use_global:
        deploy_mcp_servers(pack_opencode, target)

    # Step 3.5: Install Claude Code hooks (if Claude platform and pack has hooks)
    if plat_name == "claude" and not use_global:
        install_claude_hooks(pack_dir, target, force)

    # Step 4: Merge AGENTS.md (primary platform instructions)
    agents_src = pack_dir / "AGENTS.md"
    instructions_file = plat_dirs.get("instructions_file")

    if agents_src.is_file() and instructions_file and not use_global:
        inst_path = Path(instructions_file) if Path(instructions_file).is_absolute() else target / instructions_file

        if is_opencode and is_l1_pack:
            # L1 packs on opencode: skip inline merge (handled by rules files above)
            # Remove old inline section if present (v0.10.x → v0.11.x migration)
            if inst_path.is_file():
                _remove_inline_section(inst_path, pack_name, legacy_names)
        else:
            # Non-opencode or non-L1 packs: merge inline
            result = merge_agents_md(agents_src, inst_path, pack_name, force, manifest)
            if result == "created":
                log_success(f"{instructions_file} (created)")
            elif result == "merged":
                log_success(f"{instructions_file} (merged)")
            elif result == "updated":
                log_success(f"{instructions_file} (updated)")
            elif result == "exists":
                log_warn(f"{instructions_file} (pack section exists, use --force to update)")

    # Step 5: Merge opencode.json (if opencode platform)
    config_file_rel = plat_dirs.get("config_file") if plat_dirs else None
    example_json = pack_dir / "opencode.example.json"

    if is_opencode and config_file_rel and example_json.is_file() and not use_global:
        dst_config = Path(config_file_rel) if Path(config_file_rel).is_absolute() else target / config_file_rel
        skills_dir_str = str(skills_dir) if skills_dir else ".opencode/skills"
        # Make skills_dir relative to target if it's a subpath
        if skills_dir and str(skills_dir).startswith(str(target)):
            skills_dir_str = str(Path(skills_dir).relative_to(target))
        result = merge_opencode_json(example_json, dst_config, force, skills_dir_str)
        if result == "created":
            log_success(f"{config_file_rel} (created from example)")
        elif result == "merged":
            log_success(f"{config_file_rel} (merged)")

    # Step 5.5: Register plugins in config (must be AFTER config merge to avoid overwrite)
    if is_opencode and is_l1_pack and not use_global:
        config_file = plat_dirs.get("config_file")
        if config_file:
            register_plugin_in_config(Path(config_file) if Path(config_file).is_absolute() else target / config_file)

    # Step 6: Translate instructions for secondary platforms
    if platforms_data and not use_global and instructions_file:
        src_agents = target / instructions_file if not Path(instructions_file).is_absolute() else Path(instructions_file)
        if not is_opencode:
            translate_instructions(
                src_agents if src_agents.is_file() else agents_src,
                target, plat_name, platforms_data, force
            )

    # Step 7: Update registry
    update_registry(
        registry,
        pack_name,
        manifest,
        installed_skills,
        installed_commands,
        installed_agents,
    )

    # Summary
    counts = []
    if installed_skills:
        counts.append(f"{len(installed_skills)} skill(s)")
    if installed_commands:
        counts.append(f"{len(installed_commands)} command(s)")
    if installed_agents:
        counts.append(f"{len(installed_agents)} agent(s)")

    summary = ", ".join(counts) if counts else "no new files"
    log_success(f"{pack_name} v{source_ver}: {summary}")

    return True


def _remove_inline_section(agents_file: Path, pack_name: str, legacy_names: list[str]):
    """Remove old inline pack section from AGENTS.md (v0.10.x → v0.11.x migration)."""
    if not agents_file.is_file():
        return

    text = agents_file.read_text(encoding="utf-8")
    all_names = [pack_name] + legacy_names
    changed = False

    for name in all_names:
        bm = re.escape(f"<!-- BEGIN pack: {name} -->")
        em = re.escape(f"<!-- END pack: {name} -->")
        pattern = bm + r".*?" + em
        new_text = re.sub(pattern, "", text, flags=re.DOTALL)
        if new_text != text:
            text = new_text
            changed = True

    if changed:
        text = re.sub(r"\n{3,}", "\n\n", text).strip() + "\n"
        agents_file.write_text(text, encoding="utf-8")


# ---------------------------------------------------------------------------
# Phase 4: Remove AGENTS.md rules-file reference row
# ---------------------------------------------------------------------------
def _remove_rules_file_reference(agents_file: Path, l1_name: str):
    """Remove the table row referencing l1_name from AGENTS.md."""
    if not agents_file.is_file():
        return
    text = agents_file.read_text(encoding="utf-8")
    pattern = re.compile(
        rf"^\|[^\n]*{re.escape(l1_name)}[^\n]*\|\s*\n?", re.MULTILINE
    )
    new_text = pattern.sub("", text)
    if new_text != text:
        new_text = re.sub(r"\n{3,}", "\n\n", new_text).rstrip() + "\n"
        agents_file.write_text(new_text, encoding="utf-8")
        log_success(f"AGENTS.md (removed rules-file reference for {l1_name})")


# ---------------------------------------------------------------------------
# Phase 4: Remove unique opencode.json config entries
# ---------------------------------------------------------------------------
def remove_unique_config_entries(
    pack_name: str,
    pack_example: Path,
    config_file: Path,
    packs_dir: Path,
    registry: dict,
):
    """Remove config entries that ONLY this pack contributed.

    Checks ALL other installed packs' manifests before deleting keys.
    Critical: prevents removing shared config entries (M6 risk).
    """
    if not pack_example.is_file() or not config_file.is_file():
        return

    try:
        pack_cfg = json.loads(pack_example.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return

    installed = list((registry.get("packs") or {}).keys())

    # Collect all keys claimed by OTHER installed packs
    other_claims: dict[str, set] = {}
    for other in installed:
        if other == pack_name:
            continue
        # Look in local packs dirs
        other_example = None
        for subdir in ("core", "optional"):
            candidate = packs_dir / subdir / other / "opencode.example.json"
            if candidate.is_file():
                other_example = candidate
                break
        if other_example is None:
            continue
        try:
            other_cfg = json.loads(other_example.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue
        for p1, v1 in (other_cfg or {}).items():
            if isinstance(v1, dict):
                s = other_claims.setdefault(p1, set())
                for p2 in v1.keys():
                    s.add(p2)

    try:
        dst = json.loads(config_file.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return

    changed = False
    for p1, v1 in (pack_cfg or {}).items():
        if not isinstance(v1, dict):
            continue
        if not isinstance(dst.get(p1), dict):
            continue
        claimed = other_claims.get(p1, set())
        for p2 in v1.keys():
            if p2 in claimed:
                continue
            if p2 in dst[p1]:
                del dst[p1][p2]
                changed = True

    if changed:
        config_file.write_text(
            json.dumps(dst, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        log_success(f"{config_file.name} (removed unique entries from this pack)")


# ---------------------------------------------------------------------------
# Phase 4: Uninstall pack
# ---------------------------------------------------------------------------
def uninstall_pack(
    pack_alias: str,
    target: Path,
    plat_dirs: dict,
    platforms_data: dict,
    script_root: Path,
    offline: bool,
    github_token: str | None = None,
) -> int:
    """Uninstall a pack. Returns number of items removed."""
    # Resolve pack name from alias
    is_community = pack_alias.startswith("community/")
    if is_community:
        owner, repo, _ = _parse_community_spec(pack_alias)
        if not owner or not repo:
            log_error(f"Invalid community pack spec: {pack_alias}")
            return 0
        pack_name = f"community--{owner}--{repo}"
        manifest = None
        legacy_names = []
    else:
        pack_name = resolve_pack_alias(pack_alias)
        pack_dir = find_pack_dir(pack_name)
        if pack_dir is None:
            log_error(f"Pack not found: {pack_name}")
            return 0
        manifest = load_manifest(pack_dir)
        if manifest is None:
            log_error(f"No pack-manifest.json for {pack_name}")
            return 0
        legacy_names = manifest.get("legacy_names", [])

    # Find registry
    reg_path = find_registry_path(target, plat_dirs)
    if not reg_path.is_file():
        log_error(f"No installed-packs.json found at {reg_path}. Nothing to uninstall.")
        return 0
    registry = load_registry(reg_path)

    # Check if installed (including legacy names)
    packs = registry.get("packs", {})
    is_installed = pack_name in packs
    if not is_installed:
        for ln in legacy_names:
            if ln in packs:
                is_installed = True
                break
    if not is_installed:
        log_error(f"Pack '{pack_alias}' ({pack_name}) is not installed. Nothing to uninstall.")
        return 0

    print(f"\n  Uninstalling pack: {pack_name} (alias: {pack_alias})", file=sys.stderr)
    removed = 0

    # Read skills/commands/agents list
    if is_community:
        entry = packs.get(pack_name) or {}
        skills_list = entry.get("skills", [])
        commands_list = entry.get("commands", [])
        agents_list = entry.get("agents", [])
    else:
        skills_list = (manifest or {}).get("skills", [])
        commands_list = (manifest or {}).get("commands", [])
        agents_list = (manifest or {}).get("agents", [])

    # Remove skill directories
    skills_dir = plat_dirs.get("skills_dir")
    if skills_dir:
        for skill_name in skills_list:
            skill_dir = Path(skills_dir) / skill_name
            if skill_dir.is_dir():
                shutil.rmtree(skill_dir, ignore_errors=True)
                log(f"    - skills/{skill_name}")
                removed += 1

    # Remove command files/directories
    commands_dir = plat_dirs.get("commands_dir")
    if commands_dir:
        for cmd in commands_list:
            cmd_dir = Path(commands_dir) / cmd
            cmd_file = Path(commands_dir) / f"{cmd}.md"
            if cmd_dir.is_dir():
                shutil.rmtree(cmd_dir, ignore_errors=True)
                log(f"    - commands/{cmd}")
                removed += 1
            elif cmd_file.is_file():
                cmd_file.unlink(missing_ok=True)
                log(f"    - commands/{cmd}.md")
                removed += 1

    # Remove agent directories
    agents_dir = plat_dirs.get("agents_dir")
    if agents_dir:
        for agent_name in agents_list:
            agent_dir = Path(agents_dir) / agent_name
            if agent_dir.is_dir():
                shutil.rmtree(agent_dir, ignore_errors=True)
                log(f"    - agents/{agent_name}")
                removed += 1

    # Remove AGENTS.md inline section
    instructions_file = plat_dirs.get("instructions_file")
    if instructions_file:
        inst_path = Path(instructions_file) if Path(instructions_file).is_absolute() else target / instructions_file
        _remove_inline_section(inst_path, pack_name, legacy_names)

    # Remove L1 rules file and its AGENTS.md reference row
    l1_name = L1_PACK_MAP.get(pack_name)
    if l1_name:
        rules_file = target / ".opencode" / "agents-rules" / l1_name
        if rules_file.is_file():
            rules_file.unlink(missing_ok=True)
            log(f"    - .opencode/agents-rules/{l1_name}")
            removed += 1

        if instructions_file:
            inst_path = Path(instructions_file) if Path(instructions_file).is_absolute() else target / instructions_file
            _remove_rules_file_reference(inst_path, l1_name)

    # Remove unique opencode.json entries
    config_file_rel = plat_dirs.get("config_file")
    if config_file_rel and not is_community:
        config_path = Path(config_file_rel) if Path(config_file_rel).is_absolute() else target / config_file_rel
        pack_dir_found = find_pack_dir(pack_name)
        if pack_dir_found:
            pack_example = pack_dir_found / "opencode.example.json"
            packs_root = script_root / "packs"
            remove_unique_config_entries(
                pack_name, pack_example, config_path, packs_root, registry
            )

    # Remove registry entry (pack_name + legacy_names)
    changed = False
    if pack_name in packs:
        del packs[pack_name]
        changed = True
    for ln in legacy_names:
        if ln in packs:
            del packs[ln]
            changed = True
    if changed:
        registry["packs"] = packs
        save_registry(reg_path, registry)
        log_success("installed-packs.json (registry updated)")
        removed += 1

    print(f"\n  Uninstall complete: {removed} items removed.", file=sys.stderr)
    return removed


# ---------------------------------------------------------------------------
# Phase 4: Global uninstall
# ---------------------------------------------------------------------------
def uninstall_global_pack(
    pack_alias: str,
    plat_dirs: dict,
    platforms_data: dict,
    script_root: Path,
    offline: bool,
    github_token: str | None = None,
) -> int:
    """Uninstall a pack from global directory. Returns number of items removed."""
    is_community = pack_alias.startswith("community/")
    if is_community:
        owner, repo, _ = _parse_community_spec(pack_alias)
        if not owner or not repo:
            log_error(f"Invalid community pack spec: {pack_alias}")
            return 0
        pack_name = f"community--{owner}--{repo}"
        manifest = None
        legacy_names = []
    else:
        pack_name = resolve_pack_alias(pack_alias)
        pack_dir = find_pack_dir(pack_name)
        if pack_dir is None:
            log_error(f"Pack not found: {pack_name}")
            return 0
        manifest = load_manifest(pack_dir)
        if manifest is None:
            log_error(f"No pack-manifest.json for {pack_name}")
            return 0
        legacy_names = manifest.get("legacy_names", [])

    # Get global skills dir
    skills_dir = plat_dirs.get("skills_dir")
    if not skills_dir:
        log_warn("This platform does not support global skill installation. Nothing to uninstall.")
        return 0

    # Find global registry
    skills_dir_path = Path(skills_dir)
    reg_path = skills_dir_path.parent / "installed-packs.json"
    if not reg_path.is_file():
        log_error(f"No installed-packs.json found at {reg_path}. Nothing to uninstall.")
        return 0
    registry = load_registry(reg_path)

    # Check if installed
    packs = registry.get("packs", {})
    is_installed = pack_name in packs
    if not is_installed:
        for ln in legacy_names:
            if ln in packs:
                is_installed = True
                break
    if not is_installed:
        log_error(f"Pack '{pack_alias}' ({pack_name}) is not installed globally. Nothing to uninstall.")
        return 0

    print(f"\n  Uninstalling pack (global): {pack_name} (alias: {pack_alias})", file=sys.stderr)
    removed = 0

    # Read skills/commands list
    if is_community:
        entry = packs.get(pack_name) or {}
        skills_list = entry.get("skills", [])
        commands_list = entry.get("commands", [])
    else:
        skills_list = (manifest or {}).get("skills", [])
        commands_list = (manifest or {}).get("commands", [])

    # Remove skills from global dir
    for skill_name in skills_list:
        skill_dir = skills_dir_path / skill_name
        if skill_dir.is_dir():
            shutil.rmtree(skill_dir, ignore_errors=True)
            log(f"    - skills/{skill_name}")
            removed += 1

    # Remove commands from global dir
    commands_dir = plat_dirs.get("commands_dir")
    if commands_dir:
        commands_dir_path = Path(commands_dir)
        for cmd in commands_list:
            cmd_dir = commands_dir_path / cmd
            cmd_file = commands_dir_path / f"{cmd}.md"
            if cmd_dir.is_dir():
                shutil.rmtree(cmd_dir, ignore_errors=True)
                log(f"    - commands/{cmd}")
                removed += 1
            elif cmd_file.is_file():
                cmd_file.unlink(missing_ok=True)
                log(f"    - commands/{cmd}.md")
                removed += 1

    # Remove registry entry
    changed = False
    if pack_name in packs:
        del packs[pack_name]
        changed = True
    for ln in legacy_names:
        if ln in packs:
            del packs[ln]
            changed = True
    if changed:
        registry["packs"] = packs
        save_registry(reg_path, registry)
        log_success("installed-packs.json (registry updated)")
        removed += 1

    print(f"\n  Uninstall complete: {removed} items removed.", file=sys.stderr)
    return removed


# ---------------------------------------------------------------------------
# Phase 4: Claude Code hooks installation
# ---------------------------------------------------------------------------
def install_claude_hooks(pack_dir: Path, target: Path, force: bool):
    """Install Claude Code hooks from pack's .claude/hooks/ directory."""
    src_hooks = pack_dir / ".claude" / "hooks"
    if not src_hooks.is_dir():
        return

    target_hooks = target / ".claude" / "hooks"
    target_hooks.mkdir(parents=True, exist_ok=True)

    for hook_file in src_hooks.iterdir():
        if not hook_file.is_file():
            continue
        dst_hook = target_hooks / hook_file.name
        if dst_hook.is_file() and not force:
            log_warn(f"hooks/{hook_file.name} (exists, use --force to overwrite)")
            continue
        shutil.copy2(hook_file, dst_hook)
        # Make executable on Unix
        if os.name != "nt":
            try:
                os.chmod(dst_hook, 0o755)
            except OSError:
                pass
        log_success(f"hooks/{hook_file.name}")

    # Merge hooks into settings.json
    settings_file = target / ".claude" / "settings.json"
    merge_claude_hooks(settings_file)


def merge_claude_hooks(settings_file: Path):
    """Merge fish-trail hooks into .claude/settings.json."""
    hooks_config = {
        "hooks": {
            "UserPromptSubmit": [
                {"hooks": [{"type": "command", "command": "bash .claude/hooks/fish-trail-gateway.sh", "timeout": 5}]}
            ],
            "PreCompact": [
                {"hooks": [{"type": "command", "command": "bash .claude/hooks/fish-trail-precompact.sh", "timeout": 5}]}
            ],
            "PostCompact": [
                {"hooks": [{"type": "command", "command": "bash .claude/hooks/fish-trail-postcompact.sh", "timeout": 5}]}
            ],
        }
    }

    if settings_file.is_file():
        try:
            settings = json.loads(settings_file.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, ValueError):
            settings = {}
    else:
        settings_file.parent.mkdir(parents=True, exist_ok=True)
        settings = {}

    if "hooks" not in settings:
        settings["hooks"] = {}

    for event_name, event_groups in hooks_config["hooks"].items():
        if event_name not in settings["hooks"]:
            settings["hooks"][event_name] = event_groups
        else:
            # Check existing commands to avoid duplicates
            existing_commands = set()
            for group in settings["hooks"][event_name]:
                for hook in group.get("hooks", []):
                    cmd = hook.get("command")
                    if cmd:
                        existing_commands.add(cmd)

            for group in event_groups:
                for hook in group.get("hooks", []):
                    if hook.get("command") and hook["command"] not in existing_commands:
                        settings["hooks"][event_name].append(group)
                        break

    settings_file.write_text(
        json.dumps(settings, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    log_success(".claude/settings.json (hooks merged)")


# ---------------------------------------------------------------------------
# Phase 4: v0.9.x → v1.4.x Migration
# ---------------------------------------------------------------------------
PACK_RENAMES = {
    "context-router-skill": "fish-trail",
    "companion": "petfish-companion-skill",
    "toolchain": "petfish-toolchain-skill",
    "project-initializer": "project-initializer-skill",
    "anti-sycophancy-calibration": "anti-sycophancy-calibration-pack",
    "anti-sycophancy-calibration-pack": "judgment-calibration-pack",
    "petfish-style-rewriter": "petfish-style-skill",
    "de-ai-detector": "petfish-style-skill",
    "style-extractor": "petfish-style-skill",
    "skill-trust-governance": "trustskills-governance-pack",
}

SKILL_RENAMES = {
    "context-router": "fish-trail",
    "petfish-companion": "fish-brain",
    "marketplace-connector": "fish-market",
    "project-initializer": "fish-init",
    "anti-sycophancy-calibration": "fish-calibrate",
    "petfish-style-rewriter": "fish-style",
    "skill-trust-governance": "fish-guard",
}

RULES_RENAMES = {
    "context-router.md": "fish-trail.md",
}


def migrate_legacy_v0_9(target: Path, skills_dir_rel: str, config_file_rel: str, rules_dir_rel: str | None):
    """Migrate v0.9.x → v1.4.x artifacts (renamed packs, skills, MCP paths)."""
    if not target.is_dir():
        return

    migrated = False

    def find_registry_file(base: Path) -> Path | None:
        for candidate in [
            base / ".opencode" / "installed-packs.json",
            base / ".claude" / "installed-packs.json",
            base / ".agents" / "installed-packs.json",
        ]:
            if candidate.is_file():
                return candidate
        return None

    # Check target dir and home dir for registries
    home = Path.home()
    for base_dir in [target, home]:
        reg_file = find_registry_file(base_dir)
        if not reg_file or not reg_file.is_file():
            continue
        try:
            reg = json.loads(reg_file.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue

        packs = reg.get("packs")
        if packs is None:
            continue
        # Convert old array format to dict
        if isinstance(packs, list):
            packs = {p: {} for p in packs if isinstance(p, str)}
            reg["packs"] = packs

        changed = False
        for old_key, new_key in PACK_RENAMES.items():
            if old_key in packs and new_key not in packs:
                packs[new_key] = packs.pop(old_key)
                log(f"    ↻ Registry: {old_key} -> {new_key}")
                changed = True
                migrated = True
            elif old_key in packs and new_key in packs:
                del packs[old_key]
                log(f"    ↻ Registry: removed stale {old_key}")
                changed = True
                migrated = True

        if changed:
            reg_file.write_text(
                json.dumps(reg, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )

    # Rename skill directories on disk
    abs_skills = target / skills_dir_rel if not Path(skills_dir_rel).is_absolute() else Path(skills_dir_rel)
    if abs_skills.is_dir():
        for old_dir, new_dir in SKILL_RENAMES.items():
            old_path = abs_skills / old_dir
            new_path = abs_skills / new_dir
            if old_path.is_dir():
                if new_path.is_dir():
                    shutil.rmtree(old_path, ignore_errors=True)
                    log(f"    ↻ Removed stale skill dir: {old_dir}/")
                else:
                    old_path.rename(new_path)
                    log(f"    ↻ Renamed skill dir: {old_dir}/ -> {new_dir}/")
                migrated = True

    # Rename rules files on disk
    if rules_dir_rel:
        abs_rules = target / rules_dir_rel if not Path(rules_dir_rel).is_absolute() else Path(rules_dir_rel)
        if abs_rules.is_dir():
            for old_file, new_file in RULES_RENAMES.items():
                old_path = abs_rules / old_file
                new_path = abs_rules / new_file
                if old_path.is_file():
                    if new_path.is_file():
                        old_path.unlink(missing_ok=True)
                        log(f"    ↻ Removed stale rules file: {old_file}")
                    else:
                        old_path.rename(new_path)
                        log(f"    ↻ Renamed rules file: {old_file} -> {new_file}")
                    migrated = True

    # Update MCP paths in config files
    if config_file_rel:
        abs_config = target / config_file_rel if not Path(config_file_rel).is_absolute() else Path(config_file_rel)
        if abs_config.is_file():
            content = abs_config.read_text(encoding="utf-8")
            new_content = content
            for old_str, new_str in [
                ("context-router/mcp", "fish-trail/mcp"),
                ("context-router/", "fish-trail/"),
            ]:
                if old_str in new_content:
                    new_content = new_content.replace(old_str, new_str)

            # Also update MCP server config
            try:
                config = json.loads(new_content)
                mcp = config.get("mcp", {})
                if "context-state" in mcp:
                    srv = mcp["context-state"]
                    if isinstance(srv, dict):
                        for field in ["command", "args"]:
                            val = srv.get(field, "")
                            if isinstance(val, str) and "context-router" in val:
                                srv[field] = val.replace("context-router", "fish-trail")
                            elif isinstance(val, list):
                                srv[field] = [
                                    a.replace("context-router", "fish-trail")
                                    if isinstance(a, str) and "context-router" in a else a
                                    for a in val
                                ]
                        for env_key in ["cwd", "PETFISH_STATE_DIR"]:
                            env_val = srv.get(env_key, "")
                            if isinstance(env_val, str) and "context-router" in env_val:
                                srv[env_key] = env_val.replace("context-router", "fish-trail")
                        env = srv.get("env", {})
                        if isinstance(env, dict):
                            for k, v in env.items():
                                if isinstance(v, str) and "context-router" in v:
                                    env[k] = v.replace("context-router", "fish-trail")
                    updated = json.dumps(config, indent=2, ensure_ascii=False)
                    if updated != new_content:
                        new_content = updated + "\n"
            except (json.JSONDecodeError, KeyError):
                pass

            if new_content != content:
                abs_config.write_text(new_content, encoding="utf-8")
                log(f"    ↻ Updated MCP paths in {config_file_rel}")
                migrated = True

    if migrated:
        banner("Legacy v0.9.x artifacts migrated to v1.4.x")


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------
def build_parser() -> argparse.ArgumentParser:
    """Build CLI argument parser."""
    parser = argparse.ArgumentParser(
        prog="install.py",
        description="PEtFiSh Skill Pack Installer",
        epilog="Examples:\n"
        "  uv run install.py --pack init --target .\n"
        "  uv run install.py --pack course,deploy --detect\n"
        "  uv run install.py --list\n"
        "  uv run install.py --pack all --platform claude --force\n",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "pack_positional",
        nargs="?",
        default=None,
        help="Pack alias or name (positional, can also use --pack)",
    )
    parser.add_argument(
        "--pack", "-p",
        default=None,
        help="Comma-separated pack aliases or names (e.g. 'init,companion')",
    )
    parser.add_argument(
        "--target", "-t",
        default=".",
        help="Target directory (default: current directory)",
    )
    parser.add_argument(
        "--platform",
        default="opencode",
        help="Platform name or group: opencode|claude|codex|cursor|copilot|windsurf|antigravity|universal|all|primary|ide|cli",
    )
    parser.add_argument(
        "--detect",
        action="store_true",
        help="Auto-detect platform from target markers",
    )
    parser.add_argument(
        "--force", "-f",
        action="store_true",
        help="Force reinstall/upgrade",
    )
    parser.add_argument(
        "--global",
        dest="global_install",
        action="store_true",
        help="Install to user-level directory",
    )
    parser.add_argument(
        "--list", "-l",
        action="store_true",
        help="List available packs",
    )
    parser.add_argument(
        "--uninstall",
        action="store_true",
        help="Remove a pack",
    )
    parser.add_argument(
        "--offline",
        action="store_true",
        help="Skip network queries",
    )
    parser.add_argument(
        "--branch",
        default=None,
        help="Override git branch (for remote mode)",
    )
    parser.add_argument(
        "--repo",
        default=None,
        help="Override source repo (for remote mode)",
    )
    parser.add_argument(
        "--trust-scan",
        action="store_true",
        help="Run trust scan on community packs",
    )
    parser.add_argument(
        "--github-token",
        default=None,
        help="GitHub auth token",
    )
    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()

    # Load platforms data
    platforms_data = load_platforms()

    # Handle --list
    if args.list:
        list_packs(offline=args.offline, github_token=args.github_token)
        return 0

    # Handle --uninstall
    if args.uninstall:
        pack_spec = args.pack or args.pack_positional
        if not pack_spec:
            log_error("No pack specified for uninstall. Use --pack <alias> --uninstall.")
            return 1

        pack_names = resolve_pack_names(pack_spec)
        if not pack_names:
            log_error("No valid packs specified.")
            return 1

        target = Path(args.target).resolve()
        if not target.is_dir():
            log_error(f"Target directory does not exist: {target}")
            return 1

        if args.detect:
            plat_name = detect_platform(target, platforms_data)
        else:
            plat_names = resolve_platform_name(args.platform, platforms_data)
            plat_name = plat_names[0] if len(plat_names) == 1 else "opencode"

        plat_dirs = get_platform_dirs(plat_name, platforms_data, args.global_install, target)
        total_removed = 0
        for pack_alias in pack_names:
            if args.global_install:
                total_removed += uninstall_global_pack(
                    pack_alias, plat_dirs, platforms_data, SCRIPT_ROOT,
                    offline=args.offline, github_token=args.github_token,
                )
            else:
                total_removed += uninstall_pack(
                    pack_alias, target, plat_dirs, platforms_data, SCRIPT_ROOT,
                    offline=args.offline, github_token=args.github_token,
                )

        banner(f"Uninstall done: {total_removed} total items removed")
        return 0

    # Handle --detect only (no pack specified)
    pack_spec = args.pack or args.pack_positional
    if args.detect and not pack_spec:
        target = Path(args.target).resolve()
        show_detection(target, platforms_data)
        return 0

    # Must have a pack to install
    if not pack_spec:
        parser.print_help()
        print("\nERROR: No pack specified. Use --pack <alias> or a positional argument.", file=sys.stderr)
        return 1

    # Resolve pack names
    pack_names = resolve_pack_names(pack_spec)
    if not pack_names:
        log_error("No valid packs specified.")
        return 1

    # Resolve target
    target = Path(args.target).resolve()
    if not target.is_dir():
        log_error(f"Target directory does not exist: {target}")
        return 1

    # Resolve platform
    if args.detect:
        plat_name = detect_platform(target, platforms_data)
        display = platforms_data.get("platforms", {}).get(plat_name, {}).get(
            "display_name", plat_name
        )
        banner(f"Detected platform: {display} ({plat_name})")
    else:
        plat_names = resolve_platform_name(args.platform, platforms_data)
        plat_name = plat_names[0] if len(plat_names) == 1 else "opencode"
        # For platform groups, install to each
        if len(plat_names) > 1:
            banner(f"Platform group '{args.platform}' expands to: {', '.join(plat_names)}")
            # Install to first platform in group for now
            plat_name = plat_names[0]
            log_warn(f"Installing to first platform only: {plat_name}")

    # Get platform directories
    plat_dirs = get_platform_dirs(plat_name, platforms_data, args.global_install, target)

    # Validate
    skills_dir = plat_dirs.get("skills_dir")
    if not skills_dir:
        log_error(f"No skills directory for platform '{plat_name}' in {'global' if args.global_install else 'project'} mode")
        return 1

    # Ensure skills directory exists
    Path(skills_dir).mkdir(parents=True, exist_ok=True)

    # Find registry path
    reg_path = find_registry_path(target, plat_dirs)
    registry = load_registry(reg_path)

    # Run v0.9.x → v1.4.x migration
    skills_dir_rel = plat_dirs.get("skills_dir", ".opencode/skills")
    if skills_dir_rel and Path(skills_dir_rel).is_absolute():
        try:
            skills_dir_rel = str(Path(skills_dir_rel).relative_to(target))
        except ValueError:
            skills_dir_rel = str(skills_dir_rel)
    config_file_rel = plat_dirs.get("config_file") or ""
    rules_dir_rel = ".opencode/agents-rules"
    migrate_legacy_v0_9(target, skills_dir_rel, config_file_rel, rules_dir_rel)

    # Reload registry after migration may have modified it on disk
    registry = load_registry(reg_path)

    # Check for remote mode (no local packs/ dir)
    has_local_packs = (SCRIPT_ROOT / "packs").is_dir()
    if not has_local_packs and args.offline:
        log_error("No packs/ directory found and --offline prevents network downloads.")
        log_error("Clone the repo first: git clone https://github.com/kylecui/petfish.ai.git")
        return 1

    # Install each pack
    # Fix #215: When init is mixed with other packs, split the install —
    # init goes global, rest stays local. Only when:
    #   - not explicitly --global
    #   - not explicitly --target (other than default ".")
    #   - target is "." (cwd, the default)
    target_explicit = args.target != "."
    INIT_PACK_NAME = "project-initializer-skill"
    should_split = (
        not args.global_install
        and not target_explicit
        and str(target) == str(Path(".").resolve())
        and any(p == INIT_PACK_NAME for p in pack_names)
    )

    success_count = 0

    if should_split:
        init_packs = [p for p in pack_names if p == INIT_PACK_NAME]
        other_packs = [p for p in pack_names if p != INIT_PACK_NAME]
        log("init pack defaults to global install. Use --target to install locally.")

        # Install init globally
        global_plat_dirs = get_platform_dirs(plat_name, platforms_data, True, target)
        global_skills_dir = global_plat_dirs.get("skills_dir")
        if global_skills_dir:
            Path(global_skills_dir).mkdir(parents=True, exist_ok=True)
            global_reg_path = find_registry_path(target, global_plat_dirs)
            global_registry = load_registry(global_reg_path)
            for pack_name in init_packs:
                try:
                    install_ok = install_single_pack(
                        pack_name, target, global_plat_dirs, args.force,
                        global_reg_path, global_registry,
                        plat_name=plat_name,
                        platforms_data=platforms_data,
                        use_global=True,
                        offline=args.offline,
                        github_token=args.github_token,
                    )
                    if install_ok:
                        success_count += 1
                except Exception as exc:
                    log_error(f"{pack_name}: {exc}")
            save_registry(global_reg_path, global_registry)

        # Install rest locally
        for pack_name in other_packs:
            try:
                if pack_name.startswith("community/"):
                    result = download_community_pack(pack_name, github_token=args.github_token)
                    if result is None:
                        log_error(f"Failed to download community pack: {pack_name}")
                        continue
                    staged_name, staged_path = result
                    install_ok = install_single_pack(
                        staged_name, target, plat_dirs, args.force, reg_path, registry,
                        plat_name=plat_name,
                        platforms_data=platforms_data,
                        use_global=False,
                        offline=args.offline,
                        github_token=args.github_token,
                    )
                    if install_ok:
                        success_count += 1
                    continue

                install_ok = install_single_pack(
                    pack_name, target, plat_dirs, args.force, reg_path, registry,
                    plat_name=plat_name,
                    platforms_data=platforms_data,
                    use_global=False,
                    offline=args.offline,
                    github_token=args.github_token,
                )
                if install_ok:
                    success_count += 1
            except Exception as exc:
                log_error(f"{pack_name}: {exc}")
    else:
        # Normal install: all packs to the same target (global or local)
        for pack_name in pack_names:
            try:
                # Community packs: download first, then install as the staged name
                if pack_name.startswith("community/"):
                    result = download_community_pack(pack_name, github_token=args.github_token)
                    if result is None:
                        log_error(f"Failed to download community pack: {pack_name}")
                        continue
                    staged_name, staged_path = result
                    install_ok = install_single_pack(
                        staged_name, target, plat_dirs, args.force, reg_path, registry,
                        plat_name=plat_name,
                        platforms_data=platforms_data,
                        use_global=args.global_install,
                        offline=args.offline,
                        github_token=args.github_token,
                    )
                    if install_ok:
                        success_count += 1
                    continue

                install_ok = install_single_pack(
                    pack_name, target, plat_dirs, args.force, reg_path, registry,
                    plat_name=plat_name,
                    platforms_data=platforms_data,
                    use_global=args.global_install,
                    offline=args.offline,
                    github_token=args.github_token,
                )
                if install_ok:
                    success_count += 1
            except Exception as exc:
                log_error(f"{pack_name}: {exc}")

    # Cleanup staging directories
    _cleanup_staging()

    # Save registry
    if success_count > 0:
        save_registry(reg_path, registry)
        log_success(f"Registry updated: {reg_path}")

    # Final summary
    banner(f"Done: {success_count}/{len(pack_names)} pack(s) processed")

    return 0 if success_count > 0 else 1


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    try:
        sys.exit(main() or 0)
    except KeyboardInterrupt:
        print("", file=sys.stderr)
        banner("Interrupted.")
        sys.exit(130)
    except Exception as exc:
        print(f"\n  {red('ERROR:')} {exc}", file=sys.stderr)
        print(
            f"  {yellow('Run with --help for usage information.')}",
            file=sys.stderr,
        )
        sys.exit(1)
