"""Fish Trail MCP Server — stdio JSON-RPC 2.0 server for topic governance.

Implements the MCP (Model Context Protocol) over stdio transport using only
Python stdlib. No external dependencies required.

Usage:
    python server.py [--base-dir .petfish/fish-trail]
    # Or via opencode.json MCP config (stdio transport)
"""

import json
import logging
import os
import re
import sys
import time
from datetime import datetime, timezone
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger("fish-trail")

# Add the directory containing this file to sys.path so sibling imports work
# regardless of how the server is launched (direct script, module, or MCP).
_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
if _THIS_DIR not in sys.path:
    sys.path.insert(0, _THIS_DIR)

# Also add the scripts directory for topic_route, topic_report, topic_validate
_SCRIPTS_DIR = os.path.normpath(os.path.join(_THIS_DIR, "..", "..", "scripts"))
if os.path.isdir(_SCRIPTS_DIR) and _SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, _SCRIPTS_DIR)

from topic_store import TopicStore  # noqa: E402
from topic_detector import TopicDetector  # noqa: E402
from contamination_scorer import ContaminationScorer  # noqa: E402
from context_builder import ContextBuilder  # noqa: E402
from session_store import SessionStore  # noqa: E402

# Optional: embedding support (all deps are optional)
try:
    from embeddings import EmbeddingManager  # noqa: E402

    _HAS_EMBEDDINGS = True
except ImportError:
    _HAS_EMBEDDINGS = False

# Optional: scripts may not be installed in all environments
try:
    from topic_route import TopicRouter  # noqa: E402
    from topic_report import TopicReporter  # noqa: E402
    from topic_validate import TopicValidator  # noqa: E402

    _HAS_SCRIPTS = True
except ImportError:
    _HAS_SCRIPTS = False

# Optional: Tiered Memory v2 modules
try:
    from topic_registry_v2 import TopicRegistryV2  # noqa: E402
    from memory_pressure_monitor import MemoryPressureMonitor  # noqa: E402
    from memory_context import MemoryContextProvider  # noqa: E402
    from feature_flags import FeatureFlags, load_feature_flags  # noqa: E402

    _HAS_MEMORY_V2 = True
except ImportError:
    _HAS_MEMORY_V2 = False


# ---------------------------------------------------------------------------
# Minimal MCP server over stdio (LSP base protocol framing)
# Auto-detects transport: Content-Length headers vs bare JSONL.
# ---------------------------------------------------------------------------

# Transport mode: None = not yet detected, "clength" or "jsonl"
_transport_mode: Optional[str] = None


def _read_message(stream) -> Optional[Dict[str, Any]]:
    """Read one JSON-RPC message.  Auto-detects transport on the first call.

    Supported transports:
      - Content-Length framing (LSP-style): ``Content-Length: N\\r\\n\\r\\n{...}``
      - Bare JSONL: one JSON object per line (``{...}\\n``)
    """
    global _transport_mode

    while True:
        first_line = stream.readline()
        if not first_line:
            return None  # EOF
        if isinstance(first_line, bytes):
            first_line = first_line.decode("utf-8")
        stripped = first_line.strip()
        if stripped == "":
            continue  # skip blank lines between messages
        break

    # --- Auto-detect on first non-blank line ---
    if _transport_mode is None:
        if stripped.startswith("{"):
            _transport_mode = "jsonl"
        else:
            _transport_mode = "clength"

    # --- JSONL transport ---
    if _transport_mode == "jsonl":
        if stripped.startswith("{"):
            return json.loads(stripped)
        # In JSONL mode but got a non-JSON line — skip and retry
        return _read_message(stream)

    # --- Content-Length transport ---
    # first_line is the first header line
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


def _jsonrpc_error(
    id: Any, code: int, message: str, data: Any = None
) -> Dict[str, Any]:
    err = {"jsonrpc": "2.0", "id": id, "error": {"code": code, "message": message}}
    if data is not None:
        err["error"]["data"] = data
    return err


# ---------------------------------------------------------------------------
# Tool definitions (MCP tools/list response)
# ---------------------------------------------------------------------------

TOOLS = [
    # Topic lifecycle (9)
    {
        "name": "topic_create",
        "description": "Create a new topic with title, scope, and optional parent.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "title": {"type": "string", "description": "Topic title"},
                "scope": {"type": "string", "description": "Topic scope description"},
                "parent": {
                    "type": "string",
                    "description": "Parent topic ID (optional)",
                },
                "tags": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Tags",
                },
            },
            "required": ["title", "scope"],
        },
    },
    {
        "name": "topic_list",
        "description": "List topics, optionally filtered by status.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "status": {
                    "type": "string",
                    "description": "Filter: active|paused|archived",
                },
            },
        },
    },
    {
        "name": "topic_show",
        "description": "Show topic details and related topics.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "topic_id": {"type": "string", "description": "Topic ID"},
            },
            "required": ["topic_id"],
        },
    },
    {
        "name": "topic_update",
        "description": "Update topic fields (scope, status, summary, tags, etc.).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "topic_id": {"type": "string", "description": "Topic ID"},
                "title": {"type": "string"},
                "scope": {"type": "string"},
                "status": {"type": "string"},
                "summary": {"type": "string"},
                "tags": {"type": "array", "items": {"type": "string"}},
                "reflective_brief": {
                    "type": "string",
                    "description": "Agent-authored reflective brief (validated; fallback to heuristic if invalid or degraded)",
                },
            },
            "required": ["topic_id"],
        },
    },
    {
        "name": "topic_archive",
        "description": "Archive a topic and freeze its summary.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "topic_id": {"type": "string", "description": "Topic ID"},
            },
            "required": ["topic_id"],
        },
    },
    {
        "name": "topic_search",
        "description": "Full-text search across topic titles, scopes, summaries, and tags.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query"},
            },
            "required": ["query"],
        },
    },
    {
        "name": "topic_link",
        "description": "Create a relationship between two topics.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "source": {"type": "string", "description": "Source topic ID"},
                "target": {"type": "string", "description": "Target topic ID"},
                "relation": {
                    "type": "string",
                    "description": "Relation type: continue|fork|switch|merge|archive|reset|bridge",
                },
            },
            "required": ["source", "target", "relation"],
        },
    },
    {
        "name": "topic_unlink",
        "description": "Remove a relationship between two topics.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "source": {"type": "string", "description": "Source topic ID"},
                "target": {"type": "string", "description": "Target topic ID"},
            },
            "required": ["source", "target"],
        },
    },
    {
        "name": "topic_graph",
        "description": "Return the complete topic relationship graph.",
        "inputSchema": {"type": "object", "properties": {}},
    },
    # Detection (1)
    {
        "name": "topic_detect",
        "description": "Detect the relation between input text and the current active topic.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "User message text"},
                "current_topic": {
                    "type": "string",
                    "description": "Current topic ID (optional, uses active)",
                },
                "session_id": {
                    "type": "string",
                    "description": "Session ID for event tracking",
                },
                "agent_id": {
                    "type": "string",
                    "description": "Agent identifier",
                },
            },
            "required": ["text"],
        },
    },
    # Context operations (4)
    {
        "name": "context_build",
        "description": "Generate a Context Package for the specified topic.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "topic_id": {"type": "string", "description": "Topic ID"},
            },
            "required": ["topic_id"],
        },
    },
    {
        "name": "context_build_bridge",
        "description": "Generate a bridge Context Package between two topics.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "topic_a": {"type": "string", "description": "First topic ID"},
                "topic_b": {"type": "string", "description": "Second topic ID"},
            },
            "required": ["topic_a", "topic_b"],
        },
    },
    {
        "name": "context_export",
        "description": "Export a handoff-compatible Context Package.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "topic_id": {"type": "string", "description": "Topic ID"},
                "reason": {"type": "string", "description": "Export reason"},
                "session_id": {
                    "type": "string",
                    "description": "Filter export to this session only",
                },
            },
            "required": ["topic_id"],
        },
    },
    {
        "name": "context_freeze",
        "description": "Freeze the current Context Package as an immutable snapshot.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "topic_id": {"type": "string", "description": "Topic ID"},
            },
            "required": ["topic_id"],
        },
    },
    # Contamination (2)
    {
        "name": "contamination_score",
        "description": "Calculate contamination risk between two topics.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "topic_a": {"type": "string", "description": "First topic ID"},
                "topic_b": {"type": "string", "description": "Second topic ID"},
            },
            "required": ["topic_a", "topic_b"],
        },
    },
    {
        "name": "contamination_explain",
        "description": "Explain contamination risk sources in detail.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "topic_a": {"type": "string", "description": "First topic ID"},
                "topic_b": {"type": "string", "description": "Second topic ID"},
            },
            "required": ["topic_a", "topic_b"],
        },
    },
    # Decision tracking (2)
    {
        "name": "decision_log",
        "description": "Record a routing decision.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "relation": {"type": "string"},
                "source_topic": {"type": "string"},
                "target_topic": {"type": "string"},
                "risk_score": {"type": "number"},
                "risk_level": {"type": "string"},
                "action": {"type": "string"},
                "user_confirmed": {"type": "boolean"},
                "session_id": {
                    "type": "string",
                    "description": "Session ID to associate with this decision",
                },
                "agent_id": {
                    "type": "string",
                    "description": "Agent identifier",
                },
            },
            "required": ["relation", "source_topic", "action"],
        },
    },
    {
        "name": "decision_history",
        "description": "View routing decision history.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "topic_id": {"type": "string", "description": "Filter by topic ID"},
                "session_id": {
                    "type": "string",
                    "description": "Filter by session ID",
                },
                "limit": {"type": "integer", "description": "Max entries (default 50)"},
            },
        },
    },
    # Session management (4)
    {
        "name": "session_bind",
        "description": "Create or resume a session, optionally binding to an external session ID and topic.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "external_session_id": {
                    "type": "string",
                    "description": "External session ID (e.g. OpenCode session ID)",
                },
                "topic_id": {
                    "type": "string",
                    "description": "Topic to bind to this session",
                },
                "metadata": {
                    "type": "object",
                    "description": "Additional session metadata",
                },
            },
        },
    },
    {
        "name": "session_get",
        "description": "Get full session record including timeline and topic refs.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "session_id": {"type": "string", "description": "Session ID"},
            },
            "required": ["session_id"],
        },
    },
    {
        "name": "session_list",
        "description": "List sessions, optionally filtered by topic, date, or status.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "topic_id": {
                    "type": "string",
                    "description": "Filter by topic ID",
                },
                "since": {
                    "type": "string",
                    "description": "ISO 8601 timestamp — only sessions with activity after this time",
                },
                "status": {
                    "type": "string",
                    "description": "Filter: active|closed",
                },
                "limit": {
                    "type": "integer",
                    "description": "Max results (default 50)",
                },
            },
        },
    },
    {
        "name": "session_resume",
        "description": "Find the best session to resume for a topic or session ID. Returns session data plus inherited context package.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "topic_id": {
                    "type": "string",
                    "description": "Find most recent session for this topic",
                },
                "session_id": {
                    "type": "string",
                    "description": "Resume a specific session",
                },
            },
        },
    },
    {
        "name": "session_close",
        "description": "Close a session with an optional summary. Also auto-closes inactive sessions.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "session_id": {
                    "type": "string",
                    "description": "Session ID to close",
                },
                "summary": {
                    "type": "string",
                    "description": "Session summary for handoff",
                },
                "auto_close_inactive": {
                    "type": "boolean",
                    "description": "Also close sessions inactive >24h (default false)",
                },
                "threshold_hours": {
                    "type": "number",
                    "description": "Inactivity threshold in hours (default 24)",
                },
            },
            "required": ["session_id"],
        },
    },
    {
        "name": "session_timeline",
        "description": "Get session timeline summary with recent events.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "session_id": {
                    "type": "string",
                    "description": "Session ID",
                },
                "max_events": {
                    "type": "integer",
                    "description": "Max recent events to return (default 20)",
                },
            },
            "required": ["session_id"],
        },
    },
    # Session analytics (2)
    {
        "name": "session_query",
        "description": "Query activity across sessions. Answers 'what did we work on yesterday?' style questions.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "since": {
                    "type": "string",
                    "description": "ISO 8601 timestamp — only events after this time",
                },
                "until": {
                    "type": "string",
                    "description": "ISO 8601 timestamp — only events before this time",
                },
                "topic_id": {
                    "type": "string",
                    "description": "Filter events by topic ID",
                },
                "agent_id": {
                    "type": "string",
                    "description": "Filter events by agent ID",
                },
                "limit": {
                    "type": "integer",
                    "description": "Max events to return (default 50)",
                },
            },
        },
    },
    {
        "name": "session_agents",
        "description": "Show which agents worked on which topics (multi-agent attribution).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "session_id": {
                    "type": "string",
                    "description": "Scope to a single session",
                },
                "topic_id": {
                    "type": "string",
                    "description": "Filter by topic ID",
                },
            },
        },
    },
    # Topic recommendations (1)
    {
        "name": "topic_recommend",
        "description": "Recommend related topics by walking the topic graph from a given topic.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "topic_id": {
                    "type": "string",
                    "description": "Source topic ID",
                },
                "max_depth": {
                    "type": "integer",
                    "description": "Max graph hops (default 2)",
                },
            },
            "required": ["topic_id"],
        },
    },
    # Topic routing & governance (3)
    {
        "name": "topic_route",
        "description": "Route a query to the most relevant topic and generate active_context.md with context firewall (must_load/may_load/must_not_load).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "User query to route"},
                "current_topic_id": {
                    "type": "string",
                    "description": "Current topic ID to boost (optional)",
                },
                "write_active_context": {
                    "type": "boolean",
                    "description": "Write active_context.md (default true)",
                },
            },
            "required": ["query"],
        },
    },
    {
        "name": "topic_report",
        "description": "Generate TOPIC_REPORT.md with hub topics, stale topics, pollution risks, and maintenance suggestions.",
        "inputSchema": {
            "type": "object",
            "properties": {},
        },
    },
    {
        "name": "topic_validate",
        "description": "Validate topic_graph.json structure: check node IDs, edge references, evidence levels, and topic card consistency.",
        "inputSchema": {
            "type": "object",
            "properties": {},
        },
    },
    {
        "name": "get_memory_context",
        "description": "Get tiered memory context for the current conversation. Returns hot/warm/cold topic summaries with budget-aware token allocation.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "current_topic_id": {
                    "description": "Active topic ID to prioritize (optional, uses most recent if omitted)",
                    "type": "string",
                },
                "include_warm": {
                    "description": "Include warm-tier topic summaries (default: true)",
                    "type": "boolean",
                },
                "include_cold_summaries": {
                    "description": "Include cold-tier one-line summaries (default: true)",
                    "type": "boolean",
                },
                "budget_tokens": {
                    "description": "Max tokens for memory context (default: uses pressure monitor allocation)",
                    "type": "integer",
                },
            },
        },
    },
]


# ---------------------------------------------------------------------------
# Server implementation
# ---------------------------------------------------------------------------


class ContextStateServer:
    """MCP server that wires the 31 fish-trail tools to TopicStore et al."""

    MUTATION_TOOLS = frozenset(
        {
            "topic_create",
            "topic_update",
            "topic_archive",
            "topic_link",
            "topic_unlink",
            "session_bind",
            "session_close",
        }
    )

    def __init__(self, base_dir: str):
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s [fish-trail] %(levelname)s %(message)s",
            stream=sys.stderr,  # MCP uses stdout for JSON-RPC, so log to stderr
        )
        self.store = TopicStore(base_dir)
        self._base_dir = base_dir  # for call-log path

        # Load config (stdlib json, no external deps)
        config = self._load_config(base_dir)

        # Optional embedding manager
        embedding_mgr = None
        embedding_cfg = config.get("embedding", {})
        if _HAS_EMBEDDINGS and embedding_cfg.get("enabled", True):
            embedding_mgr = EmbeddingManager(
                base_dir=base_dir,
                timeout_ms=embedding_cfg.get("timeout_ms", 2000),
            )

        self.detector = TopicDetector(embedding_manager=embedding_mgr)
        self.scorer = ContaminationScorer()
        self.builder = ContextBuilder(base_dir)
        self.sessions = SessionStore(base_dir)

        # Optional: Tiered Memory v2 (flag-controlled)
        self._memory_context: Optional["MemoryContextProvider"] = None
        self._feature_flags: Optional["FeatureFlags"] = None
        if _HAS_MEMORY_V2:
            try:
                self._feature_flags = load_feature_flags(
                    base_dir=base_dir, config_data=config
                )
                if self._feature_flags.memory_context_enabled:
                    registry_v2 = (
                        TopicRegistryV2(base_dir)
                        if self._feature_flags.registry_enabled
                        else None
                    )
                    pressure_monitor = (
                        MemoryPressureMonitor()
                        if self._feature_flags.pressure_monitor_enabled
                        else None
                    )
                    self._memory_context = MemoryContextProvider(
                        registry=registry_v2,
                        pressure_monitor=pressure_monitor,
                    )
            except Exception:
                pass  # Graceful degradation if v2 init fails

        self._handlers = {}  # type: Dict[str, Callable]
        self._register_handlers()

    @staticmethod
    def _load_config(base_dir: str) -> dict:
        """Load config.json from base_dir. Returns empty dict if missing."""
        import json as _json

        config_path = os.path.join(base_dir, "config.json")
        if os.path.exists(config_path):
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    return _json.load(f)
            except (OSError, ValueError):
                pass
        return {}

    # -- Handler registration -----------------------------------------------

    def _register_handlers(self) -> None:
        h = self._handlers
        # Topic lifecycle
        h["topic_create"] = self._handle_topic_create
        h["topic_list"] = self._handle_topic_list
        h["topic_show"] = self._handle_topic_show
        h["topic_update"] = self._handle_topic_update
        h["topic_archive"] = self._handle_topic_archive
        h["topic_search"] = self._handle_topic_search
        h["topic_link"] = self._handle_topic_link
        h["topic_unlink"] = self._handle_topic_unlink
        h["topic_graph"] = self._handle_topic_graph
        # Detection
        h["topic_detect"] = self._handle_topic_detect
        # Context operations
        h["context_build"] = self._handle_context_build
        h["context_build_bridge"] = self._handle_context_build_bridge
        h["context_export"] = self._handle_context_export
        h["context_freeze"] = self._handle_context_freeze
        # Contamination
        h["contamination_score"] = self._handle_contamination_score
        h["contamination_explain"] = self._handle_contamination_explain
        # Decision tracking
        h["decision_log"] = self._handle_decision_log
        h["decision_history"] = self._handle_decision_history
        # Session management
        h["session_bind"] = self._handle_session_bind
        h["session_get"] = self._handle_session_get
        h["session_list"] = self._handle_session_list
        h["session_resume"] = self._handle_session_resume
        h["session_close"] = self._handle_session_close
        h["session_timeline"] = self._handle_session_timeline
        h["session_query"] = self._handle_session_query
        h["session_agents"] = self._handle_session_agents
        # Topic recommendations
        h["topic_recommend"] = self._handle_topic_recommend
        # Topic routing & governance
        if _HAS_SCRIPTS:
            h["topic_route"] = self._handle_topic_route
            h["topic_report"] = self._handle_topic_report
            h["topic_validate"] = self._handle_topic_validate
        # Tiered Memory v2
        if self._memory_context is not None:
            h["get_memory_context"] = self._handle_get_memory_context

    # -- JSON-RPC dispatch --------------------------------------------------

    def handle_message(self, msg: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Dispatch a JSON-RPC message. Returns a response or None for notifications."""
        method = msg.get("method", "")
        msg_id = msg.get("id")
        params = msg.get("params", {})

        if method == "initialize":
            return _jsonrpc_response(
                msg_id,
                {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {"tools": {}},
                    "serverInfo": {"name": "fish-trail", "version": "0.5.1"},
                },
            )

        if method == "notifications/initialized":
            return None  # no response for notifications

        if method == "tools/list":
            return _jsonrpc_response(msg_id, {"tools": TOOLS})

        if method == "tools/call":
            return self._dispatch_tool_call(msg_id, params)

        if method == "ping":
            return _jsonrpc_response(msg_id, {})

        # Unknown method
        if msg_id is not None:
            return _jsonrpc_error(msg_id, -32601, "Method not found: {}".format(method))
        return None

    def _sanitize_args(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Truncate large values in args for safe logging."""
        sanitized = {}
        for key, value in args.items():
            s = str(value)
            if len(s) > 200:
                sanitized[key] = s[:200] + "..."
            else:
                sanitized[key] = value
        return sanitized

    def _auto_log_mutation(
        self,
        tool_name: str,
        original_args: Dict[str, Any],
        result: Any,
    ) -> None:
        """Auto-log a mutation to decision-log with correct identifiers.

        Captures identifiers from original_args (before handler mutation)
        and enriches from result (for created resources like topic IDs).
        """
        try:
            # Resolve source_topic and target_topic per-tool
            source_topic = None
            target_topic = None
            session_id = None

            if tool_name == "topic_create":
                # New topic ID lives in result
                if isinstance(result, dict):
                    target_topic = result.get("id") or result.get("topic_id")
            elif tool_name == "topic_update":
                source_topic = original_args.get("topic_id")
            elif tool_name == "topic_archive":
                source_topic = original_args.get("topic_id")
            elif tool_name in ("topic_link", "topic_unlink"):
                source_topic = original_args.get("source")
                target_topic = original_args.get("target")
            elif tool_name == "session_bind":
                if isinstance(result, dict):
                    session_obj = result.get("session", result)
                    session_id = session_obj.get("id") if isinstance(session_obj, dict) else None
            elif tool_name == "session_close":
                session_id = original_args.get("session_id")

            log_entry = {
                "action": tool_name,
                "source_topic": source_topic,
                "target_topic": target_topic,
                "risk_level": "info",
                "user_confirmed": False,
                "payload": {
                    k: v
                    for k, v in self._sanitize_args(original_args).items()
                    if k not in ("topic_id", "source", "target", "session_id")
                },
            }
            if session_id:
                log_entry["session_id"] = session_id

            self.store.log_decision(log_entry)
        except Exception:
            pass  # Never let audit logging break the response

    def _log_tool_call(
        self,
        tool_name: str,
        args: Dict[str, Any],
        duration_ms: float,
        ok: bool,
        error: Optional[str] = None,
    ) -> None:
        """Append a JSONL entry to mcp-call-log.jsonl for benchmark observability.

        Each line is a self-contained JSON object with:
          - ts: ISO 8601 timestamp
          - tool: tool name
          - ok: whether the call succeeded
          - duration_ms: wall-clock duration
          - args: sanitized arguments (truncated for safety)
          - error: error message (only on failure)

        The log is written to <base_dir>/mcp-call-log.jsonl.
        Rotation: when the file exceeds 1MB, it is truncated to the last
        1000 lines to keep disk usage bounded.
        """
        try:
            log_path = os.path.join(self._base_dir, "mcp-call-log.jsonl")
            entry = {
                "ts": time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime()) + "Z",
                "tool": tool_name,
                "ok": ok,
                "duration_ms": round(duration_ms, 1),
                "args": self._sanitize_args(args),
            }
            if error is not None:
                entry["error"] = error[:200]  # cap error length

            line = json.dumps(entry, ensure_ascii=False) + chr(10)  # chr(10) = newline

            # Rotation: if file > 1MB, truncate to last 1000 lines
            if os.path.exists(log_path) and os.path.getsize(log_path) > 1_000_000:
                try:
                    with open(log_path, "r", encoding="utf-8") as f:
                        lines = f.readlines()
                    with open(log_path, "w", encoding="utf-8") as f:
                        for l in lines[-1000:]:
                            f.write(l)
                except Exception:
                    pass  # rotation failure should not block logging

            with open(log_path, "a", encoding="utf-8") as f:
                f.write(line)
        except Exception:
            pass  # Never let call logging break the response

    def _dispatch_tool_call(
        self, msg_id: Any, params: Dict[str, Any]
    ) -> Dict[str, Any]:
        tool_name = params.get("name", "")
        arguments = params.get("arguments", {})
        start = time.monotonic()

        handler = self._handlers.get(tool_name)
        if handler is None:
            logger.warning("unknown_tool name=%s", tool_name)
            return _jsonrpc_error(msg_id, -32602, "Unknown tool: {}".format(tool_name))

        logger.info("tool_call name=%s", tool_name)
        try:
            # Snapshot args BEFORE handler runs (handlers may mutate args)
            original_args = dict(arguments)
            result = handler(arguments)
            duration_ms = (time.monotonic() - start) * 1000
            logger.info("tool_done name=%s duration=%.1fms", tool_name, duration_ms)

            # Auto-log mutations to decision-log for audit trail
            if tool_name in self.MUTATION_TOOLS:
                self._auto_log_mutation(tool_name, original_args, result)

            # Server-side call logging for benchmark observability
            self._log_tool_call(tool_name, original_args, duration_ms, ok=True)

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
            duration_ms = (time.monotonic() - start) * 1000
            logger.error(
                "tool_error name=%s duration=%.1fms error=%s",
                tool_name,
                duration_ms,
                exc,
            )
            self._log_tool_call(tool_name, original_args, duration_ms, ok=False, error=str(exc))
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
            duration_ms = (time.monotonic() - start) * 1000
            logger.error(
                "tool_error name=%s duration=%.1fms error=%s",
                tool_name,
                duration_ms,
                exc,
            )
            self._log_tool_call(tool_name, original_args, duration_ms, ok=False, error=str(exc))
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
            duration_ms = (time.monotonic() - start) * 1000
            logger.error(
                "tool_error name=%s duration=%.1fms error=%s",
                tool_name,
                duration_ms,
                exc,
            )
            self._log_tool_call(tool_name, original_args, duration_ms, ok=False, error=str(exc))
            return _jsonrpc_error(msg_id, -32603, "Internal error: {}".format(exc))

    # -- Tool handlers ------------------------------------------------------

    def _handle_topic_create(self, args: Dict[str, Any]) -> Dict[str, Any]:
        return self.store.create(
            title=args["title"],
            scope=args["scope"],
            parent=args.get("parent"),
            tags=args.get("tags"),
        )

    def _handle_topic_list(self, args: Dict[str, Any]) -> List[Dict[str, Any]]:
        return self.store.list_topics(status=args.get("status"))

    def _handle_topic_show(self, args: Dict[str, Any]) -> Dict[str, Any]:
        topic_id = args["topic_id"]
        topic = self.store.get(topic_id)
        if topic is None:
            raise KeyError("Topic not found: {}".format(topic_id))
        graph = self.store.graph()
        related = []
        for edge in graph.get("edges", []):
            if edge.get("source") == topic_id:
                related.append(
                    {"relation": edge["relation"], "topic_id": edge["target"]}
                )
            elif edge.get("target") == topic_id:
                related.append(
                    {"relation": edge["relation"], "topic_id": edge["source"]}
                )
        return {"topic": topic, "related": related}

    # -- Brief validation and heuristic generation --------------------------

    _BRIEF_LOW_QUALITY_PATTERN = re.compile(
        r"^(?:继续|ongoing|working on it|进行中|继续开发中|ok|done|完成)$",
        re.IGNORECASE,
    )

    @staticmethod
    def _validate_brief(brief: str) -> tuple:
        """Validate a reflective_brief value.  Returns (is_valid, reason)."""
        if brief is None or brief.strip() == "":
            return (False, "empty")

        stripped = brief.strip()

        # Reject if only whitespace/punctuation (no word characters)
        if not re.search(r"\w", stripped):
            return (False, "no_content")

        if len(stripped) < 10:
            return (False, "too_short")

        if len(stripped) > 200:
            return (False, "too_long")

        if ContextStateServer._BRIEF_LOW_QUALITY_PATTERN.match(stripped):
            return (False, "low_quality_pattern")

        return (True, "ok")

    @staticmethod
    def _heuristic_brief(summary: str, max_chars: int = 200) -> str:
        """Auto-generate a brief from the topic summary when no agent brief exists."""
        if not summary or not summary.strip():
            return ""

        text = summary.strip()

        # Strategy 1: Extract "At:/Progress:/Status:" prefix
        m = re.search(r"(?:At|Progress|Status)[:]\s*(.+?)(?:\.|$)", text, re.M)
        if m and len(m.group(1).strip()) >= 10:
            result = m.group(1).strip()
            if len(result) > max_chars:
                result = result[: max_chars - 1] + chr(0x2026)
            return result

        # Strategy 2: First sentence
        m = re.match(r"^(.+?[.!?])\s", text)
        if m and len(m.group(1).strip()) >= 10:
            result = m.group(1).strip()
            if len(result) > max_chars:
                result = result[: max_chars - 1] + chr(0x2026)
            return result

        # Strategy 3: Hard truncate
        if len(text) > max_chars:
            return text[: max_chars - 1] + chr(0x2026)
        return text

    def _handle_topic_update(self, args: Dict[str, Any]) -> Dict[str, Any]:
        topic_id = args.get("topic_id")

        # --- reflective_brief handling ---
        if "reflective_brief" in args or (
            "summary" in args and "reflective_brief" not in args
        ):
            topic = self.store.get(topic_id)
            if topic is None:
                raise KeyError("topic not found: {0}".format(topic_id))

            stats = topic.get("brief_stats")
            if stats is None:
                stats = {
                    "agent_attempts": 0,
                    "agent_accepted": 0,
                    "agent_rejected": 0,
                    "heuristic_count": 0,
                    "degraded": False,
                }

            # Determine effective summary: incoming args override, else topic's existing
            effective_summary = args.get("summary", topic.get("summary", ""))

            now_ts = datetime.now(timezone.utc).isoformat()

            if stats.get("degraded", False):
                # Degraded mode: ignore agent brief, always use heuristic
                brief = self._heuristic_brief(effective_summary)
                if brief:
                    args["reflective_brief"] = brief
                    args["brief_model"] = "heuristic"
                    args["brief_generated_at"] = now_ts
                    stats["heuristic_count"] += 1
                logger.warning(
                    "topic_update degraded heuristic topic_id=%s brief_len=%d",
                    topic_id,
                    len(brief) if brief else 0,
                )

            elif "reflective_brief" in args:
                raw_brief = args.get("reflective_brief", "")
                is_valid, reason = self._validate_brief(raw_brief)
                stats["agent_attempts"] += 1

                if is_valid:
                    stats["agent_accepted"] += 1
                    args["brief_model"] = "agent"
                    args["brief_generated_at"] = now_ts
                else:
                    stats["agent_rejected"] += 1
                    # Remove invalid brief — don't store it
                    del args["reflective_brief"]
                    logger.warning(
                        "topic_update brief_rejected topic_id=%s reason=%s len=%d",
                        topic_id,
                        reason,
                        len(raw_brief) if raw_brief else 0,
                    )

            else:
                # No reflective_brief in args — check if topic already has one
                existing_brief = topic.get("reflective_brief")
                if existing_brief:
                    # Keep it — do not overwrite
                    pass
                else:
                    brief = self._heuristic_brief(effective_summary)
                    if brief:
                        args["reflective_brief"] = brief
                        args["brief_model"] = "heuristic"
                        args["brief_generated_at"] = now_ts
                        stats["heuristic_count"] += 1

            # Degradation check
            attempts = max(stats["agent_attempts"], 1)
            if (
                stats["agent_rejected"] / attempts > 0.5
                and stats["agent_attempts"] >= 3
            ):
                stats["degraded"] = True

            args["brief_stats"] = stats

        update_kwargs = {k: v for k, v in args.items() if k != "topic_id"}
        return self.store.update(topic_id, **update_kwargs)

    def _handle_topic_archive(self, args: Dict[str, Any]) -> Dict[str, Any]:
        return self.store.archive(args["topic_id"])

    def _handle_topic_search(self, args: Dict[str, Any]) -> List[Dict[str, Any]]:
        return self.store.search(args["query"])

    def _handle_topic_link(self, args: Dict[str, Any]) -> Dict[str, Any]:
        return self.store.link(args["source"], args["target"], args["relation"])

    def _handle_topic_unlink(self, args: Dict[str, Any]) -> bool:
        return self.store.unlink(args["source"], args["target"])

    def _handle_topic_graph(self, args: Dict[str, Any]) -> Dict[str, Any]:
        graph = self.store.graph()
        # Persist to topic_graph.json so topic_validate can read it (#55)
        graph_path = self.store.base_dir / "topic_graph.json"
        self.store._atomic_write(graph_path, graph)
        return graph

    def _handle_topic_detect(self, args: Dict[str, Any]) -> Dict[str, Any]:
        text = args["text"]
        session_id = args.get("session_id")
        agent_id = args.get("agent_id")
        # Resolve current topic
        current_topic_id = args.get("current_topic")
        current_topic = None
        if current_topic_id:
            current_topic = self.store.get(current_topic_id)
        if current_topic is None:
            current_topic = self.store.get_active()

        # Get all non-archived topics for switch detection
        all_topics = [
            t
            for t in self.store.list_topics()
            if isinstance(t, dict) and t.get("status") != "archived"
        ]
        # list_topics returns registry summaries — enrich with full data
        enriched = []
        for t in all_topics:
            full = self.store.get(t.get("id", ""))
            if full:
                enriched.append(full)

        result = self.detector.detect(text, current_topic, enriched)

        # If switch detected with a target, update active topic
        if result.get("relation") == "switch" and result.get("target_topic"):
            target = self.store.get(result["target_topic"])
            if target:
                self.store.set_active(result["target_topic"])

        # Record session event if session_id provided
        if session_id:
            event_fields = {
                "relation": result.get("relation"),
                "risk": result.get("risk"),
            }
            if agent_id:
                event_fields["agent_id"] = agent_id
            try:
                self.sessions.add_event(
                    session_id,
                    "topic_transition",
                    topic_id=result.get("target_topic")
                    or (current_topic.get("id") if current_topic else None),
                    **event_fields,
                )
            except KeyError:
                pass  # session not found — don't fail detection

            # Auto-close session on archive/reset signals
            relation = result.get("relation")
            if relation in ("archive", "reset"):
                try:
                    summary = "Auto-closed: {} detected".format(relation)
                    self.sessions.close(session_id, summary=summary)
                except KeyError:
                    pass

        # Include session_id in result for caller convenience
        if session_id:
            result["session_id"] = session_id

        return result

    def _handle_context_build(self, args: Dict[str, Any]) -> Dict[str, Any]:
        topic_id = args["topic_id"]
        topic = self.store.get(topic_id)
        if topic is None:
            raise KeyError("Topic not found: {}".format(topic_id))
        related = self._get_related_topic_dicts(topic_id)
        decisions = self.store.get_decisions(topic_id=topic_id)
        return self.builder.build(topic, related, decisions)

    def _handle_context_build_bridge(self, args: Dict[str, Any]) -> Dict[str, Any]:
        ta = self.store.get(args["topic_a"])
        tb = self.store.get(args["topic_b"])
        if ta is None:
            raise KeyError("Topic not found: {}".format(args["topic_a"]))
        if tb is None:
            raise KeyError("Topic not found: {}".format(args["topic_b"]))
        # Compute shared keywords
        kw_a = self.scorer._extract_keywords(
            " ".join([ta.get("scope", ""), ta.get("title", "")])
        )
        kw_b = self.scorer._extract_keywords(
            " ".join([tb.get("scope", ""), tb.get("title", "")])
        )
        shared = sorted(kw_a & kw_b)
        return self.builder.build_bridge(ta, tb, shared, [])

    def _handle_context_export(self, args: Dict[str, Any]) -> Dict[str, Any]:
        topic_id = args["topic_id"]
        topic = self.store.get(topic_id)
        if topic is None:
            raise KeyError("Topic not found: {}".format(topic_id))
        related = self._get_related_topic_dicts(topic_id)
        decisions = self.store.get_decisions(topic_id=topic_id)
        reason = args.get("reason", "")
        session_id = args.get("session_id")
        return self.builder.export(
            topic, related, decisions, reason, session_id=session_id
        )

    def _handle_context_freeze(self, args: Dict[str, Any]) -> Dict[str, Any]:
        topic_id = args["topic_id"]
        topic = self.store.get(topic_id)
        if topic is None:
            raise KeyError("Topic not found: {}".format(topic_id))
        related = self._get_related_topic_dicts(topic_id)
        decisions = self.store.get_decisions(topic_id=topic_id)
        return self.builder.freeze(topic, related, decisions)

    def _handle_contamination_score(self, args: Dict[str, Any]) -> Dict[str, Any]:
        ta = self.store.get(args["topic_a"])
        tb = self.store.get(args["topic_b"])
        if ta is None:
            raise KeyError("Topic not found: {}".format(args["topic_a"]))
        if tb is None:
            raise KeyError("Topic not found: {}".format(args["topic_b"]))
        return self.scorer.score(ta, tb)

    def _handle_contamination_explain(self, args: Dict[str, Any]) -> Dict[str, Any]:
        ta = self.store.get(args["topic_a"])
        tb = self.store.get(args["topic_b"])
        if ta is None:
            raise KeyError("Topic not found: {}".format(args["topic_a"]))
        if tb is None:
            raise KeyError("Topic not found: {}".format(args["topic_b"]))
        return self.scorer.explain(ta, tb)

    def _handle_decision_log(self, args: Dict[str, Any]) -> Dict[str, Any]:
        return self.store.log_decision(args)

    def _handle_decision_history(self, args: Dict[str, Any]) -> List[Dict[str, Any]]:
        return self.store.get_decisions(
            topic_id=args.get("topic_id"),
            session_id=args.get("session_id"),
            limit=args.get("limit", 50),
        )

    # -- Session handlers ---------------------------------------------------

    def _handle_session_bind(self, args: Dict[str, Any]) -> Dict[str, Any]:
        # Auto-close stale sessions on bind
        self.sessions.auto_close_inactive()
        return self.sessions.bind(
            external_session_id=args.get("external_session_id"),
            topic_id=args.get("topic_id"),
            metadata=args.get("metadata"),
        )

    def _handle_session_get(self, args: Dict[str, Any]) -> Dict[str, Any]:
        session_id = args["session_id"]
        session = self.sessions.get(session_id)
        if session is None:
            raise KeyError("Session not found: {}".format(session_id))
        return session

    def _handle_session_list(self, args: Dict[str, Any]) -> List[Dict[str, Any]]:
        return self.sessions.list_sessions(
            topic_id=args.get("topic_id"),
            since=args.get("since"),
            status=args.get("status"),
            limit=args.get("limit", 50),
        )

    def _handle_session_resume(self, args: Dict[str, Any]) -> Dict[str, Any]:
        result = self.sessions.resume(
            topic_id=args.get("topic_id"),
            session_id=args.get("session_id"),
        )
        # Enrich with resume context
        session = result.get("session", {})
        sid = session.get("id")
        if sid:
            result["resume_context"] = self.sessions.get_resume_context(sid)
        return result

    def _handle_session_close(self, args: Dict[str, Any]) -> Dict[str, Any]:
        session_id = args["session_id"]
        summary = args.get("summary")
        session = self.sessions.close(session_id, summary=summary)

        response = {"session": session, "auto_closed": []}

        if args.get("auto_close_inactive"):
            threshold = args.get("threshold_hours", 24)
            closed = self.sessions.auto_close_inactive(threshold_hours=threshold)
            response["auto_closed"] = closed

        return response

    def _handle_session_timeline(self, args: Dict[str, Any]) -> Dict[str, Any]:
        return self.sessions.get_timeline_summary(
            session_id=args["session_id"],
            max_events=args.get("max_events", 20),
        )

    def _handle_session_query(self, args: Dict[str, Any]) -> Dict[str, Any]:
        return self.sessions.query_activity(
            since=args.get("since"),
            until=args.get("until"),
            topic_id=args.get("topic_id"),
            agent_id=args.get("agent_id"),
            limit=args.get("limit", 50),
        )

    def _handle_session_agents(self, args: Dict[str, Any]) -> Dict[str, Any]:
        return self.sessions.get_agent_attribution(
            session_id=args.get("session_id"),
            topic_id=args.get("topic_id"),
        )

    def _handle_topic_recommend(self, args: Dict[str, Any]) -> Dict[str, Any]:
        return self.store.recommend_related(
            topic_id=args["topic_id"],
            max_depth=args.get("max_depth", 2),
        )

    # -- Topic routing & governance -----------------------------------------

    def _handle_topic_route(self, args: Dict[str, Any]) -> Dict[str, Any]:
        router = TopicRouter(self.store.base_dir)
        result = router.route(
            query=args["query"],
            current_topic_id=args.get("current_topic_id"),
        )
        if args.get("write_active_context", True):
            path = router.write_active_context(result, args["query"])
            result["active_context_path"] = path
        return result

    def _handle_topic_report(self, args: Dict[str, Any]) -> Dict[str, Any]:
        reporter = TopicReporter(self.store.base_dir)
        report = reporter.generate()
        path = reporter.write_report(report)
        return {"path": path, "report": report}

    def _handle_topic_validate(self, args: Dict[str, Any]) -> Dict[str, Any]:
        validator = TopicValidator(self.store.base_dir)
        return validator.validate()

    # -- Helpers ------------------------------------------------------------

    def _get_related_topic_dicts(self, topic_id: str) -> List[Dict[str, Any]]:
        """Get full topic dicts for all topics related to topic_id."""
        graph = self.store.graph()
        related = []
        seen = set()
        for edge in graph.get("edges", []):
            other_id = None
            relation = edge.get("relation", "")
            if edge.get("source") == topic_id:
                other_id = edge.get("target")
            elif edge.get("target") == topic_id:
                other_id = edge.get("source")
            if other_id and other_id not in seen:
                seen.add(other_id)
                other = self.store.get(other_id)
                if other:
                    related.append(
                        {
                            "relation": relation,
                            "id": other.get("id", other_id),
                            "title": other.get("title", other_id),
                        }
                    )
        return related

    # -- Tiered Memory v2 handler -------------------------------------------

    def _handle_get_memory_context(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Handle get_memory_context tool call with v1 fallback."""
        if self._memory_context is None:
            raise ValueError("Memory context provider is not initialized")
        try:
            result = self._memory_context.get_memory_context(
                current_topic_id=args.get("current_topic_id"),
                budget_tokens=args.get("budget_tokens"),
                include_warm=args.get("include_warm", True),
                include_cold_summaries=args.get("include_cold_summaries"),
            )
            return result.to_dict()
        except Exception:
            if self._feature_flags and self._feature_flags.v1_fallback_on_error:
                from memory_context import MemoryContextResult

                return MemoryContextResult(
                    context_block="",
                    tokens_used=0,
                ).to_dict()
            raise


# ---------------------------------------------------------------------------
# Main loop
# ---------------------------------------------------------------------------


def main() -> None:
    """Run the MCP server on stdio."""
    base_dir = os.path.join(".petfish", "fish-trail")

    # Allow --base-dir override
    args = sys.argv[1:]
    for i, arg in enumerate(args):
        if arg == "--base-dir" and i + 1 < len(args):
            base_dir = args[i + 1]
            break

    # Auto-migrate from legacy .ai-context directory
    legacy_dir = ".ai-context"
    if os.path.isdir(legacy_dir) and not os.path.exists(base_dir):
        os.makedirs(os.path.dirname(base_dir), exist_ok=True)
        import shutil

        shutil.move(legacy_dir, base_dir)

    server = ContextStateServer(base_dir)

    # Use binary stdio for reliable Content-Length framing
    stdin = sys.stdin.buffer
    stdout = sys.stdout.buffer

    while True:
        msg = _read_message(stdin)
        if msg is None:
            break  # EOF

        response = server.handle_message(msg)
        if response is not None:
            _write_message(stdout, response)


if __name__ == "__main__":
    main()
