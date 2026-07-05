# Changelog

Full release notes are available on [GitHub Releases](https://github.com/kylecui/petfish.ai/releases).

---

## v1.9 — Testing Team Issue Resolution + Delivery Pipeline Fix

## v2.2 — Council Thinking + Pack Rename

### v2.2.0

Pack rename `anti-sycophancy-calibration-pack` → `judgment-calibration-pack`; added `council-thinking` skill (5+1 multi-perspective adversarial reasoning); pack now contains 2 skills (fish-calibrate + council-thinking); alias `calibrate` unchanged; `legacy_names` preserves upgrade compatibility.

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
