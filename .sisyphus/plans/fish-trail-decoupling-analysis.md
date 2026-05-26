# Fish-Trail Architecture Decoupling Analysis

**Date**: 2026-05-26
**Status**: Draft v2 — revised after Oracle review (bg_5a1af49b, score 6/10)
**Oracle Verdict**: Direction correct, D1 speculative, 3-copy problem underestimated, 12-file decomposition over-engineered
**Trigger**: "记忆压缩和skills应该是两件正交的事情，也许还有别的要解耦"

---

## 0. Anti-Sycophancy Check

Before proceeding, I must define "good decoupling" and find at least one thing wrong with the current direction.

**Rubric for good decoupling**:
1. Each module has a single, clearly bounded concern
2. Changing one concern doesn't require understanding another
3. Each concern can be tested, benchmarked, and evolved independently
4. Cross-concern integration is via explicit interfaces, not shared state
5. Decoupling reduces total system complexity, not just redistributes it

**Counter-argument to the user's instinct**: The user says "memory compression and skills should be orthogonal." But in practice, fish-trail's compression *depends on* topic state (what to compress), topic state *depends on* topic CRUD (how state changes), and the plugin *depends on* all of these (what to inject). Some coupling is inherent to the problem domain — decoupling everything would create integration glue that's worse than the current coupling. The right question is: **which coupling is harmful vs inherent?**

---

## 1. Evidence Base

This analysis is grounded in:

| Source | Key Finding | Confidence |
|--------|-------------|------------|
| Report 16 (Root Cause) | Cost = MCP tool calls → uncached context, not architecture size | High |
| Report 19 (Memory Architecture) | Industry converges on "read from system prompt, write via tool call" | High |
| Research Report (Optimization) | "Measurement problem, not architecture problem" — fix measurement first | High |
| Report 00 (Complete History) | 6 phases, compaction was null result, disk mode quality 98/100 | High |
| v3 Benchmark (210 entries, 5 models) | Model-dependent behavior: Claude benefits from injection, Flash/Mini don't | Medium |
| v4 Benchmark (270 entries, 3 arms) | Compression ablation: tiered compression shows promise but needs tuning | Medium |
| Academic survey (24 sources) | Three-tier memory is consensus (Park, MemGPT, CoALA, MemoryBank) | High |

---

## 2. Current Coupling Map

### 2.1 Plugin: God-Object (2055 lines)

The plugin `system-prompt-context-inject.ts` is the single biggest coupling problem. It contains:

| Lines | Concern | Change Frequency |
|-------|---------|-----------------|
| 1-120 | Constants, types, hashing | Low |
| 122-170 | OpenCode version detection + auto-patching | Low (changes on OpenCode upgrade) |
| 223-270 | CJK text utilities | Very low |
| 274-953 | **TopicDetector** (keyword extraction, Jaccard, signal detection, drift, bilingual) | Medium |
| 955-1020 | Config/constants, logging | Low |
| 1022-1050 | Utilities (readJSON, truncate) | Low |
| 1047-1090 | **resolveActiveTopic** (topic state reading) | Low |
| 1091-1120 | **buildRegistryView** (topic list formatting) | Low |
| 1124-1186 | **computeBriefMetrics** (metrics collection) | Medium |
| 1188-1260 | **formatRegistryBlock, formatWarmBriefBlock** (injection formatting) | Low |
| 1261-1288 | **reflectiveBrief** (v1.2 reflective compression) | Medium |
| 1289-1330 | **measureRecallSignal** (adaptive compression signal) | Medium |
| 1333-1448 | **resolveAdaptiveMode** (adaptive state machine) | Medium |
| 1449-1570 | **formatActiveFocusBlock** × 3 variants (injection formatting) | Medium |
| 1575-1605 | **readInjectedState, writeInjectedState** (state persistence) | Low |
| 1606-1655 | **extractUserMessage** (realtime mode hook) | Low |
| 1658-2055 | **resolvePluginOptions + main plugin export** (config + orchestration) | Low |

**The plugin mixes 6 concerns**: topic detection, memory formatting, compression strategy, metrics, adaptive state, and infrastructure.

### 2.2 MCP Server: Moderate Coupling (1599 lines)

The MCP server `server.py` imports and orchestrates:

| Module | Concern | Coupled To |
|--------|---------|-----------|
| TopicStore | Topic CRUD | topic JSON schema |
| TopicDetector | Detection (keyword + embedding) | topic data |
| ContaminationScorer | Risk scoring | topic data |
| ContextBuilder | Context package assembly | topic data + session data |
| SessionStore | Session management | session JSON schema |
| FeatureFlags | v1.2 feature toggles | config |
| MemoryPressureMonitor | v1.2 memory pressure | topic count/size |
| Brief validation + heuristic | v1.2 reflective compression | topic_update handler |

**The MCP server is better structured** — it delegates to modules. But brief validation logic is embedded directly in the `topic_update` handler, coupling write-path to compression logic.

### 2.3 Agent Rules: Policy Coupling

`fish-trail.md` (agents-rules) mixes:
- **When to call MCP** (policy decision)
- **How to write briefs** (compression guidance)
- **What to do on topic switch** (routing logic)
- **Session management instructions** (session lifecycle)

This is a single document that the LLM must parse holistically. Changes to brief guidance require re-reading the entire governance policy.

---

## 3. Identified Coupling Dimensions

### D1: Memory Compression ↔ Topic CRUD (Harmful)

**Current state**: When `topic_update` is called with a `reflective_brief`, the MCP server validates the brief (quality check), computes heuristic fallback, tracks degradation, and writes it to topic JSON — all in the same handler.

**Why harmful**:
- Changing compression ratio requires touching the MCP server
- Adding a new compression strategy requires modifying the topic_update handler
- Brief validation logic is tested alongside topic CRUD tests
- v1.2's `computeBriefMetrics` (in plugin) reads topic files to compute brief stats — plugin now knows about compression quality metrics

**Evidence**: Report 16 — "The problem is 'LLM makes tool calls that put results in conversation context instead of having the plugin put equivalent information in system prompt.'" This diagnosis is correct but incomplete. The deeper problem is that the write-path (topic_update) is entangled with compression quality enforcement.

**Decoupling target**: Compression should be a middleware/pipeline that wraps topic_update, not embedded in it.

### D2: Memory Injection ↔ Plugin Infrastructure (Harmful)

**Current state**: The plugin's main export does everything: reads config, detects OpenCode version, reads topic state, formats 3 blocks, computes metrics, manages adaptive state, writes persistence.

**Why harmful**:
- 2055 lines in one file means any change risks breaking any other concern
- 3 synchronized copies (lib/, .opencode/, packs/) must all be updated together
- Testing requires loading the entire plugin, not just the changed function
- The plugin cannot be partially enabled/disabled

**Evidence**: v1.2 added 4 feature flags (P1-P7) as booleans, but the code paths are interleaved. You can't enable adaptive compression without also loading brief metrics code. The `resolveAdaptiveMode` function (lines 1333-1448) is 115 lines of state machine logic embedded in a "plugin" whose primary job is system prompt transformation.

**Decoupling target**: Extract concerns into independent modules with a thin orchestration layer.

### D3: Topic Detection ↔ Plugin (Moderate)

**Current state**: TopicDetector class (680 lines) lives inside the plugin. It's used only when `detectionMode: "experimental.realtime"` is enabled (which is currently disabled — we use disk mode).

**Why moderately harmful**:
- 680 lines of detection logic inflate the plugin but are mostly dormant
- The detection algorithm (keyword extraction + Jaccard + bilingual + drift) is conceptually independent of injection formatting
- But: it's currently unused (disk mode only), so the real impact is code bloat, not runtime coupling

**Evidence**: Report 16 section 3 — "Tier 2 Was NOT Active During P1." The entire embedding infrastructure exists but is dormant. The detection code adds complexity without runtime benefit in current config.

**Decoupling target**: Move TopicDetector to its own module. Plugin imports it only when realtime mode is enabled.

### D4: Session Management ↔ Topic Lifecycle (Inherent — Low Harm)

**Current state**: Sessions are bound to topics, session_resume loads topic context, session_timeline shows topic-related events.

**Why this is inherent**: Sessions *should* know about topics — that's the point. A session is "work done on a topic." Decoupling them would create awkward glue code.

**Assessment**: Not harmful. The current SessionStore + TopicStore separation is already decent. Leave it.

### D5: Metrics/Logging ↔ Everything (Moderate)

**Current state**: `computeBriefMetrics` (plugin) reads all topic files to compute brief_hit_rate, heuristic_ratio, agent_reject_rate. `measureRecallSignal` (plugin) reads mcp-call-log.jsonl. Both write to `injected-block-state.json`.

**Why moderately harmful**:
- Metrics code is interleaved with injection formatting
- Adding a new metric requires touching the injection pipeline
- Metrics persistence is coupled to the injection state file
- The metrics are v1.2-specific (brief stats) but will expand to cover adaptive compression, model-tier behavior, etc.

**Evidence**: Research Report section 2 — "We have a measurement problem." The team correctly identified measurement as a bottleneck. But the current metrics implementation adds coupling instead of solving it. Metrics should be a cross-cutting concern with its own pipeline, not embedded in the injection plugin.

**Decoupling target**: Metrics as an observer/pipeline that hooks into injection and compression events without being in the critical path.

### D6: Skill Activation ↔ Topic Routing (Not Coupled)

**Current state**: Skills match on description text. Topics match on keyword/embedding similarity. They're completely independent code paths.

**Assessment**: The user's instinct about "memory compression and skills should be orthogonal" is correct in principle, but in practice, fish-trail skills and memory compression are **already** in separate directories with separate activation logic. The coupling is at the AGENTS.md level (rules tell the LLM when to use which), which is a policy layer, not a code layer.

**The real coupling the user may be sensing**: The Companion Gateway (which includes Skill Sense, Failure Signal Detection) is defined in the root AGENTS.md alongside fish-trail rules. Both are injected into system prompt. But they're separate skill packs with separate code. The coupling is at the documentation/rules layer, not the code layer.

### D7: Feature Flags ↔ All Concerns (Emerging)

**Current state**: v1.2 added `reflectiveBriefEnabled` and `adaptiveCompressionEnabled`. These are booleans that gate code paths scattered across the plugin.

**Why emerging-harmful**:
- Feature flags create N×M testing combinations (each flag × each code path)
- v1.3+ will add more flags (model-tier awareness, verification loop, budget-constrained attention)
- Without a feature flag management layer, the plugin becomes a combinatorial explosion of conditionals

**Evidence**: The v1.2 test plan has 21 acceptance criteria partly because feature flags multiply test cases.

**Decoupling target**: Feature flags should be a configuration concern that selects strategy implementations, not boolean guards in the middle of functions.

---

## 4. What the Test Team Got Right (And What They Missed)

### Got Right

1. **"Cost = uncached tool calls, not architecture size"** (Report 16) — Correct. The 10x cost difference between system prompt (cached) and tool call output (uncached) is the dominant factor. Any architecture that moves reads from tool calls to system prompt injection will save cost.

2. **"Fix measurement before architecture"** (Research Report) — Correct. The v3 benchmark's mcp_calls=0 blind spot means we're optimizing partly on faith. MCP server logging + LLM-as-judge should come before v1.3 architecture changes.

3. **"Model-dependent behavior is real"** (Report 19, v3/v4 data) — Correct. Claude benefits from injection, Flash/Mini don't. Any architecture must be model-aware.

### Missed

1. **The plugin is a god-object** — The test team focused on the MCP server (31 tools, server.py) but didn't scrutinize the plugin. The plugin is 2055 lines doing 6 different things. This is the most harmful coupling in the system, but it wasn't identified because the test team measured cost/quality/latency, not code maintainability.

2. **Compression is embedded in write-path** — Brief validation in `topic_update` handler couples "how topics are updated" with "how briefs are validated." The test team saw the feature working correctly but didn't assess the implementation coupling.

3. **Metrics are a cross-cutting concern treated as inline code** — The research report correctly identified "we need better measurement" but the implementation adds metrics inline in the plugin, creating new coupling instead of building a clean measurement pipeline.

4. **Feature flags are accumulating without a strategy pattern** — v1.2 has 2 flags. v1.3+ will add model-tier, verification loop, budget constraints. Without a strategy/registry pattern, each new flag adds conditional branches throughout the plugin.

---

## 5. Proposed Decoupling Architecture

### 5.1 Principle: Separate WHAT from HOW from WHEN

| Layer | Concern | Analogy |
|-------|---------|---------|
| **State** | What is the current topic/memory state? | Database |
| **Strategy** | How do we compress/inject/measure? | Query optimizer |
| **Orchestration** | When do we apply which strategy? | Query planner |
| **Infrastructure** | Plugin hooks, config, file I/O, caching | Connection pool |

### 5.2 Module Boundaries

```
system-prompt-context-inject.ts (thin orchestrator, ~200 lines)
  │
  ├─ state/
  │   ├─ topic-reader.ts         ← reads topic JSON, resolves active topic
  │   └─ session-reader.ts       ← reads session state (future)
  │
  ├─ strategy/
  │   ├─ format-registry.ts      ← Registry block formatting
  │   ├─ format-warm.ts          ← Warm Brief block formatting
  │   ├─ format-focus.ts         ← Active Focus block formatting (3 variants)
  │   ├─ compression.ts          ← reflectiveBrief + compression logic
  │   └─ adaptive.ts             ← adaptive state machine + recall signal
  │
  ├─ measurement/
  │   ├─ metrics-collector.ts    ← brief stats, adaptive metrics
  │   └─ metrics-persistence.ts  ← reads/writes injected-block-state.json
  │
  ├─ detection/
  │   └─ topic-detector.ts       ← keyword + Jaccard + bilingual (680 lines, lazy-loaded)
  │
  └─ infra/
      ├─ plugin-config.ts        ← resolvePluginOptions + feature flag registry
      ├─ file-utils.ts           ← readJSON, writeJSON, hashing
      ├─ opencode-patch.ts       ← version detection + auto-patching
      └─ cjk-utils.ts            ← CJK text utilities
```

### 5.3 MCP Server Decoupling

```
server.py (thin handler, dispatches to modules)
  │
  ├─ handlers/
  │   ├─ topic_crud.py           ← create, update, archive, show, list
  │   ├─ session.py              ← bind, resume, timeline, agents
  │   ├─ contamination.py        ← detect, score, route
  │   └─ context.py              ← build, export, freeze
  │
  ├─ compression/
  │   ├─ brief_validator.py      ← schema validation + quality checks
  │   ├─ heuristic_brief.py      ← 3-strategy heuristic fallback
  │   └─ degradation_tracker.py  ← auto-degradation state machine
  │
  └─ measurement/
      └─ mcp_logger.py           ← per-request logging to mcp-call-log.jsonl
```

The key change: `compression/` is a separate module. `topic_crud.py` calls `brief_validator.py` via an explicit interface, not inline code. Adding a new compression strategy = adding a new file in `compression/`, not modifying the topic_update handler.

### 5.4 Feature Flag → Strategy Registry

```typescript
// Instead of scattered booleans:
if (options.reflectiveBriefEnabled) { ... }
if (options.adaptiveCompressionEnabled) { ... }

// Use a strategy registry:
type CompressionStrategy = {
  name: string;
  compress(summary: string, context: TopicState): string;
  validate(brief: string): boolean;
}

const strategies: Record<string, CompressionStrategy> = {
  "none": new NoCompression(),
  "reflective": new ReflectiveCompression(),
  "adaptive": new AdaptiveCompression(),
  "model-aware": new ModelAwareCompression(),  // v1.3+
};

// Plugin selects strategy based on config:
const strategy = strategies[config.compressionMode] || strategies["none"];
```

This replaces boolean flags with a named strategy. New features = new strategies, not new branches.

---

## 6. Prioritized Decoupling Roadmap

### Phase A: Measurement First (Week 1-2) — No Architecture Changes

The research report's conclusion is correct: **fix measurement before architecture**. This requires zero decoupling.

| Task | Effort | Impact |
|------|--------|--------|
| Add MCP server request logging to mcp-call-log.jsonl | Low | High — ground truth cost data |
| Add input_tokens decomposition to benchmark | Low | Medium — cost attribution |
| Design LLM-as-judge evaluation prompt | Medium | Medium — calibrated quality scores |
| Collect Alpha observation data (brief_hit_rate, agent_reject_rate) | Wait | High — validate v1.2 |

**Why no architecture changes yet**: We don't know if the current coupling actually causes problems in production. v1.2 is in Alpha. Let it run. Collect data. Then decide what to decouple based on evidence, not theory.

### Phase B: Plugin Modularization (Week 3-4) — If Data Justifies

**Trigger**: Alpha data shows brief_hit_rate ≥ 0.7 (P7 success criteria met), OR metrics reveal a specific coupling-caused failure.

| Task | Effort | Risk |
|------|--------|------|
| Extract `state/topic-reader.ts` from plugin | Low | Low — pure extraction |
| Extract `strategy/format-*.ts` from plugin | Medium | Low — pure extraction |
| Extract `measurement/metrics-collector.ts` from plugin | Low | Low — pure extraction |
| Extract `detection/topic-detector.ts` (lazy-load) | Low | Low — already isolated class |
| Keep `infra/` inline for now (not worth abstracting) | — | — |

**What NOT to do**: Don't refactor the 3-copy sync problem. That's a deployment concern, not a coupling concern. The sync is annoying but not harmful.

### Phase C: MCP Server Decompression (Week 5-6) — If Needed

| Task | Effort | Risk |
|------|--------|------|
| Extract `compression/` from topic_update handler | Medium | Medium — changes write path |
| Extract `handlers/` per MCP tool group | Medium | Low — pure extraction |
| Add `measurement/mcp_logger.py` | Low | Low — additive |

### Phase D: Strategy Pattern (Week 7-8) — For v1.3 Features

| Task | Effort | Risk |
|------|--------|------|
| Replace boolean flags with strategy registry | Medium | Medium — changes config format |
| Implement ModelAwareCompression strategy | Medium | Medium — new behavior |
| Implement VerificationLoop strategy | High | High — changes read path |

---

## 7. Risks and Counter-Arguments

### Risk 1: Over-Engineering

**Argument**: The plugin works. 2055 lines is a lot but it's tested (17/17 pass) and stable. Refactoring introduces risk without user-visible benefit.

**Counter**: The risk isn't today's 2055 lines — it's v1.3's projected 3000+ lines when model-aware compression, verification loops, and budget-constrained attention are added. Decoupling now (while the code is stable and tested) is cheaper than decoupling later (when it's 3000+ lines with 5 feature flags).

**Mitigation**: Phase A does nothing. Phase B only extracts. No behavioral changes until measurement data justifies them.

### Risk 2: The 3-Copy Sync Problem Gets Worse

**Argument**: Modularizing the plugin into 8+ files means syncing 24+ files across 3 directories. This is worse than syncing 3 files.

**Counter**: This is a deployment problem, not a coupling problem. The right fix is a build step that generates the 3 copies from a single source, not keeping 3 copies in sync manually.

**Mitigation**: Add a `sync-plugin.sh` script or build step as part of Phase B. Don't modularize without solving the copy problem.

### Risk 3: Performance Overhead from Module Boundaries

**Argument**: TypeScript module imports and function calls across files add overhead. The plugin runs on every message — it must be fast.

**Counter**: Module boundaries are compile-time constructs. Bun bundles everything into a single file. Runtime performance is identical to the monolith.

**Mitigation**: Verify with a benchmark before/after extraction. If Bun doesn't bundle as expected, keep hot-path code inline.

### Risk 4: "Measurement First" Delays Real Progress

**Argument**: The user wants research-grade ambition ("领先的独特的方案"). Waiting 2 weeks for data feels like inaction.

**Counter**: The research report's #1 finding is "we have a measurement problem." Optimizing without measurement is guessing. v1.2 is in Alpha — we literally can't measure its effectiveness yet because there's no production data.

**Mitigation**: Phase A isn't passive. It includes building MCP server logging, LLM-as-judge, and benchmark improvements — these are meaningful engineering work that directly enables better architecture decisions.

---

## 8. What Should Stay Coupled

Not everything should be decoupled. Some coupling is inherent to the problem:

1. **Topic state ↔ Injection formatting**: The plugin must read topics to format them. This coupling is inherent — the injection IS the topic state, formatted. Decoupling them would add an abstraction layer with no benefit.

2. **Session ↔ Topic**: Sessions track work on topics. They should know about each other.

3. **Detection ↔ Topic data**: Detection reads topic data to compute similarity. This is inherent.

4. **Agent rules ↔ Everything**: The agent-rules document is a policy layer that naturally references all concerns. It's documentation, not code. Decoupling documentation is counterproductive.

---

## 9. Oracle Review Findings (bg_5a1af49b)

An independent Oracle review with anti-sycophancy discipline identified 5 issues with this proposal:

### 9.1 D1 Is Speculative — Brief Validation Code Doesn't Exist in server.py

The proposal claims brief validation is "embedded in the `topic_update` handler" in the MCP server. Oracle checked `server.py` — **there is no `topic_update` handler or `reflective_brief` reference in the current server.py**. The brief validation exists in test files referencing a `_heuristic_brief` method that may be on the v1.2 branch but not in the currently deployed server.

**Action**: D1 should be reclassified from "Harmful" to "Emerging (post-v1.2-merge)." The actual harmful coupling today is D2 (plugin god-object) and D5 (metrics inline).

### 9.2 Missing Dimension D8: Plugin ↔ OpenCode Runtime API

The plugin uses `@opencode-ai/plugin` types, `execSync` for version detection, and has auto-patching. When OpenCode changes its plugin API, the plugin breaks. v1.2's `experimental.realtime` mode depends on an unmerged upstream PR (#163). This is real coupling not identified in D1-D7.

### 9.3 Missing Dimension D9: Schema ↔ Code Drift

Topic JSON schema, plugin TypeScript types, and MCP Python data classes are three separate implementations of the same data contract. Schema changes require coordinated edits across TS, Python, and documentation. This coupling gets *worse* with modularization (more files to update).

### 9.4 12-File Decomposition Is Over-Engineered

The proposal's own §0 principle says "integration glue that's worse than the current coupling." Creating 12 files from 1 file violates this. **The right first step is 3 files**, not 12:
1. `plugin-core.ts` — orchestrator + state reading + config (~400 lines)
2. `plugin-formatting.ts` — all 3 block formatters + reflective brief (~500 lines)
3. `plugin-infra.ts` — utilities, CJK, version detection, file I/O (~200 lines)

Extract to 12 files only when v1.3 features arrive and justify the granularity.

### 9.5 3-Copy Sync Is a Prerequisite, Not a Follow-up

The proposal says "add a sync script" as a mitigation. Oracle argues: modularizing amplifies the copy problem from 3 files → 36 files (if 12 modules × 3 copies). If sync is already error-prone at 3 files (the v0.10.7 lesson), it's 12× worse at 36 files.

**Correct sequence**: Build source-of-truth mechanism first → then modularize.

### 9.6 D4 "Session↔Topic Is Inherent" Is Wrong

Sessions without topics are useful:
- Generic work sessions ("What did I do yesterday?") don't require a topic
- Cross-topic sessions have identity independent of any single topic
- `session_bind` currently requires `topic_id` — making it optional is low-cost decoupling

**Reclassification**: D4 from "Inherent" to "Low-cost decoupling opportunity."

---

## 10. Revised Summary: Coupling Problems, Ranked

| Rank | Coupling | Harm | Fix Complexity | When to Fix |
|------|----------|------|---------------|-------------|
| 1 | **Plugin god-object** (D2) | High | Medium (3-file split) | Phase B, after Alpha data + sync fix |
| 2 | **3-copy sync problem** (not D-numbered) | High (blocks modularization) | Medium (build step) | **Before Phase B** |
| 3 | **Plugin ↔ OpenCode API** (D8, new) | High (breaks on upgrade) | Low (abstraction layer) | Phase B |
| 4 | **Schema ↔ Code drift** (D9, new) | Medium (worse with modularization) | Medium (shared schema spec) | Phase B |
| 5 | **Compression in write-path** (D1) | Emerging (post-v1.2) | Medium (middleware) | Phase C, after v1.2 merges |
| 6 | **Metrics inline** (D5) | Medium | Low (extraction) | Phase B |
| 7 | **Feature flags accumulating** (D7) | Medium now, High later | Medium (strategy enum) | Phase D |
| 8 | **Session↔Topic** (D4, revised) | Low (optional decoupling) | Low (make topic_id optional) | When needed |
| 9 | **Dormant detection code** (D3) | Low | Low (lazy-load) | When realtime mode is enabled |

**Not worth fixing**: D4 (session↔topic, inherent), D6 (skill↔topic, already decoupled).

---

## 11. Recommendation

**Stop. Measure. Fix sync. Then split to 3 files.**

1. Let v1.2 Alpha run for 1-2 weeks. Collect brief_hit_rate, agent_reject_rate, and MCP call logs.
2. Build measurement infrastructure (MCP logging, LLM-as-judge). This is the highest-ROI work.
3. **Before any modularization**: Fix the 3-copy sync problem. Build a source-of-truth mechanism (single source → generate copies, or build step). This is a prerequisite, not a follow-up.
4. Start Phase B with a **3-file split** (core/formatting/infra), not 12 files. Extract further only when v1.3 features justify it.
5. The user's instinct is correct — memory compression and skills should be orthogonal. But the more urgent coupling is **within the memory system itself** (plugin god-object, sync problem, schema drift).

The most impactful near-term action is not decoupling — it's **proving that v1.2 works** with real data. Once we have that proof, decoupling decisions become evidence-driven instead of theory-driven.
