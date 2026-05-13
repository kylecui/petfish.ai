# Tiered AGENTS.md Feasibility Plan

## 1. Problem Statement

AGENTS.md is loaded in full into every conversation's system prompt. At 1,360 lines (~4,136 tokens), it consumes fixed context budget regardless of whether the user's task relates to course development, deployment, research, or simple coding.

As more packs are installed, this cost grows linearly with no upper bound.

## 2. Current State (Measured)

| Component | Lines | Est. Tokens | Always Needed? |
|-----------|-------|-------------|----------------|
| Base (global discipline + Companion Gateway) | 378 | ~1,348 | YES |
| opencode-course-skills-pack | 515 | ~909 | Only for course tasks |
| repo-deploy-ops-skill-pack | 68 | ~189 | Only for deploy/ops tasks |
| petfish-style-skill | 57 | ~260 | Only for writing tasks |
| petfish-companion-skill | 63 | ~346 | Only for /petfish commands |
| anti-sycophancy-calibration-pack | 39 | ~123 | Only for review/judgment tasks |
| fish-trail | 89 | ~231 | Partially (gateway check is in Base) |
| research-skill-pack | 138 | ~730 | Only for research tasks |
| **TOTAL** | **1,360** | **~4,136** | |

**Key insight**: Only ~1,348 tokens (Base) are universally needed. The remaining ~2,788 tokens are pack-specific rules that apply <20% of conversations each.

## 3. Proposed Architecture

### 3.1 Two-Layer Design

```
L0 (always-on, in AGENTS.md):
  - Global discipline rules (release, python env, cross-repo, todo, etc.)
  - Companion Gateway (topic check + skill sense)
  - Pack Route Table (trigger keywords → file path)
  - "MUST READ" instruction for agent

L1 (on-demand, in separate files):
  - Each pack's rules in .opencode/agents-rules/<pack-name>.md
  - Agent reads the relevant file when task matches a pack domain
```

### 3.2 File Structure

```
AGENTS.md                              # L0: ~400-450 lines (~1,500 tokens)
.opencode/agents-rules/
  course-skills.md                     # 515 lines
  deploy-ops.md                        # 68 lines
  petfish-style.md                     # 57 lines
  petfish-companion.md                 # 63 lines
  anti-sycophancy.md                   # 39 lines
  fish-trail.md                        # 89 lines
  research.md                          # 138 lines
```

### 3.3 L0 AGENTS.md Structure

```markdown
# PEtFiSh 项目开发纪律

[... existing global rules unchanged ...]

---

## Pack-Specific Rules (On-Demand Loading)

When a task matches a pack domain, you MUST read the corresponding rules file
before proceeding. Use the Read tool on the listed path.

| Pack Domain | Trigger Signals | Rules File |
|-------------|----------------|------------|
| Course development | 课程, 教学, 大纲, 实验, QA/QC | `.opencode/agents-rules/course-skills.md` |
| Deployment & Ops | deploy, Docker, 部署, 回滚, 运维 | `.opencode/agents-rules/deploy-ops.md` |
| Writing style | 润色, 说人话, 去AI味, 风格 | `.opencode/agents-rules/petfish-style.md` |
| PEtFiSh companion | /petfish, skill创建, skill搜索 | `.opencode/agents-rules/petfish-companion.md` |
| Review/Calibration | 评审, review, critique, calibration | `.opencode/agents-rules/anti-sycophancy.md` |
| Topic governance | 话题治理, topic管理, 上下文污染 | `.opencode/agents-rules/fish-trail.md` |
| Research | 研究, 调研, 文献, evidence, 综述 | `.opencode/agents-rules/research.md` |

**Rules:**
1. If task clearly matches ONE pack → read that file immediately
2. If task matches MULTIPLE packs → read all matching files
3. If unsure → proceed without loading; load later if needed
4. Pack rules files are authoritative for their domain
```

### 3.4 Multi-Platform Scope

**This plan targets OpenCode only for L1 on-demand loading.** Other platforms are unaffected.

**Why OpenCode-only:**
- OpenCode is the only platform where the agent has `Read` tool to load files mid-conversation
- Other platforms (Claude, Cursor, Copilot, Windsurf, Codex, Antigravity) load instructions files at init — no mid-conversation file reading capability
- Cursor and Windsurf already have `condense.max_tokens` settings (8000 and 6000 respectively) — their instructions are already size-managed
- Claude, Copilot, Codex, Antigravity use `instructions_translation` to copy/rename AGENTS.md content — they need the full content in their instructions file

**Per-platform behavior after this change:**

| Platform | Instructions File | L1 On-Demand? | Change from current |
|----------|------------------|---------------|---------------------|
| OpenCode | `AGENTS.md` | YES — route table + Read tool | L0-only AGENTS.md (slim) |
| Claude | `CLAUDE.md` | NO — full injection continues | None |
| Codex | `AGENTS.md` | NO — full injection continues | None (shares AGENTS.md but no Read tool) |
| Cursor | `.cursor/rules/*.mdc` | NO — condensed injection continues | None |
| Copilot | `.github/copilot-instructions.md` | NO — full injection continues | None |
| Windsurf | `.windsurfrules` | NO — condensed injection continues | None |
| Antigravity | `AGENTS.md` | NO — full injection continues | None |

**Installer implication:** When `--platform opencode`, installer writes L0 AGENTS.md + separate L1 files. When `--platform` is anything else, installer continues current full-injection behavior unchanged. When `--platform all`, both behaviors execute for their respective platforms.

**Codex shares AGENTS.md with OpenCode** — but Codex agents lack Read tool access, so they need full content. The installer must handle this: if both opencode and codex target the same project, AGENTS.md must remain full (fall back to current behavior). This is a known constraint; in practice, projects rarely target both simultaneously.

### 3.5 Multi-Platform Install (`--platform all`) Mechanics

When `--platform all` (or a group like `--platform primary`), the installer serves multiple platforms from one run. The key constraint: **non-OpenCode instruction files (CLAUDE.md, .github/copilot-instructions.md, etc.) are translated/copied from a "full content" source, not from the slim L0 AGENTS.md.**

**Solution — Full-Content Assembly:**

1. Installer always has access to the individual pack AGENTS.md templates (from the repo/download)
2. For OpenCode: write L0 AGENTS.md + L1 files to `.opencode/agents-rules/`
3. For non-OpenCode: assemble full content by concatenating Base + all installed pack templates (same as current behavior), then translate/copy to the platform's instruction file
4. The "source of truth" for non-OpenCode translations is **not** the project's AGENTS.md file — it's the installer's in-memory assembly of Base + pack templates

**Implementation detail:**
- Current flow: `Merge-AgentsMd` writes to AGENTS.md → translation reads AGENTS.md → writes CLAUDE.md etc.
- New flow (Phase 2+): For OpenCode, write slim AGENTS.md. For translations, build full content in-memory from Base + pack templates, then translate. The in-memory assembly replaces reading AGENTS.md as the translation source.
- This means `--platform all` produces: slim AGENTS.md (for OpenCode) + full CLAUDE.md/copilot-instructions.md/etc. (for others). No contradiction.

### 3.5 Token Budget Analysis

| Scenario | Current | Proposed | Savings |
|----------|---------|----------|---------|
| Generic coding task | 4,136 | ~1,500 (L0 only) | **~63%** |
| Course task | 4,136 | ~2,409 (L0 + course) | **~42%** |
| Research task | 4,136 | ~2,230 (L0 + research) | **~46%** |
| Deploy task | 4,136 | ~1,689 (L0 + deploy) | **~59%** |
| Multi-domain (course + research) | 4,136 | ~3,139 (L0 + both) | **~24%** |
| All packs needed (worst case) | 4,136 | ~4,136 + read overhead | **~0% (slightly worse)** |

**Expected average savings**: ~50-60% (most conversations touch 0-1 packs).

## 4. Installer Modification

### 4.1 Current Behavior

```
Merge-AgentsMd:
  1. Read pack's AGENTS.md template
  2. Check if BEGIN/END markers exist in project AGENTS.md
  3. If exists + force → replace between markers
  4. If not exists → append with markers
```

### 4.2 Proposed New Behavior

```
Install-PackRules:
  1. Read pack's AGENTS.md template
  2. Write to .opencode/agents-rules/<pack-name>.md (overwrite if exists)
  3. Update route table in AGENTS.md:
     - If pack entry exists in route table → no change needed
     - If not → insert row into route table
  4. Update .opencode/installed-packs.json (unchanged)
```

### 4.3 Migration Path

**Phase 1: Dual-write (v0.11.0)**
- Installer writes BOTH: traditional merged AGENTS.md AND separate .opencode/agents-rules/ files
- AGENTS.md route table added at bottom
- Zero breakage: old behavior preserved, new behavior available

**Phase 2: Slim-down (v0.12.0)**
- Installer stops injecting pack content into AGENTS.md body
- Only writes route table entries + separate files
- AGENTS.md shrinks to L0-only

**Phase 3: Cleanup (v0.13.0)**
- Remove dual-write code path for OpenCode (no longer writes pack bodies into AGENTS.md for `--platform opencode`)
- Non-OpenCode platforms: BEGIN/END marker merge code is **retained** — it remains the only injection mechanism for Claude/Copilot/Codex/Windsurf/Antigravity
- Rename internal functions: `Merge-AgentsMd` → `Install-PackRules` (OpenCode path), keep `Merge-AgentsMd` for non-OpenCode platforms (or keep one function with a platform branch)

### 4.4 Backward Compatibility

- Users who don't upgrade keep working (old AGENTS.md still valid)
- `--force` reinstall migrates to new format
- No data loss: pack rules files are exact copies of what was in AGENTS.md

## 5. Risk Assessment

| Risk | Severity | Likelihood | Mitigation |
|------|----------|------------|------------|
| Agent forgets to read pack rules file | High | Medium | Strong "MUST READ" instruction in L0; Companion Gateway skill-sense already detects domain |
| Agent reads wrong pack file | Low | Low | Clear trigger signals in route table |
| First-turn latency (extra read call) | Low | High | Acceptable: one read tool call adds <1s |
| Complex multi-domain tasks miss a pack | Medium | Medium | "If unsure, load later" rule; agent can always read mid-conversation |
| OpenCode changes AGENTS.md loading | Medium | Low | Monitor OpenCode releases; architecture is future-proof either way |
| Installer migration breaks existing installs | High | Low | Dual-write phase ensures zero breakage |

### 5.1 Key Risk Deep-Dive: Agent Compliance

The biggest risk is agent non-compliance (forgetting to read the file). Mitigations:

1. **Route table is visually prominent** — placed right after global rules, impossible to miss
2. **Companion Gateway already does domain detection** — Tier 1 keyword matching fires every message, naturally surfaces which pack is relevant
3. **Skills themselves reference their pack rules** — skills like `course-development-orchestrator` already assume course rules are loaded
4. **Fallback is graceful** — if agent doesn't load pack rules, it still has skill instructions (SKILL.md) which contain the operational workflow; pack rules are supplementary governance, not core logic

## 6. Implementation Checklist & QA Scenarios

### v0.11.0 (L1-Only — Originally "Dual-Write", Skipped to Direct L1)

**Status: ✅ COMPLETE (v0.11.0 + v0.11.1)**

**What actually happened:** Skipped dual-write entirely. Went straight to L1-only for OpenCode:
- OpenCode + L1 pack → `Write-PackRulesFile` + `Install-PluginFile` + `Register-PluginInConfig` + `Remove-InlinePackSection`
- Non-OpenCode → `Merge-AgentsMd` (unchanged)
- System-prompt-rules plugin delivers L1 files via cached system prompt prefix (-19.1% token savings)
- AGENTS.md is already L0-only (~400 lines)

**Implementation:**
- [x] Create `.opencode/agents-rules/` directory structure
- [x] Extract pack content from AGENTS.md into individual files
- [x] Add route table section to AGENTS.md Base
- [x] L1 branch in all 4 installers: skip `Merge-AgentsMd`, call L1 helpers instead
- [x] Plugin delivery: `system-prompt-rules.ts` with mode=all
- [x] v0.10.x migration: `Remove-InlinePackSection` strips old inline markers

**QA Scenario 1 — Fresh install produces both formats (PS1):**
```
Setup: Empty temp directory, no existing .opencode/
Command: .\install.ps1 -Pack "course,deploy" -Target $tempDir -Platform opencode
Verify:
  1. cat $tempDir/AGENTS.md | Select-String "BEGIN pack: opencode-course" → MUST match (legacy injection present)
  2. cat $tempDir/AGENTS.md | Select-String "Pack-Specific Rules" → MUST match (route table present)
  3. Test-Path $tempDir/.opencode/agents-rules/course-skills.md → MUST be True
  4. Test-Path $tempDir/.opencode/agents-rules/deploy-ops.md → MUST be True
  5. diff (content between BEGIN/END markers in AGENTS.md) vs (agents-rules/course-skills.md) → MUST be identical
```

**QA Scenario 2 — Upgrade from v0.10.x preserves content (bash):**
```
Setup: Directory with v0.10.x AGENTS.md (has BEGIN/END markers, no route table, no agents-rules/)
Command: ./install.sh --pack course --target $tempDir --platform opencode --force
Verify:
  1. grep "BEGIN pack: opencode-course" $tempDir/AGENTS.md → exit 0 (legacy markers present)
  2. grep "Pack-Specific Rules" $tempDir/AGENTS.md → exit 0 (route table added)
  3. test -f $tempDir/.opencode/agents-rules/course-skills.md → exit 0
  4. diff <(sed -n '/BEGIN pack: opencode-course/,/END pack: opencode-course/p' AGENTS.md) agents-rules/course-skills.md → identical content
```

**QA Scenario 3 — Non-OpenCode platform unchanged:**
```
Setup: Empty temp directory
Command: .\install.ps1 -Pack "course" -Target $tempDir -Platform claude
Verify:
  1. Test-Path $tempDir/CLAUDE.md → True (instructions file created)
  2. cat $tempDir/CLAUDE.md | Select-String "BEGIN pack: opencode-course" → MUST match (full injection)
  3. Test-Path $tempDir/.opencode/agents-rules/ → False (no L1 files for non-OpenCode)
```

**QA Scenario 4 — Agent reads on-demand file when triggered:**
```
Setup: Project with v0.11.0 dual-write install (both formats present)
Prompt to agent: "帮我设计一个课程大纲"
Expected observable behavior:
  1. Agent's Companion Gateway Tier 1 matches "课程" → course pack domain
  2. Agent calls Read tool on .opencode/agents-rules/course-skills.md (visible in tool call log)
  3. Agent's response follows course-skills rules (e.g., mentions "先提纲后正文", respects directory conventions)
Negative test: Prompt "fix the type error in auth.ts"
  → Agent should NOT read any agents-rules/ file (no pack domain match)
```

### v0.12.0 → Collapsed into v0.11.x (Slim-Down)

**Status: ✅ COMPLETE — AGENTS.md was already L0-only after v0.11.0 implementation**

**Implementation:**
- [x] Remove pack content injection into AGENTS.md body for OpenCode platform
- [x] AGENTS.md shrinks to L0 (~400 lines)
- [x] Non-OpenCode platforms continue full injection

**QA Scenario 5 — AGENTS.md is L0-only after slim-down:**
```
Setup: Fresh install with v0.12.0
Command: .\install.ps1 -Pack "course,deploy,research" -Target $tempDir -Platform opencode
Verify:
  1. (Get-Content $tempDir/AGENTS.md).Count → ≤500 lines (L0 only, no pack bodies)
  2. Select-String "BEGIN pack:" $tempDir/AGENTS.md → NO matches (no legacy markers)
  3. Select-String "Pack-Specific Rules" $tempDir/AGENTS.md → match (route table present)
  4. (Get-ChildItem $tempDir/.opencode/agents-rules/*.md).Count → 3 (course, deploy, research)
```

**QA Scenario 6 — All 7 pack domains functional via on-demand loading:**
```
For each pack domain, send a domain-specific prompt and verify:
  - Course: "课程大纲设计" → agent reads course-skills.md, follows course rules
  - Deploy: "部署到服务器" → agent reads deploy-ops.md, follows deploy rules
  - Research: "帮我研究一下" → agent reads research.md, routes to research-router
  - Style: "润色这段话" → agent reads petfish-style.md, applies style rules
  - Companion: "/petfish status" → agent reads petfish-companion.md
  - Calibrate: "评审这个方案" → agent reads anti-sycophancy.md
  - Context: "整理话题" → agent reads fish-trail.md
Observable: each prompt triggers exactly one Read tool call to the correct agents-rules/ file
```

**QA Scenario 7 — Token measurement:**
```
Method: In OpenCode, start a new conversation. Before sending any message, check the system prompt token count (via OpenCode debug/stats if available, or estimate from AGENTS.md line count × 1.5 tokens/word).
Target: L0 AGENTS.md ≤ 1,800 tokens (vs current ~4,136)
```

### v0.13.0 → Collapsed into v0.11.x (Cleanup)

**Status: ✅ COMPLETE — No dual-write code was ever created; nothing to remove**

**Implementation:**
- [x] Remove dual-write code: N/A — skipped dual-write, went straight to L1-only
- [x] Retain BEGIN/END marker merge for non-OpenCode platforms (unchanged — `else` branch in all 4 installers)
- [x] Non-OpenCode translations continue via `Merge-AgentsMd` inline injection
- [x] All 4 installers verified: identical L1 branching logic, no dead code

**QA Scenario 8 — Phase 3 cleanup verified:**
```
Verify:
  1. install.ps1 OpenCode path: no longer injects pack bodies into AGENTS.md (only route table)
  2. install.ps1 non-OpenCode path: still uses BEGIN/END markers to inject into CLAUDE.md etc. (marker code retained)
  3. install.sh same split: OpenCode=slim, non-OpenCode=full injection
  4. --platform all: produces slim AGENTS.md + full CLAUDE.md (run with -Pack course -Platform all, compare file sizes)
```

**QA Scenario 9 — Force reinstall from clean state:**
```
Setup: Directory with NO .opencode/ at all
Command: .\install.ps1 -Pack all -Target $tempDir -Platform opencode -Force
Verify:
  1. AGENTS.md exists with route table, no pack bodies
  2. All installed pack L1 files exist in .opencode/agents-rules/
  3. installed-packs.json lists all packs
```

## 7. Success Criteria

1. **Token reduction**: Average conversation loads ≤2,000 tokens of AGENTS.md content (vs current 4,136)
2. **Zero regression**: All pack-domain tasks still work correctly (agent reads rules when needed)
3. **Installer robustness**: Fresh install, upgrade, and force-reinstall all work
4. **Scalability**: Adding new packs doesn't grow L0 beyond +1 table row (~20 tokens)

## 8. Decision Required

Proceed with Phase 1 (dual-write) in v0.11.0? This is fully backward-compatible and allows real-world testing of agent compliance before committing to the slim-down.
