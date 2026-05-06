[中文版](docs/zh/README.md)

<p align="center">
  <img src="assets/petfish-logo.png" alt="胖鱼 PEtFiSh logo" width="360" />
</p>

# PEtFiSh
<p align="center">
  <img src="assets/petfish-icon-256.png" alt="胖鱼 PEtFiSh icon" width="128" />
</p>
**Your AI Companion**
From first commit to final delivery, PEtFiSh is there.
```text
><(((^>  PEtFiSh v0.6

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

## 10 Skill Packs
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
| `comprehensive` | `course`, `deploy`, `petfish`, `ppt`, `testdocs`, `trust`, `context` |

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
- `uv` for Python-based skills
- `python3` for platform config parsing and instructions translation
- The installer warns when `uv` is missing

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
│   └── opencode-ppt-skills/                      # ppt
├── platforms.json                                # platform registry
├── install.ps1                                   # local PowerShell installer
├── install.sh                                    # local shell installer
├── remote-install.ps1                            # remote PowerShell installer
├── remote-install.sh                             # remote shell installer
└── README.md
```

---

## Version History
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

PEtFiSh — your AI companion in every interaction.
