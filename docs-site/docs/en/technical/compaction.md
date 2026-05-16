# Token Cost Engineering

How PEtFiSh reduces AI agent session costs by 20% through compaction frequency reduction and behavioral change.

---

## The Cost Problem

Long AI agent sessions are expensive — not because of prompt size or response length, but because of **compaction**. When conversation context fills up, the platform summarizes history to make room. Each compaction event burns 50K–80K tokens in overhead.

The dominant cost driver in AI agent sessions isn't what you send — it's how often compaction fires.

PEtFiSh ran two controlled experiments to understand and reduce this cost.

---

## Background: Why v0.11.0 Regressed 37%

PEtFiSh v0.11.0 introduced a tiered architecture for agent rules: instead of one 1,037-line inline file, rules were split into a 57-line entry point plus 7 on-demand sub-files. Cleaner, more maintainable.

But A/B testing revealed a **36.6% token regression**. The reason: dynamically loaded rules land in uncached conversation context. They accumulate with each tool call, inflating the context window faster, triggering more compactions (2 → 3), each costing 50–80K tokens.

The fix wasn't "go back to inline." It was understanding *where* rules live in the LLM's memory architecture.

---

## Experiment 1: System Prompt Injection

Two plugins were built using OpenCode's `experimental.chat.system.transform` hook to move rules back into the cached system prompt prefix:

- **All-rules** — Inject all 7 rule files (~9.4K tokens) into the system prompt. 71 lines of code, zero config.
- **Smart-rules** — Dynamically match rules to the active topic. 131 lines, requires a mapping registry.

### Results

21 messages, 3 topics, `claude-sonnet-4`:

| Metric | Baseline (v0.10.x) | All-Rules Plugin | Delta |
|---|---|---|---|
| Total tokens | 586,917 | 475,039 | **-19.1%** |
| Input tokens | 455,533 | 327,834 | -28.0% |
| Compactions | 2 | 1 | **-50%** |
| Peak context | 152,990 | 145,530 | -4.9% |

Smart-rules achieved 12.3% savings but proved fragile — silent failures on missing mappings, false-positive keyword matching, manual maintenance burden. For rule sets under 30K tokens, all-rules wins on every dimension.

### Key Insight

The 20-token overhead of injecting all rules into the system prompt is negligible. What matters is that cached prefix content **doesn't count toward compaction threshold accumulation**. One fewer compaction = 50–80K tokens saved.

---

## Experiment 2: Topic-Aware Compaction

A separate study asked: when compaction *does* fire, can PEtFiSh's topic management make it smarter?

The fish-trail topic system already tracks what you're working on — which topics are active, their relationships, their summaries. A Phase 2 plugin restructures the compaction prompt using this topic data, telling the model: "here are 3 topics, compress each separately, prioritize the active one."

### Results

21 messages, 3 interleaved topics, `claude-sonnet-4`:

| Metric | Baseline | Topic Plugin | Delta |
|---|---|---|---|
| Total tokens | 857,115 | 683,522 | **-20.3%** |
| API calls | 140 | 89 | -36.4% |
| Wall time | 49 min | 30 min | -39.4% |
| Cache reads | 10.6M | 5.3M | -49.9% |
| Recall quality | Pass | Pass | **No loss** |

### The Surprise: Behavioral Change

The expected savings were from better compression ratios. That's not what happened.

The primary mechanism is **behavioral change**. When the model receives topic-structured context, it produces more focused responses — fewer intermediate tool calls (4.2/msg vs 6.7/msg), more consolidated answers. This cascades: fewer API calls → less cache reads → faster wall time.

This is why Phase 3 (pre-computed summaries that skip the LLM) was shelved: it can't trigger this behavioral effect. The model needs to *process* topic-structured context during compaction, not just receive a pre-built summary.

---

## Findings

1. **Compaction frequency dominates token cost.** Everything else — prompt size, output length, caching strategy — is secondary. Reduce compactions and costs drop dramatically.

2. **Cached prefix is free real estate.** Rules in the system prompt cost almost nothing (cache reads are ~10× cheaper than input tokens). Rules in conversation context are a ticking time bomb toward the next compaction.

3. **Topic structure changes model behavior.** Not just compression quality — the model actually becomes more efficient when it has structured context about what it's doing.

4. **Simple beats clever.** All-rules (71 lines, zero config) beat Smart-rules (131 lines, registry dependency) on both cost and reliability. Don't optimize what doesn't need optimizing.

---

## Limitations

- Tested on `claude-sonnet-4` only. Other models may differ.
- 21-message sessions with 3 topics. Larger sessions may show different patterns.
- Single-user scenarios. Multi-window concurrent sessions untested.
- OpenCode's plugin hooks are marked `experimental` — though 11+ external projects use them in production.

---

## Availability

Both plugins ship with PEtFiSh:

- **System prompt plugin**: Included in the `companion` pack
- **Topic-aware compaction plugin**: Included in the `context` pack (fish-trail)

```bash
# Install both plugins
curl -fsSL https://raw.githubusercontent.com/kylecui/petfish.ai/master/remote-install.sh \
  | bash -s -- --pack companion,context --detect
```

Full research data, A/B test harness, and raw results are in the [GitHub repo](https://github.com/kylecui/petfish.ai):

- Experiment 1: `evals/v011-sysprompt-plugin-report/PAPER.md`
- Experiment 2: `research/topic-aware-compaction/06_outputs/research-report.md`

All experiments ran on `claude-sonnet-4` via the `github-copilot` provider in OpenCode.

---

## Further Reading

- [System Prompt Architecture](sysprompt-design.md) — How PEtFiSh structures agent instructions
- [Companion Gateway](companion-gateway.md) — The always-on pre-processing pipeline
