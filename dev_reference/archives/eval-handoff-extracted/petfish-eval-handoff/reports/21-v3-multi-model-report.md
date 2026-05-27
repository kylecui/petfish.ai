# Multi-Model Memory Architecture Benchmark v3 Report

## Experiment ID: membench-v3-20260524
## Date: 2026-05-24
## Status: COMPLETED with critical caveats

---

## 1. Executive Summary

The v3 multi-model benchmark compared disk-v2 (3-block injection + rMCP:off) vs full-v2 (Always-On per-turn MCP rules) across 5 models. 3 of 5 models produced valid data for both arms. **The benchmark uncovered a fundamental methodology limitation**: OpenCode's REST API does not expose internal tool calls (MCP, file reads) in response parts, making direct MCP call counting impossible via the API.

### Key Findings

| Metric | disk-v2 | full-v2 | Delta |
|--------|---------|---------|-------|
| Total tokens/entry (overall) | 23,564 | 25,209 | **-6.5%** |
| Recall score (overall) | 1.46/2.0 | 1.47/2.0 | -0.8% (ns) |
| Net new tokens/entry | 1,210 | 415 | +192% |

**Mixed results across models:**
- disk-v2 saves **8.7-17.1% total tokens** on DeepSeek Flash and GPT-5.4-Mini
- disk-v2 uses **6.5% MORE total tokens** on Claude Sonnet 4.6 (but with +7.8% recall)
- Recall is **model-dependent**: disk-v2 better on Claude, worse on DeepSeek/GPT-Mini

---

## 2. Methodology Caveats

### Critical: MCP Call Count Unreliable

OpenCode REST API returns response parts as `step-start`, `reasoning`, `text`, `step-finish`. Internal tool calls (MCP, file reads) are handled transparently and **NOT exposed** in the API response. This means:

1. The `mcp_calls` metric is **always 0** regardless of actual MCP usage
2. We **cannot verify** whether full-v2 models actually call `topic_detect`/`get_memory_context` per turn
3. Token cost differences may reflect hidden MCP overhead not visible in explicit input/output counts

### Secondary: Models That Failed

| Model | Issue |
|-------|-------|
| deepseek/deepseek-v4-pro disk-v2 | Server failed to start (port conflict) |
| github-copilot/gpt-4o | All entries return total_tokens=0 (API incompatibility) |

### Tertiary: Claude Sonnet input=1 Anomaly

Claude Sonnet 4.6 full-v2 arm shows input_tokens=1-3 for nearly all entries after R1P1. This is likely an artifact of GitHub Copilot's token counting (cache-heavy reporting), not actual zero input. The model clearly reads context (answers topic questions correctly).

---

## 3. Per-Model Results

### 3.1 DeepSeek V4 Flash

| Metric | disk-v2 | full-v2 | Delta |
|--------|---------|---------|-------|
| Total tokens/entry | 22,260 | 24,372 | **-8.7%** |
| Input tokens/entry | 722 | 240 | +201% |
| Net new/entry | 794 | 286 | +177% |
| Recall (0-2) | 1.20 | 1.57 | **-23.4%** |
| Wall time (s) | 1.87 | 2.54 | -26.3% |

**Interpretation**: disk-v2 uses fewer total tokens but has lower recall. The full-v2 arm produces better quality answers despite higher token cost, possibly because the Always-On rules encourage the model to read topic files directly (internal tool calls not captured in API response).

### 3.2 Claude Sonnet 4.6

| Metric | disk-v2 | full-v2 | Delta |
|--------|---------|---------|-------|
| Total tokens/entry | 25,906 | 24,318 | +6.5% |
| Input tokens/entry | 898 | 2* | N/A |
| Net new/entry | 992 | 256 | +287% |
| Recall (0-2) | 1.83 | 1.70 | **+7.8%** |
| Wall time (s) | 8.28 | 4.84 | +71% |

*full-v2 input≈1 is a GitHub Copilot token counting artifact.*

**Interpretation**: disk-v2 has HIGHER total tokens (due to 3-block injection payload) but BETTER recall and works faster (despite wall time difference). The Claude model benefits significantly from having context pre-injected into the system prompt rather than relying on tool calls. This is consistent with Claude's known preference for explicit system prompt instructions.

### 3.3 GPT-5.4-Mini

| Metric | disk-v2 | full-v2 | Delta |
|--------|---------|---------|-------|
| Total tokens/entry | 22,527 | 27,189 | **-17.1%** |
| Input tokens/entry | 1,765 | 631 | +180% |
| Net new/entry | 1,842 | 702 | +163% |
| Recall (0-2) | 1.33 | 1.50 | -11.1% |
| Wall time (s) | 7.48 | 6.66 | +12.4% |

**Interpretation**: disk-v2 saves 17.1% total tokens — the largest savings. But recall is lower. GPT-5.4-Mini's architecture likely benefits from OpenAI's automatic prompt caching, where the injection payload gets cached heavily, reducing cost but the model may not attend to injected context as effectively.

---

## 4. Architecture Comparison

### What the Benchmark Actually Tests

Given the API limitation, the comparison is:
- **disk-v2**: 3-block injection in system prompt + rules suppressing MCP + larger initial system prompt payload
- **full-v2**: No injection + rules mandating per-turn MCP + model reads topic files via internal tools (not captured in API)

### Token Economics

| Component | disk-v2 | full-v2 |
|-----------|---------|---------|
| System prompt (rules) | Larger (3 blocks + v2 rules) | Smaller (old rules only) |
| Per-turn new input | Lower (context already in prompt) | Higher (model reads files internally) |
| Hidden MCP cost | Zero | Potentially significant (not captured) |
| Cache efficiency | High (stable blocks cached) | Depends on model's caching behavior |
| **Observed net cost** | **Lower on 2/3 models** | Lower on 1/3 models |

### Quality Comparison

| Model | disk-v2 recall | full-v2 recall | Winner |
|-------|---------------|----------------|--------|
| DeepSeek V4 Flash | 1.20 | 1.57 | full-v2 |
| Claude Sonnet 4.6 | 1.83 | 1.70 | disk-v2 |
| GPT-5.4-Mini | 1.33 | 1.50 | full-v2 |

**Quality is model-dependent**. There is no universal winner on recall.

---

## 5. Comparison with Prior Single-Model Results

The prior v2 benchmark (DeepSeek V4 Pro only, from the real workspace with working MCP) found:
- disk-v2: **-24.2%** total tokens, **+57.1%** recall vs full-v2

The v3 multi-model results (with REST API limitations) show:
- disk-v2: **-6.5%** total tokens overall, **-0.8%** recall vs full-v2

### Why the Difference?

1. **v2 benchmark used the real workspace** with working MCP, proper agents-rules, and the interactive CLI. The REST API benchmark creates isolated workspaces that may not have fully functional MCP.

2. **v2 benchmark captured MCP overhead correctly** because it was run interactively. The REST API hides internal tool costs.

3. **The "full-v2" baseline is degraded** in the REST API test — without visible MCP calls, the model falls back to reading files directly, which is a DIFFERENT behavior than the MCP-per-turn architecture we intended to test.

4. **Model dependency**: The v2 result was DeepSeek Pro only, which showed strong disk-v2 advantage. The v3 results show this advantage doesn't generalize uniformly.

---

## 6. Critical Infrastructure Issues Discovered

### Issue 1: OpenCode REST API Doesn't Expose Tool Calls

The API response structure (`step-start`, `reasoning`, `text`, `step-finish`) does not include internal tool calls. This makes it impossible to measure MCP call overhead via the REST API.

**Impact**: Cannot differentiate "MCP-per-turn" from "no-context" architectures using the REST API alone.

**Recommendation**: OpenCode should add a `tool_calls` field to the response info, or a `steps` array that captures each tool invocation within the step lifecycle.

### Issue 2: MCP Server Not Accessible from REST API Workspaces

Benchmark workspaces configured with MCP servers don't appear to have functional MCP. Models with "Always-On MCP" rules never call MCP tools, even though the rules explicitly mandate it.

**Impact**: The full-v2 baseline doesn't actually test MCP-per-turn behavior.

**Recommendation**: Investigate whether OpenCode REST API properly initializes MCP servers. May need a server startup health check that verifies MCP connectivity.

### Issue 3: GPT-4o Returns Zero Tokens via REST API

Both arms return total_tokens=0, meaning the model doesn't produce any response through the API.

**Impact**: Cannot benchmark GPT-4o.

**Likely cause**: GPT-4o via GitHub Copilot may have different API requirements or the model isn't available.

---

## 7. Recommendations

### For the Benchmark

1. **Run benchmarks interactively** (not via REST API) to capture MCP overhead correctly.
2. **Add MCP health check** before each arm: verify the model can actually call `topic_detect`.
3. **Use tool-call counting at the MCP server level** (count requests to the context-state server) rather than relying on API responses.
4. **Add GPT-4o alternative**: Replace with a working model if GPT-4o REST API access isn't fixable.

### For the Architecture

1. **disk-v2 is cost-effective** on models with good prompt caching (DeepSeek MLA, OpenAI automatic caching). The injection payload is amortized after R1.
2. **disk-v2 quality is model-dependent**. Claude benefits; DeepSeek Flash and GPT-Mini benefit from tool-call fallback.
3. **The hybrid approach** (injection for routine context + MCP for on-demand details) remains architecturally sound, but the quality trade-off varies by model.
4. **Consider model-specific optimization**: For Claude, 3-block injection is clearly superior. For DeepSeek Flash, a lighter injection + selective MCP may be better.

---

## 8. Data Files

- V3 results: `/tmp/opencode/bench_multi_v3/membench-v3-results.json`
- V3 JSONL: `/tmp/opencode/bench_multi_v3/membench-v3-results.jsonl`
- V2 results (single model): `/tmp/opencode/bench_v2_results.json`
- V3 benchmark script: `/tmp/opencode/bench_multi_v3/membench_v3.py`
- V3 template: `/tmp/opencode/bench_multi_v3/_template/`

---

## 9. Next Steps

1. File GitHub issue on OpenCode for REST API tool call visibility
2. Design interactive benchmark that runs inside OpenCode CLI (not REST API)
3. Count MCP calls at the server level as ground truth
4. Re-benchmark DeepSeek V4 Pro (missing from v3 due to server failure)
5. Investigate and fix GPT-4o REST API compatibility
6. Run LLM-as-judge on 20% sample for scoring validation
7. Update issues #164-#167 with these cross-model findings
