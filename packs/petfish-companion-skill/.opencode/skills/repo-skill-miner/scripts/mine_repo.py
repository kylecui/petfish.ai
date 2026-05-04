#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = []
# ///
"""Mine a repository for reusable skill candidates.

Usage:
  uv run mine_repo.py --repo .
  uv run mine_repo.py --repo https://github.com/owner/repo --depth quick
  uv run mine_repo.py --repo owner/repo --format json
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import textwrap
import urllib.error
import urllib.parse
import urllib.request
from collections.abc import Iterable
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path

IGNORE_DIRS = {
    ".git",
    ".hg",
    ".svn",
    ".idea",
    ".vscode",
    ".venv",
    "venv",
    "node_modules",
    "dist",
    "build",
    "coverage",
    ".mypy_cache",
    ".pytest_cache",
    "__pycache__",
}

README_NAMES = (
    "README.md",
    "README.mdx",
    "README.txt",
    "readme.md",
    "readme.txt",
)

SCRIPT_SUFFIXES = {".py", ".sh", ".ps1", ".bat", ".cmd", ".rb", ".js", ".ts"}
TASK_FILES = {
    "Makefile",
    "makefile",
    "Taskfile.yml",
    "Taskfile.yaml",
    "justfile",
    "Justfile",
}
PACKAGE_FILES = {
    "package.json",
    "pyproject.toml",
    "requirements.txt",
    "go.mod",
    "Cargo.toml",
    "pom.xml",
    "build.gradle",
    "build.gradle.kts",
    "composer.json",
}

DEPTH_LIMITS = {
    "quick": 250,
    "standard": 1200,
    "deep": 4000,
}


@dataclass
class RepoInfo:
    name: str
    source_type: str
    location: str
    description: str = ""
    stars: int | None = None
    topics: list[str] = field(default_factory=list)
    languages: list[str] = field(default_factory=list)
    default_branch: str = ""
    top_level_dirs: list[str] = field(default_factory=list)
    detected_domains: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "source_type": self.source_type,
            "location": self.location,
            "description": self.description,
            "stars": self.stars,
            "topics": self.topics,
            "languages": self.languages,
            "default_branch": self.default_branch,
            "top_level_dirs": self.top_level_dirs,
            "detected_domains": self.detected_domains,
        }


@dataclass
class CandidateSkill:
    name: str
    workflow: str
    boundary: str
    complexity: str
    required_tools: list[str]
    security_risks: list[str]
    evidence: list[str]
    reusability: int
    automation: int
    safety: int
    demand: int
    priority_score: float
    priority: str

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "workflow": self.workflow,
            "boundary": self.boundary,
            "complexity": self.complexity,
            "required_tools": self.required_tools,
            "security_risks": self.security_risks,
            "evidence": self.evidence,
            "scores": {
                "reusability": self.reusability,
                "automation": self.automation,
                "safety": self.safety,
                "demand": self.demand,
                "priority_score": round(self.priority_score, 2),
                "priority": self.priority,
            },
        }


@dataclass
class MiningReport:
    repository: RepoInfo
    reusable_workflows: list[str]
    candidate_skills: list[CandidateSkill]
    required_tools: list[str]
    security_risks: list[str]
    suggested_boundaries: list[str]
    not_suitable: list[str]
    priority_ranking: list[str]

    def to_dict(self) -> dict:
        return {
            "repository": self.repository.to_dict(),
            "reusable_workflows": self.reusable_workflows,
            "candidate_skills": [
                candidate.to_dict() for candidate in self.candidate_skills
            ],
            "required_tools": self.required_tools,
            "security_risks": self.security_risks,
            "suggested_skill_boundaries": self.suggested_boundaries,
            "not_suitable_for_skillization": self.not_suitable,
            "priority_ranking": self.priority_ranking,
        }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Analyze a local or GitHub repo and generate a skill mining report."
    )
    parser.add_argument(
        "--repo",
        required=True,
        help="Local path, GitHub URL, or owner/repo slug.",
    )
    parser.add_argument(
        "--output",
        default="outputs",
        help="Output directory for the generated report. Defaults to 'outputs/'.",
    )
    parser.add_argument(
        "--format",
        choices=["markdown", "json"],
        default="markdown",
        help="Report format. Defaults to markdown.",
    )
    parser.add_argument(
        "--depth",
        choices=["quick", "standard", "deep"],
        default="standard",
        help="How much of the repo tree to inspect. Defaults to standard.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Shortcut for --format json.",
    )
    return parser.parse_args()


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or "repository"


def classify_repo_target(target: str) -> tuple[str, str]:
    local_path = Path(target).expanduser()
    if local_path.exists():
        return "local", str(local_path.resolve())

    github_url = parse_github_target(target)
    if github_url:
        return "github", github_url

    raise ValueError(
        "--repo must be an existing local path, a GitHub URL, or owner/repo slug."
    )


def parse_github_target(target: str) -> str | None:
    target = target.strip()
    if not target:
        return None

    if target.startswith("https://github.com/") or target.startswith(
        "http://github.com/"
    ):
        parsed = urllib.parse.urlparse(target)
        parts = [part for part in parsed.path.split("/") if part]
        if len(parts) >= 2:
            owner = parts[0]
            repo = parts[1].removesuffix(".git")
            return f"{owner}/{repo}"
        return None

    if re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", target):
        return target
    return None


def read_text_file(path: Path, max_chars: int = 4000) -> str:
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return ""
    return text[:max_chars]


def summarize_readme(text: str) -> tuple[str, str]:
    if not text.strip():
        return "", ""

    title = ""
    summary = ""
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if not title and stripped.startswith("#"):
            title = stripped.lstrip("# ").strip()
            continue
        if not stripped.startswith("#") and not stripped.startswith("<"):
            summary = stripped
            break
    return title, summary


def walk_local_repo(repo_path: Path, depth: str) -> tuple[list[str], list[str]]:
    limit = DEPTH_LIMITS[depth]
    entries: list[str] = []
    top_level_dirs: list[str] = []

    for root, dirs, files in os.walk(repo_path):
        root_path = Path(root)
        dirs[:] = sorted(
            directory for directory in dirs if directory not in IGNORE_DIRS
        )
        files = sorted(files)

        rel_root = root_path.relative_to(repo_path)
        if rel_root == Path("."):
            top_level_dirs = [directory for directory in dirs]

        for directory in dirs:
            rel_dir = (rel_root / directory).as_posix()
            if rel_dir.startswith("./"):
                rel_dir = rel_dir[2:]
            if rel_dir:
                entries.append(f"{rel_dir}/")
            if len(entries) >= limit:
                return entries, top_level_dirs

        for file_name in files:
            rel_file = (rel_root / file_name).as_posix()
            if rel_file.startswith("./"):
                rel_file = rel_file[2:]
            if rel_file:
                entries.append(rel_file)
            if len(entries) >= limit:
                return entries, top_level_dirs

    return entries, top_level_dirs


def detect_languages_from_paths(paths: list[str]) -> list[str]:
    mapping = {
        ".py": "Python",
        ".js": "JavaScript",
        ".ts": "TypeScript",
        ".tsx": "TSX",
        ".jsx": "JSX",
        ".go": "Go",
        ".rs": "Rust",
        ".java": "Java",
        ".kt": "Kotlin",
        ".rb": "Ruby",
        ".php": "PHP",
        ".cs": "C#",
        ".cpp": "C++",
        ".c": "C",
        ".sh": "Shell",
        ".ps1": "PowerShell",
        ".swift": "Swift",
    }
    counter: Counter[str] = Counter()
    for entry in paths:
        suffix = Path(entry.rstrip("/")).suffix.lower()
        language = mapping.get(suffix)
        if language:
            counter[language] += 1
    return [name for name, _count in counter.most_common(5)]


def scan_local_repo(repo_path: Path, depth: str) -> dict:
    entries, top_level_dirs = walk_local_repo(repo_path, depth)

    readme_path = next(
        (repo_path / name for name in README_NAMES if (repo_path / name).is_file()),
        None,
    )
    readme_text = read_text_file(readme_path) if readme_path else ""
    _title, summary = summarize_readme(readme_text)

    return {
        "name": repo_path.name,
        "description": summary,
        "location": str(repo_path),
        "default_branch": "",
        "topics": [],
        "languages": detect_languages_from_paths(entries),
        "top_level_dirs": top_level_dirs,
        "tree_entries": entries,
        "readme_excerpt": readme_text,
    }


def github_headers() -> dict[str, str]:
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "PEtFiSh-repo-skill-miner/0.2.0",
    }
    token = os.environ.get("GITHUB_TOKEN", "")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def http_get_json(url: str) -> dict | list:
    request = urllib.request.Request(url, headers=github_headers())
    with urllib.request.urlopen(request, timeout=20) as response:
        return json.loads(response.read().decode("utf-8"))


def run_gh_json(args: list[str]) -> dict | list | None:
    try:
        completed = subprocess.run(
            ["gh", *args],
            check=False,
            capture_output=True,
            text=True,
        )
    except OSError:
        return None

    if completed.returncode != 0 or not completed.stdout.strip():
        return None

    try:
        return json.loads(completed.stdout)
    except json.JSONDecodeError:
        return None


def fetch_github_repo_metadata(owner_repo: str) -> dict:
    repo_url = f"https://api.github.com/repos/{owner_repo}"
    payload = http_get_json(repo_url)
    if not isinstance(payload, dict):
        raise ValueError(f"Could not fetch metadata for GitHub repo {owner_repo}.")

    languages_payload = http_get_json(
        payload.get("languages_url", repo_url + "/languages")
    )
    languages = []
    if isinstance(languages_payload, dict):
        languages = list(languages_payload.keys())

    return {
        "name": payload.get("name", owner_repo.split("/")[-1]),
        "description": payload.get("description") or "",
        "location": payload.get("html_url") or f"https://github.com/{owner_repo}",
        "default_branch": payload.get("default_branch") or "main",
        "stars": int(payload.get("stargazers_count", 0)),
        "topics": payload.get("topics") or [],
        "languages": languages,
    }


def list_github_tree(owner_repo: str, default_branch: str, depth: str) -> list[str]:
    tree_payload = run_gh_json(
        [
            "api",
            f"repos/{owner_repo}/git/trees/{default_branch}?recursive=1",
        ]
    )
    if isinstance(tree_payload, dict) and isinstance(tree_payload.get("tree"), list):
        tree_entries: list[str] = []
        for item in tree_payload["tree"]:
            path = item.get("path", "")
            if not path:
                continue
            suffix = "/" if item.get("type") == "tree" else ""
            tree_entries.append(f"{path}{suffix}")
            if len(tree_entries) >= DEPTH_LIMITS[depth]:
                break
        if tree_entries:
            return tree_entries

    root_url = f"https://api.github.com/repos/{owner_repo}/contents"
    root_payload = http_get_json(root_url)
    if not isinstance(root_payload, list):
        raise ValueError(
            f"Could not fetch directory listing for GitHub repo {owner_repo}."
        )

    tree_entries = []
    for item in root_payload:
        path = item.get("path", "")
        if not path:
            continue
        suffix = "/" if item.get("type") == "dir" else ""
        tree_entries.append(f"{path}{suffix}")

        if item.get("type") == "dir" and item.get("name") in {
            ".github",
            "scripts",
            "docs",
            "docker",
        }:
            sub_url = item.get("url")
            if not sub_url:
                continue
            try:
                sub_payload = http_get_json(sub_url)
            except (
                urllib.error.URLError,
                urllib.error.HTTPError,
                TimeoutError,
                OSError,
            ):
                continue
            if not isinstance(sub_payload, list):
                continue
            for child in sub_payload:
                child_path = child.get("path", "")
                if not child_path:
                    continue
                child_suffix = "/" if child.get("type") == "dir" else ""
                tree_entries.append(f"{child_path}{child_suffix}")
                if len(tree_entries) >= DEPTH_LIMITS[depth]:
                    return tree_entries

    return tree_entries[: DEPTH_LIMITS[depth]]


def scan_github_repo(owner_repo: str, depth: str) -> dict:
    metadata = fetch_github_repo_metadata(owner_repo)
    entries = list_github_tree(owner_repo, metadata["default_branch"], depth)
    top_level_dirs = sorted(
        {
            entry.rstrip("/")
            for entry in entries
            if entry.endswith("/") and "/" not in entry.rstrip("/")
        }
    )
    return {
        **metadata,
        "top_level_dirs": top_level_dirs,
        "tree_entries": entries,
        "readme_excerpt": "",
    }


def collect_signals(scan: dict, source_type: str) -> dict:
    entries = scan["tree_entries"]
    lower_entries = [entry.lower() for entry in entries]
    readme_excerpt = scan.get("readme_excerpt", "")
    search_text = "\n".join(
        [
            scan.get("name", ""),
            scan.get("description", ""),
            readme_excerpt,
            *scan.get("topics", []),
        ]
    ).lower()

    workflows = [entry for entry in entries if entry.startswith(".github/workflows/")]
    ci_configs = [
        entry
        for entry in entries
        if entry
        in {
            ".gitlab-ci.yml",
            "azure-pipelines.yml",
            "Jenkinsfile",
            ".circleci/config.yml",
        }
    ]
    dockerfiles = [
        entry
        for entry in entries
        if Path(entry.rstrip("/")).name.lower().startswith("dockerfile")
        or "docker-compose" in Path(entry.rstrip("/")).name.lower()
        or entry.startswith(".devcontainer/")
    ]
    task_files = [
        entry for entry in entries if Path(entry.rstrip("/")).name in TASK_FILES
    ]
    package_files = [
        entry for entry in entries if Path(entry.rstrip("/")).name in PACKAGE_FILES
    ]
    script_files = [
        entry
        for entry in entries
        if not entry.endswith("/")
        and (
            entry.startswith("scripts/")
            or entry.startswith("tools/")
            or entry.startswith("bin/")
            or Path(entry).suffix.lower() in SCRIPT_SUFFIXES
        )
    ]

    signals = {
        "workflows": workflows,
        "ci_configs": ci_configs,
        "dockerfiles": dockerfiles,
        "task_files": task_files,
        "package_files": package_files,
        "script_files": script_files,
        "has_release_signal": any(
            keyword in entry.lower()
            for entry in workflows + ci_configs + script_files
            for keyword in ("release", "publish", "deploy")
        ),
        "has_test_signal": any(
            keyword in entry.lower()
            for entry in workflows + task_files + script_files
            for keyword in ("test", "lint", "check", "verify")
        ),
        "is_docs_heavy": (
            (
                not workflows
                and not dockerfiles
                and not task_files
                and len(script_files) <= 1
            )
            and any(
                entry.startswith("docs/") or entry.startswith("book/")
                for entry in lower_entries
            )
        ),
        "search_text": search_text,
        "source_type": source_type,
    }
    return signals


def detect_domains(scan: dict, signals: dict) -> list[str]:
    search_text = signals["search_text"]
    lower_entries = "\n".join(entry.lower() for entry in scan["tree_entries"])
    domains: list[str] = []
    domain_rules = [
        ("AI apps", ["chat", "assistant", "copilot", "app", "ui", "prompt"]),
        ("Agent frameworks", ["agent", "langgraph", "crewai", "workflow", "orchestr"]),
        ("MCP", ["mcp", "model context protocol", "tool registry", "transport"]),
        ("RAG", ["rag", "retrieval", "embedding", "vector", "qdrant"]),
        (
            "System design",
            ["system design", "architecture", "distributed systems", "primer"],
        ),
        (
            "Dev tools",
            ["cli", "tooling", "lint", "ci", "workflow", "makefile", "docker"],
        ),
        ("Local model stacks", ["ollama", "llama.cpp", "local model", "quantization"]),
    ]

    combined = f"{search_text}\n{lower_entries}"
    for domain_name, keywords in domain_rules:
        if any(keyword in combined for keyword in keywords):
            domains.append(domain_name)
    return domains


def make_candidate(
    name: str,
    workflow: str,
    boundary: str,
    complexity: str,
    required_tools: list[str],
    security_risks: list[str],
    evidence: list[str],
    reusability: int,
    automation: int,
    safety: int,
    demand: int,
) -> CandidateSkill:
    priority_score = (
        reusability * 0.35 + automation * 0.30 + safety * 0.20 + demand * 0.15
    )
    if priority_score >= 4.0:
        priority = "high"
    elif priority_score >= 3.2:
        priority = "medium"
    else:
        priority = "low"

    return CandidateSkill(
        name=name,
        workflow=workflow,
        boundary=boundary,
        complexity=complexity,
        required_tools=required_tools,
        security_risks=security_risks,
        evidence=evidence[:5],
        reusability=reusability,
        automation=automation,
        safety=safety,
        demand=demand,
        priority_score=priority_score,
        priority=priority,
    )


def unique(items: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for item in items:
        if item and item not in seen:
            seen.add(item)
            ordered.append(item)
    return ordered


def derive_candidates(
    scan: dict, signals: dict
) -> tuple[list[CandidateSkill], list[str], list[str]]:
    candidates: list[CandidateSkill] = []
    reusable_workflows: list[str] = []
    not_suitable: list[str] = []
    needs_gh = signals["source_type"] == "github"

    if signals["workflows"] or signals["ci_configs"]:
        candidates.append(
            make_candidate(
                name="ci-workflow-triager",
                workflow="Inspect CI/CD configs, map checks to local commands, and reproduce safe failures outside the hosted runner.",
                boundary="Own workflow discovery, check selection, local reproduction, and failure summary. Do not dispatch release workflows or touch CI secrets.",
                complexity="medium" if not signals["has_release_signal"] else "high",
                required_tools=unique(["Read", "Bash"] + (["gh"] if needs_gh else [])),
                security_risks=[
                    "CI logs or workflow files may reference secrets or internal endpoints.",
                    "Release or deploy jobs can mutate registries, artifacts, or external environments.",
                ],
                evidence=signals["workflows"] + signals["ci_configs"],
                reusability=5,
                automation=4,
                safety=3 if signals["has_release_signal"] else 4,
                demand=4,
            )
        )
        reusable_workflows.append(
            "CI workflow discovery, local check reproduction, and failure triage"
        )

    if signals["task_files"] or signals["script_files"]:
        candidates.append(
            make_candidate(
                name="repo-task-runner",
                workflow="Discover documented task entrypoints in Makefiles or scripts, select safe targets, and execute them with explicit arguments.",
                boundary="Own task discovery, safe target selection, execution, and output capture. Do not run undocumented destructive targets by default.",
                complexity="medium",
                required_tools=unique(["Read", "Bash"]),
                security_risks=[
                    "Make targets or helper scripts can execute destructive shell commands.",
                    "Setup scripts may install packages, edit system state, or write credentials locally.",
                ],
                evidence=signals["task_files"] + signals["script_files"],
                reusability=5 if signals["task_files"] else 4,
                automation=5,
                safety=3,
                demand=4,
            )
        )
        reusable_workflows.append(
            "Task discovery and safe execution from repo-native scripts"
        )

    if signals["dockerfiles"]:
        candidates.append(
            make_candidate(
                name="container-env-bootstrap",
                workflow="Bootstrap the repo's Docker or devcontainer environment, verify services, and summarize runtime dependencies.",
                boundary="Own container config discovery, image/build command selection, runtime verification, and smoke-check reporting. Do not publish images or deploy containers remotely.",
                complexity="medium",
                required_tools=unique(["Read", "Bash", "Docker"]),
                security_risks=[
                    "Container builds may pull untrusted images or execute build hooks.",
                    "Compose files may expose ports, mount host paths, or reference secrets.",
                ],
                evidence=signals["dockerfiles"],
                reusability=4,
                automation=4,
                safety=3,
                demand=4,
            )
        )
        reusable_workflows.append(
            "Containerized environment bootstrap and smoke verification"
        )

    combined_text = signals["search_text"]
    if any(keyword in combined_text for keyword in ("mcp", "model context protocol")):
        candidates.append(
            make_candidate(
                name="mcp-server-tester",
                workflow="Inspect MCP server layout, identify transports and tool definitions, then verify safe startup and capability exposure.",
                boundary="Own repo inspection, startup instructions, tool surface mapping, and risk notes. Do not expose secrets or connect the server to sensitive data by default.",
                complexity="medium",
                required_tools=unique(["Read", "Bash"] + (["gh"] if needs_gh else [])),
                security_risks=[
                    "MCP servers may expose file, network, or credential access if started without sandboxing.",
                    "Tool definitions can imply high-risk actions even when the server code looks small.",
                ],
                evidence=[
                    entry for entry in scan["tree_entries"] if "mcp" in entry.lower()
                ]
                or [scan["name"]],
                reusability=4,
                automation=4,
                safety=3,
                demand=4,
            )
        )
        reusable_workflows.append(
            "MCP server discovery, startup verification, and tool-surface review"
        )

    if any(
        keyword in combined_text
        for keyword in ("agent", "langgraph", "crewai", "orchestr")
    ):
        candidates.append(
            make_candidate(
                name="agent-workflow-mapper",
                workflow="Trace agent, graph, or orchestration entrypoints and explain how the runtime pieces fit together for execution and debugging.",
                boundary="Own topology discovery, prompt/config location, runtime entrypoint mapping, and debugging handoff. Do not rewrite prompts or alter orchestration logic automatically.",
                complexity="high",
                required_tools=unique(["Read", "Bash"]),
                security_risks=[
                    "Agent workflows may call network tools, external models, or production integrations during smoke tests.",
                    "Prompt or tool configs can leak internal policies or identifiers.",
                ],
                evidence=[
                    entry
                    for entry in scan["tree_entries"]
                    if any(
                        token in entry.lower() for token in ("agent", "graph", "prompt")
                    )
                ]
                or [scan["name"]],
                reusability=4,
                automation=3,
                safety=3,
                demand=4,
            )
        )
        reusable_workflows.append(
            "Agent runtime topology mapping and debug-entrypoint discovery"
        )

    if any(
        keyword in combined_text
        for keyword in ("rag", "retrieval", "embedding", "vector", "qdrant")
    ):
        candidates.append(
            make_candidate(
                name="rag-pipeline-debugger",
                workflow="Locate ingestion, indexing, retrieval, and evaluation paths for a RAG stack and identify the minimum smoke-test loop.",
                boundary="Own pipeline discovery, config mapping, and safe validation recommendations. Do not reindex production data or mutate shared vector stores by default.",
                complexity="high",
                required_tools=unique(["Read", "Bash"]),
                security_risks=[
                    "Indexing workflows can consume large data sets or touch shared vector databases.",
                    "Retrieval tests may expose embedded private documents or sample queries.",
                ],
                evidence=[
                    entry
                    for entry in scan["tree_entries"]
                    if any(
                        token in entry.lower()
                        for token in ("rag", "retriev", "embed", "qdrant", "vector")
                    )
                ]
                or [scan["name"]],
                reusability=4,
                automation=3,
                safety=2,
                demand=4,
            )
        )
        reusable_workflows.append(
            "RAG ingestion and retrieval-path inspection with smoke-test planning"
        )

    if signals["is_docs_heavy"]:
        not_suitable.append(
            "The repo appears documentation-heavy with weak executable signals; summarize it as reference material before trying to turn it into a skill."
        )

    if (
        not signals["task_files"]
        and not signals["workflows"]
        and len(signals["script_files"]) <= 1
    ):
        not_suitable.append(
            "Thin or missing automation entrypoints: the repo may not contain stable workflows with clear agent inputs and outputs."
        )

    if any(
        entry.startswith("examples/") or entry.startswith("notebooks/")
        for entry in scan["tree_entries"]
    ):
        not_suitable.append(
            "Examples and notebooks are useful references, but they are not skills unless they map to a repeatable operator workflow."
        )

    not_suitable.extend(
        [
            "Generated artifacts, caches, vendored dependencies, and lockfile churn should never become skills.",
            "One-off maintainer release rituals that depend on private credentials should stay out of reusable skills unless heavily sandboxed.",
        ]
    )

    deduped_candidates = {candidate.name: candidate for candidate in candidates}
    return (
        list(deduped_candidates.values()),
        unique(reusable_workflows),
        unique(not_suitable),
    )


def build_report(scan: dict, source_type: str) -> MiningReport:
    signals = collect_signals(scan, source_type)
    repo_info = RepoInfo(
        name=scan["name"],
        source_type=source_type,
        location=scan["location"],
        description=scan.get("description", ""),
        stars=scan.get("stars"),
        topics=scan.get("topics", []),
        languages=scan.get("languages", []),
        default_branch=scan.get("default_branch", ""),
        top_level_dirs=scan.get("top_level_dirs", []),
    )
    repo_info.detected_domains = detect_domains(scan, signals)

    candidates, reusable_workflows, not_suitable = derive_candidates(scan, signals)
    candidates.sort(key=lambda item: item.priority_score, reverse=True)

    required_tools = unique(
        tool for candidate in candidates for tool in candidate.required_tools
    )
    security_risks = unique(
        risk for candidate in candidates for risk in candidate.security_risks
    )
    suggested_boundaries = [
        f"{candidate.name}: {candidate.boundary}" for candidate in candidates
    ]
    priority_ranking = [
        f"{index}. {candidate.name} ({candidate.priority}, score {candidate.priority_score:.2f})"
        for index, candidate in enumerate(candidates, start=1)
    ]

    if not candidates:
        reusable_workflows = reusable_workflows or [
            "No strong reusable workflow candidates were detected from the available repo signals."
        ]

    return MiningReport(
        repository=repo_info,
        reusable_workflows=reusable_workflows,
        candidate_skills=candidates,
        required_tools=required_tools,
        security_risks=security_risks,
        suggested_boundaries=suggested_boundaries,
        not_suitable=not_suitable,
        priority_ranking=priority_ranking,
    )


def markdown_table(candidates: list[CandidateSkill]) -> str:
    if not candidates:
        return "No strong skill candidates found."

    lines = [
        "| Name | Workflow | Complexity | Tools | Priority | Safety | Evidence |",
        "|---|---|---|---|---|---|---|",
    ]
    for candidate in candidates:
        evidence = "; ".join(candidate.evidence[:2]) or "n/a"
        tools = ", ".join(candidate.required_tools)
        workflow = candidate.workflow.replace("|", "/")
        lines.append(
            f"| {candidate.name} | {workflow} | {candidate.complexity} | {tools} | {candidate.priority} ({candidate.priority_score:.2f}) | {candidate.safety}/5 | {evidence} |"
        )
    return "\n".join(lines)


def render_markdown(report: MiningReport) -> str:
    repo = report.repository
    lines = ["# Repo Skill Mining Report", "", "## Repository Info", ""]
    lines.extend(
        [
            f"- **Name:** {repo.name}",
            f"- **Source:** {repo.source_type}",
            f"- **Location:** {repo.location}",
            f"- **Description:** {repo.description or 'n/a'}",
            f"- **Stars:** {repo.stars if repo.stars is not None else 'n/a'}",
            f"- **Topics:** {', '.join(repo.topics) if repo.topics else 'n/a'}",
            f"- **Languages:** {', '.join(repo.languages) if repo.languages else 'n/a'}",
            f"- **Default branch:** {repo.default_branch or 'n/a'}",
            f"- **Top-level directories:** {', '.join(repo.top_level_dirs) if repo.top_level_dirs else 'n/a'}",
            f"- **Detected domains:** {', '.join(repo.detected_domains) if repo.detected_domains else 'n/a'}",
            "",
            "## Candidate Skills",
            "",
            markdown_table(report.candidate_skills),
            "",
            "## Reusable Workflows",
            "",
        ]
    )
    lines.extend(
        f"- {workflow}"
        for workflow in report.reusable_workflows or ["No reusable workflows detected."]
    )
    lines.extend(["", "## Required Tools", ""])
    lines.extend(
        f"- {tool}" for tool in report.required_tools or ["- None identified yet"]
    )
    lines.extend(["", "## Security Risks", ""])
    lines.extend(
        f"- {risk}"
        for risk in report.security_risks
        or ["- No major risks identified from available signals"]
    )
    lines.extend(["", "## Suggested Skill Boundaries", ""])
    lines.extend(
        f"- {boundary}"
        for boundary in report.suggested_boundaries
        or ["- No boundary suggestions available"]
    )
    lines.extend(["", "## Not Suitable for Skillization", ""])
    lines.extend(f"- {item}" for item in report.not_suitable or ["- None noted"])
    lines.extend(["", "## Priority Ranking", ""])
    lines.extend(
        f"- {item}" for item in report.priority_ranking or ["- No ranked candidates"]
    )
    return "\n".join(lines).rstrip() + "\n"


def ensure_output_dir(path_str: str) -> Path:
    output_dir = Path(path_str).expanduser()
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir.resolve()


def write_report(report: MiningReport, output_dir: Path, output_format: str) -> Path:
    slug = slugify(report.repository.name)
    if output_format == "json":
        file_path = output_dir / f"{slug}-skill-mining-report.json"
        file_path.write_text(
            json.dumps(report.to_dict(), ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        return file_path

    file_path = output_dir / f"{slug}-skill-mining-report.md"
    file_path.write_text(render_markdown(report), encoding="utf-8")
    return file_path


def main() -> int:
    args = parse_args()
    output_format = "json" if args.json else args.format

    try:
        source_type, normalized_repo = classify_repo_target(args.repo)
        if source_type == "local":
            scan = scan_local_repo(Path(normalized_repo), args.depth)
        else:
            scan = scan_github_repo(normalized_repo, args.depth)

        report = build_report(scan, source_type)
        output_dir = ensure_output_dir(args.output)
        output_path = write_report(report, output_dir, output_format)
    except (
        ValueError,
        urllib.error.URLError,
        urllib.error.HTTPError,
        TimeoutError,
        OSError,
    ) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    print(f"Wrote {output_format} report to {output_path}")
    print(
        textwrap.dedent(
            f"""
            Candidates: {len(report.candidate_skills)}
            Domains: {", ".join(report.repository.detected_domains) if report.repository.detected_domains else "n/a"}
            Top priorities: {", ".join(candidate.name for candidate in report.candidate_skills[:3]) if report.candidate_skills else "none"}
            """
        ).strip()
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
