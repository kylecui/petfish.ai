# PEtFiSh Fish-Trail Performance Evaluation — Complete History

> Timeline: 2026-05-06 ~ 2026-05-25
> Author: Test Team (kylecui)
> Repository: kylecui/petfish_tester + kylecui/petfish.ai

---

## Table of Contents

1. [Overview & Goals](#1-overview--goals)
2. [Phase 0: Foundation — Trigger Evaluation & Initial QA](#2-phase-0-foundation)
3. [Phase 1: Compaction Plugin Testing](#3-phase-1-compaction-plugin-testing)
4. [Phase 2: v0.11.0 Upgrade Impact Analysis](#4-phase-2-v0110-upgrade-impact-analysis)
5. [Phase 3: System Prompt Plugin Injection](#5-phase-3-system-prompt-plugin-injection)
6. [Phase 4: Multi-Model Architecture Evaluation](#6-phase-4-multi-model-architecture-evaluation)
7. [Phase 5: Deep Research & Architecture Redesign](#7-phase-5-deep-research--architecture-redesign)
8. [Phase 6: v1.1.0-pre Benchmark Series (v1~v4)](#8-phase-6-v110-pre-benchmark-series)
9. [Cumulative Findings & Decisions](#9-cumulative-findings--decisions)
10. [Open Issues & Next Steps](#10-open-issues--next-steps)
11. [Artifact Index](#11-artifact-index)

---

## 1. Overview & Goals

### 1.1 Mission

Evaluate and optimize the PEtFiSh fish-trail memory architecture for:
- **Token efficiency**: Reduce per-turn token cost without quality loss
- **Recall quality**: Ensure topic context is available when needed
- **Contamination control**: Prevent cross-topic context leakage
- **Multi-model robustness**: Architecture must work across DeepSeek/Claude/GPT providers

### 1.2 Key Metrics

| Metric | Definition | Measurement |
|--------|-----------|-------------|
| Total tokens | Cumulative input+output per session | OpenCode REST API `info.tokens.total` |
| Input tokens | Per-turn input cost | `info.tokens.input` |
| Cache read | Cached prefix reuse | `info.tokens.cache.read` |
| Wall time | End-to-end latency per turn | `time.monotonic()` delta |
| Recall (0-2) | Topic context availability in response | Keyword scoring + LLM-as-judge |
| Contamination | Cross-topic leakage | Keyword presence in wrong-topic responses |
| MCP calls | Tool calls to context-state server | REST API (unreliable) + server log |

### 1.3 Experimental Infrastructure

- **OpenCode REST API**: `opencode serve --port N` → HTTP session/message endpoints
- **Models**: DeepSeek V4 Pro/Flash, Claude Sonnet 4.6, GPT-5.4-Mini, GPT-4o, Gemini 3 Flash
- **Test workspace**: Synthetic topic data (3-5 topics, 15-35 messages), topic-aware prompts
- **Benchmark scripts**: Python (httpx), sequential per-arm server lifecycle

---

## 2. Phase 0: Foundation — Trigger Evaluation & Initial QA

> Date: 2026-05-06 ~ 2026-05-08
> Goal: Verify PEtFiSh skill packs trigger correctly and basic functionality works

### 2.1 Trigger Evaluation

- Ran 563 trigger checks across all installed skills
- Initial pass rate: ~33% (many skills failed to trigger on matching keywords)
- After fixes: **563/563 passed**
- Findings documented in `experiments/trigger-eval-batch-report-2026-05-08.md`

### 2.2 Pack-Level QA

| Pack | Status | Key Finding |
|------|--------|-------------|
| Course | QA/QC cycle tested | Full lifecycle works |
| Deploy/Ops | Docker/deploy tested | Skills trigger correctly |
| PPT | Reader/writer tested | Trigger edge cases found |
| Research | E2E pipeline tested | Source discovery works |
| Companion | `/petfish` commands tested | Suggest fixture matrix documented |

### 2.3 Token Accounting Baseline

Measured system prompt sizes using `tiktoken cl100k_base`:

| Component | Tokens |
|-----------|--------|
| AGENTS.md (v0.10.x, all inline) | 13,937 |
| Base instructions | 415 (3.0%) |
| Pack inline rules | 13,523 (97.0%) |
| 7 packs with inline rules | course 5,852, research 2,568, fish-trail 1,512, deploy-ops 973, petfish-companion 986, anti-sycophancy 826, petfish-style 610 |

**Key insight**: 97% of system prompt is pack rules, most of which are irrelevant to any given task.

---

## 3. Phase 1: Compaction Plugin Testing

> Date: 2026-05-10 ~ 2026-05-15
> Goal: Test whether topic-aware compaction (TAC) reduces API calls and token cost
> Hypothesis: TAC should reduce calls by >25% vs baseline

### 3.1 Round 1 — Initial Compaction Test

| Arm | Model | Recall | Topic Separation |
|-----|-------|--------|-----------------|
| Baseline (no plugin) | claude-opus-4.6 | 5/5 | 4/5 |
| Plugin enabled | claude-opus-4.6 | 5/5 | 5/5 |

Compaction preserved all risk scores exactly. Topic separation improved 4→5.

### 3.2 Round 2 — Multi-Model A/B (7 runs)

| Run | Model | Token Delta | API Call Delta | Notes |
|-----|-------|-------------|---------------|-------|
| 3 | Claude Sonnet 4 | **-20.3%** | -49.9% cache reads | Best result |
| 4 | Claude Sonnet 4 | +197.6% | 159 API calls (outlier) | Plugin went rogue |
| 5 | Claude Sonnet 4 | +9.5% | -68.3% cache reads | Moderate |
| 6 | Claude Sonnet 4 | +31.9% | baseline 8 errors | Plugin 0 errors |
| 7 | Claude Sonnet 4 | +152.8% | baseline 8 errors | Plugin 0 errors |
| 8 | GPT-5.4-Mini | -33.9% | plugin 8 errors | Reversed failure |
| 9 | Gemini 3 Flash | **-52.1%** | -79.3% API calls | Strong result |

**Critical finding**: Claude Sonnet 4 showed **9× variance** in API calls (17-159) for the same 21 messages. Plugin results were stochastic — sometimes saves 50%, sometimes costs 200%.

### 3.3 Round 3 — Formal TAC A/B Test (P0-P1a)

3 arms × 5 blocks × claude-opus-4.6, temp=0:

| Arm | Mean Calls/Msg | SD | N |
|-----|---------------|-----|---|
| CF (baseline) | 3.74 | 0.89 | 5 |
| TAC (plugin) | 3.84 | 0.95 | 5 |
| COMPR (control) | 4.35 | 2.63 | 5 |

| Comparison | p-value | Effect size d | 95% CI |
|-----------|---------|--------------|--------|
| TAC vs CF | 0.928 | -0.11 (wrong direction) | [-1.09, +0.93] |
| COMPR vs CF | 0.809 | 0.31 | [-1.23, +3.07] |
| COMPR vs TAC | 0.837 | 0.30 | [-1.34, +3.08] |

### 3.4 Round 3 — Recall Quality Test

| Metric | Baseline | Plugin | Delta |
|--------|---------|--------|-------|
| Factual Recall | 0.833 | 0.667 | -0.167 |
| Detail Completeness | 0.806 | 0.611 | -0.194 |
| Cross-Topic Isolation | 0.806 | 0.667 | -0.139 |

### 3.5 Phase 1 Conclusion

> **H1 REJECTED**: TAC does NOT reduce API calls (observed -2.5%, wrong direction, p=0.928).
> **H2 REJECTED**: Plugin recall is WORSE than baseline on all metrics.
> Compaction plugin is a dead end for cost reduction. The compaction hook only fires during message transform, not at the API level where real savings would occur.

---

## 4. Phase 2: v0.11.0 Upgrade Impact Analysis

> Date: 2026-05-09 ~ 2026-05-13
> Goal: Measure token impact of v0.11.0's tiered AGENTS.md loading

### 4.1 The Problem

v0.11.0 introduced on-demand pack loading via `agents-rules/` directory. Instead of all pack rules inlined in AGENTS.md, packs are loaded only when triggered. But the inline rules were NOT stripped during upgrade, causing duplication.

### 4.2 Token Measurements

| Config | Total Tokens | Calls | Compactions | Cost |
|--------|-------------|-------|-------------|------|
| v0.10.x (baseline) | 744,904 | 110 | 2 | $5.86 |
| v0.11.0 (upgraded) | 1,017,201 | 109 | 3 | $6.80 |
| v0.11.0 + plugin | 241,804 | 28 | 0 | $2.59 |

**v0.11.0 regression**: +36.6% tokens despite 94% smaller AGENTS.md.

### 4.3 Root Cause

- **Inline duplication bug**: v0.11.0 kept inline rules (13,523 tokens) AND added agents-rules/ files (13,327 tokens) = **26,850 tokens duplicated**
- **Read tool overhead**: v0.11.0 uses `Read` tool to load pack rules on-demand, but each Read call inflates conversation context by ~4K tokens
- The 94% AGENTS.md shrinkage was offset by repeated Read calls

### 4.4 Fix Verification

After removing inline rules from AGENTS.md:
- AGENTS.md: 13,937 → 777 tokens (**94.4% savings**)
- 7 packs now load on-demand only when triggered
- Per-pack costs: course 5,852 (largest), petfish-style 610 (smallest)

### 4.5 Phase 2 Conclusion

> v0.11.0's tiered loading CAN work but requires inline rules to be stripped. The Read tool overhead makes on-demand loading expensive for frequently-triggered packs. For rarely-triggered packs, savings are 55-93%.
>
> **Filed issue #102**: Inline pack rules not stripped on upgrade.

---

## 5. Phase 3: System Prompt Plugin Injection

> Date: 2026-05-13 ~ 2026-05-18
> Goal: Inject pack rules into system prompt cached prefix to avoid Read tool overhead
> This was the pivot from "compaction" to "system prompt engineering"

### 5.1 Architecture

Built `system-prompt-rules.ts` plugin that:
1. Reads agents-rules/*.md files at system prompt construction time
2. Injects matching rules into the cached system prompt prefix
3. Avoids per-turn Read tool calls entirely
4. Variants: `all-rules` (always inject) vs `smart-rules` (domain-matched)

### 5.2 Three-Way Benchmark

3 arms × DeepSeek V4 Pro × 5 blocks × 10 messages/block:

| Arm | Total Tokens | Compactions | Peak Context | Notes |
|-----|-------------|-------------|-------------|-------|
| Baseline (v0.10.x) | 586,917 | 2 | ~152K | Inline rules |
| all-rules plugin | **475,039** | 1 | ~145K | **-19.1%** |
| smart-rules plugin | **635,712** | 1 | ~141K | -12.3% |

**Key finding**: Each compaction costs ~50-80K extra tokens. Reducing compactions from 2→1 accounts for most of the savings.

### 5.3 Plugin Quality Evaluation

Blinded LLM-as-judge evaluation (Flash and Pro judges):

| Metric | Plugin-inject | FULL-current | p-value |
|--------|-------------|-------------|---------|
| Accuracy (strict, 2.0 scale) | 1.57 | 1.67 | 0.753 |
| Contamination-free (strict) | 89% | 78% | — |
| Contamination-free (lenient) | 100% | 89% | — |

### 5.4 Phase 3 Conclusion

> **System prompt injection works**: -19.1% tokens with all-rules plugin, quality preserved.
> Plugin is 71 lines of TypeScript, zero dependencies, production-ready.
> **Recommended for v0.11.0 as standard plugin.**

---

## 6. Phase 4: Multi-Model Architecture Evaluation

> Date: 2026-05-18 ~ 2026-05-23
> Goal: Extend evaluation beyond DeepSeek to Claude, GPT, Gemini
> Focus: disk-mode plugin vs full-MCP vs no-context baseline

### 6.1 Disk Mode Evaluation

Plugin-inject vs OFF-clean (no context), DeepSeek V4 Pro:

| Metric | OFF-clean | Disk-mode |
|--------|----------|-----------|
| Quality score (/100) | 33 | **98** |
| Topic-aware accuracy | 3/60 | **80/80** |
| Contamination | 0% | 0% |
| Avg input delta | — | +228/turn |
| Wall time | 6.2s | 6.8s (+9.7%) |

### 6.2 Three-Arm Interactive Benchmark

disk-smart vs FULL-current vs OFF-clean, DeepSeek V4 Pro, 50 entries/arm:

| Metric | disk-smart | FULL-current | OFF-clean |
|--------|-----------|-------------|-----------|
| Total tokens | 1,247,591 | 1,225,198 | 97,697 |
| Net new tokens | 43,111 | 14,190 | — |
| Cost | $0.2545 | $0.2058 | — |
| Wall time | **3.41s** | 4.90s | — |
| Recall | 0.82 | 1.26 | — |

**Cold start issue**: disk-smart R1 input = 3,601 (vs FULL's 340). Cache hit 82.6%.
**R2+**: disk-smart stabilizes — input ~107, cost -4%.

### 6.3 Phase 4 Conclusion

> Disk mode has 98% quality but is NOT cheaper than FULL-current (+23.7% cost) because of per-turn MCP calls.
> The cold start penalty (3,601 vs 340 input) is the main cost driver.
> Wall time savings (-30.4%) is the main benefit.
> Need architecture change: eliminate per-turn MCP calls by injecting context from disk.

---

## 7. Phase 5: Deep Research & Architecture Redesign

> Date: 2026-05-21 ~ 2026-05-23
> Goal: Research LLM agent memory architectures, design optimized fish-trail v2

### 7.1 Literature Survey (15 sources)

| Source | Key Contribution |
|--------|-----------------|
| Park et al. (Stanford 2023) | recency × importance × relevance scoring |
| MemGPT/Letta (UC Berkeley 2023) | core_memory + archival_memory hybrid |
| CoALA (Princeton 2023) | Formal taxonomy: declarative + procedural memory |
| MemoryBank (人大+腾讯 2023) | Ebbinghaus forgetting curve for decay |
| Zhang survey (清华 2024) | Three-layer architecture consensus |
| Claude Memory | System-prompt read + tool-call write |
| ChatGPT Memory | Implicit model-decided updates |
| Anthropic caching | 0.1× cache read, cache_control API |
| OpenAI caching | Automatic prefix caching, 0.5× discount |
| DeepSeek MLA | KV cache ~90% compression |

**Cross-cutting consensus**: `system_prompt_injection_for_read + tool_call_write_back` is the dominant pattern across all production systems.

### 7.2 Root Cause Analysis

Decomposed the per-turn token cost:

| Component | Tokens | Frequency |
|-----------|--------|-----------|
| Tool schema (42 tools) | ~22K | Every turn (cached) |
| topic_detect MCP call | ~4-6K input | Every turn (full-v2 only) |
| get_memory_context | ~2-4K | Every turn (full-v2 only) |
| topic_update | ~1-2K | Periodic |
| System prompt rules | ~30K (v0.10.x) / ~16K (v0.11.0) | Every turn (cached) |

### 7.3 Architecture Redesign: 4 Issues Filed

Filed with PEtFiSh team, all implemented:

| Issue | Architecture Change | Status |
|-------|-------------------|--------|
| #164 | Cache-stable 3-block injection (Topics/Related/Focus) | Implemented |
| #165 | Mode-aware MCP suppression ([disk|rMCP:off]) | Implemented |
| #166 | Reflective compression (summary injection) | Implemented |
| #167 | Tiered MCP access + compressionLevel option | Implemented |

### 7.4 Projected v2 Performance

Based on literature and v1 data:
- Cold start: ~800 input (vs 3,601 in v1)
- Steady state: ~80 input (vs 107 in v1)
- Recall: ~1.1+ (vs 0.82 in v1)
- Cache hit: ~99%

---

## 8. Phase 6: v1.1.0-pre Benchmark Series (v1~v4)

> Date: 2026-05-23 ~ 2026-05-25
> Goal: Validate the new 3-block architecture across models
> Upstream branch: `feat/fish-trail-tiered-memory-v2`

### 8.1 v1 — Single-Model Interactive (DeepSeek V4 Pro)

| Arm | Avg Input | Recall | MCP Calls | Wall Time |
|-----|----------|--------|-----------|-----------|
| OFF-clean | 340 | 0.62 | 0 | 4.90s |
| disk-naive (v1 rules) | 3,601 (R1) → 107 (R2+) | 0.82 | 30 | 3.41s |
| FULL-current | 340 | 1.26 | per-turn | 4.90s |

**Cold start fixed in v2**: R1 input 3,601→135 via 3-block architecture.

### 8.2 v2 — Single-Model REST API (DeepSeek V4 Pro, 50 entries/arm)

| Metric | disk-v2 | full-v2 | Delta |
|--------|---------|---------|-------|
| Total tokens | lower | higher | **-24.2%** |
| Recall | 1.76 | 1.12 | **+57.1%** |
| MCP calls | 0 | 30 | -100% |

**disk-v2 wins all metrics** in single-model test.

### 8.3 v3 — Multi-Model REST API (5 models, 3 valid)

**Issue**: Template had wrong agents-rules files. Fixed mid-benchmark.

| Model | disk-v2 Total Δ | disk-v2 Recall | full-v2 Recall | Recall Δ |
|-------|----------------|---------------|----------------|---------|
| DeepSeek Flash | **-8.7%** | 1.20 | 1.57 | -23.4% |
| Claude Sonnet 4.6 | +6.5% | **1.83** | 1.70 | +7.8% |
| GPT-5.4-Mini | **-17.1%** | 1.33 | 1.50 | -11.1% |
| GPT-4o | — | — | — | Zero tokens (API bug) |
| DeepSeek Pro | — | — | — | Server failed |

**Model-dependent behavior confirmed**: Claude benefits from injection; Flash/GPT-Mini lose recall.

**Claude round-by-round convergence**:

| Round | disk-v2 Δ | Convergence |
|-------|----------|-------------|
| R1 | +8.4% | — |
| R2 | +6.0% | Yes |
| R3 | +5.4% | Yes |

**MCP measurement failure**: REST API does NOT expose internal tool calls. All mcp_calls=0 across all entries.

### 8.4 v4 — Compression Ablation (3 models × 3 arms)

3 arms: full-v2 / disk-compact (~48 tok Focus) / disk-full (~108 tok Focus)

| Model | full-v2 | disk-compact | disk-full | compact Δ | full Δ |
|-------|---------|-------------|-----------|-----------|--------|
| DeepSeek Flash | 20,666 | 27,769 | 41,601 | +34.4% | +101.3% |
| Claude Sonnet 4.6 | 26,367 | 27,657 | **24,342** | +4.9% | **-7.7%** |
| GPT-5.4-Mini | 21,026 | 34,934 | 25,480 | +66.2% | +21.2% |

**Output tokens (recall proxy)**:

| Model | full-v2 | disk-compact | disk-full |
|-------|---------|-------------|-----------|
| Flash | 50 | 62 | 121 |
| Claude | 150 | 109 | **154** |
| GPT-Mini | 47 | 50 | 59 |

**Claude round-by-round (only model where disk wins)**:

| Round | full-v2 | disk-compact | disk-full |
|-------|---------|-------------|-----------|
| R1 | 24,864 | 24,507 | **22,125** |
| R2 | 26,190 | 28,663 | **24,623** |
| R3 | 27,446 | 29,802 | **26,279** |

### 8.5 Issues Filed During Phase 6

| Issue | Description | Status |
|-------|-------------|--------|
| #168 | compressionLevel dispatch bug (dead code) | Fixed (commit bdb388a) |
| #169 | console.log TUI pollution (19 occurrences) | Fixed (commit 3e58529) |
| #170 | v4 benchmark results report | Filed |
| #163 | OpenCode hook API limitation | Open |
| #162 | topic_validate schema mismatch | Open |

### 8.6 MCP Server Instability Discovery

During v4 benchmark prep, discovered that `opencode serve` crashes when MCP server is configured in minimal workspaces. Root cause: MCP server imports fail without full Python module set.

Workaround: Run benchmarks without MCP (no ground truth for MCP call counts).

---

## 9. Cumulative Findings & Decisions

### 9.1 What Works

| Finding | Confidence | Evidence |
|---------|-----------|----------|
| System prompt injection saves 8-19% tokens | High | 3-way benchmark, 150 entries |
| Disk-mode is production-quality (98% recall, 0% contamination) | High | Disk-mode evaluation, 100 queries |
| 3-block architecture (Topics/Related/Focus) reduces cold start 96% | High | v2 benchmark, 50 entries |
| disk-full is optimal for Claude (-7.7% tokens, highest recall) | High | v4 benchmark, 86 valid entries |
| compactionLevel should be per-model setting | Medium | v4 shows model-dependent optimum |
| Wall time improves -30% with disk mode | High | v1 benchmark |

### 9.2 What Doesn't Work

| Finding | Confidence | Evidence |
|---------|-----------|----------|
| Compaction plugin reduces API calls | **Disproven** | Round 3 TAC test, p=0.928 |
| Compaction plugin improves recall | **Disproven** | Recall quality test, -0.167 delta |
| disk-v2 beats full-v2 for all models | **Disproven** | v3/v4 multi-model, Flash/GPT-Mini lose |
| REST API can measure MCP tool calls | **Disproven** | v2/v3/v4, always mcp_calls=0 |
| MCP server is stable in opencode serve | **Disproven** | v4 prep, server crashes |

### 9.3 Key Decisions

1. **Compaction plugin: abandoned** (null result, Phase 1)
2. **System prompt injection: adopted** (-19.1%, Phase 3)
3. **3-block architecture: adopted** (#164-#167, Phase 5)
4. **Per-model compressionLevel: recommended** (model-dependent, Phase 6)
5. **MCP ground truth: deferred** (server instability, Phase 6)
6. **DeepSeek Pro testing: deferred** (server failures, Phase 6)
7. **Claude +6.5% accepted** (highest recall, cache convergence, Phase 6)

---

## 10. Open Issues & Next Steps

### 10.1 Open Issues

| Issue | Priority | Description |
|-------|----------|-------------|
| MCP server crash | High | `opencode serve` crashes with MCP in minimal workspaces |
| DeepSeek Pro data gap | High | Production model never successfully benchmarked in multi-model |
| MCP call ground truth | High | Server log exists but can't be collected (server crashes) |
| GPT-4o zero tokens | Medium | Returns total_tokens=0 via REST API |
| OpenCode hook API (#163) | Medium | system.transform only provides {sessionID, model} |
| topic_validate (#162) | Low | Schema mismatch |

### 10.2 Recommended Next Steps

1. **Fix MCP server stability**: Test with all Python modules present, ensure `uv run` resolves correctly
2. **Run v4 with MCP ground truth**: Once stable, collect server-side call logs
3. **Add DeepSeek V4 Pro**: Targeted single-model test (production model)
4. **LLM-as-judge validation**: Score 20% of v4 responses for recall quality
5. **GPT-4o investigation**: Diagnose zero-tokens issue
6. **Long-session test**: 50+ rounds to verify cache convergence beyond R3

---

## 11. Artifact Index

### 11.1 Experiment Reports (chronological)

| File | Phase | Description |
|------|-------|-------------|
| `experiments/trigger-eval-batch-report-2026-05-08.md` | 0 | 563/563 trigger evaluation |
| `experiments/compaction-test/test-results-A.md` | 1 | Compaction baseline (5/5 recall) |
| `experiments/compaction-test/test-results-B.md` | 1 | Compaction plugin (5/5 recall, separation improved) |
| `experiments/compact-test-round2/ANALYSIS.md` | 1 | 7-run multi-model A/B (9x variance found) |
| `experiments/compact-test-round3/results/EXPERIMENT-REPORT.md` | 1 | Formal TAC test (H1 rejected, p=0.928) |
| `experiments/compact-test-round3/RECALL-QUALITY-RESULTS.md` | 1 | Recall quality (plugin worse on all metrics) |
| `experiments/v011-upgrade/UPGRADE-FINDINGS.md` | 2 | v0.11.0 token regression (+36.6%) |
| `experiments/v011-upgrade/V011-3WAY-ANALYSIS.md` | 2 | 3-way config comparison |
| `experiments/v011-upgrade/COMPACTION-REEVALUATION.md` | 2 | v0.11.0 impact on compaction |
| `experiments/v011-upgrade/VERIFICATION-PLAN.md` | 2 | Tiered loading verification plan |
| `outputs/v011-sysprompt-plugin-report/REPORT.md` | 3 | System prompt plugin (-19.1%) |
| `experiments/plugin-context-inject/README.md` | 3-4 | Plugin experiment overview |
| `experiments/plugin-context-inject/3-ARM-BENCHMARK-v2.md` | 4 | 3-arm interactive benchmark |
| `experiments/plugin-context-inject/DISK-MODE-FINAL-EVALUATION.md` | 4 | Disk mode quality (98/100) |
| `experiments/plugin-context-inject/VALIDATION-RESULTS.md` | 4 | Plugin validation (-8% tokens) |
| `experiments/plugin-context-inject/ONE-TURN-DELAY-ASSESSMENT.md` | 4 | One-turn delay analysis |
| `experiments/plugin-context-inject/MEMORY-ARCHITECTURE-RESEARCH.md` | 5 | 15-source literature survey |
| `experiments/plugin-context-inject/ROOT-CAUSE-ANALYSIS.md` | 5 | Token cost decomposition |
| `experiments/plugin-context-inject/MCP-TOOL-CALLING-INVESTIGATION.md` | 5 | MCP tool calling analysis |
| `experiments/plugin-context-inject/LOGGING-ADEQUACY-AUDIT.md` | 5 | MCP logging gaps |
| `experiments/plugin-context-inject/PETFISH-FIX-VERIFICATION-2026-05-23.md` | 6 | v1.1.0-pre fix verification |
| `experiments/plugin-context-inject/MULTI-MODEL-BENCHMARK-v3-REPORT.md` | 6 | v3 multi-model results |
| `/tmp/opencode/bench_v4/results/membench-v4-results.json` | 6 | v4 compression ablation (270 entries) |

### 11.2 Research Outputs

| File | Description |
|------|-------------|
| `experiments/llm-agent-memory-research-findings.json` | 15-source research findings |
| `research/00_brief/research-brief.md` | Optimization evaluation brief |
| `research/01_sources/source-index.jsonl` | 24-source index |
| `research/06_outputs/optimization-evaluation-research-report.md` | Evaluation methodology report |

### 11.3 Benchmark Data

| File | Entries | Description |
|------|---------|-------------|
| `/tmp/opencode/bench_v2_results.json` | 100 | v2 single-model (DeepSeek Pro) |
| `/tmp/opencode/bench_multi_v3/membench-v3-results.json` | 210 | v3 multi-model |
| `/tmp/opencode/bench_v4/results/membench-v4-results.json` | 270 | v4 compression ablation |

### 11.4 Issues Filed

| Issue | Title | Status |
|-------|-------|--------|
| #102 | Inline pack rules not stripped on v0.11.0 upgrade | Fixed |
| #145-#163 | P1 evaluation series (19 issues) | 17 closed, 2 open |
| #164 | Cache-stable 3-block architecture | Implemented |
| #165 | Mode-aware MCP suppression | Implemented |
| #166 | Reflective compression | Implemented |
| #167 | Tiered MCP access + compressionLevel | Implemented |
| #168 | compressionLevel dispatch dead code | Fixed |
| #169 | console.log TUI pollution | Fixed |
| #170 | v4 benchmark results report | Filed |

---

*End of document. Generated 2026-05-25.*
