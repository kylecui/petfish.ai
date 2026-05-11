# /// script
# requires-python = ">=3.11"
# ///
"""Generate trigger eval datasets for all skills across all packs.

Walks all packs under packs/, finds SKILL.md files, and generates
eval JSON files using the same logic as evaluate_triggers.py's
auto_generate_tests(). Output format is the per-skill schema:

  {"skill": "name", "should_trigger": [...], "should_not_trigger": [...]}

Usage:
  uv run scripts/gen_trigger_evals.py [--output-dir evals/trigger] [--force]
  uv run scripts/gen_trigger_evals.py --pack course
  uv run scripts/gen_trigger_evals.py --dry-run
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Constants (mirrored from evaluate_triggers.py)
# ---------------------------------------------------------------------------

STOPWORDS = frozenset(
    {
        "a",
        "an",
        "the",
        "is",
        "are",
        "was",
        "were",
        "be",
        "been",
        "being",
        "have",
        "has",
        "had",
        "do",
        "does",
        "did",
        "will",
        "would",
        "shall",
        "should",
        "may",
        "might",
        "must",
        "can",
        "could",
        "to",
        "of",
        "in",
        "for",
        "on",
        "with",
        "at",
        "by",
        "from",
        "as",
        "into",
        "through",
        "during",
        "before",
        "after",
        "above",
        "below",
        "between",
        "under",
        "about",
        "against",
        "along",
        "among",
        "around",
        "because",
        "but",
        "if",
        "or",
        "nor",
        "not",
        "so",
        "yet",
        "both",
        "each",
        "few",
        "more",
        "most",
        "other",
        "some",
        "such",
        "than",
        "too",
        "very",
        "and",
        "that",
        "this",
        "these",
        "those",
        "it",
        "its",
        "i",
        "me",
        "my",
        "we",
        "our",
        "you",
        "your",
        "he",
        "she",
        "they",
        "them",
        "what",
        "which",
        "who",
        "when",
        "where",
        "how",
        "all",
        "any",
        "use",
        "user",
        "skill",
        "when",
        "says",
        "trigger",
        "also",
        "using",
        "used",
        "need",
        "needs",
        "want",
        "wants",
        "like",
    }
)

_CJK_RE = re.compile(r"[\u4e00-\u9fff\u3400-\u4dbf\uf900-\ufaff]")
_TRIGGER_SECTION_RE = re.compile(
    r"(?:^|\n)#+\s*(?:触发场景|Trigger|Activation|When to (?:Use|Trigger)|Use this skill when)"
    r"(.*?)(?=\n#+\s|\Z)",
    re.DOTALL | re.IGNORECASE,
)
_BULLET_RE = re.compile(r"^\s*[-*]\s+(.+)", re.MULTILINE)
_QUOTED_RE = re.compile(r'["""]([^"""]+)["""]')

NEGATIVE_QUERY_POOL = [
    "帮我写个函数",
    "fix the bug in auth.py",
    "deploy this to production",
    "create a new React component",
    "run the tests",
    "refactor this class",
    "帮我润色这段话",
    "what is the weather today",
    "translate this to Japanese",
    "write a unit test for login",
    "optimize this SQL query",
    "set up CI/CD pipeline",
    "帮我画一个流程图",
    "review this pull request",
    "add dark mode to the app",
    "explain how git rebase works",
    "帮我写个README",
    "configure nginx reverse proxy",
    "debug memory leak in Node.js",
    "create a REST API endpoint",
    "help me with CSS flexbox",
    "write a Dockerfile",
    "帮我整理一下目录结构",
    "format this JSON file",
]


# ---------------------------------------------------------------------------
# Frontmatter parser (simplified from evaluate_triggers.py)
# ---------------------------------------------------------------------------


def extract_frontmatter(text: str) -> tuple[dict, str]:
    """Extract YAML-like frontmatter from SKILL.md."""
    lines = text.split("\n")
    if not lines or lines[0].strip() != "---":
        return {}, text

    end_idx = -1
    for i, line in enumerate(lines[1:], 1):
        if line.strip() == "---":
            end_idx = i
            break
    if end_idx < 0:
        return {}, text

    meta: dict = {}
    current_key = ""
    current_val = ""
    for line in lines[1:end_idx]:
        if ":" in line and not line.startswith(" ") and not line.startswith("\t"):
            if current_key:
                meta[current_key] = current_val.strip()
            key, _, val = line.partition(":")
            current_key = key.strip()
            current_val = val.strip()
        else:
            current_val += " " + line.strip()
    if current_key:
        meta[current_key] = current_val.strip()

    body = "\n".join(lines[end_idx + 1 :])
    return meta, body


# ---------------------------------------------------------------------------
# Keyword / trigger extraction (mirrored from evaluate_triggers.py)
# ---------------------------------------------------------------------------


def extract_keywords(text: str) -> set[str]:
    """Extract keywords from text, handling CJK via bigrams."""
    tokens: set[str] = set()
    text_lower = text.lower()
    # ASCII tokens
    for tok in re.findall(r"[a-z0-9_-]+", text_lower):
        if tok not in STOPWORDS and len(tok) > 1:
            tokens.add(tok)
    # CJK bigrams
    cjk_chars = _CJK_RE.findall(text)
    for i in range(len(cjk_chars) - 1):
        tokens.add(cjk_chars[i] + cjk_chars[i + 1])
    return tokens


def _is_doc_snippet(phrase: str) -> bool:
    """Filter out backtick phrases, long strings, 'Best for/Use when' patterns."""
    if "`" in phrase:
        return True
    if len(phrase) > 120:
        return True
    if re.match(r"^(Best for|Use when|Returns|Supports|Filter)", phrase, re.IGNORECASE):
        return True
    return False


def extract_trigger_phrases(body_text: str) -> list[str]:
    """Extract trigger phrases from SKILL.md body text."""
    phrases: list[str] = []

    # From trigger sections
    for match in _TRIGGER_SECTION_RE.finditer(body_text):
        section = match.group(1)
        for bullet in _BULLET_RE.findall(section):
            cleaned = bullet.strip().rstrip("。.;；")
            if cleaned and not _is_doc_snippet(cleaned):
                phrases.append(cleaned)

    # Quoted strings from full text
    for match in _QUOTED_RE.findall(body_text):
        cleaned = match.strip()
        if 2 < len(cleaned) < 80 and not _is_doc_snippet(cleaned):
            if cleaned not in phrases:
                phrases.append(cleaned)

    return phrases


# ---------------------------------------------------------------------------
# Test generation (mirrored from evaluate_triggers.py auto_generate_tests)
# ---------------------------------------------------------------------------


def build_positive_queries(
    name: str,
    desc_keywords: set[str],
    trigger_phrases: list[str],
) -> list[str]:
    """Build positive test queries (up to 8)."""
    queries: list[str] = []

    # Direct trigger phrases (up to 4)
    for phrase in trigger_phrases[:4]:
        if phrase not in queries:
            queries.append(phrase)

    # Template expansions using name/keywords
    templates = [
        f"Help me with {name.replace('-', ' ')}",
        f"I need {name.replace('-', ' ')}",
    ]
    # Pick top keywords for template
    keyword_list = sorted(
        desc_keywords - {name.replace("-", "")}, key=len, reverse=True
    )
    for kw in keyword_list[:2]:
        templates.append(f"{kw} help needed")

    for tmpl in templates:
        if len(queries) >= 8:
            break
        if tmpl not in queries:
            queries.append(tmpl)

    # Name-based fallback
    if len(queries) < 4:
        fallback = name.replace("-", " ")
        if fallback not in queries:
            queries.append(fallback)

    return queries[:8]


def build_negative_queries(desc_keywords: set[str]) -> list[str]:
    """Build negative test queries (up to 8) from pool, filtered by no keyword overlap."""
    queries: list[str] = []
    for candidate in NEGATIVE_QUERY_POOL:
        candidate_kw = extract_keywords(candidate)
        overlap = candidate_kw & desc_keywords
        if not overlap:
            queries.append(candidate)
            if len(queries) >= 8:
                break
    # Fallback if not enough
    if len(queries) < 4:
        for candidate in NEGATIVE_QUERY_POOL:
            if candidate not in queries:
                queries.append(candidate)
                if len(queries) >= 8:
                    break
    return queries[:8]


def auto_generate_tests(name: str, description: str, body: str) -> dict:
    """Generate eval test set for a single skill."""
    desc_keywords = extract_keywords(description)
    trigger_phrases = extract_trigger_phrases(body)

    positive = build_positive_queries(name, desc_keywords, trigger_phrases)
    negative = build_negative_queries(desc_keywords)

    return {
        "skill": name,
        "should_trigger": positive,
        "should_not_trigger": negative,
    }


# ---------------------------------------------------------------------------
# Pack / skill discovery
# ---------------------------------------------------------------------------


def find_all_skills(packs_dir: Path, pack_filter: str | None = None) -> list[dict]:
    """Find all SKILL.md files across packs. Returns list of {pack, name, path, skill_dir}."""
    skills = []
    for pack_dir in sorted(packs_dir.iterdir()):
        if not pack_dir.is_dir():
            continue
        if pack_filter and pack_filter not in pack_dir.name:
            continue

        # Skills can be at .opencode/skills/*/SKILL.md
        skills_root = pack_dir / ".opencode" / "skills"
        if not skills_root.is_dir():
            continue

        for skill_dir in sorted(skills_root.iterdir()):
            if not skill_dir.is_dir():
                continue
            skill_file = skill_dir / "SKILL.md"
            if skill_file.is_file():
                skills.append(
                    {
                        "pack": pack_dir.name,
                        "name": skill_dir.name,
                        "path": str(skill_file),
                        "skill_dir": str(skill_dir),
                    }
                )
    return skills


def load_skill_description(skill_file: Path) -> tuple[str, str, str]:
    """Load skill name, description, and body from SKILL.md.

    Returns (name, description, body).
    """
    text = skill_file.read_text(encoding="utf-8")
    meta, body = extract_frontmatter(text)
    name = meta.get("name", skill_file.parent.name)
    description = meta.get("description", "")
    return name, description, body


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate trigger eval datasets for all packs"
    )
    parser.add_argument(
        "--output-dir",
        default="evals/trigger",
        help="Output directory for eval JSON files (default: evals/trigger)",
    )
    parser.add_argument(
        "--pack",
        default=None,
        help="Filter to a specific pack (substring match on directory name)",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing eval files",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be generated without writing files",
    )
    parser.add_argument(
        "--packs-dir",
        default="packs",
        help="Path to packs directory (default: packs)",
    )
    args = parser.parse_args()

    packs_dir = Path(args.packs_dir).resolve()
    if not packs_dir.is_dir():
        print(f"Packs directory not found: {packs_dir}", file=sys.stderr)
        return 2

    output_dir = Path(args.output_dir).resolve()

    skills = find_all_skills(packs_dir, args.pack)
    if not skills:
        print("No skills found.", file=sys.stderr)
        return 1

    print(f"Found {len(skills)} skills across packs")

    generated = 0
    skipped = 0
    errors = 0

    # Group by pack for organized output
    by_pack: dict[str, list[dict]] = {}
    for s in skills:
        by_pack.setdefault(s["pack"], []).append(s)

    for pack_name, pack_skills in sorted(by_pack.items()):
        pack_output_dir = output_dir / pack_name
        if not args.dry_run:
            pack_output_dir.mkdir(parents=True, exist_ok=True)

        for skill_info in pack_skills:
            out_file = pack_output_dir / f"{skill_info['name']}.json"

            if out_file.exists() and not args.force:
                skipped += 1
                continue

            try:
                name, description, body = load_skill_description(
                    Path(skill_info["path"])
                )
                if not description:
                    print(f"  SKIP {skill_info['name']}: no description")
                    skipped += 1
                    continue

                test_data = auto_generate_tests(name, description, body)

                if args.dry_run:
                    pos = len(test_data["should_trigger"])
                    neg = len(test_data["should_not_trigger"])
                    print(
                        f"  {skill_info['name']}: {pos} positive, {neg} negative → {out_file}"
                    )
                else:
                    out_file.write_text(
                        json.dumps(test_data, indent=2, ensure_ascii=False) + "\n",
                        encoding="utf-8",
                    )
                generated += 1

            except Exception as exc:
                print(f"  ERROR {skill_info['name']}: {exc}", file=sys.stderr)
                errors += 1

    print(f"\nSummary: {generated} generated, {skipped} skipped, {errors} errors")
    if args.dry_run:
        print("(dry-run: no files written)")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
