#!/usr/bin/env python3
"""
PEtFiSh Companion — Skill Catalog Query

Dynamically reads pack-manifest.json from each pack directory, with embedded
fallback data for offline/remote operation.

Supports:
  --list              List all packs with aliases and descriptions
  --search TERM       Search packs by keyword (matches name, triggers, capabilities)
  --profile NAME      Show packs auto-installed for a given profile
  --check-failures T  Scan text for failure signals, recommend uninstalled packs
  --json              Output as JSON instead of plain text

Usage:
  uv run catalog_query.py --list
  uv run catalog_query.py --search 部署
  uv run catalog_query.py --profile code
  uv run catalog_query.py --search deploy --json
"""

import argparse
import json
import re
import sys
import urllib.error
import urllib.request
import platform as platform_mod
from pathlib import Path

# ---------------------------------------------------------------------------
# Alias → pack directory name mapping (single source of truth for aliases)
# ---------------------------------------------------------------------------

ALIAS_MAP = {
    "init": "project-initializer-skill",
    "fish-init": "project-initializer-skill",
    "companion": "petfish-companion-skill",
    "fish-brain": "petfish-companion-skill",
    "fish-core": "petfish-companion-skill",
    "toolchain": "petfish-toolchain-skill",
    "course": "opencode-course-skills-pack",
    "deploy": "repo-deploy-ops-skill-pack",
    "petfish": "petfish-style-skill",
    "fish-style": "petfish-style-skill",
    "ppt": "opencode-ppt-skills",
    "testdocs": "opencode-skill-pack-testcases-usage-docs",
    "trust": "trustskills-governance-pack",
    "fish-guard": "trustskills-governance-pack",
    "calibrate": "judgment-calibration-pack",
    "fish-calibrate": "judgment-calibration-pack",
    "council-thinking": "judgment-calibration-pack",
    "context": "fish-trail",
    "research": "research-skill-pack",
    "reflect": "fish-reflection-pack",
    "doc-reader": "doc-reader-skill",
    "de-ai-detector": "petfish-style-skill",
    "style-extractor": "petfish-style-skill",
}

# Reverse map: pack name → canonical alias (first alias listed for each pack)
PACK_TO_ALIAS = {}
_seen_packs = set()
for _a, _p in ALIAS_MAP.items():
    if _p not in _seen_packs:
        PACK_TO_ALIAS[_p] = _a
        _seen_packs.add(_p)

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
    "research": [
        "研究",
        "帮我研究",
        "仔细研究",
        "调研",
        "文献",
        "literature",
        "research",
        "investigate",
        "来源",
        "证据",
        "evidence",
        "综述",
        "论文",
        "学术",
        "academic",
        "citation",
        "source verification",
        "市场分析",
        "竞品分析",
        "论文方向",
        "规划方案",
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
    "reflect": [
        "反思",
        "reflect",
        "复盘",
        "what went wrong",
        "lessons learned",
        "纠正",
        "返工",
        "rework",
    ],
    "doc-reader": [
        "PDF", "DOCX", "读文档", "文档转换", "doc to markdown",
        "read document", "convert document", "extract text",
    ],
    "de-ai-detector": [
        "去AI味检测",
        "AI味检测",
        "检测AI写作",
        "detect AI writing",
        "AI text detector",
        "humanizer check",
        "AI slop detector",
    ],
    "style-extractor": [
        "提炼写作风格",
        "提取我的风格",
        "风格画像",
        "style extraction",
        "writing style analysis",
        "extract my voice",
        "nuwa style",
    ],
    # v1.3/v1.4 aliases share triggers with canonical
    "fish-init": ["初始化", "新项目", "project init", "scaffold", "创建项目"],
    "fish-brain": ["/petfish", "what skills", "what can you do", "help with"],
    "fish-core": ["/petfish", "what skills", "what can you do", "help with"],
    "toolchain": ["lint", "audit", "gate", "skill publish", "toolchain"],
    "fish-style": ["说人话", "润色", "去AI味", "风格", "改写", "rewrite", "polish"],
    "fish-guard": ["skill trust", "skill安全", "治理", "可信度", "trust scan"],
    "fish-calibrate": [
        "评审", "评价", "批判", "review", "critique", "feedback",
        "校准", "迎合", "sycophancy", "方案评估",
        "好吗", "合理吗", "你觉得", "对吗", "是不是", "这个想法怎么样",
    ],
    "council-thinking": [
        "方案评估", "战略判断", "产品定位", "技术路线选择", "研究设计", "课程设计",
        "Council", "五人顾问团", "多视角", "对抗式判断", "用Council分析",
        "presentation主线", "商业分析", "逻辑审查", "是否值得做", "反迎合审查",
        "multi-perspective", "adversarial reasoning", "council review",
        "judgment calibration", "collective judgment", "顾问团", "多角度评审",
    ],
}

# ---------------------------------------------------------------------------
# Failure Signal Detection (Tier 0)
# Maps regex patterns (applied to previous assistant output) → recommended pack
# ---------------------------------------------------------------------------

FAILURE_SIGNALS = {
    "ppt": re.compile(r"无法(打开|读取|解析).*(PDF|PPTX|PPT|幻灯片)", re.IGNORECASE),
    "deploy": re.compile(
        r"(deploy|部署|Docker).*(fail|失败|error|错误)", re.IGNORECASE
    ),
    "testdocs": re.compile(
        r"(测试用例|test case).*(无法|不确定|需要).*生成", re.IGNORECASE
    ),
    "research": re.compile(
        r"(需要更多|证据不足|无法确认).*(来源|evidence|文献)", re.IGNORECASE
    ),
    "context": re.compile(r"(上下文|context).*(混乱|污染|冲突|drift)", re.IGNORECASE),
}


def check_failures(text: str, target: Path, as_json: bool = False) -> None:
    """Scan text for failure signals; report packs that can help (skip installed)."""
    installed_path = target / ".opencode" / "installed-packs.json"
    installed_aliases: set[str] = set()
    if installed_path.exists():
        try:
            data = json.loads(installed_path.read_text(encoding="utf-8"))
            installed_aliases = set(data.get("packs", {}).keys())
        except (json.JSONDecodeError, OSError):
            pass

    matches: list[dict] = []
    for alias, pattern in FAILURE_SIGNALS.items():
        if alias in installed_aliases:
            continue
        if pattern.search(text):
            matches.append({"pack": alias, "pattern": pattern.pattern})

    if as_json:
        print(json.dumps({"failures": matches}, ensure_ascii=False, indent=2))
    else:
        for m in matches:
            print(
                f"💡 检测到上轮失败信号 — {m['pack']}-skill 可以处理此类问题。"
                f"安装: /petfish install {m['pack']}"
            )
        if not matches:
            pass  # silent when no failures detected


# ---------------------------------------------------------------------------
# Market index query
# ---------------------------------------------------------------------------

MARKET_INDEX_URL = (
    "https://raw.githubusercontent.com/kylecui/petfish-market/main/index.json"
)

# Core packs always come from petfish.ai tarball; optional packs are market-first.
CORE_PACK_ALIASES = {"init", "companion", "toolchain", "context"}


def query_market(alias: str) -> dict | None:
    """Query petfish-market index.json for a pack by alias.

    Returns the matching pack dict from the index, or None if not found or
    the index is unavailable (network error, timeout, parse failure).
    """
    req = urllib.request.Request(MARKET_INDEX_URL)
    req.add_header("User-Agent", "PEtFiSh-Catalog/1.0")
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        for pack in data.get("packs", []):
            if alias in pack.get("alias", []) or pack.get("name") == alias:
                return pack
    except Exception:
        pass
    return None


# ---------------------------------------------------------------------------
# Built-in profiles (role/scenario-based)
#
# Design principles:
#   - Each profile represents a user *role/scenario*, not a feature bundle.
#   - Core packs (context, toolchain, init, companion) are auto-installed and
#     intentionally omitted here — they are not optional add-ons.
#   - Legacy profile names are kept as aliases for backward compatibility.
# ---------------------------------------------------------------------------

PROFILES: dict[str, list[str]] = {
    # --- Role-based profiles (v2) ---
    "starter": ["petfish"],
    "developer": ["petfish", "deploy", "testdocs", "calibrate"],
    "researcher": ["petfish", "research", "doc-reader", "calibrate"],
    "writer": ["petfish", "ppt", "doc-reader", "research"],
    "educator": ["petfish", "course", "ppt", "doc-reader", "testdocs"],
    "ops-engineer": ["petfish", "deploy", "trust", "calibrate"],
    "power-user": [
        "petfish",
        "deploy",
        "testdocs",
        "trust",
        "research",
        "calibrate",
        "reflect",
        "ppt",
        "doc-reader",
    ],
    # --- Kept for backward compatibility ---
    "minimal": ["petfish"],
    "course": ["course", "petfish", "doc-reader"],
    "code": ["deploy", "petfish", "testdocs"],
    "ops": ["deploy", "petfish"],
    "security": ["deploy", "petfish", "testdocs", "trust"],
    "writing": ["petfish", "ppt"],
    "skills-package": ["petfish", "testdocs"],
    "research": ["petfish", "research", "doc-reader"],
    "comprehensive": [
        "course",
        "deploy",
        "petfish",
        "ppt",
        "testdocs",
        "trust",
        "context",
        "research",
        "reflect",
        "doc-reader",
    ],
}

# Human-readable descriptions for built-in profiles
PROFILE_DESCRIPTIONS: dict[str, str] = {
    "starter": "Just getting started — writing style and basic assistance",
    "developer": "Daily coding — deployment, test docs, and decision review",
    "researcher": "Academic/research — deep research, document reading, judgment calibration",
    "writer": "Content creation — writing style, presentations, doc reading, research",
    "educator": "Course development — full teaching toolchain",
    "ops-engineer": "DevOps/security — deployment, trust governance, decision calibration",
    "power-user": "Full-featured setup (add course/context as needed)",
    # legacy
    "minimal": "Minimal — writing style only (legacy alias for starter)",
    "course": "Course development (legacy)",
    "code": "Coding projects (legacy alias for developer)",
    "ops": "Ops projects (legacy alias for ops-engineer)",
    "security": "Security-focused projects (legacy)",
    "writing": "Writing projects (legacy alias for writer)",
    "skills-package": "Skill pack development (legacy)",
    "research": "Research projects (legacy alias for researcher)",
    "comprehensive": "All optional packs (legacy alias for power-user)",
}


def _find_packs_root() -> Path | None:
    """Walk up from this script to find the packs/ directory."""
    # Script lives in: packs/{core,optional}/<pack>/.opencode/skills/<skill>/scripts/
    # So packs/ is 7 levels up
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


def _find_registry_path(target: Path | None = None) -> Path | None:
    """Find the installed-packs.json path for the given target (or CWD)."""
    base = target if target is not None else Path.cwd()
    for rel in _REGISTRY_PATHS:
        path = base / rel
        if path.exists():
            return path

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
            return path
    return None


def _load_registry_data(target: Path | None = None) -> dict:
    """Load and return the full installed-packs.json data dict (all keys)."""
    path = _find_registry_path(target)
    if path is None:
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return {}


def _save_registry_data(data: dict, target: Path | None = None) -> Path | None:
    """Write data back to installed-packs.json, returning the path used or None."""
    path = _find_registry_path(target)
    if path is None:
        # Default to .opencode/installed-packs.json in target/CWD
        base = target if target is not None else Path.cwd()
        path = base / ".opencode" / "installed-packs.json"
        path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return path
    except OSError:
        return None


def _load_installed_registry(target: Path | None = None) -> dict:
    """Load installed-packs.json from the target project or global paths.

    Returns a dict of pack_name -> {version, installed_at, ...} or empty dict.
    """
    return _load_registry_data(target).get("packs", {})


def _load_custom_profiles(target: Path | None = None) -> dict[str, list[str]]:
    """Return user-defined custom profiles from installed-packs.json."""
    return _load_registry_data(target).get("custom_profiles", {})


def build_catalog(target: Path | None = None) -> list[dict]:
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
            # v1.4: packs restructured into core/ + optional/
            pack_dir = packs_root / "core" / pack_name
            if not pack_dir.is_dir():
                pack_dir = packs_root / "optional" / pack_name
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
            # Soft-dependency hints (pack-manifest.json recommends field)
            if manifest.get("recommends"):
                entry["recommends"] = manifest["recommends"]
            if manifest.get("recommends_reason"):
                entry["recommends_reason"] = manifest["recommends_reason"]
        else:
            # Fallback: try installed-packs.json registry
            if installed_registry is None:
                installed_registry = _load_installed_registry(target)

            reg_info = installed_registry.get(pack_name, {})
            entry["description"] = reg_info.get("description", "")
            entry["version"] = reg_info.get("version", "unknown")
            entry["skill_count"] = reg_info.get(
                "skill_count", len(reg_info.get("skills", []))
            )
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


def list_packs(as_json: bool = False, target: Path | None = None):
    """List all packs."""
    catalog = build_catalog(target)

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


def search_packs(term: str, as_json: bool = False, target: Path | None = None):
    """Search packs by keyword across name, description, and triggers."""
    catalog = build_catalog(target)
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


def show_profile(name: str, as_json: bool = False, target: Path | None = None):
    """Show packs for a given profile (built-in or custom)."""
    custom = _load_custom_profiles(target)
    all_profiles = {**PROFILES, **custom}

    if name == "list":
        _list_profiles(as_json=as_json, target=target)
        return

    if name not in all_profiles:
        print(f"Unknown profile '{name}'. Available: {', '.join(sorted(all_profiles.keys()))}")
        sys.exit(1)

    catalog = build_catalog(target)
    aliases = all_profiles[name]
    packs = [p for p in catalog if p["alias"] in aliases]
    is_custom = name in custom

    if as_json:
        print(
            json.dumps(
                {"profile": name, "is_custom": is_custom, "packs": packs},
                ensure_ascii=False,
                indent=2,
            )
        )
        return

    label = "custom" if is_custom else "built-in"
    desc = PROFILE_DESCRIPTIONS.get(name, "")
    print(f"Profile: {name}  [{label}]")
    if desc:
        print(f"  {desc}")
    print(f"Auto-installed packs ({len(aliases)}):\n")
    for p in packs:
        counts = _counts_str(p)
        desc_p = p.get("description", p["pack"])
        print(f"  {p['alias'].ljust(14)} {desc_p}  {counts}")
    print()


def _list_profiles(as_json: bool = False, target: Path | None = None):
    """List all built-in and custom profiles."""
    custom = _load_custom_profiles(target)
    built_in_new = ["starter", "developer", "researcher", "writer", "educator", "ops-engineer", "power-user"]
    built_in_legacy = [k for k in PROFILES if k not in built_in_new]

    if as_json:
        result = {
            "built_in": {k: PROFILES[k] for k in built_in_new},
            "legacy": {k: PROFILES[k] for k in built_in_legacy},
            "custom": custom,
        }
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    print("Built-in profiles:")
    for name in built_in_new:
        packs_str = ", ".join(PROFILES[name])
        desc = PROFILE_DESCRIPTIONS.get(name, "")
        print(f"  {name.ljust(15)} [{packs_str}]")
        if desc:
            print(f"  {''.ljust(15)}  {desc}")
    print()
    print("Legacy profiles (kept for compatibility):")
    for name in built_in_legacy:
        packs_str = ", ".join(PROFILES[name])
        print(f"  {name.ljust(15)} [{packs_str}]")
    if custom:
        print()
        print("Custom profiles:")
        for name, aliases in custom.items():
            print(f"  {name.ljust(15)} [{', '.join(aliases)}]")
    print()
    print("Use --profile <name> to see details, or --profile list to see this summary.")
    print("Use --profile-save <name> to save current installed packs as a profile.")


def save_profile(name: str, as_json: bool = False, target: Path | None = None):
    """Save currently installed packs as a named custom profile."""
    if name in PROFILES:
        msg = f"'{name}' is a built-in profile name. Choose a different name."
        if as_json:
            print(json.dumps({"error": msg}, ensure_ascii=False, indent=2))
        else:
            print(f"Error: {msg}", file=sys.stderr)
        sys.exit(1)

    installed = _load_installed_registry(target)
    # Map installed pack names back to aliases
    pack_to_alias = {v: k for k, v in ALIAS_MAP.items() if k in ALIAS_MAP}
    aliases = sorted(
        set(pack_to_alias.get(pname, pname) for pname in installed.keys())
    )
    if not aliases:
        msg = "No packs installed. Install some packs first, then save a profile."
        if as_json:
            print(json.dumps({"error": msg}, ensure_ascii=False, indent=2))
        else:
            print(f"Error: {msg}", file=sys.stderr)
        sys.exit(1)

    data = _load_registry_data(target)
    data.setdefault("custom_profiles", {})[name] = aliases
    path = _save_registry_data(data, target)

    if as_json:
        print(json.dumps({"profile": name, "aliases": aliases, "saved_to": str(path)}, ensure_ascii=False, indent=2))
    else:
        print(f"✅ Profile '{name}' saved with packs: {', '.join(aliases)}")
        if path:
            print(f"   Stored in: {path}")


def delete_profile(name: str, as_json: bool = False, target: Path | None = None):
    """Delete a custom profile by name."""
    if name in PROFILES:
        msg = f"'{name}' is a built-in profile and cannot be deleted."
        if as_json:
            print(json.dumps({"error": msg}, ensure_ascii=False, indent=2))
        else:
            print(f"Error: {msg}", file=sys.stderr)
        sys.exit(1)

    data = _load_registry_data(target)
    custom = data.get("custom_profiles", {})
    if name not in custom:
        msg = f"Custom profile '{name}' not found."
        if as_json:
            print(json.dumps({"error": msg}, ensure_ascii=False, indent=2))
        else:
            print(f"Error: {msg}", file=sys.stderr)
        sys.exit(1)

    del custom[name]
    data["custom_profiles"] = custom
    path = _save_registry_data(data, target)

    if as_json:
        print(json.dumps({"deleted": name, "saved_to": str(path)}, ensure_ascii=False, indent=2))
    else:
        print(f"🗑️  Custom profile '{name}' deleted.")


def show_profile_recommends(name: str, as_json: bool = False, target: Path | None = None):
    """Show install command for all packs in a profile."""
    custom = _load_custom_profiles(target)
    all_profiles = {**PROFILES, **custom}

    if name not in all_profiles:
        print(f"Unknown profile '{name}'. Use --profile list to see available profiles.")
        sys.exit(1)

    aliases = all_profiles[name]
    installed = _load_installed_registry(target)
    installed_aliases = {PACK_TO_ALIAS.get(p, p) for p in installed.keys()}
    missing = [a for a in aliases if a not in installed_aliases]

    if as_json:
        print(json.dumps({"profile": name, "missing": missing, "installed": list(installed_aliases & set(aliases))}, ensure_ascii=False, indent=2))
        return

    if not missing:
        print(f"✅ All packs for profile '{name}' are already installed.")
        return

    packs_str = ",".join(missing)
    cmd = (
        "uv run https://raw.githubusercontent.com/kylecui/petfish.ai/master/install.py"
        f" --pack {packs_str}"
    )
    print(f"Profile '{name}' — missing packs: {', '.join(missing)}")
    print(f"\nInstall command:\n  {cmd}")


def show_triggers(as_json: bool = False):
    """Show all trigger keywords grouped by alias."""
    rows = [
        {"alias": alias, "triggers": TRIGGERS.get(alias, [])} for alias in ALIAS_MAP
    ]

    if as_json:
        print(json.dumps(rows, ensure_ascii=False, indent=2))
        return

    for row in rows:
        print(f"{row['alias']}: {', '.join(row['triggers'])}")


def suggest_packs(as_json: bool = False, target: Path | None = None):
    """Suggest known packs that are currently not installed."""
    catalog = build_catalog(target)
    installed = _load_installed_registry(target)
    suggestions = [
        {
            "alias": p["alias"],
            "pack": p["pack"],
            "install_scope": p["install_scope"],
            "description": p.get("description", ""),
        }
        for p in catalog
        if p["pack"] not in installed
    ]

    if as_json:
        print(json.dumps(suggestions, ensure_ascii=False, indent=2))
        return

    if not suggestions:
        print("No suggestions. All known packs are already installed.")
        return

    print("Suggested packs:")
    for row in suggestions:
        print(f"  {row['alias']} ({row['pack']})")


def show_counts(as_json: bool = False, target: Path | None = None):
    """Show aggregate pack/skill/command/agent counts."""
    catalog = build_catalog(target)
    result = {
        "packs": len(catalog),
        "skills": sum(int(p.get("skill_count", 0) or 0) for p in catalog),
        "commands": sum(int(p.get("command_count", 0) or 0) for p in catalog),
        "agents": sum(int(p.get("agent_count", 0) or 0) for p in catalog),
    }

    if as_json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    print(
        f"packs={result['packs']} skills={result['skills']} "
        f"cmds={result['commands']} agents={result['agents']}"
    )


def show_upgrade_command(as_json: bool = False):
    """Show one-line command to upgrade packs via install.py."""
    os_name = platform_mod.system()

    command = (
        "uv run https://raw.githubusercontent.com/kylecui/petfish.ai/master/install.py"
        " --pack all --force"
    )

    if as_json:
        print(
            json.dumps(
                {"os": os_name, "command": command}, ensure_ascii=False, indent=2
            )
        )
        return

    print("To upgrade all packs, run:")
    print(command)
    print()
    print(
        'To upgrade a specific pack: replace "all" with the pack alias (e.g., "deploy")'
    )


def show_uninstall_command(alias: str, as_json: bool = False):
    """Show command to uninstall a pack via install.py."""
    os_name = platform_mod.system()

    if alias == "all":
        msg = "Cannot uninstall all packs at once. Specify individual pack aliases."
        if as_json:
            print(json.dumps({"error": msg}, ensure_ascii=False, indent=2))
        else:
            print(f"Error: {msg}", file=sys.stderr)
        sys.exit(1)

    # Resolve alias to pack name to validate
    pack_name = ALIAS_MAP.get(alias, alias)
    known = pack_name in PACK_TO_ALIAS or alias in ALIAS_MAP
    if not known:
        msg = f"Unknown pack alias: '{alias}'. Use --list to see available packs."
        if as_json:
            print(json.dumps({"error": msg}, ensure_ascii=False, indent=2))
        else:
            print(f"Error: {msg}", file=sys.stderr)
        sys.exit(1)

    command = (
        "uv run https://raw.githubusercontent.com/kylecui/petfish.ai/master/install.py"
        f" --pack {alias} --uninstall"
    )

    if as_json:
        print(
            json.dumps(
                {"os": os_name, "alias": alias, "pack": pack_name, "command": command},
                ensure_ascii=False,
                indent=2,
            )
        )
        return

    print("To uninstall a pack, run:")
    print(command)
    print()
    print("Add --target <path> if the project is not in the current directory.")


def show_install_command(alias: str, as_json: bool = False):
    """Show install.py command for a pack alias."""
    os_name = platform_mod.system()

    pack_name = ALIAS_MAP.get(alias)
    if not pack_name:
        msg = f"Unknown pack alias: '{alias}'. Use --list to see available packs."
        if as_json:
            print(json.dumps({"error": msg}, ensure_ascii=False, indent=2))
        else:
            print(f"Error: {msg}", file=sys.stderr)
        sys.exit(1)

    command = (
        "uv run https://raw.githubusercontent.com/kylecui/petfish.ai/master/install.py"
        f" --pack {alias}"
    )

    if as_json:
        print(
            json.dumps(
                {"os": os_name, "alias": alias, "pack": pack_name, "command": command},
                ensure_ascii=False,
                indent=2,
            )
        )
        return

    print(f"To install '{alias}', run:")
    print(command)

    # Show soft-dependency hints from manifest
    catalog = build_catalog()
    for entry in catalog:
        if entry["alias"] == alias and entry.get("recommends"):
            rec_names = ", ".join(entry["recommends"])
            reason = entry.get("recommends_reason", "")
            print()
            print(f"💡 '{alias}' recommends also installing: {rec_names}")
            if reason:
                print(f"   {reason}")


def main():
    parser = argparse.ArgumentParser(description="PEtFiSh Skill Catalog Query")
    parser.add_argument(
        "subcommand",
        nargs="?",
        choices=["catalog", "triggers", "suggest", "counts"],
        help="Subcommand mode",
    )
    group = parser.add_mutually_exclusive_group(required=False)
    group.add_argument("--list", action="store_true", help="List all packs")
    group.add_argument("--search", type=str, help="Search by keyword")
    group.add_argument(
        "--profile",
        type=str,
        metavar="NAME",
        help="Show packs for a profile; use 'list' to list all profiles",
    )
    group.add_argument(
        "--profile-save",
        type=str,
        metavar="NAME",
        help="Save currently installed packs as a named custom profile",
    )
    group.add_argument(
        "--profile-delete",
        type=str,
        metavar="NAME",
        help="Delete a custom profile by name",
    )
    group.add_argument(
        "--profile-install",
        type=str,
        metavar="NAME",
        help="Show install command for missing packs in a profile",
    )
    group.add_argument(
        "--upgrade", action="store_true", help="Show command to upgrade packs"
    )
    group.add_argument(
        "--check-failures",
        type=str,
        metavar="TEXT",
        help="Scan text for failure signals and recommend packs",
    )
    group.add_argument(
        "--uninstall",
        type=str,
        metavar="ALIAS",
        help="Show command to uninstall a pack via local installer",
    )
    group.add_argument(
        "--install",
        type=str,
        metavar="ALIAS",
        help="Show remote install command for a pack alias",
    )
    parser.add_argument(
        "--target",
        type=str,
        help="Target project path for installed registry lookup (default: current working directory)",
    )
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    target = Path(args.target).resolve() if args.target else Path.cwd()
    if args.target and not target.exists():
        print(f"Target path does not exist: {target}", file=sys.stderr)
        sys.exit(1)

    if args.subcommand:
        if args.subcommand == "catalog":
            list_packs(as_json=args.json, target=target)
        elif args.subcommand == "triggers":
            show_triggers(as_json=args.json)
        elif args.subcommand == "suggest":
            suggest_packs(as_json=args.json, target=target)
        elif args.subcommand == "counts":
            show_counts(as_json=args.json, target=target)
        return

    check_failures_text = getattr(args, "check_failures", None)
    profile_save = getattr(args, "profile_save", None)
    profile_delete = getattr(args, "profile_delete", None)
    profile_install = getattr(args, "profile_install", None)

    if not (
        args.list
        or args.search
        or args.profile
        or profile_save
        or profile_delete
        or profile_install
        or args.upgrade
        or check_failures_text
        or args.uninstall
        or args.install
    ):
        parser.error(
            "one mode is required: subcommand or one of --list/--search/--profile/--profile-save/--profile-delete/--profile-install/--upgrade/--check-failures/--uninstall/--install"
        )

    if args.list:
        list_packs(as_json=args.json, target=target)
    elif args.search:
        search_packs(args.search, as_json=args.json, target=target)
    elif args.profile:
        show_profile(args.profile, as_json=args.json, target=target)
    elif profile_save:
        save_profile(profile_save, as_json=args.json, target=target)
    elif profile_delete:
        delete_profile(profile_delete, as_json=args.json, target=target)
    elif profile_install:
        show_profile_recommends(profile_install, as_json=args.json, target=target)
    elif args.upgrade:
        show_upgrade_command(as_json=args.json)
    elif check_failures_text:
        check_failures(check_failures_text, target=target, as_json=args.json)
    elif args.uninstall:
        show_uninstall_command(args.uninstall, as_json=args.json)
    elif args.install:
        show_install_command(args.install, as_json=args.json)


if __name__ == "__main__":
    main()
