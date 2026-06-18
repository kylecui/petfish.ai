# QA/QC Record — petfish-companion-skill v1.2.0 + v1.3.0

**Date**: 2026-06-18
**Scope**: Contract-driven Gateway atoms + observability + reading-notes
**Method**: Deterministic validators (pure stdlib) + eval regression

---

## QA: Problem Discovery & Validation

### QA-1: Contract Validators (42 checks)

| Atom | Golden | Known-bad | Result |
|---|---|---|---|
| step0-mode-read | 5/5 PASS | 3/3 rejected | ✅ |
| step1-topic-check | 5/5 PASS | 3/3 rejected | ✅ |
| step1.5-failure-signal | 4/4 PASS | 3/3 rejected | ✅ |
| step2-skill-sense | 5/5 PASS | 3/3 rejected | ✅ |
| step2.5-anti-sycophancy | 4/4 PASS (detection) | 2/2 rejected | ✅ |
| gateway-macro | 3/3 PASS | 3/3 rejected | ✅ |
| **Total** | **26/26** | **17/17** | **PASS** |

### QA-2: Eval Regression (no behavioral regression)

| Dataset | Entries | Accuracy | Result |
|---|---|---|---|
| skill-sense.jsonl | 20 | 1.0000 | ✅ |
| failure-signal.jsonl | 15 | 1.0000 | ✅ |

### QA-3: Repair Loop Finding

Phase 3 validator caught calibrate TRIGGERS missing "好吗"/"合理"/"你觉得".
Fixed in catalog_query.py + skill_sense_eval.py. Regression passed.
This demonstrates the contract-driven methodology working as designed.

### QA-4: Reading-Notes Lint

| Test | Entries | Errors | Result |
|---|---|---|---|
| Valid entries | 3 | 0 | ✅ PASS |
| Invalid entries | 1 | 4 (all violations caught) | ✅ PASS |

### QA-5: Non-Coupling Verification

- Zero references to evidence-ledger/EV- in companion scripts: ✅
- Zero references to reading-notes/CN- in research pack: ✅ (1 false positive = directory name coincidence)

### QA-6: Install Pipeline

- shutil.copytree recursively copies contracts/fixtures/validators: ✅
- New directories ship to users without install.py changes: ✅

---

## QC: Release Decision

### Issues Found → Resolved

| Issue | Severity | Resolution | Status |
|---|---|---|---|
| calibrate TRIGGERS missing Chinese eval patterns | Medium | Added 6 keywords to catalog_query.py + skill_sense_eval.py | ✅ Closed |
| Install/upgrade docs not synced | Low | Updated agent-install.md + agent-upgrade.md | ✅ Closed |
| Contract concepts not in agent instructions | Medium | Added SKILL.md Section 9 + AGENTS.md sections | ✅ Closed |
| Reading-notes not Gateway-enforced | High | Added Step 2.6 to Gateway flow | ✅ Closed |
| Staleness detection missing | High | Added file_mtime + file_size schema fields + stat logic | ✅ Closed |
| Version tag conflict (v1.2.0/v1.3.0 vs project v1.7.0) | Critical | Deleted erroneous tags, will release as v1.8.0 | ✅ Closed |

### Open Issues (accepted risk)

| Issue | Risk | Rationale |
|---|---|---|
| step2.5 behavior-level validation deferred to llm_judge | Low | Detection-level is deterministic; behavior-level inherently requires LLM judgment |
| Known-bad library is incremental (novel failures not pre-cataloged) | Medium | Accepted per claim boundary; matches paper Appendix A discipline |
| Reading-notes relies on agent compliance (no plugin enforcement) | Medium | Gateway Step 2.6 + trace observability provide best-effort enforcement without plugin infrastructure |

### Decision

**RELEASE APPROVED** — all blocking issues closed. Open issues are accepted risks with documented rationale.

Conditions:
- Release as project v1.8.0 (not pack-internal version)
- Update README Version History
- Create companion CHANGELOG (this document's sibling)
