# Plan: Council Thinking Skillpack — B+ Integration

**Date**: 2025-07-05
**Mode**: balanced (rigor off)
**Decision**: B+ — add council-thinking as 2nd skill in calibrate pack + rename pack to broader name.

## Decisions Confirmed
- **Pack directory name**: `judgment-calibration-pack` (from `anti-sycophancy-calibration-pack`)
- **Alias**: `calibrate` (UNCHANGED — backwards compat, no muscle-memory break)
- **Skill names**: `fish-calibrate` (existing, untouched) + `council-thinking` (new)
- **v0.1 scope**: Full v0.1 + v0.2 preview (SKILL.md + agents/*.md + schemas/ + examples/ + references/ + evals/)

## Rename Strategy
- `legacy_names` field appends old dir name: `["anti-sycophancy-calibration", "anti-sycophancy-calibration-pack"]`
- `PACK_RENAMES` in installers gains: `"anti-sycophancy-calibration-pack": "judgment-calibration-pack"` (auto-cleanup on upgrade, per v1.8.2 precedent)
- `SKILL_RENAMES` unchanged (fish-calibrate mapping already exists)
- External repo `kylecui/petfish-pack-anti-sycophancy` NOT renamed (cross-repo protection; out of scope)

## Work Units (Parallel)

### Unit 0 (me): Rename pack dir
- `git mv packs/optional/anti-sycophancy-calibration-pack packs/optional/judgment-calibration-pack`

### Unit 1 (deep agent): Pack internals
**Scope**: Inside `packs/optional/judgment-calibration-pack/`
- Create `.opencode/skills/council-thinking/` with:
  - `SKILL.md` (frontmatter + 5+1 workflow distillation from dev plan)
  - `references/` (full-output-template.md, quick-output-template.md, arbiter-summary-template.md)
  - `agents/` (critic.md, essence.md, opportunity.md, outsider.md, executor.md, arbiter.md)
  - `schemas/` (subagent-output.schema.md, council-output.schema.md)
  - `examples/` (strategy-review.md, presentation-review.md, product-positioning-review.md, research-design-review.md)
  - `evals/trigger/council-thinking.json` (trigger evals)
- Update `pack-manifest.json`: name, legacy_names, skill_count=2, skills array, contents, description
- Update `AGENTS.md`: broaden title to "Judgment Calibration Pack", add council-thinking routing rules + conflict resolution
- Source: `dev_reference/council-thinking-skillpack-dev-plan.md`
- Pattern: follow `fish-calibrate/SKILL.md` structure

### Unit 2 (quick agent): Installers
**Scope**: 5 files at repo root
- `install.py`: ALIASES values (2 lines) → `judgment-calibration-pack`; L1_PACK_MAP key → new name; add PACK_RENAMES entry `old→new`
- `install.ps1`, `install.sh`, `remote-install.ps1`, `remote-install.sh`: same pattern (ALIASES, L1Map, rename maps, AllPacks arrays, display orders)

### Unit 3 (quick agent): Catalog + Market
**Scope**: Companion catalog scripts + market registration
- `catalog_query.py`: ALIAS_MAP values; add `"council-thinking": "judgment-calibration-pack"`; TRIGGERS add council-thinking entry; PROFILES add council-thinking to comprehensive
- `check_installed.py`: KNOWN_PACKS value
- `gateway_classifiers.py`: add council-thinking triggers if applicable
- `skill-registry/server.py`: value update
- `marketplace_search.py`: comment update
- Market: rename `petfish-market/registry/official/anti-sycophancy-calibration-pack.json` → `judgment-calibration-pack.json`; update `petfish-market/index.json` (name, aliases, skills, path)

### Unit 4 (unspecified-high agent): Docs + Website
**Scope**: Root docs and website source
- `README.md`, `docs/zh/README.md`: optional packs table, profile mapping, repo structure, version history
- `REPO-LANDSCAPE.md`: pack tree + alias table
- `AGENTS.md` (root): pack-specific rules mapping line (`.opencode/agents-rules/anti-sycophancy.md` path stays — it's the rules FILE name, not the pack name)
- `docs/agent-install.md`, `docs/companion-gateway.md`, `docs/online-projects.md`, `docs/zh/companion-gateway.md`
- `website/*.html`, `website/market-data.js`

### Unit 5 (unspecified-high agent): docs-site + tests + root .opencode
**Scope**: docs-site source + tests + installed copies
- `docs-site/docs/**` (28 files): pack reference pages, skill reference, guides, nav
- `docs-site/mkdocs.yml`: nav entry
- `docs-site/scripts/generate_skill_reference.py`: alias map
- `tests/test_companion_gateway.py`, `tests/test_migration_e2e.py`: update expected names
- `evals/trigger/anti-sycophancy-calibration-pack/`: rename dir if needed
- Root `.opencode/agents-rules/anti-sycophancy.md`, `.opencode/skills/fish-calibrate/`, `.opencode/skills/fish-brain/scripts/`: update installed copies for consistency
- `.opencode/plugin/system-prompt-rules.ts`: update if it hardcodes pack name

## Out of Scope (Explicit)
- External repo `kylecui/petfish-pack-anti-sycophancy` rename (cross-repo protection)
- `docs-site/site/` generated HTML (rebuild via `mkdocs build` after source edits)
- v0.3 real subagent implementation (deferred per dev plan)
- GitHub Release creation (user-triggered separately)

## Verification (After all agents complete)
1. `uv run .opencode/skills/skill-lint/scripts/lint_skill.py --path packs/optional/judgment-calibration-pack/.opencode/skills/council-thinking/`
2. `uv run install.py --list` (verify new pack name appears, old name in legacy)
3. Grep for stale `anti-sycophancy-calibration-pack` references that should be `judgment-calibration-pack` (exclude legacy_names, PACK_RENAMES, docs-site/site/)
4. Check pack-manifest.json contents list matches actual files
