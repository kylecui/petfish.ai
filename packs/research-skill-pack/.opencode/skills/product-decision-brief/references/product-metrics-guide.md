# Product Metrics Guide for Decision Briefs

## 1) Purpose

Metrics should reduce decision ambiguity.
A good metrics system links strategic outcomes to controllable inputs.

This guide helps select North Star metrics, define input hierarchy,
and avoid metric anti-patterns.

## 2) North Star metric selection

A North Star metric (NSM) should represent delivered user value,
not internal activity volume.

Selection criteria:

- correlates with long-term retention or expansion,
- reflects meaningful user progress,
- sensitive to product improvements,
- hard to game without delivering value.

Examples:

- collaboration product: weekly successful shared workflows,
- analytics product: recurring insight actions completed,
- infrastructure product: reliable production deployments per active team.

## 3) NSM validation checks

Before committing to NSM, test three checks:

1. Causality check: does NSM movement precede business outcomes?
2. Segment robustness: does it hold across priority segments?
3. Manipulation resistance: can teams inflate it without true value?

If any check fails, refine metric definition.

## 4) Input metric hierarchy

Build a driver tree from NSM down to actionable levers.

Typical hierarchy:

- Level 1: NSM (value outcome)
- Level 2: core drivers (activation, engagement, retention)
- Level 3: component drivers (task completion, time-to-value, reliability)
- Level 4: operational inputs (UX friction, support latency, error rate)

Each lower-level metric should have an owner and intervention path.

## 5) Leading vs lagging indicators

Use both, but for different decisions.

- Leading indicators: early movement signals (onboarding completion, setup success, first-week usage depth).
- Lagging indicators: outcome confirmation (retention, expansion revenue, churn).

Decision rule:

- execution cadence decisions -> leading indicators,
- strategic continuation decisions -> lagging + leading alignment.

## 6) Metric specification template

Define each metric with this schema:

- Name
- Formula
- Unit
- Time window
- Segment scope
- Data source
- Update cadence
- Owner
- Known caveats

No metric should enter decision brief without explicit formula and scope.

## 7) Guardrail metrics

Guardrails prevent local optimization damage.

Examples:

- improve activation without increasing support burden excessively,
- improve engagement without harming trust/compliance,
- increase conversion without lowering retention quality.

For each primary metric, define at least one guardrail.

## 8) Metric anti-patterns to avoid

Anti-pattern 1: Vanity metrics (page views, raw signups) as success proxy.
Anti-pattern 2: Metric overload without prioritization.
Anti-pattern 3: Unsegmented averages hiding critical cohort failures.
Anti-pattern 4: Post-hoc metric redefinition to fit narrative.
Anti-pattern 5: Ignoring data quality and instrumentation drift.

Correction: freeze metric definitions for each decision cycle.

## 9) Confidence and data quality layer

Add a confidence tag to each metric used in decisions:

- High: validated pipeline, stable definition, low missingness.
- Medium: minor quality caveats.
- Low: incomplete or recent instrumentation changes.

Low-confidence metrics should not be sole basis for go/no-go calls.

## 10) Decision-brief metric section structure

Include these blocks:

1. NSM and rationale.
2. Driver hierarchy snapshot.
3. Current baseline vs target thresholds.
4. Leading indicators trend.
5. Guardrail status.
6. Data quality caveats and confidence labels.

## 11) Example metric stack

Case: B2B workflow onboarding decision.

- NSM: weekly active workflows completed per account.
- Leading metric: day-7 activation rate.
- Diagnostic metric: setup step completion by stage.
- Guardrail: support tickets per activated account.
- Lagging metric: 90-day retention.

Decision use:

- proceed if leading metrics improve and guardrail stable,
- hold if leading improves but guardrail degrades sharply,
- no-go/pivot if no meaningful leading movement after planned iterations.
