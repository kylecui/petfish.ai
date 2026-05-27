# Paper: Topic-Aware Compaction

**Target**: COLM 2026 (backup: EMNLP 2026 Findings)

## Directory Structure

```
07_paper/
├── data/
│   ├── experiment-1-sysprompt/     # 3-way system-prompt injection test
│   │   ├── raw-data/               # 4 JSON files (round1/round2, original/clean)
│   │   ├── PAPER.md                # 161-line draft for Exp 1
│   │   └── REPORT.md               # 400-line test report
│   └── experiment-2-fishtrial-ab/  # fish-trail A/B test (N=21, 3 topics)
│       ├── ab_test_results.json    # Raw JSON results
│       └── ANALYSIS.md             # 810-line detailed analysis
├── scripts/
│   ├── ab_test_harness.py          # Original test automation (Exp 1)
│   ├── ab_test_harness_v2.py       # Updated harness (Exp 2)
│   └── setup_ab_test.py            # Environment setup
├── drafts/
│   ├── paper-plan.md               # Section outline and narrative
│   ├── experiment-design.md        # 7 ablation experiments designed
│   ├── related-work-draft.md       # Related work section
│   ├── bibliography.md             # References
│   └── writing-guide.md            # Style and formatting notes
└── figures/                        # (empty — to be populated)
```

## Key Results

| Metric | Experiment 1 (sysprompt) | Experiment 2 (fish-trail A/B) |
|--------|--------------------------|-------------------------------|
| Token savings | -19.1% (all-rules) | -20.3% |
| API calls | — | 4.2 vs 6.7 per message (-36.4%) |
| Cache reads | — | -49.9% |
| Wall time | — | -39.4% |
| Quality loss | None measured | Zero recall loss |
| Model | claude-sonnet-4 | claude-sonnet-4 |
| N | 2 rounds | 21 messages, 3 interleaved topics |

## Core Thesis

> Behavioral change is the primary token-saving mechanism, not text compression.

The agent makes fewer API calls and produces more focused responses when context is structured by topic rather than chronology.

## Next Steps

1. Run ablation experiments (priority: #1 compression-only, #4 single-topic control, #6 model variation)
2. Write complete paper draft
3. Generate figures from existing data
