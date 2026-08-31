# /// script
# requires-python = ">=3.10"
# ///
"""Skill Vault MCP Server — on-demand skill fetch/stage/install (stdio, stdlib-only).

Part of the dynamic skill-loading plan (.sisyphus/plans/dynamic-skill-loading-plan.md P1).
Skills are delivered as TOOL RESULTS (bypassing the platform's session-static
skill discovery); install makes them natively visible from the NEXT session.

Tools:
    vault_index(filter?)        list vault/market/community/installed skills (no bodies)
    vault_fetch(name)           return SKILL.md body (60KB cap, session hash dedup)
    vault_stage(source)         stage a skill from a raw GitHub URL or local path
                                (P1 scope: single-skill sources only; market pack
                                tarball staging arrives with P2 search integration)
    vault_install(name)         copy vault skill to .opencode/skills/ + regenerate
                                skill-index.json (restart required for native load)

Security: domain whitelist, 2MB skill cap, zip-slip-safe copies, mirror fallback
(ghfast.top -> ghproxy.com) for raw.githubusercontent.com URLs.

Selftest: python server.py --selftest  (used by the installer before registration)

Usage:
    via opencode.json MCP config (stdio transport), or directly for testing.
"""

import argparse
import hashlib
import json
import os
import re
import shutil
import sys
import time
import urllib.request
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

def _find_project_root(start: str) -> str:
    current = os.path.abspath(start)
    while True:
        if os.path.isdir(os.path.join(current, ".opencode")):
            return current
        parent = os.path.dirname(current)
        if parent == current:
            return os.path.abspath(start)
        current = parent


PROJECT_ROOT = Path(_find_project_root(os.getcwd()))
VAULT_DIR = PROJECT_ROOT / ".opencode" / "skill-vault"
STATE_DIR = PROJECT_ROOT / ".petfish" / "skill-vault"
STATE_FILE = STATE_DIR / "state.json"
SKILLS_DIR = PROJECT_ROOT / ".opencode" / "skills"
SKILL_INDEX = PROJECT_ROOT / ".opencode" / "skill-index.json"

MAX_SKILL_BYTES = 2 * 1024 * 1024       # 2MB per staged skill
MAX_FETCH_CHARS = 60 * 1024             # 60KB SKILL.md body cap
STATE_TTL_SECONDS = 7 * 24 * 3600       # 7-day dedup expiry

ALLOWED_HOSTS = {
    "raw.githubusercontent.com",
    "github.com",
    "ghfast.top",
    "ghproxy.com",
    "gh-proxy.com",
    "codeload.github.com",
}

# ---------------------------------------------------------------------------
# Minimal MCP stdio transport (Content-Length or bare JSONL, auto-detected)
# ---------------------------------------------------------------------------

_transport_mode: Optional[str] = None


def _read_message(stream) -> Optional[Dict[str, Any]]:
    global _transport_mode
    while True:
        line = stream.readline()
        if not line:
            return None
        if isinstance(line, bytes):
            line = line.decode("utf-8")
        stripped = line.strip()
        if stripped == "":
            continue
        break

    if _transport_mode is None:
        _transport_mode = "jsonl" if stripped.startswith("{") else "clength"

    if _transport_mode == "jsonl":
        if stripped.startswith("{"):
            try:
                return json.loads(stripped)
            except json.JSONDecodeError:
                print(f"skill-vault: skipping malformed JSONL line ({len(stripped)} chars)", file=sys.stderr)
                return _read_message(stream)
        return _read_message(stream)

    headers = {}
    while stripped:
        if ":" in stripped:
            k, _, v = stripped.partition(":")
            headers[k.strip().lower()] = v.strip()
        line = stream.readline()
        if isinstance(line, bytes):
            line = line.decode("utf-8")
        stripped = line.strip()
        if stripped == "":
            break
    length = int(headers.get("content-length", "0"))
    if length <= 0:
        return None
    body = stream.read(length)
    if isinstance(body, bytes):
        body = body.decode("utf-8")
    return json.loads(body)


def _write_message(stream, payload: Dict[str, Any]) -> None:
    data = json.dumps(payload, ensure_ascii=False)
    if _transport_mode == "jsonl":
        stream.write(data + "\n")
    else:
        body = data.encode("utf-8")
        stream.write(f"Content-Length: {len(body)}\r\n\r\n")
        stream.write(data)
    stream.flush()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _frontmatter(content: str) -> Dict[str, str]:
    m = re.match(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
    if not m:
        return {}
    out: Dict[str, str] = {}
    for line in m.group(1).split("\n"):
        if ":" in line and not line.startswith((" ", "\t")):
            k, _, v = line.partition(":")
            out[k.strip()] = v.strip().strip("\"'")
    return out


def _skill_meta(skill_dir: Path) -> Optional[Dict[str, str]]:
    md = skill_dir / "SKILL.md"
    if not md.is_file():
        return None
    try:
        content = md.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None
    fm = _frontmatter(content)
    name = fm.get("name") or skill_dir.name
    desc = fm.get("description", "")[:160]
    return {"name": name, "description": desc, "dir": skill_dir.name}


def _load_index() -> Dict[str, Any]:
    try:
        return json.loads(SKILL_INDEX.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _load_state() -> Dict[str, Any]:
    try:
        state = json.loads(STATE_FILE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        state = {}
    active = state.get("active") or {}
    expires = active.get("expires")
    if not expires or time.time() > float(expires):
        state = {"active": {"fetched": {}, "expires": time.time() + STATE_TTL_SECONDS}}
    return state


def _save_state(state: Dict[str, Any]) -> None:
    try:
        STATE_DIR.mkdir(parents=True, exist_ok=True)
        STATE_FILE.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")
    except OSError:
        pass


def _sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _is_url_allowed(url: str) -> bool:
    m = re.match(r"^https?://([^/]+)/", url)
    return bool(m) and m.group(1).lower() in ALLOWED_HOSTS


def _http_get(url: str, timeout: float = 15.0) -> Optional[bytes]:
    """GET with mirror fallback for raw.githubusercontent.com URLs."""
    candidates = [url]
    if "raw.githubusercontent.com/" in url:
        candidates = [
            url,
            url.replace("https://raw.githubusercontent.com/", "https://ghfast.top/"),
            url.replace("https://raw.githubusercontent.com/", "https://ghproxy.com/"),
        ]
    for u in candidates:
        try:
            req = urllib.request.Request(u, headers={"User-Agent": "petfish-skill-vault/1.0"})
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return resp.read()
        except Exception:
            continue
    return None


def _safe_copytree(src: Path, dst: Path) -> None:
    """Copytree with zip-slip/e scape protection: every member must resolve inside src."""
    src = src.resolve()
    dst = dst.resolve()
    dst.mkdir(parents=True, exist_ok=True)
    for item in src.rglob("*"):
        resolved = item.resolve()
        if not str(resolved).startswith(str(src)):
            continue  # escape attempt — skip
        target = dst / item.relative_to(src)
        if item.is_dir():
            target.mkdir(parents=True, exist_ok=True)
        elif item.is_file():
            if item.stat().st_size > MAX_SKILL_BYTES:
                raise ValueError(f"file too large: {item.name} ({item.stat().st_size} bytes)")
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(item, target)


def _dir_size(path: Path) -> int:
    return sum(f.stat().st_size for f in path.rglob("*") if f.is_file())


def _lint_quick(skill_dir: Path) -> Dict[str, Any]:
    """Run lint_skill.py ERROR-level check when importable; otherwise skip."""
    try:
        toolchain_root = PROJECT_ROOT / ".opencode" / "skills"
        # lint_skill.py ships in the toolchain pack; locate lazily
        for cand in toolchain_root.glob("skill-lint/scripts/lint_skill.py"):
            import importlib.util
            spec = importlib.util.spec_from_file_location("lint_skill_mod", cand)
            if spec and spec.loader:
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)
                report = getattr(mod, "lint_skill", lambda *_: None)(skill_dir)
                if isinstance(report, dict):
                    errors = sum(
                        1 for f in report.get("findings", [])
                        if str(f.get("severity", "")).upper() == "ERROR"
                    )
                    warnings = sum(
                        1 for f in report.get("findings", [])
                        if str(f.get("severity", "")).upper() == "WARNING"
                    )
                    return {"errors": errors, "warnings": warnings}
                break
    except Exception:
        pass
    return {"skipped": True}


def _regenerate_index() -> bool:
    """Best-effort skill-index regeneration (domains map preserved when present)."""
    gen_candidates = [
        PROJECT_ROOT / "scripts" / "generate_skill_index.py",
    ]
    skills_dir = SKILLS_DIR
    if not skills_dir.is_dir():
        return False
    # Prefer the repo generator when present (keeps domains in sync)
    for gen in gen_candidates:
        if gen.is_file():
            try:
                import subprocess
                subprocess.run(
                    [sys.executable, str(gen)],
                    cwd=str(PROJECT_ROOT),
                    capture_output=True,
                    timeout=60,
                    check=False,
                )
                return SKILL_INDEX.is_file()
            except Exception:
                pass
    # Fallback: minimal regeneration (names/descriptions only, keep old domains)
    old = _load_index()
    skills = []
    for d in sorted(skills_dir.iterdir()):
        meta = _skill_meta(d) if d.is_dir() else None
        if meta:
            skills.append({"name": meta["name"], "description": meta["description"]})
    index = {
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "skill_count": len(skills),
        "skills": skills,
    }
    if isinstance(old.get("domains"), dict):
        index["domains"] = old["domains"]
    try:
        SKILL_INDEX.write_text(json.dumps(index, ensure_ascii=False, indent=2), encoding="utf-8")
        return True
    except OSError:
        return False


# ---------------------------------------------------------------------------
# Tool implementations
# ---------------------------------------------------------------------------

def tool_vault_index(args: Dict[str, Any]) -> Dict[str, Any]:
    filter_kw = str(args.get("filter") or "").lower()
    out: List[Dict[str, Any]] = []

    installed_names = set()
    index = _load_index()
    for s in index.get("skills", []):
        if isinstance(s, dict) and s.get("name"):
            installed_names.add(s["name"])
            out.append({
                "name": s["name"],
                "description": str(s.get("description", ""))[:160],
                "source": "installed",
                "pack": "",
            })

    if VAULT_DIR.is_dir():
        for d in sorted(VAULT_DIR.iterdir()):
            if not d.is_dir():
                continue
            meta = _skill_meta(d)
            if not meta:
                continue
            out.append({"name": meta["name"], "description": meta["description"], "source": "vault", "pack": ""})

    for pack in (index.get("available_packs") or {}).get("market", []) or []:
        if isinstance(pack, dict):
            out.append({
                "name": str(pack.get("alias") or pack.get("name", "")),
                "description": str(pack.get("description", ""))[:160],
                "source": "market",
                "pack": str(pack.get("name", "")),
            })
    for pack in (index.get("available_packs") or {}).get("community", []) or []:
        if isinstance(pack, dict):
            out.append({
                "name": str(pack.get("name", "")),
                "description": str(pack.get("description", ""))[:160],
                "source": "community",
                "pack": str(pack.get("repo", "")),
            })

    if filter_kw:
        out = [
            e for e in out
            if filter_kw in e["name"].lower() or filter_kw in e["description"].lower()
        ]
    return {"skills": out, "total": len(out)}


def tool_vault_fetch(args: Dict[str, Any]) -> Dict[str, Any]:
    name = str(args.get("name") or "").strip()
    if not name:
        raise ValueError("name is required")
    skill_dir = VAULT_DIR / name
    # Allow directory-name match fallback
    if not skill_dir.is_dir():
        for d in VAULT_DIR.iterdir() if VAULT_DIR.is_dir() else []:
            meta = _skill_meta(d)
            if meta and meta["name"] == name:
                skill_dir = d
                break
    md = skill_dir / "SKILL.md"
    if not md.is_file():
        raise FileNotFoundError(
            f"skill '{name}' not in vault (.opencode/skill-vault/). "
            "Use vault_stage(source) first, or vault_index to see sources."
        )
    content = md.read_text(encoding="utf-8", errors="replace")
    digest = _sha256(content)
    state = _load_state()
    fetched = state["active"]["fetched"]
    files = sorted(
        str(p.relative_to(skill_dir)) for p in skill_dir.rglob("*") if p.is_file()
    )
    if fetched.get(name, {}).get("sha256") == digest:
        return {"name": name, "sha256": digest, "already_loaded": True, "files": files}
    truncated = len(content) > MAX_FETCH_CHARS
    fetched[name] = {"sha256": digest, "ts": time.time()}
    state["active"]["expires"] = time.time() + STATE_TTL_SECONDS
    _save_state(state)
    return {
        "name": name,
        "sha256": digest,
        "content": content[:MAX_FETCH_CHARS],
        "truncated": truncated,
        "files": files,
    }


def tool_vault_stage(args: Dict[str, Any]) -> Dict[str, Any]:
    source = str(args.get("source") or "").strip()
    if not source:
        raise ValueError("source is required (raw GitHub URL to SKILL.md, or local path)")

    name: Optional[str] = None
    skill_md_text: Optional[str] = None

    if re.match(r"^https?://", source):
        if not _is_url_allowed(source):
            raise PermissionError(f"host not in whitelist: {source}")
        data = _http_get(source)
        if data is None:
            raise ConnectionError(f"download failed (mirror fallback exhausted): {source}")
        if len(data) > MAX_SKILL_BYTES:
            raise ValueError(f"SKILL.md too large: {len(data)} bytes (cap {MAX_SKILL_BYTES})")
        skill_md_text = data.decode("utf-8", errors="replace")
        fm = _frontmatter(skill_md_text)
        name = fm.get("name") or re.sub(r"[^a-z0-9-]", "-", source.rsplit("/", 1)[-1].replace(".md", "").lower()).strip("-")
    else:
        src_path = (PROJECT_ROOT / source).resolve() if not os.path.isabs(source) else Path(source).resolve()
        if not src_path.is_file():
            raise FileNotFoundError(f"local source not found: {source}")
        skill_md_text = src_path.read_text(encoding="utf-8", errors="replace")
        fm = _frontmatter(skill_md_text)
        name = fm.get("name") or src_path.parent.name

    if not name:
        raise ValueError("cannot derive skill name from source (missing frontmatter name)")
    dest = VAULT_DIR / name
    dest.mkdir(parents=True, exist_ok=True)
    (dest / "SKILL.md").write_text(skill_md_text, encoding="utf-8")

    lint = _lint_quick(dest)
    if lint.get("errors"):
        shutil.rmtree(dest, ignore_errors=True)
        raise ValueError(f"lint ERRORs ({lint['errors']}) — skill rejected and removed from vault")

    return {"name": name, "staged": True, "path": f".opencode/skill-vault/{name}", "lint": lint}


def tool_vault_install(args: Dict[str, Any]) -> Dict[str, Any]:
    name = str(args.get("name") or "").strip()
    if not name:
        raise ValueError("name is required")
    skill_dir = VAULT_DIR / name
    if not (skill_dir / "SKILL.md").is_file():
        raise FileNotFoundError(f"skill '{name}' not in vault — vault_stage first")
    if _dir_size(skill_dir) > MAX_SKILL_BYTES:
        raise ValueError("skill exceeds 2MB cap")
    dest = SKILLS_DIR / name
    _safe_copytree(skill_dir, dest)
    index_ok = _regenerate_index()
    return {"name": name, "installed": True, "restart_required": True, "index_regenerated": index_ok}


TOOLS: Dict[str, Tuple[str, str, Callable[[Dict[str, Any]], Dict[str, Any]]]] = {
    "vault_index": (
        "List all skill sources (installed / vault / market / community) with names and short descriptions. No bodies.",
        "filter: string (optional keyword)",
        tool_vault_index,
    ),
    "vault_fetch": (
        "Fetch a staged skill's SKILL.md body on demand (60KB cap, session hash dedup — repeat calls return a short already_loaded marker).",
        "name: string (skill name from vault_index)",
        tool_vault_fetch,
    ),
    "vault_stage": (
        "Stage a skill into .opencode/skill-vault/ from a raw GitHub URL (to SKILL.md) or a local path. Domain whitelist + size cap + lint ERROR gate.",
        "source: string (URL or path)",
        tool_vault_stage,
    ),
    "vault_install": (
        "Copy a vault skill to .opencode/skills/ and regenerate skill-index.json. Native visibility from the NEXT session (restart required).",
        "name: string",
        tool_vault_install,
    ),
}


# ---------------------------------------------------------------------------
# Selftest
# ---------------------------------------------------------------------------

def _selftest() -> int:
    failures: List[str] = []

    def check(name: str, cond: bool, detail: str = "") -> None:
        print(f"  {'PASS' if cond else 'FAIL'}  {name}" + ("" if cond else f"  {detail}"))
        if not cond:
            failures.append(name)

    import tempfile
    with tempfile.TemporaryDirectory() as td:
        tdp = Path(td)
        # truncation
        check("60KB truncation flag", len("x" * (MAX_FETCH_CHARS + 10)) > MAX_FETCH_CHARS)
        # zip-slip guard: _safe_copytree skips escaping symlinks (dir-based)
        src = tdp / "s"; src.mkdir()
        (src / "SKILL.md").write_text("---\nname: t\n---\nbody", encoding="utf-8")
        dst = tdp / "d"
        try:
            _safe_copytree(src, dst)
            check("safe copytree copies files", (dst / "SKILL.md").is_file())
        except Exception as exc:
            check("safe copytree copies files", False, str(exc))
        # whitelist
        check("whitelist allows raw.githubusercontent", _is_url_allowed("https://raw.githubusercontent.com/a/b/c/SKILL.md"))
        check("whitelist blocks evil host", not _is_url_allowed("https://evil.example.com/x"))
        # frontmatter
        fm = _frontmatter("---\nname: my-skill\ndescription: d\n---\nbody")
        check("frontmatter parse", fm.get("name") == "my-skill")
        # state dedup round-trip (use real state path but clean up)
        global STATE_FILE
        real_state = STATE_FILE
        try:
            STATE_FILE = tdp / "state.json"
            st = _load_state()
            st["active"]["fetched"]["x"] = {"sha256": "h", "ts": time.time()}
            _save_state(st)
            st2 = _load_state()
            check("state round-trip + ttl", st2["active"]["fetched"].get("x", {}).get("sha256") == "h")
        finally:
            STATE_FILE = real_state

    print()
    if failures:
        print(f"SELFTEST: {len(failures)} failure(s): {failures}")
        return 1
    print("SELFTEST: all pass")
    return 0


# ---------------------------------------------------------------------------
# MCP dispatch
# ---------------------------------------------------------------------------

def handle(request: Dict[str, Any]) -> Dict[str, Any]:
    method = request.get("method", "")
    req_id = request.get("id")
    params = request.get("params") or {}

    if method == "initialize":
        return {
            "jsonrpc": "2.0", "id": req_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "skill-vault", "version": "1.0.0"},
            },
        }
    if method == "notifications/initialized":
        return {"jsonrpc": "2.0", "id": req_id, "result": {}}
    if method == "tools/list":
        return {
            "jsonrpc": "2.0", "id": req_id,
            "result": {
                "tools": [
                    {
                        "name": name,
                        "description": desc,
                        "inputSchema": {"type": "object", "properties": _schema_of(sig), "required": _required_of(sig)},
                    }
                    for name, (desc, sig, _fn) in TOOLS.items()
                ]
            },
        }
    if method == "tools/call":
        tname = str(params.get("name") or "")
        if tname not in TOOLS:
            return {
                "jsonrpc": "2.0", "id": req_id,
                "result": {"isError": True, "content": [{"type": "text", "text": f"unknown tool: {tname}"}]},
            }
        try:
            result = TOOLS[tname][2](params.get("arguments") or {})
            return {
                "jsonrpc": "2.0", "id": req_id,
                "result": {"content": [{"type": "text", "text": json.dumps(result, ensure_ascii=False)}]},
            }
        except Exception as exc:
            return {
                "jsonrpc": "2.0", "id": req_id,
                "result": {"isError": True, "content": [{"type": "text", "text": f"{type(exc).__name__}: {exc}"}]},
            }
    if method == "ping":
        return {"jsonrpc": "2.0", "id": req_id, "result": {}}
    return {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32601, "message": f"method not found: {method}"}}


def _schema_of(sig: str) -> Dict[str, Any]:
    props: Dict[str, Any] = {}
    for part in [p.strip() for p in sig.split(",") if p.strip()]:
        if ":" in part:
            key, _, rest = part.partition(":")
            optional = "(optional" in rest
            typ = "string"
            if "bool" in rest:
                typ = "boolean"
            props[key.strip()] = {"type": typ, **({"description": rest.split(")", 1)[-1].strip()} if rest else {})}
    return props


def _required_of(sig: str) -> List[str]:
    return [
        p.split(":")[0].strip()
        for p in sig.split(",")
        if p.strip() and "(optional" not in p
    ]


def main() -> int:
    ap = argparse.ArgumentParser(description="Skill Vault MCP Server")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()
    if args.selftest:
        return _selftest()
    while True:
        msg = _read_message(sys.stdin)
        if msg is None:
            return 0
        _write_message(sys.stdout, handle(msg))


if __name__ == "__main__":
    sys.exit(main())
