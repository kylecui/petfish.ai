# PEtFiSh Documentation Engineering Plan

## Goal

Build a bilingual (zh/en) documentation site for PEtFiSh covering user manuals, pack task guides, auto-generated skill reference, developer guides, and technical papers. Published via GitHub Pages with MkDocs Material. petfish.ai homepage remains; docs site becomes the canonical documentation destination linked from petfish.ai.

## Decisions (Locked)

- **SSG**: MkDocs Material (Python-native, uv-managed, first-class i18n)
- **Bilingual model**: Hybrid — independent authoring for guides (~30%), translated for reference (~70%), auto-generated for catalogs
- **Auto-generation**: Yes — build pipeline from SKILL.md frontmatter + pack-manifest.json → skill reference pages
- **Versioning**: Latest-only with version banner (no mike/multi-version)
- **Website fate**: Docs site eventually replaces website content EXCEPT homepage (index.html stays at petfish.ai)
- **Sysprompt paper**: Formalize from blog into standalone technical paper on docs site; blog stays on website only
- **URL scheme**: `/en/...` and `/zh/...` top-level language split

## Site Information Architecture

```
/                          → redirect to /en/ (or /zh/ based on locale)
/en/
  getting-started/         → What is PEtFiSh, installation, first run, profiles
  guides/
    companion-gateway/     → How the always-on gateway works
    deploy/                → Task guide: deploy a repo to your server
    research/              → Task guide: run a structured research project
    course/                → Task guide: develop a course end-to-end
    petfish-commands/       → /petfish command reference
    other-packs/            → Lighter guides for ppt, calibrate, petfish-style, testdocs, context
  reference/
    packs/                 → Auto-generated pack index (12 packs)
     skills/                → Auto-generated skill pages (96 skills)
  developer/
    skill-authoring/       → How to create a skill
    quality-gate/          → Lint, security audit, trust governance, trigger eval
    contributing/          → How to contribute to PEtFiSh
  technical/
    token-economics-compaction/   → Topic-aware compaction paper (snapshot)
    token-economics-sysprompt/    → Sysprompt optimization paper (formalized, snapshot)
    companion-gateway-design/     → Companion Gateway technical deep dive (snapshot)
  changelog/               → Release history
/zh/
  (mirrors /en/ structure, independently authored for guides, translated for reference)
```

## Phases

### Phase 0: Infrastructure (1-2 days)

**What**: Set up MkDocs Material project, GitHub Pages CI, auto-generation pipeline, URL scheme.

**Tasks**:
1. Initialize MkDocs Material project in `docs-site/` directory (separate from existing `docs/`)
2. Configure `mkdocs.yml` with i18n plugin, navigation, theme, search (with Chinese segmentation)
3. Create GitHub Actions workflow: build MkDocs on push to `dev`, deploy to GitHub Pages on push to `master`
4. Build auto-generation script `scripts/generate_skill_reference.py`:
   - Input: all `packs/*/.opencode/skills/*/SKILL.md` frontmatter + `packs/*/pack-manifest.json`
- Output: one Markdown page per skill under `docs-site/docs/en/reference/skills/` and `docs-site/docs/zh/reference/skills/`
   - Output: one Markdown page per pack under `docs-site/docs/en/reference/packs/` and `docs-site/docs/zh/reference/packs/`
   - Fields: name, description, pack membership, triggers, compatibility, related skills
5. Define URL scheme (as above) and document it in `docs-site/URL-SCHEME.md`
6. Configure petfish.ai to link to docs site (e.g., docs.petfish.ai or petfish.ai/docs/)

**Acceptance**: `mkdocs serve` renders site locally with placeholder content in both languages. Auto-gen script produces reference pages for all skills (currently 96). GitHub Actions pipeline deploys to Pages successfully.

**QA Scenarios**:
1. **Local build**: Run `uv run mkdocs serve` in `docs-site/`. Expected: site renders at localhost:8000, nav shows en/zh split, no build warnings.
2. **Auto-gen completeness**: Run `uv run python scripts/generate_skill_reference.py`. Then `ls docs-site/docs/en/reference/skills/ | Measure-Object -Line` (PowerShell) or `ls docs-site/docs/en/reference/skills/ | wc -l` (bash). Expected: count matches actual `packs/*/.opencode/skills/*/SKILL.md` file count (currently 96). Spot-check 3 random files contain name, description, pack, triggers fields.
3. **CI pipeline**: Push to `dev`, check GitHub Actions `docs` workflow. Expected: workflow completes green, artifact uploaded to Pages.
4. **i18n**: Navigate to `/zh/` in local serve. Expected: Chinese nav labels render, search returns Chinese results.

**Files touched**: `docs-site/` (new), `scripts/generate_skill_reference.py` (new), `.github/workflows/docs.yml` (new)

### Phase 1: "I can install and understand PEtFiSh" (1 week)

**What**: Core onboarding content — a new user goes from zero to installed-and-running using only the docs site.

**Tasks**:
1. Write `getting-started/index.md` (en) — What is PEtFiSh, value proposition, who it's for
   - Source: extract from README.md + website pitch.html + whitepaper
2. Write `getting-started/installation.md` (en) — Step-by-step for all platforms
   - Source: consolidate from `docs/agent-install.md` + `docs/agent-upgrade.md`
   - Cover: one-liner, profiles, pack selection, uv setup, troubleshooting
3. Write `getting-started/first-run.md` (en) — First interaction, /petfish status, understanding companion gateway
4. Write `guides/companion-gateway/index.md` (en) — Reformat existing `docs/companion-gateway.md`
5. Write `guides/petfish-commands/index.md` (en) — /petfish command reference from companion skill
6. Run auto-gen script to populate all reference pages (en + zh)
7. Write zh versions of getting-started (independently authored, not translated)
8. QA pass: each page checked against petfish-style criteria

**Acceptance**: A test reader (or simulated) can install PEtFiSh on macOS/Linux/Windows using only the docs site. No README.md fallback needed. All auto-generated reference pages render correctly.

**QA Scenarios**:
1. **Install walkthrough**: Open `getting-started/installation.md` in browser. Follow steps on a clean machine (or verify commands are copy-pasteable). Expected: one-liner, profile selection, and verification steps are all present and match current `remote-install.sh`/`remote-install.ps1` behavior.
2. **No dead links**: Run `uv run mkdocs build --strict` in `docs-site/`. Expected: zero warnings about broken links or missing pages.
3. **Reference pages**: Navigate to 5 random skill reference pages. Expected: each shows name, description, pack, triggers, and links to pack page. No "TODO" or placeholder text.
4. **zh getting-started**: Open zh getting-started pages. Expected: independently written (not machine-translated), covers same install steps, culturally appropriate examples.

**Files touched**: `docs-site/docs/en/getting-started/` (new), `docs-site/docs/en/guides/companion-gateway/` (new), `docs-site/docs/en/guides/petfish-commands/` (new), `docs-site/docs/zh/getting-started/` (new)

### Phase 2: "I can use the key packs" (2 weeks)

**What**: Task-oriented guides for the 3 highest-value packs (deploy, research, course).

**Tasks**:
1. Write deploy task guide (en): "Deploy a GitHub repo to your server"
   - Covers full chain: repo-runtime-discovery → target-host-readiness → deployment-executor → deployment-verifier → service-operations
   - Include: real example walkthrough, common failure modes, rollback
2. Write research task guide (en): "Run a structured research project"
   - Covers: research-router → brief → sources → notes → evidence → synthesis → report → review
   - Include: example research question, what each step produces, when to skip steps
3. Write course task guide (en): "Develop a course end-to-end"
   - Covers: orchestrator → outline → content → labs → learner/instructor materials → QA → QC
   - Include: directory structure, quality gates, common workflows
4. Write lighter guides for remaining packs (en): ppt, calibrate, petfish-style, testdocs, context
   - 1-2 pages each covering: what it does, when to use it, quick example
5. Write zh versions of deploy and research guides (independently authored)
6. Write zh versions of remaining pack guides (translated with localization)
7. QA pass on all guide pages

**Acceptance**: A user can complete a deploy workflow and a research workflow using only the docs site task guides. Each guide tested against an actual use case.

**QA Scenarios**:
1. **Deploy guide smoke test**: Follow deploy task guide from start. Expected: guide mentions all 5 skills in chain (repo-runtime-discovery → target-host-readiness → deployment-executor → deployment-verifier → service-operations), includes at least 1 concrete example, covers rollback.
2. **Research guide smoke test**: Follow research task guide. Expected: guide covers router → brief → sources → notes → evidence → synthesis → report → review chain, shows example research question and what each step produces.
3. **Lighter pack guides**: Check each of ppt, calibrate, petfish-style, testdocs, context guides. Expected: each has "what it does", "when to use", and at least 1 quick example. No guide exceeds 3 pages.
4. **Build clean**: `uv run mkdocs build --strict`. Expected: zero warnings.

**Files touched**: `docs-site/docs/en/guides/deploy/` (new), `docs-site/docs/en/guides/research/` (new), `docs-site/docs/en/guides/course/` (new), `docs-site/docs/en/guides/other-packs/` (new), zh mirrors

### Phase 3: Developer docs + Technical papers (2 weeks)

**What**: Skill developer onboarding + formalized technical papers.

**Tasks**:
1. Write skill authoring guide (en): How to create a skill from scratch
   - Source: skill-author SKILL.md + existing skill examples
   - Cover: SKILL.md structure, naming rules, scripts/, references/, evals
2. Write quality gate guide (en): Lint → security audit → trust scan → trigger eval → publish
   - Source: quality-gate, skill-lint, skill-security-auditor, skill-trigger-evaluator SKILL.md files
3. Write contributing guide (en): How to contribute to PEtFiSh
   - Cover: branch model, release discipline, 9-touchpoint checklist (now 10), PR process
4. Formalize sysprompt optimization paper (en):
   - Source: `evals/v011-sysprompt-plugin-report/PAPER.md` + `REPORT.md` + blog post
   - Output: standalone technical paper with abstract, methodology, results, conclusion
5. Reformat topic-aware compaction paper (en):
   - Source: `research/topic-aware-compaction/06_outputs/research-report.md` + A/B analysis
   - Output: technical paper formatted for docs site
6. Reformat companion gateway design paper (en):
   - Source: `docs/companion-gateway.md` (already well-written)
7. Write zh versions of developer guides (translated with localization)
8. Write zh versions of technical papers (translated)
9. QA pass on all pages

**Acceptance**: A new contributor can create a skill, run quality gate, and submit a PR using only the docs. Technical papers render as standalone publications with proper citations.

**QA Scenarios**:
1. **Skill authoring walkthrough**: Follow skill authoring guide to create a minimal test skill. Install the companion pack to a temp workspace, then run `uv run packs/petfish-companion-skill/.opencode/skills/skill-lint/scripts/lint_skill.py --path <test-skill>`. Expected: guide steps produce a valid skill that passes lint with score ≥ 80.
2. **Quality gate guide**: Follow quality gate guide. Expected: covers lint → security → trust → trigger eval → publish sequence with concrete commands.
3. **Technical papers**: Open each of the 3 technical papers. Expected: each has abstract, methodology, results, conclusion sections. No "TODO" or placeholder text. Citations reference actual files in the repo.
4. **Build clean**: `uv run mkdocs build --strict`. Expected: zero warnings.

**Files touched**: `docs-site/docs/en/developer/` (new), `docs-site/docs/en/technical/` (new), zh mirrors

### Phase 4: Integration + Launch (2-3 days)

**What**: Final integration, touchpoint updates, DNS, launch.

**Tasks**:
1. Add "docs site pages" as touchpoint #10 in AGENTS.md new-pack checklist
2. Add "review affected doc pages" to release checklist in AGENTS.md
3. Update README.md to link to docs site
4. Configure petfish.ai DNS/nginx to route to docs site
   - **External handoff** — not automated by this plan. Requires manual SSH session:
     - Host: `ssh ubuntu@165.154.218.237`
     - Nginx config: `/etc/nginx/sites-available/` (petfish.ai server block)
     - Web root: `/var/www/petfish.ai/`
     - Action: Add `location /docs/ { proxy_pass ... }` or CNAME `docs.petfish.ai` → GitHub Pages
     - Prerequisite: GitHub Pages deployment working (Phase 0 task 3)
     - Fallback: If DNS/nginx is deferred, docs remain accessible at `<username>.github.io/<repo>/` directly
5. Update website homepage to link to docs
6. Final cross-language consistency check
7. Smoke test: all pages render, search works in both languages, links resolve

**Acceptance**: Docs site is live, linked from petfish.ai, all touchpoints updated.

**QA Scenarios**:
1. **Touchpoint audit**: Search AGENTS.md for "docs site". Expected: touchpoint #10 present in new-pack checklist AND "review affected doc pages" in release checklist.
2. **README links**: Open README.md. Expected: contains link to docs site URL.
3. **Smoke test**: Navigate to docs site URL. Expected: homepage loads, search works in both languages, 5 random internal links resolve, no 404s.
4. **DNS/nginx** (if applied): `curl -sI https://docs.petfish.ai/en/` or `curl -sI https://petfish.ai/docs/en/`. Expected: HTTP 200. If DNS deferred, verify GitHub Pages URL works instead.

**Files touched**: `AGENTS.md`, `README.md`, website nginx config (external handoff), DNS (external handoff)

## Risk Mitigations Built Into Plan

| Risk | Mitigation in plan |
|---|---|
| Scope creep | Strict phase boundaries; Phase 1 is ONLY install+overview |
| Staleness | Auto-gen reference pages; docs in release checklist |
| AI slop | QA pass every phase; petfish-style criteria enforced |
| Missing touchpoint | Phase 4 explicitly adds touchpoint #10 before launch |
| Bilingual maintenance burden | Hybrid model: auto-gen + translated for 70%, independent only for guides |
| URL instability | URL scheme locked in Phase 0 |

## Estimated Effort

| Phase | Duration | Primary work |
|---|---|---|
| Phase 0 | 1-2 days | Infrastructure, auto-gen pipeline |
| Phase 1 | 1 week | Getting started + companion gateway (mostly reformat existing) |
| Phase 2 | 2 weeks | 3 major task guides + lighter pack guides |
| Phase 3 | 2 weeks | Developer docs + 3 technical papers |
| Phase 4 | 2-3 days | Integration, DNS, launch |
| **Total** | **~6 weeks** | |

## Out of Scope

- Migrating website blog posts to docs site (blogs stay on website)
- Versioned docs (latest-only decision locked)
- Video tutorials or interactive demos
- API documentation (no public API exists)
- Skill-by-skill deep dives for all 97 skills (auto-generated reference is sufficient; deep dives only for complex chains in task guides)
