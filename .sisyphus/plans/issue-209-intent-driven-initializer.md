# Plan: #209 Intent-Driven Dynamic Skill Discovery for project-initializer

## Issue Summary

The `project-initializer` SKILL.md (Section 11) has a hardcoded Profile → Pack mapping table that goes stale every time a new pack is added. The proposal replaces this with intent-driven discovery using existing `skill-registry search_skills` MCP.

## Critical Evaluation

### The Problem is Real

- SKILL.md Section 11 (lines 360-411) has a static table mapping 9 profiles to packs
- The table is missing `calibrate`, `reflect`, `series-style` packs
- Pack classification elsewhere in the file says "9 optional" when there are 11
- Every new pack requires manual SKILL.md edits → maintenance trap confirmed

### The Proposed Solution: Over-Engineered for Phase 1

The proposal's core idea (replace static table with dynamic registry query) is correct. However, the specific implementation has several issues:

**Issue 1: Keyword extraction is non-deterministic and fragile**

"Extract 3-5 domain keywords" from free text is unreliable. Different agents/sessions may extract different keywords for identical user intent. A user saying "我要做一个Python全栈项目的开发测试和部署" might get keywords ["开发","测试","部署"] or ["Python","全栈","项目"] — leading to different pack recommendations.

**Issue 2: search_skills matches skills, not packs**

`skill-registry search_skills` searches individual SKILL.md descriptions (granular). A user saying "我要做部署" would get individual skill results (deployment-executor, deployment-verifier, etc.) but not the pack-level recommendation. The aggregation step ("group by pack") adds complexity and may miss packs whose individual skills don't match the keyword but whose pack-level intent does.

**Issue 3: UX regression for common case**

Profile selection is fast, deterministic, and well-understood. Intent-driven discovery adds:
- Agent must call MCP tools (latency, tokens)
- Keyword extraction step (non-deterministic)
- Pack grouping step (fragile)
- More back-and-forth with user

For the 80% case where the user knows their profile, this is strictly worse.

**Issue 4: Conflates two problems**

- Problem A: Static data in SKILL.md goes stale (maintenance issue)
- Problem B: Profile selection is too rigid (UX issue, debatable)

Problem A can be solved without changing the UX. Problem B may not be a real problem — profiles already cover common use cases well.

### What Should Actually Change

**The right fix is simpler than the proposal suggests:**

1. **Remove hardcoded pack counts and static tables** from SKILL.md
2. **Instruct the agent to query `skill-registry list_installed_packs` + `skill-registry list_available_packs`** at runtime to get the current pack list
3. **Keep profiles as the primary path**, but make the mapping dynamic:
   - Instead of a hardcoded table, define profile semantics ("code profile → needs deploy, testing, and style packs")
   - Agent resolves these semantics against the live registry
4. **Add intent-driven as a supplement** (not replacement): when no profile fits, or user provides custom intent, fall back to keyword search
5. **Remove the "Research Domain Clarification" gate from Section 2** — this couples initialization to a specific pack's internal structure, which is exactly the kind of coupling we're trying to eliminate

### Proposed SKILL.md Changes (Phase 1 Only)

**Remove:**
- Lines 364-376: Static Profile → Pack Mapping table
- Lines 116: "Check the Profile → Pack Mapping table to determine eligibility" (hardcoded reference)
- Pack counts anywhere ("4 core + 9 optional")

**Replace Section 11 with:**

```markdown
### 11. Auto-Install Skill Packs (Post-Initialization)

After `init_project.py` completes successfully, recommend and install skill packs.

#### Pack Discovery (Dynamic)

Query the live registry to get available packs. Do NOT use hardcoded pack lists.

1. Call `skill-registry list_available_packs` to get all installable packs
2. Call `skill-registry list_installed_packs` to check what's already installed
3. Use the profile semantics below to determine which packs to recommend
4. Present the recommendation and ask the user to confirm, add, or remove

#### Profile Semantics (Not Pack Lists)

Profiles define the project's NEED, not a specific pack list. The agent resolves
these needs against the current registry at runtime.

| Profile | Needs (semantic) | Example Resolution |
|---|---|---|
| `minimal` | Writing style only | petfish |
| `course` | Course development + style | course, petfish |
| `code` | Development, testing, deployment, style | deploy, testdocs, petfish |
| `ops` | Operations, deployment, style | deploy, petfish |
| `security` | Security, testing, deployment, style | deploy, testdocs, trust, petfish |
| `research` | Research, style | research, petfish |
| `writing` | Writing, presentations, style | ppt, petfish |
| `skills-package` | Style, testing | petfish, testdocs |
| `comprehensive` | All available packs | (resolved from full registry) |

When a new pack is added to the registry, it automatically appears in `comprehensive`
and can be matched to other profiles by semantic need.

For `comprehensive`: install ALL available packs from the registry.

For other profiles: match the semantic needs to pack descriptions from the registry.
If unsure whether a pack matches a need, include it in the "optional" list for user review.

#### No Profile / Custom Intent

If no standard profile fits, or the user provides a custom description:
1. Extract domain keywords from the user's intent
2. Call `skill-registry search_skills` for each keyword
3. Collect unique parent packs from matched skills
4. Present matched packs first, then remaining available packs
5. Ask user to confirm

#### Presentation Format

```
Based on your profile, these packs will be installed:
  ✅ [matched packs with descriptions]

Available but not recommended for your profile:
  📦 [remaining packs]

Would you like to add or remove any packs? (Enter pack names, or "proceed")
```

#### Procedure

1. Detect platform: `.agents/` → `antigravity`, `.opencode/` → `opencode`, both → `all`
2. Run the remote installer for each confirmed pack (Windows PowerShell / macOS Linux)
3. If installer fails, provide manual installation instructions
4. Record installed packs in the completion report
```

### What NOT to Change

1. **Profile list** — the 9 profiles remain as-is
2. **Section 2 Research Domain Clarification** — keep it but decouple from the mapping table (it should check if research pack is in the resolved recommendation, not a hardcoded table)
3. **`init_project.py`** — no script changes in Phase 1
4. **`search_skills` MCP** — no enhancement needed in Phase 1

### Scope

| In Scope (Phase 1) | Out of Scope |
|---|---|
| Rewrite SKILL.md Section 11 | `init_project.py` changes |
| Replace static table with dynamic instructions | `search_skills` MCP enhancement |
| Update Section 2 research gate reference | New profile definitions |
| Remove hardcoded pack counts | Phase 2 (script --intent flag) |
| Version bump to 1.1.0 | Phase 3 (bilingual matching) |

### Acceptance Criteria

- [ ] SKILL.md contains zero hardcoded pack counts or pack name lists
- [ ] Section 11 instructs agent to query live registry instead of reading a table
- [ ] Profile → Pack mapping uses semantic needs, not hardcoded pack names
- [ ] New packs added to market are automatically discoverable without SKILL.md changes
- [ ] Profiles work identically from user perspective (backward compatible)
- [ ] `comprehensive` profile installs ALL packs from live registry
- [ ] AGENTS.md pack-specific rules injection still works (no installer changes)
- [ ] Section 2 research gate works without referencing the removed table

### Files to Change

| File | Change |
|---|---|
| `packs/core/project-initializer-skill/.opencode/skills/fish-init/SKILL.md` | Sections 2, 11 rewrite |
| `packs/core/project-initializer-skill/AGENTS.md` | No change needed (no hardcoded packs) |

### Reviewer Feedback (test team comment on #209)

The test team noted that Tier 1 (profile semantic resolution) and Tier 2 (intent keyword extraction) share the same fundamental uncertainty — both are keyword matching against descriptions. Profile-first is the right UX choice not because it eliminates uncertainty, but because it is predictable, testable, and lower cognitive load.

**Accepted recommendations for Phase 2 (not Phase 1):**
1. Externalize profile semantic mapping rules into YAML config (not hardcoded in script)
2. Always show unmatched packs as optional — Tier 2 fills Tier 1 gaps
3. Monitor hit rates (profile-matched vs user-added) to detect stale semantic rules

**No change to Phase 1 scope** — these are Phase 2 considerations for `init_project.py`.

### Risks

1. **Agent may not call MCP correctly** — mitigated by clear instructions and fallback to profile semantics
2. **`skill-registry` MCP not available** — fallback: use profile semantics as hardcoded defaults (same as current behavior)
3. **Pack descriptions may not match semantic needs well** — mitigated by including "optional" list for user review
4. **Both tiers share description-matching uncertainty** — accepted; profile-first is chosen for predictability and testability, not accuracy. Phase 2 will externalize rules to address this.
