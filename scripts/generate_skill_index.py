# /// script
# requires-python = ">=3.10"
# ///
"""Generate skill-index.json from installed SKILL.md files.

Scans .opencode/skills/*/SKILL.md, parses YAML frontmatter, and produces
.opencode/skill-index.json — an authoritative local index of all installed
skills for use by companion-gateway.ts Skill Sense and fish-market search.

Usage:
    uv run scripts/generate_skill_index.py [--skills-dir .opencode/skills] [--output .opencode/skill-index.json]
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import re
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

MARKET_INDEX_URL = "https://raw.githubusercontent.com/kylecui/petfish-market/main/index.json"
COMMUNITY_PACKS_URL = "https://raw.githubusercontent.com/kylecui/petfish.ai/master/community-packs.json"


def load_catalog(skills_dir: Path):
    """Import catalog_query (single source of TRIGGERS/ALIAS_MAP), best-effort."""
    candidates = [
        skills_dir / "fish-brain" / "scripts" / "catalog_query.py",  # installed layout
        Path(__file__).resolve().parent.parent / "packs" / "core"
        / "petfish-companion-skill" / ".opencode" / "skills" / "fish-brain"
        / "scripts" / "catalog_query.py",  # repo layout
    ]
    for path in candidates:
        if path.is_file():
            spec = importlib.util.spec_from_file_location("petfish_catalog_query", path)
            if spec and spec.loader:
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)
                return mod
    return None


def fetch_json(url: str, timeout: float = 5.0):
    """Best-effort JSON fetch; returns None on any failure."""
    try:
        with urllib.request.urlopen(url, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception:
        return None


def build_domains(catalog) -> dict:
    """domains map: alias -> {keywords, pack} from catalog TRIGGERS/ALIAS_MAP."""
    if catalog is None:
        return {}
    alias_map = getattr(catalog, "ALIAS_MAP", {}) or {}
    domains: dict = {}
    for alias, keywords in (getattr(catalog, "TRIGGERS", {}) or {}).items():
        domains[alias] = {
            "keywords": list(keywords),
            "pack": alias_map.get(alias, alias),
        }
    return domains


def build_available_packs() -> dict:
    """Best-effort market + community pack listings (never fails)."""
    market = fetch_json(MARKET_INDEX_URL) or {}
    market_packs = [
        {
            "name": p.get("name", ""),
            "alias": (p.get("alias") or [None])[0],
            "description": p.get("description", ""),
            "version": p.get("version", ""),
            "skill_count": p.get("skill_count", 0),
            "source": "market",
        }
        for p in market.get("packs", [])
        if isinstance(p, dict)
    ]
    local_community = Path("community-packs.json")
    community_data = (
        json.loads(local_community.read_text(encoding="utf-8"))
        if local_community.is_file()
        else fetch_json(COMMUNITY_PACKS_URL)
    ) or {}
    community_packs = [
        {
            "name": p.get("name", ""),
            "description": p.get("description", ""),
            "repo": p.get("repo", ""),
            "source": "community",
        }
        for p in community_data.get("packs", [])
        if isinstance(p, dict)
    ]
    return {"market": market_packs, "community": community_packs}


def parse_frontmatter(content: str) -> dict:
    """Parse YAML frontmatter from SKILL.md content, including nested blocks."""
    match = re.match(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
    if not match:
        return {}

    frontmatter_text = match.group(1)
    result: dict = {}
    current_nested_key: str | None = None

    for line in frontmatter_text.split("\n"):
        # Indented line under a nested key
        if current_nested_key and line.startswith("  ") and ":" in line:
            nested_line = line.strip()
            if ":" in nested_line:
                nk, _, nv = nested_line.partition(":")
                nk = nk.strip()
                nv = nv.strip()
                # Parse array values: [a, b, c]
                if nv.startswith("[") and nv.endswith("]"):
                    nv = [x.strip().strip("\"'") for x in nv[1:-1].split(",") if x.strip()]
                elif nv.lower() in ("true", "false"):
                    nv = nv.lower() == "true"
                if nk:
                    result[current_nested_key][nk] = nv
            continue

        # Non-indented line — could be top-level key or start of nested block
        current_nested_key = None
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if ":" in stripped:
            key, _, value = stripped.partition(":")
            key = key.strip()
            value = value.strip()
            if not value:
                # Could be a nested block header (e.g., "orchestration:")
                current_nested_key = key
                result[key] = {}
            else:
                value = value.strip("\"'")
                if key and value:
                    result[key] = value

    return result


def extract_body_preview(content: str, max_chars: int = 500) -> str:
    """Extract a short preview of the SKILL.md body (after frontmatter)."""
    # Remove frontmatter
    body = re.sub(r"^---\s*\n.*?\n---\s*\n", "", content, flags=re.DOTALL)
    # Take first paragraph
    preview = body.strip().split("\n\n")[0] if body.strip() else ""
    return preview[:max_chars]


def index_skill(skill_dir: Path) -> dict | None:
    """Index a single skill directory."""
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.is_file():
        return None

    content = skill_md.read_text(encoding="utf-8")
    fm = parse_frontmatter(content)

    if not fm.get("name"):
        return None

    # Collect trigger keywords from description
    description = fm.get("description", "")
    triggers = []
    for word in re.findall(r"[\w-]+", description.lower()):
        if len(word) > 2:
            triggers.append(word)

    entry = {
        "name": fm.get("name", skill_dir.name),
        "description": description,
        "triggers": list(set(triggers)),
        "path": str(skill_dir.relative_to(skill_dir.parent.parent)),
        "has_scripts": (skill_dir / "scripts").is_dir(),
        "has_references": (skill_dir / "references").is_dir(),
        "preview": extract_body_preview(content),
    }

    # Add orchestration metadata if present
    orch = fm.get("orchestration")
    if isinstance(orch, dict) and orch:
        entry["orchestration"] = {
            "role": orch.get("role", "specialist"),
            "input_contract": orch.get("input_contract", []),
            "output_contract": orch.get("output_contract", []),
            "parallel_safe": orch.get("parallel_safe", False),
        }

    return entry


def collect_skill_dirs(skills_dir: Path) -> list[Path]:
    """Collect candidate skill dirs: skills_dir children + repo packs layout.

    In a user project (installed layout) packs/ does not exist and behavior
    is unchanged. In the petfish.ai dev repo, pack skills live under
    packs/{core,optional}/<pack>/.opencode/skills/ and are unioned in.
    """
    dirs: list[Path] = []
    seen: set[str] = set()

    def add_children(parent: Path) -> None:
        if not parent.is_dir():
            return
        for child in sorted(parent.iterdir()):
            if child.is_dir() and child.name not in seen:
                seen.add(child.name)
                dirs.append(child)

    add_children(skills_dir)
    cwd = Path.cwd()
    for packs_root in (cwd / "packs" / "core", cwd / "packs" / "optional"):
        if packs_root.is_dir():
            for pack_dir in sorted(packs_root.iterdir()):
                add_children(pack_dir / ".opencode" / "skills")
    return dirs


def build_pack_attribution() -> dict[str, str]:
    """Map skill name -> parent pack name. Registry first (installed layout),
    then repo pack manifests (dev layout). Best-effort."""
    attribution: dict[str, str] = {}
    # 1) installed registry (.opencode/installed-packs.json): packs -> skills list
    reg = Path(".opencode") / "installed-packs.json"
    try:
        data = json.loads(reg.read_text(encoding="utf-8"))
        for pack_name, entry in (data.get("packs") or {}).items():
            if isinstance(entry, dict):
                for s in entry.get("skills") or []:
                    if isinstance(s, str) and s:
                        attribution.setdefault(s, pack_name)
    except (OSError, json.JSONDecodeError):
        pass
    # 2) repo manifests (dev layout)
    for group in ("core", "optional"):
        root = Path.cwd() / "packs" / group
        if not root.is_dir():
            continue
        for pack_dir in root.iterdir():
            mf = pack_dir / "pack-manifest.json"
            if not mf.is_file():
                continue
            try:
                data = json.loads(mf.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                continue
            for se in data.get("skills", []):
                nm = se.get("name", "") if isinstance(se, dict) else se
                if isinstance(nm, str) and nm:
                    attribution.setdefault(nm, pack_dir.name)
    return attribution


def generate_index(skills_dir: Path) -> dict:
    """Generate the full skill index."""
    skills = []
    for skill_dir in collect_skill_dirs(skills_dir):
        entry = index_skill(skill_dir)
        if entry:
            skills.append(entry)

    attribution = build_pack_attribution()
    for entry in skills:
        if entry["name"] in attribution:
            entry["pack"] = attribution[entry["name"]]

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "skill_count": len(skills),
        "skills": skills,
        "domains": build_domains(load_catalog(skills_dir)),
        "available_packs": build_available_packs(),
    }


def main():
    parser = argparse.ArgumentParser(description="Generate skill-index.json")
    parser.add_argument(
        "--skills-dir",
        default=".opencode/skills",
        help="Skills directory to scan (default: .opencode/skills)",
    )
    parser.add_argument(
        "--output",
        default=".opencode/skill-index.json",
        help="Output file path (default: .opencode/skill-index.json)",
    )
    args = parser.parse_args()

    skills_dir = Path(args.skills_dir)
    if not skills_dir.is_dir():
        repo_layout = (Path.cwd() / "packs" / "core").is_dir() or (
            Path.cwd() / "packs" / "optional"
        ).is_dir()
        if not repo_layout:
            print(f"Error: skills directory not found: {skills_dir}", file=sys.stderr)
            sys.exit(1)

    index = generate_index(skills_dir)

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(index, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    print(f"Generated {output_path}: {index['skill_count']} skills indexed")


if __name__ == "__main__":
    main()
