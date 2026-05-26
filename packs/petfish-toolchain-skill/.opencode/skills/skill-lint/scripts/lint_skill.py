#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = []
# ///
"""Lint SKILL.md files and skill directory structure.

Usage:
  uv run lint_skill.py --path ./my-skill/
  uv run lint_skill.py --path ./my-skill/ --json
  uv run lint_skill.py --path ./my-skill/ --severity error
  uv run lint_skill.py --path . --recursive
"""

from __future__ import annotations

import argparse
import ast
import json
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path

SEVERITY_ORDER = {"info": 1, "warn": 2, "error": 3}
TRIGGER_HINTS = (
    "when",
    "when the user",
    "use this skill",
    "trigger",
    "activate",
    "activates when",
    "if the user",
    "asks",
    "ask to",
    "当用户",
    "用于",
    "适用于",
)

# Filler prefixes that inflate description token count without adding trigger value.
# Kept in sync with scripts/compress_descriptions.py FILLER_PREFIXES.
COMPRESSIBLE_PREFIXES: list[re.Pattern[str]] = [
    re.compile(p, re.IGNORECASE)
    for p in [
        r"^Use this skill when the user wants to\s+",
        r"^Use this skill when the user needs to\s+",
        r"^Use this skill when the user asks to\s+",
        r"^Use this skill when the user wants\s+",
        r"^Use this skill when the user needs\s+",
        r"^Use this skill when the user asks\s+",
        r"^Use this skill when the user\s+",
        r"^Use this skill to\s+",
        r"^Use this skill when\s+",
        r"^Use this skill for\s+",
    ]
]


@dataclass
class Finding:
    id: str
    severity: str
    message: str
    fix: str
    type: str | None = None
    coverage_pct: float | None = None

    def to_dict(self) -> dict:
        payload: dict[str, object] = {
            "id": self.id,
            "type": self.type or self.id,
            "severity": self.severity,
            "message": self.message,
            "fix": self.fix,
        }
        if self.coverage_pct is not None:
            payload["coverage_pct"] = self.coverage_pct
        return payload


@dataclass
class LintResult:
    skill: str
    path: str
    score: int
    findings: list[Finding]
    summary: dict
    planned_fixes: list[str]

    def to_dict(self) -> dict:
        payload = {
            "skill": self.skill,
            "path": self.path,
            "score": self.score,
            "findings": [finding.to_dict() for finding in self.findings],
            "summary": self.summary,
        }
        if self.planned_fixes:
            payload["planned_fixes"] = self.planned_fixes
        return payload


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Lint SKILL.md files and skill directory structure."
    )
    parser.add_argument("--path", required=True, help="Path to skill directory or root")
    parser.add_argument("--json", action="store_true", help="Output findings as JSON")
    parser.add_argument(
        "--severity",
        choices=["error", "warn", "info"],
        help="Filter by minimum severity",
    )
    parser.add_argument(
        "--recursive",
        action="store_true",
        help="Find and lint all subdirectories containing SKILL.md",
    )
    parser.add_argument(
        "--fix",
        action="store_true",
        help="Show auto-fix plan (dry run by default)",
    )
    parser.add_argument(
        "--fix-apply",
        action="store_true",
        help="Apply supported fixes",
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


def dump_frontmatter(data: dict) -> str:
    def render_mapping(mapping: dict, indent: int = 0) -> list[str]:
        lines: list[str] = []
        pad = " " * indent
        for key, value in mapping.items():
            if isinstance(value, dict):
                lines.append(f"{pad}{key}:")
                lines.extend(render_mapping(value, indent + 2))
            elif "\n" in str(value):
                lines.append(f"{pad}{key}: >")
                for part in str(value).splitlines():
                    lines.append(f"{' ' * (indent + 2)}{part}")
            else:
                lines.append(
                    f"{pad}{key}: {json.dumps(str(value), ensure_ascii=False)}"
                )
        return lines

    return "---\n" + "\n".join(render_mapping(data)) + "\n---\n"


def estimate_tokens(text: str) -> int:
    words = re.findall(r"\S+", text)
    return int(len(words) * 1.3)


def has_trigger_hint(description: str) -> bool:
    lowered = description.lower()
    return any(hint in lowered for hint in TRIGGER_HINTS)


def add_finding(
    findings: list[Finding],
    rule_id: str,
    severity: str,
    message: str,
    fix: str,
    finding_type: str | None = None,
    coverage_pct: float | None = None,
):
    findings.append(
        Finding(
            rule_id,
            severity,
            message,
            fix,
            type=finding_type,
            coverage_pct=coverage_pct,
        )
    )


TRIGGER_SECTION_TITLES = (
    "触发场景",
    "trigger",
    "use this skill when",
    "适用场景",
    "when to use",
    "触发短语",
    "trigger phrases",
)

TRIGGER_STOPWORDS = {
    "the",
    "and",
    "for",
    "with",
    "this",
    "that",
    "from",
    "when",
    "where",
    "which",
    "user",
    "users",
    "skill",
    "skills",
    "asks",
    "ask",
    "use",
    "using",
    "used",
    "trigger",
    "triggers",
    "phrases",
    "phrase",
    "适用",
    "触发",
    "场景",
    "用户",
    "使用",
    "技能",
    "时候",
}


def normalized_whitespace(text: str) -> str:
    return " ".join(text.strip().split())


def normalize_for_match(text: str) -> str:
    cleaned = re.sub(r"[`*_~#>\[\](){}]", " ", text.lower())
    cleaned = re.sub(r"[\s\-_/\\]+", " ", cleaned)
    return normalized_whitespace(cleaned)


def extract_terms(text: str) -> set[str]:
    terms: set[str] = set()
    for token in re.findall(r"[a-z][a-z0-9-]{1,}|[\u4e00-\u9fff]{2,}", text.lower()):
        token = token.strip("-_")
        if len(token) < 2:
            continue
        if token in TRIGGER_STOPWORDS:
            continue
        terms.add(token)
    return terms


def extract_trigger_sections(body: str) -> str:
    lines = body.splitlines()
    captured_chunks: list[str] = []
    collecting = False

    for line in lines:
        heading_match = re.match(r"^\s{0,3}#{1,6}\s*(.+?)\s*$", line)
        if heading_match:
            heading = heading_match.group(1).strip().lower()
            collecting = any(title in heading for title in TRIGGER_SECTION_TITLES)
            continue

        inline_match = re.match(r"^\s*(?:[-*]\s*)?([^:：]+)\s*[:：]\s*(.+)$", line)
        if inline_match:
            lead = inline_match.group(1).strip().lower()
            value = inline_match.group(2).strip()
            if any(title in lead for title in TRIGGER_SECTION_TITLES):
                captured_chunks.append(value)

        if collecting:
            captured_chunks.append(line)

    return "\n".join(captured_chunks)


def extract_quoted_phrases(text: str) -> set[str]:
    phrases: set[str] = set()
    patterns = [
        r'"([^"\n]{2,120})"',
        r"'([^'\n]{2,120})'",
        r"“([^”\n]{2,120})”",
        r"‘([^’\n]{2,120})’",
    ]
    for pattern in patterns:
        for match in re.findall(pattern, text):
            phrase = normalize_for_match(match)
            if len(phrase) >= 2:
                phrases.add(phrase)
    return phrases


def extract_trigger_keywords(body: str) -> set[str]:
    section_text = extract_trigger_sections(body)
    if not section_text.strip():
        return set()

    keywords: set[str] = set()
    separator_pattern = re.compile(r"[/、,，;；]|\bor\b", re.I)
    section_header_pattern = re.compile(
        r"^(?:use\s+this\s+skill\s+when|when\s+to\s+use|trigger(?:\s+phrases?)?|触发(?:场景|短语)?|适用场景)\s*[:：-]?\s*",
        re.I,
    )

    for raw_line in section_text.splitlines():
        line = re.sub(r"^\s*(?:[-*+]|\d+\.)\s*", "", raw_line).strip()
        if not line:
            continue

        quoted = extract_quoted_phrases(line)
        if quoted:
            keywords.update(extract_terms(" ".join(quoted)))

        if not separator_pattern.search(line):
            continue

        normalized_line = section_header_pattern.sub("", line)
        for chunk in re.split(separator_pattern, normalized_line):
            chunk = normalize_for_match(chunk)
            if not chunk or len(chunk) < 2:
                continue
            keywords.update(extract_terms(chunk))

    return keywords


def term_is_covered(
    term: str, description_terms: set[str], normalized_description: str
) -> bool:
    if term in normalized_description:
        return True
    for desc_term in description_terms:
        if term == desc_term:
            return True
        if len(term) >= 2 and len(desc_term) >= 2:
            if term in desc_term or desc_term in term:
                return True
    return False


def check_trigger_coverage(
    description: str, body: str, findings: list[Finding]
) -> None:
    if not description.strip() or not body.strip():
        return

    body_terms = extract_trigger_keywords(body)
    if not body_terms:
        return

    normalized_description = normalize_for_match(description)
    description_terms = extract_terms(description)

    matched = {
        term
        for term in body_terms
        if term_is_covered(term, description_terms, normalized_description)
    }
    coverage_pct = round((len(matched) / len(body_terms)) * 100, 1)

    if coverage_pct < 50:
        add_finding(
            findings,
            "trigger-coverage",
            "error",
            f"description trigger coverage is {coverage_pct}% ({len(matched)}/{len(body_terms)})",
            "Include key trigger terms from SKILL.md trigger sections in the frontmatter description.",
            finding_type="trigger-coverage",
            coverage_pct=coverage_pct,
        )
    elif coverage_pct < 80:
        add_finding(
            findings,
            "trigger-coverage",
            "warn",
            f"description trigger coverage is {coverage_pct}% ({len(matched)}/{len(body_terms)})",
            "Expand the frontmatter description to cover more trigger terms from SKILL.md trigger sections.",
            finding_type="trigger-coverage",
            coverage_pct=coverage_pct,
        )


def relative_display(path: Path) -> str:
    try:
        return os.path.relpath(path, Path.cwd())
    except ValueError:
        return str(path)


def scan_security_patterns(scripts_dir: Path) -> list[Finding]:
    findings: list[Finding] = []
    if not scripts_dir.is_dir():
        return findings

    sc003 = re.compile(
        r"(?i)\b(api[_-]?key|password|passwd|token|secret)\b\s*=\s*['\"][^'\"]{6,}['\"]"
    )
    sc001 = re.compile(r"subprocess\.call\s*\([\s\S]*?shell\s*=\s*True")
    sc002 = re.compile(r"\b(eval|exec)\s*\(")
    sc004 = re.compile(r"\b(urllib(?:\.request)?|requests|httpx)\b|\bcurl\s+https?://")

    for file_path in scripts_dir.rglob("*"):
        if not file_path.is_file():
            continue
        try:
            text = file_path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue

        display = relative_display(file_path)
        if file_path.suffix == ".py":
            findings.extend(scan_python_security(file_path, text))
        else:
            if sc001.search(text):
                add_finding(
                    findings,
                    "SC001",
                    "warn",
                    f"{display} uses subprocess.call with shell=True",
                    "Prefer subprocess.run([...], check=True) without shell=True.",
                )
            if sc002.search(text):
                add_finding(
                    findings,
                    "SC002",
                    "warn",
                    f"{display} contains eval() or exec()",
                    "Replace dynamic code execution with explicit parsing or safe dispatch logic.",
                )
            if sc004.search(text):
                add_finding(
                    findings,
                    "SC004",
                    "info",
                    f"{display} appears to make network requests",
                    "Document why network access is needed and keep timeouts and error handling explicit.",
                )
        if sc003.search(text):
            add_finding(
                findings,
                "SC003",
                "warn",
                f"{display} may contain hardcoded credentials",
                "Move secrets to environment variables or external config and rotate exposed values.",
            )

    return findings


def dotted_name(node: ast.AST) -> str:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        base = dotted_name(node.value)
        return f"{base}.{node.attr}" if base else node.attr
    return ""


def call_uses_curl(node: ast.Call) -> bool:
    for arg in node.args:
        if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
            if re.search(r"\bcurl\s+https?://", arg.value):
                return True
    return False


def scan_python_security(file_path: Path, text: str) -> list[Finding]:
    findings: list[Finding] = []
    display = relative_display(file_path)

    try:
        tree = ast.parse(text)
    except SyntaxError:
        return findings

    network_detected = False

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            if any(
                alias.name.split(".")[0] in {"urllib", "requests", "httpx"}
                for alias in node.names
            ):
                network_detected = True
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            if module.split(".")[0] in {"urllib", "requests", "httpx"}:
                network_detected = True
        elif isinstance(node, ast.Call):
            func_name = dotted_name(node.func)
            if func_name == "subprocess.call":
                shell_true = any(
                    keyword.arg == "shell"
                    and isinstance(keyword.value, ast.Constant)
                    and keyword.value.value is True
                    for keyword in node.keywords
                )
                if shell_true:
                    add_finding(
                        findings,
                        "SC001",
                        "warn",
                        f"{display} uses subprocess.call with shell=True",
                        "Prefer subprocess.run([...], check=True) without shell=True.",
                    )
                if call_uses_curl(node):
                    network_detected = True
            elif func_name in {"eval", "exec"}:
                add_finding(
                    findings,
                    "SC002",
                    "warn",
                    f"{display} contains eval() or exec()",
                    "Replace dynamic code execution with explicit parsing or safe dispatch logic.",
                )
            elif func_name.startswith("requests.") or func_name.startswith("httpx."):
                network_detected = True
            elif func_name.startswith("urllib."):
                network_detected = True

    if network_detected:
        add_finding(
            findings,
            "SC004",
            "info",
            f"{display} appears to make network requests",
            "Document why network access is needed and keep timeouts and error handling explicit.",
        )

    return findings


def token_overlap_ratio(reference_text: str, skill_body: str) -> float:
    token_pattern = r"[A-Za-z0-9_-]+|[\u4e00-\u9fff]"
    ref_tokens = set(re.findall(token_pattern, reference_text.lower()))
    skill_tokens = set(re.findall(token_pattern, skill_body.lower()))
    if len(ref_tokens) < 40 or not skill_tokens:
        return 0.0
    return len(ref_tokens & skill_tokens) / len(ref_tokens)


def lint_skill_dir(skill_dir: Path) -> tuple[LintResult, dict, str]:
    findings: list[Finding] = []
    skill_md = skill_dir / "SKILL.md"
    raw_text = ""
    frontmatter: dict = {}
    body = ""

    if not skill_md.is_file():
        add_finding(
            findings,
            "ST001",
            "error",
            "SKILL.md not found",
            f"Create {skill_dir.name}/SKILL.md with valid frontmatter and instructions.",
        )
        result = build_result(skill_dir.name, skill_dir, findings, [])
        return result, {}, ""

    raw_text = skill_md.read_text(encoding="utf-8")
    frontmatter, body = extract_frontmatter(raw_text)

    name = str(frontmatter.get("name", "")).strip()
    description = str(frontmatter.get("description", "")).strip()
    metadata = frontmatter.get("metadata")
    metadata = metadata if isinstance(metadata, dict) else {}

    if not name:
        add_finding(
            findings,
            "FM001",
            "error",
            "name field missing in frontmatter",
            f"Add 'name: {skill_dir.name}' to frontmatter.",
        )
    else:
        if len(name) > 64:
            add_finding(
                findings,
                "FM002",
                "error",
                "name exceeds 64 chars",
                "Shorten the skill name to 64 characters or fewer.",
            )
        if not re.fullmatch(r"[a-z0-9-]+", name):
            add_finding(
                findings,
                "FM003",
                "error",
                "name contains invalid characters",
                "Use only lowercase letters, digits, and hyphens in the name field.",
            )
        if name != skill_dir.name:
            add_finding(
                findings,
                "FM004",
                "warn",
                f"name '{name}' does not match parent directory '{skill_dir.name}'",
                "Rename the directory or update the frontmatter name so they match.",
            )

    if not description:
        add_finding(
            findings,
            "FM005",
            "error",
            "description field missing in frontmatter",
            "Add a short description that explains when to use the skill.",
        )
    else:
        if len(description) > 1024:
            add_finding(
                findings,
                "FM006",
                "warn",
                "description exceeds 1024 chars",
                "Trim the description to 1024 characters or fewer.",
            )
        if not has_trigger_hint(description):
            add_finding(
                findings,
                "FM007",
                "warn",
                "description doesn't mention when to use the skill",
                "Add trigger phrases such as 'Use this skill when...' or concrete user intents.",
            )

    if not str(metadata.get("version", "")).strip():
        add_finding(
            findings,
            "FM008",
            "info",
            "missing metadata.version",
            "Add metadata.version so pack maintainers can track skill revisions.",
        )
    if not str(metadata.get("author", "")).strip():
        add_finding(
            findings,
            "FM009",
            "info",
            "missing metadata.author",
            "Add metadata.author to show ownership of the skill.",
        )

    check_trigger_coverage(description, body, findings)

    # FM010: description compression check
    if description:
        for pat in COMPRESSIBLE_PREFIXES:
            if pat.search(description):
                add_finding(
                    findings,
                    "FM010",
                    "warn",
                    "description contains compressible filler prefix (wastes tokens in system prompt)",
                    "Remove the filler prefix. Run: uv run scripts/compress_descriptions.py --root <path> --apply",
                )
                break  # one warning per skill is enough

    references_dir = skill_dir / "references"
    scripts_dir = skill_dir / "scripts"
    evals_dir = skill_dir / "evals"

    if not references_dir.is_dir():
        add_finding(
            findings,
            "ST002",
            "warn",
            "no references/ directory",
            "Create a references/ directory for detailed rules, examples, or reference material.",
        )
    if not scripts_dir.is_dir():
        add_finding(
            findings,
            "ST003",
            "warn",
            "no scripts/ directory",
            "Create a scripts/ directory for helper tools or validators.",
        )
    if evals_dir.is_dir() and not any(evals_dir.iterdir()):
        add_finding(
            findings,
            "ST004",
            "info",
            "empty evals/ directory",
            "Add at least one eval asset or remove the empty evals/ directory.",
        )

    extra_root_files = sorted(
        entry.name
        for entry in skill_dir.iterdir()
        if entry.is_file() and entry.name not in {"SKILL.md", "README.md"}
    )
    if extra_root_files:
        add_finding(
            findings,
            "ST005",
            "warn",
            f"unexpected root files: {', '.join(extra_root_files)}",
            "Move ad-hoc files into references/, scripts/, examples/, or remove them if no longer needed.",
        )

    if not body.strip():
        add_finding(
            findings,
            "CT001",
            "warn",
            "SKILL.md body is empty",
            "Add instructions after the frontmatter so the skill explains how it should be used.",
        )
    if estimate_tokens(body) > 5000:
        add_finding(
            findings,
            "CT002",
            "warn",
            "SKILL.md body exceeds estimated 5000 tokens",
            "Move long examples or detailed rules into references/ files and keep SKILL.md focused.",
        )

    lowered_body = body.lower()
    if "must do" not in lowered_body and "must not do" not in lowered_body:
        add_finding(
            findings,
            "CT003",
            "info",
            'no "must do" / "must not do" section in SKILL.md',
            "Add short must-do and must-not-do guidance to make the skill behavior clearer.",
        )

    if references_dir.is_dir():
        for reference_file in references_dir.rglob("*"):
            if not reference_file.is_file():
                continue
            text = reference_file.read_text(encoding="utf-8", errors="ignore")
            overlap = token_overlap_ratio(text, body)
            if overlap > 0.5:
                add_finding(
                    findings,
                    "CT004",
                    "warn",
                    f"{relative_display(reference_file)} duplicates SKILL.md content (>50% overlap)",
                    "Move repeated text out of one file or rewrite the reference to add detail instead of duplication.",
                )

    findings.extend(scan_security_patterns(scripts_dir))

    planned_fixes = build_fix_plan(skill_dir, frontmatter, findings)
    result = build_result(name or skill_dir.name, skill_dir, findings, planned_fixes)
    return result, frontmatter, body


def build_fix_plan(
    skill_dir: Path, frontmatter: dict, findings: list[Finding]
) -> list[str]:
    rule_ids = {finding.id for finding in findings}
    plan: list[str] = []
    if "ST002" in rule_ids:
        plan.append(f"Create directory: {relative_display(skill_dir / 'references')}")
    if "ST003" in rule_ids:
        plan.append(f"Create directory: {relative_display(skill_dir / 'scripts')}")
    description = str(frontmatter.get("description", "")).strip()
    if "FM006" in rule_ids and description:
        plan.append("Trim description to 1024 characters")
    if "FM010" in rule_ids and description:
        plan.append("Remove compressible filler prefix from description")
    return plan


def build_result(
    skill_name: str, skill_dir: Path, findings: list[Finding], planned_fixes: list[str]
) -> LintResult:
    errors = sum(1 for finding in findings if finding.severity == "error")
    warnings = sum(1 for finding in findings if finding.severity == "warn")
    info = sum(1 for finding in findings if finding.severity == "info")
    score = max(100 - (errors * 20) - (warnings * 5) - info, 0)
    return LintResult(
        skill=skill_name,
        path=relative_display(skill_dir),
        score=score,
        findings=findings,
        summary={"errors": errors, "warnings": warnings, "info": info},
        planned_fixes=planned_fixes,
    )


def filter_findings(findings: list[Finding], minimum: str | None) -> list[Finding]:
    if not minimum:
        return findings
    threshold = SEVERITY_ORDER[minimum]
    return [
        finding for finding in findings if SEVERITY_ORDER[finding.severity] >= threshold
    ]


def apply_fixes(
    skill_dir: Path, frontmatter: dict, body: str, findings: list[Finding]
) -> list[str]:
    applied: list[str] = []
    rule_ids = {finding.id for finding in findings}

    if "ST002" in rule_ids:
        target = skill_dir / "references"
        target.mkdir(parents=True, exist_ok=True)
        applied.append(f"Created directory: {relative_display(target)}")
    if "ST003" in rule_ids:
        target = skill_dir / "scripts"
        target.mkdir(parents=True, exist_ok=True)
        applied.append(f"Created directory: {relative_display(target)}")

    description = str(frontmatter.get("description", "")).strip()
    if "FM006" in rule_ids and description:
        updated = dict(frontmatter)
        updated["description"] = description[:1024].rstrip()
        skill_md = skill_dir / "SKILL.md"
        skill_md.write_text(
            dump_frontmatter(updated) + body.lstrip("\n"), encoding="utf-8"
        )
        applied.append("Trimmed description to 1024 characters")

    if "FM010" in rule_ids and description:
        compressed = description
        for pat in COMPRESSIBLE_PREFIXES:
            compressed = pat.sub("", compressed)
        if compressed != description:
            # Capitalize first letter after prefix removal
            if compressed and compressed[0].islower():
                compressed = compressed[0].upper() + compressed[1:]
            updated = dict(frontmatter)
            updated["description"] = compressed
            skill_md = skill_dir / "SKILL.md"
            skill_md.write_text(
                dump_frontmatter(updated) + body.lstrip("\n"), encoding="utf-8"
            )
            applied.append("Removed compressible filler prefix from description")

    return applied


def discover_skill_dirs(root: Path) -> list[Path]:
    found: list[Path] = []
    if (root / "SKILL.md").is_file():
        found.append(root)
    for skill_md in root.rglob("SKILL.md"):
        parent = skill_md.parent
        if parent not in found:
            found.append(parent)
    return sorted(found)


def print_text_result(result: LintResult, minimum: str | None) -> None:
    shown = filter_findings(result.findings, minimum)
    print(f"Linting: {result.skill}/")
    print()
    if shown:
        for finding in shown:
            label = finding.severity.upper().ljust(5)
            print(f"  {label}  {finding.id}  {finding.message}")
            print(f"                fix: {finding.fix}")
    else:
        print("  No findings at the selected severity.")
    print()
    print(f"Score: {result.score}/100")
    print(
        f"Errors: {result.summary['errors']}  Warnings: {result.summary['warnings']}  Info: {result.summary['info']}"
    )
    if result.planned_fixes:
        print()
        print("Planned fixes:")
        for item in result.planned_fixes:
            print(f"  - {item}")


def main() -> int:
    args = parse_args()
    if args.fix_apply:
        args.fix = True

    root = Path(args.path)
    if not root.exists():
        print(f"Path not found: {root}", file=sys.stderr)
        return 2

    skill_dirs = discover_skill_dirs(root) if args.recursive else [root]
    if args.recursive and not skill_dirs:
        print(f"No skill directories found under: {root}", file=sys.stderr)
        return 1

    results: list[LintResult] = []
    applied_fixes: dict[str, list[str]] = {}

    for skill_dir in skill_dirs:
        result, frontmatter, body = lint_skill_dir(skill_dir)
        if args.fix_apply and result.planned_fixes:
            applied = apply_fixes(skill_dir, frontmatter, body, result.findings)
            if applied:
                applied_fixes[result.path] = applied
                result, _, _ = lint_skill_dir(skill_dir)
        if not args.fix:
            result.planned_fixes = []
        results.append(result)

    if args.json:
        if len(results) == 1:
            payload = results[0].to_dict()
            payload["findings"] = [
                finding.to_dict()
                for finding in filter_findings(results[0].findings, args.severity)
            ]
            if applied_fixes.get(results[0].path):
                payload["applied_fixes"] = applied_fixes[results[0].path]
        else:
            payload = {
                "results": [],
                "summary": {
                    "skills": len(results),
                    "errors": sum(result.summary["errors"] for result in results),
                    "warnings": sum(result.summary["warnings"] for result in results),
                    "info": sum(result.summary["info"] for result in results),
                },
            }
            for result in results:
                item = result.to_dict()
                item["findings"] = [
                    finding.to_dict()
                    for finding in filter_findings(result.findings, args.severity)
                ]
                payload["results"].append(item)
            if applied_fixes:
                payload["applied_fixes"] = applied_fixes
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        for index, result in enumerate(results):
            if index:
                print()
            print_text_result(result, args.severity)
            if args.fix_apply and applied_fixes.get(result.path):
                print()
                print("Applied fixes:")
                for item in applied_fixes[result.path]:
                    print(f"  - {item}")

    return 1 if any(result.summary["errors"] for result in results) else 0


if __name__ == "__main__":
    raise SystemExit(main())
