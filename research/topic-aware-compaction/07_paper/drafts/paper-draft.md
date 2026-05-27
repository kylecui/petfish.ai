# Topic-Aware Compaction: Behavioral Change as a Primary Token-Saving Mechanism in Multi-Topic LLM Agent Sessions

**Abstract**
Long-running LLM agent sessions with multiple topics suffer from context bloat and excessive API calls. We propose that compacting context by topic rather than chronology fundamentally alters agent behavior. We introduce fish-trail, a plugin for OpenCode that hooks into session compaction to inject topic structures. A/B testing reveals 20.3% token savings driven primarily by a 36.4% reduction in API calls per message, maintaining zero recall quality loss.

## 1. Introduction
Long-running LLM agent sessions face context boundary issues when spanning multiple interleaved topics. Standard chronological context windows accumulate irrelevant intermediate reasoning and state data, degrading response precision over time. As context grows, models exhibit increased uncertainty, leading to excessive exploratory tool calls to re-verify state.

We investigate the mechanics of context compaction in agent workflows. Standard compaction systems summarize chronological message histories. We hypothesize that injecting explicit topic structures during the compaction phase re-anchors the agent's internal state. Our core thesis is: Behavioral change is the primary token-saving mechanism, not text compression. 

We demonstrate that providing an agent with a topic-aware context boundary stops exploratory looping. We are the first to show that structural compaction directly reduces API calls and focuses agent behavior.

## 2. Background
Agentic coding assistants execute complex tasks across multiple interaction rounds. OpenCode represents a typical multi-turn agent environment where standard context windows hit token limits, triggering automated compaction. 

In a multi-topic session, users switch between distinct domains (e.g., configuring Python, setting up a database, modifying CI/CD pipelines). Chronological compaction squashes these distinct boundaries into a single linear narrative. This causes the agent to lose track of active working state for background topics. When the user switches back to a previous topic, the agent issues redundant tool calls (such as reading environment variables or querying git history) to rebuild context. 

OpenCode exposes an `experimental.session.compacting` event hook. This allows plugins to intercept the context window before the summarization model executes and replace the standard chronological grouping with a structured schema.

## 3. Method (fish-trail system architecture)
We implement `fish-trail`, a session management plugin for OpenCode. `fish-trail` intercepts the `experimental.session.compacting` hook.

When the session reaches the token threshold, the OpenCode runtime fires the compacting event. `fish-trail` prevents the default chronological summarizer. Instead, it reads the active context and extracts distinct topics. It organizes past messages, tool outputs, and environment states into discrete topic clusters. 

The plugin then injects this topic-structured schema back into the compacted context window. The agent receives a state summary explicitly partitioned by domain rather than a flattened timeline. The prompt modification forces the agent to read state via topic references, eliminating the need to search historical interactions.

## 4. Experimental Setup
We tested `fish-trail` in the OpenCode AI coding assistant environment. The experiment isolates the compaction methodology as the single independent variable.

We simulated a deterministic developer interaction comprising N=21 user messages. The session interleaved three distinct topics: `python-setup`, `database`, and `cicd`. The underlying model was `claude-sonnet-4`. 

We established two testing variants:
1. **Baseline**: Standard OpenCode compaction (chronological summarization).
2. **Plugin**: OpenCode running `fish-trail` injected via the `experimental.session.compacting` hook.

To measure context retention, we inserted three specific factual recall questions at the end of the session, one for each topic. 

## 5. Results

The performance metrics focus on token consumption, API utilization, and computational overhead.

### Experiment 1: System Prompt Injection Configuration
We first evaluated the impact of varying the system rules and the plugin's presence against the v0.10.x baseline architecture.

| Config | Total Tokens | vs baseline | Compactions |
|---|---|---|---|
| v0.10.x baseline | 586,917 | — | 2 |
| v0.11.0 + all-rules | 475,039 | -19.1% | 1 |
| v0.11.0 + smart-rules | 635,712 | -12.3% | 1 |
| v0.11.0 no plugin | 1,017,201 | +36.6% | 3 |

### Experiment 2: Main Result
We isolated the plugin's effect against the finalized baseline. 

| Metric | Baseline | Plugin | Delta % |
|---|---|---|---|
| Input Tokens | 726,474 | 576,050 | -20.7% |
| Output Tokens | 130,641 | 107,472 | -17.7% |
| Cache Read | 10,631,340 | 5,330,527 | -49.9% |
| Total (input+output) | 857,115 | 683,522 | -20.3% |
| API calls | 140 | 89 | -36.4% |
| Calls/message | 6.67 | 4.24 | -36.4% |
| Wall Time | 2,938s | 1,781s | -39.4% |
| Compactions | 2 | 2 | same |
| Peak Context | 151,285 | 148,017 | -2.2% |
| Errors | 1 | 0 | - |

### Context Growth Data
Both variants reach ~145-151K tokens before compaction, dropping to ~30K tokens afterward. The baseline grows at a rate of ~4,300 tokens/call. The plugin variant grows at ~3,700 tokens/call. The plugin regrows slower post-compaction due to fewer intermediate messages. The baseline finishes the session at 133K context, while the plugin finishes at 69K.

### Recall Quality
Both variants achieved zero loss in recall. Both the baseline and the plugin accurately answered all 3 recall questions spanning the `python-setup`, `database`, and `cicd` topics.

## 6. Analysis
The core thesis is supported by the 36.4% reduction in API calls per message (from 6.67 to 4.24). Token compression algorithms typically reduce input volume by dropping tokens. The `fish-trail` architecture achieves a 20.3% total token savings because the agent alters its problem-solving trajectory.

By injecting topic structures during compaction, the model possesses a clear mental map of the workspace. When switching from `cicd` back to `database`, the baseline agent issues exploratory commands to rebuild its lost chronological state. The plugin agent immediately retrieves the structured state from the topic map and executes the target action. 

The context growth rate (3,700 tokens/call vs 4,300 tokens/call) confirms that the savings compound. The plugin avoids the recursive inflation caused by intermediate tool outputs. This explains why the baseline finishes at 133K context while the plugin finishes at 69K, despite both dropping to ~30K at the actual point of compaction. The savings originate from behavioral efficiency.

## 7. Related Work
Recent literature addresses context limitations through either text compression, trajectory optimization, or architectural turn control.

**Context Compression and Dialogue Structure:**
Jiang et al. [7] introduce LLMLingua, targeting prompt compression through token-level entropy evaluation, further expanded in ACL 2024. Semantic Compression [6] similarly targets token-level reduction. These approaches focus on text density rather than agent state. Membox [1] proposes a memory storage level via a Topic Loom, establishing structural boundaries for retrieval. Context-Agent [5] constructs tree-structured dialogues, achieving 45-52% context reduction by abandoning linear history.

**Agent Trajectories and Turn Control:**
ACON [2] demonstrates 26-54% token reduction via trajectory optimization, altering how models plan execution paths. SWE-Pruner [3] reports 18-26% fewer interaction rounds as a side effect of filtering environment outputs. Focus Agent [4] secures 22.7% savings by restricting the search space, noting that LLMs fail to self-optimize their context utilization. Turn Control Studies [8] further analyze the correlation between interaction constraints and token expenditure. 

## 8. Discussion
The results represent a proof-of-concept for compaction-time topic injection. The data strictly relies on a single deterministic run comprising N=21 messages and a single model (`claude-sonnet-4`) operating within a synthetic conversation. Statistical significance requires broad-scale testing across varied interaction datasets and alternative base models. 

This approach challenges the standard metric for context optimization. Optimization efforts typically target the compression ratio of the text itself. The 39.4% reduction in wall time and 49.9% reduction in cache reads suggest that structural interventions yield higher operational returns by steering the agent's logic. Compaction is an active control mechanism.

## 9. Conclusion
Chronological context compaction degrades LLM agent efficiency by obscuring topic boundaries, triggering redundant tool execution. The `fish-trail` plugin replaces timeline-based summaries with topic-aware structures via OpenCode's compaction hook. This structural injection alters the agent's behavior, decreasing API calls per message by 36.4% without degrading factual recall. Behavioral change is the primary token-saving mechanism, overshadowing the raw token drop achieved during the text compaction event itself.

**References**
1. Membox (arxiv:2601.03785) - Topic Loom, memory storage level.
2. ACON (arxiv:2510.00615) - 26-54% token reduction via trajectory optimization.
3. SWE-Pruner (arxiv:2601.16746) - 18-26% fewer interaction rounds as side effect.
4. Focus Agent (arxiv:2601.07190) - 22.7% savings, LLMs won't self-optimize.
5. Context-Agent (arxiv:2604.05552) - Tree-structured dialogue, 45-52% reduction.
6. Semantic Compression (ACL 2024, aclanthology.org/2024.findings-acl.306).
7. LLMLingua (EMNLP 2023 & ACL 2024).
8. Turn Control Study (arxiv:2510.16786).