# Assumption Risk Matrix for Product Validation Planning

## 1) Why assumption mapping matters

Most product failures come from untested assumptions, not execution speed.
An assumption-risk matrix helps teams test what can kill the initiative first.

## 2) Assumption categories (D/F/V)

Classify assumptions into:

- Desirability: users want this and will adopt it.
- Feasibility: we can build and operate it reliably.
- Viability: economics and business model sustain it.

Add optional category when needed:

- Compliance/Trust: legal, security, policy acceptance.

## 3) Assumption statement format

Use testable phrasing:

"We assume [segment] will [behavior] because [reason], under [constraints]."

Each assumption must include:

- evidence status (known/partial/unknown),
- potential impact if wrong,
- earliest test method.

## 4) Risk scoring model

Score assumptions with two dimensions:

- Impact if false (1-5)
- Uncertainty (1-5)

Risk score = Impact x Uncertainty

Priority bands:

- 16-25: critical (test immediately)
- 9-15: important (test in near term)
- 1-8: monitor (defer unless dependencies require)

## 5) Matrix structure

Use a table with fields:

- Assumption ID
- Category (D/F/V/C)
- Statement
- Evidence status
- Impact
- Uncertainty
- Risk score
- Test method
- Decision deadline
- Owner

Sort by risk score descending.

## 6) Risk-based prioritization workflow

1. List all critical assumptions from brief and opportunity map.
2. Merge duplicates and clarify wording.
3. Score independently by two stakeholders.
4. Resolve score disagreements with evidence review.
5. Select top critical assumptions for immediate experiments.

Do not prioritize by political visibility or implementation convenience.

## 7) Kill criteria definition

Kill criteria are precommitted conditions that stop investment.

Strong kill criteria are:

- measurable,
- time-bounded,
- tied to critical assumptions.

Template:

"If [critical metric] remains below [threshold] after [time window] despite [specified intervention], terminate or radically pivot initiative."

Examples:

- If activation remains <20% after 3 onboarding experiment cycles, stop current approach.
- If CAC payback exceeds 24 months in pilot channels, pause scale-up.

## 8) Pivot triggers vs kill triggers

Do not collapse pivot and kill into one condition.

- Pivot trigger: evidence suggests demand exists but current solution fit is weak.
- Kill trigger: evidence shows core assumption is invalid or economics fail.

Define both before running major experiments.

## 9) Evidence maturity levels

Tag assumptions by evidence maturity:

- Level 0: belief only
- Level 1: qualitative signal
- Level 2: directional quantitative signal
- Level 3: replicated quantitative evidence

Critical assumptions should move to Level 2+ before scale decisions.

## 10) Governance rhythm

Run assumption review cadence:

- weekly during discovery/validation,
- bi-weekly during early build,
- monthly after launch stabilization.

At each review:

- update scores,
- retire validated assumptions,
- add emerging risks,
- confirm next tests and owners.

## 11) Common anti-patterns

Anti-pattern 1: hiding assumptions inside feature specs.
Anti-pattern 2: scoring risk without evidence status.
Anti-pattern 3: no explicit kill criteria, causing sunk-cost drift.
Anti-pattern 4: testing easy assumptions first while critical ones remain untouched.

Correction: enforce top-risk-first validation rule.

## 12) Example matrix slice

A-03 (Desirability): impact 5, uncertainty 4, risk 20, test via Wizard-of-Oz onboarding, kill if completion <35% after 2 iterations.
A-07 (Viability): impact 4, uncertainty 3, risk 12, test via pilot cohort cost-to-serve tracking.
