#!/usr/bin/env python3
"""
Multi-Model Memory Architecture Benchmark v4
3 arms x 3 models x 10 prompts x 3 rounds = 270 entries

Arms:
- full-v2: Always-On per-turn MCP rules + NO inject plugin
- disk-compact: v2 plugin rules + inject plugin (compact ~48 tok)
- disk-full: v2 plugin rules + inject plugin (full ~108 tok)

Ground truth: MCP server log from .petfish/fish-trail/mcp-call-log.jsonl
"""
import httpx, base64, json, time, statistics, os, subprocess, sys, shutil

basic = 'basic ' + base64.b64encode(b'opencode:test').decode()

MODELS = [
    "deepseek/deepseek-v4-flash",
    "github-copilot/claude-sonnet-4.6",
    "openai/gpt-5.4-mini",
]

ARMS = ["full-v2", "disk-compact", "disk-full"]

PROMPTS = [
    "What topic are we currently working on?",
    "What is the status of the QA Audit Topic?",
    "Tell me about API Monitoring Setup",
    "What topics exist in this project?",
    "Switch to Performance Benchmarking topic",
    "What did we discuss about QA audits?",
    "Are there any links between topics?",
    "What's the current active topic?",
    "Summarize what we know about API Monitoring",
    "Is Performance Benchmarking still active?",
]

ROUNDS = 3
BASE = "/tmp/opencode/bench_v4"
TPL = f"{BASE}/workspaces/_tpl"
RESULTS_FILE = f"{BASE}/results/membench-v4-results.jsonl"

def setup_workspace(model, arm):
    safe = model.replace("/", "_")
    ws = f"{BASE}/workspaces/{safe}_{arm}"
    if os.path.exists(ws):
        shutil.rmtree(ws)
    shutil.copytree(TPL, ws)

    ar = f"{ws}/.opencode/agents-rules"

    if arm == "full-v2":
        plugin_cfg = '[[".opencode/plugin/system-prompt-rules.ts", {"mode": "all"}]]'
        inject = f"{ws}/.opencode/plugin/system-prompt-context-inject.ts"
        if os.path.exists(inject):
            os.remove(inject)
        shutil.copy(f"{TPL}/.opencode/agents-rules/fish-trail-old.md", f"{ar}/fish-trail.md")
        for f in ["fish-trail-plugin.md", "fish-trail-old.md"]:
            p = f"{ar}/{f}"
            if os.path.exists(p): os.remove(p)
    elif arm == "disk-compact":
        plugin_cfg = '[[".opencode/plugin/system-prompt-context-inject.ts", {"mode": "disk", "compressionLevel": "compact"}], [".opencode/plugin/system-prompt-rules.ts", {"mode": "all"}]]'
        shutil.copy(f"{TPL}/.opencode/agents-rules/fish-trail-plugin.md", f"{ar}/fish-trail.md")
        for f in ["fish-trail-plugin.md", "fish-trail-old.md"]:
            p = f"{ar}/{f}"
            if os.path.exists(p): os.remove(p)
    elif arm == "disk-full":
        plugin_cfg = '[[".opencode/plugin/system-prompt-context-inject.ts", {"mode": "disk", "compressionLevel": "full"}], [".opencode/plugin/system-prompt-rules.ts", {"mode": "all"}]]'
        shutil.copy(f"{TPL}/.opencode/agents-rules/fish-trail-plugin.md", f"{ar}/fish-trail.md")
        for f in ["fish-trail-plugin.md", "fish-trail-old.md"]:
            p = f"{ar}/{f}"
            if os.path.exists(p): os.remove(p)

    config = {
        "$schema": "https://opencode.ai/config.json",
        "model": model,
        
        "plugin": json.loads(plugin_cfg),
        "permission": {"skill": {"fish-trail": "allow"}}
    }
    with open(f"{ws}/opencode.json", "w") as f:
        json.dump(config, f, indent=2)

    return ws

def read_mcp_log(ws):
    log_path = f"{ws}/.petfish/fish-trail/mcp-call-log.jsonl"
    calls = []
    if os.path.exists(log_path):
        with open(log_path, "r") as f:
            for line in f:
                line = line.strip()
                if line:
                    try: calls.append(json.loads(line))
                    except: pass
    return calls

def start_server(port, ws):
    log = f"{BASE}/results/server_{port}.log"
    env = os.environ.copy()
    env["OPENCODE_SERVER_PASSWORD"] = "test"
    proc = subprocess.Popen(
        ["opencode", "serve", "--port", str(port)],
        cwd=ws, stdout=open(log, "w"), stderr=subprocess.STDOUT, env=env,
    )
    for i in range(90):
        try:
            r = httpx.post(f'http://localhost:{port}/session',
                          headers={'Authorization': basic}, timeout=5)
            if r.status_code == 200:
                return proc
        except:
            time.sleep(1)
    # Check if process is still alive
    if proc.poll() is None:
        raise Exception(f"Server on port {port} listening but session creation hangs")
    raise Exception(f"Server on port {port} crashed (exit code {proc.returncode})")

def stop_server(proc):
    if proc:
        proc.terminate()
        try: proc.wait(timeout=10)
        except:
            proc.kill()
            try: proc.wait(timeout=5)
            except: pass

def create_session(port):
    r = httpx.post(f'http://localhost:{port}/session', headers={'Authorization': basic}, timeout=30)
    return r.json()['id']

def send_message(port, sid, prompt):
    r = httpx.post(
        f'http://localhost:{port}/session/{sid}/message',
        headers={'Authorization': basic, 'Content-Type': 'application/json'},
        json={"parts": [{"type": "text", "text": prompt}]},
        timeout=300,
    )
    body = r.json()
    info = body.get("info", {})
    tokens = info.get("tokens", {})
    resp_text = ""
    tool_calls_resp = []
    for part in body.get("parts", []):
        if part.get("type") == "text":
            resp_text += part.get("text", "")
        if part.get("type") == "tool":
            tool_calls_resp.append(part.get("tool", part.get("name", "unknown")))
    return {
        "total_tokens": tokens.get("total", 0),
        "input_tokens": tokens.get("input", 0),
        "output_tokens": tokens.get("output", 0),
        "cache_read": tokens.get("cache", {}).get("read", 0),
        "cache_write": tokens.get("cache", {}).get("write", 0),
        "reasoning_tokens": tokens.get("reasoning", 0),
        "cost": info.get("cost", 0),
        "model_id": info.get("modelID", ""),
        "provider_id": info.get("providerID", ""),
        "response": resp_text[:800],
        "tool_calls": tool_calls_resp,
    }

# Make sure no leftover servers
subprocess.run(["pkill", "-9", "-f", "opencode serve"], capture_output=True)
time.sleep(3)

all_results = []
port = 3700

for model in MODELS:
    print(f"\n{'='*60}")
    print(f"MODEL: {model}")
    print(f"{'='*60}")

    for arm in ARMS:
        print(f"\n  ARM: {arm} (port {port})")
        ws = setup_workspace(model, arm)

        try:
            proc = start_server(port, ws)
        except Exception as e:
            print(f"  FAILED: {e}")
            for pidx in range(len(PROMPTS)):
                for ridx in range(1, ROUNDS+1):
                    all_results.append({
                        "experiment_id": "membench-v4-20260525", "model": model, "arm": arm,
                        "round": ridx, "prompt_idx": pidx+1, "prompt": PROMPTS[pidx],
                        "wall_seconds": 0, "total_tokens": 0, "input_tokens": 0, "output_tokens": 0,
                        "cache_read": 0, "cache_write": 0, "reasoning_tokens": 0,
                        "cost": 0, "model_id": "", "provider_id": "", "response": "", "tool_calls": [],
                        "mcp_calls_count": 0, "mcp_calls_detail": [],
                        "error": f"server_failed: {str(e)[:100]}",
                    })
            port += 1
            continue

        try:
            sid = create_session(port)
            print(f"  Session: {sid}")
        except Exception as e:
            print(f"  SESSION FAILED: {e}")
            stop_server(proc)
            port += 1
            continue

        arm_results = []
        for round_idx in range(ROUNDS):
            for pidx, prompt in enumerate(PROMPTS):
                label = f"R{round_idx+1} P{pidx+1}"
                mcp_before = read_mcp_log(ws)
                start_t = time.monotonic()
                try:
                    result = send_message(port, sid, prompt)
                    elapsed = time.monotonic() - start_t
                    mcp_after = read_mcp_log(ws)
                    new_mcp = mcp_after[len(mcp_before):]
                    entry = {
                        "experiment_id": "membench-v4-20260525", "model": model, "arm": arm,
                        "round": round_idx+1, "prompt_idx": pidx+1, "prompt": prompt,
                        "wall_seconds": round(elapsed, 2),
                        **result,
                        "mcp_calls_count": len(new_mcp),
                        "mcp_calls_detail": [{"tool": c.get("tool",""), "ok": c.get("ok",""), "duration_ms": c.get("duration_ms",0)} for c in new_mcp],
                        "error": None,
                    }
                except Exception as e:
                    elapsed = time.monotonic() - start_t
                    mcp_after = read_mcp_log(ws)
                    new_mcp = mcp_after[len(mcp_before):]
                    entry = {
                        "experiment_id": "membench-v4-20260525", "model": model, "arm": arm,
                        "round": round_idx+1, "prompt_idx": pidx+1, "prompt": prompt,
                        "wall_seconds": round(elapsed, 2),
                        "total_tokens": 0, "input_tokens": 0, "output_tokens": 0,
                        "cache_read": 0, "cache_write": 0, "reasoning_tokens": 0,
                        "cost": 0, "model_id": "", "provider_id": "", "response": "", "tool_calls": [],
                        "mcp_calls_count": len(new_mcp), "mcp_calls_detail": [],
                        "error": str(e)[:200],
                    }

                all_results.append(entry)
                arm_results.append(entry)
                if entry.get('error'):
                    print(f"    {label}: ERR {entry['error'][:60]}")
                else:
                    print(f"    {label}: total={entry['total_tokens']:,} in={entry['input_tokens']:,} out={entry['output_tokens']:,} mcp={entry['mcp_calls_count']}")
                time.sleep(1.5)

        valid = [r for r in arm_results if not r.get('error')]
        if valid:
            avg_total = statistics.mean([r['total_tokens'] for r in valid])
            total_mcp = sum(r['mcp_calls_count'] for r in valid)
            print(f"  SUMMARY: avg_total={avg_total:,.0f} mcp_log={total_mcp}")
        print(f"  MCP LOG TOTAL: {len(read_mcp_log(ws))} calls")

        stop_server(proc)
        time.sleep(5)

        # Incremental save
        with open(RESULTS_FILE, 'w') as f:
            for r in all_results:
                f.write(json.dumps(r, ensure_ascii=False) + '\n')

        port += 1

# Final save
with open(RESULTS_FILE, 'w') as f:
    for r in all_results:
        f.write(json.dumps(r, ensure_ascii=False) + '\n')
with open(f"{BASE}/results/membench-v4-results.json", 'w') as f:
    json.dump(all_results, f, indent=2, ensure_ascii=False)

print(f"\nDONE. {len(all_results)} entries, {len([r for r in all_results if r.get('error')])} errors")
