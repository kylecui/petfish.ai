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
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path


def parse_frontmatter(content: str) -> dict:
    """Parse YAML frontmatter from SKILL.md content."""
    match = re.match(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
    if not match:
        return {}

    frontmatter_text = match.group(1)
    result = {}
    for line in frontmatter_text.split("\n"):
        line = line.strip()
        if ":" in line:
            key, _, value = line.partition(":")
            key = key.strip()
            value = value.strip().strip("\"'")
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

    return {
        "name": fm.get("name", skill_dir.name),
        "description": description,
        "triggers": list(set(triggers)),
        "path": str(skill_dir.relative_to(skill_dir.parent.parent)),
        "has_scripts": (skill_dir / "scripts").is_dir(),
        "has_references": (skill_dir / "references").is_dir(),
        "preview": extract_body_preview(content),
    }


def generate_index(skills_dir: Path) -> dict:
    """Generate the full skill index."""
    skills = []
    for skill_dir in sorted(skills_dir.iterdir()):
        if not skill_dir.is_dir():
            continue
        entry = index_skill(skill_dir)
        if entry:
            skills.append(entry)

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "skill_count": len(skills),
        "skills": skills,
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
