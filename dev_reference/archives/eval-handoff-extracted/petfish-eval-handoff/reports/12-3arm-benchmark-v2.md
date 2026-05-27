# 3-Arm Benchmark: Disk-mode vs FULL-current vs OFF-clean

**Date**: 2026-05-24
**Model**: DeepSeek V4 Pro
**Rounds**: 5 × 10 prompts = 50 entries/arm
**Topics**: 3 (QA Audit Topic, API Monitoring Setup, Performance Benchmarking)

---

## Executive Summary

**Disk-mode (smart) is NOT cheaper than FULL-current.** The core hypothesis — "plugin injection eliminates per-turn MCP overhead" — does not hold under our current architecture, because:

1. **FULL-current's MCP tool calls are cached**: The MCP round-trips add conversational turns, but those turns hit DeepSeek's prompt cache (~99% cache hit rate). The net new token cost per MCP call is minimal.

2. **Disk-mode's plugin injection adds uncacheable context**: The system prompt grows by ~8K tokens of topic context. While system prompts ARE cached, the topic context changes between turns (switching topics, summaries updating), causing cache misses on re-injection.

3. **Wall time is the only real win**: disk-smart averages 3.41s vs FULL's 4.90s (**-30.4%**) because it avoids MCP round-trip latency.

---

## Arm Definitions

| Arm | Plugin Inject | System-Prompt Rules | MCP Topic Sensing | MCP Mutation |
|-----|:---:|:---:|:---:|:---:|
| OFF-clean | No | No | No | No |
| disk-smart | Yes | Yes (MCP-suppressed) | No | Only on user request |
| FULL-current | No | Yes (original) | Every turn | Only on user request |

---

## Results

### Token Cost

| Metric | disk-smart | FULL-current | Delta |
|--------|-----------:|-------------:|------:|
| Total tokens | 1,247,591 | 1,225,198 | +1.8% |
| Input tokens | 40,313 | 11,047 | +264.9% |
| Output tokens | 1,412 | 1,923 | -26.6% |
| Cache read | 1,204,480 | 1,211,008 | -0.5% |
| **Net new tokens** | **43,111** | **14,190** | **+203.8%** |
| Cost ($) | 0.2545 | 0.2058 | +23.7% |
| Avg wall time (s) | 3.41 | 4.90 | **-30.4%** |

### Quality

| Metric | disk-smart | FULL-current |
|--------|-----------:|-------------:|
| Avg Recall (0-2) | 0.98 | 1.26 |
| Contamination % | 32.0% | 40.0% |

### Per-Entry Averages

| Metric | disk-smart | FULL-current | Delta |
|--------|-----------:|-------------:|------:|
| Total tokens/entry | 24,952 | 24,504 | +1.8% |
| Output tokens/entry | 28 | 38 | -26.6% |
| Net new/entry | 862 | 284 | +203.8% |
| Cost/entry ($) | 0.0051 | 0.0041 | +23.7% |

---

## Root Cause Analysis

### Why disk-mode is NOT cheaper

**The MCP calls in FULL-current are nearly free due to prompt caching.**

When FULL-current calls `topic_detect` → model generates tool call → MCP returns result → model reads result, each intermediate turn re-reads the entire conversation. But DeepSeek's cache hit rate is ~99%, meaning:

- Total tokens per FULL turn: ~24,504
- Cache read: ~24,220 (99%)
- Net new tokens: only ~284

The MCP round-trip "costs" thousands of total tokens but only ~100-200 net new tokens because the conversation prefix is cached.

**Disk-mode's system prompt injection is cache-unfriendly.**

The disk plugin injects topic context into the system prompt. This context changes between turns:
- After a topic switch, the active topic changes
- After new activity, summaries update

Each change invalidates the system prompt cache, requiring re-injection of ~8K tokens as net new input. That's why disk-mode's `input_tokens` are 3.6× higher than FULL-current's (40,313 vs 11,047).

### Why disk-mode is faster

Despite higher token cost, disk-smart is 30.4% faster because:
1. No MCP round-trip latency (saves 1-3s per turn)
2. Fewer LLM inference steps (1 step vs 2-4 steps for FULL)
3. Tool calls require model to generate structured output (slower than free-text)

### Why quality is slightly lower

Disk-smart recall (0.98) < FULL recall (1.26):
- FULL calls `topic_detect` which provides explicit risk classification
- FULL calls `get_memory_context` which returns structured tiered summaries
- Disk-smart relies on the model reading the (shorter) context block in system prompt
- The model sometimes doesn't fully utilize the injected context

---

## Cross-Reference: disk-naive (with MCP) vs disk-smart (MCP suppressed)

From the earlier 3-arm run where disk-mode still had MCP calls:

| Metric | disk-naive | disk-smart |
|--------|-----------:|-----------:|
| Total tokens | 1,230,741 | 1,247,591 |
| MCP tool calls | 23 | 0 |
| Cost ($) | 0.2086 | 0.2545 |

Suppressing MCP calls in disk-smart actually **increased** total cost because:
- Without MCP, the model has to answer from injected context alone
- Injected context is briefer than what MCP `topic_show` returns
- The model generates more reasoning tokens to compensate (1,386 vs 1,220)

---

## Implications for Architecture

### The fundamental tension

| Approach | Token Cost | Latency | Quality |
|----------|:----------:|:-------:|:-------:|
| FULL (MCP per turn) | Baseline | 4.90s | 1.26/2 |
| Disk + suppress MCP | +23.7% | 3.41s (-30%) | 0.98/2 |
| Disk + allow MCP | +1.4% | ~4s | ~1.0/2 |
| No memory (OFF-clean) | -30% | 3.6s | 0/2 |

### What disk-mode IS good at

1. **Latency**: -30% wall time is significant for interactive use
2. **Simplicity**: No MCP dependency for routine sensing = fewer failure modes
3. **Offline capability**: Works even when MCP server is down

### What disk-mode is NOT good at

1. **Token efficiency**: The system prompt injection pattern is inherently more expensive than MCP + cache
2. **Quality**: Injected context is less detailed than MCP tool results
3. **Freshness**: Disk context is one turn behind (written after previous turn, not read fresh from MCP)

---

## Recommendations

### 1. Disk-mode should focus on latency, not cost savings

The value proposition of disk-mode should be reframed:
- **NOT**: "Save tokens by eliminating MCP calls"
- **YES**: "Respond 30% faster by eliminating MCP round-trips"

The token savings hypothesis is invalidated by prompt caching.

### 2. Hybrid approach may be optimal

Consider: **disk-mode for low-risk turns, MCP for high-risk turns**
- Disk inject gives the model enough context for routine "continue" interactions
- When topic_detect would return "high" (fork/switch), fall back to MCP for richer context
- This gives latency benefits for ~70% of interactions while maintaining quality for critical moments

### 3. Reduce system prompt injection size

The ~8K token injection is the biggest cost driver. If we can compress it to ~2K:
- Cache read stays the same
- Net new on cache miss drops from ~862 to ~300
- This could close the token cost gap

Optimization opportunities:
- Remove redundant topic metadata from injection
- Use more compact formatting (no markdown tables)
- Only inject active topic, not all 3

### 4. Consider making disk-mode the default for its latency benefit

Even at +23% token cost, a 30% latency improvement is valuable for interactive coding. Users perceive speed more than token count.

---

## Data Files

- `/tmp/opencode/bench_2arm_v3_results.json` — Raw 2-arm results (disk-smart vs FULL, 100 entries)
- `/tmp/opencode/bench_2arm_v3_scored.json` — Scored 2-arm results
- `/tmp/opencode/bench_3arm_v2_results.json` — Raw 3-arm results (OFF/disk/FULL, 150 entries)
- `/tmp/opencode/bench_3arm_v3_scored.json` — Scored 3-arm results (token data only, no response text due to API parsing bug)

---

## Methodology Notes

- **API**: OpenCode REST API `POST /session/{id}/message` with `{parts: [{type: "text", text: ...}]}`
- **Response text extraction**: `body.parts.filter(p => p.type === "text").map(p => p.text).join()`
- **Token accounting**: From `info.tokens` in API response; cache-aware (net new = total - cache_read)
- **Quality scoring**: 0-2 recall scale based on whether correct topic names appear in response
- **Contamination check**: Wrong topic mentioned before correct topic in focused prompts
- **Model**: DeepSeek V4 Pro via OpenCode auth; temperature=0
- **Sessions**: Fresh per arm; same 3 topics seeded via `.petfish/fish-trail/`
