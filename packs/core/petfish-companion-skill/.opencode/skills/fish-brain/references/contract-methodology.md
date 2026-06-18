# Contract-Driven Gateway Methodology

**Status**: Phase 1-5 complete — all 5 atoms + macro contract implemented and validated (42/42 checks PASS)
**Source paper**: `dev_reference/contract-driven-harness-arxiv-v4-humanized-draft.md`
**Plan**: `.sisyphus/plans/contract-driven-companion-upgrade.md`

---

## What this is

The Companion Gateway runs 6 steps before every user message. Each step is a **mechanism atom** — a bounded operation with one primary mechanism and one dominant failure mode. This directory formalizes each atom as an explicit **contract** so failures become inspectable, repairable, and regressable.

This is NOT contract-driven execution of the whole companion. It is contract-driven **verification** of the Gateway's bounded steps. See [Claim Boundary](#claim-boundary) below.

## Paper → Companion mapping

The paper (§3.2) defines 7 harness objects. Each contract file instantiates them:

| Paper Object | Contract Field | Role in Companion Gateway |
|---|---|---|
| `TaskSpec` | `task_spec` | What this Gateway step must accomplish (objective, constraints, success conditions, non-goals) |
| `MemorySlice` | `memory_slice` | What the step may read (admissible), must not read (excluded), and cannot know (unknown_state) |
| `EvidenceBundle` | `evidence_bundle` | The deterministic data the step uses (regex tables, registry state) |
| `OutputContract` | `output_contract` | Required output fields, types, validators, and blocked outputs |
| `WorkflowGraph` | `workflow_gate` | Predecessors, successors, and carried obligations between steps |
| `TraceLog` | `trace_log` | What must be traceable after the step runs |
| `ValidatorGate` | `validator_gate` | The deterministic test that distinguishes golden from known-bad |

## Mechanism Atom (paper §3.4)

Each Gateway step is the smallest testable unit. It isolates one primary mechanism on a fixed input under an explicit output contract. Admission requires (paper §3.5):

1. fixture schema validates
2. golden output passes
3. at least one known-bad output fails for the intended reason
4. baseline leaves improvement room OR the evaluation targets absolute adherence
5. the composition interface is declared
6. cross-step carried obligations are explicit

## Repair Loop (paper §3.6)

When a validator fails, the 7-step protocol runs (adapted for deterministic atoms):

1. **Observe** — validator returns a violation
2. **Isolate** — which contract field failed? which failure mode?
3. **Explicit** — update the `.contract.json` with the missing obligation
4. **Known-bad** — write a fixture capturing the exact violation
5. **Regression** — run the validator; golden passes, known-bad fails
6. **Smoke** — for deterministic atoms, the validator IS the smoke test
7. **Update** — append to a known-bad registry; update this doc if claim scope changed

**Termination**: `max_iterations=1`. If one contract revision doesn't fix it, escalate to backlog (do not loop).

## The 5 Gateway Atoms

| Atom | Primary Mechanism | Dominant Failure Mode | Status |
|---|---|---|---|
| `step0-mode-read` | Load depth/rigor from yaml | Missing/invalid fields | ✅ Phase 2 |
| `step1-topic-check` | Read injected topic context | Misread risk level | ✅ Phase 2 |
| `step1.5-failure-signal` | Regex match prev turn | False positive / false negative | ✅ Phase 1 |
| `step2-skill-sense` | 3-tier gap detection | Wrong pack / missed gap | ✅ Phase 3 |
| `step2.5-anti-sycophancy` | Rubric-first pause | Skipped pause on eval question | ✅ Phase 3 (detection-level) |
| `gateway-macro` | Sequence + carried obligations | Obligation loss / duplicate | ✅ Phase 4 |

## Running the validators

All 6 validators (5 atoms + 1 macro) run with pure stdlib Python, no test framework:

```bash
# Run all validators (from repo root)
$v="packs/core/petfish-companion-skill/.opencode/skills/fish-brain/validators"
foreach ($f in @("test_mode_read","test_topic_check","test_failure_signal","test_skill_sense","test_anti_sycophancy","test_macro_composition")) {
    uv run python "$v/$f.py"
}
```

Each validator reuses existing `classify()` functions from `benchmarks/scripts/modules/` — no logic duplication. Total: 42 checks across 6 atoms, all golden pass + all known-bad rejected.

## Repair loop in action (Phase 3 finding)

During Phase 3 validation, the `step2.5-anti-sycophancy` validator caught that calibrate TRIGGERS were missing common Chinese evaluative patterns ("好吗", "合理", "你觉得"). This triggered the full repair loop (paper §3.6):

1. **Observe** — validator failed on "这个方案好吗？" and "你觉得...合理吗？"
2. **Isolate** — `fish-calibrate` TRIGGERS in both `catalog_query.py` and `skill_sense_eval.py` lacked these patterns
3. **Explicit** — added "好吗", "合理", "你觉得" to both source files
4. **Known-bad** — fixture `kb2-me` already captured the violation
5. **Regression** — re-ran validator: 6/6 PASS
6. **Smoke** — deterministic validator is the smoke test
7. **Update** — documented here; claim boundary unchanged (detection-level only for this atom)

This is the methodology working as designed: a contract-driven validator caught a real gap that would have caused the Companion to miss evaluative questions in Chinese, and the repair loop fixed it with a traceable evidence chain.

## External references (from research)

| Framework | Mechanism | How it maps |
|---|---|---|
| DSPy Signatures | Declarative input/output field declarations | Our `output_contract.required_fields` |
| Instructor | Pydantic schema + auto-retry on validation fail | Our `validator_gate` + `repair_strategy` |
| Outlines | Generation-time constraint enforcement | N/A (our atoms are deterministic, no generation) |
| CRITIC | Tool-interactive critique; tools are the key | Our `classify()` IS the tool; validator checks its output |
| Self-Refine | Generate→critique→refine; diminishing returns without tools | Our `max_iterations=1` bound reflects this finding |
| promptfoo | `is-json` + `llm-rubric` assertions in CI | Our pytest validator is the equivalent assertion layer |

Key lesson from the literature: **contracts + repair must be paired** (Instructor, DSPy Assertions). A contract without a validator is documentation; a validator without a contract is a test. Both together make failures repairable objects.

---

## Claim Boundary

**What this establishes** (bounded):

> Each Companion Gateway atom, when formalized as a contract with golden/known-bad fixtures and a deterministic validator, can be tested, repaired, and regression-covered independently. Cross-step carried obligations can be preserved when made explicit.

**What this does NOT establish** (non-claims, mirroring paper Appendix A):

- whole-companion reliability or production readiness
- that contract-driven Gateway improves user-facing outcomes
- that the methodology transfers to skill execution, deploy, research, or course workflows
- cost-effectiveness vs. a stronger model
- coverage of novel failure modes (the known-bad library is incremental)
- that step2-skill-sense or step2.5-anti-sycophancy (LLM-involving atoms) are contract-bound (Phase 3)

These non-goals are deliberate. The paper's authors reject whole-workflow claims on bounded-macro evidence; we apply the same discipline to the Companion.
