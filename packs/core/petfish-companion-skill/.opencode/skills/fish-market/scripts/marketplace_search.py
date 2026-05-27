#!/usr/bin/env python3
"""
PEtFiSh Marketplace Connector — Unified skill/MCP search across multiple sources.

Searches: PEtFiSh local catalog → PEtFiSh Market (community) → Glama → Smithery → SkillKit → anthropics/skills → GitHub

Usage:
  uv run marketplace_search.py --query "pdf processing"
  uv run marketplace_search.py --query "database" --source glama,smithery
  uv run marketplace_search.py --query "deploy" --limit 5 --json
  uv run marketplace_search.py --query "react" --type skill
"""

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

# ---------------------------------------------------------------------------
# Local catalog (PEtFiSh core packs only)
# Optional packs (course, deploy, petfish, ppt, testdocs, calibrate, context,
# trust, research, reflect) are resolved via petfish-market index — not listed
# here to avoid stale hardcoded metadata.
# ---------------------------------------------------------------------------

LOCAL_CATALOG = [
    {
        "name": "companion",
        "pack": "petfish-companion-skill",
        "description": "常驻伙伴skill",
        "type": "skill",
    },
    {
        "name": "init",
        "pack": "project-initializer-skill",
        "description": "项目初始化器",
        "type": "skill",
    },
    {
        "name": "toolchain",
        "pack": "petfish-toolchain-skill",
        "description": "Skill lifecycle pipeline — author, lint, audit, gate, optimize, eval",
        "type": "skill",
    },
    {
        "name": "context",
        "pack": "fish-trail",
        "description": "话题治理与上下文隔离",
        "type": "skill",
    },
]

TIMEOUT = 10  # seconds per API call


def _http_get(url: str, headers: dict | None = None) -> dict | list | None:
    """Simple HTTP GET returning parsed JSON, or None on failure."""
    req = urllib.request.Request(url, headers=headers or {})
    req.add_header("User-Agent", "PEtFiSh-Marketplace/0.2")
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except (
        urllib.error.URLError,
        urllib.error.HTTPError,
        OSError,
        json.JSONDecodeError,
        TimeoutError,
    ):
        return None


# ---------------------------------------------------------------------------
# Source: PEtFiSh local
# ---------------------------------------------------------------------------


def search_local(query: str, limit: int) -> list[dict]:
    q = query.lower()
    results = []
    for item in LOCAL_CATALOG:
        searchable = f"{item['name']} {item['pack']} {item['description']}".lower()
        if q in searchable:
            results.append(
                {
                    "source": "petfish",
                    "name": item["name"],
                    "description": item["description"],
                    "type": "skill",
                    "install": f"./install.ps1 -Pack {item['name']}  |  ./install.sh --pack {item['name']}",
                    "url": "",
                }
            )
    return results[:limit]


# ---------------------------------------------------------------------------
# Source: PEtFiSh Community Registry (curated packs in main repo)
# ---------------------------------------------------------------------------

COMMUNITY_REGISTRY_URL = (
    "https://raw.githubusercontent.com/kylecui/petfish.ai/master/community-packs.json"
)


def search_community_registry(query: str, limit: int) -> list[dict]:
    """Search the curated community-packs.json registry in the main repo."""
    data = _http_get(COMMUNITY_REGISTRY_URL)
    if not data or "packs" not in data:
        return []

    q = query.lower()
    results = []
    for pack in data["packs"]:
        searchable = " ".join(
            str(pack.get(f, "")) for f in ("name", "description", "author", "repo")
        ).lower()
        if q in searchable:
            repo = pack.get("repo", "")
            results.append(
                {
                    "source": "community",
                    "name": pack.get("name", ""),
                    "description": pack.get("description", ""),
                    "type": "skill",
                    "author": pack.get("author", ""),
                    "verified": pack.get("verified", False),
                    "min_version": pack.get("min_version", ""),
                    "url": f"https://github.com/{repo}" if repo else "",
                    "install": f"remote-install.sh --community {repo}" if repo else "",
                }
            )
    return results[:limit]


# ---------------------------------------------------------------------------
# Source: PEtFiSh Market (community skills)
# ---------------------------------------------------------------------------

PETFISH_MARKET_INDEX_URL = (
    "https://raw.githubusercontent.com/kylecui/petfish-market/main/index.json"
)


def search_petfish_market(query: str, limit: int) -> list[dict]:
    """Search the PEtFiSh Market community skill index."""
    data = _http_get(PETFISH_MARKET_INDEX_URL)
    if not data or "skills" not in data:
        return []

    q = query.lower()
    results = []
    for skill in data["skills"]:
        searchable = " ".join(
            str(skill.get(f, ""))
            for f in ("name", "display_name", "description", "author")
        ).lower()
        if q in searchable:
            repo = skill.get("repo", "")
            ref = skill.get("ref", "")
            results.append(
                {
                    "source": "petfish-market",
                    "name": skill.get("display_name", skill.get("name", "")),
                    "description": skill.get("description", ""),
                    "type": "skill",
                    "author": skill.get("author", ""),
                    "version": skill.get("version", ""),
                    "license": skill.get("license", ""),
                    "platforms": skill.get("platforms", []),
                    "url": f"https://github.com/{repo}" if repo else "",
                    "install": f"community/{skill.get('name', '')}",
                }
            )
    return results[:limit]


# ---------------------------------------------------------------------------
# Source: Glama (free, no auth)
# ---------------------------------------------------------------------------


def search_glama(query: str, limit: int) -> list[dict]:
    url = f"https://glama.ai/api/mcp/v1/servers?query={urllib.request.quote(query)}&limit={limit}"
    data = _http_get(url)
    if not data or "servers" not in data:
        return []

    results = []
    for srv in data["servers"][:limit]:
        results.append(
            {
                "source": "glama",
                "name": srv.get("name", ""),
                "description": srv.get("description", ""),
                "type": "mcp",
                "namespace": srv.get("namespace", ""),
                "license": (srv.get("spdxLicense") or {}).get("name", ""),
                "url": srv.get(
                    "url", f"https://glama.ai/mcp/servers/{srv.get('id', '')}"
                ),
                "install": f"MCP config: see glama.ai/mcp/servers/{srv.get('namespace', '')}/{srv.get('slug', '')}",
            }
        )
    return results


# ---------------------------------------------------------------------------
# Source: Smithery (requires SMITHERY_API_KEY)
# ---------------------------------------------------------------------------


def search_smithery(query: str, limit: int) -> list[dict]:
    api_key = os.environ.get("SMITHERY_API_KEY", "")
    if not api_key:
        return []

    url = f"https://registry.smithery.ai/servers?q={urllib.request.quote(query)}&pageSize={limit}"
    data = _http_get(url, headers={"Authorization": f"Bearer {api_key}"})
    if not data or "servers" not in data:
        return []

    results = []
    for srv in data["servers"][:limit]:
        qname = srv.get("qualifiedName", "")
        results.append(
            {
                "source": "smithery",
                "name": srv.get("displayName", qname),
                "description": srv.get("description", ""),
                "type": "mcp",
                "verified": srv.get("verified", False),
                "use_count": srv.get("useCount", 0),
                "url": f"https://smithery.ai/server/{qname}",
                "install": f"smithery mcp add {qname}",
            }
        )
    return results


# ---------------------------------------------------------------------------
# Source: SkillKit (local REST server at :3737)
# ---------------------------------------------------------------------------


def search_skillkit(query: str, limit: int) -> list[dict]:
    url = f"http://localhost:3737/search?q={urllib.request.quote(query)}&limit={limit}"
    data = _http_get(url)
    if not data or "skills" not in data:
        return []

    results = []
    for sk in data["skills"][:limit]:
        results.append(
            {
                "source": "skillkit",
                "name": sk.get("name", ""),
                "description": sk.get("description", ""),
                "type": "skill",
                "score": sk.get("score", 0),
                "tags": sk.get("tags", []),
                "install": f"skillkit install {sk.get('source', '')} --skills={sk.get('name', '')}",
                "url": "",
            }
        )
    return results


# ---------------------------------------------------------------------------
# Source: anthropics/skills (GitHub)
# ---------------------------------------------------------------------------


def search_anthropics(query: str, limit: int) -> list[dict]:
    url = "https://api.github.com/repos/anthropics/skills/contents/skills"
    headers = {}
    gh_token = os.environ.get("GITHUB_TOKEN", "")
    if gh_token:
        headers["Authorization"] = f"Bearer {gh_token}"

    data = _http_get(url, headers=headers)
    if not data or not isinstance(data, list):
        return []

    q = query.lower()
    results = []
    for item in data:
        if item.get("type") != "dir":
            continue
        name = item.get("name", "")
        if q in name.lower():
            results.append(
                {
                    "source": "anthropics",
                    "name": name,
                    "description": f"Official Anthropic skill: {name}",
                    "type": "skill",
                    "url": f"https://github.com/anthropics/skills/tree/main/skills/{name}",
                    "install": f"skillkit install anthropics/skills --skills={name}",
                }
            )
    return results[:limit]


# ---------------------------------------------------------------------------
# Source: GitHub search (SKILL.md files)
# ---------------------------------------------------------------------------


def search_github(query: str, limit: int) -> list[dict]:
    url = f"https://api.github.com/search/repositories?q={urllib.request.quote(query)}+topic:ai-skills&sort=stars&per_page={limit}"
    headers = {}
    gh_token = os.environ.get("GITHUB_TOKEN", "")
    if gh_token:
        headers["Authorization"] = f"Bearer {gh_token}"

    data = _http_get(url, headers=headers)
    if not data or "items" not in data:
        return []

    results = []
    for repo in data["items"][:limit]:
        results.append(
            {
                "source": "github",
                "name": repo.get("name", ""),
                "description": repo.get("description", ""),
                "type": "skill",
                "stars": repo.get("stargazers_count", 0),
                "url": repo.get("html_url", ""),
                "install": f"git clone {repo.get('clone_url', '')}",
            }
        )
    return results


# ---------------------------------------------------------------------------
# Aggregator
# ---------------------------------------------------------------------------

ALL_SOURCES = {
    "petfish": search_local,
    "petfish-market": search_petfish_market,
    "community": search_community_registry,
    "glama": search_glama,
    "smithery": search_smithery,
    "skillkit": search_skillkit,
    "anthropics": search_anthropics,
    "github": search_github,
}

SOURCE_LABELS = {
    "petfish": "🐟 PEtFiSh (本地)",
    "community": "🐟 PEtFiSh Community (注册表)",
    "petfish-market": "🐟 PEtFiSh Market (社区)",
    "glama": "🌐 Glama (MCP)",
    "smithery": "🔧 Smithery (MCP)",
    "skillkit": "📦 SkillKit",
    "anthropics": "🏛️ anthropics/skills",
    "github": "🐙 GitHub",
}


def search_all(query: str, sources: list[str], limit: int, type_filter: str) -> dict:
    """Search across all requested sources and return aggregated results."""
    all_results = {}
    errors = []

    for src in sources:
        fn = ALL_SOURCES.get(src)
        if not fn:
            errors.append(f"Unknown source: {src}")
            continue
        try:
            results = fn(query, limit)
            if type_filter != "all":
                results = [r for r in results if r.get("type") == type_filter]
            all_results[src] = results
        except Exception as e:
            errors.append(f"{src}: {e}")
            all_results[src] = []

    return {"query": query, "results": all_results, "errors": errors}


def print_text(data: dict):
    """Pretty-print search results."""
    query = data["query"]
    results = data["results"]
    errors = data["errors"]

    total = sum(len(v) for v in results.values())
    print(f'\n  ><(((^>  Marketplace Search: "{query}"')
    print(f"  Found {total} result(s) across {len(results)} source(s)\n")

    idx = 1
    for src, items in results.items():
        label = SOURCE_LABELS.get(src, src)
        print(f"  {label}")
        if not items:
            print("    (no matches)\n")
            continue
        for item in items:
            name = item.get("name", "?")
            desc = item.get("description", "")[:80]
            type_badge = "MCP" if item.get("type") == "mcp" else "Skill"
            extras = []
            if "stars" in item:
                extras.append(f"★ {item['stars']}")
            if "use_count" in item:
                extras.append(f"{item['use_count']} uses")
            if "verified" in item and item["verified"]:
                extras.append("✓ verified")
            if "license" in item and item["license"]:
                extras.append(item["license"])
            if "score" in item:
                extras.append(f"score: {item['score']}")
            extra_str = f" | {' | '.join(extras)}" if extras else ""
            print(f"    {idx}. [{type_badge}] {name}{extra_str}")
            print(f"       {desc}")
            if item.get("install"):
                print(f"       Install: {item['install']}")
            print()
            idx += 1

    if errors:
        print("  ⚠️ Errors:")
        for e in errors:
            print(f"    - {e}")
        print()


def main():
    parser = argparse.ArgumentParser(description="PEtFiSh Marketplace Search")
    parser.add_argument("--query", "-q", required=True, help="Search keyword")
    parser.add_argument(
        "--source",
        "-s",
        type=str,
        default="",
        help="Comma-separated sources: petfish,community,petfish-market,glama,smithery,skillkit,anthropics,github (default: all)",
    )
    parser.add_argument(
        "--limit", "-l", type=int, default=5, help="Max results per source (default: 5)"
    )
    parser.add_argument(
        "--type",
        "-t",
        choices=["skill", "mcp", "all"],
        default="all",
        help="Filter by type",
    )
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    sources = (
        [s.strip() for s in args.source.split(",") if s.strip()]
        if args.source
        else list(ALL_SOURCES.keys())
    )

    data = search_all(args.query, sources, args.limit, args.type)

    if args.json:
        print(json.dumps(data, ensure_ascii=False, indent=2))
    else:
        print_text(data)


if __name__ == "__main__":
    main()
