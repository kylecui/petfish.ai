#!/usr/bin/env python3
"""Trigger-eval harness for research-skill-pack.

Loads trigger-evals.json files from:
  - evals/trigger/*.json  (pack-level, all files)
  - .opencode/skills/*/evals/trigger-evals.json  (per-skill)

Reports which prompts matched/mismatched for deterministic CI execution.

Usage:
    uv run packs/research-skill-pack/scripts/run_trigger_evals.py
    uv run packs/research-skill-pack/scripts/run_trigger_evals.py --verbose
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

PACK_ROOT = Path(__file__).resolve().parents[1]


def _load_skill_triggers(skill_path: Path) -> dict[str, list[str]] | None:
    """Load trigger keywords from a SKILL.md description field."""
    skill_md = skill_path / "SKILL.md"
    if not skill_md.exists():
        return None

    text = skill_md.read_text(encoding="utf-8")
    # Extract description from frontmatter
    fm_match = re.search(r"^---\s*\n(.*?\n)---", text, re.DOTALL)
    if not fm_match:
        return None

    frontmatter = fm_match.group(1)
    desc_match = re.search(
        r"description:\s*['\"]?(.*?)['\"]?\s*$", frontmatter, re.MULTILINE
    )
    if not desc_match:
        # Try multi-line description
        desc_match = re.search(r"description:\s*>\s*\n((?:\s+.*\n)*)", frontmatter)
        if not desc_match:
            return None
        description = " ".join(
            line.strip() for line in desc_match.group(1).strip().splitlines()
        )
    else:
        description = desc_match.group(1).strip()

    return {"description": [description], "skill_name": [skill_path.name]}


def _simple_keyword_match(prompt: str, skill_name: str, skill_path: Path) -> bool:
    """Simple deterministic trigger matching based on skill description keywords.

    This does NOT replicate the full LLM-based skill matching. It checks whether
    the prompt contains keywords that a reasonable skill matcher would use.
    """
    skill_md = skill_path / "SKILL.md"
    if not skill_md.exists():
        return False

    text = skill_md.read_text(encoding="utf-8")
    prompt_lower = prompt.lower()

    # Extract description from frontmatter
    fm_match = re.search(r"^---\s*\n(.*?\n)---", text, re.DOTALL)
    if not fm_match:
        return False

    frontmatter = fm_match.group(1)

    # Get description text
    desc_match = re.search(
        r"description:\s*['\"]?(.*?)['\"]?\s*$", frontmatter, re.MULTILINE
    )
    if desc_match:
        description = desc_match.group(1).strip().lower()
    else:
        desc_match = re.search(r"description:\s*>\s*\n((?:\s+.*\n)*)", frontmatter)
        if desc_match:
            description = " ".join(
                line.strip() for line in desc_match.group(1).strip().splitlines()
            ).lower()
        else:
            description = ""

    # Extract trigger phrases from description (quoted phrases and key terms)
    # Simple heuristic: check if prompt contains the skill name or key domain words
    skill_words = skill_name.replace("research-", "").replace("-", " ").split()

    # Check direct skill name reference
    if skill_name in prompt_lower:
        return True

    # Check domain keywords from description
    domain_keywords = set()
    for word in description.split():
        cleaned = word.strip(".,;:\"'()[]")
        if len(cleaned) > 3:
            domain_keywords.add(cleaned)

    # A match requires at least one skill-specific keyword
    skill_specific = {
        "research",
        "brief",
        "source",
        "note",
        "evidence",
        "synthesis",
        "report",
        "quality",
        "review",
        "literature",
        "insight",
        "router",
        "研究",
        "调研",
        "文献",
        "综述",
        "证据",
        "摘录",
        "笔记",
        "报告",
        "竞品",
        "分析",
        "论文",
        "routing",
    }

    prompt_words = set(re.findall(r"[\w\u4e00-\u9fff]+", prompt_lower))
    matches = prompt_words & skill_specific

    if not matches:
        return False

    # Check if the matching keywords are relevant to THIS skill
    for kw in skill_words:
        if kw in prompt_lower:
            return True

    return False


def _load_eval_files() -> list[dict[str, Any]]:
    """Discover and load all trigger-eval JSON files."""
    eval_entries: list[dict[str, Any]] = []

    # Pack-level evals — glob all JSON files under evals/trigger/
    trigger_dir = PACK_ROOT / "evals" / "trigger"
    if trigger_dir.is_dir():
        for eval_file in sorted(trigger_dir.glob("*.json")):
            data = json.loads(eval_file.read_text(encoding="utf-8"))
            for entry in data.get("evals", []):
                entry["_source"] = str(eval_file.relative_to(PACK_ROOT))
                eval_entries.append(entry)

    # Per-skill evals
    skills_dir = PACK_ROOT / ".opencode" / "skills"
    for skill_dir in sorted(skills_dir.iterdir()):
        trigger_file = skill_dir / "evals" / "trigger-evals.json"
        if trigger_file.exists():
            data = json.loads(trigger_file.read_text(encoding="utf-8"))
            entry = {
                "id": f"{skill_dir.name}-trigger-eval",
                "skill": data.get("skill", skill_dir.name),
                "type": "trigger",
                "should_trigger": data.get("should_trigger", []),
                "should_not_trigger": data.get("should_not_trigger", []),
                "_source": str(trigger_file.relative_to(PACK_ROOT)),
            }
            eval_entries.append(entry)

    return eval_entries


def run_evals(verbose: bool = False) -> dict[str, Any]:
    """Run all trigger evals and return results."""
    eval_entries = _load_eval_files()

    if not eval_entries:
        return {"status": "fail", "error": "No eval files found", "results": []}

    results: list[dict[str, Any]] = []
    total_checks = 0
    total_pass = 0
    total_fail = 0

    skills_dir = PACK_ROOT / ".opencode" / "skills"

    for entry in eval_entries:
        skill_name = entry.get("skill", "<unknown>")
        skill_path = skills_dir / skill_name
        eval_id = entry.get("id", skill_name)

        false_negatives: list[str] = []
        false_positives: list[str] = []

        # Test should_trigger prompts
        for prompt in entry.get("should_trigger", []):
            total_checks += 1
            if _simple_keyword_match(prompt, skill_name, skill_path):
                total_pass += 1
            else:
                total_fail += 1
                false_negatives.append(prompt)

        # Test should_not_trigger prompts
        for prompt in entry.get("should_not_trigger", []):
            total_checks += 1
            if not _simple_keyword_match(prompt, skill_name, skill_path):
                total_pass += 1
            else:
                total_fail += 1
                false_positives.append(prompt)

        result = {
            "eval_id": eval_id,
            "skill": skill_name,
            "source": entry.get("_source", ""),
            "should_trigger_total": len(entry.get("should_trigger", [])),
            "should_not_trigger_total": len(entry.get("should_not_trigger", [])),
            "false_negatives": false_negatives,
            "false_positives": false_positives,
            "pass": not false_negatives and not false_positives,
        }
        results.append(result)

    status = "pass" if total_fail == 0 else "fail"
    summary = {
        "status": status,
        "total_evals": len(eval_entries),
        "total_checks": total_checks,
        "passed": total_pass,
        "failed": total_fail,
        "pass_rate": f"{(total_pass / total_checks * 100):.1f}%"
        if total_checks > 0
        else "N/A",
        "results": results,
    }

    return summary


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run trigger evaluation suite for research-skill-pack."
    )
    parser.add_argument(
        "--verbose", action="store_true", help="Show per-prompt results."
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    summary = run_evals(verbose=args.verbose)
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0 if summary["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
