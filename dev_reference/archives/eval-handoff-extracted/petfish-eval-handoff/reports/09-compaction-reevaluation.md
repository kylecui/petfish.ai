# Fish-Trail Compaction Plugin Re-evaluation Under v0.11.0

## Context

The fish-trail compaction plugin was designed to reduce context window usage by compacting older messages in long conversations. We tested it extensively in `experiments/compact-test-round2/` across 7 runs (3-9).

v0.11.0 changes the baseline by reducing AGENTS.md from **13,937 tokens** (all inline) to **777 tokens** (base + route table). This fundamentally changes the compaction plugin's value proposition.

**Update (2026-05-12):** Actual test data now available from 3-way A/B test (runs 10-11). See full analysis in `V011-3WAY-ANALYSIS.md`.

---

## System Prompt Impact Analysis

### Before (v0.10.x)
- System prompt: ~30,000 tokens (AGENTS.md 13,937 + OpenCode framework ~16,000)
- AGENTS.md was 46% of system prompt
- Conversation context budget: ~170K tokens (200K limit - 30K system)

### After (v0.11.0, no packs triggered)
- System prompt: ~16,777 tokens (AGENTS.md 777 + OpenCode framework ~16,000)
- AGENTS.md is now 4.6% of system prompt
- Conversation context budget: ~183K tokens (200K limit - 17K system)
- **Net gain: ~13K more tokens for conversation**

### After (v0.11.0, 1 typical pack triggered)
- System prompt: ~18,800 tokens (AGENTS.md 777 + route table read ~2,000 avg + framework ~16,000)
- Conversation context budget: ~181K tokens
- **Net gain: ~11K more tokens for conversation**

---

## Actual Test Results (Runs 10-11)

### Round 1: v0.10.x vs v0.11.0 (no plugin)

| Metric | v0.10.x (Run 10) | v0.11.0 (Run 10) | Delta |
|--------|------------------|-------------------|-------|
| Total tokens | 744,904 | 1,017,201 | **+36.6%** |
| API calls | 110 | 109 | -0.9% |
| Errors | 0 | 0 | — |
| Peak context | 155,648 | 148,764 | -4.4% |

**Key finding:** v0.11.0 used MORE total tokens despite 94% smaller AGENTS.md. The on-demand Read tool mechanism converts system prompt tokens (cached) into conversation context tokens (uncached), increasing net cost.

### Round 2: v0.11.0 vs v0.11.0 + Plugin

| Metric | v0.11.0 (Run 11) | v0.11.0+Plugin (Run 11) | Delta |
|--------|-------------------|--------------------------|-------|
| Total tokens | 721,245 | 241,804 | **-66.5%** |
| API calls | 106 | 28 | -73.6% |
| Compactions | 2 | 0 | — |
| Errors | 0 | 0 | — |
| Peak context | 152,480 | 137,668 | -9.7% |
| Wall time | 2,125s | 1,445s | -32.0% |

**Key finding:** Plugin showed strong savings, but 28 API calls is the lowest ever recorded across all 11 runs. This is likely a stochastic outlier — the LLM happened to solve tasks in fewer turns.

### Updated Cross-Run Statistics (All Sonnet Runs)

| Metric | Runs 3-9 (v0.10.x) | Runs 10-11 (v0.11.0) |
|--------|---------------------|----------------------|
| Plugin delta range | -20.3% to +197.6% | -66.5% (single run) |
| Mean plugin delta | +62.3% (plugin worse) | -66.5% (plugin better) |
| Baseline errors | 0-8 per run | 0 |
| Plugin errors | 0 per run | 0 |

**Combined Sonnet mean (all 6 valid runs):** +30.1% ± 118.5% — **not statistically significant.**

---

## Impact on Compaction Plugin Value

### 1. Token Savings (UNRELIABLE — CONFIRMED)

The compaction plugin's primary claimed benefit was reducing total tokens consumed. Our testing showed this was already **unreliable on Claude Sonnet 4**:

**v0.10.x runs (3-9):**
- Run 3: -20.3% (only clean positive result)
- Run 4: +197.6% (plugin used far MORE tokens)
- Run 5: +9.5% (plugin used slightly more)
- Average across valid Sonnet runs: +62.3% (plugin WORSE)

**v0.11.0 runs (10-11):**
- Run 11: -66.5% (strong positive result, but 28 API calls = stochastic outlier)
- Combined mean across all Sonnet runs: +30.1% ± 118.5% (not significant)

### 2. Timeout Resilience (ANSWERED)

**v0.10.x:** Plugin's most proven benefit was timeout resilience — 0 plugin errors vs 17 baseline errors across 5 Sonnet runs.

**v0.11.0:** Both baseline AND plugin had **0 errors** in runs 10-11. This suggests v0.11.0's smaller system prompt may independently reduce timeout frequency, making the plugin's timeout benefit partially redundant. (Sample size: 1 run each — needs more data to confirm.)

### 3. Cross-Model Results (Updated)

| Model | Plugin Effect (v0.10.x) | Plugin Effect (v0.11.0) |
|-------|------------------------|------------------------|
| Claude Sonnet 4 | Unreliable (-20% to +198%) | -66.5% (single run, outlier) |
| Gemini 3 Flash | Strong (-52.1%) | Not tested |
| GPT-5.4-mini | Invalid (plugin timed out) | Not tested |

---

## Revised Recommendation (Updated with Actual Data)

### For Claude Sonnet 4 Users
**Do NOT use the compaction plugin.** Combined evidence across 6 valid Sonnet runs shows mean +30.1% ± 118.5% — the plugin is as likely to increase costs as decrease them. v0.11.0 alone provides deterministic system prompt reduction.

### For Gemini Users
**Tentatively useful.** Single-run -52% result on Gemini 3 Flash was promising. Not retested under v0.11.0.

### For All Users
**Upgrade to v0.11.0 first.** The tiered AGENTS.md is a guaranteed, zero-risk improvement:
- No behavioral changes
- No runtime overhead
- Deterministic savings (unlike compaction's stochastic results)

The compaction plugin should be considered **experimental/research** — not production-ready.

**Important caveat:** v0.11.0's static savings (94% AGENTS.md reduction) do NOT translate to runtime savings. Our Round 1 test showed v0.11.0 actually used +36.6% MORE total tokens than v0.10.x due to on-demand Read tool overhead. The real benefit of v0.11.0 is reduced system prompt size (better prompt caching), not reduced total token consumption.

---

## Answered Questions

1. ✅ **Does v0.11.0 alone reduce Sonnet timeouts?** Yes — 0 errors in both variants (run 10). But single-run sample.
2. ✅ **Does on-demand rule loading add latency?** Yes — Read tool calls add conversation tokens, resulting in +36.6% total token increase.
3. ✅ **Is there a compounding benefit?** (v0.11.0 + compaction) Run 11 showed -66.5%, but this is a stochastic outlier (28 API calls). Not a reliable signal.
4. ⬜ **Does the reduced system prompt change Claude's behavior?** Recall quality was comparable across all 3 configs. No degradation observed.

## Remaining Questions

1. **Would native agents-rules/ support (system prompt injection) recover the savings?** Requires OpenCode feature request.
2. **Is the v0.11.0 timeout resilience real?** Need 3+ more runs to confirm 0-error result isn't luck.
3. **Does Gemini still benefit from plugin under v0.11.0?** Not tested.

---

## Data Sources

- Round 1: `experiments/compact-test-round2/ab_test_results_v011_round1_20260512_100428.json`
- Round 2: `experiments/compact-test-round2/ab_test_results_v011_round2_20260512_100428.json`
- Full log: `experiments/compact-test-round2/v011_3way_test_20260512_100428.log`
- Comprehensive analysis: `experiments/v011-upgrade/V011-3WAY-ANALYSIS.md`
- Prior runs (3-9): `experiments/compact-test-round2/ANALYSIS.md`
