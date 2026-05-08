# Gap Types

## How to use this guide

A research gap is not “I did not see a paper.” A gap is a bounded deficiency that is demonstrated against a mapped literature set. Each gap entry should include definition, detection signal, concrete paper grounding, counterexample handling, and false gap risk. This file defines seven gap families for CS/security research workflows.

---

## 1) Problem Gap

### Definition
The field does not adequately formulate or directly address an important problem variant, despite practical relevance.

### Detection signals
- papers optimize adjacent objectives but avoid the target problem,
- problem boundary is repeatedly under specified,
- operational constraints from real deployment are ignored in problem setup.

### CS/security example
A set of network defense papers focuses on offline attack classification but does not model real time policy enforcement under strict latency SLOs.

### False gap risk
Terminology mismatch can hide prior work. The problem may already be addressed under a different label.

---

## 2) Method Gap

### Definition
Existing methods share structural limitations under realistic assumptions or fail under critical constraints.

### Detection signals
- dependence on unrealistic assumptions,
- missing mechanism explanation despite claimed improvement,
- repeated failure in constrained environments.

### CS/security example
Detection methods require full packet visibility and large offline retraining cycles, but deployment environment permits only lightweight in path processing.

### False gap risk
Confusing implementation immaturity with method deficiency. Verify whether stronger engineering could close the observed weakness.

---

## 3) Evaluation Gap

### Definition
Evaluation design is insufficient to support reliable method comparison or conclusion confidence.

### Detection signals
- no fair baseline alignment,
- no ablation for key components,
- no statistical uncertainty reporting,
- metric definitions inconsistent across papers.

### CS/security example
Several IDS papers report accuracy only, with no false positive burden, latency impact, or deployment overhead.

### False gap risk
Assuming missing detail in main paper means no evaluation exists. Check appendices, artifacts, and technical reports.

---

## 4) Dataset Gap

### Definition
Available datasets do not represent target conditions, causing weak external validity.

### Detection signals
- outdated or overly sanitized datasets,
- label quality uncertainty,
- narrow distribution that hides realistic drift,
- no cross dataset transfer testing.

### CS/security example
A malware traffic model performs well on a classic benchmark but fails on enterprise traffic with modern encrypted protocol mix.

### False gap risk
Assuming “no public dataset” equals impossible validation. Sometimes proxy datasets or synthetic workload plus real traces can provide credible evidence.

---

## 5) System Gap

### Definition
Work remains at conceptual or algorithm level without system implementation evidence for operational feasibility.

### Detection signals
- simulation only results,
- no integration path with existing stack,
- no resource overhead or operational cost discussion,
- no deployment failure analysis.

### CS/security example
An access control strategy model is proposed, but no implementation in real data plane pipeline (e.g., eBPF/XDP) is provided.

### False gap risk
Not all research must be system papers. For theory oriented contributions, missing system prototype is not automatically a gap unless system feasibility is part of the claim.

---

## 6) Theory-Practice Gap

### Definition
Theoretical conclusions do not transfer cleanly to real world operation due to violated assumptions or hidden constraints.

### Detection signals
- global state assumptions break in distributed runtime,
- adversarial adaptation ignored,
- practical observability constraints omitted,
- implementation introduces behavior not covered by model.

### CS/security example
A policy optimization model assumes perfect timely state updates, but production deployment has delayed telemetry and inconsistent policy propagation.

### False gap risk
Blaming theory for failures caused by poor engineering execution. Separate model boundary violation from implementation defects.

---

## 7) Domain Transfer Gap

### Definition
Promising methods from adjacent fields are not yet adapted and validated for the target domain’s constraints.

### Detection signals
- transfer attempts are superficial,
- adaptation assumptions are unstated,
- no domain specific robustness checks,
- no analysis of mismatch between source and target distributions.

### CS/security example
An NLP representation model is reused for vulnerability code analysis without addressing compiler optimization effects and label noise specific to security datasets.

### False gap risk
Treating cross domain reuse as novelty by default. If adaptation is trivial and no new mechanism is introduced, contribution value may be limited.

---

## Cross type mapping guidance

One observed deficiency may involve multiple gap types. Use primary plus secondary labels.

Example:

- Primary: Evaluation Gap
- Secondary: Dataset Gap

This helps avoid over collapsing everything into “method gap.”

## Minimal evidence rule for claiming a gap

Before confirming any gap:

1. map to specific papers in matrix,
2. include at least one potential counterexample,
3. explain why counterexample does not close the gap,
4. define boundary where gap holds,
5. propose at least one verifiable contribution path.

If these five conditions are not met, classify as “candidate gap” rather than “confirmed gap.”
