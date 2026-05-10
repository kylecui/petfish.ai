# Test Protocol: Phase 1 Fish-Trail Compaction Plugin

## Objective

Quantitatively measure whether injecting fish-trail topic context into OpenCode's compaction flow improves context quality and token efficiency.

## What We're Measuring

1. **Context quality after compaction** — does the summary preserve topic-relevant info better?
2. **Topic recall** — after compaction, can the LLM recall topic-specific details?
3. **Token consumption** — via LLM provider dashboard (Anthropic/OpenAI usage page)

## Prerequisites

- OpenCode with `.opencode/plugin/fish-trail-compaction.ts` in place
- fish-trail MCP running (topic registry populated)
- An active topic set in `.petfish/fish-trail/topic-registry.json`

## Test Procedure

### Round A: Baseline (plugin disabled)

1. **Rename** `.opencode/plugin/fish-trail-compaction.ts` → `.opencode/plugin/fish-trail-compaction.ts.disabled`
2. Start a **new OpenCode session**
3. Work through this **scripted multi-topic conversation** (aim for ~80K+ tokens to trigger compaction):

```
Turn 1: "Let's discuss the fish-trail topic detection algorithm. How does topic_detect work?"
Turn 2: [Follow up with 2-3 detailed questions about topic detection]
Turn 3: "Now switch topic — let's talk about the installer scripts. How does remote-install.ps1 handle pack resolution?"
Turn 4: [Follow up with 2-3 questions about installer internals]
Turn 5: "Back to topic detection — what were the risk thresholds we discussed?"  ← RECALL TEST
Turn 6: "What specific details did we cover about topic_detect's confidence scoring?" ← DEEP RECALL TEST
```

4. **After compaction triggers** (you'll see the response pause briefly), ask:

```
Turn N: "Summarize everything we discussed about topic detection specifically."
Turn N+1: "What were the exact risk threshold numbers for topic_detect?"
```

5. **Collect data** (see Data Collection below)

### Round B: Plugin enabled

1. **Restore** plugin: rename `.ts.disabled` → `.ts`
2. Set active topic to something matching topic detection (e.g., create a topic titled "Fish-trail topic detection algorithm")
3. **Repeat the exact same scripted conversation** in a new session
4. **Collect same data**

## Data Collection

After each round, collect these 5 items and save to a file `test-results-{A|B}.md`:

### Item 1: Recall Score (manual, 1-5)

After compaction, ask the recall test questions. Score:

- 5 = Perfect recall of specific details (thresholds, function names, etc.)
- 4 = Correct general recall, some specifics lost
- 3 = Vague recall, major details lost
- 2 = Mostly forgotten, generic response
- 1 = No recall at all

### Item 2: Compaction summary capture

Right after compaction triggers, ask:

```
"What is your current understanding of our conversation so far? Please be comprehensive."
```

Save the full response verbatim.

### Item 3: Topic separation score (manual, 1-5)

In the compaction summary, does the LLM clearly separate the two topics?

- 5 = Topics clearly delineated with accurate details
- 4 = Topics separated but some details mixed
- 3 = Topics partially mixed
- 2 = Topics largely conflated
- 1 = No distinction between topics

### Item 4: Token usage from provider dashboard

Go to your LLM provider's usage dashboard (Anthropic Console / OpenAI Usage):

- Total input tokens for the session
- Total output tokens for the session
- Number of API calls

### Item 5: Session message count

Ask the LLM:

```
How many messages are in this conversation?
```

## Results Template

```markdown
# Test Results - Round {A|B}

**Date**: 
**Plugin**: enabled / disabled
**Active Topic** (Round B only): 
**LLM Model**: 
**Compaction triggered at turn**: ~

## Scores
- Recall Score (topic detection details): /5
- Topic Separation Score: /5

## Compaction Summary (verbatim)
> [paste full response here]

## Recall Test Response (verbatim)
> [paste "summarize topic detection" response here]

## Token Usage (from provider dashboard)
- Input tokens: 
- Output tokens: 
- Total API calls: 

## Message count: 

## Notes
[Any observations about response quality, speed, behavior differences]
```

## Analysis Plan

With the two results files, the following comparisons will be made:

| Metric | Method | Expected Phase 1 Impact |
|--------|--------|------------------------|
| Topic recall quality | Recall scores A vs B | B should score higher |
| Topic separation | Separation scores A vs B | B should show clearer delineation |
| Summary quality | Compare verbatim summaries | B should mention active topic more prominently |
| Token efficiency | Provider dashboard numbers | B may show ~10-15% less input tokens over full session |
