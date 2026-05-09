# Jobs-to-be-Done (JTBD) Framework for Opportunity Mapping

## 1) Core principle

People do not buy products; they hire solutions to make progress in a context.
JTBD helps describe that progress in a structured, testable way.

Use JTBD to avoid feature-first thinking and to expose unmet outcomes.

## 2) Job statement format

Use a stable job statement template:

"When [situation], I want to [motivation/action], so I can [expected outcome]."

Quality criteria:

- context is concrete,
- action is user-centered,
- outcome is measurable or observable,
- no embedded solution bias.

Bad: "I want AI dashboards."
Better: "When preparing weekly performance review, I want to detect anomalies quickly, so I can decide interventions before Monday planning."

## 3) Job hierarchy model

Model jobs at three levels:

- Functional job: task progress the user seeks.
- Emotional job: how the user wants to feel.
- Social job: how user wants to be perceived.

Functional job drives roadmap priority.
Emotional/social jobs shape adoption and messaging decisions.

## 4) Outcome expectation definition

Define outcomes as improvement directions, not solution ideas.

Outcome statement pattern:

"Minimize [undesired effort/risk/time]" or
"Increase [desired certainty/speed/quality]."

Examples:

- Minimize time to confirm data accuracy.
- Increase confidence before sharing result with leadership.

Each outcome should map to a possible measurement proxy.

## 5) Switching forces analysis (push/pull/anxiety/habit)

Assess why users move (or do not move) from current solutions.

- Push: dissatisfaction with current state.
- Pull: attraction to new solution promise.
- Anxiety: fear of switching risk.
- Habit: inertia and routine lock-in.

Scoring suggestion (1-5 each):

Switch momentum = (push + pull) - (anxiety + habit)

Prioritize jobs where momentum is positive and evidence-supported.

## 6) Opportunity scoring formula

Use a transparent formula tied to user outcomes:

Opportunity score = Importance + Dissatisfaction - Current satisfaction

Practical variant with weighted factors:

Opportunity score =
0.35 x importance +
0.30 x dissatisfaction +
0.20 x switch momentum +
0.15 x strategic fit

Normalize all factors to 0-10 scale.
Record confidence for each factor.

## 7) Data collection for JTBD rigor

Minimum evidence set:

- 10-15 contextual interviews,
- 1-2 artifact reviews per segment (tickets, logs, workflows),
- optional survey for prevalence confirmation.

Capture moments where users "fire" or "fire" solutions.
These moments reveal real constraints and decision criteria.

## 8) Common mistakes and corrections

Mistake: treating personas as jobs.
Correction: personas are actors; jobs are progress goals.

Mistake: writing jobs as product features.
Correction: remove product names from statements.

Mistake: scoring opportunities without dissatisfaction evidence.
Correction: require at least one direct evidence anchor per score.

## 9) JTBD-to-roadmap translation

For each high-score job:

1. define smallest testable outcome,
2. map capability hypotheses,
3. identify adoption barrier from switching forces,
4. define validation metric and threshold.

This converts JTBD insight into execution backlog.

## 10) Output template

Use a table with these columns:

- Job ID
- Job statement
- Segment
- Importance (0-10)
- Dissatisfaction (0-10)
- Switch momentum (-10 to +10)
- Strategic fit (0-10)
- Opportunity score
- Confidence
- Recommended next experiment

## 11) Example

Job statement:

"When preparing monthly security review, I want to consolidate incident signals quickly, so I can explain risk posture with confidence."

Observed forces:

- push = 4 (current process slow and error-prone),
- pull = 5 (automation promise clear),
- anxiety = 3 (trust in generated summaries),
- habit = 2 (spreadsheet routine).

Switch momentum = 4.
If importance and dissatisfaction are both high, this becomes a prime opportunity candidate.
