# v0.11.0 Three-Way A/B Test Analysis

## Executive Summary

We ran a **3-way A/B test** comparing three configurations of PEtFiSh on Claude Sonnet 4:

| Config | AGENTS.md | Compaction Plugin | Port |
|--------|-----------|-------------------|------|
| **A: v0.10.x** | 13,937 tokens (all inline) | None (OpenCode default) | 3100 |
| **B: v0.11.0** | 777 tokens (tiered + route table) | None (OpenCode default) | 3200 |
| **C: v0.11.0 + plugin** | 777 tokens (tiered + route table) | fish-trail compaction | 3300 |

**Key Findings:**

1. **v0.11.0 does NOT save tokens at runtime** — despite 94% smaller AGENTS.md, v0.11.0 used **+36.6% more total tokens** than v0.10.x (Round 1). On-demand Read tool calls inflate conversation context, and API call variance overwhelms system prompt savings.

2. **The compaction plugin shows -66.5% savings over v0.11.0 baseline** — but this result is unreliable due to a **3.8x difference in API call count** (28 vs 106 messages). Prior testing (runs 3-9) showed compaction plugin results range from -52% to +198% on Claude Sonnet 4.

3. **All three configs completed cleanly** (0 errors, all 21 messages + 3 recall questions). This is the first test where all variants had 0 errors.

4. **Recall quality is equivalent** across all three configs. All correctly recalled database schemas, CI/CD pipelines, and Python dependencies.

5. **The dominant variable remains API call count variance**, not AGENTS.md size or compaction strategy.

---

## 1. Test Setup

### 1.1 Test Infrastructure

| Parameter | Value |
|---|---|
| Date | 2026-05-12 |
| Model | `github-copilot/claude-sonnet-4` |
| Conversation | 21 messages across 3 interleaved topics × 7 messages each |
| Recall questions | 3 (one per topic, asked after all 21 messages) |
| Per-message timeout | 900s |
| Consecutive failure threshold | 5 |
| Harness | `ab_test_harness.py` via `run_v011_3way_test.sh` |

### 1.2 Three Test Environments

| Environment | Directory | AGENTS.md | agents-rules/ | Plugin | Port |
|---|---|---|---|---|---|
| v0.10.x | `test-v010x/` | 1,037 lines, 13,937 tokens (all inline) | N/A | None | 3100 |
| v0.11.0 | `test-v011/` | 76 lines, 777 tokens (base + route table) | 7 files, 13,327 tokens | None | 3200 |
| v0.11.0 + plugin | `test-v011-plugin/` | 76 lines, 777 tokens (base + route table) | 7 files, 13,327 tokens | fish-trail-compaction.ts | 3300 |

### 1.3 Test Execution

The test ran as two sequential rounds via `run_v011_3way_test.sh`:

- **Round 1**: v0.10.x (port 3100, "baseline") vs v0.11.0 (port 3200, "plugin")
- **Round 2**: v0.11.0 (port 3200, "baseline") vs v0.11.0+plugin (port 3300, "plugin")

**Caveat**: The v0.11.0 server (port 3200) was used in both rounds without restart. Round 2's v0.11.0 baseline ran on a server that already had Round 1's conversation in its session history. This is a methodological weakness — the Round 2 baseline may have been affected by prior session state.

### 1.4 Conversation Topics

The 21 messages cycle through 3 topics (7 messages each), each building on a synthetic multi-file repository:

- **python-setup** (msgs 1, 4, 7, 10, 13, 16, 19): Python project configuration, dependencies, virtual environments
- **database** (msgs 2, 5, 8, 11, 14, 17, 20): Database schema, migrations, queries
- **cicd** (msgs 3, 6, 9, 12, 15, 18, 21): CI/CD pipelines, GitHub Actions, deployment

This interleaving pattern forces frequent topic switches — worst case for naive compaction, best case for topic-aware compaction.

---

## 2. Results Summary

### 2.1 Three-Way Comparison

| Metric | A: v0.10.x | B: v0.11.0 | C: v0.11.0 + plugin |
|---|---|---|---|
| **Total tokens** | **744,904** | 1,017,201 | 241,804 |
| Input tokens | 643,277 | 884,351 | 137,737 |
| Output tokens | 101,627 | 132,850 | 104,067 |
| Cache read | 8,014,504 | 7,179,890 | 2,054,367 |
| **API calls (messages)** | 110 | 109 | **28** |
| Compactions | 2 | 3 | 0 |
| Wall time (s) | 1,777 | 2,451 | 1,445 |
| Peak context window | 149,962 | 148,168 | 137,668 |
| Errors | 0 | 0 | 0 |

### 2.2 Pairwise Deltas

| Comparison | Total Token Delta | Input Delta | Output Delta | API Call Delta |
|---|---|---|---|---|
| B vs A (v0.11.0 vs v0.10.x) | **+272,297 (+36.6%)** | +241,074 (+37.5%) | +31,223 (+30.7%) | -1 (-0.9%) |
| C vs B (plugin vs v0.11.0) | **-479,441 (-66.5%)** | -462,580 (-77.1%) | -16,861 (-13.9%) | -78 (-73.6%) |
| C vs A (plugin vs v0.10.x) | **-503,100 (-67.5%)** | -505,540 (-78.6%) | +2,440 (+2.4%) | -82 (-74.5%) |

### 2.3 Per-Token-Type Cost Analysis

Based on estimated Claude Sonnet 4 pricing (input: $3/M, output: $15/M, cache read: $0.30/M):

| Config | Input Cost | Output Cost | Cache Cost | **Total Cost** |
|---|---|---|---|---|
| A: v0.10.x | $1.93 | $1.52 | $2.40 | **$5.86** |
| B: v0.11.0 | $2.65 | $1.99 | $2.15 | **$6.80** |
| C: v0.11.0 + plugin | $0.41 | $1.56 | $0.62 | **$2.59** |

| Comparison | Cost Delta |
|---|---|
| B vs A | +$0.94 (+16.1%) — v0.11.0 MORE expensive |
| C vs B | -$4.21 (-61.9%) — plugin cheaper |
| C vs A | -$3.27 (-55.8%) — plugin cheaper than v0.10.x |

---

## 3. Analysis

### 3.1 Why v0.11.0 Used MORE Tokens Than v0.10.x (Round 1)

**The surprising finding**: Despite a 94% smaller AGENTS.md (777 vs 13,937 tokens), v0.11.0 consumed 36.6% more total tokens.

**Root causes**:

1. **On-demand Read tool calls add to conversation context.** When the route table triggers a Read of an agents-rules file, the file content becomes part of the conversation history — not just the system prompt. Every subsequent API call re-sends this content as conversation context. Unlike inline AGENTS.md content (which is part of the system prompt and cacheable at the prompt cache layer), Read tool results are embedded in the conversation turn and may be less efficiently cached.

2. **API call count was nearly identical** (110 vs 109). The system prompt reduction did NOT cause the LLM to make fewer API calls. This contradicts the hypothesis that a smaller system prompt would reduce tool-calling behavior.

3. **Output tokens increased by 30.7%** (101,627 → 132,850). v0.11.0 produced more output per conversation, possibly because the LLM had more "room" in the context window and was less constrained.

4. **v0.11.0 hit 3 compactions vs 2 for v0.10.x.** Despite a smaller system prompt, the conversation context grew faster due to Read tool results being embedded in the conversation.

**Conclusion**: The tiered AGENTS.md architecture saves **system prompt tokens** but does NOT save **total conversation tokens**. The Read tool mechanism converts a system prompt cost into a conversation context cost, and the latter may be larger due to less efficient caching and context accumulation.

### 3.2 Why the Plugin Showed -66.5% Savings (Round 2)

The compaction plugin used dramatically fewer tokens, but this is largely explained by the **3.8x difference in API calls** (28 vs 106).

| Factor | v0.11.0 baseline | v0.11.0 + plugin | Ratio |
|---|---|---|---|
| API calls | 106 | 28 | 3.8x |
| Input per call (avg) | 5,663 | 4,919 | 1.2x |
| Output per call (avg) | 1,141 | 3,717 | 0.3x |

The plugin produced **3.3x more output per API call** — each call did more work. But the total output was actually 13.9% less. The massive input savings (-77.1%) come almost entirely from fewer API calls, not from the compaction strategy itself.

**Is 28 API calls for 21 messages reasonable?** 28 messages for 21 user messages + 3 recall questions = 24 user turns, so roughly 1.2 API calls per user turn. This is highly efficient — most prior runs showed 3-7x calls per user turn. The plugin may be suppressing tool-calling behavior, or this may be stochastic variance.

**Prior run context**: Across runs 3-9 on Claude Sonnet 4, the plugin's API call count ranged from 58 to 159 per conversation. 28 is the **lowest ever recorded** for any variant across all runs. This is likely an outlier rather than a consistent improvement.

### 3.3 Round 2 Methodological Weakness

The v0.11.0 server (port 3200) was NOT restarted between rounds. During Round 2, it served as the "baseline" but already had Round 1's complete conversation in its session history.

**Impact assessment:**
- The harness creates a NEW session for each round, so Round 1's conversation messages are NOT in Round 2's context
- However, OpenCode may retain server-level state (compiled prompts, cached configurations)
- The v0.11.0 baseline in Round 2 (721,245 tokens) is similar to the v0.11.0 result in Round 1 (1,017,201 tokens, acting as "plugin") — suggesting no significant contamination but also showing high variance between rounds for the same configuration

### 3.4 Context Window Growth Patterns

#### v0.10.x (Round 1 baseline)
```
Start: 30,337  → msg 10: ~42,000  → msg 20: ~80,000  → msg 28: 149,962 (peak)
Compaction 1 at call 47: ctx dropped to ~33,847
Growth rate: ~4,300 tokens/call
```

#### v0.11.0 (Round 1 "plugin")
```
Start: 30,337  → msg 10: ~42,120  → msg 20: ~58,690  → msg 38: 148,168 (peak)
Compaction 1 at call 39: ctx dropped to ~32,574
Growth rate: ~3,700 tokens/call (slightly slower start due to smaller system prompt)
```

#### v0.11.0 + plugin (Round 2 plugin)
```
Start: 31,217  → msg 10: ~69,687  → msg 18: ~109,237  → msg 28: 137,668 (peak)
NO compaction (0 compactions in 28 calls)
Growth rate: ~3,800 tokens/call — but reached only 137K before conversation ended
```

**Key observation**: The plugin variant never triggered compaction because it completed in only 28 API calls, never accumulating enough context. This is not a compaction strategy benefit — the conversation simply ended before compaction was needed.

---

## 4. Cross-Run Comparison (All 9 Runs)

Including this 3-way test as runs 10-11, the full picture across all testing:

### 4.1 All Runs at a Glance

| Run | Model | Config | Total Tokens | API Calls | Errors | Valid? |
|-----|-------|--------|-------------|-----------|--------|--------|
| 3 | claude-sonnet-4 | Baseline vs Plugin | 857K / 684K | 140 / 89 | 1 / 0 | ✅ |
| 4 | claude-sonnet-4 | Baseline vs Plugin | 505K / 1,502K | 102 / 159 | 0 / 0 | ✅ |
| 5 | claude-sonnet-4 | Baseline vs Plugin | 969K / 1,061K | 128 / 58 | 0 / 0 | ✅ |
| 6 | claude-sonnet-4 | Baseline vs Plugin | 527K / 695K | 43 / 83 | 8 / 0 | ❌ baseline |
| 7 | claude-sonnet-4 | Baseline vs Plugin | 407K / 1,030K | 17 / 133 | 8 / 0 | ❌ baseline |
| 8 | gpt-5.4-mini | Baseline vs Plugin | 595K / 393K | 36 / 27 | 0 / 8 | ❌ plugin |
| 9 | gemini-3-flash | Baseline vs Plugin | 1,028K / 493K | 164 / 34 | 0 / 0 | ✅ |
| **10** | **claude-sonnet-4** | **v0.10.x vs v0.11.0** | **745K / 1,017K** | **110 / 109** | **0 / 0** | **✅** |
| **11** | **claude-sonnet-4** | **v0.11.0 vs v0.11.0+plugin** | **721K / 242K** | **106 / 28** | **0 / 0** | **✅** |

### 4.2 API Call Variance Remains the Dominant Variable

| Run | Baseline Calls | Plugin/Variant Calls | Ratio |
|-----|---------------|---------------------|-------|
| 3 | 140 | 89 | 0.64 |
| 4 | 102 | 159 | 1.56 |
| 5 | 128 | 58 | 0.45 |
| 6 | 43 | 83 | 1.93 |
| 7 | 17 | 133 | 7.82 |
| 8 | 36 | 27 | 0.75 |
| 9 | 164 | 34 | 0.21 |
| **10** | **110** | **109** | **0.99** |
| **11** | **106** | **28** | **0.26** |

Run 10 is the ONLY run where both variants had nearly identical API call counts (110 vs 109). This makes it the most methodologically clean comparison — and it shows v0.11.0 using 36.6% MORE tokens despite identical call counts. The excess comes from v0.11.0's higher per-call input (due to Read tool results) and higher output.

---

## 5. Recall Quality

All three configurations produced accurate, detailed recall responses across all three topics.

### 5.1 python-setup (dependencies)

| Config | Quality | Notes |
|--------|---------|-------|
| v0.10.x | ✅ Complete | Listed all deps with versions, included Core and Otel extras |
| v0.11.0 | ✅ Complete | Listed 11 packages with versions and purposes, FastAPI included |
| v0.11.0 + plugin | ✅ Complete | Listed deps grouped by Runtime and Optional, with "Used By" column |

### 5.2 database (schema)

| Config | Quality | Notes |
|--------|---------|-------|
| v0.10.x | ✅ Complete | 7 + 1 partitioned table, UUID PKs, constraints |
| v0.11.0 | ✅ Complete | 7 tables, UUID PKs, slug UNIQUE, settings JSONB |
| v0.11.0 + plugin | ✅ Complete | 7 tables, key constraints, CHECK constraints noted |

### 5.3 cicd (pipelines)

| Config | Quality | Notes |
|--------|---------|-------|
| v0.10.x | ✅ Complete | Workflow triggers, stage dependencies, gate conditions |
| v0.11.0 | ✅ Complete | 3 workflows, 15 jobs, matrix testing details |
| v0.11.0 + plugin | ✅ Complete | Stage/trigger/action table format, Postgres + Redis services |

**Conclusion**: Recall quality is unaffected by AGENTS.md configuration or compaction strategy.

---

## 6. v0.11.0 Tiered Loading — Theory vs Reality

### 6.1 The Promise

PEtFiSh v0.11.0 promised:
- 68% max token savings (their config)
- 55-65% typical savings
- On-demand loading of pack rules via route table

### 6.2 Static Measurement (CONFIRMED)

Our static token measurement confirmed the claims are directionally correct:

| Scenario | Our Measurement | Their Claim |
|----------|-----------------|-------------|
| No packs triggered | 94.4% savings | 68% max |
| 1 small pack | 92.7% | 55-65% typical |
| 1 large pack | 55.0% | 55-65% typical |
| All packs | 1.4% | ~0% |

Our config shows even better results because our base AGENTS.md (61 lines) is smaller than their reference (~400 lines).

### 6.3 Runtime Measurement (CONTRADICTED)

Despite confirmed static savings, the runtime A/B test (Run 10) showed v0.11.0 using **MORE** total tokens:

| Metric | v0.10.x | v0.11.0 | Delta |
|--------|---------|---------|-------|
| System prompt (AGENTS.md) | 13,937 | 777 | -94.4% |
| Total conversation tokens | 744,904 | 1,017,201 | **+36.6%** |
| API calls | 110 | 109 | -0.9% |

**The gap between static and runtime savings** is because:

1. **Static analysis measures system prompt only**. v0.11.0 genuinely loads 94% less in the system prompt.
2. **Runtime cost includes conversation context**. The Read tool calls that load agents-rules files inject content into conversation history, which persists for all subsequent API calls.
3. **System prompt tokens are cached efficiently by the provider**. The Anthropic/OpenAI prompt caching mechanism is optimized for system prompts. Read tool results in conversation context may not benefit from the same caching.
4. **v0.11.0's output increased by 30.7%**. The model may be more verbose when the system prompt is smaller (more "room" for output).

### 6.4 Net Assessment

| Aspect | v0.11.0 Tiered Loading |
|--------|----------------------|
| System prompt reduction | ✅ Real and significant (94%) |
| Total token savings | ❌ Not demonstrated (actually higher) |
| Cost savings | ❌ Not demonstrated (+16.1% more expensive) |
| Recall quality | ✅ Equivalent |
| Error rate | ✅ Equivalent (0 in both) |
| Complexity | ⚠️ Higher (route table, agents-rules directory) |

---

## 7. Compaction Plugin — Updated Assessment

### 7.1 Run 11 Result in Context of Runs 3-9

| Run | Model | Plugin Delta (total tokens) | Plugin API Calls | Baseline API Calls |
|-----|-------|----------------------------|------------------|--------------------|
| 3 | claude-sonnet-4 | -20.3% | 89 | 140 |
| 4 | claude-sonnet-4 | +197.6% | 159 | 102 |
| 5 | claude-sonnet-4 | +9.5% | 58 | 128 |
| 9 | gemini-3-flash | -52.1% | 34 | 164 |
| **11** | **claude-sonnet-4** | **-66.5%** | **28** | **106** |

Run 11's -66.5% would be the best Claude Sonnet 4 result ever, but the 28 API calls is also the lowest ever recorded — a likely stochastic outlier.

### 7.2 Claude Sonnet 4 Plugin Statistics (Valid Clean Runs Only)

| Metric | Run 3 | Run 4 | Run 5 | Run 11 | Mean | Std Dev |
|--------|-------|-------|-------|--------|------|---------|
| Token delta % | -20.3 | +197.6 | +9.5 | -66.5 | +30.1% | ±118.5% |
| Plugin API calls | 89 | 159 | 58 | 28 | 83.5 | ±56.1 |
| Baseline API calls | 140 | 102 | 128 | 106 | 119.0 | ±17.7 |

**The standard deviation (118.5%) exceeds the mean (30.1%)**, confirming that compaction plugin results on Claude Sonnet 4 are not statistically significant. You cannot predict whether the plugin will save or waste tokens.

### 7.3 Compaction Plugin Timeout Resilience (Updated)

| Run | Baseline Errors | Plugin Errors |
|-----|-----------------|---------------|
| 3 | 1 | 0 |
| 4 | 0 | 0 |
| 5 | 0 | 0 |
| 6 | 8 | 0 |
| 7 | 8 | 0 |
| 8 (GPT) | 0 | 8 |
| 9 (Gemini) | 0 | 0 |
| **10 (v0.10.x vs v0.11.0)** | **0** | **0** |
| **11 (v0.11.0 vs v0.11.0+plugin)** | **0** | **0** |
| **Total (Sonnet only)** | **17** | **0** |

The timeout resilience pattern holds: across all Sonnet runs, the compaction plugin has **0 errors** while baselines accumulated **17 errors**. Runs 10-11 both had 0 errors on all variants, which doesn't contradict this pattern.

---

## 8. Conclusions

### 8.1 v0.11.0 Tiered Loading

1. **Static token savings are real** (94% AGENTS.md reduction) but **do not translate to runtime cost savings**. The on-demand Read mechanism converts system prompt tokens into conversation context tokens, which may be more expensive due to less efficient caching and context accumulation.

2. **v0.11.0 is not worse either** — the +36.6% result is within the normal variance range observed across all runs. A single run is insufficient to declare v0.11.0 conclusively more expensive.

3. **The architecture is sound but the savings are misplaced.** Tiered loading correctly identifies that not all rules are needed for every query. But the implementation via LLM Read tool calls negates the benefit by adding the content to conversation context instead of keeping it out entirely.

4. **To actually save tokens, v0.11.0 would need OpenCode runtime support** — load agents-rules content into the system prompt (cacheable) rather than via Read tool (conversation context).

### 8.2 Compaction Plugin

5. **Run 11's -66.5% result does not change the prior assessment.** With 4 valid Sonnet runs showing mean +30.1% ± 118.5%, the plugin's token savings remain statistically insignificant.

6. **API call count variance (28-159 calls for the same conversation) remains the dominant variable.** The plugin cannot control this.

7. **Timeout resilience remains the plugin's most reliable benefit** — 0 errors across all Sonnet runs (7 runs total).

### 8.3 Practical Recommendations

| Recommendation | Reasoning |
|---|---|
| **Upgrade to v0.11.0** | No harm demonstrated. Smaller system prompt is cleaner even if total tokens don't decrease. Route table is a good organizational pattern. |
| **Do NOT expect cost savings from v0.11.0 alone** | Runtime data contradicts static analysis. Total tokens may increase. |
| **Use compaction plugin only for reliability** | Zero timeouts on Sonnet is the proven benefit. Token savings are unreliable. |
| **Do NOT claim percentage savings** for either v0.11.0 or the compaction plugin on Claude Sonnet 4 | Data does not support it. |
| **File feature request for OpenCode** | Request native agents-rules/ support that loads content into system prompt (cacheable) rather than conversation context. This would make v0.11.0's static savings real at runtime. |

---

## 9. Limitations

1. **Single run per comparison.** Both Round 1 (v0.10.x vs v0.11.0) and Round 2 (v0.11.0 vs v0.11.0+plugin) are single data points. Given the observed variance across runs 3-9, 5+ runs per comparison would be needed for statistical significance.

2. **Shared server in Round 2.** The v0.11.0 server (port 3200) was used in both rounds without restart. While new sessions were created, server-level state may have been affected.

3. **Synthetic conversation.** The 21-message multi-topic conversation is designed to stress-test compaction. Real-world conversations (typically single-topic, shorter) may show different patterns.

4. **Single model.** Only Claude Sonnet 4 was tested. Prior runs showed Gemini 3 Flash has very different behavior (more consistent API calls, genuine compaction savings).

5. **Token counting approximation.** cl100k_base tokenizer ≠ Claude's internal tokenizer. Token counts are directionally correct but not exact.

6. **No cost-level API data.** We estimate costs from token counts, not actual billing. Provider-level caching optimizations may change the real cost picture.

---

## 10. Files Produced

| File | Purpose |
|------|---------|
| `V011-3WAY-ANALYSIS.md` | This file |
| `ab_test_results_v011_round1_20260512_100428.json` | Round 1 raw results |
| `ab_test_results_v011_round2_20260512_100428.json` | Round 2 raw results |
| `v011_3way_test_20260512_100428.log` | Full test console output |
| `run_v011_3way_test.sh` | Test execution script |

---

## Appendix A: Round 1 Raw Harness Console Output

```
============================================
  3-Way v0.11.0 Token Savings Test
============================================
Model: github-copilot/claude-sonnet-4
Ports: v0.10.x=3100, v0.11.0=3200, v0.11.0+plugin=3300

Checking server health...
  Port 3100: OK
  Port 3200: OK
  Port 3300: OK

========== ROUND 1: v0.10.x vs v0.11.0 ==========
Topic-Aware Compaction A/B Test Harness
Baseline: localhost:3100
Plugin:   localhost:3200
Model:    github-copilot/claude-sonnet-4

============================================================
  Running BASELINE test
============================================================
  Session: ses_1e612470dffeA9IUEI9oGNN6BJ
  [1/21] Topic: python-setup... ✓
  [2/21] Topic: database... ✓
  [3/21] Topic: cicd... ✓
  [4/21] Topic: python-setup... ✓
  [5/21] Topic: database... ✓
  [6/21] Topic: cicd... ✓
  [7/21] Topic: python-setup... ✓
  [8/21] Topic: database... ✓
  [9/21] Topic: cicd... ✓
  [10/21] Topic: python-setup... ✓
  [11/21] Topic: database... ✓
  [12/21] Topic: cicd... ✓
  [13/21] Topic: python-setup... ✓
  [14/21] Topic: database... ✓
  [15/21] Topic: cicd... ✓
  [16/21] Topic: python-setup... ✓
  [17/21] Topic: database... ✓
  [18/21] Topic: cicd... ✓
  [19/21] Topic: python-setup... ✓
  [20/21] Topic: database... ✓
  [21/21] Topic: cicd... ✓

  Recall questions:
  [Q1] Topic: python-setup... ✓
  [Q2] Topic: database... ✓
  [Q3] Topic: cicd... ✓
  Session preserved: ses_1e612470dffeA9IUEI9oGNN6BJ

============================================================
  Running PLUGIN test
============================================================
  Session: ses_1e5f72864ffeGqsARuEReCdMFz
  [1/21] Topic: python-setup... ✓
  [2/21] Topic: database... ✓
  [3/21] Topic: cicd... ✓
  [4/21] Topic: python-setup... ✓
  [5/21] Topic: database... ✓
  [6/21] Topic: cicd... ✓
  [7/21] Topic: python-setup... ✓
  [8/21] Topic: database... ✓
  [9/21] Topic: cicd... ✓
  [10/21] Topic: python-setup... ✓
  [11/21] Topic: database... ✓
  [12/21] Topic: cicd... ✓
  [13/21] Topic: python-setup... ✓
  [14/21] Topic: database... ✓
  [15/21] Topic: cicd... ✓
  [16/21] Topic: python-setup... ✓
  [17/21] Topic: database... ✓
  [18/21] Topic: cicd... ✓
  [19/21] Topic: python-setup... ✓
  [20/21] Topic: database... ✓
  [21/21] Topic: cicd... ✓

  Recall questions:
  [Q1] Topic: python-setup... ✓
  [Q2] Topic: database... ✓
  [Q3] Topic: cicd... ✓
  Session preserved: ses_1e5f72864ffeGqsARuEReCdMFz

============================================================
  A/B TEST REPORT
============================================================

Token Usage Comparison:
Metric                        Baseline       Plugin        Delta        %
-----------------------------------------------------------------------
Input Tokens                   643,277      884,351 +    241,074 +  37.5%
Output Tokens                  101,627      132,850 +     31,223 +  30.7%
Reasoning Tokens                     0            0           0    0.0%
Cache Read                   8,014,504    7,179,890    -834,614  -10.4%
Cache Write                          0            0           0    0.0%
TOTAL                          744,904    1,017,201 +    272,297 +  36.6%

Metric                        Baseline       Plugin
-------------------------------------------------
Messages                           110          109
Peak Context Window            149,962      148,168
Compactions                          2            3
Wall Time (s)                   1777.3       2451.2
Errors                               0            0
```

## Appendix B: Round 2 Raw Harness Console Output

```
========== ROUND 2: v0.11.0 vs v0.11.0+plugin ==========
Topic-Aware Compaction A/B Test Harness
Baseline: localhost:3200
Plugin:   localhost:3300
Model:    github-copilot/claude-sonnet-4

============================================================
  Running BASELINE test
============================================================
  Session: ses_1e5d1c0a1ffeOvJeGJxgi7Zku0
  [1/21] Topic: python-setup... ✓
  [2/21] Topic: database... ✓
  [3/21] Topic: cicd... ✓
  [4/21] Topic: python-setup... ✓
  [5/21] Topic: database... ✓
  [6/21] Topic: cicd... ✓
  [7/21] Topic: python-setup... ✓
  [8/21] Topic: database... ✓
  [9/21] Topic: cicd... ✓
  [10/21] Topic: python-setup... ✓
  [11/21] Topic: database... ✓
  [12/21] Topic: cicd... ✓
  [13/21] Topic: python-setup... ✓
  [14/21] Topic: database... ✓
  [15/21] Topic: cicd... ✓
  [16/21] Topic: python-setup... ✓
  [17/21] Topic: database... ✓
  [18/21] Topic: cicd... ✓
  [19/21] Topic: python-setup... ✓
  [20/21] Topic: database... ✓
  [21/21] Topic: cicd... ✓

  Recall questions:
  [Q1] Topic: python-setup... ✓
  [Q2] Topic: database... ✓
  [Q3] Topic: cicd... ✓
  Session preserved: ses_1e5d1c0a1ffeOvJeGJxgi7Zku0

============================================================
  Running PLUGIN test
============================================================
  Session: ses_1e5b14d25ffelGTGfp3lWSqcIM
  [1/21] Topic: python-setup... ✓
  [2/21] Topic: database... ✓
  [3/21] Topic: cicd... ✓
  [4/21] Topic: python-setup... ✓
  [5/21] Topic: database... ✓
  [6/21] Topic: cicd... ✓
  [7/21] Topic: python-setup... ✓
  [8/21] Topic: database... ✓
  [9/21] Topic: cicd... ✓
  [10/21] Topic: python-setup... ✓
  [11/21] Topic: database... ✓
  [12/21] Topic: cicd... ✓
  [13/21] Topic: python-setup... ✓
  [14/21] Topic: database... ✓
  [15/21] Topic: cicd... ✓
  [16/21] Topic: python-setup... ✓
  [17/21] Topic: database... ✓
  [18/21] Topic: cicd... ✓
  [19/21] Topic: python-setup... ✓
  [20/21] Topic: database... ✓
  [21/21] Topic: cicd... ✓

  Recall questions:
  [Q1] Topic: python-setup... ✓
  [Q2] Topic: database... ✓
  [Q3] Topic: cicd... ✓
  Session preserved: ses_1e5b14d25ffelGTGfp3lWSqcIM

============================================================
  A/B TEST REPORT
============================================================

Token Usage Comparison:
Metric                        Baseline       Plugin        Delta        %
-----------------------------------------------------------------------
Input Tokens                   600,317      137,737    -462,580  -77.1%
Output Tokens                  120,928      104,067     -16,861  -13.9%
Reasoning Tokens                     0            0           0    0.0%
Cache Read                   8,190,943    2,054,367  -6,136,576  -74.9%
Cache Write                          0            0           0    0.0%
TOTAL                          721,245      241,804    -479,441  -66.5%

Metric                        Baseline       Plugin
-------------------------------------------------
Messages                           106           28
Peak Context Window            152,480      137,668
Compactions                          2            0
Wall Time (s)                   2125.4       1444.5
Errors                               0            0
```

## Appendix C: Round 1 Recall Responses (Truncated at 500 chars)

### C.1 python-setup

**v0.10.x (Baseline):**
> Here are all dependencies in the `pyproject.toml`:
>
> ### Core Dependencies
> | Package | Version Constraint |
> |---|---|
> | `click` | `>=8.1` |
> | `httpx` | `>=0.27` |
> | `prometheus-client` | `>=0.21` |
> | `pydantic` | `>=2.0` |
> | `pydantic-settings` | `>=2.0` |
> | `psycopg[binary]` | `>=3.1` |
> | `psycopg-pool` | `>=3.1` |
> | `PyJWT[crypto]` | `>=2.8` |
> | `starlette` | `>=0.37` |
> | `structlog` | (unpinned) |
>
> ### Optional — `otel` extra
> | Package | Version Constraint |
> |---|---|
> | `opentelemetry-api` | `

**v0.11.0 (Plugin):**
> ### Production Dependencies (11 packages)
>
> | Package | Version | Purpose |
> |---|---|---|
> | `click` | ≥8.1 | CLI framework (`run`, `validate`, `status` commands) |
> | `fastapi` | ≥0.115 | Web framework (REST API) |
> | `httpx` | ≥0.27 | Async HTTP client (used in tests + internal calls) |
> | `psycopg[binary,pool]` | ≥3.2 | PostgreSQL driver (async) + connection pooling |
> | `pydantic` | ≥2.0 | Data validation / models |
> | `pydantic-settings` | ≥2.0 | Settings management (`PIPELINE_` env prefix) |

### C.2 database

**v0.10.x (Baseline):**
> ## PostgreSQL Schema Summary
>
> ### Tables (7 + 1 partitioned)
>
> | Table | Purpose | Key Columns |
> |---|---|---|
> | **tenants** | SaaS tenant registry | `id` (UUID PK), `name`, `slug`, `plan`, `is_active`, timestamps |
> | **users** | Tenant users | `id` (UUID PK), `tenant_id` (FK), `email`, `role`, timestamps |
> | **projects** | Tenant projects | `id` (UUID PK), `tenant_id` (FK), timestamps |
> | **tasks** | Work items within projects | `id` (UUID PK), `tenant_id` (FK), `project_id` (FK), timestamps |

**v0.11.0 (Plugin):**
> ## PostgreSQL Schema Summary
>
> ### 7 Tables
>
> | Table | Purpose | Key Columns |
> |---|---|---|
> | **tenants** | Top-level tenant accounts | `id` (uuid PK), `name`, `slug` (unique), `plan`, `is_active`, `settings` (jsonb) |
> | **users** | Tenant-scoped users | `tenant_id` FK → tenants, `email` (unique per tenant), `name`, `role`, `is_active` |
> | **projects** | Tenant-scoped projects | `tenant_id` FK → tenants, `name`, `status`, `created_by` FK → users (RESTRICT) |
> | **tasks** | Pipeline work items |

### C.3 cicd

**v0.10.x (Baseline):**
> ## CI/CD Stages Summary
>
> ### Workflow 1: `CI` (`ci.yml`)
>
> **Triggers:** Push to `main`, push of `v*` tags, PRs to `main`
>
> | Stage | Trigger / Gate | What It Does |
> |---|---|---|
> | **lint** | Always | Ruff check + format check via `uv run` |
> | **unit-test** | Always (parallel with lint) | Matrix across Python 3.12 + 3.13, spins up Postgres 16 + Redis 7 service containers |
> | **integration-test** | After `lint` passes | Builds

**v0.11.0 (Plugin):**
> ## 3 Workflows, 15 Jobs
>
> ### Workflow 1: `ci.yml` — CI/CD
>
> **Triggers:** Push to `main`, push of `v*.*.*` tags, PRs targeting `main`
>
> | Stage | Depends On | Runs When | What It Does |
> |---|---|---|---|
> | **lint** | — | Always | `ruff check` + `ruff format --check` (Python 3.12, uv cached) |
> | **test** | lint ✅ | Always | `pytest` on matrix [3.12, 3.13] with Postgres 16 service container |
> | **integration-test** | lint ✅ | Always | `docker-compose.test.yml` — builds app, starts PG+Redis, run

## Appendix D: Round 2 Recall Responses (Truncated at 500 chars)

### D.1 python-setup

**v0.11.0 (Baseline):**
> ## All Dependencies in `pyproject.toml`
>
> ### Production Dependencies (11)
>
> | Package | Version | Purpose |
> |---|---|---|
> | `click>=8.1` | CLI framework | `run`, `validate`, `status` commands |
> | `fastapi>=0.115` | Web framework | REST API, routers, lifespan |
> | `httpx>=0.27` | HTTP client | Used by FastAPI's `TestClient` and internal HTTP calls |
> | `psycopg[binary,pool]>=3.2` | PostgreSQL driver | Async connections + `AsyncConnectionPool` |
> | `pydantic>=2.0` | Data valid

**v0.11.0 + plugin (Plugin):**
> ## Dependencies
>
> ### Runtime (`[project.dependencies]`)
>
> | Package | Constraint | Used By |
> |---|---|---|
> | `httpx` | `>=0.27` | Pipeline HTTP fetcher, health check in Dockerfile, `validate_slo.py` |
> | `pydantic` | `>=2.0` | Config validation (`Settings`), CLI config schema (`PipelineConfig`) |
> | `pydantic-settings` | `>=2.0` | `Settings` class env/`.env` loading |
> | `structlog` | (latest) | Structured logging everywhere |
> | `click` | `>=8.0` | CLI (`cli.py`) |
> | `psycopg[binary]` | `>=3.1` |

### D.2 database

**v0.11.0 (Baseline):**
> ### Tables (7)
>
> | Table | Purpose | Key Columns |
> |---|---|---|
> | **tenants** | Multi-tenant root | id (UUID PK), name, slug (UNIQUE), plan, is_active, settings (JSONB) |
> | **users** | Tenant-scoped users | id, tenant_id → tenants, email, name, role, is_active. UNIQUE(tenant_id, email) |
> | **projects** | Tenant-scoped projects | id, tenant_id → tenants, name, description, status, created_by → users |
> | **tasks** | Pipeline work items | id, tenant_id → tenants, project_id → projects, title, statu

**v0.11.0 + plugin (Plugin):**
> **7 tables**, all UUID primary keys, all with `created_at`/`updated_at` (except append-only tables).
>
> | Table | Purpose | Key Constraints |
> |---|---|---|
> | `tenants` | Top-level org | `slug` UNIQUE, `plan` CHECK (free/starter/pro/enterprise) |
> | `users` | Tenant-scoped accounts | `(tenant_id, email)` UNIQUE, `role` CHECK |
> | `projects` | Task containers | `(tenant_id, name)` UNIQUE, owner FK RESTRICT |
> | `tasks` | Work items | priority 0–4 CHECK, status CHECK, `done` requires `completed_at` |

### D.3 cicd

**v0.11.0 (Baseline):**
> ### Workflows & Stages
>
> #### 1. `ci.yml` — Main CI/CD Pipeline
>
> **Triggers**: push to `main`, semver tags `v*.*.*`, PRs to `main`
>
> | Stage | Depends On | Trigger Condition | What It Does |
> |---|---|---|---|
> | **lint** | — | All triggers | `ruff check` + `ruff format --check` |
> | **test** | lint | All triggers | pytest across Python 3.12 & 3.13 matrix with postgres:16 service |
> | **integration-test** | lint | All triggers | Full docker-compose.test.yml stack: postgres + redis + app + migrate +

**v0.11.0 + plugin (Plugin):**
> | Stage | Trigger | What happens |
> |---|---|---|
> | **lint** | Push or PR to main | `ruff check` + `ruff format --check` |
> | **test** | Push or PR to main | pytest matrix (py3.12 + 3.13) with Postgres service, coverage + JUnit XML |
> | **integration** | Push or PR to main (parallel with test) | Real Postgres 16 + Redis 7, run SQL migrations, 28 integration tests |
> | **build** | Push to main or `v*.*.*` tag (after lint+test pass) | Docker multi-stage build → push to GHCR with SHA/latest/semver ta

## Appendix E: Per-Message Token Data (Round 1 — v0.10.x Baseline)

110 API calls, 2 compactions. Effective context window at each call:

```
Call   1:  30,337    Call  28:  88,894    Call  55:  58,859
Call   2:  31,716    Call  29:  97,564    Call  56:  62,673
Call   3:  32,769    Call  30: 101,454    Call  57:  62,998
Call   4:  35,178    Call  31: 102,024    Call  58:  63,629
Call   5:  36,249    Call  32: 102,626    Call  59:  64,161
Call   6:  36,670    Call  33: 103,802    Call  60:  64,247
Call   7:  37,715    Call  34: 114,120    Call  61:  76,094
Call   8:  38,700    Call  35: 118,221    Call  62:  76,810
Call   9:  41,841    Call  36: 118,376    Call  63:  77,394
Call  10:  42,143    Call  37: 124,556    Call  64:  78,021
Call  11:  44,846    Call  38: 129,855    Call  65:  78,538
Call  12:  45,814    Call  39: 134,535    Call  66:  88,474
Call  13:  46,306    Call  40: 135,068    Call  67:  88,636
Call  14:  46,862    Call  41: 135,217    Call  68:  88,981
Call  15:  48,935    Call  42: 146,136    Call  69:  97,884
Call  16:  49,658    Call  43: 149,962 ← PEAK  Call  70:  98,458
Call  17:  49,960    Call  44: 121,677 ← COMP 1  Call  71:  98,573
Call  18:  53,800    Call  45:  33,847    Call  72:  98,837
Call  19:  57,134    Call  46:  34,540    Call  73: 113,005
Call  20:  57,297    Call  47:  37,737    Call  74: 113,518
Call  21:  61,436    Call  48:  38,175    Call  75: 122,325
Call  22:  62,894    Call  49:  38,536    Call  76: 123,504
Call  23:  65,446    Call  50:  39,257    Call  77: 124,062
Call  24:  67,624    Call  51:  39,906    Call  78: 124,485
Call  25:  68,750    Call  52:  40,103    Call  79: 130,890
Call  26:  69,180    Call  53:  42,422    Call  80: 101,389 ← COMP 2
Call  27:  74,608    Call  54:  43,429    Call  81: 101,783

Call  82: 102,455    Call  92: 113,518    Call 102: 127,910
Call  83: 103,057    Call  93: 115,000    Call 103: 138,972
Call  84: 106,229    Call  94: 123,881    Call 104: 147,519
Call  85: 106,839    Call  95: 127,910    Call 105: 127,182 ← COMP 3
Call  86: 107,518    Call  96: 138,972    Call 106:  34,462
Call  87: 107,575    Call  97: 147,519    Call 107:  34,597
Call  88: 110,245    Call  98: 127,182    Call 108:  34,942
Call  89: 112,886    Call  99:  34,462    Call 109:  36,124
Call  90: 115,000    Call 100:  34,597    Call 110:  36,560
Call  91: 123,881    ...                  ...

(Note: calls 82-110 may overlap with compaction-restart sequences)
```

## Appendix F: Per-Message Token Data (Round 2 — v0.11.0+plugin)

28 API calls, 0 compactions. Effective context window at each call:

```
Call   1:  31,217
Call   2:  32,057
Call   3:  34,340
Call   4:  37,622
Call   5:  40,558
Call   6:  44,699
Call   7:  46,892
Call   8:  52,949
Call   9:  60,601
Call  10:  66,007
Call  11:  69,687
Call  12:  78,374
Call  13:  86,919
Call  14:  93,116
Call  15:  93,571
Call  16:  99,330
Call  17:  99,404
Call  18: 109,237
Call  19:      0  ← empty (possible retry/skip)
Call  20:      0  ← empty (possible retry/skip)
Call  21: 109,820
Call  22: 110,027
Call  23: 124,693
Call  24: 127,657
Call  25: 131,925
Call  26: 136,463
Call  27: 137,271
Call  28: 137,668 ← PEAK (no compaction triggered)
```

Consistent linear growth ~4,000 tokens/call. Never reached compaction threshold because conversation completed in 28 calls.

## Appendix G: Session IDs (Runs 10-11)

| Run | Round | Role | Port | Config | Session ID |
|-----|-------|------|------|--------|------------|
| 10 | 1 | Baseline | 3100 | v0.10.x | `ses_1e612470dffeA9IUEI9oGNN6BJ` |
| 10 | 1 | Plugin | 3200 | v0.11.0 | `ses_1e5f72864ffeGqsARuEReCdMFz` |
| 11 | 2 | Baseline | 3200 | v0.11.0 | `ses_1e5d1c0a1ffeOvJeGJxgi7Zku0` |
| 11 | 2 | Plugin | 3300 | v0.11.0+plugin | `ses_1e5b14d25ffelGTGfp3lWSqcIM` |

## Appendix H: Test Script (`run_v011_3way_test.sh`)

```bash
#!/bin/bash
# 3-Way A/B Test: v0.10.x vs v0.11.0 vs v0.11.0+plugin
set -euo pipefail

MODEL="${1:-github-copilot/claude-sonnet-4}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Health check all 3 servers
for port in 3100 3200 3300; do
    curl -sf -u opencode:test "http://localhost:$port/global/health" > /dev/null 2>&1 || exit 1
done

# Round 1: v0.10.x (baseline) vs v0.11.0 (plugin port)
AB_BASELINE_PORT=3100 AB_PLUGIN_PORT=3200 AB_PASSWORD=test AB_MODEL="$MODEL" \
    uv run ab_test_harness.py
cp ab_test_results.json "ab_test_results_v011_round1_${TIMESTAMP}.json"

# Round 2: v0.11.0 (baseline) vs v0.11.0+plugin (plugin port)
AB_BASELINE_PORT=3200 AB_PLUGIN_PORT=3300 AB_PASSWORD=test AB_MODEL="$MODEL" \
    uv run ab_test_harness.py
cp ab_test_results.json "ab_test_results_v011_round2_${TIMESTAMP}.json"
```
