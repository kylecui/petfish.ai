#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = []
# ///
"""Analyze and improve skill descriptions for better trigger accuracy."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path

SPECIFIC_VERBS = {
    "analyze",
    "audit",
    "build",
    "check",
    "compare",
    "create",
    "debug",
    "deploy",
    "design",
    "detect",
    "extract",
    "fix",
    "generate",
    "improve",
    "install",
    "lint",
    "migrate",
    "optimize",
    "publish",
    "refactor",
    "review",
    "rewrite",
    "run",
    "scan",
    "score",
    "search",
    "test",
    "track",
    "validate",
    "verify",
    "write",
}

VAGUE_PHRASES = {
    "help with",
    "helps with",
    "assist",
    "assists",
    "support",
    "supports",
    "manage",
    "manages",
    "handle",
    "handles",
    "work on",
    "deal with",
    "various",
    "general",
    "miscellaneous",
}

BOUNDARY_PATTERNS = (
    r"\bonly\b",
    r"\bnot for\b",
    r"\bnot when\b",
    r"\bdoes not\b",
    r"\bdo not\b",
    r"\bdon't use\b",
    r"\bnever\b",
    r"\bexcept\b",
    r"\brather than\b",
    r"\binstead of\b",
    r"\bwithout\b",
)

TRIGGER_CUES = (
    "use this skill when",
    "when the user",
    "asks to",
    "ask to",
    "trigger phrases",
    "triggered when",
    "activate",
    "activates",
    "if the user",
)

STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "by",
    "for",
    "from",
    "if",
    "in",
    "into",
    "is",
    "it",
    "its",
    "of",
    "on",
    "or",
    "that",
    "the",
    "this",
    "to",
    "use",
    "user",
    "when",
    "with",
    "you",
    "your",
    "ask",
    "asks",
    "skill",
    "skills",
}


@dataclass
class SkillInfo:
    name: str
    description: str
    path: Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Analyze a skill description and suggest improvements."
    )
    parser.add_argument(
        "--path", required=True, help="Path to the target skill directory"
    )
    parser.add_argument(
        "--siblings",
        help="Directory containing sibling skills for overlap analysis",
    )
    parser.add_argument("--json", action="store_true", help="Output JSON report")
    parser.add_argument(
        "--suggest",
        action="store_true",
        help="Include a suggested replacement description",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Show detailed analysis sections",
    )
    return parser.parse_args()


def normalize_scalar(value: str) -> str:
    value = value.strip()
    if not value:
        return ""
    if (value.startswith('"') and value.endswith('"')) or (
        value.startswith("'") and value.endswith("'")
    ):
        return value[1:-1]
    return value


def extract_frontmatter(text: str) -> tuple[dict, str]:
    clean = text.lstrip("\ufeff")
    match = re.match(r"^---\s*\r?\n(.*?)\r?\n---\s*(?:\r?\n|$)", clean, re.S)
    if not match:
        return {}, clean

    block = match.group(1)
    body = clean[match.end() :]
    lines = block.splitlines()
    data: dict = {}
    stack: list[tuple[int, dict]] = [(0, data)]
    index = 0

    while index < len(lines):
        raw_line = lines[index]
        if not raw_line.strip() or raw_line.lstrip().startswith("#"):
            index += 1
            continue

        indent = len(raw_line) - len(raw_line.lstrip(" "))
        stripped = raw_line.strip()

        while len(stack) > 1 and indent < stack[-1][0]:
            stack.pop()

        if ":" not in stripped:
            index += 1
            continue

        key, raw_value = stripped.split(":", 1)
        key = key.strip()
        raw_value = raw_value.strip()
        parent = stack[-1][1]

        if raw_value in {">", "|"}:
            index += 1
            block_indent = None
            collected: list[str] = []
            while index < len(lines):
                next_line = lines[index]
                if not next_line.strip():
                    collected.append("")
                    index += 1
                    continue

                next_indent = len(next_line) - len(next_line.lstrip(" "))
                if next_indent <= indent and block_indent is None:
                    break
                if block_indent is None:
                    block_indent = next_indent
                if next_indent < block_indent:
                    break
                collected.append(next_line[block_indent:])
                index += 1

            if raw_value == ">":
                value = " ".join(part.strip() for part in collected if part.strip())
            else:
                value = "\n".join(collected).rstrip()
            parent[key] = value
            continue

        if raw_value == "":
            nested: dict = {}
            parent[key] = nested
            stack.append((indent + 2, nested))
            index += 1
            continue

        parent[key] = normalize_scalar(raw_value)
        index += 1

    return data, body


def load_skill(skill_dir: Path) -> SkillInfo:
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.is_file():
        raise FileNotFoundError(f"Missing SKILL.md in {skill_dir}")

    text = skill_md.read_text(encoding="utf-8")
    frontmatter, _ = extract_frontmatter(text)
    name = str(frontmatter.get("name", skill_dir.name)).strip() or skill_dir.name
    description = str(frontmatter.get("description", "")).strip()
    if not description:
        raise ValueError(f"Missing frontmatter description in {skill_md}")
    return SkillInfo(name=name, description=description, path=skill_dir)


def tokenize(text: str) -> list[str]:
    return re.findall(r"[a-z][a-z0-9-]{1,}", text.lower())


def keyword_set(text: str) -> set[str]:
    return {
        token for token in tokenize(text) if len(token) >= 4 and token not in STOPWORDS
    }


def extract_request_phrases(description: str) -> list[str]:
    phrases: list[str] = []
    lowered = description.lower()
    cue_patterns = [
        r"(?:when the user|if the user) asks to\s+([^.;]+)",
        r"use this skill when\s+([^.;]+)",
    ]

    for pattern in cue_patterns:
        for match in re.finditer(pattern, lowered):
            chunk = match.group(1)
            chunk = re.sub(r"^the request includes ideas like\s+", "", chunk)
            parts = re.split(r",|\bor\b|\band\b", chunk)
            for part in parts:
                cleaned = part.strip(" .:;\"'")
                cleaned = re.sub(r"^(to|for)\s+", "", cleaned)
                if len(cleaned) >= 4:
                    phrases.append(cleaned)

    unique: list[str] = []
    seen = set()
    for phrase in phrases:
        if phrase not in seen:
            seen.add(phrase)
            unique.append(phrase)
    return unique


def extract_trigger_phrases(description: str) -> dict:
    lowered = description.lower()
    tokens = tokenize(description)
    verbs = sorted({token for token in tokens if token in SPECIFIC_VERBS})

    keywords = [token for token in tokens if len(token) >= 4 and token not in STOPWORDS]
    nouns = sorted(dict.fromkeys(keywords))[:15]
    request_phrases = extract_request_phrases(description)

    patterns: list[str] = []
    for match in re.findall(r'"([^"]{3,80})"', description):
        patterns.append(match.strip())
    for match in re.findall(r"'([^']{3,80})'", description):
        patterns.append(match.strip())
    patterns.extend(request_phrases)
    for sentence in re.split(r"(?<=[.!?])\s+", description):
        sentence_clean = sentence.strip()
        if not sentence_clean:
            continue
        sentence_lower = sentence_clean.lower()
        if any(cue in sentence_lower for cue in TRIGGER_CUES):
            patterns.append(sentence_clean)

    unique_patterns = []
    seen = set()
    for pattern in patterns:
        key = pattern.lower()
        if key not in seen:
            seen.add(key)
            unique_patterns.append(pattern)

    actionable_hits = sum(1 for cue in TRIGGER_CUES if cue in lowered) + len(verbs)
    density = actionable_hits / max(len(tokens), 1)

    return {
        "verbs": verbs,
        "nouns": nouns,
        "request_phrases": request_phrases,
        "action_patterns": unique_patterns,
        "density": round(density, 3),
    }


def analyze_length(description: str) -> dict:
    count = len(description)
    if count < 100:
        status = "too_short"
        note = "Under-specified; likely missing trigger detail or boundaries."
    elif count <= 500:
        status = "ideal"
        note = "Dense enough for routing without becoming noisy."
    elif count <= 800:
        status = "acceptable"
        note = "Longer than ideal, but still likely usable if each clause adds signal."
    else:
        status = "too_long"
        note = "Likely unfocused; trim broad or repetitive clauses."
    return {"characters": count, "status": status, "note": note}


def boundary_check(description: str) -> dict:
    lowered = description.lower()
    hits = []
    for pattern in BOUNDARY_PATTERNS:
        match = re.search(pattern, lowered)
        if match:
            hits.append(match.group(0))
    return {
        "has_boundary": bool(hits),
        "markers": hits,
    }


def specificity_score(
    description: str, triggers: dict, boundary: dict, length_info: dict
) -> dict:
    lowered = description.lower()
    score = 55

    vague_hits = [phrase for phrase in VAGUE_PHRASES if phrase in lowered]
    score -= min(len(vague_hits) * 9, 30)

    specific_verb_count = len(triggers["verbs"])
    score += min(specific_verb_count * 5, 25)

    pattern_count = len(triggers["action_patterns"])
    if pattern_count:
        score += min(pattern_count * 4, 12)
    else:
        score -= 10

    if any(cue in lowered for cue in TRIGGER_CUES):
        score += 8
    else:
        score -= 12

    if boundary["has_boundary"]:
        score += 10
    else:
        score -= 10

    if length_info["status"] == "too_short":
        score -= 15
    elif length_info["status"] == "too_long":
        score -= 12
    elif length_info["status"] == "ideal":
        score += 6

    score = max(0, min(100, score))

    summary = "high"
    if score < 45:
        summary = "low"
    elif score < 75:
        summary = "medium"

    return {
        "score": score,
        "summary": summary,
        "vague_hits": vague_hits,
    }


def analyze_overlap(target: SkillInfo, siblings_dir: Path | None) -> list[dict]:
    if siblings_dir is None:
        return []
    if not siblings_dir.is_dir():
        raise FileNotFoundError(f"Siblings directory not found: {siblings_dir}")

    target_keywords = keyword_set(target.description)
    results: list[dict] = []
    for entry in siblings_dir.iterdir():
        if not entry.is_dir() or entry.resolve() == target.path.resolve():
            continue
        skill_md = entry / "SKILL.md"
        if not skill_md.is_file():
            continue
        try:
            sibling = load_skill(entry)
        except (OSError, ValueError, FileNotFoundError):
            continue

        sibling_keywords = keyword_set(sibling.description)
        shared = sorted(target_keywords & sibling_keywords)
        overlap_pct = round((len(shared) / max(len(target_keywords), 1)) * 100, 1)
        jaccard = round(
            (len(shared) / max(len(target_keywords | sibling_keywords), 1)) * 100, 1
        )
        results.append(
            {
                "name": sibling.name,
                "overlap_pct": overlap_pct,
                "jaccard_pct": jaccard,
                "shared_keywords": shared[:15],
            }
        )

    results.sort(key=lambda item: item["overlap_pct"], reverse=True)
    return results


def build_suggestions(
    skill: SkillInfo,
    triggers: dict,
    length_info: dict,
    boundary: dict,
    specificity: dict,
    overlaps: list[dict],
) -> list[str]:
    suggestions: list[str] = []

    if length_info["status"] == "too_short":
        suggestions.append(
            "Add one sentence that names concrete user requests and another that defines the activation boundary."
        )
    elif length_info["status"] == "too_long":
        suggestions.append(
            "Trim broad or repetitive clauses so the description stays focused on one routing job."
        )

    if specificity["vague_hits"]:
        suggestions.append(
            "Replace vague phrases like "
            + ", ".join(sorted(specificity["vague_hits"]))
            + " with concrete verbs such as analyze, lint, deploy, generate, or audit."
        )

    if not triggers["request_phrases"]:
        suggestions.append(
            "Add realistic request-shaped trigger phrases, for example: 'when the user asks to ...'."
        )

    if len(triggers["verbs"]) < 2:
        suggestions.append(
            "Increase actionable verb density so the matcher sees a clear job instead of general assistance."
        )

    if not boundary["has_boundary"]:
        suggestions.append(
            "Add a boundary clause using markers like only, not, or rather than to reduce false positives."
        )

    high_overlap = [item for item in overlaps if item["overlap_pct"] >= 35]
    if high_overlap:
        names = ", ".join(item["name"] for item in high_overlap[:3])
        suggestions.append(
            f"Reduce sibling overlap with {names} by naming the primary use case and excluding adjacent workflows."
        )

    if not suggestions:
        suggestions.append(
            "Description is already reasonably targeted; consider only light wording cleanup or stronger boundary phrasing."
        )

    return suggestions


def first_sentence(text: str) -> str:
    parts = re.split(r"(?<=[.!?])\s+", text.strip())
    return parts[0].strip() if parts and parts[0].strip() else text.strip()


def build_suggested_description(
    skill: SkillInfo,
    triggers: dict,
    overlaps: list[dict],
) -> str:
    purpose = first_sentence(skill.description)
    if len(purpose) > 180:
        purpose = purpose[:177].rstrip() + "..."

    quoted = []
    if triggers["request_phrases"]:
        quoted.extend(triggers["request_phrases"][:4])
    for pattern in triggers["action_patterns"]:
        cleaned = pattern.strip().strip(".")
        if (
            4 <= len(cleaned) <= 40
            and cleaned.lower() == cleaned
            and cleaned not in quoted
        ):
            quoted.append(cleaned)
    if not quoted:
        fallback = []
        for verb in triggers["verbs"][:3]:
            noun = next((item for item in triggers["nouns"] if item != verb), "request")
            fallback.append(f"{verb} {noun}")
        quoted = fallback or [f"improve {skill.name}"]

    trigger_clause = ", ".join(f'"{item}"' for item in quoted[:4])

    boundary_clause = "Only use it when the request is primarily about description matching quality, not general skill authoring or full-skill QA."
    if overlaps:
        adjacent = [item["name"] for item in overlaps if item["overlap_pct"] >= 35][:2]
        if adjacent:
            boundary_clause = (
                "Only use it when the request is primarily about description matching quality, not adjacent workflows handled by "
                + " and ".join(adjacent)
                + "."
            )

    suggested = (
        f"{purpose} Use this skill when the user asks to {trigger_clause}. "
        f"{boundary_clause}"
    )
    return re.sub(r"\s+", " ", suggested).strip()


def relative_display(path: Path) -> str:
    try:
        return os.path.relpath(path, Path.cwd())
    except ValueError:
        return str(path)


def format_report(report: dict, verbose: bool, include_suggestion: bool) -> str:
    lines = [
        "Skill Description Optimization Report",
        "=" * 36,
        f"Skill: {report['skill']['name']}",
        f"Path:  {report['skill']['path']}",
        "",
        "Current description:",
        report["skill"]["description"],
        "",
        f"Length: {report['length']['characters']} chars [{report['length']['status']}],",
        f"Trigger density: {report['triggers']['density']}",
        f"Specificity: {report['specificity']['score']}/100 ({report['specificity']['summary']})",
        f"Boundary check: {'yes' if report['boundary']['has_boundary'] else 'no'}",
    ]

    if verbose:
        lines.extend(
            [
                "",
                "Extracted trigger signals:",
                f"- verbs: {', '.join(report['triggers']['verbs']) or '(none)'}",
                f"- nouns: {', '.join(report['triggers']['nouns']) or '(none)'}",
                f"- request phrases: {', '.join(report['triggers']['request_phrases']) or '(none)'}",
                "- action patterns:",
            ]
        )
        patterns = report["triggers"]["action_patterns"] or ["(none)"]
        lines.extend(f"  - {pattern}" for pattern in patterns)

        lines.extend(
            [
                "",
                "Suggestions:",
            ]
        )
        lines.extend(f"- {item}" for item in report["suggestions"])
    else:
        lines.append("")
        lines.append("Suggestions:")
        lines.extend(f"- {item}" for item in report["suggestions"])

    if report["overlap"]:
        lines.extend(["", "Sibling overlap:"])
        for item in report["overlap"]:
            shared = ", ".join(item["shared_keywords"][:6]) or "-"
            lines.append(
                f"- {item['name']}: {item['overlap_pct']}% overlap, {item['jaccard_pct']}% jaccard | shared: {shared}"
            )

    if include_suggestion and report.get("suggested_description"):
        lines.extend(
            [
                "",
                "Suggested description:",
                report["suggested_description"],
            ]
        )

    return "\n".join(lines)


def main() -> int:
    args = parse_args()

    try:
        target_dir = Path(args.path).expanduser().resolve()
        if not target_dir.is_dir():
            raise FileNotFoundError(f"Target skill directory not found: {target_dir}")

        siblings_dir = None
        if args.siblings:
            siblings_dir = Path(args.siblings).expanduser().resolve()

        skill = load_skill(target_dir)
        triggers = extract_trigger_phrases(skill.description)
        length_info = analyze_length(skill.description)
        boundary = boundary_check(skill.description)
        specificity = specificity_score(
            skill.description, triggers, boundary, length_info
        )
        overlap = analyze_overlap(skill, siblings_dir)
        suggestions = build_suggestions(
            skill,
            triggers,
            length_info,
            boundary,
            specificity,
            overlap,
        )
        suggested_description = (
            build_suggested_description(skill, triggers, overlap)
            if args.suggest
            else None
        )

        report = {
            "skill": {
                "name": skill.name,
                "path": relative_display(skill.path),
                "description": skill.description,
            },
            "length": length_info,
            "triggers": triggers,
            "specificity": specificity,
            "boundary": boundary,
            "overlap": overlap,
            "suggestions": suggestions,
        }
        if suggested_description:
            report["suggested_description"] = suggested_description

        if args.json:
            print(json.dumps(report, ensure_ascii=False, indent=2))
        else:
            print(
                format_report(
                    report, verbose=args.verbose, include_suggestion=args.suggest
                )
            )

        return 0
    except (FileNotFoundError, ValueError, OSError) as exc:
        message = {"error": str(exc)} if args.json else f"Error: {exc}"
        if args.json:
            print(json.dumps(message, ensure_ascii=False, indent=2), file=sys.stderr)
        else:
            print(message, file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
