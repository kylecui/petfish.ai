#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = []
# ///
"""Pre-flight model audit for OpenCode (oh-my-opencode) long tasks.

Skill: opencode-session-doctor (pack: opencode-resilience-pack), layer L1.

Audits, before parallel/background task emission:
  1. Model references — every `model` / `fallback_models` entry in the config
     ("provider/model-id"), checked against the registry (provider present,
     model id present under that provider) and against auth (provider key
     EXISTS in auth.json — presence only, secret values are never read aloud,
     printed, or logged; the report says only "authenticated: yes/no").
  2. Agent alias consistency (best-effort) — config top-level agent keys vs
     AGENT_DISPLAY_NAMES-style display names found in the config/plugin
     section; keys that look like display names (spaces/uppercase/CJK) without
     a matching normalized registry key are flagged. Limitation: the plugin
     alias map lives inside plugin code, not JSON, so this check is heuristic.

Default paths (they vary by OS and install method — override with flags):
  config   ~/.config/opencode/oh-my-openagent.json
  registry ~/.cache/opencode/models.json
  auth     ~/.local/share/opencode/auth.json

Usage:
  uv run preflight_model_audit.py
  uv run preflight_model_audit.py --config c.json --registry m.json --auth a.json
  uv run preflight_model_audit.py --json

Exit codes: 0 = PASS, 1 = BLOCK (bad refs / registry missing / inconsistent
            agents), 2 = config file missing or usage error.
Stdlib only; no network access; no writes.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

DEFAULT_CONFIG = Path.home() / ".config" / "opencode" / "oh-my-openagent.json"
DEFAULT_REGISTRY = Path.home() / ".cache" / "opencode" / "models.json"
DEFAULT_AUTH = Path.home() / ".local" / "share" / "opencode" / "auth.json"

# A key that contains spaces, uppercase letters, or CJK characters looks like a
# display name rather than a registry key (registry keys are lowercase-hyphen).
DISPLAY_NAME_LIKE = re.compile(r"[\sA-Z\u4e00-\u9fff]")


def load_json(path: Path) -> dict:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid JSON in {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise ValueError(f"expected a JSON object at top level in {path}")
    return data


def collect_model_refs(node: object, refs: dict[str, int]) -> None:
    """Recursively collect `model` and `fallback_models` provider/model refs."""
    if isinstance(node, dict):
        for key, value in node.items():
            if key == "model" and isinstance(value, str) and "/" in value:
                refs[value] = refs.get(value, 0) + 1
            elif key == "fallback_models" and isinstance(value, list):
                for item in value:
                    if isinstance(item, str) and "/" in item:
                        refs[item] = refs.get(item, 0) + 1
            else:
                collect_model_refs(value, refs)
    elif isinstance(node, list):
        for item in node:
            collect_model_refs(item, refs)


def registry_model_ids(registry: dict, provider: str) -> set[str] | None:
    """Return model ids for a provider, or None if the provider is absent."""
    entry = registry.get(provider)
    if not isinstance(entry, dict):
        return None
    models = entry.get("models")
    if isinstance(models, dict):
        return set(models)
    # Fallback shape: provider maps directly to a model-id dict.
    return {key for key, value in entry.items() if isinstance(value, dict)}


def collect_display_names(node: object, names: set[str]) -> None:
    """Best-effort harvest of display names from plugin/config sections."""
    if isinstance(node, dict):
        for key, value in node.items():
            if "AGENT_DISPLAY_NAMES" in str(key) and isinstance(value, dict):
                for sub_value in value.values():
                    if isinstance(sub_value, str):
                        names.add(sub_value)
            else:
                collect_display_names(value, names)
    elif isinstance(node, list):
        for item in node:
            collect_display_names(item, names)


def audit_agent_aliases(config: dict) -> list[dict[str, str]]:
    """Flag agent keys that look like display names without a registry-key twin.

    Limitation: the plugin-side alias map is code, not JSON; this three-way
    check (config keys vs AGENT_DISPLAY_NAMES vs normalized twins) is
    best-effort and may produce false positives.
    """
    agent_section = config.get("agent") or config.get("agents") or {}
    if not isinstance(agent_section, dict):
        return []
    keys = [str(key) for key in agent_section]
    inconsistent: list[dict[str, str]] = []
    for key in keys:
        if DISPLAY_NAME_LIKE.search(key):
            twin = key.lower().replace(" ", "-").replace("_", "-")
            other_twins = {
                other.lower().replace(" ", "-").replace("_", "-")
                for other in keys
                if other != key
            }
            if twin == key or twin not in other_twins:
                inconsistent.append(
                    {
                        "key": key,
                        "reason": (
                            "looks like a display name without a matching "
                            "registry key (best-effort heuristic; plugin alias "
                            "map is code-side and not fully visible)"
                        ),
                    }
                )
    return inconsistent


def audit(config: dict, registry: dict | None, auth: dict | None) -> dict:
    refs: dict[str, int] = {}
    collect_model_refs(config, refs)

    refs_bad: list[dict[str, str]] = []
    notes: list[str] = []

    if registry is None:
        notes.append(
            "registry file missing — cannot validate providers/models; "
            "verdict forced to BLOCK"
        )
        for ref in sorted(refs):
            refs_bad.append({"ref": ref, "reason": "registry missing — cannot validate"})
    else:
        for ref in sorted(refs):
            provider, _, model_id = ref.partition("/")
            model_ids = registry_model_ids(registry, provider)
            if model_ids is None:
                refs_bad.append({"ref": ref, "reason": "provider not in registry"})
                continue
            if model_id not in model_ids:
                refs_bad.append(
                    {"ref": ref, "reason": "model id missing under provider"}
                )
                continue
            if auth is None or provider not in auth:
                refs_bad.append(
                    {"ref": ref, "reason": "provider not authenticated"}
                )

    if auth is None:
        notes.append(
            "auth file missing — every provider treated as unauthenticated"
        )

    agents_inconsistent = audit_agent_aliases(config)

    verdict = "BLOCK" if (refs_bad or agents_inconsistent) else "PASS"
    return {
        "refs_total": len(refs),
        "refs_bad": refs_bad,
        "agents_inconsistent": agents_inconsistent,
        "verdict": verdict,
        "notes": notes,
        "refs_ok": [
            ref for ref in sorted(refs) if all(b["ref"] != ref for b in refs_bad)
        ],
        "auth": auth,
    }


def print_human(result: dict, config_path: Path, registry_path: Path, auth_path: Path) -> None:
    auth = result["auth"]
    print("PEtFiSh preflight model audit (L1)")
    print(f"  config:   {config_path}")
    print(f"  registry: {registry_path}")
    print(f"  auth:     {auth_path}")
    print(f"refs: {result['refs_total']} unique model references")
    for ref in result["refs_ok"]:
        provider = ref.partition("/")[0]
        authenticated = "yes" if (auth is not None and provider in auth) else "no"
        print(f"  OK   {ref} (authenticated: {authenticated})")
    for bad in result["refs_bad"]:
        print(f"  BAD  {bad['ref']} — {bad['reason']}")
    print(f"agents: {len(result['agents_inconsistent'])} inconsistent")
    for item in result["agents_inconsistent"]:
        print(f"  INCONSISTENT  {item['key']} — {item['reason']}")
    for note in result["notes"]:
        print(f"  note: {note}")
    print(f"verdict: {result['verdict']}")
    if result["verdict"] == "BLOCK":
        print("Do NOT emit parallel/background tasks until refs_bad is empty.")


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Pre-flight model/agent audit before emitting parallel tasks."
    )
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG,
                        help=f"oh-my-openagent.json path (default: {DEFAULT_CONFIG})")
    parser.add_argument("--registry", type=Path, default=DEFAULT_REGISTRY,
                        help=f"models.json registry path (default: {DEFAULT_REGISTRY})")
    parser.add_argument("--auth", type=Path, default=DEFAULT_AUTH,
                        help=f"auth.json path (default: {DEFAULT_AUTH})")
    parser.add_argument("--json", action="store_true", help="machine-readable output")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)

    if not args.config.is_file():
        message = (
            f"error: config not found: {args.config}\n"
            "Pass --config <oh-my-openagent.json>; default paths vary by OS — "
            "see skill SKILL.md L1 section."
        )
        if args.json:
            print(json.dumps({"error": message}, ensure_ascii=False))
        else:
            print(message, file=sys.stderr)
        return 2

    try:
        config = load_json(args.config)
    except (ValueError, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    registry = None
    if args.registry.is_file():
        try:
            registry = load_json(args.registry)
        except (ValueError, OSError) as exc:
            print(f"warning: registry unreadable ({exc}); cannot validate", file=sys.stderr)
            registry = None

    auth = None
    if args.auth.is_file():
        try:
            auth = load_json(args.auth)
        except (ValueError, OSError) as exc:
            print(f"warning: auth file unreadable ({exc}); treating providers as unauthenticated", file=sys.stderr)
            auth = None

    result = audit(config, registry, auth)

    if args.json:
        payload = {
            "refs_total": result["refs_total"],
            "refs_bad": result["refs_bad"],
            "agents_inconsistent": result["agents_inconsistent"],
            "verdict": result["verdict"],
            "notes": result["notes"],
        }
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print_human(result, args.config, args.registry, args.auth)

    return 0 if result["verdict"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
