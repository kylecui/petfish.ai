# Validity Threats

## Why explicit threat analysis is mandatory

Method sections often fail because they report what was done but not why conclusions should be trusted. Validity threats make the trust boundary explicit. They define which claims are robust, which claims are conditional, and which claims should not be made. In CS/security research, hidden assumptions about workload, attacker model, observability, and deployment environment can invalidate otherwise polished experiments.

This guide covers five threat classes and practical mitigation actions.

## 1) Internal validity

### Question
Did the intervention itself cause the observed effect?

### Typical threats
- confounding variables (hardware variance, background traffic, operator differences),
- measurement distortion (sampling loss, instrumentation overhead),
- baseline unfairness (different tuning effort across methods),
- implementation drift between compared systems.

### Mitigation actions
- control critical variables and log configuration,
- run ablation to isolate mechanism contributions,
- align optimization effort across baselines,
- report repeat runs and variance,
- validate instrumentation overhead.

### Red flag example
A method appears faster because baseline was run with default settings while proposed method used tuned parameters.

## 2) External validity

### Question
Can results generalize beyond the test setup?

### Typical threats
- single dataset or single environment dependence,
- unrealistic synthetic workload,
- narrow scale testing,
- absence of cross domain checks.

### Mitigation actions
- evaluate across multiple datasets/workloads,
- include near real operational scenarios,
- report transfer limits and boundary conditions,
- run sensitivity analysis on scale/noise/adversary strength.

### Red flag example
Lab results from a small testbed are presented as production ready without deployment constraint analysis.

## 3) Construct validity

### Question
Do chosen metrics truly represent the conceptual objective?

### Typical threats
- proxy metric mismatch,
- ambiguous metric definition,
- selective metric reporting,
- ignored tradeoff dimensions.

### Mitigation actions
- map each metric to each conceptual claim,
- include complementary metrics (effectiveness + cost),
- define denominator and measurement procedure,
- state what the metric cannot capture.

### Red flag example
Accuracy gain is interpreted as better operational security while false positive operational cost is omitted.

## 4) Conclusion validity

### Question
Are statistical conclusions justified by the data and analysis procedure?

### Typical threats
- low statistical power,
- multiple hypothesis testing without correction,
- p value only reporting,
- selective publication of positive results.

### Mitigation actions
- estimate sample size before experiments,
- report effect size and confidence intervals,
- predefine analysis plan,
- disclose non significant and negative results,
- apply correction for multiple comparisons where relevant.

### Red flag example
One run with marginal significance is reported as stable superiority.

## 5) Ecological validity

### Question
Does the study environment reflect real use conditions?

### Typical threats
- idealized user behavior,
- unrealistic attacker assumptions,
- short duration tests hiding long term effects,
- omission of operational constraints (maintenance, rollout, rollback).

### Mitigation actions
- include realistic workload traces,
- include operational constraints in evaluation protocol,
- run staged pilot where feasible,
- collect longitudinal indicators when claims imply sustained impact.

### Red flag example
Method works in controlled benchmark but fails under continuous deployment conditions due to operational overhead.

## Threat record template

Use this structure in `validity-threats.md`:

```markdown
## Threat T-XX

- Category: Internal / External / Construct / Conclusion / Ecological
- Description:
- Affected claims:
- Severity: high / medium / low
- Mitigation plan:
- Residual risk:
- Cannot claim boundary:
```

Each major claim should map to at least one threat record.

## Mapping threats to “cannot claim” boundaries

Threat analysis must produce explicit non claim statements.

Examples:

- if external validity is weak, do not claim cross domain generality,
- if construct mapping is partial, do not claim full objective achievement,
- if statistical power is low, do not claim robust superiority,
- if ecological validity is limited, do not claim production readiness.

These boundaries protect scientific integrity and reduce review rejection risk.

## Minimum acceptance criteria for threat analysis

Threat analysis is acceptable only when:

1. relevant threat categories are covered,
2. each category has concrete project specific entries,
3. mitigation actions are actionable,
4. residual risk is disclosed,
5. non claim boundaries are explicit.

Generic boilerplate threat paragraphs do not meet this standard.
