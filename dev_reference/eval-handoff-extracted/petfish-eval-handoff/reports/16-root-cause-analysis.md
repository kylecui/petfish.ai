# Root Cause Analysis: Fish-trail v1.1.0 Performance Overhead

**Date**: 2026-05-22  
**Scope**: Why does fish-trail FULL arm increase cost without improving quality?

---

## 1. Cost Breakdown

### 1.1 Observed P1 Data (Template A, N=10 paired blocks)

| Metric | OFF-clean | FULL | Delta |
|--------|-----------|------|-------|
| API Calls | 55 | 62 | +13.9% (d_z=0.38) |
| Total Tokens | 97,697 | 109,672 | +12.3% (d_z=0.22) |
| Wall Time (s) | 342 | 523 | +52.8% (d_z=0.50) |

### 1.2 Attributed Cost Sources

| Source | Mechanism | Est. Per-Turn Cost | Cacheable? |
|--------|-----------|-------------------|------------|
| Tool schema (31 tools) | Fixed system prompt JSON | ~2K tokens | Yes (cached) |
| topic_detect tool call | LLM decides to call → API round-trip + response parsing | ~4-6K tokens, 2-8s | No (conversation context) |
| get_memory_context tool call | LLM calls → memory text injected into conversation | ~2-4K tokens | No (conversation context) |
| topic_update tool call | After substantial work, state update | ~1-2K tokens periodic | No |

**The ~2K tool schema tokens are negligible (cached). The dominant cost is MCP tool call round-trips putting results into uncached conversation context.**

---

## 2. Architecture Analysis

### 2.1 Current Data Flow

```
User message arrives
  │
  ├─ Plugin hook: system-prompt-rules.ts
  │   └─ Injects agents-rules/*.md into system prompt (CACHED) ✓
  │   └─ Does NOT inject topic state or memory context
  │
  ├─ LLM reads fish-trail.md rule:
  │   "Step 1: Call MCP tool topic_detect"  → 1 API round-trip
  │   "Step 2: Call MCP tool get_memory_context" → 1 API round-trip
  │
  ├─ Results enter conversation context (UNCACHED) ✗
  │
  └─ LLM generates final response
```

### 2.2 Where the Design Split Occurred

The v0.11.0 system-prompt plugin was built to solve a *different* problem:
- v0.11.0 tiered AGENTS.md uses Read tool for on-demand rule loading
- Read tool puts rule content into conversation context (uncached)
- This caused +36.6% token overhead (REPORT.md in outputs/v011-sysprompt-plugin-report/)

The plugin solved this by injecting rules into system prompt via
`experimental.chat.system.transform`. But it only addressed **rule files**,
not **runtime state** (topic status, memory context).

The fish-trail.md agents-rules file instructs the LLM to call MCP tools
for topic state and memory, bypassing the plugin's system-prompt injection pathway.

**Result: Rules are cached, but runtime state still requires uncached tool calls.**

### 2.3 What Should Have Happened

```
User message arrives
  │
  ├─ Plugin hook: system-prompt-context-inject.ts
  │   ├─ Read .petfish/fish-trail/topics/*.json (local file, <1ms)
  │   ├─ Inject topic state into system prompt (CACHED) ✓
  │   ├─ Read topic summaries → inject memory context (CACHED) ✓
  │   └─ Inject agents-rules/*.md (CACHED) ✓
  │
  ├─ LLM has rules + topic state + memory, all in system prompt
  │   No MCP tool calls needed for routine turns
  │
  └─ LLM generates final response
```

---

## 3. `topic_detect` Does NOT Call Remote LLM

### 3.1 Tier 1: Pure Rule Engine

File: `.opencode/skills/fish-trail/mcp/context-state/topic_detector.py`

- Keyword extraction + stopword filtering + bilingual expansion
- Signal phrase matching (switch/fork/merge/archive/reset/bridge)
- Jaccard similarity for topic overlap
- Semantic drift detection via keyword overlap threshold
- **All local CPU, <1ms, no LLM inference**

### 3.2 Tier 2: ONNX Embedding (Optional)

File: `.opencode/skills/fish-trail/mcp/context-state/embeddings.py`

- Model: `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`
- ONNX int8 quantized, 113MB on disk
- Only triggered in "ambiguous zone" (0 < Jaccard relevance < 0.10)
- Local CPU inference, ~30ms with onnxruntime
- **Graceful fallback to Tier 1 when deps unavailable**

### 3.3 Tier 2 Was NOT Active During P1

Evidence:
- `.petfish/fish-trail/config.json` has no `embedding` section
- `onnxruntime` not installed in uv-managed Python environment
- `.petfish/fish-trail/models/` directory does not exist
- v0.7.2 test report confirmed embedding worked with manual setup,
  but config was not persisted across environment changes

**P1 results reflect Tier-1-only performance. The hybrid architecture was designed but never operational in production testing.**

---

## 4. The v0.11.0 "All-in-System-Prompt" Decision Was Correct

### 4.1 Experimental Evidence

From `outputs/v011-sysprompt-plugin-report/REPORT.md`:

| Configuration | Total Tokens | vs v0.10.x | Compactions |
|---------------|-------------|------------|-------------|
| v0.10.x (inline rules) | 586K | — | 2 |
| v0.11.0 (on-demand Read tool) | 1,017K | **+36.6%** | 3 |
| v0.11.0 + all-rules plugin | 475K | **-19.1%** | 1 |

Root cause: Read tool puts content into conversation context (uncached),
accelerating context window growth → more compactions → each compaction costs 50-80K tokens.

**Decision: Put everything you can into system prompt (cached prefix).**
This decision was correct for rules. It should also apply to topic state and memory context.

### 4.2 Why Tool Call Results Are Uncached

MCP tool call results enter the LLM's conversation context as assistant/user
message turns. These are NOT part of the system prompt prefix and therefore
cannot benefit from provider prefix caching. Every token in a tool call result
is billed as fresh input on every subsequent turn.

Plugin-injected system prompt content IS the cached prefix. It's paid once
and cached across all turns in the session.

---

## 5. Implications for the Decoupling Proposal

The `references/petfish_core_runtime_decoupling_and_minimal_evaluation.md`
proposal's core diagnosis is correct: the system is over-coupled and hard
to attribute costs. But the proposed solution (separate MCP servers, minimal
tool sets) addresses the wrong layer.

**The problem is not "31 tools exposed" or "MCP server too big".
The problem is "LLM makes tool calls that put results in conversation context
instead of having the plugin put equivalent information in system prompt."**

The fix is:
1. Extend the existing plugin to inject topic state and memory context
2. Remove mandatory per-turn MCP tool calls from fish-trail.md
3. Reserve MCP tool calls for user-initiated topic management actions only

This is a **configuration/rule change + plugin extension**, not an
architecture rewrite. It can be validated in 1-2 days.
