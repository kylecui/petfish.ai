# Trigger Evaluation Batch Report

**Date**: 2026-05-08  
**Evaluator**: `skill-trigger-evaluator/scripts/evaluate_triggers.py`  
**PEtFiSh version**: v0.8.1  
**Skills tested**: 51  
**Method**: keyword overlap scoring (Jaccard-like), threshold 0.80

## Summary

| Verdict | Count | Percentage |
|---------|-------|-----------|
| PASS    | 17    | 33%       |
| FAIL    | 34    | 67%       |

**Two-thirds of all installed skills fail trigger evaluation.**

## Full Results

| Skill | Pass Rate | FP Rate | Verdict | Test Source |
|-------|-----------|---------|---------|-------------|
| anti-sycophancy-calibration | 0.75 | 0.00 | FAIL | auto |
| course-content-authoring | 0.00 | 0.00 | FAIL | auto |
| course-development-orchestrator | 0.25 | 0.00 | FAIL | auto |
| course-directory-structure | 0.13 | 0.00 | FAIL | auto |
| course-lab-design | 0.00 | 0.00 | FAIL | auto |
| course-methodology-playbook | 0.00 | 0.00 | FAIL | auto |
| course-outline-design | 0.25 | 0.00 | FAIL | auto |
| course-quality-assurance | 0.25 | 0.00 | FAIL | auto |
| course-quality-control-reporting | 0.00 | 0.00 | FAIL | auto |
| deployment-executor | 0.25 | 0.00 | FAIL | auto |
| deployment-verifier | 0.00 | 0.00 | FAIL | auto |
| development-plan-governance | 0.00 | 0.00 | FAIL | auto |
| drawio-course-diagrams | 0.25 | 0.00 | FAIL | auto |
| fish-trail | 0.00 | 0.00 | FAIL | auto |
| generate-test-cases | 1.00 | 0.00 | PASS | auto |
| generate-usage-docs | 1.00 | 0.13 | PASS | auto |
| incident-rollback | 1.00 | 0.00 | PASS | auto |
| instructor-reference-materials | 0.25 | 0.00 | FAIL | auto |
| learner-materials | 0.25 | 0.00 | FAIL | auto |
| markdown-course-writing | 1.00 | 0.00 | PASS | auto |
| marketplace-connector | 0.50 | 0.00 | FAIL | auto |
| petfish-companion | 0.70 | 0.20 | FAIL | curated |
| petfish-style-rewriter | 1.00 | 0.00 | PASS | auto |
| ppt-reader | 0.00 | 0.25 | FAIL | auto |
| ppt-writer | 0.00 | 0.00 | FAIL | auto |
| project-initializer | 0.13 | 0.13 | FAIL | auto |
| quality-gate | 1.00 | 0.00 | PASS | auto |
| reference-document-review | 0.25 | 0.00 | FAIL | auto |
| repo-runtime-discovery | 1.00 | 0.00 | PASS | auto |
| repo-service-lifecycle | 1.00 | 0.00 | PASS | auto |
| repo-skill-miner | 1.00 | 0.00 | PASS | auto |
| research-brief-framer | 1.00 | 0.00 | PASS | auto |
| research-evidence-ledger | 0.33 | 0.00 | FAIL | auto |
| research-insight-log | 0.13 | 0.00 | FAIL | auto |
| research-literature-access | 1.00 | 0.00 | PASS | auto |
| research-note-capture | 0.00 | 0.00 | FAIL | auto |
| research-quality-reviewer | 0.00 | 0.00 | FAIL | auto |
| research-report-writer | 0.25 | 0.00 | FAIL | auto |
| research-router | 0.10 | 0.25 | FAIL | curated |
| research-source-discovery | 0.00 | 0.00 | FAIL | auto |
| research-synthesis | 0.00 | 0.00 | FAIL | auto |
| service-operations | 1.00 | 0.00 | PASS | auto |
| skill-author | 0.17 | 0.00 | FAIL | auto |
| skill-description-optimizer | 1.00 | 0.00 | PASS | auto |
| skill-lint | 0.75 | 0.00 | FAIL | auto |
| skill-reference-discovery | 0.00 | 0.00 | FAIL | auto |
| skill-security-auditor | 1.00 | 0.00 | PASS | auto |
| skill-trigger-evaluator | 1.00 | 0.00 | PASS | auto |
| skill-trust-governance | 1.00 | 0.00 | PASS | auto |
| skill-usage-tracker | 0.63 | 0.00 | FAIL | auto |
| target-host-readiness | 1.00 | 0.00 | PASS | auto |

## Analysis

### Not a language issue

Both CN and EN description skills appear in PASS and FAIL groups. The correlation is with **how distinctive the skill's trigger keywords are**, not with language.

### Skills that PASS tend to have:
- Unique domain-specific terms in their description (e.g., "rollback", "lint", "ONNX", "trust")
- Narrow, specific trigger scope
- Short, keyword-dense descriptions

### Skills that FAIL tend to have:
- Generic terms shared across many skills (e.g., "course", "review", "create", "design")
- Broad domain coverage
- Long descriptions where keywords get diluted

### The auto-generated query problem

Most skills use auto-generated test queries. The evaluator extracts trigger phrases from the description and generates test queries from them. When the description uses generic verbs and nouns, the auto-generated queries also use generic terms, which don't achieve high keyword overlap scores against the full description keyword set.

### Root cause

Same as #77: keyword-only scoring is structurally inadequate for:
1. Skills with broad trigger domains
2. Skills whose descriptions share vocabulary with sibling skills
3. Chinese descriptions where single-character splitting creates noise
4. Auto-generated queries that don't match real user intent patterns

## Recommendation

The evaluator needs semantic scoring (embedding similarity) to be useful across the full skill catalog. The current keyword-overlap approach produces meaningful results for only ~33% of skills.

## Related Issues

- [#77](https://github.com/kylecui/petfish.ai/issues/77) — evaluate_triggers keyword scoring fails for broad skills
- [#74](https://github.com/kylecui/petfish.ai/issues/74) — research-router trigger-eval harness
