# Literature Review Method

## 1) Why this method exists

A literature review is not a summary dump. It is a reproducible process that explains what is known, what remains unresolved, which methods dominate, where evaluation is weak, and why specific gaps matter for your next contribution. If another reviewer cannot trace your search logic and screening logic, your review is descriptive writing, not scientific evidence work.

This method enforces a seven stage pipeline:

1. define research questions,
2. build search queries,
3. select databases,
4. screen title and abstract,
5. perform full text review,
6. extract into matrix,
7. synthesize threads and categories.

## 2) Stage A — Define RQ with boundaries

Start with one primary research question and multiple secondary questions.

Required boundary dimensions:

- research object (system, model, dataset, protocol, workflow),
- context (industry, threat model, deployment condition),
- time window,
- evidence expectation (what counts as support).

Good RQ is falsifiable and scoped. “What is the state of AI security” is too broad. “How do data plane policy enforcement methods compare under low latency constraints in enterprise east-west traffic scenarios” is actionable.

Record each RQ revision. If the question changed after initial retrieval, explain why.

## 3) Stage B — Build query logic

Construct query blocks:

- concept block (problem terms),
- method block (algorithm/system terms),
- context block (scenario terms),
- evaluation block (benchmark/metric terms).

Use boolean composition and synonyms. Keep a query evolution log:

- query v1: broad retrieval,
- query v2: noise reduction,
- query v3: targeted gap coverage.

Do not hide failed queries. Failed queries explain search bias and strengthen reproducibility.

## 4) Stage C — Select databases strategically

No single index is complete. Use at least two independent sources and document why each was chosen.

Typical combination for CS/security:

- broad index (Google Scholar or Semantic Scholar),
- venue focused index (IEEE Xplore, ACM DL),
- frontier index (arXiv for early signals).

For each database log:

- date/time,
- exact query,
- field scope,
- result count,
- export method.

This log is part of your method artifact, not an optional appendix.

## 5) Stage D — Title and abstract screening

Screening must follow explicit inclusion and exclusion rules.

Inclusion examples:

- directly addresses at least one RQ,
- contains method detail sufficient for matrix extraction,
- provides evaluation or theory evidence relevant to comparison.

Exclusion examples:

- commentary with no method detail,
- domain mismatch,
- duplicate publication,
- inaccessible full text with no credible secondary signal.

Record exclusion reasons at minimum granularity. “Not relevant” is not sufficient. Use reason tags such as `E-domain-mismatch`, `E-no-method`, `E-no-evaluation`, `E-duplicate`.

## 6) Stage E — Full text review

Abstracts are not enough for robust synthesis. Full text extraction is required for:

- assumptions,
- mechanism details,
- dataset construction,
- metric definition,
- baseline fairness,
- limitation disclosure.

Mandatory extraction fields per paper:

- research problem,
- method mechanism,
- data/object,
- metrics,
- key findings,
- limitations,
- relation to your work.

If a field is unknown, mark unknown and explain why. Never invent completion text.

## 7) Stage F — Matrix extraction

Matrix extraction transforms papers into comparable units. A matrix is useful only when columns support cross paper comparison. Keep metric definitions and dataset scope explicit to avoid false equivalence.

Minimum matrix quality checks:

- each row corresponds to one reviewed paper,
- each row includes at least one concrete limitation,
- relation to your work is specific and testable,
- evidence IDs are linked if evidence ledger is active.

Do not store matrix as a bibliography clone. Store it as a comparison instrument.

## 8) Stage G — Synthesis

Synthesis should produce:

1. **Research threads**: evolution of problem framing and solution paths.
2. **Method categories**: families of approaches with assumptions and tradeoffs.
3. **Disagreement map**: where results conflict and why.
4. **Gap candidates**: at least three gap types with paper level grounding.

Recommended synthesis structure:

- Thread 1: problem framing and scope evolution,
- Thread 2: method families and mechanism differences,
- Thread 3: evaluation practice quality and comparability,
- Thread 4: unresolved constraints and transfer barriers.

## 9) Quality gates for completion

A review is complete only if all conditions hold:

- documented query strategy,
- explicit inclusion/exclusion criteria,
- full text based matrix extraction,
- method category and thread synthesis,
- at least three grounded gap types,
- uncertainty notes for weak evidence regions.

If any gate fails, treat output as draft notes, not review conclusion.

## 10) Frequent failure modes

1. abstract stacking with no comparability,
2. search strategy undocumented,
3. selection bias toward supportive papers,
4. metric mismatch ignored,
5. timeline claims without freshness checks,
6. gap claims without paper grounded evidence.

## 11) Practical review handoff

Before handing off to gap analysis or methodology design, provide:

- final query log,
- inclusion/exclusion file,
- literature matrix,
- synthesized review text,
- preliminary gap candidates with paper IDs.

This handoff turns literature work into an actionable substrate for the next research stages.
