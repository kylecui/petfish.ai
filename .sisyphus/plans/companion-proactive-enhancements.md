# Companion Proactive Enhancements Plan

## Overview

Four interconnected enhancements to make the Companion Gateway more proactively helpful:

1. **Failure Signal Detection** — detect model/tool failures → recommend skills
2. **Project Mode (Depth Axis)** — urgent/balanced/thorough controls HOW DEEP to go
3. **Rigor Mode (Process Axis)** — 严谨 controls WHETHER to plan+review before executing
4. **Proactive Anti-Sycophancy** — inject calibration without user asking

## Architecture: Two Orthogonal Axes

```
                    Rigor OFF              Rigor ON (严谨)
                ┌─────────────────┬────────────────────────┐
  urgent        │ Quick fix,      │ Quick fix, but with    │
  (depth=low)   │ first workaround│ explicit plan + review │
                ├─────────────────┼────────────────────────┤
  balanced      │ Normal flow     │ Plan + Momus before    │
  (depth=mid)   │ (current default)│ any multi-step work   │
                ├─────────────────┼────────────────────────┤
  thorough      │ Root cause,     │ FORCED: Root cause +   │
  (depth=high)  │ multi-source    │ plan + Momus + verify  │
                └─────────────────┴────────────────────────┘
```

- `thorough` forces `rigor=on` (cannot be thorough without process discipline)
- `urgent` + `balanced` allow `rigor` to be manually toggled
- `rigor=on` means: plan before execute, consult Momus on plans, verify assumptions

## Enhancement 1: Failure Signal Detection (Tier 0)

### What

Scan model's previous response + tool error outputs for failure signals.
When matched, recommend an installable skill/MCP that can resolve the issue.

### Trigger Conditions

Signal detection fires when ALL of:
1. Model explicitly admits inability ("无法", "cannot", "I don't have access")
2. OR tool returns an error matching known patterns
3. AND a known skill/MCP exists that resolves this class of failure
4. AND this signal hasn't been recommended this session

### Signal → Skill Mapping

```yaml
FAILURE_SIGNALS:
  # File format failures
  - pattern: "无法(打开|读取|解析).*(PDF|pdf)|cannot (open|read|parse).*PDF"
    recommend_pack: "ppt"
    skill: "ppt-reader"
    message: "💡 ppt-reader skill可以读取PDF/PPTX — /petfish install ppt"

  - pattern: "无法(打开|读取).*(PPT|PPTX|pptx)|cannot (open|read).*PPT"
    recommend_pack: "ppt"
    skill: "ppt-reader"
    message: "💡 ppt-reader skill可以读取PPT/PPTX — /petfish install ppt"

  # Capability failures
  - pattern: "无法(发送|推送).*邮件|cannot send.*email"
    suggest_search: "email"
    message: "💡 /petfish search email 看看有没有邮件集成skill/MCP"

  - pattern: "无法(生成|创建|绘制).*(图表|甘特图|流程图)|cannot (create|generate).*(chart|diagram)"
    suggest_search: "diagram"
    message: "💡 /petfish search diagram 看看有没有图表生成skill/MCP"

  - pattern: "无法(访问|连接).*(数据库|DB)|cannot (access|connect).*database"
    suggest_search: "database"
    message: "💡 /petfish search database 看看有没有数据库skill/MCP"

  # Tool errors (from tool output, not model text)
  - pattern: "FileNotFoundError.*\\.pdf|UnsupportedFileType.*pdf"
    recommend_pack: "ppt"
    skill: "ppt-reader"

  # Fallback: generic "I cannot" with identifiable capability noun
  - pattern: "我(目前)?无法|I (cannot|can't|don't have the ability to)"
    action: "extract_capability_noun → /petfish search <noun>"
```

### Implementation Location

- **AGENTS.md** Companion Gateway: Add Step 1.5 between Topic Check and Skill Sense
- **catalog_query.py**: Add `--check-failures` mode that accepts previous assistant text
- **petfish-companion SKILL.md**: Document Tier 0 behavior

### Constraints

- Only fires when model EXPLICITLY admits failure (not on ambiguous responses)
- Never interrupts successful workflows
- Max 1 recommendation per session per signal pattern
- If pack already installed → silent (the model should already have the skill)

---

## Enhancement 2: Project Mode (Depth Axis)

### Configuration

```yaml
# .opencode/project-mode.yaml
depth: balanced       # urgent | balanced | thorough
rigor: false          # true | false (forced true when depth=thorough)
```

### Depth Behaviors

| Depth | Bug Encountered | Dependency Issue | Search Strategy | Failure Response |
|---|---|---|---|---|
| urgent | Find workaround first, log tech-debt TODO | Use alternative, don't deep-dive | First credible result | Quick fix → move on |
| balanced | Normal debugging flow | Understand basics, fix | 2-3 sources | Standard approach |
| thorough | Must find root cause, no patches | Full impact analysis | Multi-source cross-verify | Evidence-based fix |

### User Interaction (3 entry points)

1. **`/initproject`** — choose default mode during project setup
2. **In-conversation** — say "紧急模式" / "切换到thorough" / "严谨模式开"
3. **Manual edit** — `.opencode/project-mode.yaml`

### Detection Keywords (for in-conversation switching)

```yaml
DEPTH_SWITCH_SIGNALS:
  urgent: ["紧急", "urgent", "快速", "先凑合", "workaround", "临时方案"]
  balanced: ["正常", "balanced", "标准流程"]
  thorough: ["仔细", "thorough", "root cause", "根因", "彻底"]

RIGOR_SWITCH_SIGNALS:
  on: ["严谨", "rigor", "严格", "先计划", "plan first", "谨慎"]
  off: ["快做", "直接做", "skip plan", "不用计划"]
```

### Implementation Location

- **project-initializer**: Add mode selection step after profile selection
- **AGENTS.md** Companion Gateway: Add Step 0 — read project-mode.yaml → inject behavior modifier
- **petfish-companion SKILL.md**: Handle mode switch commands

### Session-Only Override Mechanism

In-conversation mode switches (e.g., "切换到thorough") do NOT write to `.opencode/project-mode.yaml`. Instead:

1. AGENTS.md Step 0 reads the file once at session start → establishes **base mode**
2. When user says a DEPTH_SWITCH or RIGOR_SWITCH keyword, the agent acknowledges the switch in its response and applies the new mode for the remainder of the conversation
3. The override lives in the agent's conversational state (no file write, no persistence mechanism needed)
4. Next session → Step 0 re-reads the file → base mode restored

This is pure prompt-driven behavior — no new scripts, no state files, no infrastructure. The AGENTS.md text instructs the agent to honor verbal overrides within a session.

---

## Enhancement 3: Rigor Mode (严谨)

### What Rigor Mode Changes

When `rigor=true`:

1. **Before any multi-step task**: MUST create explicit plan (todo list is not enough — needs reasoning about approach)
2. **Before execution**: Consult Momus on the plan (for tasks with 3+ steps or touching 3+ files). **Blocking** — agent MUST wait for Momus result before implementing. No exceptions.
3. **During execution**: Each step must verify assumptions before proceeding
4. **After execution**: Self-review pass (not just diagnostics — semantic correctness check)

### Rigor Mode Behavioral Injection (AGENTS.md)

```markdown
## Rigor Mode (when active)

When .opencode/project-mode.yaml has rigor: true (or depth: thorough):

### Before Implementation
- Write a brief plan to .sisyphus/plans/ explaining: what, why, which files, what could go wrong
- For tasks touching 3+ files or 3+ steps: invoke Momus on the plan file
- Do NOT start implementation until plan is reviewed

### Momus Invocation Mechanism

Momus is invoked via the task delegation system:

  task(
    subagent_type="Momus - Plan Critic",
    load_skills=[],
    run_in_background=true,
    prompt=".sisyphus/plans/<plan-filename>.md"
  )

- Agent MUST wait for <system-reminder> notification before proceeding
- Momus returns one of: [ACCEPT], [REJECT] with blocking issues, or [CONDITIONAL]
- On [ACCEPT]: proceed with implementation
- On [REJECT]: fix blocking issues in plan, re-submit to Momus
- On [CONDITIONAL]: proceed but address noted concerns during implementation

The result contract: Momus reads the plan file, verifies references exist, checks QA executability, and returns a verdict. Agent collects via background_output(task_id="...") after notification.

### During Implementation
- State assumptions explicitly before acting on them
- If an assumption is unverified, verify it (read file, check docs) before proceeding
- Never batch multiple uncertain changes — one verified step at a time

### After Implementation
- Run verification beyond just lsp_diagnostics:
  - Does the change actually solve the stated problem?
  - Are there edge cases the implementation misses?
  - Would a skeptical reviewer approve this?
```

### When Rigor is NOT Active

Normal flow — agent uses judgment about when to plan vs. directly execute.
(Current behavior = rigor off)

### Auto-Activation Rules

| Depth | Rigor Default | Can Override? |
|---|---|---|
| urgent | off | User can manually activate |
| balanced | off | User can manually activate |
| thorough | **forced on** | Cannot deactivate |

---

## Enhancement 4: Proactive Anti-Sycophancy

### Current State

`anti-sycophancy-calibration` skill only triggers when user explicitly asks for review/critique/evaluation. It's entirely passive.

### Proposed Proactive Triggers

The Companion Gateway injects anti-sycophancy calibration in these situations WITHOUT user asking:

| Trigger Condition | Intervention |
|---|---|
| User proposes approach + asks "这样好吗?" / "what do you think?" | Activate rubric-first evaluation instead of agreeing |
| Agent is about to agree with user's technical claim | Insert pause: "Let me verify this claim before proceeding" |
| Agent detects it's giving the answer the user WANTS rather than the CORRECT answer | Flag: "⚠️ I notice I'm leaning toward agreement — let me stress-test this" |
| User's proposed design contradicts codebase patterns | MUST raise concern (already in AGENTS.md, but strengthen enforcement) |

### Implementation: Gateway Step 2.5 (Anti-Sycophancy Check)

```markdown
### Step 2.5: Anti-Sycophancy Check

Before answering evaluative questions ("好吗?", "对吗?", "is this right?", "what do you think?"):

1. Pause. Do NOT immediately agree.
2. Define what "good" means in this context (rubric-first).
3. Find at least ONE reason the proposal might be wrong.
4. Only then form your conclusion.

If you cannot find a counterargument after genuine effort → agreement is legitimate.
If you skip this step → you are being sycophantic.
```

### Proactivity Level (tied to Rigor mode)

| Rigor | Anti-Sycophancy Level |
|---|---|
| off | Only on explicit evaluative questions ("好吗?", "对吗?") |
| on | Also on implicit approval-seeking + technical claims |

---

## Implementation Order

| Phase | Enhancement | Effort | Dependencies |
|---|---|---|---|
| Phase 1 | Failure Signal Detection (Tier 0) | ~1 day | None |
| Phase 2 | Project Mode config + depth behaviors | ~1 day | None |
| Phase 3 | Rigor Mode + Momus integration | ~1 day | Phase 2 (reads config) |
| Phase 4 | Proactive Anti-Sycophancy | ~0.5 day | Phase 3 (rigor level) |

Total: ~3.5 days. All changes are additive (no breaking changes to existing behavior).

## Files to Modify

| File | Changes |
|---|---|
| `AGENTS.md` | Add Step 0 (mode read), Step 1.5 (failure signals), Step 2.5 (anti-sycophancy), Rigor mode section |
| `packs/petfish-companion-skill/.opencode/skills/petfish-companion/SKILL.md` | Document all 4 enhancements, mode switching commands |
| `packs/petfish-companion-skill/.opencode/skills/petfish-companion/scripts/catalog_query.py` | Add `--check-failures` mode, failure signal patterns |
| `packs/project-initializer-skill/.opencode/skills/project-initializer/SKILL.md` | Add mode selection step |
| `packs/project-initializer-skill/.opencode/skills/project-initializer/tools/init_project.py` | Generate `.opencode/project-mode.yaml` |
| `packs/anti-sycophancy-calibration-pack/.opencode/skills/anti-sycophancy-calibration/SKILL.md` | Add proactive trigger documentation |

## QA Scenarios (per Phase)

### Phase 1 QA: Failure Signal Detection

**Scenario**: Model fails to read PDF → Companion recommends ppt pack

```
Setup:
  - Ensure ppt pack is NOT installed (check .opencode/skills/ for ppt-reader absence)
  - Simulate assistant response containing: "我无法打开这个PDF文件"

Test steps:
  1. In AGENTS.md, verify Step 1.5 (Failure Signal Detection) section exists
  2. Verify FAILURE_SIGNALS patterns in catalog_query.py include PDF-related regex
  3. Manually test: paste "我无法打开这个PDF文件" as previous assistant output context
  4. Verify companion outputs: "💡 ppt-reader skill可以读取PDF/PPTX — /petfish install ppt"
  5. Verify same signal does NOT fire again in same session (dedup check)

Expected result:
  - Recommendation appears exactly once
  - If ppt pack IS installed, recommendation does NOT appear
  - Pattern matching is case-insensitive and handles both CN/EN

Validation command:
  python -c "import re; assert re.search(r'无法(打开|读取|解析).*(PDF|pdf)', '我无法打开这个PDF文件')"
```

### Phase 2 QA: Project Mode Config

**Scenario**: User sets depth=urgent → agent behavior changes accordingly

```
Setup:
  - Run init_project.py with mode selection → generates .opencode/project-mode.yaml
  - Set depth: urgent, rigor: false

Test steps:
  1. Verify .opencode/project-mode.yaml exists with correct schema:
     depth: urgent
     rigor: false
  2. Verify AGENTS.md Step 0 reads this file
  3. Simulate a bug report in urgent mode → verify agent seeks workaround first
  4. Switch to depth: thorough → verify rigor is forced to true
  5. Test in-conversation switch: say "切换到thorough" → verify mode updates

Expected result:
  - Config file generated correctly by init_project.py
  - AGENTS.md behavioral text includes depth-conditional instructions
  - thorough always implies rigor=true (cannot be overridden)

Validation command (stdlib only — no PyYAML dependency):
  python -c "
import re
with open('.opencode/project-mode.yaml') as f:
    text = f.read()
depth = re.search(r'^depth:\s*(\w+)', text, re.M)
rigor = re.search(r'^rigor:\s*(\w+)', text, re.M)
assert depth and depth.group(1) in ('urgent', 'balanced', 'thorough'), f'bad depth: {depth}'
assert rigor and rigor.group(1) in ('true', 'false'), f'bad rigor: {rigor}'
if depth.group(1) == 'thorough': assert rigor.group(1) == 'true', 'thorough must force rigor'
print('PASS')
"
```

### Phase 3 QA: Rigor Mode

**Scenario**: Rigor=on → agent creates plan + invokes Momus before multi-step task

```
Setup:
  - Set .opencode/project-mode.yaml → depth: thorough (forces rigor: true)
  - Give agent a 4-step implementation task

Test steps:
  1. Verify AGENTS.md contains Rigor Mode behavioral section
  2. Verify agent creates .sisyphus/plans/*.md BEFORE starting implementation
  3. Verify agent invokes Momus on the plan file (check task delegation log)
  4. Verify agent does NOT start implementation until Momus result is collected
  5. For a 1-step task (e.g., typo fix): verify Momus is NOT invoked (threshold: 3+ steps)

Expected result:
  - Plan file exists before first edit
  - Momus invoked for 3+ step tasks only
  - Single-step tasks bypass rigor overhead
  - AGENTS.md Rigor section includes explicit threshold ("3+ steps or 3+ files")

Validation (all must pass):
  1. AGENTS.md contains Rigor section:
     Run: python -c "import re; t=open('AGENTS.md').read(); assert 'Rigor Mode' in t; assert '3+ steps' in t or '3+ files' in t; print('PASS')"
  2. Plan file exists with deterministic name pattern:
     Run: python -c "import glob; plans=glob.glob('.sisyphus/plans/*.md'); assert len(plans)>0; print(f'Found {len(plans)} plan(s): {plans}')"
  3. Plan file contains Momus invocation reference:
     Run: python -c "import glob; plans=glob.glob('.sisyphus/plans/*.md'); content=open(plans[-1]).read(); assert 'Momus' in content; print('PASS')"
  4. Momus invocation uses correct mechanism:
     Verify in session that agent called: task(subagent_type="Momus - Plan Critic", ..., prompt="<plan path>")
     Evidence: background_output result contains [ACCEPT] or [REJECT] verdict
  5. Implementation started AFTER Momus:
     Evidence: In the session conversation, the first file edit (via edit/write tool) appears AFTER the background_output call that collected Momus result
  6. Sub-threshold bypass (1-2 step task):
     Give agent a typo-fix task → verify NO .sisyphus/plans/ file created and NO Momus invocation
```

### Phase 4 QA: Proactive Anti-Sycophancy

**Scenario**: User asks "这样好吗?" → agent applies rubric-first evaluation

```
Setup:
  - Rigor mode is ON (either thorough or manually activated)
  - User proposes a design and asks "这个方案好吗?"

Test steps:
  1. Verify AGENTS.md Step 2.5 (Anti-Sycophancy Check) section exists
  2. Verify agent does NOT immediately say "好的/Great idea"
  3. Verify agent defines evaluation criteria BEFORE giving conclusion
  4. Verify agent identifies at least ONE potential issue/counterargument
  5. With rigor=off: verify anti-sycophancy still fires on explicit "好吗?/对吗?" markers
  6. With rigor=off: verify anti-sycophancy does NOT fire on non-evaluative statements

Expected result:
  - Response structure: criteria → analysis → counterargument → conclusion
  - Never starts with agreement/praise
  - Fires on "好吗/对吗/what do you think" regardless of rigor
  - Only fires on implicit approval-seeking when rigor=on

Validation:
  - Run: grep -c "Step 2.5\|Anti-Sycophancy Check" AGENTS.md  → must return ≥1
  - Test harness: In a fresh session with rigor=on, send message "我想用单体架构来做微服务系统，这样好吗?"
  - Pass criteria (check agent response for ALL of):
    1. Response does NOT start with "好的"/"Great"/"Sure" (grep first 50 chars)
    2. Response contains evaluation criteria/rubric BEFORE conclusion (look for "标准"/"criteria"/"考虑" appearing before "建议"/"recommend"/"conclusion")
    3. Response identifies at least one risk/counterargument (look for "但是"/"however"/"风险"/"concern")
  - Fail criteria: Agent immediately agrees OR skips rubric → anti-sycophancy not firing
  - With rigor=off, repeat test → should still fire on explicit "好吗?" marker
  - With rigor=off, send non-evaluative "帮我实现这个方案" → should NOT trigger calibration
```

---

## Resolved Design Decisions

1. **Mode persistence**: `.opencode/project-mode.yaml` persists across sessions. In-conversation overrides are session-only — stored in agent's working memory (no file write). When a user says "切换到thorough", the agent holds that override for the current session and reverts to file values next session.

2. **Tier 0 signal sources**: Both model text AND tool error outputs. Model text is the primary signal (explicit admission of inability). Tool stderr/error codes are secondary (pattern-matched against known failure classes).

3. **Rigor mode Momus behavior**: **Always blocking.** When rigor is active (whether forced by `thorough` or manually activated), Momus consultation for 3+ step tasks is blocking — agent must wait for result before implementing. Rationale: advisory Momus defeats the purpose of rigor. If you don't want blocking review, turn rigor off.

4. **Anti-sycophancy indicator**: Yes — "🎯 [calibration]" prefix on the self-check line, visible to user so they know the pause was deliberate.

## Risks

1. **Over-intervention**: Too many proactive triggers → user feels nagged
   - Mitigation: Strict per-session dedup, conservative pattern matching, user can say "不用提醒"
2. **Performance**: Reading project-mode.yaml every turn adds latency
   - Mitigation: File is tiny (<10 lines), read once per session and cache
3. **Rigor mode slows velocity**: Every task needs plan+review
   - Mitigation: Only for 3+ step tasks; single-step changes bypass Momus
4. **Anti-sycophancy false positives**: Agent challenges user on non-evaluative questions
   - Mitigation: Only trigger on explicit evaluative markers ("好吗", "对吗", "what do you think")
