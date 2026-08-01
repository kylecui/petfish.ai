#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["pyyaml>=6.0"]
# ///
"""Generate skill and pack reference pages for MkDocs from SKILL.md frontmatter and pack-manifest.json.

Outputs:
  docs-site/docs/en/reference/packs/<pack-alias>.md   — one per pack
  docs-site/docs/zh/reference/packs/<pack-alias>.md   — zh mirror
  docs-site/docs/en/reference/packs/index.md           — pack catalog
  docs-site/docs/zh/reference/packs/index.md           — zh mirror
  docs-site/docs/en/reference/skills/<skill-name>.md   — one per skill
  docs-site/docs/zh/reference/skills/<skill-name>.md   — zh mirror
  docs-site/docs/en/reference/skills/index.md           — skill catalog
  docs-site/docs/zh/reference/skills/index.md           — zh mirror

Usage:
  uv run docs-site/scripts/generate_skill_reference.py [--packs-dir packs/] [--docs-dir docs-site/docs/]
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


# ---------------------------------------------------------------------------
# YAML frontmatter parser (stdlib-only, no PyYAML dependency at runtime)
# ---------------------------------------------------------------------------


def parse_frontmatter(text: str) -> dict[str, str]:
    """Extract YAML frontmatter key-value pairs from a SKILL.md file.

    Handles simple scalar fields only (name, description, compatibility, license).
    Does NOT attempt full YAML parsing — avoids PyYAML dependency.
    """
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end == -1:
        return {}
    block = text[3:end].strip()
    result: dict[str, str] = {}
    for line in block.splitlines():
        m = re.match(r"^(\w[\w-]*):\s*(.+)$", line)
        if m:
            key = m.group(1).strip()
            val = m.group(2).strip().strip("\"'")
            result[key] = val
    return result


def extract_body_sections(text: str) -> str:
    """Return everything after the closing --- of frontmatter."""
    if not text.startswith("---"):
        return text
    end = text.find("\n---", 3)
    if end == -1:
        return text
    return text[end + 4 :].strip()


# ---------------------------------------------------------------------------
# Pack alias mapping
# ---------------------------------------------------------------------------

PACK_ALIAS: dict[str, str] = {
    "project-initializer-skill": "init",
    "petfish-companion-skill": "companion",
    "petfish-toolchain-skill": "toolchain",
    "opencode-course-skills-pack": "course",
    "opencode-skill-pack-testcases-usage-docs": "testdocs",
    "repo-deploy-ops-skill-pack": "deploy",
    "petfish-style-skill": "petfish",
    "opencode-ppt-skills": "ppt",
    "judgment-calibration-pack": "calibrate",
    "fish-trail": "context",
    "trustskills-governance-pack": "trust",
    "research-skill-pack": "research",
    "fish-reflection-pack": "reflect",
    "drawio-radar-chart": "drawio",
    "typst-pdf-builder": "typst",
    "series-style-governor-pack": "style-governor",
    "doc-reader-skill": "doc-reader",
}


# ---------------------------------------------------------------------------
# Generators
# ---------------------------------------------------------------------------


def load_packs(packs_dir: Path) -> list[dict[str, Any]]:
    """Load all pack-manifest.json files and enrich with skill frontmatter."""
    packs: list[dict[str, Any]] = []
    for manifest_path in sorted(packs_dir.glob("**/pack-manifest.json")):
        pack_dir = manifest_path.parent
        with open(manifest_path, encoding="utf-8") as f:
            manifest = json.load(f)

        pack_name = manifest["name"]
        alias = PACK_ALIAS.get(pack_name, pack_name)
        manifest["_alias"] = alias
        manifest["_dir"] = pack_dir

        # Discover SKILL.md files
        skills_data: list[dict[str, Any]] = []
        skills_root = pack_dir / ".opencode" / "skills"
        if skills_root.is_dir():
            for skill_dir in sorted(skills_root.iterdir()):
                skill_md = skill_dir / "SKILL.md"
                if skill_md.is_file():
                    raw = skill_md.read_text(encoding="utf-8")
                    fm = parse_frontmatter(raw)
                    body = extract_body_sections(raw)
                    skills_data.append(
                        {
                            "name": fm.get("name", skill_dir.name),
                            "description": fm.get("description", ""),
                            "compatibility": fm.get("compatibility", ""),
                            "license": fm.get("license", ""),
                            "body": body,
                            "pack_alias": alias,
                            "pack_name": manifest.get("description", pack_name),
                        }
                    )

        manifest["_skills"] = skills_data
        packs.append(manifest)

    return packs


def write_file(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def gen_skill_page_en(skill: dict[str, Any]) -> str:
    lines = [
        f"# {skill['name']}",
        "",
        f"> Pack: **{skill['pack_alias']}**",
        "",
    ]
    if skill["description"]:
        lines.append(f"{skill['description']}")
        lines.append("")
    if skill["compatibility"]:
        lines.append(f"**Compatibility:** {skill['compatibility']}")
        lines.append("")
    # Include truncated body (first 80 lines max for reference)
    body_lines = skill["body"].splitlines()
    if body_lines:
        lines.append("---")
        lines.append("")
        lines.extend(body_lines[:80])
        if len(body_lines) > 80:
            lines.append("")
            lines.append(f"*... ({len(body_lines) - 80} more lines in full SKILL.md)*")
    lines.append("")
    return "\n".join(lines)


def gen_skill_page_zh(skill: dict[str, Any]) -> str:
    lines = [
        f"# {skill['name']}",
        "",
        f"> 所属包: **{skill['pack_alias']}**",
        "",
    ]
    if skill["description"]:
        lines.append(f"{skill['description']}")
        lines.append("")
    if skill["compatibility"]:
        lines.append(f"**兼容性:** {skill['compatibility']}")
        lines.append("")
    body_lines = skill["body"].splitlines()
    if body_lines:
        lines.append("---")
        lines.append("")
        lines.extend(body_lines[:80])
        if len(body_lines) > 80:
            lines.append("")
            lines.append(f"*... (完整 SKILL.md 中还有 {len(body_lines) - 80} 行)*")
    lines.append("")
    return "\n".join(lines)


def gen_pack_page_en(pack: dict[str, Any]) -> str:
    alias = pack["_alias"]
    lines = [
        f"# {alias}",
        "",
        f"**{pack.get('description', '')}**",
        "",
        f"| Field | Value |",
        f"|---|---|",
        f"| Pack name | `{pack['name']}` |",
        f"| Alias | `{alias}` |",
        f"| Version | {pack.get('version', 'N/A')} |",
        f"| Skills | {pack.get('skill_count', 0)} |",
        f"| Commands | {pack.get('command_count', 0)} |",
        f"| Agents | {pack.get('agent_count', 0)} |",
        f"| Compatibility | {pack.get('compatibility', 'N/A')} |",
        "",
        "## Skills",
        "",
    ]
    for s in pack["_skills"]:
        desc_short = (
            s["description"][:120] + "..."
            if len(s["description"]) > 120
            else s["description"]
        )
        lines.append(f"- [`{s['name']}`](../skills/{s['name']}.md) — {desc_short}")
    lines.append("")

    install_cmd = f"uv run https://raw.githubusercontent.com/kylecui/petfish.ai/master/install.py --pack {alias} --detect"

    lines.extend(
        [
            "## Install",
            "",
            "```bash",
            f"{install_cmd}",
            "```",
            "",
        ]
    )
    return "\n".join(lines)


def gen_pack_page_zh(pack: dict[str, Any]) -> str:
    alias = pack["_alias"]
    lines = [
        f"# {alias}",
        "",
        f"**{pack.get('description', '')}**",
        "",
        f"| 字段 | 值 |",
        f"|---|---|",
        f"| 包名 | `{pack['name']}` |",
        f"| 别名 | `{alias}` |",
        f"| 版本 | {pack.get('version', 'N/A')} |",
        f"| 技能数 | {pack.get('skill_count', 0)} |",
        f"| 命令数 | {pack.get('command_count', 0)} |",
        f"| 代理数 | {pack.get('agent_count', 0)} |",
        f"| 兼容性 | {pack.get('compatibility', 'N/A')} |",
        "",
        "## 技能列表",
        "",
    ]
    for s in pack["_skills"]:
        desc_short = (
            s["description"][:120] + "..."
            if len(s["description"]) > 120
            else s["description"]
        )
        lines.append(f"- [`{s['name']}`](../skills/{s['name']}.md) — {desc_short}")
    lines.append("")

    install_cmd = f"uv run https://raw.githubusercontent.com/kylecui/petfish.ai/master/install.py --pack {alias} --detect"

    lines.extend(
        [
            "## 安装",
            "",
            "```bash",
            f"{install_cmd}",
            "```",
            "",
        ]
    )
    return "\n".join(lines)


def gen_pack_index_en(packs: list[dict[str, Any]]) -> str:
    lines = [
        "# Packs",
        "",
        f"PEtFiSh ships **{len(packs)} skill packs**.",
        "",
        "| Alias | Description | Skills | Version |",
        "|---|---|---|---|",
    ]
    for p in packs:
        alias = p["_alias"]
        desc = p.get("description", "")[:80]
        lines.append(
            f"| [`{alias}`]({alias}.md) | {desc} | {p.get('skill_count', 0)} | {p.get('version', '')} |"
        )
    lines.append("")
    return "\n".join(lines)


def gen_pack_index_zh(packs: list[dict[str, Any]]) -> str:
    lines = [
        "# 技能包",
        "",
        f"PEtFiSh 提供 **{len(packs)} 个技能包**。",
        "",
        "| 别名 | 描述 | 技能数 | 版本 |",
        "|---|---|---|---|",
    ]
    for p in packs:
        alias = p["_alias"]
        desc = p.get("description", "")[:80]
        lines.append(
            f"| [`{alias}`]({alias}.md) | {desc} | {p.get('skill_count', 0)} | {p.get('version', '')} |"
        )
    lines.append("")
    return "\n".join(lines)


def gen_skill_index_en(all_skills: list[dict[str, Any]]) -> str:
    lines = [
        "# Skills",
        "",
        f"PEtFiSh includes **{len(all_skills)} skills** across all packs.",
        "",
        "| Skill | Pack | Description |",
        "|---|---|---|",
    ]
    for s in all_skills:
        desc = (
            s["description"][:100] + "..."
            if len(s["description"]) > 100
            else s["description"]
        )
        # Escape pipe characters in description
        desc = desc.replace("|", "\\|")
        lines.append(
            f"| [`{s['name']}`]({s['name']}.md) | {s['pack_alias']} | {desc} |"
        )
    lines.append("")
    return "\n".join(lines)


def gen_skill_index_zh(all_skills: list[dict[str, Any]]) -> str:
    lines = [
        "# 技能",
        "",
        f"PEtFiSh 共包含 **{len(all_skills)} 个技能**。",
        "",
        "| 技能 | 所属包 | 描述 |",
        "|---|---|---|",
    ]
    for s in all_skills:
        desc = (
            s["description"][:100] + "..."
            if len(s["description"]) > 100
            else s["description"]
        )
        desc = desc.replace("|", "\\|")
        lines.append(
            f"| [`{s['name']}`]({s['name']}.md) | {s['pack_alias']} | {desc} |"
        )
    lines.append("")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate skill reference pages for MkDocs"
    )
    parser.add_argument("--packs-dir", default="packs", help="Path to packs/ directory")
    parser.add_argument(
        "--docs-dir", default="docs-site/docs", help="Path to docs-site/docs/ directory"
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Print file list without writing"
    )
    args = parser.parse_args()

    packs_dir = Path(args.packs_dir)
    docs_dir = Path(args.docs_dir)

    if not packs_dir.is_dir():
        print(f"ERROR: packs directory not found: {packs_dir}", file=sys.stderr)
        sys.exit(1)

    packs = load_packs(packs_dir)
    all_skills: list[dict[str, Any]] = []
    for p in packs:
        all_skills.extend(p["_skills"])

    print(f"Found {len(packs)} packs, {len(all_skills)} skills")

    files_to_write: list[tuple[Path, str]] = []

    # Pack pages
    for p in packs:
        alias = p["_alias"]
        files_to_write.append(
            (
                docs_dir / "en" / "reference" / "packs" / f"{alias}.md",
                gen_pack_page_en(p),
            )
        )
        files_to_write.append(
            (
                docs_dir / "zh" / "reference" / "packs" / f"{alias}.md",
                gen_pack_page_zh(p),
            )
        )

    # Pack indexes
    files_to_write.append(
        (docs_dir / "en" / "reference" / "packs" / "index.md", gen_pack_index_en(packs))
    )
    files_to_write.append(
        (docs_dir / "zh" / "reference" / "packs" / "index.md", gen_pack_index_zh(packs))
    )

    # Skill pages
    for s in all_skills:
        files_to_write.append(
            (
                docs_dir / "en" / "reference" / "skills" / f"{s['name']}.md",
                gen_skill_page_en(s),
            )
        )
        files_to_write.append(
            (
                docs_dir / "zh" / "reference" / "skills" / f"{s['name']}.md",
                gen_skill_page_zh(s),
            )
        )

    # Skill indexes
    files_to_write.append(
        (
            docs_dir / "en" / "reference" / "skills" / "index.md",
            gen_skill_index_en(all_skills),
        )
    )
    files_to_write.append(
        (
            docs_dir / "zh" / "reference" / "skills" / "index.md",
            gen_skill_index_zh(all_skills),
        )
    )

    if args.dry_run:
        for path, _ in files_to_write:
            print(f"  {path}")
        print(f"\nTotal: {len(files_to_write)} files")
        return

    for path, content in files_to_write:
        write_file(path, content)

    print(f"Generated {len(files_to_write)} files")
    print(f"  Pack pages: {len(packs) * 2} (en+zh)")
    print(f"  Pack indexes: 2")
    print(f"  Skill pages: {len(all_skills) * 2} (en+zh)")
    print(f"  Skill indexes: 2")


if __name__ == "__main__":
    main()
