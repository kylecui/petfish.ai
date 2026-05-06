#!/usr/bin/env python3
"""
PEtFiSh Companion — Skill Catalog Query

Dynamically reads pack-manifest.json from each pack directory, with embedded
fallback data for offline/remote operation.

Supports:
  --list          List all packs with aliases and descriptions
  --search TERM   Search packs by keyword (matches name, triggers, capabilities)
  --profile NAME  Show packs auto-installed for a given profile
  --json          Output as JSON instead of plain text

Usage:
  uv run catalog_query.py --list
  uv run catalog_query.py --search 部署
  uv run catalog_query.py --profile code
  uv run catalog_query.py --search deploy --json
"""

import argparse
import json
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Alias → pack directory name mapping (single source of truth for aliases)
# ---------------------------------------------------------------------------

ALIAS_MAP = {
    "init": "project-initializer-skill",
    "companion": "petfish-companion-skill",
    "course": "opencode-course-skills-pack",
    "deploy": "repo-deploy-ops-skill-pack",
    "petfish": "petfish-style-skill",
    "ppt": "opencode-ppt-skills",
    "testdocs": "opencode-skill-pack-testcases-usage-docs",
    "trust": "trustskills-governance-pack",
    "calibrate": "anti-sycophancy-calibration-pack",
    "context": "fish-trail",
}

# Reverse map: pack name → alias
PACK_TO_ALIAS = {v: k for k, v in ALIAS_MAP.items()}

# Install scope overrides (packs not listed default to "project")
GLOBAL_PACKS = {"init", "companion"}

# Trigger keywords per alias (for search — not stored in manifest)
TRIGGERS = {
    "init": ["初始化", "新项目", "project init", "scaffold", "创建项目"],
    "companion": ["/petfish", "what skills", "what can you do", "help with"],
    "course": [
        "课程",
        "教学",
        "大纲",
        "课时",
        "模块",
        "学员",
        "教师",
        "实验",
        "QA",
        "QC",
        "发布",
        "讲义",
    ],
    "deploy": [
        "部署",
        "上线",
        "deploy",
        "Docker",
        "服务器",
        "运维",
        "回滚",
        "health check",
        "systemctl",
        "nginx",
    ],
    "petfish": [
        "说人话",
        "润色",
        "去AI味",
        "风格",
        "改写",
        "rewrite",
        "polish",
        "humanize",
    ],
    "ppt": ["PPT", "幻灯片", "演示", "slide", "deck", "presentation", "PPTX"],
    "testdocs": [
        "测试用例",
        "test case",
        "测试矩阵",
        "文档",
        "README",
        "usage docs",
        "API docs",
    ],
    "trust": [
        "skill trust",
        "skill安全",
        "治理",
        "可信度",
        "trust scan",
        "governance",
        "risk score",
        "redline",
    ],
    "calibrate": [
        "评审",
        "评价",
        "批判",
        "review",
        "critique",
        "feedback",
        "judgment",
        "decision",
        "evaluation",
        "校准",
        "迎合",
        "sycophancy",
        "方案评估",
        "可行性分析",
        "code review",
        "这个想法怎么样",
        "你觉得呢",
        "对吗",
        "是不是",
    ],
    "context": [
        "话题",
        "上下文",
        "topic",
        "context",
        "污染",
        "继承",
        "隔离",
        "话题切换",
        "话题治理",
        "context package",
        "topic detect",
        "contamination",
    ],
}

PROFILES = {
    "minimal": ["petfish"],
    "course": ["course", "petfish"],
    "code": ["deploy", "petfish", "testdocs"],
    "ops": ["deploy", "petfish"],
    "security": ["deploy", "petfish", "testdocs", "trust"],
    "writing": ["petfish", "ppt"],
    "skills-package": ["petfish", "testdocs"],
    "comprehensive": [
        "course",
        "deploy",
        "petfish",
        "ppt",
        "testdocs",
        "trust",
        "context",
    ],
}


def _find_packs_root() -> Path | None:
    """Walk up from this script to find the packs/ directory."""
    # Script lives in: packs/<pack>/.opencode/skills/<skill>/scripts/
    # So packs/ is 6 levels up
    current = Path(__file__).resolve()
    for _ in range(8):
        current = current.parent
        packs_dir = current / "packs"
        if packs_dir.is_dir():
            return packs_dir
    return None


def _load_manifest(pack_dir: Path) -> dict | None:
    """Load pack-manifest.json from a pack directory."""
    manifest_path = pack_dir / "pack-manifest.json"
    if not manifest_path.exists():
        return None
    try:
        with open(manifest_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return None


# Platform → registry file path (relative to project root)
_REGISTRY_PATHS = [
    ".opencode/installed-packs.json",
    ".claude/installed-packs.json",
    ".agents/installed-packs.json",
    ".cursor/installed-packs.json",
    ".github/installed-packs.json",
    ".windsurf/installed-packs.json",
]


def _load_installed_registry() -> dict:
    """Load installed-packs.json from the current project or global paths.

    Returns a dict of pack_name -> {version, installed_at, ...} or empty dict.
    """
    # Search from CWD upward for installed-packs.json
    cwd = Path.cwd()
    for rel in _REGISTRY_PATHS:
        path = cwd / rel
        if path.exists():
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                return data.get("packs", {})
            except (json.JSONDecodeError, OSError):
                continue

    # Fallback: global registry paths
    home = Path.home()
    global_candidates = [
        home / ".config/opencode/installed-packs.json",
        home / ".claude/installed-packs.json",
        home / ".codex/installed-packs.json",
        home / ".cursor/installed-packs.json",
        home / ".github/installed-packs.json",
        home / ".codeium/windsurf/installed-packs.json",
        home / ".agents/installed-packs.json",
    ]
    for path in global_candidates:
        if path.exists():
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                return data.get("packs", {})
            except (json.JSONDecodeError, OSError):
                continue

    return {}


def build_catalog() -> list[dict]:
    """Build catalog from manifest files, with installed-packs.json fallback."""
    packs_root = _find_packs_root()
    installed_registry = None  # Lazy-loaded only if needed
    catalog = []

    for alias, pack_name in ALIAS_MAP.items():
        entry = {
            "alias": alias,
            "pack": pack_name,
            "install_scope": "global" if alias in GLOBAL_PACKS else "project",
            "triggers": TRIGGERS.get(alias, []),
        }

        manifest = None
        if packs_root:
            pack_dir = packs_root / pack_name
            if pack_dir.is_dir():
                manifest = _load_manifest(pack_dir)

        if manifest:
            entry["description"] = manifest.get("description", "")
            entry["version"] = manifest.get("version", "unknown")
            entry["skill_count"] = manifest.get(
                "skill_count", len(manifest.get("skills", []))
            )
            entry["command_count"] = manifest.get(
                "command_count", len(manifest.get("commands", []))
            )
            entry["agent_count"] = manifest.get(
                "agent_count", len(manifest.get("agents", []))
            )
        else:
            # Fallback: try installed-packs.json registry
            if installed_registry is None:
                installed_registry = _load_installed_registry()

            reg_info = installed_registry.get(pack_name, {})
            entry["description"] = reg_info.get("description", "")
            entry["version"] = reg_info.get("version", "unknown")
            entry["skill_count"] = reg_info.get("skill_count", 0)
            entry["command_count"] = reg_info.get("command_count", 0)
            entry["agent_count"] = reg_info.get("agent_count", 0)

        catalog.append(entry)

    return catalog


def _counts_str(entry: dict) -> str:
    """Format skill/cmd/agent counts as compact string."""
    parts = []
    sc = entry.get("skill_count", 0)
    cc = entry.get("command_count", 0)
    ac = entry.get("agent_count", 0)
    if sc:
        parts.append(f"skills={sc}")
    if cc:
        parts.append(f"cmds={cc}")
    if ac:
        parts.append(f"agents={ac}")
    return " ".join(parts) if parts else ""


def list_packs(as_json: bool = False):
    """List all packs."""
    catalog = build_catalog()

    if as_json:
        print(json.dumps(catalog, ensure_ascii=False, indent=2))
        return

    print("Available packs:")
    print("-" * 60)
    for p in catalog:
        alias = p["alias"]
        desc = p["description"]
        scope = "🌐" if p["install_scope"] == "global" else "📁"
        counts = _counts_str(p)
        version = p.get("version", "")
        ver_str = f"v{version}" if version and version != "unknown" else ""

        # Format: scope alias (pack_name) ver  counts
        header = f"  {scope} {alias} ({p['pack']})"
        meta_parts = [x for x in [ver_str, counts] if x]
        meta = "  " + " ".join(meta_parts) if meta_parts else ""
        print(f"{header}{meta}")
        if desc:
            print(f"     {desc}")
    print("-" * 60)
    print("🌐 = global install   📁 = project install")
    print("Use --search <keyword> to filter by capability.")


def search_packs(term: str, as_json: bool = False):
    """Search packs by keyword across name, description, and triggers."""
    catalog = build_catalog()
    term_lower = term.lower()
    results = []
    for p in catalog:
        searchable = " ".join(
            [
                p["alias"],
                p["pack"],
                p.get("description", ""),
                " ".join(p.get("triggers", [])),
            ]
        ).lower()
        if term_lower in searchable:
            results.append(p)

    if as_json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
        return

    if not results:
        print(f"No packs found matching '{term}'.")
        return

    print(f"Found {len(results)} pack(s) matching '{term}':\n")
    for p in results:
        matched = [t for t in p.get("triggers", []) if term_lower in t.lower()]
        counts = _counts_str(p)
        print(f"  {p['alias']} — {p['pack']}  {counts}")
        if p.get("description"):
            print(f"    {p['description']}")
        if matched:
            print(f"    Matched triggers: {', '.join(matched)}")
        print()


def show_profile(name: str, as_json: bool = False):
    """Show packs for a given profile."""
    if name not in PROFILES:
        print(f"Unknown profile '{name}'. Available: {', '.join(PROFILES.keys())}")
        sys.exit(1)

    catalog = build_catalog()
    aliases = PROFILES[name]
    packs = [p for p in catalog if p["alias"] in aliases]

    if as_json:
        print(
            json.dumps({"profile": name, "packs": packs}, ensure_ascii=False, indent=2)
        )
        return

    print(f"Profile: {name}")
    print(f"Auto-installed packs ({len(aliases)}):\n")
    for p in packs:
        counts = _counts_str(p)
        desc = p.get("description", p["pack"])
        print(f"  {p['alias'].ljust(14)} {desc}  {counts}")
    print()


def main():
    parser = argparse.ArgumentParser(description="PEtFiSh Skill Catalog Query")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--list", action="store_true", help="List all packs")
    group.add_argument("--search", type=str, help="Search by keyword")
    group.add_argument("--profile", type=str, help="Show packs for a profile")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    if args.list:
        list_packs(as_json=args.json)
    elif args.search:
        search_packs(args.search, as_json=args.json)
    elif args.profile:
        show_profile(args.profile, as_json=args.json)


if __name__ == "__main__":
    main()
