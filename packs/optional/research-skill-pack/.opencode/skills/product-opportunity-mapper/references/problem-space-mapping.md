# Problem Space Mapping: From Pain Signals to Prioritized Opportunities

## 1) Why map the problem space first

Teams often jump from pain anecdotes to feature decisions.
Problem-space mapping forces structure before solution design.

Goal: identify where user pain is both significant and under-served.

## 2) Problem statement format

Use problem statements that are diagnosis-ready:

"[Segment] struggles to [goal] because [constraint], leading to [impact]."

Quality checks:

- names one segment,
- names one goal,
- names one root constraint,
- includes observable impact.

## 3) Problem tree construction

A problem tree separates symptoms from root causes.

Structure:

- Trunk: core problem.
- Roots: causal drivers.
- Branches: downstream consequences.

Construction workflow:

1. List observed symptoms from evidence.
2. Group by shared causal hypotheses.
3. Test causal links with counterexamples.
4. Mark validated vs assumed causes.

Do not treat correlation as causation without validation evidence.

## 4) Segment x problem matrix

Build a matrix to avoid one-size-fits-all conclusions.

Rows: user segments.
Columns: validated problem clusters.

For each cell track:

- severity (1-5),
- frequency (1-5),
- current workaround quality (1-5),
- evidence confidence (low/medium/high).

This exposes where the same problem has different strategic value by segment.

## 5) Opportunity size vs satisfaction gap analysis

Combine market potential and unmet need intensity.

Definitions:

- Opportunity size: reachable value if problem is solved.
- Satisfaction gap: importance minus current satisfaction.

Simple prioritization score:

Priority score = opportunity size index x satisfaction gap index x confidence factor

Use confidence factor (0.5 to 1.0) to penalize weak evidence.

## 6) Evidence model for mapping

Require multi-source evidence before promoting a problem cluster.

Suggested minimum:

- 3+ independent user evidence points,
- at least 1 behavioral or operational signal,
- contradiction log for dissenting data.

If evidence conflicts, keep cluster as candidate, not confirmed.

## 7) Opportunity categorization

Classify mapped opportunities into four buckets:

- Must-solve now (high impact, high confidence)
- Validate next (high impact, low confidence)
- Tactical quick wins (moderate impact, low effort)
- Defer/avoid (low impact or strategic mismatch)

This prevents backlog inflation from weakly supported items.

## 8) Dependency and sequencing logic

Some opportunities unlock others.
Map dependencies before prioritization commitments.

Dependency types:

- capability dependency,
- adoption dependency,
- data dependency,
- policy/compliance dependency.

Flag opportunities that appear high-scoring but are blocked by prerequisites.

## 9) Mapping anti-patterns

Anti-pattern 1: framing solution as problem.
Anti-pattern 2: combining unrelated pains into one giant cluster.
Anti-pattern 3: ignoring segment variance.
Anti-pattern 4: using impact words without measurable indicators.

Correction rule: every mapped problem must have at least one measurable signal.

## 10) Output format for planning handoff

Deliver three artifacts:

1. Problem tree with validated/assumed tags.
2. Segment x problem matrix with confidence labels.
3. Prioritized opportunity list with score rationale and next validation action.

Include explicit "not now" items to protect focus.

## 11) Example

Case: onboarding drop-off for technical product.

- Core problem: users fail to reach first value quickly.
- Root causes: unclear setup prerequisites, permission errors, weak guidance.
- Segment differences: SMB users blocked by technical depth, enterprise users blocked by governance flow.

Opportunity mapping result:

- Immediate: guided setup diagnostics for SMB path.
- Validate next: admin handoff workflow for enterprise onboarding.
- Defer: advanced customization templates until baseline activation improves.
