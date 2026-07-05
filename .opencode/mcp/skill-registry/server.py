"""Skill Registry MCP Server — stdio JSON-RPC 2.0 server for skill/pack queries.

Implements the MCP (Model Context Protocol) over stdio transport using only
Python stdlib. No external dependencies required.

Usage:
    python server.py [--base-dir /path/to/project]
    # Or via opencode.json MCP config (stdio transport)
"""

import json
import os
import re
import sys
from typing import Any, Callable, Dict, List, Optional


# ---------------------------------------------------------------------------
# Base directory detection
# ---------------------------------------------------------------------------

def _find_project_root(start: str) -> str:
    """Walk up from start to find a directory containing .opencode/."""
    current = os.path.abspath(start)
    while True:
        if os.path.isdir(os.path.join(current, ".opencode")):
            return current
        parent = os.path.dirname(current)
        if parent == current:
            # Reached filesystem root without finding .opencode/
            return os.path.abspath(start)
        current = parent


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
    {
        "name": "list_installed_packs",
        "description": (
            "List all installed packs with versions from .opencode/installed-packs.json."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {},
        },
    },
    {
        "name": "list_available_packs",
        "description": (
            "List all available packs from packs/*/pack-manifest.json with skill counts."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {},
        },
    },
    {
        "name": "search_skills",
        "description": (
            "Search installed skills by keyword. Reads SKILL.md frontmatter "
            "descriptions from .opencode/skills/*/SKILL.md."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "keyword": {
                    "type": "string",
                    "description": "Keyword or phrase to search for in skill descriptions.",
                },
            },
            "required": ["keyword"],
        },
    },
    {
        "name": "get_pack_info",
        "description": (
            "Get pack details (name, version, skill_count, skills list) from "
            "pack-manifest.json. Accepts either alias or pack directory name."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "pack": {
                    "type": "string",
                    "description": "Pack alias (e.g. 'course') or directory name (e.g. 'opencode-course-skills-pack').",
                },
            },
            "required": ["pack"],
        },
    },
    {
        "name": "get_profile_mapping",
        "description": (
            "Return the profile-to-pack mapping. Profiles define sets of packs "
            "auto-installed for different project types (minimal, course, code, etc.)."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {},
        },
    },
]


# ---------------------------------------------------------------------------
# Server
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# Alias → pack directory name mapping (mirrors catalog_query.py ALIAS_MAP)
# ---------------------------------------------------------------------------

_ALIAS_TO_DIR: Dict[str, str] = {
    "init": "project-initializer-skill",
    "companion": "petfish-companion-skill",
    "course": "opencode-course-skills-pack",
    "deploy": "repo-deploy-ops-skill-pack",
    "petfish": "petfish-style-skill",
    "ppt": "opencode-ppt-skills",
    "testdocs": "opencode-skill-pack-testcases-usage-docs",
    "trust": "trustskills-governance-pack",
    "calibrate": "judgment-calibration-pack",
    "council-thinking": "judgment-calibration-pack",
    "context": "fish-trail",
    "research": "research-skill-pack",
    "reflect": "fish-reflection-pack",
}

_DIR_TO_ALIAS: Dict[str, str] = {v: k for k, v in _ALIAS_TO_DIR.items()}


class SkillRegistryServer:
    """MCP server that answers queries about installed/available skill packs."""

    def __init__(self, base_dir: str):
        self.base_dir = base_dir
        self._handlers: Dict[str, Callable] = {}
        self._register_handlers()

    # -- Data readers --------------------------------------------------------

    def _read_installed_packs(self) -> Dict[str, Any]:
        """Read .opencode/installed-packs.json. Returns empty dict if not found."""
        path = os.path.join(self.base_dir, ".opencode", "installed-packs.json")
        if not os.path.exists(path):
            return {"packs": {}}
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            return {"packs": {}}

    def _read_all_manifests(self) -> List[Dict[str, Any]]:
        """Read all pack-manifest.json files from packs/*/directories."""
        packs_dir = os.path.join(self.base_dir, "packs")
        manifests = []
        if not os.path.isdir(packs_dir):
            return manifests

        for entry in sorted(os.listdir(packs_dir)):
            manifest_path = os.path.join(
                packs_dir, entry, "pack-manifest.json"
            )
            if os.path.isfile(manifest_path):
                try:
                    with open(manifest_path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        data["_directory"] = entry
                        manifests.append(data)
                except (json.JSONDecodeError, OSError):
                    pass
        return manifests

    def _read_skill_frontmatter(self, skill_dir: str) -> Optional[Dict[str, Any]]:
        """Extract frontmatter from a SKILL.md file. Returns dict or None."""
        skill_md = os.path.join(skill_dir, "SKILL.md")
        if not os.path.isfile(skill_md):
            return None

        try:
            with open(skill_md, "r", encoding="utf-8") as f:
                first_line = f.readline()
                if not first_line.strip() == "---":
                    return None
                # Read until closing ---
                lines = []
                for line in f:
                    if line.strip() == "---":
                        break
                    lines.append(line)
                # Simple YAML-ish frontmatter parser (key: value only)
                fm: Dict[str, str] = {}
                for line in lines:
                    stripped = line.strip()
                    if ":" in stripped:
                        key, _, val = stripped.partition(":")
                        fm[key.strip()] = val.strip().strip('"').strip("'")
                return fm
        except OSError:
            return None

    def _find_skill_dirs(self) -> List[str]:
        """Find all skill directories under .opencode/skills/"""
        skills_root = os.path.join(self.base_dir, ".opencode", "skills")
        if not os.path.isdir(skills_root):
            return []
        result = []
        for entry in sorted(os.listdir(skills_root)):
            skill_dir = os.path.join(skills_root, entry)
            if os.path.isdir(skill_dir):
                result.append(skill_dir)
        return result

    def _load_profile_mapping(self) -> Dict[str, List[str]]:
        """Load profile→pack mapping.

        Attempts to read from catalog_query.py PROFILES dict.
        Falls back to built-in mapping from README if not available.
        """
        # Try to import from catalog_query.py
        catalog_path = os.path.join(
            self.base_dir,
            "packs",
            "petfish-companion-skill",
            ".opencode",
            "skills",
            "petfish-companion",
            "scripts",
            "catalog_query.py",
        )
        if os.path.isfile(catalog_path):
            try:
                # Parse PROFILES dict from the file without importing
                with open(catalog_path, "r", encoding="utf-8") as f:
                    content = f.read()
                # Look for PROFILES = { ... }
                m = re.search(
                    r"PROFILES\s*=\s*(\{.*?\n\})", content, re.DOTALL
                )
                if m:
                    # Extract using eval with restricted context
                    profiles = eval(m.group(1), {"__builtins__": {}}, {})
                    if isinstance(profiles, dict):
                        # Convert to simple dict of lists
                        result: Dict[str, List[str]] = {}
                        for k, v in profiles.items():
                            if isinstance(v, list):
                                result[str(k)] = [str(x) for x in v]
                            else:
                                result[str(k)] = [str(v)]
                        if result:
                            return result
            except Exception:
                pass

        # Built-in fallback from README Profile → Auto-Install Mapping table
        return {
            "minimal": ["context", "petfish"],
            "course": ["context", "course", "petfish"],
            "code": ["context", "deploy", "petfish", "testdocs"],
            "ops": ["context", "deploy", "petfish"],
            "security": ["context", "deploy", "petfish", "testdocs", "trust"],
            "research": ["context", "petfish", "research"],
            "writing": ["context", "petfish", "ppt"],
            "skills-package": ["context", "petfish", "testdocs"],
            "comprehensive": [
                "course",
                "deploy",
                "petfish",
                "ppt",
                "testdocs",
                "trust",
                "context",
                "research",
                "reflect",
            ],
        }

    # -- Handler registration -----------------------------------------------

    def _register_handlers(self) -> None:
        h = self._handlers
        h["list_installed_packs"] = self._handle_list_installed_packs
        h["list_available_packs"] = self._handle_list_available_packs
        h["search_skills"] = self._handle_search_skills
        h["get_pack_info"] = self._handle_get_pack_info
        h["get_profile_mapping"] = self._handle_get_profile_mapping

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
                    "serverInfo": {"name": "skill-registry", "version": "0.1.0"},
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

    def _handle_list_installed_packs(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """List all installed packs with versions."""
        data = self._read_installed_packs()
        packs = data.get("packs", {})
        result = []
        for pack_name, info in packs.items():
            result.append(
                {
                    "name": pack_name,
                    "version": info.get("version", "unknown"),
                    "skill_count": info.get("skill_count", 0),
                    "installed_at": info.get("installed_at", ""),
                    "description": info.get("description", ""),
                    "skills": info.get("skills", []),
                }
            )
        return {"installed_packs": result, "total": len(result)}

    def _handle_list_available_packs(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """List all available packs from pack manifests."""
        manifests = self._read_all_manifests()
        result = []
        for m in manifests:
            dir_name = m.get("_directory", "")
            name = m.get("name", "")
            alias = m.get("alias", "") or _DIR_TO_ALIAS.get(dir_name, "") or _DIR_TO_ALIAS.get(name, "")
            result.append(
                {
                    "name": name,
                    "version": m.get("version", "unknown"),
                    "description": m.get("description", ""),
                    "skill_count": m.get("skill_count", 0),
                    "skills": m.get("skills", []),
                    "alias": alias,
                    "_directory": dir_name,
                }
            )
        return {"available_packs": result, "total": len(result)}

    def _handle_search_skills(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Search installed skills by keyword in their SKILL.md descriptions."""
        keyword = str(args.get("keyword", "")).lower().strip()
        if not keyword:
            return {"error": "keyword is required", "results": [], "total": 0}

        skill_dirs = self._find_skill_dirs()
        results = []
        for skill_dir in skill_dirs:
            fm = self._read_skill_frontmatter(skill_dir)
            if fm is None:
                continue
            name = fm.get("name", os.path.basename(skill_dir))
            desc = fm.get("description", "")
            # Search in name and description (case-insensitive)
            if keyword in name.lower() or keyword in desc.lower():
                results.append(
                    {
                        "name": name,
                        "description": desc,
                        "path": skill_dir,
                    }
                )
        return {"keyword": keyword, "results": results, "total": len(results)}

    def _handle_get_pack_info(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Get pack details by alias or pack directory name."""
        pack = str(args.get("pack", "")).strip()
        if not pack:
            return {"error": "pack name or alias is required"}

        # Resolve alias to directory name using static map + manifest aliases
        manifests = self._read_all_manifests()

        # Build manifest-based alias map (manifests with explicit "alias" field)
        manifest_alias: Dict[str, str] = {}
        for m in manifests:
            a = m.get("alias", "")
            if a:
                manifest_alias[a] = m.get("_directory", "")

        # Resolve: alias → directory name
        target_dir = _ALIAS_TO_DIR.get(pack)  # static alias map
        if target_dir is None:
            target_dir = manifest_alias.get(pack)  # manifest alias
        if target_dir is None:
            # Try matching by pack directory name or manifest name directly
            for m in manifests:
                if m.get("_directory") == pack or m.get("name") == pack:
                    target_dir = m.get("_directory", "")
                    break

        # Read the manifest
        if target_dir:
            manifest_path = os.path.join(
                self.base_dir, "packs", target_dir, "pack-manifest.json"
            )
            if os.path.isfile(manifest_path):
                try:
                    with open(manifest_path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    return {
                        "name": data.get("name", ""),
                        "version": data.get("version", "unknown"),
                        "description": data.get("description", ""),
                        "alias": data.get("alias", "") or _DIR_TO_ALIAS.get(target_dir, ""),
                        "skill_count": data.get("skill_count", 0),
                        "command_count": data.get("command_count", 0),
                        "agent_count": data.get("agent_count", 0),
                        "mcp_count": data.get("mcp_count", 0),
                        "skills": data.get("skills", []),
                    }
                except (json.JSONDecodeError, OSError) as exc:
                    return {"error": "Failed to read manifest: {}".format(exc)}

        # Not found in manifests — check installed packs as fallback
        installed = self._read_installed_packs()
        installed_packs = installed.get("packs", {})

        # Translate alias to installed pack name
        installed_alias = _ALIAS_TO_DIR.get(pack)
        if installed_alias and installed_alias in installed_packs:
            info = installed_packs[installed_alias]
            return {
                "name": installed_alias,
                "version": info.get("version", "unknown"),
                "description": info.get("description", ""),
                "alias": pack,
                "skill_count": info.get("skill_count", 0),
                "skills": info.get("skills", []),
                "source": "installed-packs.json",
            }

        # Direct match on installed pack name
        if pack in installed_packs:
            info = installed_packs[pack]
            return {
                "name": pack,
                "version": info.get("version", "unknown"),
                "description": info.get("description", ""),
                "alias": _DIR_TO_ALIAS.get(pack, ""),
                "skill_count": info.get("skill_count", 0),
                "skills": info.get("skills", []),
                "source": "installed-packs.json",
            }

        return {"error": "Pack not found: {}".format(pack)}

    def _handle_get_profile_mapping(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Return the profile→pack mapping."""
        mapping = self._load_profile_mapping()
        return {
            "profiles": mapping,
            "total_profiles": len(mapping),
        }


# ---------------------------------------------------------------------------
# Main loop
# ---------------------------------------------------------------------------


def main() -> None:
    """Run the MCP server on stdio."""
    args = sys.argv[1:]
    base_dir = os.path.abspath(".")

    # Allow --base-dir override
    for i, arg in enumerate(args):
        if arg == "--base-dir" and i + 1 < len(args):
            base_dir = os.path.abspath(args[i + 1])
            break

    # Auto-detect project root by walking up for .opencode/
    base_dir = _find_project_root(base_dir)

    server = SkillRegistryServer(base_dir)

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
