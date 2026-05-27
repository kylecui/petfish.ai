# Writing Guide & Reviewer Anticipation

## Anticipated Reviewer Questions & Strategies

1. **"How do you separate compression savings from behavioral change?"**
   * *Response Strategy*: Point directly to the compression-only ablation experiment. We show that when API calls are held constant, token savings drop drastically. This proves behavioral efficiency is the primary driver.

2. **"N=21 is too small for a definitive conclusion."**
   * *Response Strategy*: Discuss the statistical power of the initial test and outline the extended ablation experiments running up to 100 messages. Emphasize that the effect size (36.4% drop in API calls) is large enough to show significance even at smaller scales.

3. **"Only tested on one model (claude-sonnet-4)."**
   * *Response Strategy*: Acknowledge this limitation in the current results and refer to the multi-model ablation tests (GPT-4o, Gemini). Frame the current findings as a proof-of-concept for a model-agnostic architectural intervention.

4. **"How does this differ from semantic compression (ACL 2024)?"**
   * *Response Strategy*: Clarify that semantic compression operates at the prompt level to reduce token count passively. Our method hooks directly into active agent session compaction. For us, behavioral change is the *primary* goal; token compression is a byproduct.

5. **"Is this just prompt engineering?"**
   * *Response Strategy*: Emphasize the system architecture. This is a plugin-level intervention hooking into `experimental.session.compacting`. It fundamentally alters the agent loop rather than merely appending a system prompt instruction.

## COLM 2026 Venue Tips
* **Focus on Methodology**: Detail the exact compaction hook mechanics. Reviewers want to know *how* the structure alters the agent loop.
* **Prioritize Reproducibility**: Outline the OpenCode testing environment clearly. Ensure the metrics (API calls, cache reads, wall time) are clearly defined.

## Language and Style
* The paper can be written in English or Chinese based on author preference.
* Use clear, problem-driven analysis. Maintain an evidence-based tone.
* **Anti-Slop Rules**: Write naturally. Avoid filler words. Do not use corporate jargon. Rely on varied sentence structures and precise vocabulary.

## Key Selling Points
* **Behavior > Compression**: Traditional methods chase token reduction. We chase focused agent behavior.
* **Zero Quality Loss**: The massive drop in API calls and token usage comes with exactly zero degradation in recall.
* **Real-World Validity**: The fish-trail plugin is actively deployed in OpenCode, providing production-level insights.

## Common Pitfalls to Avoid
* **Overclaiming**: Do not claim this solves all context issues. It solves multi-topic interference.
* **Ignoring Limitations**: Openly discuss edge cases, such as single-topic performance where the mechanism yields minimal benefit.
