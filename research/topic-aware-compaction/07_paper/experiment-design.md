# Experiment Design

## Current A/B Test Results

These baseline metrics validate the fish-trail compaction system:
* **Token Savings**: 20.3% total reduction.
* **API Calls**: 4.2 per message versus 6.7 per message (36.4% drop).
* **Cache Reads**: 49.9% reduction.
* **Wall Time**: 39.4% reduction.
* **Quality**: Zero recall quality loss.
* **Setup Conditions**: N=21 messages, 3 interleaved topics, claude-sonnet-4, 2 compactions on both sides.

## Ablation Experiments to Run

### 1. Compression-Only Ablation
* **Hypothesis**: Standard compression alone yields fewer savings than structural behavioral shifts.
* **Setup**: Apply the topic-structured summary template but force the agent to execute exactly the same number of API calls as the baseline.
* **Expected Outcome**: Token savings diminish significantly.
* **Proves**: Isolates the compression benefit. Confirms behavioral change drives the savings.

### 2. Behavioral-Only Ablation
* **Hypothesis**: Forcing fewer API calls without topic structure degrades quality.
* **Setup**: Use the default compaction summary but strictly constrain the API calls to match the fish-trail frequency (4.2 per message).
* **Expected Outcome**: Savings emerge, but task completion and recall suffer.
* **Proves**: Topic structure is required to maintain quality when reducing API calls.

### 3. Topic Count Scaling
* **Hypothesis**: Savings scale non-linearly with the number of interleaved topics.
* **Setup**: Run sessions with 2, 3, 5, and 7 topics.
* **Expected Outcome**: The delta between baseline and fish-trail widens as topics increase.
* **Proves**: The mechanism specifically resolves multi-topic interference.

### 4. Single-Topic Control
* **Hypothesis**: Topic-aware compaction offers negligible benefits when only one topic exists.
* **Setup**: Run a long session focused entirely on a single topic.
* **Expected Outcome**: Minimal difference between fish-trail and baseline.
* **Proves**: The topic structure mechanism specifically targets multi-topic complexity.

### 5. Compaction Timing
* **Hypothesis**: Triggering compaction earlier prevents context bloat from corrupting behavior.
* **Setup**: Test compaction triggers at 25%, 50%, and 75% context window thresholds.
* **Expected Outcome**: Finding an optimal threshold that maximizes API call reduction without dropping context.
* **Proves**: Identifies the exact moment behavioral thrashing begins.

### 6. Model Variation
* **Hypothesis**: Behavioral shift occurs consistently across modern LLMs.
* **Setup**: Run identical A/B tests using GPT-4o and Gemini 1.5 Pro.
* **Expected Outcome**: Similar reductions in API calls per message.
* **Proves**: The phenomenon relies on general LLM attention mechanisms, not specific model quirks.

### 7. Conversation Length Scaling
* **Hypothesis**: Longer sessions amplify the API call disparity.
* **Setup**: Test sessions spanning 50 and 100 messages.
* **Expected Outcome**: Baseline API calls continue to climb, while fish-trail maintains a steady rate.
* **Proves**: Compaction sustains long-term agent efficiency.
