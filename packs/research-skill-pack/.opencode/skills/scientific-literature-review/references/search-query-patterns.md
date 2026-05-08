# Search Query Patterns

## 1) Query design principles

Search quality determines review quality. Query design should maximize relevant recall while keeping precision controllable. Treat queries as versioned research artifacts, not disposable prompts.

Core principles:

- separate concept groups,
- include synonym expansion,
- preserve exclusion logic,
- log each revision and reason,
- test across databases before screening.

A baseline composition pattern:

`(problem terms) AND (method terms) AND (context terms)`

Expanded pattern with evaluation:

`(problem) AND (method) AND (context) AND (evaluation OR benchmark OR metric)`

Noise control pattern:

`(core expression) NOT (irrelevant term set)`

## 2) Boolean templates you can adapt

### Template A: problem centric

`("policy enforcement" OR "access control") AND (network OR "data plane") AND (security OR zero trust)`

### Template B: method centric

`(eBPF OR XDP OR "in-kernel filtering") AND (enforcement OR monitoring) AND (latency OR throughput OR overhead)`

### Template C: evaluation centric

`("intrusion detection" OR "threat detection") AND (benchmark OR evaluation) AND (precision OR recall OR false positive)`

### Template D: transfer centric

`("domain transfer" OR adaptation) AND (security OR "network defense") AND (dataset OR workload)`

Use templates as starting points. Final queries should map directly to your RQ scope and terminology.

## 3) Google Scholar patterns

Strength: very broad coverage.
Weakness: high noise and inconsistent metadata.

Useful syntax patterns:

- exact phrase: `"reference monitor"`
- title focused: `allintitle: "policy enforcement" network`
- year window via UI filters plus manual log
- optional site constraints for locating canonical versions

Recommended use:

- broad discovery for seed papers,
- phrase variants for terminology mapping,
- citation graph expansion from seed results.

Avoid treating Scholar ranking as relevance truth. Ranking is not methodological quality.

## 4) Semantic Scholar patterns

Strength: better structured metadata and citation navigation.
Weakness: coverage gaps for some venues.

Effective workflow:

1. run broad query,
2. identify high relevance seeds,
3. expand through citation and related graph,
4. backfill missing venues in IEEE/ACM.

Example:

`"zero trust" "policy enforcement" eBPF evaluation`

Log result count and query timestamp to preserve reproducibility.

## 5) arXiv patterns

Strength: early frontier signals.
Weakness: peer review status varies.

Syntax habit:

- include category constraints where possible (for example cs.CR, cs.NI),
- include date range,
- pair with venue indexed sources for validation.

Example expression:

`("zero trust" OR "software-defined perimeter") AND (eBPF OR XDP) AND (latency OR throughput)`

When using arXiv claims, note version and peer review status in matrix notes.

## 6) IEEE Xplore patterns

Strength: strong engineering and systems coverage.
Weakness: query syntax can be field sensitive.

Practical pattern:

- run metadata focused search first,
- then refine by publication year and document type,
- export records for matrix prefill.

Example:

`("policy enforcement" AND "data plane") AND ("zero trust" OR eBPF)`

Always log whether query ran in metadata only or full text mode.

## 7) ACM Digital Library patterns

Strength: software/system/HCI breadth with venue metadata.
Weakness: terminology differences across communities.

Practical pattern:

- combine keyword query with venue filtering,
- inspect ACM CCS terms when available,
- track duplicate records across venue and preprint versions.

Example:

`("network security" AND enforcement) AND (kernel OR eBPF) AND evaluation`

## 8) Snowball strategy

Keyword search misses semantically related work with different vocabulary. Snowballing closes this gap.

### Backward snowball

From each seed paper, inspect references to find conceptual origin and foundational baselines.

### Forward snowball

From each seed paper, inspect citing papers to find follow up methods, criticism, and updated evaluations.

Operational rule:

- choose 3-5 seed papers,
- perform one backward and one forward cycle,
- log source path (`seed -> backward` or `seed -> forward`),
- prioritize papers repeatedly discovered across cycles.

## 9) Query iteration protocol

Use at least three rounds:

- **Round 1** broad retrieval for landscape mapping,
- **Round 2** precision tuning for screening quality,
- **Round 3** targeted retrieval for identified blind spots.

For each round, capture:

- query string,
- database,
- filter settings,
- result volume,
- main noise pattern,
- revision rationale.

Without this log, search strategy is not auditable.

## 10) Typical mistakes and fixes

1. **Mistake**: one database only.  
   **Fix**: use at least two complementary databases.

2. **Mistake**: no synonym expansion.  
   **Fix**: build and maintain term map.

3. **Mistake**: query drift without record.  
   **Fix**: keep versioned query history.

4. **Mistake**: citation count used as quality proxy.  
   **Fix**: evaluate method relevance and evidence quality.

5. **Mistake**: no snowballing cycle.  
   **Fix**: run backward and forward cycles for seeds.

## 11) Minimal query documentation schema

Use this structure in `search-strategy.md`:

```markdown
## Query Log Entry

- Query ID:
- Database:
- Timestamp:
- Query String:
- Filters:
- Result Count:
- Purpose:
- Observed Noise:
- Decision (keep/revise/discard):
- Next Action:
```

This turns query design into a reproducible method component and protects later synthesis from hidden search bias.
