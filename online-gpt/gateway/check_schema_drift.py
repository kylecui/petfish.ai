# /// script
# requires-python = ">=3.10"
# ///

"""Compare OpenAPI schema parameters against Python handler signatures.

Reports DRIFT (schema params missing from handler), EXTRA (handler params
missing from schema), and MATCH for each POST operation.
"""

from __future__ import annotations

import argparse
import inspect
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

GATEWAY_DIR = Path(__file__).resolve().parent
REPO_ROOT = GATEWAY_DIR.parent.parent

GATEWAY_ONLY_YAML = REPO_ROOT / "online-gpt" / "actions" / "openapi.gateway-only.yaml"
FULL_YAML = REPO_ROOT / "online-gpt" / "actions" / "openapi.yaml"

try:
    import yaml

    HAS_YAML = True
except ImportError:
    HAS_YAML = False


def _get_indent(line: str) -> int:
    return len(line) - len(line.lstrip())


def _strip_comments(lines: List[str]) -> List[str]:
    out = []
    for line in lines:
        stripped = line.lstrip()
        if stripped.startswith("#"):
            continue
        out.append(line)
    return out


def _parse_block(lines: List[str], start: int, end: int, block_indent: int) -> Dict[str, Any]:
    result: Dict[str, Any] = {}
    i = start
    while i < end:
        line = lines[i]
        stripped = line.strip()
        if not stripped:
            i += 1
            continue
        indent = _get_indent(line)
        if indent < block_indent:
            break
        if indent > block_indent:
            i += 1
            continue

        colon_pos = stripped.find(":")
        if colon_pos < 1 or colon_pos == len(stripped) - 1:
            if colon_pos == len(stripped) - 1:
                key = stripped[:-1].strip().strip("'\"")
                child_start = i + 1
                child_indent = indent + 2
                child_end = child_start
                for j in range(child_start, end):
                    l = lines[j]
                    if not l.strip():
                        child_end = j + 1
                        continue
                    if _get_indent(l) < child_indent:
                        break
                    child_end = j + 1
                result[key] = _parse_block(lines, child_start, child_end, child_indent)
                i = child_end
            else:
                i += 1
            continue

        key = stripped[:colon_pos].strip().strip("'\"")
        after = stripped[colon_pos + 1 :].strip()

        if after.startswith("- ") or after == "-":
            items: List[Any] = []
            j = i
            while j < end:
                l = lines[j]
                l_stripped = l.strip()
                l_indent = _get_indent(l)
                if not l_stripped:
                    j += 1
                    continue
                if l_indent < indent:
                    break
                if l_indent == indent and l_stripped.startswith("- "):
                    items.append(l_stripped[2:].strip().strip("'\""))
                j += 1
            result[key] = items
            i = j
            continue

        if after:
            val = after.strip("'\"")
            if val.startswith("[") and val.endswith("]"):
                inner = val[1:-1]
                result[key] = [x.strip().strip("'\"") for x in inner.split(",") if x.strip()]
            else:
                result[key] = val
            i += 1
            continue

        child_start = i + 1
        child_indent = indent + 2
        child_end = child_start
        for j in range(child_start, end):
            l = lines[j]
            if not l.strip():
                child_end = j + 1
                continue
            if _get_indent(l) < child_indent:
                break
            child_end = j + 1

        result[key] = _parse_block(lines, child_start, child_end, child_indent)
        i = child_end

    return result


def parse_yaml(text: str) -> Dict[str, Any]:
    if HAS_YAML:
        return yaml.safe_load(text)
    lines = _strip_comments(text.splitlines())
    return _parse_block(lines, 0, len(lines), 0)


def extract_post_operations(yaml_data: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    ops: Dict[str, Dict[str, Any]] = {}
    paths = yaml_data.get("paths", {})
    if not isinstance(paths, dict):
        return ops
    for _path, path_item in paths.items():
        if not isinstance(path_item, dict):
            continue
        post = path_item.get("post")
        if not isinstance(post, dict):
            continue
        op_id = post.get("operationId")
        if not op_id:
            continue
        ops[op_id] = post
    return ops


def resolve_ref(ref: str, yaml_data: Dict[str, Any]) -> Dict[str, Any]:
    if not ref.startswith("#/"):
        return {}
    parts = ref[2:].split("/")
    node: Any = yaml_data
    for p in parts:
        if isinstance(node, dict):
            node = node.get(p, {})
        else:
            return {}
    return node if isinstance(node, dict) else {}


def extract_schema_params(op_data: Dict[str, Any], yaml_data: Dict[str, Any]) -> List[str]:
    rb = op_data.get("requestBody")
    if not isinstance(rb, dict):
        return []
    content = rb.get("content")
    if not isinstance(content, dict):
        return []
    json_schema = content.get("application/json", {}).get("schema")
    if not isinstance(json_schema, dict):
        return []

    if "$ref" in json_schema:
        resolved = resolve_ref(json_schema["$ref"], yaml_data)
        return sorted(resolved.get("properties", {}).keys())

    props = json_schema.get("properties")
    if isinstance(props, dict):
        return sorted(props.keys())

    return []


def get_handlers() -> Dict[str, Any]:
    if str(GATEWAY_DIR) not in sys.path:
        sys.path.insert(0, str(GATEWAY_DIR))

    import importlib

    op_to_func: Dict[str, Tuple[str, str]] = {
        "routeCompanionRequest": ("router", "route_companion_request"),
        "searchCatalog": ("modules.catalog", "search_catalog"),
        "suggestPacks": ("modules.profiler", "profile_project"),
        "renderInstallCommand": ("modules.installer", "render_install_command"),
        "profileProject": ("modules.profiler", "profile_project"),
        "designSkill": ("modules.skill_workbench", "design_skill"),
        "classifyActionRisk": ("modules.trust_gate", "classify_action"),
        "previewRemoteExecution": ("modules.remote_control", "preview_remote_execution"),
        "executeRemoteCommand": ("modules.remote_control", "execute_remote_command"),
    }

    handlers: Dict[str, Any] = {}
    for op_id, (mod_name, func_name) in op_to_func.items():
        try:
            mod = importlib.import_module(mod_name)
            handlers[op_id] = getattr(mod, func_name)
        except Exception:
            pass
    return handlers


def get_handler_params(func: Any) -> List[str]:
    sig = inspect.signature(func)
    return list(sig.parameters.keys())


def classify_drift_severity(drift_params: List[str]) -> str:
    dangerous = {"approval_token"}
    for p in drift_params:
        if p in dangerous:
            return "HIGH"
    if len(drift_params) > 2:
        return "MEDIUM"
    return "LOW"


def main() -> int:
    parser = argparse.ArgumentParser(description="Check schema drift between OpenAPI and handlers")
    parser.add_argument("--full", action="store_true", help="Use full openapi.yaml instead of gateway-only")
    parser.add_argument("--json", action="store_true", help="Only output JSON")
    args = parser.parse_args()

    yaml_path = FULL_YAML if args.full else GATEWAY_ONLY_YAML
    if not yaml_path.exists():
        print(f"Error: {yaml_path} not found", file=sys.stderr)
        return 1

    yaml_text = yaml_path.read_text(encoding="utf-8")
    yaml_data = parse_yaml(yaml_text)

    operations = extract_post_operations(yaml_data)
    handlers = get_handlers()

    results: Dict[str, Dict[str, Any]] = {}
    has_high_drift = False

    for op_id in sorted(operations):
        op_data = operations[op_id]
        schema_params = extract_schema_params(op_data, yaml_data)

        handler_func = handlers.get(op_id)
        handler_name = handler_func.__name__ if handler_func else "<not found>"
        handler_params = get_handler_params(handler_func) if handler_func else []

        drift = sorted(set(schema_params) - set(handler_params))
        extra = sorted(set(handler_params) - set(schema_params))

        severity = classify_drift_severity(drift) if drift else None
        if severity == "HIGH":
            has_high_drift = True

        status = "DRIFT" if (drift or extra) else "MATCH"

        results[op_id] = {
            "handler": handler_name,
            "schema_params": schema_params,
            "handler_params": handler_params,
            "drift": drift,
            "extra_in_handler": extra,
            "severity": severity if drift else None,
            "status": status,
        }

    total = len(results)
    match_count = sum(1 for r in results.values() if r["status"] == "MATCH")
    drift_count = sum(1 for r in results.values() if r["status"] == "DRIFT")
    drift_ops = [op for op, r in results.items() if r["status"] == "DRIFT"]

    output = {
        "file": str(yaml_path.name),
        "operations": results,
        "summary": {
            "total": total,
            "match": match_count,
            "drift": drift_count,
            "drift_operations": drift_ops,
        },
    }

    json_out = json.dumps(output, indent=2, ensure_ascii=False)
    print(json_out)

    if not args.json:
        print(f"\n{'=' * 60}", file=sys.stderr)
        print(f"Schema Drift Report: {yaml_path.name}", file=sys.stderr)
        print(f"{'=' * 60}", file=sys.stderr)
        for op_id, r in results.items():
            icon = "OK" if r["status"] == "MATCH" else "!!"
            print(f"\n  [{icon}] {op_id} -> {r['handler']}", file=sys.stderr)
            print(f"      schema:  {r['schema_params']}", file=sys.stderr)
            print(f"      handler: {r['handler_params']}", file=sys.stderr)
            if r["drift"]:
                print(f"      DRIFT ({r.get('severity', 'N/A')}): {r['drift']}", file=sys.stderr)
            if r["extra_in_handler"]:
                print(f"      EXTRA:   {r['extra_in_handler']}", file=sys.stderr)
        print(f"\n  Total: {total} | Match: {match_count} | Drift: {drift_count}", file=sys.stderr)
        if drift_ops:
            print(f"  Drift operations: {drift_ops}", file=sys.stderr)
        print(f"{'=' * 60}", file=sys.stderr)

    if has_high_drift:
        print("FAIL: HIGH severity drift detected.", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
