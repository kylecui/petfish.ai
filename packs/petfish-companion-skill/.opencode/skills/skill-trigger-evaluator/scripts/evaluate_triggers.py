#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = []
# ///
"""Evaluate skill trigger accuracy with keyword-overlap heuristics."""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path

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
    "helps",
    "how",
    "i",
    "if",
    "in",
    "into",
    "is",
    "it",
    "me",
    "my",
    "of",
    "on",
    "or",
    "should",
    "silent",
    "so",
    "stay",
    "that",
    "the",
    "their",
    "them",
    "then",
    "this",
    "to",
    "use",
    "user",
    "users",
    "when",
    "whether",
    "with",
    "you",
    "your",
}

NEGATIVE_QUERY_POOL = [
    "Deploy this service to production.",
    "Write unit tests for this Python module.",
    "Review this shell script for security issues.",
    "Explain this SQL query step by step.",
    "Summarize the architecture in this README.",
    "Create a slide deck outline for this project.",
    "Refactor this React component for readability.",
    "Generate release notes from recent commits.",
    "Help me debug a Docker networking issue.",
    "Turn this design doc into a course outline.",
]


@dataclass
class SkillInfo:
    name: str
    path: Path
    description: str
    trigger_phrases: list[str]


@dataclass
class QueryResult:
    query: str
    expected: str
    triggered: bool
    score: float
    matched_keywords: list[str]

    def passed(self) -> bool:
        if self.expected == "should_trigger":
            return self.triggered
        return not self.triggered

    def to_dict(self) -> dict:
        return {
            "query": self.query,
            "expected": self.expected,
            "triggered": self.triggered,
            "score": round(self.score, 4),
            "matched_keywords": self.matched_keywords,
            "passed": self.passed(),
        }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Evaluate whether a skill triggers correctly using keyword overlap."
    )
    parser.add_argument("--path", required=True, help="Path to the skill directory")
    parser.add_argument(
        "--test-file",
        help="Optional JSON file with should_trigger and should_not_trigger queries",
    )
    parser.add_argument(
        "--siblings",
        help="Optional directory containing sibling skills for cross-trigger testing",
    )
    parser.add_argument("--json", action="store_true", help="Emit JSON output")
    parser.add_argument(
        "--verbose", action="store_true", help="Show per-query evaluation details"
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=0.80,
        help="Minimum acceptable trigger pass rate (default: 0.80)",
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


def extract_trigger_phrases(text: str) -> list[str]:
    phrases: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("- "):
            phrases.append(stripped[2:].strip())
        for match in re.findall(r'"([^"]+)"', stripped):
            phrases.append(match.strip())
    deduped: list[str] = []
    seen: set[str] = set()
    for phrase in phrases:
        lowered = phrase.lower()
        if lowered and lowered not in seen:
            seen.add(lowered)
            deduped.append(phrase)
    return deduped


def load_skill(skill_dir: Path) -> SkillInfo:
    skill_file = skill_dir / "SKILL.md"
    if not skill_file.is_file():
        raise FileNotFoundError(f"Missing SKILL.md in {skill_dir}")

    text = skill_file.read_text(encoding="utf-8")
    frontmatter, body = extract_frontmatter(text)
    description = str(frontmatter.get("description", "")).strip()
    name = str(frontmatter.get("name", skill_dir.name)).strip() or skill_dir.name
    trigger_phrases = extract_trigger_phrases(body)

    if not description:
        raise ValueError(f"Skill description is missing in {skill_file}")

    return SkillInfo(
        name=name,
        path=skill_dir,
        description=description,
        trigger_phrases=trigger_phrases,
    )


def _is_cjk(char: str) -> bool:
    return "\u4e00" <= char <= "\u9fff"


def _contains_cjk(text: str) -> bool:
    return any(_is_cjk(char) for char in text)


def _add_cjk_keywords(token: str, keywords: set[str]) -> None:
    cjk_only = "".join(char for char in token if _is_cjk(char))
    if not cjk_only:
        return

    if cjk_only not in STOPWORDS:
        keywords.add(cjk_only)

    for char in cjk_only:
        if char not in STOPWORDS:
            keywords.add(char)

    if len(cjk_only) >= 2:
        for index in range(len(cjk_only) - 1):
            bigram = cjk_only[index : index + 2]
            if bigram not in STOPWORDS:
                keywords.add(bigram)


def extract_keywords(text: str) -> set[str]:
    tokens = re.findall(r"[a-z0-9]+|[\u4e00-\u9fff]+", text.lower())
    keywords: set[str] = set()

    for token in tokens:
        if _contains_cjk(token):
            _add_cjk_keywords(token, keywords)
            continue

        if len(token) >= 3 and token not in STOPWORDS:
            keywords.add(token)

    return keywords


def score_query(description_keywords: set[str], query: str) -> tuple[float, list[str]]:
    query_keywords = extract_keywords(query)
    if not description_keywords or not query_keywords:
        return 0.0, []
    matched = sorted(description_keywords & query_keywords)
    if not matched:
        return 0.0, []

    recall = len(matched) / len(description_keywords)
    precision = len(matched) / len(query_keywords)
    score = max(recall, precision)
    return score, matched


def build_positive_queries(
    skill_name: str, description_keywords: list[str], trigger_phrases: list[str]
) -> list[str]:
    """Generate realistic positive test queries from trigger phrases and skill name."""
    queries: list[str] = []
    readable_name = skill_name.replace("-", " ")

    # Strategy 1: Use trigger phrases directly as queries (most realistic)
    for phrase in trigger_phrases[:4]:
        queries.append(phrase)

    # Strategy 2: Wrap trigger phrases in natural request templates
    request_templates = [
        "Help me {phrase}",
        "I need to {phrase}",
        "Can you {phrase} for this project?",
        "Please {phrase}",
    ]
    for i, phrase in enumerate(trigger_phrases[:4]):
        # Clean phrase: remove leading "when user says" type prefixes
        clean = phrase.strip().rstrip(".")
        template = request_templates[i % len(request_templates)]
        queries.append(template.format(phrase=clean))

    # Strategy 3: Skill-name based queries (fallback)
    name_templates = [
        f"Run {readable_name} on this file",
        f"Use {readable_name} to check my work",
        f"I want to use the {readable_name} skill",
        f"Apply {readable_name} to this content",
    ]
    queries.extend(name_templates[: max(0, 8 - len(queries))])

    # Deduplicate while preserving order
    seen: set[str] = set()
    deduped: list[str] = []
    for q in queries:
        lower = q.lower()
        if lower not in seen:
            seen.add(lower)
            deduped.append(q)

    return deduped[:8]


def build_negative_queries(description_keywords: set[str]) -> list[str]:
    negatives: list[str] = []
    for query in NEGATIVE_QUERY_POOL:
        if not (extract_keywords(query) & description_keywords):
            negatives.append(query)
        if len(negatives) == 8:
            break

    if len(negatives) < 8:
        for query in NEGATIVE_QUERY_POOL:
            if query not in negatives:
                negatives.append(query)
            if len(negatives) == 8:
                break
    return negatives


def auto_generate_tests(skill: SkillInfo) -> tuple[dict, str]:
    description_keywords = sorted(extract_keywords(skill.description))
    positive = build_positive_queries(
        skill.name, description_keywords, skill.trigger_phrases
    )
    negative = build_negative_queries(set(description_keywords))
    payload = {
        "skill": skill.name,
        "should_trigger": positive,
        "should_not_trigger": negative,
    }
    return payload, "auto-generated"


def load_test_file(test_file: Path) -> dict:
    try:
        payload = json.loads(test_file.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON in {test_file}: {exc}") from exc

    if not isinstance(payload, dict):
        raise ValueError("Test file must contain a top-level JSON object")

    for key in ("should_trigger", "should_not_trigger"):
        value = payload.get(key)
        if not isinstance(value, list) or not all(
            isinstance(item, str) for item in value
        ):
            raise ValueError(f"{key} must be a list of strings")
    return payload


def evaluate_queries(
    description_keywords: set[str], queries: list[str], expected: str
) -> list[QueryResult]:
    results: list[QueryResult] = []
    for query in queries:
        score, matched_keywords = score_query(description_keywords, query)
        results.append(
            QueryResult(
                query=query,
                expected=expected,
                triggered=score >= 0.3,
                score=score,
                matched_keywords=matched_keywords,
            )
        )
    return results


def load_sibling_skills(siblings_dir: Path, target_dir: Path) -> list[SkillInfo]:
    siblings: list[SkillInfo] = []
    for child in sorted(siblings_dir.iterdir()):
        if not child.is_dir() or child.resolve() == target_dir.resolve():
            continue
        skill_file = child / "SKILL.md"
        if not skill_file.is_file():
            continue
        try:
            siblings.append(load_skill(child))
        except (OSError, ValueError):
            continue
    return siblings


def find_cross_trigger_conflicts(
    positive_queries: list[str], siblings: list[SkillInfo]
) -> list[dict]:
    conflicts: list[dict] = []
    for sibling in siblings:
        sibling_keywords = extract_keywords(sibling.description)
        for query in positive_queries:
            score, matched_keywords = score_query(sibling_keywords, query)
            if score >= 0.3:
                conflicts.append(
                    {
                        "query": query,
                        "sibling": sibling.name,
                        "score": round(score, 4),
                        "matched_keywords": matched_keywords,
                    }
                )
    return conflicts


def build_report(
    skill: SkillInfo,
    source: str,
    positive_results: list[QueryResult],
    negative_results: list[QueryResult],
    cross_trigger_conflicts: list[dict],
    threshold: float,
) -> dict:
    total_positive = len(positive_results)
    total_negative = len(negative_results)
    passed_positive = sum(result.triggered for result in positive_results)
    failed_negative = sum(result.triggered for result in negative_results)
    failed_positive = total_positive - passed_positive

    trigger_pass_rate = passed_positive / total_positive if total_positive else 0.0
    false_positive_rate = failed_negative / total_negative if total_negative else 0.0
    false_negative_rate = failed_positive / total_positive if total_positive else 0.0
    verdict = (
        "PASS"
        if trigger_pass_rate >= threshold and false_positive_rate <= 0.15
        else "FAIL"
    )

    return {
        "skill": skill.name,
        "source": source,
        "trigger_pass_rate": round(trigger_pass_rate, 4),
        "false_positive_rate": round(false_positive_rate, 4),
        "false_negative_rate": round(false_negative_rate, 4),
        "total_positive": total_positive,
        "total_negative": total_negative,
        "passed_positive": passed_positive,
        "failed_negative": failed_negative,
        "cross_trigger_conflicts": cross_trigger_conflicts,
        "verdict": verdict,
    }


def print_human_report(
    report: dict,
    positive_results: list[QueryResult],
    negative_results: list[QueryResult],
    verbose: bool,
) -> None:
    print(f"Skill: {report['skill']}")
    print(f"Test source: {report['source']}")
    print(f"Trigger pass rate: {report['trigger_pass_rate']:.2f}")
    print(f"False positive rate: {report['false_positive_rate']:.2f}")
    print(f"False negative rate: {report['false_negative_rate']:.2f}")
    print(
        f"Positive: {report['passed_positive']}/{report['total_positive']} | "
        f"Negative slips: {report['failed_negative']}/{report['total_negative']}"
    )
    print(f"Verdict: {report['verdict']}")

    if report["cross_trigger_conflicts"]:
        print("Cross-trigger conflicts:")
        for conflict in report["cross_trigger_conflicts"]:
            print(
                f"  - {conflict['sibling']}: {conflict['query']} "
                f"(score={conflict['score']:.2f}, matched={', '.join(conflict['matched_keywords'])})"
            )

    if verbose:
        print("\nPer-query results:")
        for result in positive_results + negative_results:
            actual = "triggered" if result.triggered else "not_triggered"
            print(
                f"- [{result.expected}] {'PASS' if result.passed() else 'FAIL'} | "
                f"{actual} | score={result.score:.2f} | matched={', '.join(result.matched_keywords) or '-'}"
            )
            print(f"  {result.query}")


def main() -> int:
    args = parse_args()
    skill_dir = Path(args.path).expanduser().resolve()
    if not skill_dir.is_dir():
        print(f"Skill directory not found: {skill_dir}", file=sys.stderr)
        return 2

    try:
        skill = load_skill(skill_dir)
    except (OSError, ValueError, FileNotFoundError) as exc:
        print(str(exc), file=sys.stderr)
        return 2

    description_keywords = extract_keywords(skill.description)
    if args.test_file:
        test_path = Path(args.test_file).expanduser().resolve()
        if not test_path.is_file():
            print(f"Test file not found: {test_path}", file=sys.stderr)
            return 2
        try:
            test_payload = load_test_file(test_path)
        except ValueError as exc:
            print(str(exc), file=sys.stderr)
            return 2
        source = str(test_path)
    else:
        test_payload, source = auto_generate_tests(skill)

    positive_queries = test_payload.get("should_trigger", [])
    negative_queries = test_payload.get("should_not_trigger", [])
    positive_results = evaluate_queries(
        description_keywords, positive_queries, "should_trigger"
    )
    negative_results = evaluate_queries(
        description_keywords, negative_queries, "should_not_trigger"
    )

    cross_trigger_conflicts: list[dict] = []
    if args.siblings:
        siblings_dir = Path(args.siblings).expanduser().resolve()
        if not siblings_dir.is_dir():
            print(f"Sibling skill directory not found: {siblings_dir}", file=sys.stderr)
            return 2
        siblings = load_sibling_skills(siblings_dir, skill_dir)
        cross_trigger_conflicts = find_cross_trigger_conflicts(
            positive_queries, siblings
        )

    report = build_report(
        skill,
        source,
        positive_results,
        negative_results,
        cross_trigger_conflicts,
        args.threshold,
    )

    if args.json:
        payload = dict(report)
        if args.verbose:
            payload["results"] = {
                "should_trigger": [result.to_dict() for result in positive_results],
                "should_not_trigger": [result.to_dict() for result in negative_results],
            }
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    else:
        print_human_report(report, positive_results, negative_results, args.verbose)

    return 0 if report["verdict"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
