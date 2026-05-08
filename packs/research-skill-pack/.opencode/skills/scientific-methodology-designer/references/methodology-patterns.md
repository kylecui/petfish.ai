# Methodology Patterns

## Why pattern selection matters

Methodology design fails when teams jump from idea to implementation without selecting a structure that matches the research question. Different questions require different evidence forms. If you claim theoretical guarantees, you need model and proof rigor. If you claim deployment feasibility, you need system level evaluation. If you claim behavioral understanding, you need empirical or qualitative validity. This guide provides four common patterns for CS/security work and shows how to choose and operationalize them.

## Pattern A — System Design + Prototype + Evaluation

### Best fit

- new architecture or mechanism proposal,
- performance/security tradeoff claims,
- deployment oriented contributions.

### Core stages

1. define architecture, threat model, and assumptions,
2. implement a prototype with clear scope,
3. evaluate against fair baselines under realistic workloads.

### Required artifacts

- design document with module boundaries,
- prototype implementation notes,
- benchmark plan and metric definitions,
- result tables with cost and benefit dimensions.

### Quality checks

- baseline fairness is explicit,
- overhead is reported (latency, throughput, CPU/memory),
- failure cases are documented,
- reproducibility instructions are available.

### Common failure

Architecture claims without runnable prototype or with hand picked benchmark settings.

## Pattern B — Formal Model + Proof + Implementation

### Best fit

- correctness/security property claims,
- protocol guarantees,
- invariants that must hold under defined assumptions.

### Core stages

1. specify formal entities and transition rules,
2. prove target properties,
3. map model to implementation and test assumption drift.

### Required artifacts

- formal specification,
- theorem/lemma statements and proof sketches,
- implementation correspondence notes,
- counterexample analysis when assumptions break.

### Quality checks

- assumptions are realistic and visible,
- proved property matches stated problem,
- implementation does not silently violate model constraints.

### Common failure

Strong proofs on oversimplified models with weak real world mapping.

## Pattern C — Empirical Study + Dataset + Statistical Analysis

### Best fit

- effectiveness comparison,
- behavior or trend measurement,
- data driven validation of hypotheses.

### Core stages

1. define variables and sampling strategy,
2. document dataset provenance and preprocessing,
3. run statistical analysis with uncertainty reporting.

### Required artifacts

- dataset card (source, size, period, bias notes),
- analysis plan,
- significance and effect size results,
- robustness checks and sensitivity analysis.

### Quality checks

- sample adequacy and representativeness,
- metric-concept alignment,
- no silent p-hacking or cherry picking,
- negative results disclosed.

### Common failure

Reporting only p values without effect size and confidence intervals.

## Pattern D — Survey + Coding + Thematic Analysis

### Best fit

- practitioner behavior understanding,
- adoption barriers,
- workflow and organizational research.

### Core stages

1. collect survey/interview material,
2. create coding scheme and apply coding,
3. synthesize themes with supporting quotations and counterexamples.

### Required artifacts

- instrument design (questionnaire/interview guide),
- coding manual,
- theme map with evidence quotes,
- disagreement notes and reconciliation process.

### Quality checks

- sample diversity and recruitment rationale,
- coding consistency and traceability,
- theme claims linked to source excerpts,
- minority and conflicting voices preserved.

### Common failure

Theme claims with no direct quotation linkage.

## Pattern mixing strategy

Many projects require mixed patterns. Typical combinations:

- System + Empirical: prototype plus quantified comparison.
- Formal + System: proven properties plus implementation feasibility.
- Survey + System: needs discovery followed by system validation.

Mixing rule: each claim must map to the pattern that can validate it. Do not use one pattern to justify claims that require another pattern’s evidence.

## Pattern selection decision table

| Research intention | Primary pattern | Secondary pattern |
|---|---|---|
| Propose deployable mechanism | System+Prototype+Evaluation | Empirical analysis |
| Prove correctness/security property | Formal+Proof+Implementation | System evaluation |
| Measure comparative effectiveness | Empirical+Dataset+Statistics | System evaluation |
| Explain practitioner behavior | Survey+Coding+Thematic | Empirical summary |

## Minimum methodology package

Regardless of pattern, deliver at least:

1. object and boundary definition,
2. hypothesis and falsification criteria,
3. input/output specification,
4. baseline comparison plan,
5. validation procedure,
6. validity threats and non claim boundary.

Without these six parts, methodology is not execution ready.

## Frequent anti-patterns

1. method chosen for convenience, not question fit,
2. baseline mismatch hidden in appendix,
3. no explicit failure criteria,
4. claims that exceed validation scope,
5. threat analysis reduced to generic paragraph.

Pattern discipline improves not only paper quality but also experiment efficiency and review defensibility.
