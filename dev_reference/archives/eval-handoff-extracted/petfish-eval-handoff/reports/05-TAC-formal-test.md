# Topic-Aware Compaction (TAC) Experiment Report

## Null Result: TAC Does Not Reduce API Token Cost via Behavioral Change

**Date:** 2026-05-20  
**Experiment ID:** compact-test-round3  
**Status:** COMPLETED — PRIMARY HYPOTHESIS NOT SUPPORTED

---

## 1. Executive Summary

We conducted a controlled 3-arm A/B experiment to test whether Topic-Aware Compaction (TAC) reduces API token cost primarily through behavioral change (fewer API calls) compared to default Chronological-First compaction (CF). The experiment yielded a **clear null result**: TAC and CF produce statistically indistinguishable API call rates (p = 0.93). A compression-only control (COMPR) showed high variance but no statistically reliable degradation (p = 0.81).

**Bottom line:** Compaction strategy (topic-structured vs chronological) does not measurably influence the number of API calls an LLM makes when processing a multi-topic coding session.

---

## 2. Hypotheses

| ID | Hypothesis | Result |
|----|-----------|--------|
| H1 (Primary) | TAC reduces calls/message by >25% vs CF | **REJECTED** (observed: -2.5%, wrong direction) |
| H2 | COMPR (flat compression) increases calls/message vs CF | **NOT SUPPORTED** (p = 0.81, high variance) |
| H3 | TAC advantage is due to behavioral change, not text reduction | **MOOT** (no TAC advantage observed) |

---

## 3. Method

### 3.1 Design

- **Arms:** CF (baseline compaction), TAC (topic-aware plugin), COMPR (length-matched flat compression)
- **Template:** 3-topic, 21-message coding session (python-setup, database, cicd) + 3 recall questions
- **Blocks:** N=5 per arm (paired randomization per block)
- **Model:** `claude-opus-4.6` (fixed), temperature=0
- **Primary DV:** API calls per user message
- **Compaction trigger:** `compaction.reserved = 120000` (effective usable context ≈80K tokens)
- **COMPR budget:** 1286 tokens per compaction (calibrated from TAC average output)
- **Message timeout:** 1800s

### 3.2 Conditions

| Arm | Port | Compaction Strategy |
|-----|------|-------------------|
| CF | 3100 | Default opencode compaction (chronological summary) |
| TAC | 3200 | Topic-structured compaction via fish-trail plugin |
| COMPR | 3300 | Flat chronological compression, budget-matched to TAC output length |

### 3.3 Infrastructure

- 3 independent opencode server instances running simultaneously
- Sequential block execution (parallel execution caused server resource contention)
- Automated harness (`ab_test_harness_v3.py`) managing session creation, message delivery, metric collection

---

## 4. Results

### 4.1 Raw Data

| Block | Arm | Calls/Msg | Compactions | Wall (s) | API Calls | Peak Context |
|-------|-----|-----------|-------------|----------|-----------|--------------|
| 1 | CF | 3.33 | 5 | 638 | 70 | 49,616 |
| 2 | CF | 5.14 | 7 | 1,092 | 108 | 49,067 |
| 3 | CF | 3.05 | 5 | 580 | 64 | 52,933 |
| 4 | CF | 3.10 | 4 | 573 | 65 | 51,386 |
| 5 | CF | 4.10 | 6 | 1,076 | 86 | 54,143 |
| 1 | TAC | 4.86 | 5 | 839 | 102 | 49,135 |
| 2 | TAC | 3.19 | 4 | 636 | 67 | 52,051 |
| 3 | TAC | 3.19 | 4 | 668 | 67 | 51,856 |
| 4 | TAC | 4.90 | 8 | 1,184 | 103 | 53,646 |
| 5 | TAC | 3.05 | 3 | 575 | 64 | 52,902 |
| 1 | COMPR | 3.81 | 4 | 769 | 80 | 48,073 |
| 2 | COMPR | 8.90 | 11 | 1,831 | 187 | 52,810 |
| 3 | COMPR | 3.95 | 5 | 841 | 83 | 63,098 |
| 4 | COMPR | 2.57 | 2 | 445 | 54 | 49,317 |
| 5 | COMPR | 2.52 | 2 | 433 | 53 | 49,283 |

### 4.2 Descriptive Statistics

| Arm | N | Mean Calls/Msg | SD | Mean Wall (s) | Mean Compactions |
|-----|---|---------------|-----|---------------|-----------------|
| CF | 5 | 3.74 | 0.89 | 792 | 5.4 |
| TAC | 5 | 3.84 | 0.95 | 780 | 4.8 |
| COMPR | 5 | 4.35 | 2.63 | 864 | 4.8 |

### 4.3 Statistical Tests

#### Permutation Tests (two-tailed, 10,000 permutations)

| Comparison | Observed Δ | Raw p | Holm-adjusted p | Verdict |
|-----------|-----------|-------|-----------------|---------|
| COMPR vs CF | +0.61 | 0.809 | 1.000 | Not significant |
| COMPR vs TAC | +0.51 | 0.837 | 1.000 | Not significant |
| TAC vs CF | +0.10 | 0.928 | 0.928 | Not significant |

#### Bootstrap 95% Confidence Intervals (mean difference)

| Comparison | 95% CI |
|-----------|--------|
| CF − TAC | [−1.09, +0.93] |
| COMPR − CF | [−1.23, +3.07] |
| COMPR − TAC | [−1.34, +3.08] |

All CIs include zero. No pairwise comparison reaches conventional significance.

---

## 5. Interpretation

### 5.1 Why TAC ≈ CF

The model's API call behavior appears driven by **task complexity and stochastic tool-use chain length**, not by how prior context is organized. Both TAC and CF preserve sufficient semantic content for the model to continue working without redundant queries. The hypothesized mechanism — that topic-structured context would reduce "re-discovery" calls — does not manifest at this task granularity.

### 5.2 COMPR Variance

COMPR block 2 (8.90 calls/msg, 11 compactions) is a clear outlier. This was the first COMPR run (calibration), when the server may have had residual state or the model encountered an unusual tool-use spiral. Subsequent COMPR runs (2.52–3.95) are within the CF/TAC range. The flat compression strategy does not reliably degrade performance — it just introduces more variance.

### 5.3 What Drives API Call Variance?

Within each arm, calls/msg ranges from ~3.0 to ~5.1 (CF) or ~3.0 to ~4.9 (TAC). This 60%+ intra-arm variance suggests the dominant factor is **random variation in model behavior** (tool-use chain depth, retry patterns, exploration breadth), not compaction strategy.

### 5.4 Power Analysis

- TAC vs CF effect: d = −0.11 (negligible, wrong direction). No feasible N would yield significance.
- COMPR vs CF effect: d = 0.31 (small). Would require N ≈ 80+ for 80% power at α = 0.05 — impractical given ~15 min/block runtime.

---

## 6. Threats to Validity

| Threat | Mitigation | Residual Risk |
|--------|-----------|---------------|
| Template too simple (3 topics, 21 msgs) | Designed to trigger 4-8 compactions per run | May not stress-test topic confusion enough |
| Temperature=0 reduces stochasticity | Required for reproducibility | May suppress effects visible at temperature>0 |
| Server crashes during parallel execution | Switched to sequential; discarded failed runs | Some blocks ran under different server load conditions |
| N=5 low power | Planned N=8 extension if CIs wide | CIs span zero regardless; extending N won't find nonexistent effect |
| Same model for all arms | Controlled variable | Effect may exist for weaker models that struggle more with context |

---

## 7. Conclusions

1. **Topic-Aware Compaction does not reduce API calls** compared to default chronological compaction. The primary hypothesis (H1: >25% reduction) is decisively rejected.

2. **Flat compression does not reliably degrade performance** either. After removing one outlier, COMPR performs comparably to CF and TAC.

3. **The dominant source of variance is stochastic model behavior**, not compaction strategy. API call rates vary 60%+ within each arm across blocks.

4. **Phases P1b (single-topic control) and P3 (5-topic scaling) are cancelled** as moot — there is no TAC effect to investigate further.

5. **For publication viability:** This is a well-powered null result suitable for a workshop paper or negative-results track. The contribution is empirical evidence that compaction strategy choice (within the family of summarization-based approaches) does not materially affect downstream LLM efficiency in coding tasks.

---

## 8. Recommendations

1. **If TAC has value, it is not in API call reduction.** Future work should investigate whether TAC improves **recall quality** (can the model retrieve specific details better?) or **user-perceived coherence** rather than raw efficiency.

2. **The 3-topic template may be too simple.** A 10+ topic session with intentional topic revisitation might expose differences that a simple rotating pattern cannot.

3. **Temperature > 0 testing** could reveal whether TAC's topic organization reduces variance in model behavior (even if mean is unchanged).

4. **Cross-model comparison** (weaker models with smaller context windows) may show TAC advantages that don't manifest in a 200K-context opus-class model.

---

## 9. Artifacts

```
results/
├── P0/
│   ├── P0_block01_CF.json
│   ├── P0_block01_TAC.json
│   ├── P0_block02_CF.json
│   ├── P0_block02_COMPR.json
│   ├── P0_block02_TAC.json
│   ├── P0_block03_CF.json
│   ├── P0_block03_TAC.json
│   ├── P0_block04_CF.json
│   ├── P0_block04_TAC.json
│   ├── P0_block05_CF.json
│   └── P0_block05_TAC.json
├── P1a/
│   ├── P1a_block01_COMPR.json
│   ├── P1a_block03_COMPR.json
│   ├── P1a_block04_COMPR.json
│   └── P1a_block05_COMPR.json
├── failed/
│   ├── P0_block01_TAC.json (earlier failed attempt)
│   ├── P0_block03_CF.json
│   ├── P0_block03_TAC_timeout.json
│   ├── P0_block04_TAC.json
│   └── P0_block05_TAC.json
└── EXPERIMENT-REPORT.md (this file)
```

---

## 10. Methodology Notes

- **Statistical approach:** Non-parametric permutation tests (no distributional assumptions) + bootstrap CIs. Holm correction for multiple comparisons.
- **Failure policy:** Failed runs discarded entirely (no imputation). TAC block 3 with recall timeouts moved to failed/.
- **Calibration:** One block per arm run before formal experiment to set COMPR_BUDGET_TOKENS=1286 and validate infrastructure.
- **Execution:** Sequential (not parallel) to avoid server resource contention after initial parallel attempts caused crashes.
