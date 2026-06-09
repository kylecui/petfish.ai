"""Alignment checker for online-gpt.

This stdlib-only checker helps keep online-gpt close to core PEtFiSh.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Iterable, List

ROOT = Path(__file__).resolve().parents[2]
ONLINE = ROOT / "online-gpt"

EXPECTED_PACKS = {
    "init",
    "companion",
    "petfish",
    "toolchain",
    "course",
    "testdocs",
    "deploy",
    "ppt",
    "calibrate",
    "context",
    "trust",
    "research",
    "reflect",
    "doc-reader",
}

EXPECTED_PLATFORMS = {
    "opencode",
    "claude",
    "codex",
    "cursor",
    "copilot",
    "windsurf",
    "antigravity",
    "universal",
}

DRIFT_TERMS = [
    "replacement Companion Gateway",
    "GPT-native pack semantics",
    "online-only pack lifecycle",
    "new official pack",
]


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def markdown_files(root: Path) -> Iterable[Path]:
    yield from sorted(root.rglob("*.md"))


def check_required_files() -> List[str]:
    errors = []
    required = [
        ROOT / "README.md",
        ROOT / "AGENTS.md",
        ROOT / "docs" / "companion-gateway.md",
        ROOT / "platforms.json",
        ONLINE / "ALIGNMENT.md",
        ONLINE / "SOURCE-OF-TRUTH.md",
    ]
    for path in required:
        if not path.exists():
            errors.append(f"missing required file: {path.relative_to(ROOT)}")
    return errors


def check_drift_terms() -> List[str]:
    errors = []
    for path in markdown_files(ONLINE):
        text = read_text(path)
        for phrase in DRIFT_TERMS:
            if phrase in text and path.name not in {"ALIGNMENT.md", "SOURCE-OF-TRUTH.md"}:
                errors.append(f"drift term in {path.relative_to(ROOT)}: {phrase}")
    return errors


def check_pack_aliases() -> List[str]:
    errors = []
    pack_index = read_text(ONLINE / "knowledge" / "03-pack-index.md")
    aliases = set(re.findall(r"`([a-z][a-z0-9-]+)`", pack_index))
    unknown = sorted(alias for alias in aliases if alias not in EXPECTED_PACKS and alias not in EXPECTED_PLATFORMS)
    for alias in unknown:
        errors.append(f"unknown alias in knowledge/03-pack-index.md: {alias}")
    return errors


def check_platforms() -> List[str]:
    errors = []
    text = read_text(ONLINE / "knowledge" / "04-platform-adapters.md")
    missing = sorted(platform for platform in EXPECTED_PLATFORMS if platform not in text)
    for platform in missing:
        errors.append(f"platform missing from knowledge/04-platform-adapters.md: {platform}")
    return errors


def main() -> int:
    errors: List[str] = []
    for check in [check_required_files, check_drift_terms, check_pack_aliases, check_platforms]:
        errors.extend(check())

    if errors:
        print("online-gpt alignment check failed:")
        for error in errors:
            print(f"  - {error}")
        return 2

    print("online-gpt alignment check passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
