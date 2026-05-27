#!/usr/bin/env python3
"""Trigger-eval harness for research-skill-pack.

Loads trigger-evals.json files from:
  - evals/trigger/*.json  (pack-level, all files)
  - .opencode/skills/*/evals/trigger-evals.json  (per-skill)

Reports which prompts matched/mismatched for deterministic CI execution.

Usage:
uv run packs/optional/research-skill-pack/scripts/run_trigger_evals.py
uv run packs/optional/research-skill-pack/scripts/run_trigger_evals.py --verbose
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


def _extract_trigger_phrases(description: str) -> list[str]:
    """Extract quoted trigger phrases from a skill description.

    Looks for phrases in double quotes like "研究目标", "research brief", etc.
    These are the canonical trigger phrases the skill declares.
    Handles slash-separated lists like "研究/research/调研" by splitting.
    """
    # Match both ASCII quotes and smart quotes (U+201C/U+201D, U+FF02)
    raw = re.findall(r'["\u201c\uff02]([^"\u201d\uff02]+)["\u201d\uff02]', description)
    phrases: list[str] = []
    for item in raw:
        # Split on "/" which is used to list alternative trigger phrases
        if "/" in item:
            phrases.extend(part.strip() for part in item.split("/") if part.strip())
        else:
            phrases.append(item)
    return phrases


def _simple_keyword_match(prompt: str, skill_name: str, skill_path: Path) -> bool:
    """Simple deterministic trigger matching based on skill description keywords.

    This does NOT replicate the full LLM-based skill matching. It checks whether
    the prompt contains trigger phrases or domain keywords declared in the skill's
    description.
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
        description = desc_match.group(1).strip()
    else:
        desc_match = re.search(r"description:\s*>\s*\n((?:\s+.*\n)*)", frontmatter)
        if desc_match:
            description = " ".join(
                line.strip() for line in desc_match.group(1).strip().splitlines()
            )
        else:
            description = ""

    description_lower = description.lower()

    # Check direct skill name reference
    if skill_name in prompt_lower:
        return True

    # Strategy 1: Check if prompt contains any quoted trigger phrase from description
    trigger_phrases = _extract_trigger_phrases(description_lower)
    for phrase in trigger_phrases:
        if phrase in prompt_lower:
            return True

    # Strategy 2: Check keyword overlap between prompt and description
    # Extract meaningful words (len > 1 for CJK, len > 3 for latin)
    prompt_tokens = set(re.findall(r"[\w\u4e00-\u9fff]+", prompt_lower))
    desc_tokens = set(re.findall(r"[\w\u4e00-\u9fff]+", description_lower))

    # Filter to meaningful words
    meaningful_prompt = {
        w
        for w in prompt_tokens
        if (len(w) > 1 and re.search(r"[\u4e00-\u9fff]", w)) or len(w) > 3
    }
    meaningful_desc = {
        w
        for w in desc_tokens
        if (len(w) > 1 and re.search(r"[\u4e00-\u9fff]", w)) or len(w) > 3
    }

    # Exclude generic stop words that appear in many descriptions
    stop_words = {
        "this",
        "skill",
        "when",
        "user",
        "says",
        "that",
        "with",
        "from",
        "have",
        "will",
        "been",
        "also",
        "into",
        "what",
        "about",
        "your",
        "need",
        "want",
        "help",
        "like",
        "make",
        "just",
        "should",
        "would",
        "could",
        "does",
        "asks",
        "uses",
        "used",
        "using",
        "provides",
        "triggers",
        "trigger",
        "based",
    }
    meaningful_prompt -= stop_words
    meaningful_desc -= stop_words

    overlap = meaningful_prompt & meaningful_desc

    # Require at least 2 overlapping meaningful keywords for a match
    if len(overlap) >= 2:
        return True

    # Strategy 3: CJK bigram overlap
    # CJK compound words share characters but aren't identical tokens.
    # E.g., "合规检查" and "合规评估" share the bigram "合规".
    cjk_pat = re.compile(r"[\u4e00-\u9fff]")
    prompt_cjk = "".join(cjk_pat.findall(prompt_lower))
    desc_cjk = "".join(cjk_pat.findall(description_lower))

    if len(prompt_cjk) >= 2 and len(desc_cjk) >= 2:
        prompt_bigrams = {prompt_cjk[i : i + 2] for i in range(len(prompt_cjk) - 1)}
        desc_bigrams = {desc_cjk[i : i + 2] for i in range(len(desc_cjk) - 1)}
        cjk_overlap = prompt_bigrams & desc_bigrams
        # Require 2+ bigram matches to avoid false positives from common
        # CJK bigrams like "分析", "研究", "设计" that appear everywhere.
        threshold = 2
        if len(cjk_overlap) >= threshold:
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
