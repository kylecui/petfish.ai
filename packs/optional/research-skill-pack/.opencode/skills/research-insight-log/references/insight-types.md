# Insight Types

## Classification

| Type | Meaning | Example |
|---|---|---|
| `analogy` | Connection between two concepts from different domains | "rSwitch is like a Reference Monitor for the network" |
| `hypothesis` | Testable proposition | "XDP pipeline cannot be bypassed because..." |
| `research-question` | New question arising from reading | "Does Zero Trust require PEP at every hop?" |
| `method-idea` | Possible research or analysis method | "Could use formal verification on the policy chain" |
| `experiment-idea` | Possible experiment or test | "Benchmark XDP vs iptables under 10M flows" |
| `product-opportunity` | Potential product feature or market gap | "No open-source tool does X yet" |
| `planning-judgment` | Strategic or planning inference | "Market will consolidate within 2 years based on..." |
| `contradiction` | Observed conflict between sources | "Paper A says X, Paper B says not-X" |
| `terminology` | New term or concept naming | "Call this pattern 'policy-as-forwarding'" |
| `writing-angle` | Potential angle for a paper/report section | "Frame contribution as 'first XDP-native PEP'" |

## Status Lifecycle

```
open → validated (evidence found)
open → rejected (evidence contradicts)
open → merged (absorbed into another insight or evidence)
```

## Quality Criteria

A good insight entry must:
1. Have a concise, descriptive title
2. State what triggered it (sources, notes, context)
3. Explain its potential value
4. List at least one validation question
5. Not claim truth — only potential

## Anti-patterns

- Vague titles: "interesting idea" — useless for retrieval
- No trigger: insight without context cannot be validated
- No validation path: if you can't test it, it's just a feeling
- Treating insight as fact: insights need promotion through evidence
