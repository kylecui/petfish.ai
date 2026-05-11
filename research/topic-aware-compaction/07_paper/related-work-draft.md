# Related Work Draft

## Context Compression in LLMs
Early approaches to context management focused heavily on prompt compression. Foundational methods like LLMLingua established techniques for reducing token counts while preserving semantic meaning. Subsequent work explored semantic compression using topic modeling and divide-and-conquer strategies. These methods treat the language model as a passive receiver of text. They aim to pack more information into fewer tokens without considering how the structure of that information affects subsequent agent decisions. Our approach moves beyond passive text compression to examine active behavioral shifts.

## Agent Context Optimization
Recent research shifts focus from static prompts to dynamic agent trajectories. Systems like ACON demonstrate significant token reductions by optimizing the agent context window directly. Similarly, SWE-Pruner prunes context for coding agents, noting a reduction in interaction rounds as a side effect. Focus Agent and Context-Agent further highlight that language models do not self-optimize their context efficiency. They rely on external tree-structured dialogues or constraints to maintain focus. These systems optimize the environment but often overlook the specific mechanics of multi-topic interference.

## Topic-Structured Memory
Managing multiple topics requires specialized memory architectures. Membox introduces Topic Loom to create topic-grouped memory structures. While effective for long-term retrieval, this operates primarily at the memory storage level rather than the immediate context window. Grouping memories improves search but does not inherently restructure the immediate prompt to prevent agent thrashing during active multi-topic sessions.

## Our Positioning
We introduce a mechanism that bridges context optimization and topic-structured memory. We are the first to use compaction-time topic injection as a mechanism for behavioral change. By intervening at the `experimental.session.compacting` hook, fish-trail restructures the immediate context before the agent sees it. This proves that structural compaction directly reduces API calls and focuses agent behavior. Behavioral change becomes the primary token-saving mechanism, rendering raw text compression secondary.
