#!/usr/bin/env python3
"""
Multi-Model Memory Architecture Benchmark v3
Fixed: proper rules differentiation between disk-v2 and full-v2 arms.
- disk-v2: fish-trail-plugin.md (v2 rules, [disk|rMCP:off] aware) + inject plugin
- full-v2: fish-trail-old.md (Always-On per-turn MCP rules) + NO inject plugin
"""
import httpx, base64, json, time, statistics, os, subprocess, sys, shutil

basic = 'basic ' + base64.b64encode(b'opencode:test').decode()

MODELS = [
    "deepseek/deepseek-v4-pro",
    "deepseek/deepseek-v4-flash",
    "github-copilot/claude-sonnet-4.6",
    "github-copilot/gpt-4o",
    "openai/gpt-5.4-mini",
]

ARMS = ["disk-v2", "full-v2"]

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
BASE = "/tmp/opencode/bench_multi_v3"
TPL = f"{BASE}/_template"
RESULTS_FILE = f"{BASE}/membench-v3-results.jsonl"

def setup_workspace(model, arm):
    safe = model.replace("/", "_")
    ws = f"{BASE}/{safe}_{arm}"
    if os.path.exists(ws):
        shutil.rmtree(ws)
    shutil.copytree(TPL, ws)

    agents_rules_dir = f"{ws}/.opencode/agents-rules"

    if arm == "disk-v2":
        plugin_cfg = '[[".opencode/plugin/system-prompt-context-inject.ts", {"mode": "disk"}], [".opencode/plugin/system-prompt-rules.ts", {"mode": "all"}]]'
        shutil.copy(f"{TPL}/.opencode/agents-rules/fish-trail-plugin.md", f"{agents_rules_dir}/fish-trail.md")
        fish_trail_rules = f"{agents_rules_dir}/fish-trail-old.md"
        if os.path.exists(fish_trail_rules):
            os.remove(fish_trail_rules)
    else:
        plugin_cfg = '[[".opencode/plugin/system-prompt-rules.ts", {"mode": "all"}]]'
        inject = f"{ws}/.opencode/plugin/system-prompt-context-inject.ts"
        if os.path.exists(inject):
            os.remove(inject)
        shutil.copy(f"{TPL}/.opencode/agents-rules/fish-trail-old.md", f"{agents_rules_dir}/fish-trail.md")
        fish_trail_plugin = f"{agents_rules_dir}/fish-trail-plugin.md"
        if os.path.exists(fish_trail_plugin):
            os.remove(fish_trail_plugin)

    config = {
        "$schema": "https://opencode.ai/config.json",
        "model": model,
        "mcp": {
            "context-state": {
                "type": "local",
                "command": ["uv", "run", "python", ".opencode/skills/fish-trail/mcp/context-state/server.py"]
            }
        },
        "plugin": json.loads(plugin_cfg),
        "permission": {"skill": {"fish-trail": "allow"}}
    }

    with open(f"{ws}/opencode.json", "w") as f:
        json.dump(config, f, indent=2)

    return ws

def start_server(port, ws):
    log = f"{BASE}/server_{port}.log"
    proc = subprocess.Popen(
        ["opencode", "serve", "--port", str(port)],
        cwd=ws, stdout=open(log, "w"), stderr=subprocess.STDOUT
    )
    for i in range(60):
        try:
            r = httpx.post(f'http://localhost:{port}/session',
                          headers={'Authorization': basic}, timeout=3)
            if r.status_code == 200:
                return proc
        except:
            time.sleep(1)
    raise Exception(f"Server on port {port} not ready after 60s")

def stop_server(proc):
    if proc:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except:
            proc.kill()

def create_session(port):
    r = httpx.post(f'http://localhost:{port}/session', headers={'Authorization': basic}, timeout=10)
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
    tool_calls = []
    for part in body.get("parts", []):
        if part.get("type") == "text":
            resp_text += part.get("text", "")
        if part.get("type") == "tool":
            tool_name = part.get("tool", part.get("name", "unknown"))
            tool_calls.append(tool_name)

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
        "tool_calls": tool_calls,
    }

all_results = []
port_counter = 3520

for model in MODELS:
    safe = model.replace("/", "_")
    print(f"\n{'='*60}")
    print(f"MODEL: {model}")
    print(f"{'='*60}")

    for arm in ARMS:
        port = port_counter
        port_counter += 1

        print(f"\n  ARM: {arm} (port {port})")

        ws = setup_workspace(model, arm)
        print(f"  Workspace: {ws}")

        try:
            proc = start_server(port, ws)
        except Exception as e:
            print(f"  FAILED to start server: {e}")
            continue

        try:
            sid = create_session(port)
            print(f"  Session: {sid}")
        except Exception as e:
            print(f"  FAILED to create session: {e}")
            stop_server(proc)
            continue

        arm_results = []
        for round_idx in range(ROUNDS):
            for pidx, prompt in enumerate(PROMPTS):
                label = f"R{round_idx+1} P{pidx+1}"
                start_t = time.monotonic()

                try:
                    result = send_message(port, sid, prompt)
                    elapsed = time.monotonic() - start_t

                    entry = {
                        "experiment_id": "membench-v3-20260524",
                        "model": model,
                        "arm": arm,
                        "round": round_idx + 1,
                        "prompt_idx": pidx + 1,
                        "prompt": prompt,
                        "wall_seconds": round(elapsed, 2),
                        **result,
                        "error": None,
                    }
                except Exception as e:
                    elapsed = time.monotonic() - start_t
                    entry = {
                        "experiment_id": "membench-v3-20260524",
                        "model": model,
                        "arm": arm,
                        "round": round_idx + 1,
                        "prompt_idx": pidx + 1,
                        "prompt": prompt,
                        "wall_seconds": round(elapsed, 2),
                        "total_tokens": 0, "input_tokens": 0, "output_tokens": 0,
                        "cache_read": 0, "cache_write": 0, "reasoning_tokens": 0,
                        "cost": 0, "model_id": "", "provider_id": "",
                        "response": "", "tool_calls": [],
                        "error": str(e)[:200],
                    }

                all_results.append(entry)
                arm_results.append(entry)

                if entry['error']:
                    print(f"    {label}: ERROR {entry['error'][:50]}")
                else:
                    mcp_n = len(entry['tool_calls'])
                    print(f"    {label}: total={entry['total_tokens']:,} in={entry['input_tokens']:,} out={entry['output_tokens']:,} mcp={mcp_n}")

                time.sleep(1.5)

            print(f"  --- Round {round_idx+1} done ---")

        valid = [r for r in arm_results if not r.get('error')]
        if valid:
            avg_total = statistics.mean([r['total_tokens'] for r in valid])
            avg_input = statistics.mean([r['input_tokens'] for r in valid])
            avg_cost = statistics.mean([r['cost'] for r in valid])
            total_mcp = sum(len(r['tool_calls']) for r in valid)
            print(f"  SUMMARY: avg_total={avg_total:,.0f} avg_input={avg_input:,.0f} avg_cost=${avg_cost:.4f} mcp_calls={total_mcp}")

        stop_server(proc)
        time.sleep(5)

        with open(RESULTS_FILE, 'w') as f:
            for r in all_results:
                f.write(json.dumps(r, ensure_ascii=False) + '\n')

with open(RESULTS_FILE, 'w') as f:
    for r in all_results:
        f.write(json.dumps(r, ensure_ascii=False) + '\n')

with open(f"{BASE}/membench-v3-results.json", 'w') as f:
    json.dump(all_results, f, indent=2, ensure_ascii=False)

print(f"\n\nDONE. Total entries: {len(all_results)}")
errors = [r for r in all_results if r.get('error')]
print(f"Errors: {len(errors)}")
