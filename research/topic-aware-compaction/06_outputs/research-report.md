# Research Report: Topic-Aware Compaction

> **Research ID**: TAC-2026-001  
> **Research Type**: Product Research  
> **Date**: 2026-05-11  
> **Status**: Complete  
> **Brief**: `../00_brief/research-brief.md`  
> **Evidence Ledger**: `../03_evidence/evidence-ledger.jsonl` (17 entries)  
> **Synthesis**: `../05_analysis/synthesis.md`

---

## Executive Summary

This research investigated whether fish-trail's topic management can enhance OpenCode's compaction mechanism to save tokens in multi-topic sessions. The answer is **yes** — a Phase 2 plugin achieved **20.3% total token savings with zero recall quality loss**, validated through controlled A/B testing.

The critical finding was unexpected: the primary savings mechanism is not summary compression but **behavioral change**. Topic-structured compaction causes the model to produce more focused, consolidated responses with fewer intermediate tool-call chains, reducing API calls by 36.4% and wall time by 39.4%.

Phase 3 (skip-LLM compaction) was shelved because it cannot replicate this behavioral mechanism.

---

## 1. Research Questions & Answers

### SQ1: Integration Feasibility — ✅ Fully Feasible

OpenCode's `experimental.session.compacting` plugin hook provides complete integration surface:

- **`output.context[]`** — push additional context into compaction prompt (Phase 1)
- **`output.prompt`** — replace the entire compaction prompt (Phase 2)
- **Auto-discovery** — plugins in `.opencode/plugin/` are loaded automatically

Three key assumptions verified via source code analysis (E001-E005). 11+ external projects already use the same hook in production (E013).

### SQ2: Token Savings — 20.3% Total, 39.4% Wall Time

A/B test results (21 messages, 3 interleaved topics, `claude-sonnet-4`):

| Metric | Baseline | Plugin | Delta |
|--------|----------|--------|-------|
| Total tokens (in+out) | 857,115 | 683,522 | **-20.3%** |
| Input tokens | 726,474 | 576,050 | **-20.7%** |
| Output tokens | 130,641 | 107,472 | **-17.7%** |
| Cache reads | 10,631,340 | 5,330,527 | **-49.9%** |
| API calls | 140 | 89 | **-36.4%** |
| Wall time | 2,938s (49min) | 1,781s (30min) | **-39.4%** |
| Compactions | 2 | 2 | same |
| Errors | 1 timeout | 0 | ✓ |

The 20.3% token reduction is lower than the initial 60% estimate, but the compound effect (fewer API calls → less cache → faster wall time) delivers greater practical value.

### SQ3: Context Quality — No Degradation

Recall questions across all 3 topics showed accurate responses in both baseline and plugin runs. The plugin produced slightly more concise answers without losing factual accuracy. No quality loss detected (E017).

### SQ4: Implementation Path — Two-Phase Validated, Phase 3 Shelved

| Phase | Strategy | Status | Result |
|-------|----------|--------|--------|
| 1 (MVP) | Inject topic Context Package via `output.context[]` | ✅ Complete | Safe, marginal benefit |
| 2 | Topic-structured prompt via `output.prompt` | ✅ Complete | 20.3% savings, zero quality loss |
| 3 | Pre-computed summaries, skip LLM | 🚫 Shelved | Cannot replicate behavioral mechanism |

Phase 3 was shelved because Phase 2's savings come from the model's behavioral change (producing focused responses), not from compression ratio. A pre-computed summary cannot trigger this behavioral change — it would bypass the LLM's contextual understanding during compaction.

### SQ5: Boundary Conditions

Topic-aware compaction shows **reduced benefit** in:

- **Single-topic sessions** — no multi-topic separation benefit
- **Blurry topic boundaries** — forced separation may create artificial fragmentation
- **Stale topic summaries** — if Companion Gateway or MCP is offline, topic data may be outdated

These are not failure modes — the plugin degrades gracefully (silent skip on any error).

---

## 2. Key Findings

| # | Finding | Confidence | Evidence |
|---|---------|------------|---------|
| F1 | OpenCode plugin hook provides complete compaction integration surface | 1.0 | E001-E005 |
| F2 | Phase 2 saves 20.3% total tokens with zero quality loss | 1.0 | E015-E017 |
| F3 | Primary savings mechanism is behavioral (fewer API calls), not compression | 0.90 | E016 |
| F4 | Phase 3 cannot replicate the behavioral mechanism — shelved | 0.85 | E010, E016 |
| F5 | fish-trail's existing data model (topics, summaries, Context Package) is directly reusable | 0.90 | E007-E008 |
| F6 | 11+ external projects validate hook API stability | 0.90 | E013 |
| F7 | API call reduction (4.2/msg vs 6.7/msg) compounds into 50% cache savings and 39% time savings | 1.0 | E015 |

---

## 3. Deliverables

### Plugin (Production-Ready)

`.opencode/plugin/fish-trail-compaction.ts` — Phase 2 plugin that:

1. Reads active topic from `.petfish/fish-trail/topic-registry.json`
2. Reads all topics and builds a topic-structured compaction prompt
3. Sets `output.prompt` with per-topic compression priorities
4. Degrades gracefully on any error (silent skip, never blocks compaction)

### A/B Test Infrastructure

`research/topic-aware-compaction/06_outputs/ab_test_harness.py` — automated test harness that:

- Runs baseline vs plugin sessions against OpenCode Server API
- 21 messages across 3 interleaved topics + 3 recall questions
- Tracks per-message token usage, peak context window, compaction events
- Produces JSON results with full token breakdowns
- Configurable timeouts, failure thresholds, model selection

---

## 4. Recommendations

1. **Ship Phase 2 plugin with fish-trail pack** — A/B test validates safety and effectiveness. Include as an optional component users can enable.
2. **Consider `chat.system.transform` hook** — injecting lightweight topic awareness into every conversation (not just compaction) may provide additional value.
3. **Revisit Phase 3 only with new evidence** — if future testing on larger sessions (50+ messages, 5+ topics) shows compression ratio becomes dominant over behavioral change, Phase 3 may become relevant.
4. **Automate future A/B testing** — the harness supports this. Two separated folders with two OpenCode instances (plugin enabled vs disabled) for automated comparison.

---

## 5. Method & Limitations

### Method

1. Source code analysis of OpenCode compaction (SHA `2f11c9f7`)
2. Data model mapping (fish-trail → compaction requirements)
3. Phase 1 prototype → manual validation
4. Phase 2 prototype → controlled A/B test (21 messages, 3 topics, `claude-sonnet-4`)

### Limitations

- **Single model tested** — only `claude-sonnet-4`. Results may differ with other models.
- **Single session size** — 21 messages. Larger sessions may show different savings patterns.
- **No multi-user concurrency** — active topic is global state. Multi-window scenarios untested.
- **OpenCode hook is `experimental`** — API may change in future versions (though 11+ external users suggest stability).

---

## Evidence Traceability

| Claim | Evidence IDs |
|-------|-------------|
| Hook interface signatures | E001 |
| context[] injection path | E002 |
| prompt replacement mechanism | E003 |
| Plugin mutation pattern | E004 |
| Auto-discovery registration | E005 |
| Engram reference implementation | E006 |
| Existing Claude Code hooks | E007 |
| Context Package generation | E008 |
| SessionID mapping gap | E009 |
| Phase 3 design correction | E010 |
| Compaction trigger mechanism | E011 |
| Default template structure | E012 |
| Ecosystem maturity | E013 |
| Auxiliary hooks | E014 |
| Phase 2 token savings quantification | E015 |
| Phase 2 behavioral change mechanism | E016 |
| Phase 2 recall quality preservation | E017 |

---

## Research Artifacts

```
research/topic-aware-compaction/
├── 00_brief/
│   ├── research-brief.md
│   ├── research-questions.md
│   └── scope-boundaries.md
├── 01_sources/
│   └── source-discovery.md
├── 03_evidence/
│   ├── evidence-ledger.jsonl          # 17 entries (E001-E017)
│   └── latests_from_tester/
│       ├── ANALYSIS.md                # Detailed A/B analysis
│       └── ab_test_results.json       # Raw test data
├── 05_analysis/
│   └── synthesis.md                   # Full synthesis with design matrices
└── 06_outputs/
    ├── research-report.md             # This document
    ├── ab_test_harness.py             # Automated A/B test harness
    ├── setup_ab_test.py               # Test directory setup
    └── AB_TEST_GUIDE.md               # How to run tests
```
