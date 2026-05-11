# Paper Plan: Topic-Aware Compaction

## Title Candidates
* Topic-Aware Compaction: Behavioral Change as a Primary Token-Saving Mechanism in Multi-Topic LLM Agent Sessions

## Target Venues
* **Primary**: COLM 2026
* **Backup**: EMNLP 2026 Findings

## Abstract Skeleton
Long-running LLM agent sessions with multiple topics often suffer from context bloat and excessive API calls. We propose that compacting context by topic rather than chronology fundamentally alters agent behavior. We introduce fish-trail, a plugin for OpenCode that hooks into session compaction to inject topic structures. A/B testing reveals 20.3% token savings driven primarily by a 36.4% reduction in API calls per message, maintaining zero recall quality loss. These findings show that context management should optimize for agent behavioral efficiency rather than strict token compression rates.

## Key Narrative
The core contribution is that topic-structured compaction causes **behavioral change**. The agent makes fewer API calls and produces more focused responses. This behavioral shift is the primary token-saving mechanism, not traditional text compression.

## Section Outline
1. **Introduction**
   * Problem: Multi-topic session bloat causes agent thrashing.
   * Standard compression fails to address behavioral inefficiency.
   * Insight: Topic structure changes behavior and saves tokens.
2. **Background**
   * Context window limitations in agentic sessions.
   * Current compaction hooks and strategies.
3. **Method**
   * The fish-trail system architecture.
   * Implementation of topic-aware compaction via the `experimental.session.compacting` plugin hook.
4. **Experimental Setup**
   * Testing environment: OpenCode with claude-sonnet-4.
   * Baseline vs. fish-trail compaction.
5. **Results**
   * Primary metrics: 20.3% token savings, 4.2 vs 6.7 API calls.
   * Secondary metrics: Wall time and cache reads.
6. **Analysis**
   * Deconstructing the mechanism: behavioral change vs. compression.
   * Zero recall quality loss validation.
7. **Related Work**
   * Semantic compression, agent context optimization, topic-structured memory.
8. **Discussion**
   * Implications for future agent architecture.
   * Limitations of the current study.
9. **Conclusion**
   * Summary of findings and future directions.
