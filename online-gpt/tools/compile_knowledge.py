"""Knowledge compiler scaffold for online-gpt."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List

ROOT = Path(__file__).resolve().parents[2]
ONLINE = ROOT / "online-gpt"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def load_platforms() -> List[Dict[str, str]]:
    path = ROOT / "platforms.json"
    if not path.exists():
        return []
    data = json.loads(read(path))
    if isinstance(data, dict) and isinstance(data.get("platforms"), dict):
        # platforms.json: {"platforms": {"opencode": {...}, "claude": {...}}}
        rows = []
        for key, value in data["platforms"].items():
            row = dict(value)
            row.setdefault("name", key)
            rows.append(row)
        return rows
    if isinstance(data, dict) and isinstance(data.get("platforms"), list):
        return data["platforms"]
    if isinstance(data, dict):
        rows = []
        for key, value in data.items():
            if isinstance(value, dict):
                row = dict(value)
                row.setdefault("name", key)
                rows.append(row)
        return rows
    return []


def render_platform_reference() -> str:
    platforms = load_platforms()
    lines = [
        "# Platform Adapter Reference",
        "",
        "SYNC_REQUIRED: source=platforms.json",
        "",
        "| Platform | Skills directory | Instructions file |",
        "|---|---|---|",
    ]
    for item in platforms:
        name = item.get("name") or item.get("platform") or "unknown"
        # Platform data may be nested under "project" sub-object
        proj = item.get("project", item)
        skills_dir = proj.get("skills_dir") or proj.get("skillsDirectory") or proj.get("skills_directory") or item.get("skills_dir") or ""
        instructions = proj.get("instructions_file") or proj.get("instructionsFile") or proj.get("instructions") or item.get("instructions_file") or ""
        lines.append(f"| `{name}` | `{skills_dir}` | `{instructions}` |")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    target = ONLINE / "knowledge" / "04-platform-adapters.generated.md"
    target.write_text(render_platform_reference(), encoding="utf-8")
    print(f"wrote {target.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
