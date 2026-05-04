"""Context State MCP Server — stdio JSON-RPC 2.0 server for topic governance.

Implements the MCP (Model Context Protocol) over stdio transport using only
Python stdlib. No external dependencies required.

Usage:
    python server.py [--base-dir .ai-context]
    # Or via opencode.json MCP config (stdio transport)
"""

import json
import os
import sys
from typing import Any, Callable, Dict, List, Optional

# Add the directory containing this file to sys.path so sibling imports work
# regardless of how the server is launched (direct script, module, or MCP).
_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
if _THIS_DIR not in sys.path:
    sys.path.insert(0, _THIS_DIR)

from topic_store import TopicStore  # noqa: E402
from topic_detector import TopicDetector  # noqa: E402
from contamination_scorer import ContaminationScorer  # noqa: E402
from context_builder import ContextBuilder  # noqa: E402
from session_store import SessionStore  # noqa: E402


# ---------------------------------------------------------------------------
# Minimal MCP server over stdio (LSP base protocol framing)
# ---------------------------------------------------------------------------


def _read_message(stream) -> Optional[Dict[str, Any]]:
    """Read one JSON-RPC message using Content-Length framing."""
    headers = {}
    while True:
        line = stream.readline()
        if not line:
            return None  # EOF
        if isinstance(line, bytes):
            line = line.decode("utf-8")
        line = line.rstrip("\r\n")
        if line == "":
            break  # end of headers
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
    """Write one JSON-RPC message with Content-Length framing."""
    body = json.dumps(msg, ensure_ascii=False)
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
]


# ---------------------------------------------------------------------------
# Server implementation
# ---------------------------------------------------------------------------


class ContextStateServer:
    """MCP server that wires the 25 context-router tools to TopicStore et al."""

    def __init__(self, base_dir: str):
        self.store = TopicStore(base_dir)
        self.detector = TopicDetector()
        self.scorer = ContaminationScorer()
        self.builder = ContextBuilder(base_dir)
        self.sessions = SessionStore(base_dir)

        self._handlers = {}  # type: Dict[str, Callable]
        self._register_handlers()

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
                    "serverInfo": {"name": "context-state", "version": "0.2.0"},
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

    def _dispatch_tool_call(
        self, msg_id: Any, params: Dict[str, Any]
    ) -> Dict[str, Any]:
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

    def _handle_topic_update(self, args: Dict[str, Any]) -> Dict[str, Any]:
        topic_id = args.pop("topic_id")
        return self.store.update(topic_id, **args)

    def _handle_topic_archive(self, args: Dict[str, Any]) -> Dict[str, Any]:
        return self.store.archive(args["topic_id"])

    def _handle_topic_search(self, args: Dict[str, Any]) -> List[Dict[str, Any]]:
        return self.store.search(args["query"])

    def _handle_topic_link(self, args: Dict[str, Any]) -> Dict[str, Any]:
        return self.store.link(args["source"], args["target"], args["relation"])

    def _handle_topic_unlink(self, args: Dict[str, Any]) -> bool:
        return self.store.unlink(args["source"], args["target"])

    def _handle_topic_graph(self, args: Dict[str, Any]) -> Dict[str, Any]:
        return self.store.graph()

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


# ---------------------------------------------------------------------------
# Main loop
# ---------------------------------------------------------------------------


def main() -> None:
    """Run the MCP server on stdio."""
    base_dir = ".ai-context"

    # Allow --base-dir override
    args = sys.argv[1:]
    for i, arg in enumerate(args):
        if arg == "--base-dir" and i + 1 < len(args):
            base_dir = args[i + 1]
            break

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
