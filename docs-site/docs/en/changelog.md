# Changelog

Full release notes are available on [GitHub Releases](https://github.com/kylecui/petfish.ai/releases).

> Note: this changelog is not exhaustive. Older releases, including the v1.x and v2.x lines, are covered by the README Version History and GitHub Releases.

---

## v3.4 — Market + Gateway Hardening

### v3.4.10

Repository alignment. The topic (fish-trail) plugins in `lib/plugin/` and `.opencode/plugin/` were synced to the pack copies, closing a delivery gap: since 6f7223c only the pack copies carried the cache-first context-injection rewrite and the three `topic-context-filter` fixes (parallel topic reads, single-topic guard correction, archive-failure abort), so installs never received them. Removed two dead artifacts aimed at the installers deleted in v3.0 (`scripts/check_installer_parity.py`, `tests/test_migration_e2e.py`); the latter is replaced by `tests/test_installer_migration.py`, which exercises `install.py`'s v0.9 migration directly. Fixed `verify_install.py`, which expected the shelved `fish-trail-compaction.ts` and required 4 plugin registrations, so `/petfish verify` failed on every install. Corrected stale installer commands and package claims across the docs site, pack READMEs, and website; filled the v2.x and v3.x gaps in the README version history and both changelogs. `pre_release_check.py` now baselines pack version drift on the highest released tag instead of `git describe`, which resolved to a stale tag on `dev`. Packs: fish-trail 1.4.0, petfish-companion-skill 1.9.3, research-skill-pack 1.0.2, doc-reader-skill 1.0.1.

### v3.4.9

fish-trail topic plugins (context injection and message filtering) are now opt-in and scoped to the `context` pack, registered with `"enabled": false`; previously they were default-on for any L1 pack and could not be disabled on OpenCode v1.18.3. The topic-aware compaction plugin was shelved after a measured null result (p=0.928). Also fixed a pre-existing syntax error in the pack copy of `system-prompt-context-inject.ts` and corrected public copy that still advertised the shipped compaction plugin. `fish-trail` 1.2.0 → 1.3.0.

### v3.4.8

P0 fix for a companion-gateway contract violation: `output.system` is a shared string[] that plugins may only `push` to, but the gateway used `+=`, poisoning every later plugin's `push` call and silently discarding its own injected content since release. One-line fix (`output.system.push()`) applied across 3 copies, plus a 7th permanent release gate that statically scans all pack plugins for `output` field rebinding. Companion 1.9.2.

### v3.4.7

Integrated skills.sh and ClawHub as first-class `fish-market` sources (13 total). skills.sh uses the official CLI search endpoint (`/api/search`); ClawHub is the OpenClaw registry (10.7K+ skills, documented `/v1/search`, 3000/min unauthenticated, includes Chinese skills). Testing hit a Chinese Gantt-chart generator via ClawHub and four dedicated skills via skills.sh. Companion 1.9.1.

### v3.4.6

MCP Official Registry dedupe now keys on plain `name`, because multiple remote entries for the same server share a display name.

### v3.4.5

MCP Official Registry results are deduplicated by `name`+`url`, since its weak `q` filter returned duplicate entries.

### v3.4.4

Reworked `/petfish load` discovery into a marketplaces-first ladder after three root causes pushed it into minute-long GitHub mining: 4 of 8 search sources had been dead since launch (an `urllib.request.quote` AttributeError silently swallowed per-source), Chinese queries against English indexes returned zero results with no retry hint, and there was no enforced "marketplace before mining" step. Added ClaudSkills (69K+ SKILL.md, Chinese-capable), PulseMCP, and the official MCP Registry; Chinese zero-result queries now retry in English. Companion 1.9.0 / toolchain 0.3.1.

### v3.4.3

Upgrade flow rewritten natural-language-first: the one-liner is the default entry and the agent runs all commands, so users stay in chat. Step 8's closing report now includes an install health matrix, current capabilities, per-platform restart guidance, and a post-restart conversational example.

### v3.4.2

Added `/petfish verify`, a one-command visual verification built on `verify_install.py`: a 10-item PASS/FAIL checklist (plugins, registration, MCP, vault self-test, gateway markers, L1 rule repair, index quality, version comparison, commands, course capability) with per-item remediation and a gate-compatible exit code. Un-upgraded projects can run it from the raw master URL. Companion 1.8.0.

### v3.4.1

Fixed `install.py` writing a legacy minimal `skill-index.json`, which disabled gateway domain matching in user projects after v3.4.0. The installer now emits `domains` (from the shipped `catalog_query.py` single source), per-skill pack attribution, and best-effort market `available_packs`. Verified live at 110 skills / 23 domains / 107 attributed / 15 market packs.

### v3.4.0

Completed all remaining phases of dynamic skill loading (P2+P3) and the courseware upgrade (P1+P2+P3). Skill loading gained gap-aware discovery, `/petfish load <name|keyword> [--install]`, semantic repo mining with golden-repo benchmarks, market-side trigger derivation, and vault usage tracking. Courseware gained a pedagogy reference layer plus `course-assessment-design`, an LLM-as-judge evals harness with CI gate, three offline teaching artifacts, and `course-delivery-review`. Companion 1.7.0 / toolchain 0.3.0 / course 1.5.0.

## v3.3 — Dynamic Skill Loading + Courseware

### v3.3.0

First milestone of dynamic skill loading (P1) and the courseware upgrade (P0). The new skill-vault MCP server delivers skill content as tool return values to bypass per-session skill discovery caching, exposing `vault_index`, `vault_fetch`, `vault_stage`, and `vault_install`; the Gateway injects a top-3 discovery block only when a capability gap has uninstalled candidates. Courseware P0 added machine-checked outline constraints, dual confirmation gates, and an authoring completion checklist. Companion 1.5.0 → 1.6.0 / course 1.3.2 → 1.4.0.

## v3.2 — Skill Machinery Foundation + Installer Hardening

### v3.2.1

Skill machinery foundation fixes (F1-F6): single-source triggers (`skill-index.json` gains a `domains` map, the gateway reads the index instead of a hardcoded table, and `gateway_classifiers.py` imports the catalog directly), `--skill NAME` granular install, a marketplace index `packs`/`skills` dual-key fix, project-aware `suggest` ranking, doc alignment, and a regression fix for calibrate eval phrases. Companion 1.5.0 / toolchain 0.2.0 / init 1.2.1. Pre-release gate 6/6 PASS.

### v3.2.0

Fixed a systematic upgrade bug where `L1_PACK_MAP` mapped companion and toolchain to the same rules file, so `--pack all` (alphabetical) let toolchain overwrite companion's Gateway Trace rules on every upgrade; the L1 mapping was split and the stale pack copy removed. Added release gate item 6, requiring a pack-manifest version bump when pack content changes versus the latest tag, which immediately caught two existing drifts. Extended the upgrade doc with Step 3.5 delivery verification. Companion 1.3.0 → 1.4.0 / fish-trail 1.1.0 → 1.2.0.

## v3.1 — Performance & Cache Architecture

### v3.1.0

Multi-agent orchestration (Phases 0-5): task() spike validated (1.43x parallel speedup), skill I/O contracts (3 pilot skills), orchestration hints in companion-gateway, dispatch tracking, result aggregation with conflict detection, autonomy levels (suggest/delegate/auto). Documentation/website updated. Council-thinking references trimmed.

## v3.0 — Companion Overhaul

### v3.0.0

Programmatic companion-gateway.ts (6-step enforcement via TypeScript plugin). topic-context-filter fixes (placeholder bug, effective topic detection, per-topic message archiving). Legacy installers deleted (install.py sole entry). skill-index.json (100 skills). Market CLI. Web-grounding rules. 13/13 registry consolidated to monorepo. 102/102 agentskills.io compliant. 2 new packs: drawio-radar-chart, typst-pdf-builder.

## v2.2 — Council Thinking + Pack Rename

### v2.2.0

Pack rename `anti-sycophancy-calibration-pack` → `judgment-calibration-pack`; added `council-thinking` skill (5+1 multi-perspective adversarial reasoning); pack now contains 2 skills (fish-calibrate + council-thinking); alias `calibrate` unchanged; `legacy_names` preserves upgrade compatibility.

## v1.9 — Testing Team Issue Resolution + Delivery Pipeline Fix

## v0.11 — Companion Gateway Enhancement: Proactive Intelligence

### v0.11.7

Documentation catchup — companion-gateway docs (EN+ZH), README, website updated to reflect 6-step Gateway flow; Token Cost Engineering blog post published.

### v0.11.6

Companion Gateway 6-step implementation complete — all six steps (Mode Read, Topic Check, Failure Signal Detection, Skill Sense, Anti-Sycophancy Check, Proceed) integrated and operational.

### v0.11.5

Rigor threshold refinement — only Momus plan+review for 3+ step or 3+ file tasks; simpler tasks get assumption-stating and post-verification without formal plan files.

### v0.11.4

Anti-Sycophancy Check (Step 2.5) — rubric-first evaluation, mandatory counter-argument search before agreeing; proactivity level linked to Rigor mode (off=explicit only, on=implicit+assertions).

### v0.11.3

Rigor Mode — `rigor: true` in project-mode.yaml adds plan-then-review discipline: formal plan files for complex tasks, Momus review before implementation, explicit assumption-stating. Forced on when `depth: thorough`.

### v0.11.2

Project Mode (Step 0) — `depth` (urgent/balanced/thorough) and `rigor` (on/off) axes in `.opencode/project-mode.yaml`; session-only verbal overrides without file writes.

### v0.11.1

Failure Signal Detection (Step 1.5) — scan previous assistant turn for known failure patterns (PDF/deploy/test/research/context), recommend matching pack if uninstalled. Implemented via `catalog_query.py --check-failures`.

### v0.11.0

Gateway expansion from 3 steps to 6 steps — add Mode Read, Failure Signal Detection, and Anti-Sycophancy Check to the always-on Companion Gateway flow.

---

## v0.10 — Research Pack Expansion: 7 Domains

### v0.10.10

Auto-update capability — `check_installed.py --check-updates` queries GitHub latest release and compares installed pack versions; `catalog_query.py --upgrade` shows OS-appropriate upgrade command; Companion Gateway now checks for updates on session start; `/petfish upgrade` command added. Also fixes missing `research` alias in `KNOWN_PACKS`.

### v0.10.9

Systemic trigger keyword coverage fix — align all skill descriptions with body trigger words across all 11 packs (~74 skills updated); add `check_trigger_coverage()` lint rule to `lint_skill.py`; integrate trigger-coverage into `run_gate.py` decision logic; add Description-Body alignment discipline to root AGENTS.md; expand research triggers in `catalog_query.py`. Closes #91, #89, #88.

### v0.10.7–v0.10.8

Fix research pack integration — complete 9-touchpoint checklist for research pack (remote installer, companion catalog, README, docs, website). Crystallize "one audit, one fix" development lesson.

### v0.10.6

Fix 4 backlog issues — replace duplicate QA script with `qa_scan.py` (#80), add `--target` to suggest for fixture isolation (#73), document JSONL/Markdown design and improve research pack UX (#79), add hybrid semantic+keyword trigger scoring with `--semantic` flag (#77). Closes #80, #73, #79, #77.

### v0.10.5

Adapter skills — 4 lightweight domain adapters (travel, conference, training, content-selection) that enhance main research chains with domain-specific fields and checklists. Pack now has 50 skills.

### v0.10.4

Risk-procurement and experience-event research domains — 11 new skills. Pack now has 46 skills.

### v0.10.3

Learning and decision research domains — 7 new skills. Pack now has 35 skills.

### v0.10.2

Planning research domain — 6 new skills. Pack now has 28 skills.

### v0.10.1

SKILL_builder eradication — 10 stale refs fixed across 6 files; `catalog_query.py` fallback now returns actual counts. Closes #87, #86.

### v0.10.0

Product research domain — 5 new skills (user-research, competitor-analysis, opportunity-mapper, validation-planner, decision-brief). Pack now has 22 skills.

---

## v0.9 — Research Skill Pack

### v0.9.6

Fix smoke fixture missing `adr/` directory (#85); fix trigger eval runner to glob all `evals/trigger/*.json` (#84).

### v0.9.5

Fix SKILL.md schema mismatches in 4 research skills (#83, #82, #78); fix `repo_inventory.py` node_modules inclusion (#81); fix all 4 installers writing zeroed skill/command/agent counts (#71). Closes 5 issues.

### v0.9.4

Research pack scientific domain — 7 new skills (citation-auditor, literature-review, gap-finder, methodology-designer, experiment-planner, paper-writer, review-rebuttal). Pack now has 17 skills.

### v0.9.3

Research pack installable — pack-manifest, installer registration, companion catalog integration, README and CHANGELOG updates.

### v0.9.2

Research pack QA infrastructure — seeded fixtures, E2E smoke tests (15 pytest), trigger-eval harness, local smoke runner, CI gates. Closes #74, #75, #76.

### v0.9.1

Research alias added to all 4 installers and companion catalog.

### v0.9.0

Research skill pack MVP — 10 core skills, 7 JSON schemas, 9 Python scripts, pack infrastructure.

---

## v0.8 — Multi-Platform & Agent Discipline

### v0.8.1

Universal agent principles (cross-repo protection, network retry); complete ops AGENTS.md template; code profile experience crystallization; deployment-executor references for private repo access. Closes #66, #67, #68, #69.

### v0.8.0

Multi-platform instruction file generation (#63) — `detect_all_platforms()`, content condensation for token-limited platforms, Claude Code hook scripts, uv-first Python policy enforced across project.

---

## v0.7 — Stability & Pack Versioning

### v0.7.2

Fix #57 root cause (`grep -qF` replacing `echo | grep`); fix #65 (8 missing QA bilingual terms in `topic_detector.py`).

### v0.7.1

Fix #57 legacy name awareness in `merge_agents_md`; bump fish-trail and petfish-companion-skill to 1.0.0 (#64); fix corrupted AGENTS.md markers; update all 4 installer scripts.

---

## v0.6 — Companion Narrative

### v0.6.4

Bilingual website and docs; archive outdated v0.2 docs.

### v0.6.3

Companion narrative rebrand; fix #57 `--force` upgrade bug.

### v0.6.2

Fix companion pack skill sensing, installer dedup, catalog fallback, and universal platform detection.

### v0.6.1

Fix `topic_graph` persistence, schema alignment, and intent-aware skill sensing.

### v0.6.0

Companion Gateway with always-on topic check, 3-tier skill sense, and debug mode.

---

## v0.5 — Fish Trail and Repo Rename

### v0.5.4

Fix missing `version` field in `topic_graph` and stale detection in `topic_report`.

### v0.5.3

Add the agent upgrade guide and web upgrade prompt.

### v0.5.2

Add the v0.4.x → v0.5.x upgrade guide.

### v0.5.1

Pre-release documentation and test suite updates.

### v0.5.0

Rename `SKILL_builder` to `petfish.ai`; rename context-router to `fish-trail`; add 31 MCP tools, installer aliases, state directory migration, and topic routing scripts.

---

## v0.4 — Context Router and Session Management

### v0.4.10–v0.4.12

Add topic-aware session management with 10 new MCP tools, cross-session resume, boundary policy, activity query, agent attribution, and topic recommendations. Fix install guidance, trigger extraction scope, and `deploy_dirs` false positives.

### v0.4.5–v0.4.9

Fix MCP schema issues, platform-specific restart hints, CJK detection, and trigger evaluation.

### v0.4.0

Add the context router pack with topic detection, contamination scoring, context isolation, and 18 MCP tools.

---

## v0.3 — Quality and Platform Hardening

- Anti-sycophancy calibration pack.
- Style v4 AI slop detection.
- Release discipline with auto-resolved latest release tags.
- UTF-8 fixes for PowerShell.
- Comma-separated multi-pack install.

---

## v0.2 — Skill Lifecycle Management

- **Phase 1**: 8-platform adapter and companion skill with sensing, equip, and governance capabilities.
- **Phase 2**: Marketplace search, skill authoring, and quality linting.
- **Phase 3**: Repo mining, security audit, and publish quality gate.
- **Phase 4**: Description optimization, trigger evaluation, and usage tracking.

---

## v0.1 — Skill Installer

- Multi-pack installer with remote install support.
- 7 skill packs: `course`, `deploy`, `testdocs`, `petfish`, `ppt`, `init`, and `companion`.
