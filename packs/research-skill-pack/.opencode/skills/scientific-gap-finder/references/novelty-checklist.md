# Novelty Checklist

## Purpose

This checklist is used to judge whether a detected gap is genuine and whether the proposed contribution is worth pursuing. It prevents common failure patterns: novelty inflation, search incompleteness, weak differentiation, and unverifiable claims.

Use this checklist per candidate gap and attach evidence references.

## Section A — Gap authenticity

### A1. Search adequacy
- [ ] Query strategy is documented and reproducible.
- [ ] At least two databases were searched.
- [ ] At least one snowball cycle was completed.
- [ ] Synonym and terminology variants were covered.

### A2. Evidence grounding
- [ ] Gap is linked to specific paper rows in literature matrix.
- [ ] At least one counterexample paper is included.
- [ ] Evidence IDs are available for key assertions.
- [ ] Gap boundary (where it holds / where it does not) is explicit.

### A3. Non triviality
- [ ] Gap is not just naming variation.
- [ ] Gap is not pure parameter tuning opportunity.
- [ ] Closing this gap would change research understanding or practical capability.
- [ ] Gap matters for target objective, not only for benchmark cosmetics.

## Section B — Contribution value

### B1. Problem value
- [ ] Contribution addresses a clearly defined problem.
- [ ] Stakeholder value or scientific value is explicit.
- [ ] Scope and assumptions are stated.

### B2. Differentiation quality
- [ ] Difference from baseline methods is mechanism level, not wording level.
- [ ] Baselines are relevant and fair.
- [ ] Claimed novelty is proportional to actual difference.

### B3. Verifiability
- [ ] Contribution can be tested or disproved.
- [ ] Success criteria and failure criteria are defined.
- [ ] Required data/environment is realistically obtainable.
- [ ] Evaluation plan includes uncertainty handling.

### B4. Reusability and impact
- [ ] Contribution is not tied to one fragile setup only.
- [ ] Transferability limits are documented.
- [ ] Potential negative side effects are identified.

## Section C — Risk calibration

### C1. Overclaim risk
- [ ] No absolute wording without strong support (first, only, best).
- [ ] Claim confidence matches evidence confidence.
- [ ] “Cannot claim” boundaries are explicitly listed.

### C2. Execution risk
- [ ] Resource requirements fit available budget/time.
- [ ] MVP validation path exists.
- [ ] Backup plan exists if primary path fails.

### C3. Integrity risk
- [ ] No hidden dependence on inaccessible proprietary conditions.
- [ ] Reproducibility constraints are disclosed.
- [ ] Ethical or safety constraints are identified.

## Section D — Scoring framework (optional)

Score each item: 0 (not met), 1 (partly met), 2 (met).

Suggested interpretation:

- **High readiness**: >= 70% of max score.
- **Conditional readiness**: 50%–69%, requires remediation.
- **Low readiness**: < 50%, do not position as primary contribution.

Scoring is advisory. Evidence quality remains primary.

## Section E — Contribution card template

```markdown
### Contribution Candidate C-XX

- Related Gap ID:
- Problem Statement:
- Core Idea:
- Why It Matters:
- Differentiation vs Baselines:
- Evidence Links (Paper IDs / Evidence IDs):
- Validation Plan:
- Main Risks:
- Cannot Claim:
- Decision: Go / Conditional / Hold
```

## Section F — Frequent misjudgments

1. claiming novelty because papers used different words,
2. ignoring strong adjacent field baselines,
3. treating one positive experiment as robust evidence,
4. presenting engineering effort as scientific contribution,
5. using unsupported superiority wording.

Apply this checklist before moving from gap analysis to methodology design. It reduces expensive downstream rework and improves contribution credibility.
