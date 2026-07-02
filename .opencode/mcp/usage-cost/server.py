"""Usage-Cost MCP Server — stdio JSON-RPC 2.0 server for token usage tracking.

Tracks model usage costs, checks budget limits, records usage, and provides
cost estimates. Uses only Python stdlib.

Usage:
    python server.py [--usage-dir .petfish/state]
    # Or via opencode.json MCP config (stdio transport)
"""

import json
import os
import sys
from datetime import datetime, timedelta, timezone
from typing import Any, Callable, Dict, List, Optional


# ---------------------------------------------------------------------------
# Minimal MCP server over stdio (LSP base protocol framing)
# Auto-detects transport: Content-Length headers vs bare JSONL.
# ---------------------------------------------------------------------------

_transport_mode: Optional[str] = None


def _read_message(stream) -> Optional[Dict[str, Any]]:
    """Read one JSON-RPC message. Auto-detects transport on the first call."""
    global _transport_mode

    while True:
        first_line = stream.readline()
        if not first_line:
            return None  # EOF
        if isinstance(first_line, bytes):
            first_line = first_line.decode("utf-8")
        stripped = first_line.strip()
        if stripped == "":
            continue
        break

    # Auto-detect on first non-blank line
    if _transport_mode is None:
        if stripped.startswith("{"):
            _transport_mode = "jsonl"
        else:
            _transport_mode = "clength"

    # JSONL transport
    if _transport_mode == "jsonl":
        if stripped.startswith("{"):
            return json.loads(stripped)
        return _read_message(stream)

    # Content-Length transport
    headers = {}
    if ":" in stripped:
        key, value = stripped.split(":", 1)
        headers[key.strip().lower()] = value.strip()

    while True:
        line = stream.readline()
        if not line:
            return None
        if isinstance(line, bytes):
            line = line.decode("utf-8")
        line = line.rstrip("\r\n")
        if line == "":
            break
        if ":" in line:
            key, value = line.split(":", 1)
            headers[key.strip().lower()] = value.strip()

    length = int(headers.get("content-length", 0))
    if length == 0:
        return None

    body = stream.read(length)
    if isinstance(body, bytes):
        body = body.decode("utf-8")
    return json.loads(body)


def _write_message(stream, msg: Dict[str, Any]) -> None:
    """Write one JSON-RPC message using the detected transport mode."""
    body = json.dumps(msg, ensure_ascii=False)

    if _transport_mode == "jsonl":
        line = body + "\n"
        stream.write(line.encode("utf-8") if hasattr(stream, "mode") else line)
    else:
        body_bytes = body.encode("utf-8")
        header = "Content-Length: {}\r\n\r\n".format(len(body_bytes))
        stream.write(header.encode("utf-8") if hasattr(stream, "mode") else header)
        stream.write(body_bytes if hasattr(stream, "mode") else body)
    stream.flush()


def _jsonrpc_response(id: Any, result: Any) -> Dict[str, Any]:
    return {"jsonrpc": "2.0", "id": id, "result": result}


def _jsonrpc_error(id: Any, code: int, message: str, data: Any = None) -> Dict[str, Any]:
    err = {"jsonrpc": "2.0", "id": id, "error": {"code": code, "message": message}}
    if data is not None:
        err["error"]["data"] = data
    return err


# ---------------------------------------------------------------------------
# Tool definitions (MCP tools/list response)
# ---------------------------------------------------------------------------

TOOLS = [
    {
        "name": "get_pricing",
        "description": "Get pricing information for all configured models. Returns providers, models with input/output costs per million tokens.",
        "inputSchema": {
            "type": "object",
            "properties": {},
        },
    },
    {
        "name": "check_budget",
        "description": "Check budget status by comparing recorded usage against configured limits. Returns {status: ok|warning|exceeded, daily_used, daily_limit, weekly_used, weekly_limit}.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "project_root": {
                    "type": "string",
                    "description": "Project root directory for reading usage.jsonl (default: current working directory)",
                },
            },
        },
    },
    {
        "name": "list_models",
        "description": "List all configured models with their pricing tiers and provider information.",
        "inputSchema": {
            "type": "object",
            "properties": {},
        },
    },
    {
        "name": "record_usage",
        "description": "Record a token usage event to usage.jsonl. Writes {timestamp, model, input_tokens, output_tokens, estimated_cost, session_id}.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "model": {
                    "type": "string",
                    "description": "Model name (e.g., deepseek/deepseek-v4-pro)",
                },
                "input_tokens": {
                    "type": "integer",
                    "description": "Number of input tokens consumed",
                },
                "output_tokens": {
                    "type": "integer",
                    "description": "Number of output tokens consumed",
                },
                "session_id": {
                    "type": "string",
                    "description": "Session ID for correlation",
                },
                "project_root": {
                    "type": "string",
                    "description": "Project root directory (default: current working directory)",
                },
            },
            "required": ["model", "input_tokens", "output_tokens"],
        },
    },
    {
        "name": "get_usage_summary",
        "description": "Aggregate usage records from usage.jsonl by session/task. Returns total cost breakdown, per-session summaries, and daily costs.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "session_id": {
                    "type": "string",
                    "description": "Filter by specific session ID (optional)",
                },
                "days": {
                    "type": "integer",
                    "description": "Number of recent days to summarize (default: 30)",
                },
                "project_root": {
                    "type": "string",
                    "description": "Project root directory (default: current working directory)",
                },
            },
        },
    },
    {
        "name": "estimate_cost",
        "description": "Estimate cost for a model given token counts. Returns estimated cost in CNY without recording.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "model": {
                    "type": "string",
                    "description": "Model name (e.g., deepseek/deepseek-v4-pro)",
                },
                "input_tokens": {
                    "type": "integer",
                    "description": "Number of input tokens",
                },
                "output_tokens": {
                    "type": "integer",
                    "description": "Number of output tokens",
                },
            },
            "required": ["model", "input_tokens", "output_tokens"],
        },
    },
]


# ---------------------------------------------------------------------------
# Config loader
# ---------------------------------------------------------------------------

_CONFIG_PATH = os.path.expanduser("~/.config/opencode/token-tracker.json")


def load_config() -> Dict[str, Any]:
    """Load token-tracker.json. Returns empty dict with defaults if missing."""
    if not os.path.exists(_CONFIG_PATH):
        return _default_config()
    try:
        with open(_CONFIG_PATH, "r", encoding="utf-8") as f:
            cfg = json.load(f)
        # Merge with defaults for missing sections
        defaults = _default_config()
        for key in defaults:
            if key not in cfg:
                cfg[key] = defaults[key]
        return cfg
    except (OSError, json.JSONDecodeError):
        return _default_config()


def _default_config() -> Dict[str, Any]:
    return {
        "providers": {},
        "models": {},
        "budget": {
            "daily": 35.0,
            "weekly": 250.0,
            "monthly": 1000.0,
            "warnAt": 0.8,
        },
    }


# ---------------------------------------------------------------------------
# Cost calculation
# ---------------------------------------------------------------------------

def _calculate_cost(model: str, input_tokens: int, output_tokens: int, config: Dict[str, Any]) -> float:
    """Calculate cost in CNY for a given model and token counts.

    Formula: (input_tokens * input_price + output_tokens * output_price) / 1_000_000
    All prices in CNY per million tokens.
    """
    models = config.get("models", {})
    providers = config.get("providers", {})

    # Try exact model match first
    model_info = models.get(model)
    if model_info:
        input_price = model_info.get("input", 0)
        output_price = model_info.get("output", 0)
    else:
        # Try provider-level pricing fallback
        provider = model.split("/")[0] if "/" in model else model
        provider_info = providers.get(provider)
        if provider_info:
            input_price = provider_info.get("input", 0)
            output_price = provider_info.get("output", 0)
        else:
            input_price = 0
            output_price = 0

    cost = (input_tokens * input_price + output_tokens * output_price) / 1_000_000
    return round(cost, 6)


# ---------------------------------------------------------------------------
# Usage file helpers
# ---------------------------------------------------------------------------

def _usage_file_path(project_root: str) -> str:
    """Get path to usage.jsonl for a project."""
    return os.path.join(project_root, ".petfish", "state", "usage.jsonl")


def _ensure_usage_dir(project_root: str) -> None:
    """Ensure .petfish/state/ directory exists."""
    usage_dir = os.path.join(project_root, ".petfish", "state")
    os.makedirs(usage_dir, exist_ok=True)


def _read_usage_records(project_root: str) -> List[Dict[str, Any]]:
    """Read all usage records from usage.jsonl."""
    path = _usage_file_path(project_root)
    records = []
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        try:
                            records.append(json.loads(line))
                        except json.JSONDecodeError:
                            continue
        except OSError:
            pass
    return records


# ---------------------------------------------------------------------------
# Server
# ---------------------------------------------------------------------------

class UsageCostServer:
    """MCP server for usage cost tracking."""

    def __init__(self, default_project_root: str = "."):
        self._default_project_root = os.path.abspath(default_project_root)
        self._handlers: Dict[str, Callable] = {}
        self._register_handlers()

    # -- Handler registration -----------------------------------------------

    def _register_handlers(self) -> None:
        h = self._handlers
        h["get_pricing"] = self._handle_get_pricing
        h["check_budget"] = self._handle_check_budget
        h["list_models"] = self._handle_list_models
        h["record_usage"] = self._handle_record_usage
        h["get_usage_summary"] = self._handle_get_usage_summary
        h["estimate_cost"] = self._handle_estimate_cost

    # -- JSON-RPC dispatch --------------------------------------------------

    def handle_message(self, msg: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        method = msg.get("method", "")
        msg_id = msg.get("id")
        params = msg.get("params", {})

        if method == "initialize":
            return _jsonrpc_response(
                msg_id,
                {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {"tools": {}},
                    "serverInfo": {"name": "usage-cost", "version": "0.1.0"},
                },
            )

        if method == "notifications/initialized":
            return None

        if method == "tools/list":
            return _jsonrpc_response(msg_id, {"tools": TOOLS})

        if method == "tools/call":
            return self._dispatch_tool_call(msg_id, params)

        if method == "ping":
            return _jsonrpc_response(msg_id, {})

        if msg_id is not None:
            return _jsonrpc_error(msg_id, -32601, "Method not found: {}".format(method))
        return None

    def _dispatch_tool_call(self, msg_id: Any, params: Dict[str, Any]) -> Dict[str, Any]:
        tool_name = params.get("name", "")
        arguments = params.get("arguments", {})

        handler = self._handlers.get(tool_name)
        if handler is None:
            return _jsonrpc_error(msg_id, -32602, "Unknown tool: {}".format(tool_name))

        try:
            result = handler(arguments)
            return _jsonrpc_response(
                msg_id,
                {
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps(result, ensure_ascii=False, indent=2),
                        }
                    ],
                },
            )
        except KeyError as exc:
            return _jsonrpc_response(
                msg_id,
                {
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps({"error": str(exc)}, ensure_ascii=False),
                        }
                    ],
                    "isError": True,
                },
            )
        except (ValueError, TypeError) as exc:
            return _jsonrpc_response(
                msg_id,
                {
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps({"error": str(exc)}, ensure_ascii=False),
                        }
                    ],
                    "isError": True,
                },
            )
        except Exception as exc:
            return _jsonrpc_error(msg_id, -32603, "Internal error: {}".format(exc))

    # -- Tool handlers ------------------------------------------------------

    def _handle_get_pricing(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Return full pricing config from token-tracker.json."""
        config = load_config()
        return {
            "providers": config.get("providers", {}),
            "models": config.get("models", {}),
            "budget": config.get("budget", {}),
            "config_source": _CONFIG_PATH,
        }

    def _handle_check_budget(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Check budget status: compare recorded usage against limits."""
        project_root = os.path.abspath(args.get("project_root", self._default_project_root))
        config = load_config()
        budget = config.get("budget", _default_config()["budget"])
        warn_at = budget.get("warnAt", 0.8)

        daily_limit = budget.get("daily", 35.0)
        weekly_limit = budget.get("weekly", 250.0)

        records = _read_usage_records(project_root)

        # Calculate daily usage (today, UTC)
        now = datetime.now(timezone.utc)
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        daily_used = 0.0

        # Calculate weekly usage (last 7 days)
        week_ago = now - timedelta(days=7)
        weekly_used = 0.0

        for rec in records:
            try:
                ts_str = rec.get("timestamp", "")
                if ts_str:
                    ts = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
                    cost = float(rec.get("estimated_cost", 0))

                    if ts >= today_start:
                        daily_used += cost
                    if ts >= week_ago:
                        weekly_used += cost
            except (ValueError, TypeError):
                continue

        daily_used = round(daily_used, 6)
        weekly_used = round(weekly_used, 6)

        # Determine status
        if daily_used > daily_limit or weekly_used > weekly_limit:
            status = "exceeded"
        elif daily_used >= daily_limit * warn_at or weekly_used >= weekly_limit * warn_at:
            status = "warning"
        else:
            status = "ok"

        return {
            "status": status,
            "daily_used": daily_used,
            "daily_limit": daily_limit,
            "daily_remaining": round(daily_limit - daily_used, 6),
            "daily_percent": round((daily_used / daily_limit * 100) if daily_limit > 0 else 0, 1),
            "weekly_used": weekly_used,
            "weekly_limit": weekly_limit,
            "weekly_remaining": round(weekly_limit - weekly_used, 6),
            "weekly_percent": round((weekly_used / weekly_limit * 100) if weekly_limit > 0 else 0, 1),
            "warn_at": warn_at,
            "monthly_limit": budget.get("monthly", 1000.0),
            "records_count": len(records),
        }

    def _handle_list_models(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """List all configured models with pricing."""
        config = load_config()
        models = config.get("models", {})
        providers = config.get("providers", {})

        model_list = []
        for model_name, model_info in models.items():
            entry = {
                "name": model_name,
                "input_price": model_info.get("input", 0),
                "output_price": model_info.get("output", 0),
                "input_unit": "CNY per million tokens",
                "output_unit": "CNY per million tokens",
            }
            # Attach provider info if available
            provider = model_name.split("/")[0] if "/" in model_name else None
            if provider and provider in providers:
                entry["provider"] = provider
                entry["provider_input_price"] = providers[provider].get("input", 0)
                entry["provider_output_price"] = providers[provider].get("output", 0)
            model_list.append(entry)

        # Also list providers without specific models
        for provider_name, provider_info in providers.items():
            p_entry = {
                "name": provider_name,
                "input_price": provider_info.get("input", 0),
                "output_price": provider_info.get("output", 0),
                "input_unit": "CNY per million tokens",
                "output_unit": "CNY per million tokens",
                "is_provider_default": True,
            }
            model_list.append(p_entry)

        return {
            "models": model_list,
            "total_models": len(models),
            "total_providers": len(providers),
            "config_source": _CONFIG_PATH,
        }

    def _handle_record_usage(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Record a usage event to usage.jsonl."""
        project_root = os.path.abspath(args.get("project_root", self._default_project_root))
        model = args["model"]
        input_tokens = int(args["input_tokens"])
        output_tokens = int(args["output_tokens"])
        session_id = args.get("session_id", "")

        config = load_config()
        estimated_cost = _calculate_cost(model, input_tokens, output_tokens, config)

        now = datetime.now(timezone.utc)
        record = {
            "timestamp": now.isoformat(),
            "model": model,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "estimated_cost": estimated_cost,
            "session_id": session_id,
        }

        _ensure_usage_dir(project_root)
        path = _usage_file_path(project_root)

        with open(path, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

        return {
            "recorded": True,
            "record": record,
            "usage_file": path,
        }

    def _handle_get_usage_summary(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Aggregate usage records by session and day."""
        project_root = os.path.abspath(args.get("project_root", self._default_project_root))
        filter_session = args.get("session_id")
        days = int(args.get("days", 30))

        records = _read_usage_records(project_root)

        if not records:
            return {
                "total_cost": 0.0,
                "total_records": 0,
                "total_input_tokens": 0,
                "total_output_tokens": 0,
                "sessions": [],
                "daily_costs": [],
            }

        # Filter by session if requested
        if filter_session:
            records = [r for r in records if r.get("session_id") == filter_session]

        now = datetime.now(timezone.utc)
        cutoff = now - timedelta(days=days)

        total_cost = 0.0
        total_input = 0
        total_output = 0
        session_costs: Dict[str, Dict[str, Any]] = {}
        daily_costs: Dict[str, float] = {}

        for rec in records:
            try:
                ts_str = rec.get("timestamp", "")
                if ts_str:
                    ts = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
                    if ts < cutoff:
                        continue
                    day_key = ts.strftime("%Y-%m-%d")
                else:
                    day_key = "unknown"

                cost = float(rec.get("estimated_cost", 0))
                i_tok = int(rec.get("input_tokens", 0))
                o_tok = int(rec.get("output_tokens", 0))
                sid = rec.get("session_id", "unknown")

                total_cost += cost
                total_input += i_tok
                total_output += o_tok

                # Session aggregation
                if sid not in session_costs:
                    session_costs[sid] = {
                        "session_id": sid,
                        "total_cost": 0.0,
                        "total_input_tokens": 0,
                        "total_output_tokens": 0,
                        "record_count": 0,
                        "models": {},
                    }
                session_costs[sid]["total_cost"] += cost
                session_costs[sid]["total_input_tokens"] += i_tok
                session_costs[sid]["total_output_tokens"] += o_tok
                session_costs[sid]["record_count"] += 1

                model = rec.get("model", "unknown")
                if model not in session_costs[sid]["models"]:
                    session_costs[sid]["models"][model] = {"cost": 0.0, "count": 0}
                session_costs[sid]["models"][model]["cost"] += cost
                session_costs[sid]["models"][model]["count"] += 1

                # Daily aggregation
                daily_costs[day_key] = daily_costs.get(day_key, 0) + cost

            except (ValueError, TypeError):
                continue

        # Round values
        total_cost = round(total_cost, 6)
        for sid in session_costs:
            session_costs[sid]["total_cost"] = round(session_costs[sid]["total_cost"], 6)
            for m in session_costs[sid]["models"]:
                session_costs[sid]["models"][m]["cost"] = round(
                    session_costs[sid]["models"][m]["cost"], 6
                )
        daily_costs = {k: round(v, 6) for k, v in daily_costs.items()}

        # Sort by cost descending
        sessions_sorted = sorted(
            session_costs.values(), key=lambda x: x["total_cost"], reverse=True
        )
        daily_sorted = sorted(daily_costs.items(), key=lambda x: x[0], reverse=True)
        daily_list = [{"date": k, "cost": v} for k, v in daily_sorted]

        return {
            "total_cost": total_cost,
            "total_records": len(records),
            "total_input_tokens": total_input,
            "total_output_tokens": total_output,
            "sessions": sessions_sorted,
            "daily_costs": daily_list,
            "date_range": "{} - {}".format(
                cutoff.strftime("%Y-%m-%d"), now.strftime("%Y-%m-%d")
            ),
            "usage_file": _usage_file_path(project_root),
        }

    def _handle_estimate_cost(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Estimate cost without recording."""
        model = args["model"]
        input_tokens = int(args["input_tokens"])
        output_tokens = int(args["output_tokens"])

        config = load_config()
        cost = _calculate_cost(model, input_tokens, output_tokens, config)

        models = config.get("models", {})
        providers = config.get("providers", {})

        model_info = models.get(model)
        if model_info:
            input_price = model_info.get("input", 0)
            output_price = model_info.get("output", 0)
            price_source = "model"
        else:
            provider = model.split("/")[0] if "/" in model else model
            provider_info = providers.get(provider)
            if provider_info:
                input_price = provider_info.get("input", 0)
                output_price = provider_info.get("output", 0)
                price_source = "provider ({})".format(provider)
            else:
                input_price = 0
                output_price = 0
                price_source = "none"

        return {
            "model": model,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "input_price_per_million": input_price,
            "output_price_per_million": output_price,
            "currency": "CNY",
            "estimated_cost": cost,
            "price_source": price_source,
            "formula": "(input_tokens * {} + output_tokens * {}) / 1_000_000".format(
                input_price, output_price
            ),
        }


# ---------------------------------------------------------------------------
# Main loop
# ---------------------------------------------------------------------------


def main() -> None:
    """Run the MCP server on stdio."""
    project_root = "."

    # Allow --project-root override
    args = sys.argv[1:]
    for i, arg in enumerate(args):
        if arg == "--project-root" and i + 1 < len(args):
            project_root = args[i + 1]
            break

    server = UsageCostServer(project_root)

    stdin = sys.stdin.buffer
    stdout = sys.stdout.buffer

    while True:
        msg = _read_message(stdin)
        if msg is None:
            break

        response = server.handle_message(msg)
        if response is not None:
            _write_message(stdout, response)


if __name__ == "__main__":
    main()
