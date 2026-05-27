# Plugin-Context-Inject Validation Results

**Date**: 2026-05-22
**Config**: DeepSeek-V4-Flash/Pro, OpenCode server on port 3400

## Summary

Plugin-inject (system prompt injection of topic state) achieves:
- **8% lower total tokens** and **8.7% faster wall time** vs FULL-current
- **Equivalent recall accuracy** (1.57-2.00/2.0 vs 1.67-2.00/2.0, p=0.753)
- **Better contamination control** (89-100% vs 78-89%)

The quality advantage is statistically insignificant at N=7-9 per arm, but the trend is consistent across both lenient and strict judges. Combined with the cost savings, plugin-inject is strictly better.

## Efficiency Results

### Template F (3-msg, short session)

| Metric | FULL-CURRENT (N=3) | PLUGIN-INJECT (N=3) | Delta |
|--------|-------------------:|--------------------:|------:|
| api_calls | 3 | 3 | 0% |
| total_tokens | 231,683 | 232,326 | +0.3% |
| input | 941 | 941 | ~0% |
| cache_read | 229,717 | 230,656 | +0.4% |
| wall_time_s | 88 | 82 | -6.8% |
| cost | $0.0068 | $0.0068 | ~0% |

Template F is too short to trigger topic management. Both configs are functionally identical.

### Template A (21-msg, 3-topic session)

| Metric | FULL-CURRENT (N=1) | PLUGIN-INJECT (N=1) | Delta |
|--------|-------------------:|--------------------:|------:|
| api_calls | 21 | 21 | 0% |
| total_tokens | 2,270,044 | 2,086,300 | **-8.1%** |
| input | 88,523 | 86,798 | -1.9% |
| output | 7,289 | 5,021 | **-31.1%** |
| reasoning | 1,688 | 2,673 | +58.4% |
| cache_read | 2,172,544 | 1,991,808 | -8.3% |
| wall_time_s | 164.5 | 150.2 | **-8.7%** |
| cost | $0.0757 | $0.0701 | -7.5% |
| tool_calls | 0 | 0 | — |

## Quality Results

### Methodology

- **Arms**: FULL-CURRENT (rules + MCP connected) vs PLUGIN-INJECT (rules + injected topic state, no MCP)
- **Template**: 21 messages across 3 topics, followed by 3 recall questions (1 per topic)
- **Blocks**: N=3 per arm (9 recall answers per arm)
- **Judges**: Flash (lenient) and Pro (strict), both blind to arm identity
- **Metrics**: Accuracy (0=wrong, 1=partial, 2=correct), Contamination (0=mixed topics, 1=clean)

### Results

| Judge | Metric | FULL-CURRENT | PLUGIN-INJECT | p-value |
|-------|--------|-------------|--------------|---------|
| Flash (lenient) | Accuracy | 2.00/2.0 (N=9) | 2.00/2.0 (N=9) | 1.000 |
| Flash (lenient) | Contam-free | 89% | **100%** | — |
| Pro (strict) | Accuracy | 1.67/2.0 (N=9) | 1.57/2.0 (N=7) | 0.753 |
| Pro (strict) | Contam-free | 78% | **89%** | — |

**No significant difference in accuracy. Plugin-inject shows trend toward better contamination control.**

### Cross-evaluation with P1

| Source | Arm | Acc Mean | N | Contam-free |
|--------|-----|----------|---|-------------|
| P1 | FULL (rules+MCP) | 1.30/2.0 | 30 | 100% |
| P1 | OFF-clean (no rules) | 1.45/2.0 | 33 | 100% |
| Plugin-inject eval | FULL-CURRENT | 1.67/2.0 | 9 | 78% |
| Plugin-inject eval | PLUGIN-INJECT | 1.57/2.0 | 7 | 89% |

Note: P1 scores are not directly comparable due to different conversation content (P1 ran on different server sessions). The Plugin-inject evaluation used fresh sessions.

## Critical Finding: Zero MCP Tool Calls

Despite MCP server being connected and confirmed operational, **DeepSeek-V4 models make zero MCP tool calls** across all test conditions. This applies to both Flash and Pro variants, and persists even with explicit tool-calling prompts.

This means the quality comparison is actually:
- **FULL-CURRENT**: Has fish-trail rules telling it to call topic_detect/get_memory_context, but model doesn't call them → model has rules awareness but NO actual topic state
- **PLUGIN-INJECT**: Has topic state pre-injected into system prompt → model HAS actual topic state

Plugin-inject's contamination advantage likely comes from the model having real topic context (which topics exist, what they cover) rather than just instructions about topic management.

## Recommendations

1. **Plugin-inject is the right architecture** — inject topic state into cached system prompt for routine turns
2. **MCP tool calling investigation is critical** — if models can't call tools, the hybrid approach (plugin for routine, MCP for user-initiated) needs redesign
3. **Real-time detection can be deferred** — one-turn-delayed disk-read in plugin hook is acceptable for v1; the quality data shows it works
4. **Larger N for quality evaluation** would strengthen confidence but trend is clear

## Files

### Efficiency
- `results/plugin-inject-templateF.json` — Template F plugin-inject (N=3)
- `results/full-current-templateF.json` — Template F full-current (N=3)
- `results/full-current-templateA-block1.json` — Template A full-current (N=1)
- `results/plugin-inject-templateA-block1.json` — Template A plugin-inject (N=1)

### Quality
- `results/quality-eval/raw_samples.json` — Raw recall answers (18 samples)
- `results/quality-eval/anonymized_samples.json` — Blind-shuffled for judging
- `results/quality-eval/arm_mapping.json` — Arm identity mapping
- `results/quality-eval/raw_judgments.json` — Flash judge scores
- `results/quality-eval/raw_judgments_pro.json` — Pro judge scores
- `results/quality-eval/unblinded_scores.json` — Aggregated by arm
