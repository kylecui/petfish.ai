# Bibliography & Core Papers

## Primary References

1. **Membox (arxiv:2601.03785, 2026.01)**
   * *Relevance*: Introduces Topic Loom and topic-grouped memory.
   * *Positioning*: Operates at memory storage level. We operate at compaction injection.

2. **ACON: Agent Context Optimization (arxiv:2510.00615, 2025.10)**
   * *Relevance*: Achieves 26 to 54% token reduction via trajectory optimization.
   * *Positioning*: Focuses on trajectories rather than behavioral shifts through topic compaction.

3. **SWE-Pruner (arxiv:2601.16746, 2026.01)**
   * *Relevance*: Code agent context pruning. Shows 18 to 26% fewer interaction rounds.
   * *Positioning*: Observes behavioral change as a side effect. We target it directly.

4. **Focus Agent (arxiv:2601.07190, 2026.01)**
   * *Relevance*: Shows 22.7% token savings and proves LLMs will not self-optimize context efficiency.
   * *Positioning*: Reinforces the need for structural interventions like fish-trail.

5. **Context-Agent (arxiv:2604.05552, 2026.04)**
   * *Relevance*: Uses tree-structured dialogue for a 45 to 52% token reduction.
   * *Positioning*: Validates structured context but targets dialogue trees, not topic compaction hooks.

6. **Semantic Compression (ACL 2024)**
   * *Link*: aclanthology.org/2024.findings-acl.306
   * *Relevance*: Uses topic modeling and divide-and-conquer.
   * *Positioning*: Closest overlap risk. We differ by operating at compaction hooks and emphasizing behavioral change as the primary mechanism.

7. **LLMLingua Series (EMNLP 2023 & ACL 2024)**
   * *Relevance*: Foundational Microsoft Research work on prompt compression.
   * *Positioning*: Classic compression baseline. We argue against relying solely on compression.

8. **Turn Control Study (arxiv:2510.16786)**
   * *Relevance*: Demonstrates that context and turn constraints induce behavioral change.
   * *Positioning*: Supports our core thesis that structural changes alter LLM behavior.

## Supplementary References

* **OpenCode**: The AI coding assistant serving as the testbed environment (GitHub).
* **fish-trail**: The system description for the topic governance plugin handling the compaction hook.
