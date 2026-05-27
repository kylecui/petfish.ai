# PEtFiSh v0.11.0 Upgrade Findings

## Date
2026-05-12

## Pre-upgrade State (v0.10.x)
- AGENTS.md: 40,365 bytes, 1,037 lines, **13,937 tokens** (cl100k_base)
  - Base (project-specific): 61 lines, 415 tokens (3.0%)
  - Pack inline rules: 976 lines, 13,523 tokens (97.0%)
  - 7 packs with inline rules: opencode-course-skills-pack, research-skill-pack, fish-trail, repo-deploy-ops-skill-pack, petfish-companion-skill, anti-sycophancy-calibration-pack, petfish-style-skill
- installed-packs.json: 11 packs registered

## Upgrade Command
```bash
curl -fsSL https://raw.githubusercontent.com/kylecui/petfish.ai/master/remote-install.sh | bash -s -- --pack all --force
```

## Post-upgrade State (v0.11.0)
- AGENTS.md: **UNCHANGED** — byte-identical to v0.10.x (md5: a1871651d13d5593073221329bf8d30b)
- New directory: `.opencode/agents-rules/` with 7 files:
  - anti-sycophancy.md: 826 tokens
  - course-skills.md: 5,852 tokens
  - deploy-ops.md: 973 tokens
  - fish-trail.md: 1,512 tokens
  - petfish-companion.md: 986 tokens
  - petfish-style.md: 610 tokens
  - research.md: 2,568 tokens
  - **Total: 13,327 tokens**

## Bug: Inline Pack Rules NOT Stripped

The v0.11.0 release notes state:
> "AGENTS.md slimmed from 1,383 to 400 lines. Pack-specific rules extracted to `.opencode/agents-rules/*.md` and loaded on-demand via route table."

But after `--pack all --force` upgrade:
1. AGENTS.md still contains all 7 `<!-- BEGIN pack: ... -->` sections (13,523 tokens)
2. `.opencode/agents-rules/` was created with equivalent content (13,327 tokens)
3. **Result: DUPLICATION** — pack rules exist both inline AND in agents-rules, totaling 26,850 tokens

### Expected Behavior
AGENTS.md should be ~400 lines (~415 tokens base) with pack rules only in `.opencode/agents-rules/`.

### Actual Behavior
AGENTS.md is 1,037 lines (13,937 tokens) with pack rules duplicated in both locations.

### Impact
- Zero token savings achieved
- Potential confusion if inline and agents-rules versions diverge
- System prompt may load both copies depending on implementation

## Token Comparison

| Metric | v0.10.x | v0.11.0 (actual) | v0.11.0 (expected) |
|--------|---------|-------------------|---------------------|
| AGENTS.md | 13,937 | 13,937 (unchanged) | ~415 (base only) |
| agents-rules/ | N/A | 13,327 | 13,327 |
| Total loaded (no packs) | 13,937 | 13,937+ | ~415 |
| Total loaded (all packs) | 13,937 | 27,264 (worse!) | ~13,742 |

## Post-Fix Analysis (manual inline strip)

After manually removing inline pack sections (simulating intended v0.11.0 behavior):

### Token Savings (our 11-pack config, 7 with rules)

| Scenario | Tokens | Savings vs v0.10.x |
|----------|--------|---------------------|
| No packs triggered | 414 | 13,523 (97.0%) |
| + petfish-style.md | 1,024 | 12,913 (92.7%) |
| + anti-sycophancy.md | 1,240 | 12,697 (91.1%) |
| + deploy-ops.md | 1,387 | 12,550 (90.0%) |
| + petfish-companion.md | 1,400 | 12,537 (90.0%) |
| + fish-trail.md | 1,926 | 12,011 (86.2%) |
| + research.md | 2,982 | 10,955 (78.6%) |
| + course-skills.md | 6,266 | 7,671 (55.0%) |
| All 7 packs triggered | 13,741 | 196 (1.4%) |

### Claim Verification

| Claim | Theirs | Ours | Verdict |
|-------|--------|------|---------|
| v0.10.x total | ~9,579 | 13,937 | Ours higher (more packs) |
| v0.11.0 base | ~3,089 | 414 | Ours lower (minimal project AGENTS.md) |
| Max savings | 68% | 97.0% | ✅ Exceeds claim (config-dependent) |
| Typical (1 pack) | 55-65% | 55-93% | ✅ Range matches at low end |
| Worst case | ~0% | 1.4% | ✅ Matches claim |

**Conclusion**: Token savings claims are **directionally correct** but vary significantly by project config. The base AGENTS.md size matters — projects with more custom content will see lower max savings. Their claimed ~3,089 base likely includes default boilerplate that our minimal project AGENTS.md (61 lines) doesn't have.

## Bug Filed
https://github.com/kylecui/petfish.ai/issues/102 — Inline pack rules not stripped during upgrade

## Final AGENTS.md State (manually fixed)

After manually stripping inline packs and adding route table:
- AGENTS.md: 76 lines, 3,170 bytes, **777 tokens**
- Route table references 7 agents-rules files
- Total on-demand rules: 13,327 tokens

## Files Produced

| File | Purpose |
|------|---------|
| `AGENTS.md.v010x.bak` | Pre-upgrade backup |
| `installed-packs.v010x.json` | Pre-upgrade pack registry |
| `upgrade-output.log` | Full installer output |
| `AGENTS.md.reference.md` | SKILL_builder's own AGENTS.md (6,051 tokens) |
| `UPGRADE-FINDINGS.md` | This file |
| `RESTART-TEST-PLAN.md` | Runtime verification protocol |
| `VERIFICATION-PLAN.md` | Complete verification methodology |
| `COMPACTION-REEVALUATION.md` | Compaction plugin reassessment under v0.11.0 |

## GitHub Issues Filed
- https://github.com/kylecui/petfish.ai/issues/102 — Inline pack rules not stripped during upgrade
