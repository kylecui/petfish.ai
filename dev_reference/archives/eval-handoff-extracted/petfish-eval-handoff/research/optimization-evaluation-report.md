# Agent Memory Architecture: Optimization Directions and Evaluation Methodology

## Research Report
**Date**: 2026-05-24
**Type**: Mixed (Scientific + Planning)
**Scope**: PEtFiSh fish-trail memory architecture — how to optimize and how to evaluate

---

## 1. Core Finding: We Have a Measurement Problem, Not Just an Architecture Problem

The v3 benchmark reveals that **our evaluation methodology is the bottleneck**, not our architecture. Specifically:

1. **OpenCode REST API hides tool calls** — mcp_calls=0 for all entries, making cost comparison impossible
2. **Model-dependent quality is real but unexplained** — disk-v2 wins on Claude, loses on DeepSeek/GPT-Mini
3. **The academic field has the same problem** — no benchmark directly compares injection vs MCP for agent memory

This means: before iterating on architecture, we need to fix evaluation. Otherwise we're optimizing blind.

---

## 2. Evaluation Methodology: A Three-Level Design

### Level 1: Token-Level (API, Fast, Reproducible)

**What it measures**: Total cost (tokens × price), cache efficiency, wall time
**How**: Current REST API benchmark + provider billing API
**Limitation**: Cannot capture hidden tool call costs

**Proposed improvement**: Add `input_tokens` decomposition:
```
total_cost = system_prompt_tokens × cache_read_price + new_input_tokens × full_price + output_tokens × output_price
```
This isolates the injection payload cost (amortized via cache) from per-turn new input cost.

### Level 2: Tool-Call-Level (Server Logging, Ground Truth)

**What it measures**: Actual MCP call count, latency, and token overhead per call
**How**: Instrument `context-state/server.py` with request logging:
```python
# On each MCP request:
log_entry = {
    "timestamp": now(),
    "tool": request.method,
    "input_tokens": estimate_tokens(request.params),
    "output_tokens": estimate_tokens(response),
    "latency_ms": elapsed
}
append_jsonl("mcp_call_log.jsonl", log_entry)
```

**Why this matters**: Our v3 benchmark shows mcp_calls=0 via REST API, but the interactive v2 benchmark showed 30 calls per session. Server-side logging is the ground truth that resolves this discrepancy.

### Level 3: Quality-Level (LLM-as-Judge, Semantic)

**What it measures**: Recall, consistency, contamination, temporal coherence
**How**: LLM-as-judge evaluation on a held-out prompt set

**Proposed evaluation dimensions** (based on EvoMemBench + MemConflict):

| Dimension | What It Tests | Score |
|-----------|--------------|-------|
| **Recall** | Does the model correctly retrieve topic metadata? | 0-2 (existing) |
| **Consistency** | Does the model give the same answer for the same topic across turns? | Binary (same/different) |
| **Contamination** | Does the model leak Topic A's context when asked about Topic B? | Binary (leak/clean) |
| **Temporal** | Does the model prioritize recent over stale context? | 0-2 |
| **Action** | Does the model correctly perform topic management (switch, create)? | 0-2 |

### Statistical Rigor

- Minimum 30 entries per arm per model (current: 30, adequate)
- Bootstrap 95% CI for primary metrics
- Paired comparison (same prompts × same rounds)
- Cohen's d for effect size (not just p-value)
- Two-way ANOVA for model × architecture interaction

---

## 3. Why Model-Dependent Behavior Exists (And What To Do)

### Root Cause Analysis

The v3 data shows a clear pattern:

| Model | disk-v2 Recall | full-v2 Recall | Token Savings |
|-------|---------------|----------------|---------------|
| Claude Sonnet 4.6 | **1.83** | 1.70 | -6.5% (more expensive) |
| DeepSeek V4 Flash | 1.20 | **1.57** | **-8.7%** |
| GPT-5.4-Mini | 1.33 | **1.50** | **-17.1%** |

**Hypothesis**: The split correlates with model capability tier and attention architecture:

1. **Claude** (high capability, explicit caching) → Benefits from injection because:
   - Strong instruction-following: follows `[disk|rMCP:off]` directive precisely
   - Cache economics: 0.1x read cost makes injection amortization very favorable
   - System prompt attention: Claude is specifically trained to weight system prompt heavily

2. **DeepSeek Flash** (medium capability, MLA) → Benefits from tool-call fallback because:
   - MLA compresses KV differently: injection payload may not cache as effectively
   - Weaker instruction-following: may ignore injected context, preferring to "look it up"
   - Speed tier: Flash models prioritize speed over depth of attention

3. **GPT-Mini** (medium capability, automatic caching) → Mixed because:
   - Automatic caching helps injection but at 0.5x (worse than Claude's 0.1x)
   - Moderate instruction-following: attends to injection but also prefers tool verification

### Supporting Evidence

- **SRC-260014** (SAECache): System prompt tokens have 756x higher reuse rate than tool output tokens. This universally favors injection — but only when the model attends to the injected content.
- **SRC-260013** (DeepSeek MLA): KV cache compressed 93.3% via latent vectors. This changes the injection-vs-MCP calculus fundamentally — standard prefix caching assumptions may not hold.
- **SRC-260018** (Sutradhara): Tool calls account for 30-85% of FTR latency. This universally penalizes MCP-heavy architectures — but the penalty varies by model and tool.

### What To Do

**Option A: Model-aware architecture** — Detect model tier and adjust:
- Pro/Claude tier: Strict `[rMCP:off]` + full injection
- Flash/Mini tier: Soft suppression + allow tool-call fallback for uncertain queries
- Implementation: `reflectiveBrief(compression_ratio=0.45 if model_tier=="pro" else 0.25)`

**Option B: Verification loop** — Always inject, but add a lightweight verification step:
- Inject context as before
- After responding, check: "Did your answer reference the injected topic context?"
- If not, trigger a `topic_show` call and re-verify
- This catches the "model ignored injection" failure mode

**Option C: Adaptive fallback** — Start with injection, measure response quality:
- R1: Full injection, measure recall
- If recall < threshold, enable `topic_show` for subsequent turns
- This is the simplest approach but adds latency to the fallback detection

**Recommendation**: Option B (verification loop) — it preserves the injection advantage for models that attend to it, while catching failures on models that don't. The verification check is cheap (add ~50 output tokens per turn) and can be made conditional (only check on the first 2-3 turns of a new topic).

---

## 4. Optimization Directions Beyond Injection-vs-MCP

### 4.1 Compression Granularity (Near-term, High Impact)

Our current reflective compression uses a fixed 45% ratio. But the v3 data suggests this is too aggressive for Flash/Mini-tier models.

**Proposal**: Tiered compression:
- Registry Block: 0% compression (stable topic list, always cacheable)
- Warm Brief Block: 30% compression (one-liners with key tags preserved)
- Focus Block: 40-60% compression based on model tier

**Validation**: Run ablation: 0% / 30% / 45% / 60% compression × 3 models × 10 prompts. Measure recall × cost Pareto frontier.

### 4.2 Injection Position Optimization (Near-term, Medium Impact)

Our current 3-block order is Registry → Warm → Focus (stable → volatile). But Letta uses Identity → Memory → History → Task.

**Proposal**: Test block ordering:
- A: Registry → Warm → Focus (current)
- B: Focus → Warm → Registry (reversed)
- C: Focus → Registry → Warm (focus-first)

**Hypothesis**: Focus-first ordering may improve Claude's attention (important content first) but hurt DeepSeek (which may chunk the system prompt differently due to MLA).

**Validation**: Same ablation framework as 4.1, vary block order instead of compression.

### 4.3 Selective Injection via Scoring (Medium-term, High Impact)

Current fish-trail injects ALL active topics. Park et al.'s `recency × importance × relevance` scoring and MemoryBank's Ebbinghaus curve can filter which topics to inject.

**Proposal**: Add scoring to the inject plugin:
```typescript
function scoreTopic(topic: Topic, currentFocus: string): number {
  const recency = 1 / (1 + hoursSince(topic.last_seen_at));
  const importance = topic.boost || 0;
  const relevance = jaccardSimilarity(topic.tags, currentFocusTags);
  return recency * importance * relevance;
}
// Only inject topics with score > threshold
```

**Key question**: What threshold? If too aggressive, we lose context. If too permissive, we're back to injecting everything.

**Validation**: Compare recall@3 (top-3 injected) vs recall@all (current) across models. If recall@3 ≈ recall@all, we can cut injection payload significantly.

### 4.4 Sleep-Time Consolidation (Medium-term, High Impact)

Letta's pattern: between user interactions, run a consolidation pass that:
1. Reads episodic memory (raw exchanges)
2. Compresses into semantic summaries
3. Rewrites memory blocks with updated content

**Proposal**: Add a post-turn consolidation step:
```
After each turn:
  if topic_updated or new_exchange_count > threshold:
    run reflectiveBrief() in background
    write updated blocks to .petfish/fish-trail/
    next turn's injection picks up the update (1-turn delay)
```

**Advantage**: Moves compression cost off the critical path. The user doesn't wait for consolidation.

**Risk**: 1-turn delay means the model may respond with stale context for one turn after a topic update. But our v2 benchmark already showed this delay doesn't hurt quality (N=18, no significant difference).

### 4.5 Budget-Constrained Attention (Long-term, Strategic)

Instead of fixed injection, allocate a token budget:
- Total context window: 128K tokens
- Reserve: system prompt (5K) + history (growing) + output (4K)
- Memory budget: remaining tokens, allocated by priority

**Proposal**: Dynamic block sizing:
```typescript
const memoryBudget = contextWindow - systemPromptSize - historyEstimate - outputReserve;
const blocks = selectAndSizeTopics(topics, memoryBudget);
```

**This is the most ambitious optimization** because it requires:
1. Estimating history size in advance (tricky)
2. Selecting which topics to include (scoring, 4.3)
3. Sizing each block proportionally (compression, 4.1)
4. Updating dynamically as conversation grows

**When to pursue**: After 4.1-4.4 are validated. This is the "v0.8" architecture.

---

## 5. Prioritized Optimization Roadmap

### Sprint 1 (Week 1-2): Fix Measurement

| Item | Impact | Cost | Priority |
|------|--------|------|----------|
| Add MCP server-side request logging | High | Low | P0 |
| Add input_tokens decomposition to benchmark | Medium | Low | P0 |
| Design LLM-as-judge evaluation prompt | Medium | Medium | P1 |
| File OpenCode issue for tool call visibility | High | Low | P0 |

### Sprint 2 (Week 3-4): Validate Model-Dependent Behavior

| Item | Impact | Cost | Priority |
|------|--------|------|----------|
| Run ablation: compression × model (4.1) | High | Medium | P1 |
| Run ablation: block order × model (4.2) | Medium | Medium | P1 |
| Verify MCP call logging matches interactive results | High | Low | P1 |
| Measure actual MCP overhead via server logs | High | Low | P1 |

### Sprint 3 (Week 5-8): Optimize Architecture

| Item | Impact | Cost | Priority |
|------|--------|------|----------|
| Implement tiered compression (4.1) | High | Medium | P2 |
| Implement verification loop (Option B, 3.3) | High | Medium | P2 |
| Implement selective injection scoring (4.3) | High | High | P3 |
| Implement sleep-time consolidation (4.4) | Medium | High | P3 |

### Strategic (v0.8+): Advanced Architecture

| Item | Impact | Cost | Priority |
|------|--------|------|----------|
| Budget-constrained attention (4.5) | High | Very High | P4 |
| Cross-model architecture auto-tuning | Very High | Very High | P5 |
| Multi-agent memory sharing | Unknown | Very High | P6 |

---

## 6. Key Insight: The Real Innovation Is Measurement, Not Architecture

The most impactful near-term work is not a new architecture — it's **fixing our ability to measure**. Specifically:

1. **MCP server logging** gives us ground-truth tool call costs (resolves the REST API blind spot)
2. **LLM-as-judge** gives us calibrated quality scores (resolves the keyword-matching fragility)
3. **Input token decomposition** gives us cost attribution (resolves the "total tokens is misleading" problem)

With these three measurement fixes, we can:
- Validate whether disk-v2 actually saves cost (we suspect yes, but can't prove it via REST API)
- Quantify the model-dependent behavior (is it real, or a measurement artifact?)
- Compare architectures fairly (apples-to-apples, not apples-to-oranges)

**The architecture iteration should wait for measurement.** Optimizing without measurement is guessing.

---

## 7. Risk Register

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|-----------|
| OpenCode doesn't add tool call visibility | Medium | High | Use server-side logging as workaround |
| LLM-as-judge is biased toward injection architectures | Medium | Medium | Use blind evaluation (judge doesn't know which arm produced the response) |
| Model-dependent behavior is actually prompt-dependent | Low | High | Run same prompts across multiple sessions with different initial contexts |
| Compression ratio optimization is model-specific, not universal | Medium | Medium | Default to conservative compression (30%) with model-tier tuning |
| Provider pricing changes invalidate cost analysis | Low | Medium | Use relative savings (%), not absolute costs |

---

## 8. Evidence Map

| Claim | Evidence ID | Source | Confidence |
|-------|------------|--------|-----------|
| Injection saves tokens on most models | SRC-260021 | v3 benchmark data | Medium (REST API limitations) |
| Tool calls cost 30-85% of latency | SRC-260018 | Sutradhara paper | High (peer-reviewed) |
| System prompt tokens have 756x higher cache reuse | SRC-260014 | SAECache paper | High (peer-reviewed) |
| MLA changes caching economics | SRC-260013 | DeepSeek-V2 paper | High (peer-reviewed) |
| Claude benefits from injection, DeepSeek doesn't | SRC-260021 | v3 benchmark data | Medium (limited models, REST API) |
| Quality is model-dependent | SRC-260021 | v3 benchmark data | Medium (small sample, scoring limitations) |
| No benchmark directly compares injection vs MCP | SRC-260001-008 | Academic survey | High (exhaustive search) |
| Three-tier memory is consensus | SRC-260022 | Prior research findings | High (5 independent sources converge) |

---

## 9. Conclusion

The v3 benchmark exposed a fundamental truth: **we cannot optimize what we cannot measure**. The immediate priority is building measurement infrastructure (MCP logging, LLM-as-judge, token decomposition), not iterating on architecture.

Once measurement is in place, the most promising optimization direction is **tiered compression + verification loop**: compress injection content based on model tier, and add a cheap post-response check to catch cases where the model ignored injected context. This is the simplest change that addresses the model-dependent quality gap while preserving the cost advantages of injection.

The long-term direction — budget-constrained dynamic injection with scoring — is scientifically interesting but should wait until we have measurement validation and basic compression tuning in place.
