# ONLINE-PROJECT-RUNTIME Upgrade Plan

**Source**: `online-gpt/ONLINE-PROJECT-RUNTIME.md` §10-15
**Audit scope**: 40+ files referencing local-runtime patterns
**Principle**: ChatGPT Project = first-class online PEtFiSh runtime, not a fake local adapter

---

## Phase 1: Core Runtime Files (ADD)

### 1.1 `online-gpt/runtime-contract.md`
Online runtime contract defining:
- `kind: online | surface: chatgpt-project | local_adapter: none`
- Allowed work vs prohibited claims
- Trust Gate defaults for online

### 1.2 `online-gpt/profiles/review-online.yaml`
Online code review profile:
- Packs: companion, context, petfish, testdocs, trust (core); calibrate, deploy (optional)
- Review dimensions: correctness, security, tests, maintainability, architecture, release_risk, missing_evidence
- Gateway policy: topic_check, anti_sycophancy, failure_signal_detection, skill_sense, trust_gate
- Non-goals: local test execution, repository mutation, git operations, deployment, publishing

### 1.3 `online-gpt/project-instructions/code-review.md`
ChatGPT Project instructions template for online code review.

### 1.4 `docs/online-projects.md`
User-facing documentation — local vs online project mode comparison.

### 1.5 `online-gpt/evals/online-runtime-cases.jsonl`
5 eval cases for online runtime regression:
- no-platform-nag: no `--platform opencode` in online context
- no-fake-local-access: requires "upload"/"paste" instead of claiming repo access
- risky-change-trust-gate: refusal pattern for dangerous PRs
- deploy-pack-optional: deploy is optional for review-only projects
- online-profile-selection: review-online recommended for ChatGPT-only reviews

---

## Phase 2: Knowledge Files (UPDATE)

### 2.1 `knowledge/01-system-overview.md`
- **Current state**: Describes PEtFiSh as installable framework with local platforms
- **Change**: Add "Two Project Modes" section: local (IDE/CLI adapter) vs online (ChatGPT Project)
- **Risk**: Low — additive change

### 2.2 `knowledge/03-pack-index.md`
- **Current state**: Lists profiles (minimal, course, code, ops, security, research, writing, comprehensive) — all local
- **Change**: Add `review-online` profile entry; note it as online-only, no local install required
- **Risk**: Low — additive

### 2.3 `knowledge/04-platform-adapters.md`
- **Current state**: Lists 8 IDE/CLI platforms (opencode, claude, codex, cursor, copilot, windsurf, antigravity, universal)
- **Change**: Add "ChatGPT Project" as a platform row with `skills_dir: N/A (online)`, `instructions_file: GPT Instructions`
- **Risk**: Low — additive

### 2.4 `knowledge/05-install-command-reference.md`
- **Current state**: Documents `uv run install.py --platform opencode` as primary flow
- **Change**: Add section: "Online Projects" — no local install needed; packs are semantic references; explain when local install IS needed vs when online mode suffices
- **Risk**: Medium — must not break existing install reference

---

## Phase 3: Gateway Modules (UPDATE)

### 3.1 `gateway/modules/installer.py`
- **Current state**: Always renders `uv run install.py --platform <platform> --target .`
- **Change**: Detect `platform == "online"` → return `operation: semantic_only`, `command: null`, explanation that packs are referenced semantically, not installed locally
- **Risk**: Medium — changes module behavior; test with `platform=online`

### 3.2 `gateway/router.py`
- **Current state**: Platform detection defaults to `opencode`; no online context awareness
- **Change**: When `project_profile == "review-online"` or `platform == "online"`, skip install routing and prefer advice_only contract
- **Risk**: Medium — routing priority change

### 3.3 `gateway/schemas.py`
- **Current state**: `Platform` enum has 8 values, no "online"
- **Change**: Add `"online"` to Platform enum; add `"online"` to allowed platform values in both OpenAPI schemas
- **Risk**: Low — additive enum value

---

## Phase 4: Actions & APIs (UPDATE)

### 4.1 `actions/openapi.gateway-only.yaml`
- **Change**: Add `"online"` to Platform enum in schema
- **Risk**: Low

### 4.2 `actions/openapi.yaml`
- **Change**: Add `"online"` to Platform enum in schema
- **Risk**: Low

---

## Phase 5: Instructions (UPDATE)

### 5.1 `instructions/petfish-companion.instructions.md`
- **Current state**: Lists IDE/CLI agents as optional adapters (12 mentions); says "those agents are optional execution adapters"
- **Change**: Add explicit online-first section: "ChatGPT Project is a first-class online PEtFiSh runtime. It does not require any local adapter. When users ask for code review, architecture assessment, or skill design within a ChatGPT Project, treat the Project itself as the runtime."
- **Risk**: Low — boundary clarification

---

## Phase 6: RC Documents (UPDATE)

### 6.1 `online-gpt/README.md`
- **Change**: Add `runtime-contract.md`, `profiles/review-online.yaml`, `project-instructions/` to directory map
- **Risk**: Low

### 6.2 `RELEASE-CANDIDATE.md`
- **Change**: Add "ChatGPT Project as online PEtFiSh runtime" to Included in this RC → P0 Standalone
- **Risk**: Low

### 6.3 `GPT-BUILDER-RUNBOOK.md`
- **Change**: Add Step 2a: "If this GPT will be used in a ChatGPT Project for code review, also create a Project with `project-instructions/code-review.md` as the project instructions."
- **Risk**: Low

---

## Phase 7: Eval Suite (UPDATE)

### 7.1 `gateway/eval_runner.py`
- **Change**: Add `"online"` to platform inference logic
- **Risk**: Low

### 7.2 `tools/check_alignment.py`
- **Change**: Add `"online"` to `EXPECTED_PLATFORMS` set
- **Risk**: Low

---

## Phase 8: Remaining Files (REVIEW — No Change Needed)

The following files reference IDE/CLI/local terms in boundary-setting context. They correctly describe the boundary between online and local. No change required:

- `instructions/safety-boundary.md` — defines execution modes and risk classes
- `instructions/answer-contract.md` — defines response contracts, not platform defaults
- `instructions/anti-sycophancy.md` — review discipline
- `OPERATING-MODES.md` — already defines P0/P1/P2 priority
- `PRINCIPLES.md` — design principles, mentions adapters as optional
- `STANDALONE-ACCEPTANCE.md` — acceptance criteria
- `ADAPTER-ACCEPTANCE.md` — P2 boundary
- `GATEWAY-ACCEPTANCE.md` — P1 boundary
- `remote-daemon/SPEC.md` — P2 adapter spec
- `SECURITY.md` — security boundaries
- `ALIGNMENT.md`, `SOURCE-OF-TRUTH.md` — alignment docs

---

## File Change Summary

| Action | Count | Files |
|--------|-------|-------|
| **ADD** | 5 | `runtime-contract.md`, `profiles/review-online.yaml`, `project-instructions/code-review.md`, `docs/online-projects.md`, `evals/online-runtime-cases.jsonl` |
| **UPDATE** | 13 | `knowledge/01-04-05`, `installer.py`, `router.py`, `schemas.py`, `openapi.yaml`×2, `instructions`, `README`, `RELEASE-CANDIDATE`, `GPT-BUILDER-RUNBOOK`, `eval_runner.py`, `check_alignment.py` |
| **NO CHANGE** | 20+ | boundary docs, P2 specs, smoke scripts |

---

## Implementation Order

```
1. Phase 1: ADD runtime-contract.md + review-online.yaml + project-instructions + docs + evals
2. Phase 5: UPDATE instructions/petfish-companion.instructions.md (online-first preamble)
3. Phase 2: UPDATE knowledge/01, 03, 04, 05 (add online mode everywhere)
4. Phase 3: UPDATE gateway/schemas.py → router.py → installer.py
5. Phase 4: UPDATE openapi.yaml ×2 (add "online" enum)
6. Phase 7: UPDATE eval_runner + check_alignment
7. Phase 6: UPDATE README, RELEASE-CANDIDATE, GPT-BUILDER-RUNBOOK
8. Run online-gpt regression: compile, smoke, evals, alignment
```

## Rollback

All changes are additive or minimally invasive. Rollback: delete 5 new files, revert 13 updated files. No installer/platforms.json changes.
