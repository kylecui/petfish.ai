[中文版](docs/zh/README.md)

<p align="center">
  <img src="assets/petfish-logo.png" alt="胖鱼 PEtFiSh logo" width="360" />
</p>

# PEtFiSh
<p align="center">
  <img src="assets/petfish-icon-256.png" alt="胖鱼 PEtFiSh icon" width="128" />
</p>
**Your AI Companion**
From first commit to final delivery, PEtFiSh is always there.
```text
><(((^>  PEtFiSh v0.8

Always Present   Companion Gateway in every interaction
Guarding         Sense gaps, guard context, block pollution
Verified Trust   Lint + audit + red lines = earned trust
No Compromise    No sycophancy, standards don't bend

/petfish — your always-on companion
```

Not a toolbox. A companion. Tools get called. PEtFiSh is always there.

---

## Quick Start
1. Install `init` and `companion`.
2. Run `/initproject` in your project.
3. Pick a profile; PEtFiSh installs matching packs.
4. Start working; Companion Gateway is now active.
**Recommended one-line install**
```text
Install PEtFiSh by following: https://raw.githubusercontent.com/kylecui/petfish.ai/master/docs/agent-install.md
```

**Windows PowerShell**
```powershell
& ([scriptblock]::Create((irm https://raw.githubusercontent.com/kylecui/petfish.ai/master/remote-install.ps1))) -Pack "init,companion" -Detect
```

**macOS / Linux / WSL**
```bash
curl -fsSL https://raw.githubusercontent.com/kylecui/petfish.ai/master/remote-install.sh | bash -s -- --pack init,companion --detect
```

---

## Companion Gateway
Companion Gateway runs before every message:
1. **Topic Check** — detect drift and assess context risk.
2. **Skill Sense** — detect capability gaps before they hurt.
3. **Proceed** — continue with the right context in place.
See [docs/companion-gateway.md](docs/companion-gateway.md) for the full flow.

---

## `/petfish` Commands
| Command | Purpose |
|---|---|
| `/petfish` | Show installed pack and skill status |
| `/petfish catalog` | Browse available packs and skills |
| `/petfish suggest` | Recommend packs from project structure |
| `/petfish install <alias>` | Get the install command for a pack |
| `/petfish detect` | Detect the current AI platform |
| `/petfish search <keyword>` | Search skills and MCP servers across sources |
| `/petfish mine <repo>` | Mine a repository for skill candidates |
| `/petfish create <name>` | Scaffold a new skill |
| `/petfish lint [path]` | Run format and quality checks |
| `/petfish audit <path>` | Run a security audit |
| `/petfish gate <path>` | Run the full publish gate |
| `/petfish optimize <path>` | Improve skill descriptions and triggers |
| `/petfish eval <path>` | Test trigger accuracy |
| `/petfish stats` | View usage analytics |

---

## 10 Built-in Skills
```text
Skill Lifecycle Pipeline

mine → author → lint → audit → gate → optimize → eval

+ marketplace-connector
+ skill-usage-tracker
+ petfish-companion
```

| Skill | Purpose | Script |
|---|---|---|
| `petfish-companion` | Orchestration, sensing, and routing | `catalog_query.py`, `check_installed.py`, `detect_platform.py` |
| `marketplace-connector` | Search across external sources | `marketplace_search.py` |
| `skill-author` | Scaffold new skills | `generate_skill.py` |
| `skill-lint` | Format and quality checks | `lint_skill.py` |
| `repo-skill-miner` | Mine repositories for skill candidates | `mine_repo.py` |
| `skill-security-auditor` | Static security analysis | `audit_skill.py` |
| `quality-gate` | Publish decision pipeline | `run_gate.py` |
| `skill-description-optimizer` | Improve descriptions and triggers | `optimize_description.py` |
| `skill-trigger-evaluator` | Measure trigger precision and recall | `evaluate_triggers.py` |
| `skill-usage-tracker` | Usage analytics and feedback | `track_usage.py` |

---

## 11 Skill Packs
| Alias | Purpose | Scale |
|---|---|---|
| `init` | Project initializer and `/initproject` wizard | Global default |
| `companion` | Companion Gateway, `/petfish`, and 10 built-in skills | Global default |
| `course` | Course outline, content, labs, QA, and QC workflows | Project |
| `testdocs` | Test case and usage documentation workflows | Project |
| `deploy` | Deployment, CI/CD, health check, rollback, and ops workflows | Project |
| `petfish` | Writing style and rewrite guidance | Project |
| `ppt` | Slide and presentation workflows | Project |
| `calibrate` | Anti-sycophancy review and decision calibration | Project |
| `context` | Topic governance, context isolation, and contamination scoring | Project |
| `trust` | Skill trust governance and policy checks | Project |
| `research` | Research workbench — evidence-backed scientific, product, and planning research | Project |

## Profile → Auto-Install Mapping
| Profile | Auto-installed Packs |
|---|---|
| `minimal` | `petfish` |
| `course` | `course`, `petfish` |
| `code` | `deploy`, `petfish`, `testdocs` |
| `ops` | `deploy`, `petfish` |
| `security` | `deploy`, `petfish`, `testdocs` |
| `writing` | `petfish`, `ppt` |
| `skills-package` | `petfish`, `testdocs` |
| `comprehensive` | `course`, `deploy`, `petfish`, `ppt`, `testdocs`, `trust`, `context`, `research` |

---

## Platform Support
| Platform | `--platform` | Skills Directory | Instructions File | Auto-detect Markers |
|---|---|---|---|---|
| OpenCode | `opencode` | `.opencode/skills/` | `AGENTS.md` | `.opencode/`, `opencode.json` |
| Claude Code | `claude` | `.claude/skills/` | `CLAUDE.md` | `.claude/`, `CLAUDE.md` |
| Codex | `codex` | `.agents/skills/` | `AGENTS.md` | `.codex/` |
| Cursor | `cursor` | `.cursor/skills/` | `.cursor/rules/*.mdc` | `.cursor/`, `.cursorrules` |
| GitHub Copilot | `copilot` | `.github/skills/` | `.github/copilot-instructions.md` | `.github/copilot-instructions.md` |
| Windsurf | `windsurf` | `.windsurf/skills/` | `.windsurfrules` | `.windsurf/`, `.windsurfrules` |
| Antigravity | `antigravity` | `.agents/skills/` | `AGENTS.md` + `GEMINI.md` | `.agents/`, `GEMINI.md` |
| Universal | `universal` | `.agents/skills/` | `AGENTS.md` | Fallback |

---

## Install Commands
### Remote Install
```powershell
& ([scriptblock]::Create((irm https://raw.githubusercontent.com/kylecui/petfish.ai/master/remote-install.ps1))) -Pack <alias> [-Target .] [-Platform opencode] [-Detect] [-Force] [-Global]
```

```bash
curl -fsSL https://raw.githubusercontent.com/kylecui/petfish.ai/master/remote-install.sh | bash -s -- --pack <alias> [--target .] [--platform opencode] [--detect] [--force] [--global]
```

### Local Install
```powershell
.\install.ps1 -Pack <alias> [-Target path] [-Platform opencode|claude|codex|cursor|copilot|windsurf|antigravity|all|primary|ide|cli] [-Detect] [-Force] [-Global]
.\install.ps1 -List
```

```bash
./install.sh --pack <alias> [--target path] [--platform <platform|group>] [--detect] [--force] [--global]
./install.sh --list
```

### Private Repo Example
```bash
curl -fsSL -H "Authorization: token $GITHUB_TOKEN" \
  https://raw.githubusercontent.com/kylecui/petfish.ai/master/remote-install.sh \
  | GITHUB_TOKEN=$GITHUB_TOKEN bash -s -- --pack course
```

```powershell
& ([scriptblock]::Create((irm https://raw.githubusercontent.com/kylecui/petfish.ai/master/remote-install.ps1))) -Pack course -GitHubToken $env:GITHUB_TOKEN
```

---

## Upgrade
Re-run the install command with `--force` to upgrade.
```text
Upgrade PEtFiSh by following: https://raw.githubusercontent.com/kylecui/petfish.ai/master/docs/agent-upgrade.md
```

```powershell
& ([scriptblock]::Create((irm https://raw.githubusercontent.com/kylecui/petfish.ai/master/remote-install.ps1))) -Pack all -Force
```

```bash
curl -fsSL https://raw.githubusercontent.com/kylecui/petfish.ai/master/remote-install.sh | bash -s -- --pack all --force
```

Without `--force`, current packs are skipped, available updates are reported, and missing packs still install normally.

---

## Global vs Project Install

- **Global** (`--global`): installs skills and commands to the user-level directory. `init` and `companion` default to global.
- **Project** (default): installs to the target project's platform-specific directory with instructions merge, config merge, and registry tracking.

---

## Quality Gate Pipeline
```text
skill/
  │
  ├─ 1. Lint
  │    └─ Score ≥ 80/100
  │
  ├─ 2. Security Audit
  │    └─ Risk ≤ 0.5 and no CRITICAL
  │
  ├─ 3. Metadata Validation
  │    └─ Name, version, and description valid
  │
  └─ 4. Decision
       ├─ PASS
       ├─ CONDITIONAL
       └─ FAIL
```

```bash
uv run .opencode/skills/quality-gate/scripts/run_gate.py --path .opencode/skills/my-skill/
uv run .opencode/skills/quality-gate/scripts/run_gate.py --path .opencode/skills/ --recursive
```

---

## Prerequisites
- **`uv`** — required for all Python-based skills, MCP servers, and scripts with external dependencies. PEtFiSh uses uv as its sole Python environment manager. MCP servers are launched via `uv run`, standalone scripts use PEP 723 inline metadata or pack-level `pyproject.toml`. No `pip install` is used anywhere. The installer warns when `uv` is missing.
- `python3` — used by installers for stdlib-only JSON parsing and instructions translation (no virtual environment needed)

---

## Adding a New Pack
1. Create a directory under `packs/`.
2. Add `.opencode/` with `skills/`, `commands/`, and/or `agents/`.
3. Add `pack-manifest.json`.
4. Add `AGENTS.md` content for merge into the target instructions file.
5. Add `opencode.example.json` if OpenCode config merge is needed.
6. Register the alias in the installer scripts.

---

## Repo Structure
```text
petfish.ai/
├── packs/
│   ├── project-initializer-skill/                # init
│   ├── petfish-companion-skill/                  # companion
│   │   └── .opencode/skills/
│   │       ├── petfish-companion/                # orchestration and sensing
│   │       ├── marketplace-connector/            # external search
│   │       ├── skill-author/                     # scaffolding
│   │       ├── skill-lint/                       # quality checks
│   │       ├── repo-skill-miner/                 # repo mining
│   │       ├── skill-security-auditor/           # security audit
│   │       ├── quality-gate/                     # publish gate
│   │       ├── skill-description-optimizer/      # description tuning
│   │       ├── skill-trigger-evaluator/          # trigger testing
│   │       └── skill-usage-tracker/              # usage analytics
│   ├── opencode-course-skills-pack/              # course
│   ├── opencode-skill-pack-testcases-usage-docs/ # testdocs
│   ├── repo-deploy-ops-skill-pack/               # deploy
│   ├── petfish-style-skill/                      # petfish
│   ├── opencode-ppt-skills/                      # ppt
│   └── research-skill-pack/                      # research
├── platforms.json                                # platform registry
├── install.ps1                                   # local PowerShell installer
├── install.sh                                    # local shell installer
├── remote-install.ps1                            # remote PowerShell installer
├── remote-install.sh                             # remote shell installer
└── README.md
```

---

## Version History
### v0.10 — Research Pack Expansion: 7 Domains

- **v0.10.6**: Fix 4 backlog issues — replace duplicate QA script with qa_scan.py (#80), add `--target` to suggest for fixture isolation (#73), document JSONL/Markdown design and improve research pack UX (#79), add hybrid semantic+keyword trigger scoring with `--semantic` flag (#77). Closes #80, #73, #79, #77.
- **v0.10.5**: Adapter skills — 4 lightweight domain adapters (travel-adapter, conference-adapter, training-event-adapter, content-selection-adapter) that enhance main research chains with domain-specific fields and checklists. Trigger evals, smoke test coverage. Pack now has 50 skills.
- **v0.10.4**: Risk-procurement and experience-event research domains — 11 new skills (risk-research-brief, vendor-source-diligence, security-risk-review, compliance-check, tco-operational-risk, adoption-recommendation, experience-brief-framer, venue-destination-research, schedule-itinerary-planner, logistics-risk-planner, event-runbook-writer), trigger evals, smoke test coverage. Pack now has 46 skills.
- **v0.10.3**: Learning and decision research domains — 7 new skills (learning-goal-framer, learning-resource-discovery, learning-path-designer, decision-brief-framer, decision-criteria-builder, option-comparison-matrix, decision-recommendation), trigger evals, smoke test coverage. Pack now has 35 skills.
- **v0.10.2**: Planning research domain — 6 new skills (environment-scanner, stakeholder-analyst, scenario-planner, policy-researcher, technology-assessor, roadmap-developer), trigger evals, smoke test coverage. Pack now has 28 skills.
- **v0.10.1**: SKILL_builder eradication — 10 stale refs fixed across 6 files; catalog_query.py fallback now returns actual counts. Closes #87, #86.
- **v0.10.0**: Product research domain — 5 new skills (user-research, competitor-analysis, opportunity-mapper, validation-planner, decision-brief), trigger evals, smoke test coverage. Pack now has 22 skills.

### v0.9 — Research Skill Pack

- **v0.9.6**: Fix smoke fixture missing adr/ directory (#85); fix trigger eval runner to glob all evals/trigger/*.json (#84).
- **v0.9.5**: Fix SKILL.md schema mismatches in 4 research skills (#83, #82, #78); fix repo_inventory.py node_modules inclusion (#81); fix all 4 installers writing zeroed skill/command/agent counts (#71). Closes 5 issues.
- **v0.9.4**: Research pack scientific domain — 7 new skills (citation-auditor, literature-review, gap-finder, methodology-designer, experiment-planner, paper-writer, review-rebuttal), trigger evals, smoke test coverage. Pack now has 17 skills.
- **v0.9.3**: Research pack installable — pack-manifest, installer registration, companion catalog integration, README and CHANGELOG updates.
- **v0.9.2**: Research pack QA infrastructure — seeded fixtures, E2E smoke tests (15 pytest), trigger-eval harness, local smoke runner, CI gates. Closes #74, #75, #76.
- **v0.9.1**: Research alias added to all 4 installers and companion catalog.
- **v0.9.0**: Research skill pack MVP — 10 core skills, 7 JSON schemas, 9 Python scripts, pack infrastructure.

### v0.8 — Multi-Platform & Agent Discipline

- **v0.8.1**: Universal agent principles (cross-repo protection, network retry); complete ops AGENTS.md template (11 sections); code profile experience crystallization (Development Gotchas, Architecture Decisions); deployment-executor references for private repo access and local patch management. Closes #66, #67, #68, #69.
- **v0.8.0**: Multi-platform instruction file generation (#63) — `detect_all_platforms()`, content condensation for token-limited platforms, Claude Code hook scripts, uv-first Python policy enforced across project.

### v0.7 — Stability & Pack Versioning

- **v0.7.2**: Fix #57 root cause (`grep -qF` replacing `echo | grep`); fix #65 (8 missing QA bilingual terms in topic_detector.py).
- **v0.7.1**: Fix #57 legacy name awareness in merge_agents_md; bump fish-trail and petfish-companion-skill to 1.0.0 (#64); fix corrupted AGENTS.md markers; update all 4 installer scripts.

### v0.6 — Companion Narrative

- **v0.6.4**: Bilingual website and docs; archive outdated v0.2 docs.
- **v0.6.3**: Companion narrative rebrand; fix #57 `--force` upgrade bug.
- **v0.6.2**: Fix companion pack skill sensing, installer dedup, catalog fallback, and universal platform detection.
- **v0.6.1**: Fix `topic_graph` persistence, schema alignment, and intent-aware skill sensing.
- **v0.6.0**: Companion Gateway with always-on topic check, 3-tier skill sense, and debug mode.

### v0.5 — Fish Trail and Repo Rename

- **v0.5.4**: Fix missing `version` field in `topic_graph` and stale detection in `topic_report`.
- **v0.5.3**: Add the agent upgrade guide and web upgrade prompt.
- **v0.5.2**: Add the v0.4.x → v0.5.x upgrade guide.
- **v0.5.1**: Pre-release documentation and test suite updates.
- **v0.5.0**: Rename `SKILL_builder` to `petfish.ai`; rename the context router pack to `fish-trail`; add 31 MCP tools, installer aliases, state directory migration, and topic routing scripts.

### v0.4 — Context Router and Session Management

- **v0.4.0**: Add the context router pack with topic detection, contamination scoring, context isolation, and 18 MCP tools.
- **v0.4.5–v0.4.9**: Fix MCP schema issues, platform-specific restart hints, CJK detection, and trigger evaluation.
- **v0.4.10**: Add topic-aware session management with 10 new MCP tools, cross-session resume, boundary policy, activity query, agent attribution, and topic recommendations.
- **v0.4.11–v0.4.12**: Fix install guidance, trigger extraction scope, and `deploy_dirs` false positives.

### v0.3 — Quality and Platform Hardening

- Anti-sycophancy calibration pack.
- Style v4 AI slop detection.
- Release discipline with auto-resolved latest release tags.
- UTF-8 fixes for PowerShell.
- Comma-separated multi-pack install.

### v0.2 — Skill Lifecycle Management

- **Phase 1**: 8-platform adapter and companion skill with sensing, equip, and governance capabilities.
- **Phase 2**: Marketplace search, skill authoring, and quality linting.
- **Phase 3**: Repo mining, security audit, and publish quality gate.
- **Phase 4**: Description optimization, trigger evaluation, and usage tracking.

### v0.1 — Skill Installer

- Multi-pack installer with remote install support.
- 7 skill packs: `course`, `deploy`, `testdocs`, `petfish`, `ppt`, `init`, and `companion`.

---

## License

Apache-2.0 — see [LICENSE](LICENSE).

The names **胖鱼**, **PEtFiSh**, **petfish**, **petfish.ai**, and the PEtFiSh logo are trademarks not covered by the license. See [TRADEMARKS.md](TRADEMARKS.md).

---

PEtFiSh — your AI companion in every interaction.
