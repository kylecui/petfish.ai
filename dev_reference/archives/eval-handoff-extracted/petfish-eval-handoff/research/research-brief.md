# Research Brief

## 1. Research Title
Agent Memory Architecture: Optimization Directions and Evaluation Methodology for Cache-Stable System-Prompt Injection

## 2. Research Type
- [x] Scientific Research (empirical evaluation methodology, reproducibility)
- [x] Planning / Strategy Research (architecture optimization roadmap)
- [ ] Mixed: Scientific + Planning

## 3. Background

PEtFiSh fish-trail implements a cache-stable 3-block memory injection architecture (#164-#167) for AI agent topic governance. The v3 multi-model benchmark across 3 providers (DeepSeek/Claude/GPT) revealed:

1. **MCP call measurement is impossible via REST API** — OpenCode hides internal tool calls, producing mcp_calls=0 for all entries regardless of actual usage
2. **Quality is model-dependent** — disk-v2 wins on Claude (+7.8% recall) but loses on DeepSeek Flash (-23.4%) and GPT-Mini (-11.1%)
3. **Token savings are inconsistent** — disk-v2 saves 8.7-17.1% on 2/3 models but costs +6.5% on Claude
4. **The evaluation methodology itself is flawed** — REST API benchmarks can't capture the full cost of MCP-per-turn architectures; interactive benchmarks lack statistical rigor and scalability

These findings raise fundamental questions about:
- Whether injection-only architecture is universally optimal
- How to properly evaluate memory architectures when tool call costs are hidden
- What optimization directions are worth pursuing given the model-dependent behavior

## 4. Core Question

How should we optimize and evaluate agent memory architectures given (a) model-dependent quality trade-offs and (b) measurement infrastructure limitations?

## 5. Sub-questions

### SQ-1: What evaluation frameworks exist for agent memory architectures?
Specifically: How do Letta (MemGPT), Claude (artifacts/memory), ChatGPT (memory), Cursor (context), and academic systems handle the measurement problem? What metrics do they use? How do they account for hidden costs (tool calls, multi-turn overhead, cache amortization)?

### SQ-2: Is injection-only architecture suboptimal for certain model families?
The v3 data suggests Claude benefits from injection while DeepSeek Flash/GPT-Mini benefit from tool-call fallback. What determines this split? Is it:
- Model attention to system prompt vs. tool call context?
- Model's instruction-following capability tier?
- Provider-specific caching behavior?
- Something else?

### SQ-3: What optimization dimensions exist beyond injection vs. MCP?
Current comparison is binary (inject vs. call). What alternative architectures exist?
- Adaptive injection (model-tier aware compression)?
- Speculative injection + verification?
- Hybrid: injection for read + deferred write?
- Budget-constrained attention allocation?
- Prompt compression / distillation for injection payloads?

### SQ-4: How to build a rigorous evaluation pipeline that captures true costs?
The REST API limitation means MCP call costs are invisible. What measurement approaches could work?
- Server-side logging at MCP layer
- Token counting as proxy for total cost
- Model-internal evaluation (ask the model to self-report tool usage)
- Provider billing API integration
- Comparison against known baselines

### SQ-5: What are the most promising near-term optimization directions?
Given implementation constraints (OpenCode plugin system, provider API limitations, model availability), which optimizations are:
- High-impact, low-cost (quick wins)
- High-impact, medium-cost (next sprint)
- High-impact, high-cost (strategic bets)

## 6. Scope

### In Scope
- Evaluation methodology design for agent memory architectures
- Architecture optimization directions (3-block, hybrid, adaptive)
- Model-dependent behavior analysis and mitigation
- Measurement infrastructure recommendations
- Comparison with industry systems (Letta, Claude, ChatGPT, etc.)
- Academic literature on agent memory evaluation

### Out of Scope
- Implementation of specific optimizations (separate task)
- Non-memory architecture topics (prompt engineering, RAG, fine-tuning)
- Provider-specific API optimization (rate limits, batching)
- Multi-agent memory sharing (not yet in scope for fish-trail)
- Real_user_ studies (we only benchmark with synthetic prompts)

## 7. Expected Output
- [ ] Literature review: agent memory evaluation frameworks
- [ ] Comparison matrix: industry systems' memory + evaluation approaches
- [ ] Architecture optimization proposal with trade-off analysis
- [ ] Evaluation methodology design document
- [ ] Prioritized optimization roadmap

## 8. Evidence Requirements
- Minimum source count: 20 (10 academic, 5 industry, 5 internal)
- Required source types: paper, official-doc, code-repo, internal-doc
- Freshness requirement: 2024+ preferred; seminal works any date
- Must include opposing evidence: yes (systems where injection is WORSE than MCP)

## 9. Decision Criteria
Research is actionable if it produces:
1. A testable hypothesis about model-dependent optimization
2. An evaluation methodology we can implement within 1 sprint
3. A ranked list of optimization investments with expected ROI

## 10. Constraints
- Language: English + Chinese mixed (petfish project convention)
- Data: Only OpenCode-authenticated models available for benchmarking
- Evaluation: REST API has tool call visibility gap; interactive evaluation is slow
- Time: No hard deadline, but findings should inform v0.8 architecture decisions
- Format: Markdown research report + prioritized action items

## 11. Open Questions
- Can we get provider billing APIs for ground-truth cost measurement?
- Is Letta v0.7+ Memory Blocks API stable enough for comparison?
- Should we file an OpenCode feature request for tool call visibility before designing evaluation?
- What is the minimum benchmark sample size for statistically meaningful model-dependent analysis?
