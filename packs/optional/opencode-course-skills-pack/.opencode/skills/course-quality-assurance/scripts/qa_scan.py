#!/usr/bin/env python3
"""Run content-level QA checks for a course project."""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from pathlib import Path


INTERNAL_MARKERS = ["待补充", "TODO", "TBD", "后面再写", "FIXME"]
LEAK_KEYWORDS = ["答案", "answer", "instructor", "教师"]


@dataclass
class Issue:
    severity: str
    clazz: str
    file: str
    description: str

    def to_dict(self) -> dict[str, str]:
        return {
            "severity": self.severity,
            "class": self.clazz,
            "file": self.file,
            "description": self.description,
        }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run QA scan for course content quality."
    )
    parser.add_argument("--root", required=True, help="Target project root directory.")
    parser.add_argument("--emit", choices=["json", "text"], default="json")
    return parser.parse_args()


def relpath(path: Path, root: Path) -> str:
    try:
        return str(path.relative_to(root)).replace("\\", "/")
    except ValueError:
        return str(path).replace("\\", "/")


def md_files_under(path: Path) -> list[Path]:
    if not path.exists() or not path.is_dir():
        return []
    return [p for p in path.rglob("*.md") if p.is_file()]


def any_file_under(path: Path) -> bool:
    return any(p.is_file() for p in path.rglob("*") if p.exists())


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(encoding="utf-8", errors="replace")


def has_h1(markdown: str) -> bool:
    for line in markdown.splitlines():
        if line.lstrip().startswith("# "):
            return True
    return False


def has_setext_heading(markdown: str) -> bool:
    lines = markdown.splitlines()
    for idx in range(1, len(lines)):
        prev = lines[idx - 1].strip()
        cur = lines[idx].strip()
        if not prev:
            continue
        if re.fullmatch(r"=+", cur) or re.fullmatch(r"-+", cur):
            return True
    return False


def has_atx_heading(markdown: str) -> bool:
    return any(re.match(r"^\s*#{1,6}\s+", line) for line in markdown.splitlines())


def collect_prefixed_numbers(paths: list[Path]) -> list[int]:
    nums: list[int] = []
    for p in paths:
        m = re.match(r"^(\d{2})-", p.stem)
        if m:
            nums.append(int(m.group(1)))
    return sorted(set(nums))


def expected_sequence(numbers: list[int]) -> list[int]:
    if not numbers:
        return []
    return list(range(min(numbers), max(numbers) + 1))


def scan(root: Path) -> dict[str, object]:
    issues: list[Issue] = []

    docs_dir = root / "docs"
    project_brief = root / "docs/00-project/project-brief.md"
    outline_dir = root / "docs/01-outline"
    content_dir = root / "docs/02-content"
    labs_dir = root / "docs/03-labs"
    learner_dir = root / "docs/04-learner-pack"

    outline_files = md_files_under(outline_dir)
    content_files = md_files_under(content_dir)

    # 1) Scope completeness
    if not project_brief.is_file():
        issues.append(
            Issue(
                severity="blocker",
                clazz="structural",
                file="docs/00-project/project-brief.md",
                description="Missing required project brief for scope definition.",
            )
        )
    if not outline_files:
        issues.append(
            Issue(
                severity="blocker",
                clazz="structural",
                file="docs/01-outline",
                description="Outline directory has no markdown files.",
            )
        )
    if not content_files:
        issues.append(
            Issue(
                severity="blocker",
                clazz="structural",
                file="docs/02-content",
                description="Content directory has no markdown files.",
            )
        )

    # 2) Structural consistency
    kebab_pattern = re.compile(r"^(?:\d{2}-)?[a-z0-9]+(?:-[a-z0-9]+)*$")
    structural_targets = [outline_dir, content_dir, labs_dir, learner_dir]
    for base in structural_targets:
        for md in md_files_under(base):
            if not kebab_pattern.fullmatch(md.stem):
                issues.append(
                    Issue(
                        severity="minor",
                        clazz="structural",
                        file=relpath(md, root),
                        description="Filename should follow kebab-case with optional 2-digit prefix.",
                    )
                )

    for base in [outline_dir, content_dir]:
        if not base.exists():
            continue
        for directory in [base] + [p for p in base.rglob("*") if p.is_dir()]:
            files = [
                p
                for p in directory.iterdir()
                if p.is_file() and p.suffix.lower() == ".md"
            ]
            numbers = collect_prefixed_numbers(files)
            if len(numbers) <= 1:
                continue
            exp = expected_sequence(numbers)
            if numbers != exp:
                missing = [str(n).zfill(2) for n in exp if n not in numbers]
                issues.append(
                    Issue(
                        severity="minor",
                        clazz="structural",
                        file=relpath(directory, root),
                        description=f"Numbered prefixes are not sequential; missing: {', '.join(missing)}.",
                    )
                )

    # 3) Learning-objective alignment
    outline_text = (
        "\n".join(read_text(p) for p in outline_files) if outline_files else ""
    )
    outline_has_objective = bool(
        re.search(r"目标|objective", outline_text, flags=re.IGNORECASE)
    )
    if not outline_has_objective:
        issues.append(
            Issue(
                severity="major",
                clazz="pedagogical",
                file="docs/01-outline",
                description='Outline does not mention "目标" or "objective".',
            )
        )
    else:
        content_has_objective_ref = any(
            re.search(r"目标|objective", read_text(p), flags=re.IGNORECASE)
            for p in content_files
        )
        if not content_has_objective_ref:
            issues.append(
                Issue(
                    severity="major",
                    clazz="pedagogical",
                    file="docs/02-content",
                    description="Content files do not reference learning objectives from outline.",
                )
            )

    # 4) Content clarity
    marker_pattern = re.compile(
        "|".join(re.escape(marker) for marker in INTERNAL_MARKERS), flags=re.IGNORECASE
    )
    for md in content_files:
        text = read_text(md)
        match = marker_pattern.search(text)
        if match:
            issues.append(
                Issue(
                    severity="major",
                    clazz="formatting",
                    file=relpath(md, root),
                    description=f'Found internal work marker "{match.group(0)}" in content.',
                )
            )

    # 5) Lab executability
    if labs_dir.exists() and labs_dir.is_dir():
        for subdir in [p for p in labs_dir.iterdir() if p.is_dir()]:
            md_files = md_files_under(subdir)
            has_learner_guide = any(
                (
                    (
                        "learner" in md.stem
                        and ("guide" in md.stem or "manual" in md.stem)
                    )
                    or md.stem in {"learner-guide", "lab-guide", "guide", "readme"}
                )
                for md in md_files
            )
            if not has_learner_guide:
                issues.append(
                    Issue(
                        severity="major",
                        clazz="operational",
                        file=relpath(subdir, root),
                        description="Lab directory lacks learner guide style documentation.",
                    )
                )

    # 6) Learner/instructor separation
    if learner_dir.exists() and learner_dir.is_dir():
        leak_pattern = re.compile(
            "|".join(re.escape(k) for k in LEAK_KEYWORDS), flags=re.IGNORECASE
        )
        for file in [p for p in learner_dir.rglob("*") if p.is_file()]:
            if file.suffix.lower() not in {".md", ".txt"}:
                continue
            text = read_text(file)
            match = leak_pattern.search(text)
            if match:
                issues.append(
                    Issue(
                        severity="blocker",
                        clazz="operational",
                        file=relpath(file, root),
                        description=f'Learner material may leak instructor/answer content: "{match.group(0)}".',
                    )
                )

    # 7) Formatting consistency
    for md in md_files_under(docs_dir):
        text = read_text(md)
        if not has_h1(text):
            issues.append(
                Issue(
                    severity="minor",
                    clazz="formatting",
                    file=relpath(md, root),
                    description="Missing H1 heading (# ...).",
                )
            )
        if has_atx_heading(text) and has_setext_heading(text):
            issues.append(
                Issue(
                    severity="suggestion",
                    clazz="formatting",
                    file=relpath(md, root),
                    description="Mixed ATX and Setext heading styles in one markdown file.",
                )
            )

    # 8) Release readiness + scoring
    deduction = {"blocker": 20, "major": 10, "minor": 3, "suggestion": 1}
    score = 100
    blockers = 0
    for issue in issues:
        score -= deduction.get(issue.severity, 0)
        if issue.severity == "blocker":
            blockers += 1
    score = max(score, 0)

    if blockers > 0 or score < 60:
        recommendation = "not_ready"
    elif score >= 80:
        recommendation = "ready"
    else:
        recommendation = "conditional"

    status = "pass" if not issues else "issues_found"

    return {
        "status": status,
        "score": score,
        "issues": [issue.to_dict() for issue in issues],
        "release_recommendation": recommendation,
    }


def emit_text(result: dict[str, object]) -> str:
    lines = [
        f"status: {result['status']}",
        f"score: {result['score']}",
        f"release_recommendation: {result['release_recommendation']}",
        "issues:",
    ]
    raw_issues = result.get("issues", [])
    issues: list[dict[str, str]] = raw_issues if isinstance(raw_issues, list) else []
    if not issues:
        lines.append("  - none")
        return "\n".join(lines)

    for issue in issues:
        lines.append(
            "  - "
            f"[{issue['severity']}/{issue['class']}] "
            f"{issue['file']}: {issue['description']}"
        )
    return "\n".join(lines)


def main() -> None:
    args = parse_args()
    root = Path(args.root).expanduser().resolve()
    result = scan(root)

    if args.emit == "json":
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(emit_text(result))


if __name__ == "__main__":
    main()
