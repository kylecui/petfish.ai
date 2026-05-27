# PEtFiSh Fish-Trail Performance Evaluation Handoff Package

> Generated: 2026-05-25
> Source: kylecui/petfish_tester + kylecui/petfish.ai

## Quick Start

1. Read `reports/00-COMPLETE-HISTORY.md` — this is the master document covering all 6 phases
2. Dive into phase-specific reports as needed (numbered 01-21)
3. Raw data in `data/` (JSON), scripts in `benchmark-scripts/`
4. Issue tracker in `issues/ISSUE-TRACKER.md`

## Package Structure

```
├── README.md                           (this file)
├── reports/
│   ├── 00-COMPLETE-HISTORY.md          (master document, all phases)
│   ├── 01~03  Phase 1: Compaction
│   ├── 04~06  Phase 1: TAC formal test + recall
│   ├── 07~09  Phase 2: v0.11.0 upgrade
│   ├── 10      Phase 3: System prompt plugin
│   ├── 11~18  Phase 4: Multi-model + disk mode
│   ├── 19      Phase 5: Memory architecture research
│   ├── 20~21  Phase 6: v1.1.0-pre benchmarks
├── data/
│   ├── membench-v2-results.json        (100 entries, DeepSeek Pro)
│   ├── membench-v3-results.json        (210 entries, 5 models)
│   ├── membench-v4-results.json        (270 entries, 3 models × 3 arms)
│   ├── membench-v4-results.jsonl       (same, line-delimited)
│   ├── disk-quality-regression.json    (disk mode quality data)
│   ├── quality-eval-unblinded.json     (LLM-as-judge scores)
│   └── quality-eval-judgments.json     (raw judgment data)
├── research/
│   ├── optimization-evaluation-report.md  (24-source methodology report)
│   ├── research-brief.md                  (research brief)
│   ├── source-index.jsonl                 (24 sources indexed)
│   └── llm-memory-findings.json           (15-source literature survey)
├── benchmark-scripts/
│   ├── membench_v3.py                 (v3 multi-model runner)
│   └── membench_v4.py                 (v4 compression ablation runner)
└── issues/
    └── ISSUE-TRACKER.md               (all issues filed)
```

## Key Numbers at a Glance

| What | Result | Phase |
|------|--------|-------|
| Compaction plugin | **Null result** (p=0.928) | 1 |
| v0.11.0 regression | +36.6% tokens | 2 |
| System prompt plugin | **-19.1% tokens** | 3 |
| Disk mode quality | **98/100** | 4 |
| Claude disk-full | **-7.7% tokens, best recall** | 6 |
| Flash disk-v2 | -8.7% tokens, -23.4% recall | 6 |
| GPT-Mini disk-v2 | -17.1% tokens, -11.1% recall | 6 |

## Models Tested

- DeepSeek V4 Pro (production target)
- DeepSeek V4 Flash
- Claude Sonnet 4.6 (via GitHub Copilot)
- GPT-5.4-Mini (via OpenAI)
- GPT-4o (partial — zero tokens bug)
- Gemini 3 Flash (compaction phase only)
- Claude Opus 4.6 (compaction phase only)
