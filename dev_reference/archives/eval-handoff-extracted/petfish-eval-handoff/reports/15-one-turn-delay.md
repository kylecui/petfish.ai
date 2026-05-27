# One-Turn Delay Assessment: Plugin Disk-Read vs Real-Time Detection

**Date**: 2026-05-23
**Scope**: Does reading topic state from disk (previous turn) instead of real-time detection hurt quality?

## The Delay

The plugin's `experimental.chat.system.transform` hook fires **before** each LLM call. It reads topic state from disk — which was written by the **previous turn's** MCP topic_detect (if it ran). This means:

- Turn 1 (cold start): No topic state in plugin
- Turn 2+: Plugin shows topic state from turn N-1's detection
- At topic transitions: Plugin shows the **old** topic, not the one the user just switched to

## When Delay Occurs

In Template A (extreme test case with 95% transition rate), the plugin shows stale topic state on **every one of the 20 transitions**. In real-world usage (estimated 10-20% transition rate), far fewer messages are affected.

## Why It Doesn't Hurt Quality

### 1. Plugin state is supplementary, not authoritative

The model reads the user's message as the primary signal. Plugin-injected topic context helps with:
- **Continuity**: Remembering what was discussed previously
- **Contamination awareness**: Knowing other topics exist in the conversation
- **NOT real-time detection**: The model doesn't rely on the plugin to know what the user is asking about

### 2. Even stale context is better than no context

Showing the previous topic's summary gives the model awareness of the broader conversation structure. On the next turn, it gets the correct topic.

### 3. MCP topic_detect had the same effective delay

Even with MCP, the model would:
1. Read user message
2. Decide whether to call topic_detect (usually not — see issue #147)
3. Get result → respond

The detection happens **during** the turn, not before. The model's first response at a transition point is based on the message content regardless of whether it calls topic_detect.

### 4. Quality data confirms no damage

| Metric | Plugin-inject | FULL-current | p-value |
|--------|--------------|-------------|---------|
| Accuracy (strict) | 1.57/2.0 | 1.67/2.0 | 0.753 |
| Contamination-free (strict) | **89%** | 78% | — |
| Contamination-free (lenient) | **100%** | 89% | — |

Plugin-inject actually **reduced contamination** despite one-turn delay. The model correctly prioritizes the user's message over the plugin-injected topic state.

## When Real-Time Detection WOULD Matter

1. **Silent context switches**: User messages that subtly shift topics without keywords
   - e.g., "Also, the deployment script has a bug" after discussing CI/CD
   - One-turn delay means the model won't flag the switch until next turn
   - But topic_detect Tier 1 might also miss these (keyword-based)

2. **High-stakes isolation**: Medical, legal, financial conversations
   - Explicit user-initiated topic management is better than automatic detection
   - Automatic detection (MCP or plugin) is never reliable enough for these cases

3. **Long agent loops**: Agent runs multiple steps autonomously
   - Plugin reads disk at step START, not between steps
   - Topic state could drift within a multi-step agent run
   - Mitigation: Plugin re-reads disk at each step (current behavior)

## Implementation Options

| Option | Latency | Complexity | Benefit |
|--------|---------|-----------|---------|
| **Current: disk-read** | 1 turn | Low | Quality validated |
| **Tier 1 in plugin hook (TypeScript)** | 0 | Medium | Self-contained, no MCP dep |
| **fs.watch on topic files** | ~100ms | Medium | Near-real-time |
| **MCP topic_detect on demand** | 0 (when called) | Already exists | Only works when model calls it |

**Tier 1 in plugin hook** is the most interesting option: port `topic_detector.py` (lines 239-580, keyword extraction + Jaccard + signal phrase matching + bilingual expansion + semantic drift) to TypeScript and run it directly in the `experimental.chat.system.transform` hook. This would:
- Eliminate the one-turn delay entirely
- Remove MCP dependency for topic detection
- Keep Tier 2 (ONNX embedding) as MCP-side optional fallback
- Add ~2-5ms to the hook execution (keyword matching is cheap)

Estimated effort: 1-2 days for Tier 1 port, 0.5 day for integration testing.

## Recommendation

**Ship v1 with disk-read.** Quality data validates this choice. Real-time detection is a v2 optimization that adds complexity without proven quality benefit.

**Plan v2 with Tier 1 in plugin hook.** This is the cleanest path to zero-delay detection and full MCP independence. If users report topic confusion in practice, accelerate v2.
