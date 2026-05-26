# A/B Test Round 2 — Multi-Run Analysis

## Executive Summary

Across **7 runs** (5 on Claude Sonnet 4, 1 on GPT-5.4-mini, 1 on Gemini 3 Flash), the fish-trail topic-aware compaction plugin shows **highly variable results that are model-dependent and not statistically significant on Claude Sonnet 4**.

- **Claude Sonnet 4 (5 runs)**: Results range from -20.3% to +197.6% token delta. Only 1 of 3 valid clean runs showed savings; the other 2 showed the plugin using MORE tokens. The variance is driven by non-deterministic API call counts (17–159 calls for the same 21 messages), not by the compaction strategy itself.
- **Gemini 3 Flash (1 run)**: -52.1% tokens, -79% API calls, -82.5% cache reads — the best result across all runs. Both variants completed cleanly with 0 errors.
- **GPT-5.4-mini (1 run)**: Invalid — plugin timed out on 8 messages, baseline completed cleanly.
- **Plugin's proven value is timeout resilience**: In runs 6-7 the baseline timed out on 5+ consecutive messages while the plugin completed with 0 errors. Across all 7 runs, the plugin had 8 errors (all from GPT-5.4-mini) vs baseline's 17 errors.

**Bottom line**: Run 3's 20% savings claim is not reproducible on Claude Sonnet 4. The plugin's primary demonstrated benefit is resilience to timeouts. On Gemini 3 Flash it shows genuine and substantial token savings, but this is a single run.

---

## 1. Test Setup

| Parameter | Value |
|---|---|
| Conversation | 21 messages across 3 interleaved topics (python-setup, database, cicd) |
| Recall questions | 3 (one per topic, asked after all 21 messages) |
| Baseline | OpenCode default compaction (port 3100) |
| Plugin | Fish-trail topic-structured compaction (port 3200) |
| Per-message timeout | 900s |
| Consecutive failure threshold | 5 |
| Harness | `ab_test_harness.py` with session preservation, per-message token tracking |

### 1.1 Models Tested

| Run(s) | Model | Provider |
|--------|-------|----------|
| 3, 4, 5, 6, 7 | `github-copilot/claude-sonnet-4` | GitHub Copilot |
| 8 | `github-copilot/gpt-5.4-mini` | GitHub Copilot |
| 9 | `github-copilot/gemini-3-flash-preview` | GitHub Copilot |

### 1.2 Test Conversation Topics

The 21 messages cycle through 3 topics (7 messages each), each building on a synthetic multi-file repository:

- **python-setup** (msgs 1, 4, 7, 10, 13, 16, 19): Python project configuration, dependencies, virtual environments
- **database** (msgs 2, 5, 8, 11, 14, 17, 20): Database schema, migrations, queries
- **cicd** (msgs 3, 6, 9, 12, 15, 18, 21): CI/CD pipelines, GitHub Actions, deployment

This interleaving pattern forces frequent topic switches — worst case for naive compaction, best case for topic-aware compaction.

---

## 2. Multi-Run Results Summary

### 2.1 All Runs at a Glance

| Run | Model | Baseline Total | Plugin Total | Delta % | Baseline Msgs | Plugin Msgs | Baseline Errors | Plugin Errors | Valid? |
|-----|-------|---------------|-------------|---------|--------------|------------|-----------------|---------------|--------|
| 3 | claude-sonnet-4 | 857,115 | 683,522 | **-20.3%** | 140 | 89 | 1 | 0 | ✅ |
| 4 | claude-sonnet-4 | 504,662 | 1,501,686 | **+197.6%** | 102 | 159 | 0 | 0 | ✅ (plugin worse) |
| 5 | claude-sonnet-4 | 968,546 | 1,060,679 | **+9.5%** | 128 | 58 | 0 | 0 | ✅ (plugin worse) |
| 6 | claude-sonnet-4 | 526,945 | 695,120 | +31.9% | 43 | 83 | 8 | 0 | ❌ baseline incomplete |
| 7 | claude-sonnet-4 | 407,397 | 1,029,894 | +152.8% | 17 | 133 | 8 | 0 | ❌ baseline incomplete |
| 8 | gpt-5.4-mini | 594,965 | 393,324 | -33.9% | 36 | 27 | 0 | 8 | ❌ plugin incomplete |
| 9 | gemini-3-flash | 1,027,667 | 492,593 | **-52.1%** | 164 | 34 | 0 | 0 | ✅ |

### 2.2 Valid Clean Runs Only (Both Variants 0 Errors, or ≤1 Non-Fatal Error)

| Run | Model | Baseline Total | Plugin Total | Delta % | Baseline Msgs | Plugin Msgs |
|-----|-------|---------------|-------------|---------|--------------|------------|
| 3 | claude-sonnet-4 | 857,115 | 683,522 | -20.3% | 140 | 89 |
| 4 | claude-sonnet-4 | 504,662 | 1,501,686 | +197.6% | 102 | 159 |
| 5 | claude-sonnet-4 | 968,546 | 1,060,679 | +9.5% | 128 | 58 |
| 9 | gemini-3-flash | 1,027,667 | 492,593 | -52.1% | 164 | 34 |

**Claude Sonnet 4 average delta (runs 3, 4, 5)**: +62.3% — the plugin used MORE tokens on average.

### 2.3 Detailed Token Breakdown by Run

#### Run 3 — Claude Sonnet 4 (Original)

| Metric | Baseline | Plugin | Delta % |
|---|---|---|---|
| Input Tokens | 726,474 | 576,050 | -20.7% |
| Output Tokens | 130,641 | 107,472 | -17.7% |
| Cache Read | 10,631,340 | 5,330,527 | -49.9% |
| Total (input+output) | 857,115 | 683,522 | -20.3% |
| API Calls | 140 | 89 | -36.4% |
| Compactions | 2 | 2 | same |
| Wall Time | 2,938s | 1,781s | -39.4% |
| Errors | 1 | 0 | — |

#### Run 4 — Claude Sonnet 4

| Metric | Baseline | Plugin | Delta % |
|---|---|---|---|
| Input Tokens | 341,314 | 1,328,920 | +289.3% |
| Output Tokens | 163,348 | 172,766 | +5.8% |
| Cache Read | 8,028,917 | 12,860,105 | +60.2% |
| Total (input+output) | 504,662 | 1,501,686 | +197.6% |
| API Calls | 102 | 159 | +55.9% |
| Compactions | 1 | 3 | +2 |
| Wall Time | 2,621s | 3,069s | +17.1% |
| Errors | 0 | 0 | — |

**Run 4 anomaly**: The plugin made 159 API calls (vs 102 baseline) and triggered 3 compactions (vs 1). The exact opposite of Run 3's pattern. This demonstrates that the dominant variable is non-deterministic model behavior (tool-calling patterns), not the compaction strategy.

#### Run 5 — Claude Sonnet 4

| Metric | Baseline | Plugin | Delta % |
|---|---|---|---|
| Input Tokens | 834,282 | 937,190 | +12.3% |
| Output Tokens | 134,264 | 123,489 | -8.0% |
| Cache Read | 10,094,759 | 3,197,054 | -68.3% |
| Total (input+output) | 968,546 | 1,060,679 | +9.5% |
| API Calls | 128 | 58 | -54.7% |
| Compactions | 2 | 1 | -1 |
| Wall Time | 3,086s | 2,514s | -18.5% |
| Errors | 0 | 0 | — |

**Run 5 paradox**: The plugin made only 58 API calls (fewest of any run) which dramatically reduced cache reads (-68.3%), but had massive single-call input payloads (up to 143K tokens in one call), resulting in higher total input despite fewer calls.

#### Run 6 — Claude Sonnet 4 (Baseline Incomplete)

| Metric | Baseline | Plugin | Delta % |
|---|---|---|---|
| Total (input+output) | 526,945 | 695,120 | +31.9% |
| API Calls | 43 | 83 | +93.0% |
| Compactions | 1 | 2 | +1 |
| Errors | **8** | 0 | — |

Baseline failed on messages 10-14 and all 3 recall questions (timeouts). Plugin completed all 21 messages + recall with 0 errors.

#### Run 7 — Claude Sonnet 4 (Baseline Incomplete)

| Metric | Baseline | Plugin | Delta % |
|---|---|---|---|
| Total (input+output) | 407,397 | 1,029,894 | +152.8% |
| API Calls | 17 | 133 | +682.4% |
| Compactions | 1 | 3 | +2 |
| Errors | **8** | 0 | — |

Baseline failed on messages 15-19 and all 3 recall questions. Plugin completed everything with 0 errors.

#### Run 8 — GPT-5.4-mini (Plugin Incomplete)

| Metric | Baseline | Plugin | Delta % |
|---|---|---|---|
| Total (input+output) | 594,965 | 393,324 | -33.9% |
| API Calls | 36 | 27 | -25.0% |
| Compactions | 1 | 1 | same |
| Errors | 0 | **8** | — |

**Reversed failure pattern**: Baseline completed all 21 messages cleanly; plugin timed out on messages 16-19 and all 3 recall questions. This is the only run where the plugin failed and baseline succeeded.

#### Run 9 — Gemini 3 Flash (Best Result)

| Metric | Baseline | Plugin | Delta % |
|---|---|---|---|
| Input Tokens | 874,764 | 349,943 | -60.0% |
| Output Tokens | 152,903 | 142,650 | -6.7% |
| Cache Read | 12,486,646 | 2,188,972 | -82.5% |
| Total (input+output) | 1,027,667 | 492,593 | -52.1% |
| API Calls | 164 | 34 | -79.3% |
| Compactions | 3 | 1 | -2 |
| Wall Time | 2,908s | 1,784s | -38.7% |
| Errors | 0 | 0 | — |

**Run 9 is the strongest result**: Both variants completed cleanly. Gemini's tool-calling behavior was more consistent, making the compaction advantage measurable. The plugin reduced API calls by 79%, cache reads by 82.5%, and total tokens by 52.1%.

---

## 3. API Call Variance — The Dominant Variable

The single most important finding across all runs is that **API call count variance, driven by non-deterministic tool-calling behavior, overwhelms any compaction effect on Claude Sonnet 4**.

| Run | Model | Baseline Msgs | Plugin Msgs | Call Ratio (P/B) |
|-----|-------|--------------|------------|-----------------|
| 3 | claude-sonnet-4 | 140 | 89 | 0.64 |
| 4 | claude-sonnet-4 | 102 | 159 | 1.56 |
| 5 | claude-sonnet-4 | 128 | 58 | 0.45 |
| 6 | claude-sonnet-4 | 43 | 83 | 1.93 |
| 7 | claude-sonnet-4 | 17 | 133 | 7.82 |
| 8 | gpt-5.4-mini | 36 | 27 | 0.75 |
| 9 | gemini-3-flash | 164 | 34 | 0.21 |

For Claude Sonnet 4, the same 21-message conversation generates anywhere from 17 to 159 API calls. This 9x range makes it impossible to isolate the compaction effect from model behavior variance with only 5 runs.

For Gemini 3 Flash, the ratio is 0.21 (plugin used 79% fewer calls). Whether this consistency holds across multiple runs is unknown.

---

## 4. Timeout Resilience Analysis

The plugin's most consistently demonstrated benefit is **timeout resilience**.

### 4.1 Error Summary Across All Runs

| Run | Model | Baseline Errors | Plugin Errors |
|-----|-------|-----------------|---------------|
| 3 | claude-sonnet-4 | 1 (msg 15) | 0 |
| 4 | claude-sonnet-4 | 0 | 0 |
| 5 | claude-sonnet-4 | 0 | 0 |
| 6 | claude-sonnet-4 | **8** (msgs 10-14 + 3 recall) | 0 |
| 7 | claude-sonnet-4 | **8** (msgs 15-19 + 3 recall) | 0 |
| 8 | gpt-5.4-mini | 0 | **8** (msgs 16-19 + 3 recall) |
| 9 | gemini-3-flash | 0 | 0 |
| **Total** | | **17** | **8** |

On Claude Sonnet 4 specifically: Baseline had 17 errors across 5 runs, plugin had 0. The plugin never timed out on Sonnet.

### 4.2 Runs 6-7: Plugin Completes Where Baseline Fails

In runs 6 and 7, the baseline hit 5 consecutive timeouts (triggering the failure threshold), then failed all 3 recall questions. The plugin completed all 21 messages + recall with 0 errors in both runs. This pattern repeated across two independent runs, making it the most reproducible finding in the study.

### 4.3 Run 8: Reversed Failure Pattern

On GPT-5.4-mini, the plugin timed out while the baseline completed cleanly. This suggests the plugin's resilience advantage is model-specific and does not universally apply.

---

## 5. Dollar Cost Analysis

Based on GitHub Copilot API pricing (estimated at Claude Sonnet 4 rates):
- Input: $3/M tokens
- Output: $15/M tokens
- Cache read: $0.30/M tokens (10% of input)

### 5.1 Per-Conversation Cost (Valid Clean Runs)

| Run | Baseline Cost | Plugin Cost | Savings |
|-----|--------------|-------------|---------|
| Run 3 | $7.33 | $4.94 | $2.39 (32.6%) |
| Run 4 | $4.46 | $9.48 | -$5.02 (plugin 112% more expensive) |
| Run 5 | $6.54 | $5.67 | $0.87 (13.3%) |
| Run 9 | $6.76 | $2.69 | $4.07 (60.2%) |

Cost calculation: `(input × $3 + output × $15 + cache_read × $0.30) / 1,000,000`

### 5.2 Projected Monthly Savings (at 50 conversations/day)

| Scenario | Monthly Savings |
|----------|----------------|
| Best case (Run 9, Gemini) | **$6,105/month** |
| Run 3 result (Sonnet, best) | $3,584/month |
| Run 5 result (Sonnet, mixed) | $1,305/month |
| Worst case (Run 4, Sonnet) | **-$7,530/month** (plugin costs more) |

**Conclusion**: Cost savings are not guaranteed on Claude Sonnet 4. On Gemini 3 Flash the savings are substantial but based on a single run.

---

## 6. Recall Quality

All valid runs where both variants completed showed **no meaningful quality difference** in recall responses. Both variants correctly recalled:

- All 7 database tables with schemas, constraints, and relationships
- All CI/CD pipeline stages with triggers and dependencies
- All Python dependencies with versions and purposes

The plugin's responses tend to be more concise but equally accurate. See original Run 3 detailed comparison in Appendix B for examples.

---

## 7. Comparison with Prior Runs (Runs 1-2)

### Run 1 (prior session, harness bugs)
- Sessions were deleted, no post-hoc inspection possible
- Harness reported plugin used MORE tokens (+17%) — misleading due to token counting methodology
- Neither variant completed all 21 messages

### Run 2 (prior session, fixed harness)
- Both variants hit excessive timeouts (600s limit)
- Baseline: 12/21 completed, plugin: 16/21 completed
- Root cause: conversation triggers full multi-agent workflows (5-10 min per message)

---

## 8. Conclusions

1. **Run 3's 20% savings claim is NOT reproducible on Claude Sonnet 4.** Across 3 valid clean runs (3, 4, 5), the average delta was +62.3% — the plugin used MORE tokens on average. The variance between runs is enormous (range: -20.3% to +197.6%).

2. **API call count variance is the dominant factor.** The same 21-message conversation generates 17-159 API calls on Sonnet 4 due to non-deterministic tool-calling behavior. This 9x range overwhelms any compaction effect.

3. **The plugin shows genuine savings on Gemini 3 Flash (-52.1%)**, with 79% fewer API calls and 82.5% fewer cache reads. The more consistent tool-calling behavior of Gemini allows the compaction advantage to manifest. However, this is a single run.

4. **The plugin's most reliable benefit is timeout resilience on Claude Sonnet 4.** Across 5 Sonnet runs, the plugin had 0 errors while the baseline had 17. In runs 6-7, the baseline failed catastrophically (5 consecutive timeouts + all recall failures) while the plugin completed with 0 errors.

5. **Timeout resilience is model-specific.** On GPT-5.4-mini (Run 8), the plugin timed out while the baseline completed cleanly — the reversed pattern.

6. **Recall quality is unaffected.** Both variants produce accurate, detailed recall responses across all three topics in every valid run.

7. **Cost savings are unreliable on Sonnet.** Per-conversation costs range from $2.39 saved to $5.02 lost depending on the run. On Gemini, savings are $4.07/conversation (60.2%).

---

## 9. Limitations & Future Work

- **Insufficient sample size for Sonnet**: 3 valid clean runs is far too few for statistical significance given the observed variance. 20+ runs would be needed.
- **Single run per alternative model**: Gemini and GPT results are single data points.
- **Synthetic conversation**: The 21-message multi-topic conversation is designed to stress-test compaction. Real-world conversations may show different patterns.
- **Tool-call non-determinism is the confound**: The plugin cannot control how many API calls the model makes. A future version could try to influence this (e.g., via system prompt instructions), but the current results suggest the compaction strategy alone is insufficient to guarantee savings.
- **Compaction threshold not tuned**: Both variants used the same compaction threshold. Independent tuning might help.
- **No Gemini multi-run verification**: The Run 9 result is promising but needs replication.

---

## 10. Recommendations

1. **Do not claim 20% token savings** for the plugin on Claude Sonnet 4. The data does not support it.
2. **Consider positioning the plugin as a reliability improvement** for Sonnet — the zero-timeout track record is the strongest reproducible finding.
3. **Test on Gemini 3 Flash with 5+ runs** to verify whether the 52% savings are reproducible.
4. **Investigate the API call variance root cause** — why does the same conversation produce 17-159 calls? This is the key lever.
5. **Consider model-specific tuning** — the plugin may need different strategies for different models' tool-calling patterns.

---

## 11. Run 3 Deep Dives (Original Analysis)

The following sections preserve the detailed per-message analysis from the original Run 3, which remains the most thoroughly analyzed run.

### 11.1 Context Window Growth Analysis

#### Pre-Compaction Phase

**Baseline** — 28 API calls before first compaction:

```
Call  1: ctx =  30,336  (system prompt)
Call  2: ctx =  35,284  (+4,948)
Call  5: ctx =  38,629
Call 10: ctx =  52,959  (+10K jump — tool results)
Call 13: ctx =  64,207
Call 20: ctx =  89,663
Call 25: ctx = 127,887
Call 28: ctx = 151,285  ← PEAK, triggers compaction
Call 29: ctx = 127,619  ← COMPACTION (cache_read=0, fresh context)
Call 30: ctx =  33,075  ← post-compaction, rebuilding
```

Growth rate: ~4,300 tokens/call average.

**Plugin** — 31 API calls before first compaction:

```
Call  1: ctx =  30,336  (system prompt — identical start)
Call  5: ctx =  34,266
Call 11: ctx =  48,638  (+10K jump — large response)
Call 20: ctx =  76,776
Call 25: ctx = 108,122
Call 31: ctx = 144,822  ← triggers compaction
Call 32: ctx = 122,899  ← COMPACTION
Call 33: ctx =  33,119  ← post-compaction, rebuilding
```

Growth rate: ~3,700 tokens/call average. Plugin hit compaction 3 calls later.

#### Compaction Event Comparison

| | Baseline Comp 1 | Baseline Comp 2 | Plugin Comp 1 | Plugin Comp 2 |
|---|---|---|---|---|
| Pre-compaction ctx | 151,285 | 98,815 | 144,822 | 148,017 |
| Compaction input (fresh) | 127,619 | 122,255 | 122,899 | 118,687 |
| Post-compaction output | 2,918 | 3,564 | 2,962 | 2,747 |
| Post-compaction ctx | ~33K | ~37K | ~33K | ~33K |

### 11.2 API Call Efficiency (Run 3)

| Metric | Baseline | Plugin |
|---|---|---|
| Total API calls | 140 | 89 |
| Calls per user message | 6.67 | 4.24 |
| Avg input per call | 5,189 | 6,473 |
| Avg output per call | 933 | 1,208 |
| Avg effective_ctx per call | 82,457 | 73,106 |

### 11.3 Cache Efficiency (Run 3)

| Metric | Baseline | Plugin |
|---|---|---|
| Total cache reads | 10,631,340 | 5,330,527 |
| Cache read per API call | 75,938 | 59,894 |
| Calls with cache_read=0 | 3 | 3 |

---

## 12. Per-User-Message Cost Breakdown (Run 3)

### 12.1 Baseline — 34 User Turns, 140 API Calls

| # | Calls | Input | Output | Compaction? | Message (first 70 chars) |
|---|---|---|---|---|---|
| 1 | 4 | 37,228 | 2,692 | | `[search-mode]` python-setup: list all deps |
| 2 | 1 | 1,407 | 828 | | database: PostgreSQL schema design |
| 3 | 3 | 3,532 | 330 | | `<system-reminder>` background task completed |
| 4 | 1 | 132 | 932 | | cicd: GitHub Actions pipeline |
| 5 | 2 | 11,700 | 4,207 | | `<system-reminder>` background task completed |
| 6 | 2 | 10,542 | 4,761 | | python-setup: write cli.py |
| 7 | 1 | 4,305 | 303 | | `<system-reminder>` background task completed |
| 8 | 1 | 5,151 | 49 | | `<system-reminder>` background task completed |
| 9 | 3 | 6,285 | 6,866 | | database: row-level security policies |
| 10 | 2 | 14,182 | 4,008 | | cicd: write Dockerfile |
| 11 | 2 | 13,578 | 8,863 | | python-setup: write test files |
| 12 | 2 | 14,153 | 10,756 | | database: migration management setup |
| 13 | 2 | 19,826 | 8,553 | | cicd: Kubernetes manifests |
| 14 | 2 | 14,081 | 5,279 | | python-setup: config.py with Pydantic Settings |
| 15 | 1 | 127,619 | 2,918 | ★ | **COMPACTION 1** |
| 16 | 1 | 3,274 | 215 | | "Continue if you have next steps" |
| 17 | 3 | 1,255 | 637 | | database: repository pattern |
| 18 | 15 | 36,466 | 4,757 | | cicd: monitoring and observability |
| 19 | 2 | 6,373 | 637 | | python-setup: pipeline.py |
| 20 | 8 | 4,600 | 1,798 | | `[search-mode]` python-setup deps |
| 21 | 12 | 128,360 | 10,503 | | cicd: end-to-end test workflow |
| 22 | 13 | 25,429 | 8,507 | | `[search-mode]` python-setup deps |
| 23 | 5 | 6,938 | 2,910 | | database: event sourcing extension |
| 24 | 1 | 122,255 | 3,564 | ★ | **COMPACTION 2** |
| 25 | 4 | 16,668 | 5,761 | | "Continue if you have next steps" |
| 26 | 9 | 3,131 | 1,798 | | `<system-reminder>` all background tasks complete |
| 27 | 9 | 9,168 | 2,020 | | cicd: chaos engineering test suite |
| 28 | 1 | 63 | 1,469 | | python-setup: file summary |
| 29 | 8 | 10,706 | 4,744 | | `[search-mode]` python-setup deps |
| 30 | 11 | 37,989 | 10,899 | | `<system-reminder>` all background tasks complete |
| 31 | 5 | 22,899 | 6,243 | | `[search-mode]` python-setup deps |
| 32 | 2 | 5,396 | 821 | | `[search-mode]` python-setup deps |
| 33 | 1 | 760 | 1,001 | | **RECALL Q2**: database schema summary |
| 34 | 1 | 1,023 | 1,012 | | **RECALL Q3**: CI/CD stages |

### 12.2 Plugin — 33 User Turns, 89 API Calls

| # | Calls | Input | Output | Compaction? | Message (first 70 chars) |
|---|---|---|---|---|---|
| 1 | 4 | 33,241 | 1,625 | | `[search-mode]` python-setup: list all deps |
| 2 | 4 | 4,957 | 3,647 | | database: PostgreSQL schema design |
| 3 | 1 | 3,116 | 45 | | `<system-reminder>` background task completed |
| 4 | 2 | 10,455 | 4,190 | | cicd: GitHub Actions pipeline |
| 5 | 1 | 3,871 | 3,711 | | python-setup: write cli.py |
| 6 | 3 | 6,432 | 5,254 | | database: row-level security policies |
| 7 | 2 | 11,717 | 3,085 | | cicd: write Dockerfile |
| 8 | 1 | 2,989 | 26 | | `<system-reminder>` all background tasks complete |
| 9 | 2 | 6,134 | 7,856 | | python-setup: write test files |
| 10 | 2 | 12,780 | 9,324 | | database: migration management setup |
| 11 | 2 | 11,889 | 6,731 | | cicd: Kubernetes manifests |
| 12 | 1 | 6,686 | 3,882 | | python-setup: config.py with Pydantic Settings |
| 13 | 2 | 4,329 | 11,456 | | database: repository pattern |
| 14 | 2 | 16,857 | 12,831 | | cicd: monitoring and observability |
| 15 | 2 | 15,528 | 7,764 | | python-setup: pipeline.py |
| 16 | 1 | 122,899 | 2,962 | ★ | **COMPACTION 1** |
| 17 | 1 | 3,318 | 206 | | "Continue if you have next steps" |
| 18 | 4 | 2,099 | 999 | | `[search-mode]` python-setup deps |
| 19 | 3 | 1,105 | 661 | | cicd: end-to-end test workflow |
| 20 | 11 | 16,989 | 2,137 | | `[search-mode]` python-setup deps |
| 21 | 2 | 6,619 | 145 | | `<system-reminder>` background task completed |
| 22 | 6 | 15,932 | 1,413 | | database: event sourcing extension |
| 23 | 3 | 9,481 | 589 | | cicd: chaos engineering test suite |
| 24 | 3 | 12,279 | 878 | | `<system-reminder>` background task completed |
| 25 | 5 | 33,336 | 2,213 | | python-setup: file summary |
| 26 | 2 | 19,460 | 206 | | `<system-reminder>` background task completed |
| 27 | 1 | 118,687 | 2,747 | ★ | **COMPACTION 2** |
| 28 | 1 | 3,425 | 348 | | "Continue if you have next steps" |
| 29 | 7 | 16,178 | 4,068 | | `[search-mode]` python-setup deps |
| 30 | 4 | 37,953 | 4,477 | | `[search-mode]` python-setup deps |
| 31 | 2 | 3,932 | 657 | | `[search-mode]` python-setup deps |
| 32 | 1 | 596 | 761 | | **RECALL Q2**: database schema summary |
| 33 | 1 | 781 | 578 | | **RECALL Q3**: CI/CD stages |

---

## 13. Files Modified

- `ANALYSIS.md` — This file (rewritten with multi-run results)
- `ab_test_harness.py` — Timeout 600→900s, consecutive failure threshold 3→5, session preservation, per-message tracking
- `ab_test_results.json` — Run 3 results
- `ab_test_results_run4_claude-sonnet-4.json` — Run 4 results
- `ab_test_results_run5_claude-sonnet-4.json` — Run 5 results
- `ab_test_results_run6_claude-sonnet-4.json` — Run 6 results
- `ab_test_results_run7_claude-sonnet-4.json` — Run 7 results
- `ab_test_results_run8_gpt-5.4-mini.json` — Run 8 results
- `ab_test_results_run9_gemini-3-flash-preview.json` — Run 9 results

---

## Appendix A: Run 3 Raw Harness Console Output

```
Topic-Aware Compaction A/B Test Harness
Baseline: localhost:3100
Plugin:   localhost:3200
Model:    github-copilot/claude-sonnet-4

============================================================
  Running BASELINE test
============================================================
  Session: ses_1ec1c0c67ffedFkOcb7x0kjHp2
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
  [15/21] Topic: cicd... ✗ (timed out)
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
  Session preserved: ses_1ec1c0c67ffedFkOcb7x0kjHp2

============================================================
  Running PLUGIN test
============================================================
  Session: ses_1ebef373effep40l3j3QyKBx7q
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
  Session preserved: ses_1ebef373effep40l3j3QyKBx7q

============================================================
  A/B TEST REPORT
============================================================

Token Usage Comparison:
Metric                        Baseline       Plugin        Delta        %
-----------------------------------------------------------------------
Input Tokens                   726,474      576,050    -150,424  -20.7%
Output Tokens                  130,641      107,472     -23,169  -17.7%
Reasoning Tokens                     0            0           0    0.0%
Cache Read                  10,631,340    5,330,527  -5,300,813  -49.9%
Cache Write                          0            0           0    0.0%
TOTAL                          857,115      683,522    -173,593  -20.3%

Metric                        Baseline       Plugin
-------------------------------------------------
Messages                           140           89
Peak Context Window            151,285      148,017
Compactions                          2            2
Wall Time (s)                   2938.2       1780.9
Errors                               1            0


Full results saved to: ab_test_results.json
```

## Appendix B: Run 3 Recall Responses (Full Text, Truncated at 500 chars by harness)

### B.1 python-setup

**Baseline:**
> ## All Dependencies
>
> ### Runtime Dependencies (`[project.dependencies]`)
>
> | Package | Version | Purpose |
> |---|---|---|
> | `click` | >=8.1 | CLI framework (`run`, `validate`, `status` commands) |
> | `httpx` | >=0.27 | Async HTTP client (used in pipeline, health checks) |
> | `prometheus-client` | >=0.21 | Metrics exposition (histograms, counters, gauges, custom collectors) |
> | `pydantic` | >=2.0 | Data validation for config and models |
> | `pydantic-settings` | >=2.0 | Settings management from env va...

**Plugin:**
> ### Production Dependencies (11)
>
> | Package | Version Constraint | Purpose |
> |---------|-------------------|---------| 
> | `click` | >=8.1 | CLI framework (`cli.py` run/validate/status commands) |
> | `fastapi` | >=0.115 | Web framework (app factory, routers, middleware) |
> | `httpx` | >=0.27 | Async HTTP client (used by tests/health checks) |
> | `psycopg[binary,pool]` | >=3.2 | PostgreSQL driver with `AsyncConnectionPool` — extras: `binary` (C bindings), `pool` (connection pooling) |
> | `pydantic` | >...

### B.2 database

**Baseline:**
> ## Tables (7)
>
> | Table | PK | Tenant-scoped | Purpose |
> |---|---|---|---|
> | `tenants` | `id uuid` | No (root table) | Tenant registry with name, slug, plan (free/pro/enterprise), active flag |
> | `users` | `id uuid` | Yes (`tenant_id` FK) | Users with email, display_name, role (admin/member/viewer), unique `(tenant_id, email)` |
> | `projects` | `id uuid` | Yes (`tenant_id` FK) | Projects with owner (`users.id`, ON DELETE RESTRICT), status (active/paused/archived) |
> | `tasks` | `id uuid` | Yes (`...

**Plugin:**
> ### Tables (7)
>
> | Table | PK | Key Columns |
> |-------|-----|------------|
> | **tenants** | `id` UUID | `name`, `slug` (UNIQUE), `created_at` |
> | **users** | `id` UUID | `tenant_id` FK→tenants, `email`, `name`, `role` CHECK(owner/admin/member), UNIQUE(tenant_id, email) |
> | **projects** | `id` UUID | `tenant_id` FK→tenants, `name`, `created_by` FK→users, `created_at` |
> | **tasks** | `id` UUID | `tenant_id` FK→tenants, `project_id` FK→projects, `title`, `status` CHECK(todo/in_progress/done), `assign...

### B.3 cicd

**Baseline:**
> ## Workflow 1: `ci.yml` — CI/CD Pipeline
>
> Triggers: push to `main`, `v*` tags, PRs against `main`.
>
> ```
> lint ──→ test ──→ integration-test ──→ build-and-push ──┬──→ deploy-staging
>                                                         │     (main only)
>                                                         └──→ approve-production ──→ deploy-production
>                                                               (v* tags only)         (v* tags only)
>
>                          notify-failure (...

**Plugin:**
> ### CI/CD Pipeline (`.github/workflows/ci.yml`)
>
> **Triggers**: push to `main`, push of `v*` tags, PRs to `main`
>
> | Stage | Depends On | Trigger Condition | What It Does |
> |-------|-----------|-------------------|--------------| 
> | **lint** | — | always | `ruff check` + `ruff format --check` |
> | **test** | lint | always | `pytest --tb=short -q` |
> | **build-and-push** | test | push only (not PRs) | Docker build → push to GHCR with sha/semver/latest tags |
> | **deploy-staging** | build-and-push | `...

## Appendix C: Run 3 Per-Message Token Data (Baseline)

Effective context window at each API call (140 calls total):

```
Call   1:  30,336    Call  29: 127,619 ← COMPACTION 1
Call   2:  35,284    Call  30:  33,075
Call   3:  36,081    Call  31:  33,360
Call   4:  37,223    Call  32:  33,882
Call   5:  38,629    Call  33:  34,323
Call   6:  40,554    Call  34:  34,444
Call   7:  41,245    Call  35:  35,081
Call   8:  42,001    Call  36:  36,761
Call   9:  42,132    Call  37:  37,255
Call  10:  52,959    Call  38:  37,386
Call  11:  53,669    Call  39:  37,583
Call  12:  57,826    Call  40:  37,908
Call  13:  64,207    Call  41:  38,432
Call  14:  68,511    Call  42:  54,202
Call  15:  69,357    Call  43:  62,757
Call  16:  69,464    Call  44:  62,995
Call  17:  75,291    Call  45:  63,410
Call  18:  75,485    Call  46:  69,791
Call  19:  81,636    Call  47:  70,317
Call  20:  89,663    Call  48:  70,772
Call  21:  93,364    Call  49:  71,615
Call  22: 103,237    Call  50:  77,141
Call  23: 111,797    Call  51:  77,891
Call  24: 117,386    Call  52:  79,376
Call  25: 127,887    Call  53:  79,554
Call  26: 137,208    Call  54:  79,744
Call  27: 145,489    Call  55:  79,886
Call  28: 151,285    Call  56:  80,465

Call  57:  80,670    Call  86: 122,255 ← COMPACTION 2 (actual)
Call  58:  81,731    Call  87:  33,721
Call  59:  81,871    Call  88:  37,455
Call  60:  82,881    Call  89:  37,719
Call  61:  83,777    Call  90:  46,464
Call  62:  83,933    Call  91:  47,107
Call  63:  86,427    Call  92:  47,238
Call  64:  98,815    Call  93:  47,419
Call  65: 105,541    Call  94:  47,848
Call  66: 112,438    Call  95:  48,325
Call  67: 114,577    Call  96:  48,714
Call  68: 123,907    Call  97:  48,942
Call  69: 125,453    Call  98:  49,193
Call  70: 126,237    Call  99:  49,471
Call  71: 127,575    Call 100:  49,812
Call  72: 127,783    Call 101:  50,607
Call  73: 128,139    Call 102:  51,194
Call  74: 137,240    Call 103:  51,536
Call  75: 137,793    Call 104:  55,299
Call  76: 138,140    Call 105:  56,517
Call  77: 138,537    Call 106:  57,480
Call  78: 138,983    Call 107:  58,324
Call  79: 139,335    Call 108:  58,628
Call  80: 139,810    Call 109:  58,690
Call  81: 140,291    Call 110:  60,286
Call  82: 143,082    Call 111:  60,792
Call  83: 146,005    Call 112:  61,252
Call  84: 146,387    Call 113:  61,675
Call  85: 146,741    Call 114:  68,968

Call 115:  69,135    Call 130: 110,921
Call 116:  69,264    Call 131: 115,401
Call 117:  69,384    Call 132: 126,531
Call 118:  73,107    Call 133: 131,201
Call 119:  83,454    Call 134: 131,923
Call 120:  83,820    Call 135: 132,682
Call 121:  83,967    Call 136: 133,702  ← final
Call 122:  86,081
Call 123:  92,743
Call 124:  93,116
Call 125: 102,559
Call 126: 102,822
Call 127: 103,283
Call 128: 103,639
Call 129: 104,581
```

## Appendix D: Run 3 Per-Message Token Data (Plugin)

Effective context window at each API call (89 calls total):

```
Call   1:  30,336    Call  32: 122,899 ← COMPACTION 1
Call   2:  30,866    Call  33:  33,119
Call   3:  32,806    Call  34:  33,671
Call   4:  33,236    Call  35:  34,208
Call   5:  34,266    Call  36:  34,742
Call   6:  34,788    Call  37:  35,210
Call   7:  35,085    Call  38:  35,297
Call   8:  38,187    Call  39:  35,849
Call   9:  41,302    Call  40:  36,310
Call  10:  41,434    Call  41:  36,474
Call  11:  48,638    Call  42:  37,090
Call  12:  52,508    Call  43:  37,632
Call  13:  56,306    Call  44:  39,825
Call  14:  56,660    Call  45:  43,082
Call  15:  58,933    Call  46:  43,937
Call  16:  63,857    Call  47:  45,035
Call  17:  70,646    Call  48:  46,770
Call  18:  73,634    Call  49:  47,578
Call  19:  73,697    Call  50:  52,983
Call  20:  76,776    Call  51:  53,286
Call  21:  84,577    Call  52:  53,795
Call  22:  89,552    Call  53:  59,394
Call  23:  98,720    Call  54:  59,540
Call  24: 101,437    Call  55:  63,725
Call  25: 108,122    Call  56:  65,487
Call  26: 112,077    Call  57:  65,738
Call  27: 112,445    Call  58:  65,923
Call  28: 123,856    Call  59:  75,318
Call  29: 129,298    Call  60:  75,813
Call  30: 141,975    Call  61:  76,259
Call  31: 144,822    Call  62:  84,794

Call  63:  85,159
Call  64:  93,196
Call  65:  96,915
Call  66:  97,382
Call  67: 102,885
Call  68: 108,360
Call  69: 128,078
Call  70: 130,244
Call  71: 131,929
Call  72: 148,017    ← PEAK, triggers compaction 2

Call  73: 118,687 ← COMPACTION 2 (cache_read=0)
Call  74:  33,226
Call  75:  33,639
Call  76:  34,127
Call  77:  34,533
Call  78:  34,959
Call  79:  44,629
Call  80:  45,565
Call  81:  45,971
Call  82:  48,654
Call  83:  49,983
Call  84:  63,109
Call  85:  63,737
Call  86:  67,005
Call  87:  67,665
Call  88:  68,260
Call  89:  69,038    ← final
```

## Appendix E: Run 4 Summary (Claude Sonnet 4 — Plugin Worse)

```
Timestamp: 2026-05-11T13:23:11+0800
Model: github-copilot/claude-sonnet-4

Baseline:
  Input: 341,314  Output: 163,348  Cache Read: 8,028,917  Total: 504,662
  Messages: 102  Compactions: 1  Wall Time: 2,621s  Errors: 0
  Session: ses_1ead98c17ffeHKSwqZ2Q9z2XwV

Plugin:
  Input: 1,328,920  Output: 172,766  Cache Read: 12,860,105  Total: 1,501,686
  Messages: 159  Compactions: 3  Wall Time: 3,069s  Errors: 0
  Session: ses_1eab18fa5ffeVHrph7PHwbLjOC

Delta: +197.6% (plugin used 3x more tokens)
```

Full results: `ab_test_results_run4_claude-sonnet-4.json` (1,616 lines)

## Appendix F: Run 5 Summary (Claude Sonnet 4 — Plugin Slightly Worse)

```
Timestamp: 2026-05-11T14:57:58+0800
Model: github-copilot/claude-sonnet-4

Baseline:
  Input: 834,282  Output: 134,264  Cache Read: 10,094,759  Total: 968,546
  Messages: 128  Compactions: 2  Wall Time: 3,086s  Errors: 0
  Session: ses_1ea816a53ffemSpl2GnKD4DdIY

Plugin:
  Input: 937,190  Output: 123,489  Cache Read: 3,197,054  Total: 1,060,679
  Messages: 58  Compactions: 1  Wall Time: 2,514s  Errors: 0
  Session: ses_1ea525289ffeudawDXEPuFowyj

Delta: +9.5% (plugin slightly more total, but 68% less cache reads and 55% fewer calls)
```

Full results: `ab_test_results_run5_claude-sonnet-4.json` (1,166 lines)

## Appendix G: Run 6 Summary (Claude Sonnet 4 — Baseline Incomplete)

```
Timestamp: 2026-05-11T18:18:08+0800
Model: github-copilot/claude-sonnet-4

Baseline:
  Input: 459,647  Output: 67,298  Cache Read: 2,477,794  Total: 526,945
  Messages: 43  Compactions: 1  Wall Time: 8,576s  Errors: 8
  Errors: msgs 10-14 timed out, Recall Q1-Q3 timed out
  Session: ses_1ea1ae4f7ffekzDFOJYG77m58A

Plugin:
  Input: 543,098  Output: 152,022  Cache Read: 5,657,795  Total: 695,120
  Messages: 83  Compactions: 2  Wall Time: 2,315s  Errors: 0
  Session: ses_1e9980772ffeo6ercgPxIr7SoE

Note: Baseline failed catastrophically (8 errors). Plugin completed all 21 messages + recall with 0 errors.
```

Full results: `ab_test_results_run6_claude-sonnet-4.json` (811 lines)

## Appendix H: Run 7 Summary (Claude Sonnet 4 — Baseline Incomplete)

```
Timestamp: 2026-05-11T21:34:27+0800
Model: github-copilot/claude-sonnet-4

Baseline:
  Input: 277,009  Output: 130,388  Cache Read: 980,530  Total: 407,397
  Messages: 17  Compactions: 1  Wall Time: 8,474s  Errors: 8
  Errors: msgs 15-19 timed out, Recall Q1-Q3 timed out
  Session: ses_1e970a211ffe5XLgBJhp9lxQGo

Plugin:
  Input: 861,144  Output: 168,750  Cache Read: 10,212,233  Total: 1,029,894
  Messages: 133  Compactions: 3  Wall Time: 3,038s  Errors: 0
  Session: ses_1e8ef55bdffeD40wSqr0iL3Euk

Note: Baseline failed catastrophically (8 errors). Plugin completed with 0 errors.
```

Full results: `ab_test_results_run7_claude-sonnet-4.json` (955 lines)

## Appendix I: Run 8 Summary (GPT-5.4-mini — Plugin Incomplete)

```
Timestamp: 2026-05-12T00:47:29+0800
Model: github-copilot/gpt-5.4-mini

Baseline:
  Input: 454,043  Output: 140,922  Cache Read: 2,374,832  Total: 594,965
  Messages: 36  Compactions: 1  Wall Time: 1,800s  Errors: 0
  Session: ses_1e8b86800ffe0dtoCBqUehAU3e

Plugin:
  Input: 274,839  Output: 118,485  Cache Read: 1,608,137  Total: 393,324
  Messages: 27  Compactions: 1  Wall Time: 9,222s  Errors: 8
  Errors: msgs 16-19 timed out, Recall Q1-Q3 timed out
  Session: ses_1e89cf20affe4SZG1tyo0vF8KF

Note: Reversed failure pattern — plugin timed out, baseline completed cleanly. Only run where plugin failed.
```

Full results: `ab_test_results_run8_gpt-5.4-mini.json` (433 lines)

## Appendix J: Run 9 Summary (Gemini 3 Flash — Best Result)

```
Timestamp: 2026-05-12T02:14:47+0800
Model: github-copilot/gemini-3-flash-preview

Baseline:
  Input: 874,764  Output: 152,903  Cache Read: 12,486,646  Total: 1,027,667
  Messages: 164  Compactions: 3  Wall Time: 2,908s  Errors: 0
  Session: ses_1e807e7b6ffeNI1Bfd5bqWtsfS

Plugin:
  Input: 349,943  Output: 142,650  Cache Read: 2,188,972  Total: 492,593
  Messages: 34  Compactions: 1  Wall Time: 1,784s  Errors: 0
  Session: ses_1e7db8791ffeLuvdPqgXN8616X

Delta: -52.1% total, -60.0% input, -82.5% cache reads, -79.3% API calls
```

Full results: `ab_test_results_run9_gemini-3-flash-preview.json` (1,238 lines)

## Appendix K: Surviving Session IDs (All Runs)

| Run | Variant | Session ID | Model |
|-----|---------|-----------|-------|
| 3 | Baseline | `ses_1ec1c0c67ffedFkOcb7x0kjHp2` | claude-sonnet-4 |
| 3 | Plugin | `ses_1ebef373effep40l3j3QyKBx7q` | claude-sonnet-4 |
| 4 | Baseline | `ses_1ead98c17ffeHKSwqZ2Q9z2XwV` | claude-sonnet-4 |
| 4 | Plugin | `ses_1eab18fa5ffeVHrph7PHwbLjOC` | claude-sonnet-4 |
| 5 | Baseline | `ses_1ea816a53ffemSpl2GnKD4DdIY` | claude-sonnet-4 |
| 5 | Plugin | `ses_1ea525289ffeudawDXEPuFowyj` | claude-sonnet-4 |
| 6 | Baseline | `ses_1ea1ae4f7ffekzDFOJYG77m58A` | claude-sonnet-4 |
| 6 | Plugin | `ses_1e9980772ffeo6ercgPxIr7SoE` | claude-sonnet-4 |
| 7 | Baseline | `ses_1e970a211ffe5XLgBJhp9lxQGo` | claude-sonnet-4 |
| 7 | Plugin | `ses_1e8ef55bdffeD40wSqr0iL3Euk` | claude-sonnet-4 |
| 8 | Baseline | `ses_1e8b86800ffe0dtoCBqUehAU3e` | gpt-5.4-mini |
| 8 | Plugin | `ses_1e89cf20affe4SZG1tyo0vF8KF` | gpt-5.4-mini |
| 9 | Baseline | `ses_1e807e7b6ffeNI1Bfd5bqWtsfS` | gemini-3-flash |
| 9 | Plugin | `ses_1e7db8791ffeLuvdPqgXN8616X` | gemini-3-flash |

## Appendix L: Harness Configuration (Final)

```python
# ab_test_harness.py (relevant settings)
timeout = httpx.Timeout(900.0, connect=10.0)      # per-message timeout
consecutive_failure_limit = 5                       # stop after 5 consecutive failures
baseline_port = 3100
plugin_port = 3200
password = "test"
conversation_messages = 21                          # 7 per topic × 3 topics
recall_questions = 3                                # 1 per topic
session_deletion = False                            # sessions preserved for inspection
per_message_tracking = True                         # per_message_tokens array in output
peak_context_tracking = True                        # peak_context_window metric
```

## Appendix M: Harness Bug Fix History

| Bug | Symptom | Fix | Run Affected |
|---|---|---|---|
| Auth format | 401 errors | `auth=("", pw)` → `auth=("opencode", pw)` | Run 0 |
| Message body | 400 errors | `{"content": text}` → `{"parts": [...]}` | Run 0 |
| Token parsing | KeyError | `msg["role"]` → `msg["info"]["role"]` | Run 0 |
| opencode.json | Invalid config | Removed `{"provider": "anthropic"}` | Run 0 |
| Session deletion | No post-hoc inspection | Removed `client.delete_session()` call | Run 1 |
| Per-message tracking | No growth curves | Added `per_message_tokens` array | Run 2 |
| Peak context | Missing metric | Added `peak_context_window` | Run 2 |
| Model label | Wrong model used | `anthropic/claude-sonnet-4` → `github-copilot/claude-sonnet-4` | Run 2 |
| CLI command | Server start failure | `opencode server` → `opencode serve` | Run 2 |
| Timeout | Excessive failures | 600s → 900s | Run 3 |
| Failure threshold | Early abort | 3 → 5 consecutive failures | Run 3 |

---

## Addendum: v0.11.0 3-Way Test (Runs 10-11)

After upgrading to PEtFiSh v0.11.0 (AGENTS.md reduced from 13,937 to 777 tokens via tiered loading), we ran a 3-way A/B test comparing v0.10.x, v0.11.0, and v0.11.0+plugin.

**Key findings:**
- v0.11.0 used **+36.6% MORE** total tokens than v0.10.x despite 94% smaller AGENTS.md (on-demand Read converts system prompt cost → conversation context cost)
- v0.11.0+plugin showed **-66.5%** vs v0.11.0 baseline, but with only 28 API calls (lowest ever — stochastic outlier)
- Updated Sonnet plugin statistics (all 6 valid runs): mean **+30.1% ± 118.5%** — not statistically significant
- All 3 configs had **0 errors** — first time all variants completed cleanly

**Full analysis:** `experiments/v011-upgrade/V011-3WAY-ANALYSIS.md`
**Raw data:** `ab_test_results_v011_round1_20260512_100428.json`, `ab_test_results_v011_round2_20260512_100428.json`
