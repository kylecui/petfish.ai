# Recall Quality Test Results

**Date**: 2026-05-19  
**Objective**: Determine if the fish-trail-compaction plugin's topic-aware structured summary improves recall quality after compaction compared to OpenCode's default compaction.

## Setup

- **Model**: `github-copilot/claude-sonnet-4` (temperature=0)
- **Baseline** (port 3100): Default OpenCode compaction
- **Plugin** (port 3200): fish-trail-compaction plugin with topic-aware structured summary
- **Runs**: 3 baseline, 2 plugin (run2 plugin server stalled; not a test design issue)
- **Warm-up**: 21 interleaved messages across 3 topics (python-setup, database, cicd)
- **Recall**: 12 questions post-compaction
- **Judge**: LLM-as-judge scoring factual_recall, detail_completeness, cross_topic_isolation

## Aggregate Results

| Metric | Baseline (n=3) | Plugin (n=2) | Delta |
|--------|---------------|-------------|-------|
| Factual Recall | **0.833** | 0.667 | -0.167 |
| Detail Completeness % | **0.806** | 0.611 | -0.194 |
| Cross-Topic Isolation | **0.806** | 0.667 | -0.139 |

**Baseline outperforms plugin on all three metrics.**

## Per-Question Breakdown

| QID | B_recall | P_recall | B_detail% | P_detail% | B_isolation | P_isolation |
|-----|----------|----------|-----------|-----------|-------------|-------------|
| C1 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |
| C2 | 1.00 | 0.50 | 0.80 | 0.60 | 1.00 | 1.00 |
| C3 | 1.00 | 1.00 | 1.00 | 0.88 | 0.67 | 1.00 |
| D1 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |
| D2 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |
| D3 | 1.00 | 0.00 | 0.93 | 0.40 | 1.00 | 0.50 |
| P1 | 1.00 | 0.50 | 1.00 | 0.50 | 1.00 | 0.50 |
| P2 | 0.67 | 0.50 | 0.87 | 0.50 | 1.00 | 0.00 |
| P3 | 0.00 | 0.00 | 0.53 | 0.40 | 0.33 | 0.00 |
| X1 | 1.00 | 1.00 | 0.56 | 0.67 | 0.33 | 0.50 |
| X2 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |
| X3 | 0.33 | 0.50 | 0.56 | 0.50 | 0.33 | 0.50 |

## Compaction Counts

| Run | Baseline | Plugin |
|-----|----------|--------|
| 1 | 1 | **2** |
| 2 | 1 | (stalled) |
| 3 | 1 | 1 |

Note: Plugin run 1 experienced **double compaction** — the plugin's structured summary may have added enough tokens to trigger a second compaction event, further degrading recall.

## Analysis

### Key Findings

1. **Plugin does NOT improve recall quality** — it slightly degrades it across all metrics.

2. **Double compaction risk**: The plugin's structured summary (which prepends topic metadata to the compaction output) can increase the post-compaction token count enough to trigger a *second* compaction. This was observed in run 1 plugin (2 compactions vs 1 for baseline). Double compaction is catastrophic for recall.

3. **Simple questions unaffected**: Both conditions perform equally well on easy recall questions (C1, D1, D2, X2). The gap appears on harder multi-detail questions (D3, P1, P2).

4. **Cross-topic questions (X1-X3)**: Interestingly, the plugin performs slightly better on some cross-topic questions (X3), suggesting the topic-aware summary may help with cross-domain reasoning even while hurting single-topic recall.

5. **Python-setup topic most affected**: P1-P3 questions show the largest baseline advantage, suggesting the plugin's topic-bucketing may have deprioritized specific version numbers and CLI commands in favor of higher-level summaries.

### Why Plugin Underperforms

The Phase 2 plugin hooks `experimental.session.compacting` — it receives the compaction summary *after* OpenCode generates it, then prepends topic-aware metadata. This approach:

1. **Adds tokens** to the compacted output (topic headers, structured metadata)
2. May trigger **additional compaction** if the enhanced summary exceeds thresholds
3. **Does not influence** what the default compactor preserves — it only adds structure on top
4. The added structure may actually **dilute** the signal-to-noise ratio of the summary

### Implications for Phase 3

The `experimental.chat.messages.transform` hook (proposed in issue #135) would allow the plugin to influence *what gets compacted* rather than merely decorating the result. This is the correct intervention point if the goal is to improve recall.

## Conclusion

**Phase 2 plugin hypothesis REJECTED**: Topic-aware structured compaction summary does not improve (and slightly degrades) recall quality compared to default OpenCode compaction.

**Root cause**: The plugin operates too late in the pipeline. By the time it receives the compaction summary, information loss has already occurred. Adding metadata on top cannot recover lost details and may trigger additional compaction.

**Recommendation**: Phase 3 approach (pre-compaction message transformation via `messages.transform` hook) is the viable path. The plugin should influence *which information survives compaction*, not merely annotate the result.

## Test Artifacts

- `recall_results_run{1,2,3}_{baseline,plugin}.json` — raw recall responses
- `judged_recall_results_*.json` — LLM-as-judge scores
- `recall_questions.json` — 12 questions with ground truth
- `recall_test_harness.py` — test automation
- `recall_judge.py` — judge automation
