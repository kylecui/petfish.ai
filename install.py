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
import tempfile
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
    "calibrate": "anti-sycophancy-calibration-pack",
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
    "fish-calibrate": "anti-sycophancy-calibration-pack",
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
# Hardcoded platforms.json fallback
# ---------------------------------------------------------------------------
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


def resolve_pack_names(raw: str) -> list[str]:
    """Resolve comma-separated pack specifiers to canonical names."""
    tokens = [t.strip() for t in raw.split(",") if t.strip()]
    if not tokens:
        return []
    if len(tokens) == 1 and tokens[0] == "all":
        return find_all_packs()
    result = []
    for token in tokens:
        if token.startswith("community/"):
            log_warn(f"Community packs not yet supported: {token}")
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
    """Save registry file."""
    reg_path.parent.mkdir(parents=True, exist_ok=True)
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
        for skill_name in skill_names:
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
        for cmd_name in command_names:
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
        for agent_name in agent_names:
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
    "anti-sycophancy-calibration-pack": "anti-sycophancy.md",
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
    """Deploy lib/plugin/*.ts to target/.opencode/plugin/ (skip topic-detector.ts)."""
    src_plugin_dir = source_root / "lib" / "plugin"
    if not src_plugin_dir.is_dir():
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
def list_packs():
    """List all available packs."""
    packs = find_all_packs()
    if not packs:
        banner("No packs found. Are you running from a cloned repo?")
        return
    banner(f"Available packs ({len(packs)}):")
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
) -> bool:
    """Install a single pack. Returns True on success."""
    # Find pack directory
    pack_dir = find_pack_dir(pack_name)
    if pack_dir is None:
        # Check if it's a remote-only pack
        packs_root = SCRIPT_ROOT / "packs"
        if not packs_root.is_dir():
            log_error("No packs/ directory found. Remote mode not yet implemented.")
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
        help="Remove a pack (not yet implemented)",
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
        list_packs()
        return 0

    # Handle --uninstall (Phase 4 stub)
    if args.uninstall:
        print("Uninstall not yet implemented. Use Phase 4.", file=sys.stderr)
        return 1

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

    # Check for remote mode
    if not (SCRIPT_ROOT / "packs").is_dir():
        log_error("No packs/ directory found. Remote mode not yet implemented.")
        log_error("Clone the repo first: git clone https://github.com/kylecui/petfish.ai.git")
        return 1

    # Install each pack
    success_count = 0
    for pack_name in pack_names:
        try:
            if install_single_pack(
                pack_name, target, plat_dirs, args.force, reg_path, registry,
                plat_name=plat_name,
                platforms_data=platforms_data,
                use_global=args.global_install,
            ):
                success_count += 1
        except Exception as exc:
            log_error(f"{pack_name}: {exc}")

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
