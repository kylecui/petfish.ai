# Plan: fish-reflection Pack (12th PEtFiSh Pack)

## Objective

Evaluate the fish-reflection design doc, address design concerns, create the pack, and integrate via the 11-touchpoint checklist.

## Design Assessment

### Strengths

1. **Clear value proposition**: Turn one-off corrections into reusable project knowledge (AGENTS.md `开发经验沉淀` already proves this pattern works)
2. **Weak coupling principle** (§13): Explicit decision to not become a dispatcher — correct boundary
3. **Anti-patterns list** (§14): 10 concrete anti-patterns show mature thinking about failure modes
4. **Three-level model**: L1 (instant) vs L2 (task debrief) vs L3 (guidance file) provides proportional response

### Design Concerns (Must Address Before Implementation)

#### C1: L0 is redundant — remove it

L0 ("baseline self-check before output") is indistinguishable from good prompt engineering. Every well-configured agent already does sanity checks. Including L0 creates:
- Trigger scope so broad it matches every non-trivial task
- Overlap with Companion Gateway's existing checks (topic check, anti-sycophancy, failure signal detection)
- "Reflection fatigue" where the mechanism fires on everything

**Decision**: Drop L0 entirely. The skill starts at L1 (instant reflection on detected anomalies).

#### C2: Trigger scope (§7.2–7.5) is too broad — narrow to failure/rework signals only

Current triggers cover: task anomaly, multi-round rework, tool failure, high-impact tasks, user correction. This is essentially "everything non-trivial."

**Decision**: Narrow to three concrete triggers:
1. **User correction/rework** — user explicitly says something was wrong or asks to redo
2. **Repeated failure** — 2+ consecutive failed attempts at the same operation
3. **Explicit request** — user says "reflect", "what went wrong", "lessons learned"

Remove: "high-impact task" (too vague), "task anomaly" (overlaps with normal debugging).

#### C3: Reflection Card template is too heavy — simplify

9-field card template is overkill for "minimum sedimentation unit." AGENTS.md `开发经验沉淀` uses 2-3 paragraph free-form entries effectively.

**Decision**: Reduce to 4 fields:
- `trigger`: What happened (1 line)
- `root_cause`: Why it happened (1-2 lines)
- `prevention_rule`: Concrete rule to prevent recurrence (1-2 lines)
- `scope`: Where this applies (file/project/universal)

#### C4: Consumption/retrieval mechanism missing

Design says outputs are "project knowledge assets" but has no spec for how future sessions discover and use accumulated reflection files.

**Decision**: v1 keeps it simple — reflections go to `.opencode/reflections/` (platform-agnostic, not in `docs/` which is for course content). The skill's SKILL.md will include instructions to check this directory at session start for relevant accumulated lessons. No scripts in v1.

#### C5: Companion Gateway integration underspecified

**Decision**: Do NOT add reflection to the always-on Gateway flow. Reflection is triggered reactively (on failure/rework/request), not proactively on every message. This keeps it lightweight and avoids Gateway bloat.

### Design Decisions Summary

| Aspect | Design Doc | Plan Decision |
|---|---|---|
| Levels | L0-L3 (4 levels) | L1-L3 (3 levels, drop L0) |
| Triggers | 5 categories (broad) | 3 triggers (failure, rework, explicit) |
| Card fields | 9 fields | 4 fields |
| Output directory | `docs/reflections/` or `.opencode/reflections/` | `.opencode/reflections/` |
| Gateway integration | Unclear | Not in Gateway; reactive only |
| Scripts | None in v1 | None in v1 |
| Pack alias | TBD | `reflect` |
| Pack dir name | TBD | `fish-reflection-pack` |

## Pack Structure

```
packs/fish-reflection-pack/
├── .opencode/
│   └── skills/
│       └── fish-reflection/
│           ├── SKILL.md
│           ├── references/
│           │   ├── reflection-card-template.md
│           │   ├── anti-patterns.md
│           │   └── trigger-patterns.md
│           └── assets/
│               └── reflection-levels.md
├── AGENTS.md                    # Instructions merge content
├── pack-manifest.json
└── CHANGELOG.md
```

## 9-Touchpoint Integration

| # | Touchpoint | File | What to Add |
|---|---|---|---|
| 1 | Local installer alias (PS1) | `install.ps1` | `"reflect" = "fish-reflection-pack"` + `"fish-reflect" = "fish-reflection-pack"` |
| 2 | Local installer alias (sh) | `install.sh` | `[reflect]="fish-reflection-pack"` + `[fish-reflect]="fish-reflection-pack"` |
| 3 | Remote installer ALL_PACKS (PS1) | `remote-install.ps1` | Add to `$AllPacks` array + alias registry |
| 4 | Remote installer ALL_PACKS (sh) | `remote-install.sh` | Add to `ALL_PACKS` array + alias registry |
| 5 | Companion catalog | `catalog_query.py` | Add ALIAS_MAP, TRIGGERS, PROFILES (at least `comprehensive`), FAILURE_SIGNALS |
| 6 | project-initializer | `packs/project-initializer-skill/.opencode/skills/project-initializer/SKILL.md` + `tools/init_project.py` | Add `reflect` to relevant profiles and pack references |
| 7 | README | `README.md` | Update pack table to 12 packs, update profile mapping |
| 8 | Website | `website/index.html`, `website/pitch.html`, `website/blog.html` | Update pack count, add pack card/row |
| 9 | Install/upgrade docs | `docs/agent-install.md`, `docs/agent-upgrade.md` | Update pack list |
| 10 | Chinese translation | `docs/zh/README.md` | Sync all changes |
| 11 | Archive docs | `docs/archive/` relevant files | Update pack counts and lists |

## Implementation Phases

### Phase 1: Create the pack (skill content)

**Tasks:**
1. Write SKILL.md with narrowed triggers and simplified card format
2. Write `references/reflection-card-template.md`
3. Write `references/anti-patterns.md`
4. Write `references/trigger-patterns.md`
5. Write `assets/reflection-levels.md`
6. Write `pack-manifest.json`
7. Write `AGENTS.md` merge content
8. Write `CHANGELOG.md`

**QA:**
- Run `uv run packs/petfish-companion-skill/.opencode/skills/skill-lint/scripts/lint_skill.py --path packs/fish-reflection-pack/.opencode/skills/fish-reflection/`
- Expected: score ≥ 80/100, no ERROR-level findings
- Verify SKILL.md frontmatter has: name, description, version fields
- Verify `pack-manifest.json` lists all skills and has valid JSON structure (`python -c "import json; json.load(open('packs/fish-reflection-pack/pack-manifest.json'))"`)

### Phase 2: 11-touchpoint integration

**Tasks:**
1. Add alias entries to `install.ps1` (line ~108-130 `$Aliases` hashtable)
2. Add alias entries to `install.sh` (line ~515-537 `ALIASES` associative array)
3. Add to `remote-install.ps1` `$AllPacks` array + alias registry
4. Add to `remote-install.sh` `ALL_PACKS` array + alias registry
5. Add ALIAS_MAP, TRIGGERS, PROFILES, FAILURE_SIGNALS entries to `catalog_query.py`
6. Update `project-initializer` SKILL.md and `init_project.py` to include `reflect` in relevant profiles
7. Update `README.md`: pack table (11→12), profile mapping table
8. Update `website/index.html`, `website/pitch.html`, `website/blog.html`: pack counts, pack cards
9. Update `docs/agent-install.md`, `docs/agent-upgrade.md`: pack lists
10. Update `docs/zh/README.md`: sync all changes
11. Update `docs/archive/` files: pack counts and lists where referenced

**QA per sub-task:**
- Installers: search each of `install.ps1`, `install.sh`, `remote-install.ps1`, `remote-install.sh` for string "reflect" → each file should have ≥2 matches (alias + fish-alias)
- Catalog: `uv run packs/petfish-companion-skill/.opencode/skills/petfish-companion/scripts/catalog_query.py --search reflect` → should return pack info with alias and description
- Catalog: `uv run packs/petfish-companion-skill/.opencode/skills/petfish-companion/scripts/catalog_query.py --profile comprehensive` → output includes `reflect`
- README: search for "12" in pack table header, verify `reflect` appears in pack list and profile table
- project-initializer: search for `reflect` in SKILL.md and `init_project.py` → at least 1 match each

### Phase 3: End-to-end verification

**Tasks & QA:**
1. Run skill-lint on final skill: `uv run packs/petfish-companion-skill/.opencode/skills/skill-lint/scripts/lint_skill.py --path packs/fish-reflection-pack/.opencode/skills/fish-reflection/` → score ≥ 80, 0 ERRORs
2. Run quality-gate: `uv run packs/petfish-companion-skill/.opencode/skills/quality-gate/scripts/run_gate.py --path packs/fish-reflection-pack/.opencode/skills/fish-reflection/` → PASS or CONDITIONAL
3. Dry-run local installer: `.\install.ps1 -List` → `reflect` appears in available packs list
4. Verify catalog search: `uv run packs/petfish-companion-skill/.opencode/skills/petfish-companion/scripts/catalog_query.py --search reflect` → returns pack info with alias, description, and triggers
5. Verify profile inclusion: `uv run packs/petfish-companion-skill/.opencode/skills/petfish-companion/scripts/catalog_query.py --profile comprehensive` → `reflect` appears in output
6. Cross-check: search all 11 touchpoint files for string "reflect" → each has ≥1 match

## Files Changed

~18 files total:
- 8 new files (SKILL.md, 3 references, 1 asset, pack-manifest.json, CHANGELOG.md, AGENTS.md)
- ~10 existing files (4 installers, catalog_query.py, project-initializer SKILL.md + init_project.py, README.md, docs, zh docs)
- Website files (3 HTML files)
- Archive docs (variable count)

## Risks

1. **Trigger too narrow**: May miss valuable reflection opportunities. Mitigated by explicit `/reflect` command.
2. **Overlap with `开发经验沉淀`**: The existing AGENTS.md section already captures lessons. Reflection skill adds structured process but must not duplicate. Skill output feeds INTO `开发经验沉淀` when lessons are universal.
3. **Adoption**: Instruction-only skill depends on agent compliance. No enforcement mechanism in v1.
