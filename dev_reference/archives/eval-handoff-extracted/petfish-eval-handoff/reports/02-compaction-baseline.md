# Test Results - Round A (Baseline)

**Date**: 2026-05-10
**Plugin**: DISABLED
**LLM Model**: claude-opus-4.6 (github-copilot/claude-opus-4.6)
**Compaction triggered at turn**: ~6-7 (between installer failure modes discussion and first recall test)

## Scores

- Recall Score (topic detection details after compaction): 5/5
- Topic Separation Score: 4/5

## Compaction Summary (verbatim)

> **Note**: Compaction produced a structured summary that was available as context at the start of the post-compaction turns. The "What is your current understanding" response (Turn 9 post-compaction) reproduced the following:
>
> The session covered two PEtFiSh subsystems in analyze-mode:
>
> **Topic 1: Fish-Trail `topic_detect` Algorithm** (4 rounds, fully completed):
> - Architecture: Two-tier rule-based detector in `topic_detector.py` (661 lines)
> - Signal cascade: reset → archive → switch → merge → fork → bridge → drift → continue
> - Tier 1: Keyword Jaccard with CJK bigram decomposition, asymmetric formula `|intersection| / |meaningful_input|`, thresholds ≥0.10 on-topic, >0 <0.10 ambiguous, =0.0 drift
> - Tier 2: ONNX embedding (`paraphrase-multilingual-MiniLM-L12-v2`, int8, 384-dim, mean pooling + L2 normalize, cosine via dot product), only invoked in ambiguous zone
> - Bilingual expansion: 50+ term CN↔EN dictionary, used only in drift detection
> - Static risk profile: continue=0, archive=10, fork=30, bridge=35, reset=40, switch=40, merge=50. Drift override 35-45
> - Risk bands: 0-30 low, 31-60 medium, 61-100 high. topic_detect max=50, only contamination_score can reach high
> - Contamination scoring: 5 dimensions (topic_distance, goal_conflict, term_overloading, output_format_divergence, history_bias) × 0-20 each
> - Concrete example: "帮我研究一下竞品分析" against "deployment automation" → zero keyword overlap after bilingual expansion → relevance=0.0 → drift → fork risk 35-45
> - Server side effects: switch auto-updates active topic, archive/reset auto-close session
>
> **Topic 2: PEtFiSh Installer (`remote-install.sh`)** (3 rounds, fully completed):
> - 6-phase flow: uv bootstrap → release tag resolution → pack alias resolution (11 packs) → tarball download → platform resolution (8 platforms via platforms.json) → per-pack install loop
> - Platform detection: marker-file scanning in priority order, fallback to "universal"
> - AGENTS.md merge: marker-based idempotent sections (`<!-- BEGIN/END pack: name -->`), 4 outcomes (created/merged/updated/exists), legacy name migration
> - opencode.json merge: deep merge with atomic L2 for MCP entries
> - Version management: semver comparison, auto-upgrade on newer
> - Failure modes: silent release tag fallback, fatal tarball/SSL errors with no diagnostic, unhandled JSON corruption on registry (except .claude/settings.json), race conditions on concurrent installs
>
> Files read: topic_detector.py, embeddings.py, contamination_scorer.py, server.py, SKILL.md, contamination-scoring.md, installed-packs.json, check_installed.py, remote-install.sh (full via two fetches)

## Recall Test Response (verbatim)

> The "Summarize everything we discussed about topic detection specifically" response (Turn 10) included:
>
> - Full architecture description (two-tier rule-based detector)
> - Signal cascade order (all 8 types)
> - Complete Tier 1 explanation with exact formula and all three thresholds (≥0.10, >0<0.10, =0.0)
> - Complete Tier 2 explanation with model name, quantization, dimensions, pooling method
> - Bilingual expansion details with the "only in drift detection" caveat
> - Full static risk profile table (all 7 relation types with exact scores)
> - Risk band numbers (0-30, 31-60, 61-100) and the "cannot reach high" finding
> - All 5 contamination dimensions with descriptions
> - Complete concrete example walkthrough (all 6 steps)
> - Server-side side effects

## Deep Recall Test Response (verbatim)

> The deep recall test (Turn 11) reproduced:
>
> - All 7 static risk scores exactly (continue=0, archive=10, fork=30, bridge=35, reset=40, switch=40, merge=50, drift=35-45)
> - All 3 risk band ranges exactly
> - The complete 6-step concrete example trace: signal cascade fallthrough → token extraction (["研究", "竞品", "分析"]) → bilingual expansion with specific terms → zero intersection → relevance=0.0 → Tier 2 not invoked → fork with risk 35-45

## Token Usage (from provider dashboard)

- Input tokens: [TODO — fill from Anthropic/OpenAI dashboard]
- Output tokens: [TODO — fill from Anthropic/OpenAI dashboard]
- Total API calls: [TODO — fill from provider dashboard]

## Message count: ~20 (11 user turns + assistant responses, including post-compaction recall tests)

## Notes

- **Recall quality was excellent post-compaction**: All exact numbers, model names, and the concrete example were preserved with full fidelity. This is likely because the compaction summary was very detailed and structured.
- **Topic separation was good but not perfect (4/5)**: The compaction summary clearly separated the two topics, but the installer analysis (Topic 2) was marked as "partially analyzed" in the summary even though all 3 rounds had been delivered by compaction time. The summary noted "analysis NOT yet delivered to user" for the installer walkthrough, which was inaccurate — it had been delivered but compaction may have occurred mid-conversation before that context was fully captured.
- **No data loss on specific numbers**: Every threshold, dimension name, model parameter, and risk score was accurately recalled. The structured format of the original analysis (tables, numbered lists) likely helped compaction preserve details.
- **Bilingual example survived intact**: The Chinese input "帮我研究一下竞品分析" and its full trace through the algorithm were preserved with correct token decomposition and expansion terms.
- **Compaction did not blur the two topics**: Responses about topic detection did not accidentally include installer details, and vice versa. The marker-based structure in the compaction summary may have helped maintain this boundary.
- **Potential confound**: The model (claude-opus-4.6) may have high inherent recall capability that masks compaction quality differences. Round B comparison will be needed to assess plugin impact.
