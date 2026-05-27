# Test Results - Round B (Plugin Enabled)

**Date**: 2026-05-10
**Plugin**: ENABLED
**Active Topic**: `topic_20260510_53e8` — "Fish-trail topic detection algorithm"
**LLM Model**: claude-opus-4.6 (github-copilot/claude-opus-4.6)
**Compaction triggered at turn**: ~6-7 (between installer analysis completion and first recall test)

## Scores

- Recall Score (topic detection details after compaction): 5/5
- Topic Separation Score: 5/5

## Compaction Summary (verbatim)

> The compaction summary was delivered as a structured document at the start of the post-compaction turns. The "What is your current understanding" response reproduced the following:
>
> The session covered two PEtFiSh subsystems in analyze-mode:
>
> **Topic A: Fish-Trail `topic_detect` Algorithm** (fully completed):
> - Architecture: Two-tier rule-based detector in `topic_detector.py` (661 lines)
> - Signal cascade: reset → archive → switch → merge → fork → bridge → drift → continue
> - Tier 1: Keyword Jaccard with CJK bigram decomposition, asymmetric formula `|intersection| / |meaningful_input|`, thresholds ≥0.10 on-topic, >0 <0.10 ambiguous, =0.0 drift
> - Tier 2: ONNX embedding (`paraphrase-multilingual-MiniLM-L12-v2`, int8, 384-dim, mean pooling + L2 normalize, cosine via dot product), only invoked in ambiguous zone (0 < relevance < 0.10)
> - Bilingual expansion: 50+ term CN↔EN dictionary, 8 synonym groups, plural stemming, used only in drift detection
> - Static risk profile: continue=0, archive=10, fork=30, bridge=35, reset=40, switch=40, merge=50, drift=35-45
> - Risk bands: 0-30 low, 31-60 medium, 61-100 high. topic_detect max=50, only contamination_score can reach high
> - Contamination scoring: 5 dimensions (topic_distance, goal_conflict, term_overloading, output_format_divergence, history_bias) × 0-20 each
> - Escalation path: topic_detect (max medium) → optional contamination_score → if ≥61 high → full SKILL.md workflow
> - Concrete example: "帮我研究一下竞品分析" against "deployment automation" → zero keyword overlap → relevance=0.0 → drift → fork, confidence 0.65, risk 45, medium
> - Server side effects: switch auto-updates active topic, archive/reset auto-close session
>
> **Topic B: PEtFiSh Installer (`remote-install.sh`)** (fully completed):
> - 6-phase flow: uv bootstrap → release tag resolution → pack alias resolution (11 packs, 21 aliases) → tarball download → platform resolution (8 platforms via platforms.json) → per-pack install loop
> - Platform detection: marker-file scanning in priority order (opencode → claude → codex → cursor → copilot → windsurf → antigravity), fallback to "universal"
> - platforms.json schema: 8 platform definitions with project/global paths, detect_markers, merge strategies, translation configs, condensation budgets, platform_groups
> - Packs are platform-agnostic: all ship in OpenCode layout, installer remaps at install time
> - AGENTS.md merge: marker-based idempotent sections (`<!-- BEGIN/END pack: name -->`), 4 outcomes (created/merged/updated/exists), legacy name migration
> - opencode.json merge: deep merge with atomic L2 for MCP entries
> - Version management: semver comparison, auto-upgrade on newer, legacy_names lookup
> - --force: 3 levels (version bypass, AGENTS.md section replace, destructive file copy)
> - Failure modes: silent release tag fallback, fatal tarball errors, corrupted registry crash (files installed but registry broken), 4 race condition surfaces (registry, AGENTS.md, skill dirs, opencode.json) with no locking
>
> **Supporting: petfish-companion** check_installed.py (406 lines): registry lookup across 8 platforms, semver comparison, update checking
>
> Files read: topic_detector.py, contamination_scorer.py, embeddings.py, server.py, SKILL.md, contamination-scoring.md, topic-model.md, remote-install.sh (full 1384 lines via gh API), platforms.json, pack-manifest.json (fish-trail sample), check_installed.py, petfish-companion/SKILL.md (partial), test-results-A.md

## Recall Test Response (verbatim)

> The "Summarize everything we discussed about topic detection specifically" response reproduced:
>
> - Full architecture description (two-tier rule-based detector, 661 lines)
> - Signal cascade order (all 8 types in correct priority order)
> - Complete Tier 1 explanation with exact formula (`|intersection| / |meaningful_input|`), CJK bigram decomposition, and all three threshold zones (≥0.10, >0 <0.10, =0.0)
> - Complete Tier 2 explanation with model name, quantization type, dimensions, pooling method, similarity computation method
> - Narrow invocation constraint (only 0 < relevance < 0.10, not at exactly 0)
> - Bilingual expansion details (50+ pairs, 8 synonym groups, plural stemming) with "only in drift detection" caveat
> - Full static risk profile table (all 7 relation types + drift with exact scores)
> - Risk band numbers (0-30, 31-60, 61-100) and the "cannot reach high" finding
> - All 5 contamination dimensions with names
> - Complete escalation path (topic_detect → contamination_score → SKILL.md workflow)
> - Server side effects (switch auto-update, archive/reset auto-close)
> - Complete concrete example walkthrough (all 6 steps with correct values)

## Deep Recall Test Response (verbatim)

> The deep recall test reproduced:
>
> - All 7 static risk scores exactly (continue=0, archive=10, fork=30, bridge=35, reset=40, switch=40, merge=50, drift=35-45)
> - All 3 risk band ranges exactly (≤30, 31-60, 61-100)
> - The "maxes at 50, only contamination_score can reach high" finding
> - The complete 6-step concrete example trace:
>   1. Signal cascade fallthrough (no trigger phrases)
>   2. Token extraction: ["研究", "竞品", "分析"]
>   3. Bilingual expansion of topic keywords — zero overlap ("竞品"/"分析" not in map)
>   4. Relevance = 0.0 → drift
>   5. Tier 2 not invoked (only fires when 0 < relevance < 0.10, not at exactly 0)
>   6. Result: fork, confidence 0.65, risk 45, risk_level medium

## Token Usage (from provider dashboard)

- Input tokens: [TODO — fill from Anthropic/OpenAI dashboard]
- Output tokens: [TODO — fill from Anthropic/OpenAI dashboard]
- Total API calls: [TODO — fill from provider dashboard]

## Message count: ~18 (9 user turns + assistant responses, including post-compaction recall tests)

## Notes

- **Recall quality was excellent post-compaction (5/5)**: All exact numbers, model names, formula, thresholds, and the concrete example were preserved with full fidelity. Every risk score, every dimension name, every constraint (like "Tier 2 only fires in ambiguous zone") was accurately recalled.
- **Topic separation was perfect (5/5)**: Responses about topic detection never included installer details and vice versa. The two topics were cleanly separated in both the comprehensive summary and the targeted recall tests. Unlike Round A (4/5), no status confusion about which topics were "delivered" vs "pending" — the compaction correctly reflected both topics as fully completed.
- **Compared to Round A**: Round A scored 5/5 recall and 4/5 separation. Round B scored 5/5 on both. The improvement in topic separation may be attributable to the plugin's topic-aware context injection providing clearer topic boundaries during compaction, though the sample size (n=1 per condition) is too small for statistical confidence.
- **No data loss on specific numbers**: Every threshold, dimension name, model parameter, risk score, and formula was accurately recalled — identical to Round A performance.
- **Bilingual example survived intact**: The Chinese input "帮我研究一下竞品分析" and its full trace through the algorithm were preserved with correct token decomposition.
- **Installer analysis (Topic B) was significantly expanded in Round B**: Unlike Round A (which covered 6-phase flow at high level), Round B additionally analyzed platforms.json schema in full, --force interaction at 3 levels, AGENTS.md merge strategy (4 outcomes with decision tree), and a comprehensive failure mode analysis (6 failure types + 4 race conditions). All of this additional detail survived compaction.
- **Plugin behavior**: The fish-trail context-state MCP was available during this session. The compaction summary was structured and comprehensive, preserving fine-grained technical details. Whether this is due to the plugin or the model's inherent capability remains an open question requiring more controlled testing.
- **Potential confound**: Same as Round A — claude-opus-4.6 may have high inherent recall capability. The plugin's marginal contribution is hard to isolate without more rounds or a different model.
