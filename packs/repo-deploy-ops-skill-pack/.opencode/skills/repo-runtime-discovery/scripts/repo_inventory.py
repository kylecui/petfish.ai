#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.11"
# ///
"""Inspect a repository and emit deployment-oriented inventory as JSON."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

try:
    import tomllib  # py311+
except Exception:  # pragma: no cover
    tomllib = None  # type: ignore


TOP_LEVEL_FILES = [
    "README.md",
    "README",
    "Makefile",
    "Taskfile.yml",
    "Taskfile.yaml",
    "Dockerfile",
    "docker-compose.yml",
    "compose.yaml",
    "package.json",
    "pyproject.toml",
    "requirements.txt",
    "uv.lock",
    "go.mod",
    "Cargo.toml",
    "pom.xml",
    "build.gradle",
    "build.gradle.kts",
    "Procfile",
    ".env.example",
    ".env.sample",
    ".env.template",
]


def slurp(path: Path, limit: int = 40000) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")[:limit]
    except Exception:
        return ""


def detect_files(root: Path) -> dict[str, list[str]]:
    EXCLUDE_DIRS = {
        "node_modules",
        ".venv",
        "venv",
        "__pycache__",
        ".git",
        ".hg",
        "vendor",
        ".tox",
        ".mypy_cache",
        ".pytest_cache",
        "dist",
        "build",
        ".eggs",
    }
    hits: dict[str, list[str]] = {
        "dockerfiles": [],
        "compose_files": [],
        "k8s_files": [],
        "helm_charts": [],
        "systemd_units": [],
        "env_examples": [],
        "deploy_dirs": [],
        "test_dirs": [],
        "docs": [],
    }
    for path in root.rglob("*"):
        if path.is_dir():
            continue
        # Skip files inside excluded vendor/cache directories
        rel_parts = path.relative_to(root).parts
        if any(part in EXCLUDE_DIRS for part in rel_parts):
            continue
        rp = path.relative_to(root).as_posix()
        name = path.name.lower()
        if name.startswith("dockerfile"):
            hits["dockerfiles"].append(rp)
        if name in {
            "docker-compose.yml",
            "docker-compose.yaml",
            "compose.yml",
            "compose.yaml",
        }:
            hits["compose_files"].append(rp)
        if (
            "/k8s/" in f"/{rp}/"
            or name.endswith((".yaml", ".yml"))
            and any(token in rp.lower() for token in ("k8s", "kubernetes", "manifests"))
        ):
            hits["k8s_files"].append(rp)
        if name == "chart.yaml" or "/helm/" in f"/{rp}/":
            hits["helm_charts"].append(rp)
        if name.endswith(".service") or name.endswith(".socket"):
            hits["systemd_units"].append(rp)
        if name in {".env.example", ".env.sample", ".env.template"}:
            hits["env_examples"].append(rp)
        if (
            any(
                part in {"deploy", "deployment", "ops", "infra", "scripts"}
                for part in path.parts
            )
            and not any(
                part.startswith(".") for part in path.relative_to(root).parts[:-1]
            )
            and not any(
                part in {"skills", "skill"} for part in path.relative_to(root).parts
            )
        ):
            hits["deploy_dirs"].append(rp)
        if any(part in {"tests", "test", "__tests__", "e2e"} for part in path.parts):
            hits["test_dirs"].append(rp)
        if name.startswith("readme") or name.endswith(".md"):
            hits["docs"].append(rp)
    for k in hits:
        hits[k] = sorted(set(hits[k]))[:100]
    return hits


def detect_languages(root: Path) -> dict[str, bool]:
    return {
        "python": (root / "pyproject.toml").exists()
        or (root / "requirements.txt").exists(),
        "node": (root / "package.json").exists(),
        "go": (root / "go.mod").exists(),
        "rust": (root / "Cargo.toml").exists(),
        "java_maven": (root / "pom.xml").exists(),
        "java_gradle": (root / "build.gradle").exists()
        or (root / "build.gradle.kts").exists(),
    }


def parse_package_json(root: Path) -> dict[str, Any]:
    path = root / "package.json"
    if not path.exists():
        return {}
    try:
        data = json.loads(slurp(path))
    except Exception:
        return {}
    return {
        "name": data.get("name"),
        "packageManager": data.get("packageManager"),
        "scripts": data.get("scripts", {}),
        "dependencies_count": len(data.get("dependencies", {})),
        "dev_dependencies_count": len(data.get("devDependencies", {})),
    }


def parse_pyproject(root: Path) -> dict[str, Any]:
    path = root / "pyproject.toml"
    if not path.exists() or tomllib is None:
        return {}
    try:
        data = tomllib.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}
    project = data.get("project", {})
    tool = data.get("tool", {})
    return {
        "name": project.get("name"),
        "requires_python": project.get("requires-python"),
        "scripts": project.get("scripts", {}),
        "uv": bool(tool.get("uv")),
        "poetry": bool(tool.get("poetry")),
        "setuptools": bool(tool.get("setuptools")),
    }


def parse_readme_hints(root: Path) -> dict[str, list[str]]:
    text = ""
    for candidate in ("README.md", "README", "README.txt"):
        path = root / candidate
        if path.exists():
            text = slurp(path, 50000)
            break
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    run_hints, env_hints, port_hints = [], [], []
    for line in lines:
        low = line.lower()
        if any(
            token in low
            for token in (
                "docker compose",
                "docker-compose",
                "uv run",
                "npm run",
                "pnpm",
                "yarn",
                "python ",
                "gunicorn",
                "uvicorn",
                "go run",
                "java -jar",
                "cargo run",
                "systemctl",
            )
        ):
            run_hints.append(line[:300])
        if any(
            token in low
            for token in (
                "env",
                "environment variable",
                ".env",
                "secret",
                "api key",
                "token",
                "database url",
                "redis",
            )
        ):
            env_hints.append(line[:300])
        if "port" in low or re.search(r":\d{2,5}\b", line):
            port_hints.append(line[:300])
    return {
        "run_hints": run_hints[:20],
        "env_hints": env_hints[:20],
        "port_hints": port_hints[:20],
    }


def guess_candidate_methods(
    hits: dict[str, list[str]],
    langs: dict[str, bool],
    pkg: dict[str, Any],
    pyproj: dict[str, Any],
) -> list[str]:
    methods: list[str] = []
    if hits["compose_files"]:
        methods.append("docker-compose")
    if hits["dockerfiles"]:
        methods.append("docker")
    if hits["helm_charts"] or hits["k8s_files"]:
        methods.append("kubernetes")
    if hits["systemd_units"]:
        methods.append("systemd")
    if pkg:
        methods.append("node-runtime-or-build")
    if pyproj or langs["python"]:
        methods.append("python-venv-or-uv-plus-systemd")
    if langs["go"] or langs["rust"]:
        methods.append("build-binary-plus-systemd-or-container")
    if langs["java_maven"] or langs["java_gradle"]:
        methods.append("jar-plus-systemd-or-container")
    return list(dict.fromkeys(methods))


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Inspect repository structure and emit deployment-oriented JSON inventory."
    )
    parser.add_argument("--root", default=".", help="Repository root path")
    parser.add_argument(
        "--output", default="-", help="Output file path or - for stdout"
    )
    args = parser.parse_args()

    root = Path(args.root).resolve()
    if not root.exists():
        print(json.dumps({"error": f"root does not exist: {root}"}))
        return 2

    hits = detect_files(root)
    langs = detect_languages(root)
    pkg = parse_package_json(root)
    pyproj = parse_pyproject(root)
    readme = parse_readme_hints(root)

    data: dict[str, Any] = {
        "root": str(root),
        "top_level_present": [f for f in TOP_LEVEL_FILES if (root / f).exists()],
        "languages": langs,
        "signals": hits,
        "package_json": pkg,
        "pyproject": pyproj,
        "readme_hints": readme,
        "candidate_deployment_methods": guess_candidate_methods(
            hits, langs, pkg, pyproj
        ),
        "summary": {
            "has_container_signals": bool(hits["dockerfiles"] or hits["compose_files"]),
            "has_k8s_signals": bool(hits["k8s_files"] or hits["helm_charts"]),
            "has_systemd_signals": bool(hits["systemd_units"]),
            "has_test_material": bool(hits["test_dirs"]),
            "has_env_examples": bool(hits["env_examples"]),
        },
        "next_checks": [
            "Confirm required environment variables and secrets",
            "Confirm runtime dependencies such as database, cache, MQ, TLS, volumes",
            "Confirm build command, start command, and health endpoint",
            "Choose deployment method based on repo signals and target host capabilities",
        ],
    }

    payload = json.dumps(data, ensure_ascii=False, indent=2)
    if args.output == "-":
        print(payload)
    else:
        Path(args.output).write_text(payload + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
