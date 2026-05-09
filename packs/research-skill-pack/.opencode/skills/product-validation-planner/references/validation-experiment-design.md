# Validation Experiment Design for Product Hypotheses

## 1) Goal of validation work

Validation is not proving you are right.
It is reducing uncertainty before committing major resources.

Design experiments to falsify risky assumptions early and cheaply.

## 2) Hypothesis format (mandatory)

Use this standard:

"We believe [change/intervention] will cause [expected behavior/outcome], measured by [metric] in [segment/context] within [time window]."

Good hypothesis properties:

- causal claim is explicit,
- metric is observable,
- segment is specified,
- time window is bounded.

## 3) Experiment selection by uncertainty type

Map uncertainty before choosing experiment type.

- Desirability uncertainty -> demand tests (landing page, interviews, concept tests).
- Usability uncertainty -> task-based usability tests, prototype trials.
- Feasibility uncertainty -> technical spikes, shadow implementation.
- Viability uncertainty -> willingness-to-pay or pricing tests.

## 4) MVP experiment types (and when to use)

## Wizard of Oz MVP

- User sees automated system; humans do hidden work.
- Best for: testing value before heavy engineering.
- Risk: scaling assumptions can be misleading.

## Concierge MVP

- Manual, high-touch service for small cohort.
- Best for: understanding workflow depth and edge cases.
- Risk: overfitting to early adopters.

## Landing page MVP

- Simulate value proposition and capture intent behavior.
- Best for: message-market resonance and demand signal.
- Risk: intent metrics may not predict retained usage.

Choose the lightest experiment that can invalidate the hypothesis.

## 5) Metric selection hierarchy

Use a metric stack, not a single number.

1. Primary decision metric (go/pivot/kill).
2. Guardrail metrics (prevent harmful side effects).
3. Diagnostic metrics (explain why outcome moved).

Example:

- Primary: activation rate within 7 days.
- Guardrail: support tickets per activated account.
- Diagnostic: setup completion by step.

## 6) Statistical power and sample size basics

Do not pretend certainty from tiny samples.

Minimum planning inputs:

- baseline metric,
- minimum detectable effect (MDE),
- significance level (alpha, usually 0.05),
- desired power (usually 0.8).

Directional heuristics:

- exploratory prototype tests: small n is acceptable for qualitative insights,
- decision-grade A/B tests: compute sample size from MDE and baseline,
- segment comparisons: ensure each segment has sufficient n, not just total n.

If sample size is infeasible, downgrade claim strength explicitly.

## 7) Decision thresholds before running experiment

Freeze thresholds in advance to avoid post-hoc rationalization.

Template:

- Proceed if primary metric >= X and no guardrail breach.
- Pivot if metric between Y and X with clear diagnostic signal.
- Kill if metric < Y or severe guardrail breach persists.

Document exception policy for noisy data scenarios.

## 8) Experiment execution checklist

- Hypothesis and metrics documented.
- Segment and inclusion criteria defined.
- Instrumentation validated.
- Duration and stopping rule defined.
- Ethics/compliance constraints checked.
- Analysis plan written before data collection ends.

## 9) Interpretation pitfalls

Pitfall 1: metric uplift from novelty effect only.
Pitfall 2: survivorship bias in retained cohort analysis.
Pitfall 3: interpreting correlation as causation when confounds exist.
Pitfall 4: overgeneralizing from one segment to all segments.

Mitigation: run holdout, use guardrails, and report confidence intervals.

## 10) Output template for this skill

For each experiment include:

- Hypothesis statement
- Experiment type and rationale
- Segment and sample plan
- Metrics (primary/guardrail/diagnostic)
- Decision thresholds
- Risks and fallback actions
- Expected timeline and owner

## 11) Example

Hypothesis:

"We believe guided setup checklist will increase week-1 activation, measured by activated accounts ratio, for SMB admins within 14 days."

Experiment:

- Wizard of Oz onboarding support for 30 accounts,
- compare against historical baseline,
- primary threshold: +15% activation,
- guardrail: support time per account must not exceed 2x baseline.

Decision:

- proceed to productized checklist only if both thresholds pass.
