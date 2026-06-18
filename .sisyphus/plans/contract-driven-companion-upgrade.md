# Contract-Driven Companion Upgrade — Design Plan

**Branch**: `contract-driven-companion` (from `dev`)
**Source paper**: `dev_reference/contract-driven-harness-arxiv-v4-humanized-draft.md`
**Author**: Sisyphus (with anti-sycophancy pre-review)
**Status**: Awaiting Momus review
**Date**: 2026-06-18

---

## 0. Anti-Sycophancy Pre-Review (executed BEFORE design)

Before designing, I actively searched for reasons this upgrade might be wrong. Three objections found:

| # | Objection | Severity | Resolution in this plan |
|---|---|---|---|
| 1 | **Category error**: paper's evidence is fixed-input/no-tool/bounded macros. Companion is open-ended/tool-using/multi-turn. Applying wholesale = paper's explicit non-claim (Appendix A). | CRITICAL | Scope is bounded to Gateway mechanism atoms, NOT whole-workflow. Non-goals section mirrors paper's Appendix A. |
| 2 | **Known-bad library perpetually incomplete**: paper's repair loop works because fixtures are frozen; companion meets novel failures every session. | HIGH | Repair loop targets *recurring* failure classes (gateway-step violations), not novel task failures. Known-bad grows incrementally, gated by admission criteria. |
| 3 | **Cost compounds**: paper reports ~2.5K tokens + 0.5s/run overhead. Always-on companion × every message = non-trivial tax. Paper warns contracts reduce flexibility. | MEDIUM | Contracts are opt-in per Gateway step, not per message. Validators are deterministic Python (no LLM call). Repair loop has max-iteration bound (default 1). |

**Conclusion**: The upgrade is justified ONLY at bounded-operation scope. Whole-companion contract-driven is rejected. Proceeding with scoped design.

---

## 1. Problem Statement

The Companion Gateway runs 6 steps before every user message (Mode Read → Topic Check → Failure Signal Detection → Skill Sense → Anti-Sycophancy → Proceed). Today these steps are:

- **Implicit contracts**: each step has an expected output but no formal spec (fields, types, constraints, golden/known-bad).
- **No validators**: a Skill Sense output is never deterministically checked for correctness. Failures silently propagate to Step 3.
- **No repair loop**: when a step produces a wrong/violating output, the Gateway proceeds anyway. No retry, no known-bad capture, no contract tightening.
- **Scattered patterns**: `answer-contract.md` (online), `lint_skill.py` fix loop, `quality-gate` PASS/CONDITIONAL/FAIL, and `FAILURE_SIGNALS` regex already exist — but in isolation, not unified.

**Hypothesis (bounded, testable)**: Representing each Gateway step as a mechanism atom with explicit contract + validator gate + repair loop will make Gateway-step failures inspectable, repairable, and regressable — without claiming whole-companion reliability.

---

## 2. Scope

### 2.1 In Scope

- The 6 Companion Gateway steps as **mechanism atoms** (paper §3.4)
- One explicit **contract** per atom (paper's 7 objects, §3.2)
- One deterministic **validator gate** per atom (paper §3.4)
- A unified **repair loop** protocol (paper §3.6)
- **Golden + known-bad fixtures** per atom (paper §3.4 admission criteria)
- An **eval harness** extending `benchmarks/` (paper §3.7 metrics)
- A **claim-boundary document** (paper Appendix A discipline)
- **Composition**: the Gateway macro with explicit cross-step carried obligations (paper Stage 7p v2 lesson)

### 2.2 Out of Scope (Non-Goals — mirror paper Appendix A)

This upgrade does NOT claim:

- the whole companion is contract-driven;
- skill execution inside Steps 3+ is contract-bound;
- the companion becomes generally reliable, production-ready, or model-equivalent;
- every user message gets full G9 contract packet (cost-prohibitive);
- novel/rare failures are pre-cataloged (known-bad library is incremental);
- open-ended tool-using workflows (deploy, research, course) become contract-bound;
- the instruction-based Gateway is replaced by a hard-coded state machine.

These non-goals match the paper's discipline: bounded macros, not open workflows.

### 2.3 Target Location

```
packs/core/petfish-companion-skill/
└── .opencode/skills/fish-brain/
    ├── contracts/                    # NEW — one .contract.yaml per atom
    │   ├── _schema.json              # contract schema (meta-contract)
    │   ├── step0-mode-read.contract.yaml
    │   ├── step1-topic-check.contract.yaml
    │   ├── step1.5-failure-signal.contract.yaml
    │   ├── step2-skill-sense.contract.yaml
    │   ├── step2.5-anti-sycophancy.contract.yaml
    │   └── gateway-macro.contract.yaml   # composition contract
    ├── validators/                   # NEW — deterministic Python gates
    │   ├── __init__.py
    │   ├── base.py                   # ContractResult, Violation, Severity
    │   ├── validate_contract.py      # universal loader + runner
    │   └── step_validators/          # one validator per atom
    │       ├── test_mode_read.py
    │       ├── test_topic_check.py
    │       ├── test_failure_signal.py
    │       ├── test_skill_sense.py
    │       └── test_anti_sycophancy.py
    ├── fixtures/                     # NEW — golden + known-bad per atom
    │   ├── step0-mode-read/
    │   │   ├── golden.1.yaml
    │   │   ├── known_bad.1.yaml      # missing depth field
    │   │   └── known_bad.2.yaml      # invalid rigor value
    │   ├── step1.5-failure-signal/
    │   │   ├── golden.1.yaml
    │   │   ├── known_bad.1.yaml      # false positive (no failure in prev turn)
    │   │   └── known_bad.2.yaml      # false negative (clear deploy failure missed)
    │   └── ...
    ├── repair/                       # NEW — repair loop engine
    │   ├── __init__.py
    │   ├── repair_loop.py            # the 7-step protocol from paper §3.6
    │   └── known_bad_registry.jsonl  # incremental failure catalog
    ├── references/                   # existing + new
    │   ├── skill-catalog.md
    │   ├── contract-methodology.md   # NEW — paper mapping + claim boundary
    │   └── claim-boundary.md         # NEW — what this does/doesn't establish
    └── scripts/                      # existing
        ├── catalog_query.py          # extended: --validate-contracts flag
        ├── check_installed.py
        └── detect_platform.py

benchmarks/
├── datasets/
│   ├── gateway-contracts.jsonl      # NEW — eval dataset
│   └── gateway-repair-loops.jsonl   # NEW — repair-loop eval dataset
└── scripts/modules/
    ├── contract_eval.py              # NEW — atom-level eval
    └── macro_eval.py                 # NEW — Gateway macro composition eval
```

---

## 3. Design: Contract Object Model

Maps paper §3.2's 7 objects to Companion Gateway. Each `.contract.yaml` file instantiates this schema.

### 3.1 Contract Schema (`_schema.json`)

```jsonc
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Companion Gateway Mechanism Atom Contract",
  "type": "object",
  "required": ["atom_id", "version", "task_spec", "memory_slice",
               "output_contract", "validator_gate", "admission"],
  "properties": {
    "atom_id":         { "type": "string", "pattern": "^step[0-9]+(\\.[0-9]+)?-[a-z-]+$" },
    "version":         { "type": "string", "pattern": "^v[0-9]+(\\.[0-9]+)*$" },
    "task_spec":       { "$ref": "#/definitions/TaskSpec" },
    "memory_slice":    { "$ref": "#/definitions/MemorySlice" },
    "evidence_bundle": { "$ref": "#/definitions/EvidenceBundle" },
    "output_contract": { "$ref": "#/definitions/OutputContract" },
    "workflow_gate":   { "$ref": "#/definitions/WorkflowGate" },
    "trace_log":       { "$ref": "#/definitions/TraceLog" },
    "validator_gate":  { "$ref": "#/definitions/ValidatorGate" },
    "repair_strategy": { "$ref": "#/definitions/RepairStrategy" },
    "admission":       { "$ref": "#/definitions/Admission" }
  },
  "definitions": { /* ... see references/contract-methodology.md ... */ }
}
```

### 3.2 Example: Step 1.5 Failure Signal Contract (concrete)

```yaml
# step1.5-failure-signal.contract.yaml
atom_id: step1.5-failure-signal
version: v1
task_spec:
  objective: "Detect known failure patterns in the previous assistant turn and recommend the matching pack if uninstalled."
  constraints:
    - "Only scan the immediately previous assistant message, not user message"
    - "Each failure class recommended at most once per session (dedup)"
    - "Must not trigger if the matching pack is already installed"
  success_conditions:
    - "Returns {detected: bool, failure_class: str|null, recommended_pack: str|null, confidence: float}"
    - "detected=false when no failure pattern matches"
    - "detected=true implies failure_class ∈ FAILURE_SIGNALS keys"
  non_goals:
    - "Does not install the pack"
    - "Does not diagnose root cause"
memory_slice:
  admissible:
    - "Previous assistant message text"
    - "Session-level dedup set (already-recommended classes)"
    - "installed-packs.json contents"
  excluded:
    - "User's current message (not scanned for failures)"
    - "Topics older than previous turn"
  unknown_state:
    - "Whether the user will accept the recommendation"
evidence_bundle:
  admissible_evidence:
    - id: "catalog_query.FAILURE_SIGNALS"
      type: "deterministic_regex_table"
      source: "scripts/catalog_query.py lines 214-226"
    - id: "installed-packs.json"
      type: "registry_state"
      source: "platform-specific installed-packs.json"
  evidence_types: ["deterministic_regex_table", "registry_state"]
output_contract:
  required_fields:
    - name: detected
      type: boolean
      validator: "isinstance(x, bool)"
    - name: failure_class
      type: "string|null"
      validator: "x is None or x in FAILURE_SIGNALS"
    - name: recommended_pack
      type: "string|null"
      validator: "x is None or x in ALIAS_MAP.values()"
    - name: confidence
      type: number
      validator: "0.0 <= x <= 1.0"
    - name: dedup_key
      type: "string|null"
      validator: "x is None or matches '^{failure_class}::{session_id}$'"
  citation_policy: "N/A (deterministic, no LLM claims)"
  blocked_outputs:
    - "Pack recommendation when pack already installed"
    - "Duplicate recommendation within same session"
validator_gate:
  type: "deterministic_python"
  script: "validators/step_validators/test_failure_signal.py"
  golden_fixtures: ["fixtures/step1.5-failure-signal/golden.1.yaml"]
  known_bad_fixtures:
    - path: "fixtures/step1.5-failure-signal/known_bad.1.yaml"
      expected_violation: "false_positive"
      intended_reason: "No failure pattern in previous turn, but detected=true"
    - path: "fixtures/step1.5-failure-signal/known_bad.2.yaml"
      expected_violation: "false_negative"
      intended_reason: "Clear 'deploy failed' in previous turn, but detected=false"
    - path: "fixtures/step1.5-failure-signal/known_bad.3.yaml"
      expected_violation: "duplicate_recommendation"
      intended_reason: "deploy already recommended this session, recommended again"
  pass_threshold: 1.0  # all golden pass + all known-bad fail
repair_strategy:
  max_iterations: 1
  on_violation:
    - violation_type: "false_positive"
      action: "tighten_regex"
      contract_revision: "narrow FAILURE_SIGNALS pattern"
    - violation_type: "false_negative"
      action: "broaden_regex"
      contract_revision: "expand FAILURE_SIGNALS pattern"
    - violation_type: "duplicate_recommendation"
      action: "enforce_dedup"
      contract_revision: "add session-state check to output_contract.blocked_outputs"
admission:
  fixture_schema_valid: true
  golden_output_passes: true
  known_bad_output_fails_for_intended_reason: true
  composition_interface: "output feeds step2-skill-sense.memory_slice"
  claim_boundary_updated: false  # set true after first repair cycle
```

### 3.3 All 5 Atoms (summary table)

| Atom | Primary Mechanism | Dominant Failure Mode | Validator Type |
|---|---|---|---|
| step0-mode-read | Load depth/rigor from yaml | Missing/invalid fields | Schema check on yaml |
| step1-topic-check | Read injected topic context | Misread risk level | Risk-level enum + range check |
| step1.5-failure-signal | Regex match prev turn | False positive/negative | Fixture-driven classifier test |
| step2-skill-sense | 3-tier gap detection | Wrong pack / missed gap | Trigger-coverage + intent-confidence check |
| step2.5-anti-sycophancy | Rubric-first pause | Skipped pause on eval question | Eval-question detection + counter-arg presence check |

---

## 4. Design: Repair Loop (paper §3.6 adapted)

The 7-step protocol, adapted for Companion's incremental nature:

```
┌─────────────────────────────────────────────────────────────────┐
│ 1. OBSERVE     A Gateway atom produces a violating output         │
│    (validator returns ContractResult(status=FAIL, violations))   │
│                                                                  │
│ 2. ISOLATE     Classify violation: which contract field failed?  │
│    Which failure mode (false_positive/false_negative/duplicate)? │
│                                                                  │
│ 3. EXPLICIT    Update the .contract.yaml: add the obligation as  │
│    a blocked_output, narrow/broaden regex, or add field validator│
│                                                                  │
│ 4. KNOWN-BAD   Write a fixture to fixtures/{atom}/known_bad.N.yaml│
│    capturing the exact violating input/output pair               │
│                                                                  │
│ 5. REGRESSION  Run validators/validate_contract.py --atom X      │
│    All golden must pass; all known-bad must fail                 │
│                                                                  │
│ 6. SMOKE       Run catalog_query.py --check-failures "<text>"    │
│    with the triggering input; confirm repaired behavior          │
│                                                                  │
│ 7. UPDATE      Append to repair/known_bad_registry.jsonl;        │
│    update references/claim-boundary.md if claim scope changed    │
└─────────────────────────────────────────────────────────────────┘
```

**Key adaptation from paper**: Step 6 in the paper runs a "targeted real-model slice." For Companion atoms, most validators are deterministic (no LLM call), so Step 6 is a deterministic smoke test via `catalog_query.py`. Only step2-skill-sense and step2.5-anti-sycophancy involve LLM judgment — for those, Step 6 runs the existing eval dataset (`benchmarks/datasets/skill-sense.jsonl`).

**Termination**: max_iterations=1 by default. If a single contract revision doesn't fix the violation, escalate to human (log to backlog, proceed with current behavior). This prevents infinite loops and matches the paper's "update backlog before expanding scope."

---

## 5. Design: Composition (Gateway Macro)

Paper Stage 7p v1 showed: atoms passing individually ≠ macro passing. Cross-step obligations must be explicit.

The Gateway is a macro composing 5 atoms in order. The `gateway-macro.contract.yaml` defines:

```yaml
atom_id: gateway-macro
version: v1
task_spec:
  objective: "Run all Gateway atoms in order, carrying cross-step obligations"
composition:
  sequence:
    - step0-mode-read
    - step1-topic-check
    - step1.5-failure-signal
    - step2-skill-sense
    - step2.5-anti-sycophancy
  carried_obligations:           # paper Stage 7p v2 lesson
    - from: step0-mode-read
      carry: "depth, rigor"
      to: [step2.5-anti-sycophancy]   # rigor controls anti-sycophancy proactivity
    - from: step1.5-failure-signal
      carry: "recommended_pack"
      to: [step2-skill-sense]         # skill sense must not re-recommend
    - from: step2-skill-sense
      carry: "gap_detected, confidence"
      to: [step2.5-anti-sycophancy]   # eval questions only pause if not already gap-handled
  blocked_outputs:
    - "Proceeding to Step 3 when step1.5 detected an unresolved failure signal"
    - "Anti-sycophancy pause when step0 rigor=false and question is not explicitly evaluative"
```

**Macro validator**: runs all 5 atom validators + checks carried_obligations are respected. This is the paper's Stage 7p v2 "explicit composition-retention contract."

---

## 6. Integration Points (minimal, non-disruptive)

| Change | File | Type | Risk |
|---|---|---|---|
| Add `--validate-contracts` flag | `catalog_query.py` | Additive (new flag, no behavior change without flag) | Low |
| Add contract eval module | `benchmarks/scripts/modules/contract_eval.py` | New file | None |
| Add contract docs | `references/contract-methodology.md`, `claim-boundary.md` | New files | None |
| Gateway AGENTS.md references contracts | `packs/core/petfish-companion-skill/AGENTS.md` | Additive section | Low (references, not enforcement) |
| Install pipeline copies contracts/ | `install.py` | Extend skill-file copy glob | Low |

**Explicitly NOT changing**:
- `AGENTS.md` Gateway step definitions (instructions stay primary; contracts are verification layer)
- `router.py` online gateway (separate runtime; future work)
- Skill execution inside Steps 3+ (out of scope per §2.2)

---

## 7. Evaluation Plan (paper §3.7 metrics, adapted)

### 7.1 Per-atom metrics

| Metric | What it checks | Evaluator |
|---|---|---|
| `schema_validity` | Output has required fields, correct types | JSON Schema check |
| `citation_grounding` | N/A for deterministic atoms; for LLM atoms, claims cite evidence | Evidence-ID check |
| `context_relevance` | Step only read admissible memory_slice | Memory-access audit |
| `atom_primary_metric` | The atom's dominant obligation | Atom-specific (e.g., failure-signal F1) |
| `validator_gate_pass` | Golden pass + known-bad fail | Deterministic test runner |

### 7.2 Macro metrics

| Metric | What it checks |
|---|---|
| `stage_completion` | All 5 atoms ran in order |
| `carried_obligation_retention` | Cross-step obligations preserved (paper Stage 7p v2) |
| `no_blocked_output` | No blocked_output condition triggered |

### 7.3 Benchmark datasets

- `benchmarks/datasets/gateway-contracts.jsonl` — input/output pairs per atom, labeled golden/known-bad
- `benchmarks/datasets/gateway-repair-loops.jsonl` — violation→repair→revalidate sequences

### 7.4 Initial targets (bounded, matching paper discipline)

- Each atom: golden 100% pass, known-bad 100% fail (admission gate)
- Macro: carried_obligation_retention = 1.0 (paper Stage 7p v2 target)
- **NOT targeted**: whole-companion reliability, user satisfaction, open-workflow success

---

## 8. Claim Boundary (paper Appendix A discipline)

This upgrade establishes:

> Each Companion Gateway atom, when formalized as a contract with golden/known-bad fixtures and a deterministic validator, can be tested, repaired, and regression-covered independently. Cross-step carried obligations can be preserved when made explicit in the macro contract.

This upgrade does NOT establish:

- whole-companion reliability or production readiness;
- that contract-driven Gateway improves user-facing outcomes;
- that the methodology transfers to skill execution, deploy, research, or course workflows;
- cost-effectiveness vs. a stronger model;
- coverage of novel failure modes (known-bad library is incremental).

---

## 9. Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Over-engineering: contracts add overhead without value | Medium | Medium | Validators are deterministic Python (no LLM cost); contracts are opt-in via flag |
| Known-bad library never complete | High | Low | Accepted; claim boundary explicitly excludes novel failures |
| Drift between contracts and AGENTS.md instructions | Medium | High | Contract docs reference AGENTS.md line numbers; lint check for drift (future) |
| Maintenance burden (5 contracts × fixtures × validators) | Medium | Medium | Start with 1 atom (step1.5-failure-signal), prove value, expand |
| False sense of security ("we have contracts, we're reliable") | Medium | High | Claim-boundary.md is required reading; anti-sycophancy skill co-loaded |

---

## 10. Phased Delivery

### Phase 1: Prove the pattern (1 atom)
- Implement contract schema `_schema.json`
- Implement step1.5-failure-signal contract + validator + 3 fixtures (1 golden, 2 known-bad)
- Implement `validate_contract.py` runner
- Implement `contract_eval.py` benchmark
- Write `contract-methodology.md` and `claim-boundary.md`
- **Gate**: admission criteria met for this 1 atom (paper §3.5)

### Phase 2: Expand to all deterministic atoms
- step0-mode-read, step1-topic-check (deterministic, schema-validated)
- Each with golden + ≥2 known-bad fixtures
- **Gate**: all deterministic atoms pass admission

### Phase 3: LLM-involving atoms
- step2-skill-sense (uses existing skill-sense.jsonl eval)
- step2.5-anti-sycophancy (new eval dataset needed)
- Repair loop with max_iterations=1
- **Gate**: targeted smoke tests pass on existing eval datasets

### Phase 4: Macro composition
- gateway-macro.contract.yaml with carried_obligations
- Macro validator
- benchmarks/datasets/gateway-contracts.jsonl full dataset
- **Gate**: carried_obligation_retention = 1.0

### Phase 5: Integration
- `catalog_query.py --validate-contracts` flag
- AGENTS.md additive section referencing contracts
- install.py copies contracts/ directory
- **Gate**: fresh install works; `--validate-contracts` runs clean

Each phase is independently shippable. Phase 1 alone proves the methodology in this codebase.

---

## 11. Open Questions for Momus

1. **Contract file format**: YAML (chosen for readability) vs JSON (strict schema). YAML allows comments; JSON is stricter. Recommendation: YAML with JSON Schema validation.
2. **Validator placement**: inside fish-brain/scripts/ (co-located) vs separate validators/ dir (clean separation). Recommendation: separate dir, imported by scripts.
3. **Should contracts be installed to user projects, or stay in the pack source only?** If installed, they're visible but add files; if source-only, they're dev artifacts. Recommendation: install contracts/ and fixtures/ (transparency), keep validators/ as scripts (executable).
4. **Repair loop automation**: fully automatic (risky) vs human-in-loop (slow). Recommendation: log violations to known_bad_registry.jsonl automatically, but contract revisions require human commit (matches paper's "update claim boundary before expanding scope").
5. **Scope of Phase 1**: is step1.5-failure-signal the right first atom? It's the most deterministic (regex-based), lowest risk. Alternative: step0-mode-read (simplest schema check). Recommendation: step1.5 (more interesting failure modes, proves the pattern better).

---

## 12. References

- **Source paper**: `dev_reference/contract-driven-harness-arxiv-v4-humanized-draft.md` (§3.2 objects, §3.4 atoms, §3.5 admission, §3.6 repair loop, §3.7 metrics, Appendix A non-claims)
- **External research** (from librarian agent bg_5a83fd63):
  - DSPy signatures (declarative contracts + Assertions retry) — ICLR 2024
  - Instructor (Pydantic + auto-retry, cleanest contract+repair primitive)
  - Outlines (generation-time constraint enforcement)
  - LLMCompiler (DAG decomposition), ADAPT (as-needed recursive decomposition)
  - CRITIC (tool-interactive critique; ablation shows tools are the key)
  - Self-Refine / Reflexion (self-correction baselines; diminishing returns without tools)
  - Optimal stopping for repair loops (arXiv 2604.02035)
  - promptfoo (production eval harness with is-json + llm-rubric assertions)
- **Existing repo patterns** (from explore agents):
  - `online-gpt/instructions/answer-contract.md` (7 typed contracts — most mature pattern)
  - `online-gpt/gateway/CONTRACTS.md` (8 module contracts)
  - `.opencode/skills/skill-lint/scripts/lint_skill.py` (--fix/--fix-apply dry-run→apply→revalidate loop)
  - `.opencode/skills/quality-gate/scripts/run_gate.py` (PASS/CONDITIONAL/FAIL decision)
  - `packs/optional/research-skill-pack/schemas/*.json` (7 JSON Schema contracts)
  - `.opencode/skills/research-router/SKILL.md` (decomposition pattern)
  - `.opencode/skills/fish-trail/scripts/topic_validate.py` (graph validation pattern)

---

## 13. Success Criteria for THIS Plan (Momus review)

This plan is ready for implementation when Momus confirms:

- [ ] Scope is bounded (not whole-companion) and justified
- [ ] Non-goals are explicit and mirror paper discipline
- [ ] Contract object model maps paper's 7 objects faithfully
- [ ] Repair loop adapts paper's 7 steps with clear termination
- [ ] Integration is additive (no disruption to existing Gateway)
- [ ] Phased delivery has clear gates
- [ ] Anti-sycophancy pre-review is documented and addressed
- [ ] Open questions are enumerated for decision

---

**End of plan. Submitting to Momus for review.**
