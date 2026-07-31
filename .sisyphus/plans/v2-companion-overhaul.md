# PEtFiSh v2 — Companion Overhaul Plan

> **Branch**: `refactor/v2-companion-overhaul`
> **Date**: 2026-07-31
> **Status**: DRAFT — awaiting user confirmation
> **Methodology**: Test-first, no MVP stages (per user directive #10)

---

## 0. Executive Summary

Seven parallel audits across the entire PEtFiSh codebase reveal that the project's core architectural premise — a "companion gateway" that proactively guards, senses, and routes — **is almost entirely prompt-based with no programmatic enforcement**. This single root cause explains the majority of user-reported issues: inconsistent skill dispatch, unreliable topic management, aggressive approach-switching on transient failures, and passive behavior where proactivity was promised.

This plan proposes a fundamental shift: **move enforcement from prompt instructions to programmatic plugins**, fix critical data-loss bugs, unify the installer, build a real skill registry, and establish a genuine contributor marketplace — all delivered through test-first development.

---

## 1. Root Cause Diagnosis (11 Problems → 4 Architectural Gaps)

### Gap A: Prompt-Based Enforcement (Problems 1, 4, 5, 7, 9)

**Symptoms**: Gateway steps are inconsistently followed; skills require manual invocation; companion is "too passive" for skill discovery but "too proactive" when switching approaches on failure; installer still emits deprecated commands.

**Root Cause**: The Companion Gateway (6 steps in AGENTS.md) has **zero programmatic enforcement**:
- Only 2 of 4 plugins are registered in `opencode.json` (`topic-context-filter` and `fish-trail-compaction` exist but are NOT enabled).
- AGENTS.md line 479 **falsely claims** a "response gate plugin" exists — it does not.
- The OpenCode plugin API (`@opencode-ai/plugin@1.4.0`) has no `chat.response.transform` hook, making output-level enforcement currently impossible.
- `catalog_query.py` upgrade path still emits `remote-install.ps1`/`.sh` (deprecated since v1.5.0).
- Skill Sense TRIGGERS table covers only 9 domains; Tier 2 detection is LLM-only with no code backing.
- `/petfish suggest` is manual, not triggered by task context.

**Evidence Files**:
- `opencode.json` — only registers `system-prompt-rules` + `system-prompt-context-inject`
- `.opencode/plugin/topic-context-filter.ts` — exists but unregistered
- `AGENTS.md:479` — false response gate claim
- `packs/core/petfish-companion-skill/.opencode/skills/fish-brain/scripts/catalog_query.py:647-753` — deprecated upgrade commands

### Gap B: Fragile Context Management (Problem 3)

**Symptoms**: "omitted message" appears frequently in `ai_harness_courseware`, causing incomplete work.

**Root Cause**: `topic-context-filter.ts` has a **placeholder accumulation bug**:
- Removed messages are replaced with assistant placeholder messages: `[N messages from other topics omitted]`
- On the next turn, these placeholders score 0 against topic keywords (they're not system directives, not tool results) and get removed again
- New placeholders are emitted in their place
- Result: **progressive content erosion** — real messages disappear, conversation fills with self-replacing placeholders
- The log misleadingly reports `removed: 0` because placeholder count offsets removal count (1-for-1 replacement)

**Secondary Issues**:
- Keyword matching for topic relevance is inherently fragile (substring matching against a keyword set built from topic title/scope/tags)
- The filter activates with only 10 messages (`minMessages`) and protects only the last 3 (`safetyWindow`)
- `removeRatio` allows 20%-50% of messages to be replaced — a huge window for context loss

**Evidence Files**:
- `.opencode/plugin/topic-context-filter.ts:419-445` — placeholder insertion logic
- `.petfish/fish-trail/filter-debug.log` — shows `removed:0` but `remove_ratio:0.331` with placeholder previews
- 5 recent commits (9c0bd2b through 5838b84) patched symptoms but not the root cause

### Gap C: No Authoritative Skill Registry (Problems 2, 5, 7, 8)

**Symptoms**: Global/local boundary unclear; skill search finds nothing or hallucinates; publishing pipeline has many bugs; no real marketplace.

**Root Cause**:
- `marketplace_search.py` has only **4 hardcoded local items** (`companion`, `init`, `toolchain`, `context`); everything else queries remote sources live, which can fail or return nothing
- `installed-packs.json` tracks versions but no comparison logic exists to skip re-installs
- `petfish-market` is a **static JSON registry** — no CLI, no contributor workflow, no CI/CD, no versioning per skill
- OpenCode skill matching is purely frontmatter `description`-based — if a description misses a synonym, the skill never loads
- No index of all PEtFiSh skills exists locally for reliable search
- 4 installers (install.py + 3 legacy) have feature drift; install.py has market resolution + mirror fallback, others don't

**Evidence Files**:
- `packs/core/petfish-companion-skill/.opencode/skills/fish-market/scripts/marketplace_search.py` — LOCAL_CATALOG = 4 items
- `petfish-market/` — static JSON, no contributor tooling
- `install.py` — version tracking exists but no skip-if-current logic

### Gap D: Missing Web-Grounding Discipline (Problem 6)

**Symptoms**: Companion answers from model "knowledge" (potential hallucination) instead of referencing authoritative sources.

**Root Cause**: Web search tools exist (`web-search-prime`, `web-reader`, `context7`) but:
- No system prompt rule forces "search before answering" for factual/library questions
- No tool-availability signal tells the model when web tools are appropriate
- No citation verification mechanism exists
- Competitive analysis shows Cursor, Copilot, Phind, Perplexity all use **explicit tool availability + system prompt steering**, not model goodwill

---

## 2. Architectural Vision: PEtFiSh v2

### Design Principles

1. **Programmatic > Prompt-based**: Every critical gateway behavior must have code enforcement, not just AGENTS.md instructions.
2. **Test-first**: Every new behavior gets tests before implementation. No "try it and see."
3. **Companion, not toolbox**: The companion should sense, guard, and route proactively — but with guardrails that prevent rogue behavior.
4. **One installer**: `install.py` is the only installer. Legacy scripts are deleted, not "synced."
5. **Real marketplace**: GitHub-based contributor workflow with CI/CD, not static JSON.
6. **Web-first**: Factual claims require sources; library questions require documentation lookup.

### Target Architecture

```
User Message
    │
    ▼
┌─────────────────────────────────────────────┐
│ companion-gateway.ts (NEW PLUGIN)           │
│  ├── Mode Read (from project-mode.yaml)      │
│  ├── Topic Check (from injected context)     │
│  ├── Skill Sense (programmatic, indexed)     │
│  ├── Failure Guard (retry counter)           │
│  └── Inject structured context to system     │
└─────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────┐
│ topic-context-filter.ts (FIXED)              │
│  ├── Drop, don't placeholder                 │
│  ├── Tag-based, not keyword-only             │
│  └── Conservative defaults                   │
└─────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────┐
│ OpenCode Runtime                             │
│  ├── Skills loaded via description matching  │
│  ├── skill-index.json (NEW, authoritative)   │
│  └── Web tools available + steering rules    │
└─────────────────────────────────────────────┘
```

---

## 3. Problem-by-Problem Action Plan

### Problem 1: Installer Still Uses .ps1

**Fix**:
- [ ] **P0-TEST**: Write test asserting `catalog_query.py --upgrade` emits ONLY `install.py` commands (no `.ps1`/`.sh`)
- [ ] **P0-FIX**: Rewrite `catalog_query.py:647-753` upgrade command generation to use `install.py` exclusively
- [ ] **P0-FIX**: Update `fish-brain/SKILL.md:191-209` to remove `.ps1`/`.sh` references
- [ ] **P1-FIX**: Delete `remote-install.ps1`, `remote-install.sh` from repo
- [ ] **P1-FIX**: Convert `install.ps1`, `install.sh` to thin wrappers that call `install.py` with deprecation warning, OR delete them
- [ ] **P1-TEST**: Write test verifying all installer paths produce `install.py` commands

**Test-First Sequence**: Write test → verify it fails → fix code → verify it passes.

### Problem 2: Global/Local Boundary + Version Control

**Fix**:
- [ ] **P0-TEST**: Write test for `install.py --check-version` that compares installed vs latest and skips if current
- [ ] **P0-FIX**: Add `--check-version` flag to `install.py` that reads `installed-packs.json` version, queries GitHub latest release, and skips if equal
- [ ] **P0-FIX**: Make `--force` only required when versions match but user wants reinstall (not when versions differ — newer version auto-installs)
- [ ] **P1-DOC**: Document global vs local semantics clearly:
  - Global (`~/.config/opencode/skills/`): companion, init, petfish, toolchain — these are user-level defaults
  - Project (`.opencode/skills/`): course, deploy, ppt, etc. — project-specific
  - Global packs auto-update on version change; project packs require `--force` or version mismatch

### Problem 3: Topic Management Loses Messages (CRITICAL)

**Fix**:
- [ ] **P0-TEST**: Write test that runs filter twice on same conversation and asserts real content is NOT converted to placeholders
- [ ] **P0-TEST**: Write test asserting `removed` count matches actual content removed (not net array length)
- [ ] **P0-FIX**: **Remove placeholder insertion** (lines 419-445). Drop messages entirely instead of replacing with placeholders. If a summary is needed, add a single system-level note at the end, not per-run.
- [ ] **P0-FIX**: Add placeholder messages to `SYSTEM_PATTERNS` so existing placeholders from prior sessions are preserved (defensive, for transition period)
- [ ] **P1-FIX**: Increase `minMessages` default from 10 → 20 and `safetyWindow` from 3 → 5
- [ ] **P1-FIX**: Change `removeRatio` threshold from 0.2-0.5 to 0.15-0.35 (more conservative)
- [ ] **P1-FIX**: Register `topic-context-filter` in `opencode.json` (it's currently distributed but not enabled)
- [ ] **P2-FIX**: Consider replacing keyword matching with embedding-based relevance scoring (future)

### Problem 4: Too Proactive on Failure (Aggressive Approach Switching)

**Fix**:
- [ ] **P0-TEST**: Write test for retry guard that counts consecutive failures and blocks approach change without authorization
- [ ] **P0-FIX**: Create `companion-gateway.ts` plugin hook on `tool.execute.after` that:
  - Tracks consecutive tool failures per task
  - If 1 failure: allow retry
  - If 2 failures: inject "RETRY BEFORE WORKAROUND" directive
  - If 3+ failures OR approach change detected: inject "AUTHORIZATION REQUIRED" directive and pause
- [ ] **P0-FIX**: Remove false AGENTS.md:479 claim about response gate plugin; replace with accurate description of `companion-gateway.ts` enforcement
- [ ] **P1-FIX**: Add `permission.ask` integration for major approach changes (switching language, abandoning a tool, manual implementation of a library)

### Problem 5: Skill Dispatch Too Passive

**Fix**:
- [ ] **P0-TEST**: Write test asserting `companion-gateway.ts` runs Skill Sense on every message and injects results
- [ ] **P0-FIX**: Create `companion-gateway.ts` plugin (hook: `experimental.chat.system.transform`) that:
  - Reads `skill-index.json` (new authoritative index)
  - Matches user message against skill descriptions using keyword + fuzzy matching
  - Injects `## Skill Sense Results` block into system prompt with matched skills
  - This is PROGRAMMATIC — doesn't depend on LLM following instructions
- [ ] **P0-FIX**: Generate `skill-index.json` at install time — index all installed skills' name, description, triggers, scripts
- [ ] **P1-FIX**: Expand TRIGGERS table in catalog_query.py beyond 9 domains; auto-generate from skill-index.json
- [ ] **P1-FIX**: Wire Skill Sense results to influence OpenCode skill loading (inject matched skill names as recommendations)

### Problem 6: Insufficient Internet Use

**Fix**:
- [ ] **P0-FIX**: Add web-grounding rules to `system-prompt-rules.ts`:
  - "For library/framework/API questions: use `context7` tool BEFORE answering"
  - "For factual claims about current state: use `web-search-prime` to verify"
  - "For version-specific questions: never answer from training data; always search"
  - "Every factual claim in technical answers must cite a source URL"
- [ ] **P0-TEST**: Write test verifying web-grounding rules are present in injected system prompt
- [ ] **P1-FIX**: Add "web search recommended" signal to Skill Sense output when query matches library/framework patterns
- [ ] **P1-FIX**: Integrate Context7 MCP for documentation lookup (already available as MCP tool)

### Problem 7: Proactive Skill Discovery + Creation Bugs

**Fix**:
- [ ] **P0-FIX**: Wire `companion-gateway.ts` to call `catalog_query.py --check-failures` on previous assistant turn (programmatic, not LLM-dependent)
- [ ] **P0-FIX**: Wire `companion-gateway.ts` to detect task patterns and suggest skills from `skill-index.json`
- [ ] **P1-FIX**: Fix skill-author scaffolding bugs (audit `generate_skill.py` against current SKILL.md schema)
- [ ] **P1-FIX**: Fix quality-gate `run_gate.py` — audit all failure modes, write regression tests for each
- [ ] **P1-FIX**: Fix skill-publish flow — ensure `publish.py` generates valid market entries

### Problem 8: Real Skill Marketplace

**Fix**:
- [ ] **P1-DESIGN**: Design contributor workflow:
  1. Contributor creates skill via `/petfish create`
  2. Runs `/petfish gate` (lint + audit + metadata)
  3. Submits PR to `petfish-market` repo
  4. CI runs quality-gate automatically
  5. On merge, skill is auto-published to market index
- [ ] **P1-TEST**: Write CI workflow test (GitHub Actions) for skill submission validation
- [ ] **P1-FIX**: Create `.github/workflows/skill-submission.yml` in `petfish-market` that runs lint + audit on PRs
- [ ] **P1-FIX**: Add `petfish-market CLI` (`uv run market.py submit/validate/list`) for contributor workflow
- [ ] **P1-FIX**: Add per-skill versioning in pack-manifest.json schema
- [ ] **P2-FIX**: Add marketplace UI (static site generated from market index)

### Problem 9: Companion Vision Realignment

**Diagnosis**: PEtFiSh's vision ("always present companion") is correct but implementation is far behind competitors:
- WorkBuddy: multi-agent, end-to-end task completion, IM integration
- Cursor: Plan Mode, agent harness, marketplace
- Cline: open-source, Plan/Act, MCP marketplace
- Anthropic Skills: progressive disclosure, open standard

**Strategic Actions**:
- [ ] **P1-DESIGN**: Adopt Agent Skills open standard (`agentskills.io`) for cross-platform compatibility
- [ ] **P1-DESIGN**: Implement progressive disclosure (metadata → instructions → resources) properly
- [ ] **P2-DESIGN**: Design multi-agent orchestration (companion delegates to specialist skills, not just routes)
- [ ] **P2-DESIGN**: Design "companion memory" — persistent task context across sessions
- [ ] **P2-DESIGN**: Design proactive monitoring — companion watches for patterns and suggests actions

### Problem 10: Test-First Development (Methodology)

**Rule**: For every fix in this plan, the sequence is:
1. Write failing test that describes desired behavior
2. Verify test fails
3. Implement minimum code to pass test
4. Verify test passes
5. Run full test suite
6. Only then mark complete

**Test Infrastructure**:
- [ ] **P0-FIX**: Ensure `pytest` test suite covers all plugin behaviors
- [ ] **P0-FIX**: Add TypeScript tests for all `.ts` plugins (vitest or similar)
- [ ] **P0-FIX**: Add integration tests that simulate full conversation flows (message in → filtered output)

### Problem 11: Additional Items

From the audit findings:
- [ ] **P1-FIX**: Enable or delete `fish-trail-compaction.ts` (currently distributed but unregistered)
- [ ] **P1-FIX**: Align all 4 installers or delete legacy ones (stop the "sync" burden)
- [ ] **P1-FIX**: Run 9-touchpoint verification for recent `de-ai-detector` skill
- [ ] **P1-FIX**: Verify `scripts/pre_release_check.py` exists and is wired into CI
- [ ] **P2-FIX**: Add `skill-usage-tracker` data to Skill Sense (suggest frequently-used skills first)
- [ ] **P2-FIX**: Add "companion health check" — periodic self-audit of gateway enforcement

---

## 4. Implementation Phases

### Phase 1: Critical Fixes (P0) — Data Loss + False Claims

**Goal**: Stop losing data and stop lying about enforcement.

| Item | Test | Fix |
|---|---|---|
| topic-context-filter placeholder bug | Test: no placeholder accumulation | Remove placeholder insertion |
| catalog_query deprecated commands | Test: upgrade emits install.py only | Rewrite upgrade command |
| AGENTS.md false response gate claim | N/A | Correct the documentation |
| companion-gateway.ts basic plugin | Test: Skill Sense runs programmatically | Create plugin |

**Estimated effort**: 3-5 focused sessions.

### Phase 2: Enforcement Architecture (P0-P1)

**Goal**: Move critical behaviors from prompt to code.

| Item | Test | Fix |
|---|---|---|
| companion-gateway.ts full | Test: all 6 steps have programmatic backing | Complete implementation |
| Retry guard | Test: 3 failures triggers authorization | tool.execute.after hook |
| skill-index.json | Test: index matches all installed skills | Generate at install time |
| Web-grounding rules | Test: rules present in system prompt | system-prompt-rules.ts update |
| Installer unification | Test: only install.py paths | Delete legacy installers |

**Estimated effort**: 5-8 focused sessions.

### Phase 3: Marketplace + Skill Lifecycle (P1)

**Goal**: Real contributor marketplace.

| Item | Test | Fix |
|---|---|---|
| petfish-market CI | Test: PR triggers validation | GitHub Actions |
| market CLI | Test: submit/validate/list work | market.py |
| Per-skill versioning | Test: version in manifest | Schema update |
| skill-author/gate/publish fixes | Test: each step produces valid output | Bug fixes |

**Estimated effort**: 5-8 focused sessions.

### Phase 4: Vision Realignment (P2)

**Goal**: Catch up to competitors.

| Item | Approach |
|---|---|
| Agent Skills standard adoption | Align SKILL.md format with agentskills.io |
| Progressive disclosure | Three-level loading (metadata → body → resources) |
| Multi-agent orchestration | Design document → prototype |
| Companion memory | Design document → prototype |

**Estimated effort**: Ongoing.

---

## 5. Risk Assessment

| Risk | Mitigation |
|---|---|
| OpenCode plugin API lacks output hook | Use `tool.execute.after` + `permission.ask` instead; contribute upstream to OpenCode |
| topic-context-filter fix changes behavior | Test-first; gradual rollout with feature flag |
| Legacy installer deletion breaks users | Provide deprecation period (v2.0 warns, v2.1 removes) |
| Marketplace CI is complex | Start with simple lint-only CI; add security audit later |
| companion-gateway.ts is large change | Phase it in: basic Skill Sense first, full gateway later |

---

## 6. Anti-Sycophancy Check

I applied the calibration framework to this plan:

**Rubric**: A good plan must (1) correctly identify root causes, not symptoms; (2) propose feasible solutions within OpenCode's technical constraints; (3) prioritize by impact; (4) be testable.

**Counter-argument considered**: Is building `companion-gateway.ts` too ambitious given the OpenCode API limitations? **Assessment**: The API provides `experimental.chat.system.transform` and `tool.execute.after` — sufficient for input-side enforcement. Output-side enforcement (response gate) is genuinely blocked by API limitations; the plan acknowledges this and proposes input-side mitigation instead of pretending output-side works.

**Confidence**: HIGH for Phase 1 (critical fixes are well-understood bug fixes). MEDIUM for Phase 2 (plugin architecture requires testing against real OpenCode runtime). MEDIUM for Phase 3 (marketplace design needs user input on contributor model).

---

## 7. What I Need From You

Before implementation, I need confirmation on:

1. **Legacy installer fate**: Delete entirely, or keep as thin wrappers during deprecation period?
2. **topic-context-filter approach**: Drop messages entirely (cleaner), or keep conservative filtering with bug fix (less disruptive)?
3. **Marketplace model**: GitHub PR-based (like this plan proposes), or separate web application?
4. **companion-gateway.ts scope**: Full 6-step programmatic enforcement, or just Skill Sense + Retry Guard first?
5. **Agent Skills standard**: Adopt agentskills.io format now, or keep current SKILL.md format?
6. **Priority**: All phases sequential, or specific problems first?

---

## Appendix A: Evidence Index

| Finding | Source File | Lines |
|---|---|---|
| Gateway is prompt-only | `opencode.json` | plugin array |
| Response gate is fictional | `AGENTS.md` | 479 |
| topic-context-filter unregistered | `opencode.json` | plugin array |
| Placeholder accumulation bug | `.opencode/plugin/topic-context-filter.ts` | 419-445 |
| catalog_query deprecated commands | `catalog_query.py` | 647-753 |
| Only 4 local catalog items | `marketplace_search.py` | LOCAL_CATALOG |
| No version comparison in installer | `install.py` | (absent) |
| TRIGGERS table only 9 domains | `catalog_query.py` | 35-241 |
| Tier 2 not implemented in code | `step2-skill-sense.contract.json` | non_goals |
| petfish-market is static JSON | `petfish-market/` | (structure) |

## Appendix B: Audit Task Sessions

| Task ID | Session ID | Domain |
|---|---|---|
| bg_7e9a9915 | ses_04a79d1ecffe5fxOEJz7Eq9Lka | Installer/Upgrade |
| bg_419bd528 | ses_04a79a167ffeBO3wOcxcFmS0r8 | Skill Dispatch |
| bg_53531ee2 | ses_04a765a1cffe0VEgyMPrQGHQ60 | Gateway Enforcement |
| bg_cbbc75b4 | ses_04a79bb2effe8cm02fF34Uw77p | Topic Management |
| bg_0a055d41 | ses_04a74110bffe6VfL6xYqn9Dmq | Competitive Analysis |
| bg_2d62dc3f | ses_04a798dd7ffejIq6Ty8iI6JPqb | Skill Pipeline |
| bg_676fac3e | ses_04a6f5a9affeeyWbHCO1TPlz6e | Web-Grounding |
