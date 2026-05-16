# System Prompt Architecture

How PEtFiSh structures AI agent instructions for consistency, maintainability, and token efficiency.

---

## The Problem

Most AI agent setups put everything in a single instructions file. As projects grow, this file becomes unwieldy — thousands of lines of rules, conventions, tool usage patterns, and domain knowledge competing for the agent's attention.

PEtFiSh takes a different approach: **layered instruction injection** with on-demand loading.

---

## Architecture Overview

```text
┌─────────────────────────────────────────────┐
│  Platform System Prompt (immutable)         │
├─────────────────────────────────────────────┤
│  AGENTS.md — Project-level rules           │
│  ├── Companion Gateway (always-on)         │
│  ├── Release discipline                    │
│  ├── Python environment policy             │
│  ├── Pack-specific rules (injected)        │
│  └── Development lessons                   │
├─────────────────────────────────────────────┤
│  Skills — On-demand prompt modules         │
│  ├── SKILL.md (loaded when triggered)      │
│  ├── references/ (lazy-loaded)             │
│  └── scripts/ (executed, not loaded)       │
├─────────────────────────────────────────────┤
│  Commands & Agents — Workflow entry points  │
└─────────────────────────────────────────────┘
```

Each layer has a specific role and loading strategy.

---

## Layer 1: AGENTS.md — The Always-On Core

The `AGENTS.md` file is loaded by the platform on every interaction. It contains rules that apply to *every* task regardless of domain.

### What Goes Here

- **Companion Gateway**: The 6-step pre-processing pipeline that runs before every message
- **Cross-cutting policies**: Release discipline, Python environment rules, cross-repo protection
- **Development lessons**: Hard-won patterns from production incidents (e.g., "bash-embedded Python uses `chr()` not escape literals")
- **Pack-specific rules**: Injected via markers during pack installation

### What Doesn't Go Here

- Domain-specific workflows (use skills instead)
- Detailed API documentation (use skill references)
- One-time setup instructions (use commands)

### Design Principle: Assertive Defaults

AGENTS.md rules are written as **mandatory directives**, not suggestions:

```markdown
<!-- Good: Clear, enforceable -->
## Release Discipline (Mandatory)
- Every merge to master = one release
- Tag format: vX.Y.Z (semantic versioning)
- Forbidden: master merges without release tags

<!-- Bad: Vague, unenforced -->
## Release Guidelines
- Consider creating releases when merging to master
- Try to use semantic versioning
```

The agent treats AGENTS.md content as project law. Vague guidelines get ignored under pressure; explicit rules don't.

---

## Layer 2: Pack-Specific Rules — Injected at Install Time

When a pack is installed, its rules are injected into AGENTS.md between HTML comment markers:

```markdown
<!-- agents-rules/deploy-ops.md -->
# Repo Deployment & Operations Rules
...skill routing rules, work principles, output preferences...
<!-- /agents-rules/deploy-ops.md -->
```

### Marker-Based Injection

The install script uses HTML comment markers to:

1. **Insert** rules on first install
2. **Replace** rules on upgrade (`--force`)
3. **Remove** rules on uninstall

This keeps AGENTS.md as a single file the platform can read, while allowing modular rule management.

### Routing Tables

Each pack's rules include a mandatory **skill routing section** that tells the agent exactly which skill to use for which task:

```markdown
## Skill Routing (Mandatory)

1. User says "deploy" → MUST use repo-runtime-discovery first
2. User says "帮我部署" → MUST route to repo-service-lifecycle
3. Deployment complete → MUST verify with deployment-verifier
```

Without routing tables, the agent guesses which skill to use. With them, routing is deterministic.

### Conflict Resolution

When packs' rules overlap, each pack includes explicit conflict resolution:

```markdown
### Conflict Resolution
- When review intent AND style rewrite intent coexist →
  load BOTH anti-sycophancy-calibration AND petfish-style-rewriter
- When "help me review" context is simple proofreading →
  treat as proofreading, don't enable calibration skill
```

---

## Layer 3: Skills — On-Demand Prompt Modules

Skills are the core reusable unit. A skill is only loaded into context when the agent determines it's needed.

### Loading Trigger

The agent matches user intent against skill descriptions in the frontmatter:

```yaml
---
name: deployment-executor
description: >-
  Execute deployment/upgrade/redeployment per confirmed plan.
  Trigger for 执行发布, 切换release, 配置注入, 迁移与启动.
---
```

The `description` field is the **only** thing the agent sees before loading. If a trigger keyword isn't in the description, the skill won't fire. This is why PEtFiSh enforces [description-body trigger alignment](../developer/skill-authoring.md#activation).

### Lazy-Loaded References

Skills can include `references/` directories with detailed knowledge:

```text
skill/
├── SKILL.md           # Loaded on trigger
├── references/
│   ├── api-guide.md   # Loaded only when needed
│   └── patterns.md    # Loaded only when needed
└── scripts/
    └── deploy.py      # Executed, never loaded as context
```

The SKILL.md instructs the agent: "Read `references/api-guide.md` only when you need API details." This keeps the initial context load minimal.

### Scripts vs. References

| Asset | Loaded into context? | Purpose |
|---|---|---|
| `SKILL.md` | Yes, on trigger | Instructions for the agent |
| `references/*.md` | On demand | Detailed knowledge the agent reads when needed |
| `scripts/*.py` | No (executed) | Tools the agent runs, not reads |
| `schemas/*.json` | On demand | Validation schemas for structured output |
| `assets/*` | On demand | Templates, diagrams, static resources |

This distinction matters for token budget. A 500-line Python script used as a tool costs zero context tokens. The same content loaded as a reference would cost ~2,000 tokens.

---

## Layer 4: Commands and Agents

Commands and agents provide workflow entry points but don't add persistent context.

- **Commands**: Named shortcuts for common workflows (e.g., `/course-init`, `/course-qa`)
- **Agents**: Role-based configurations with specific tool permissions and skill loadouts

Both reference skills for their actual logic — they're routing mechanisms, not knowledge stores.

---

## Token Budget Management

PEtFiSh's architecture is designed around a finite context window. Every token of instructions competes with the user's actual work content.

### Budget Allocation

```text
Platform system prompt:     ~5,000 tokens (fixed, not controllable)
AGENTS.md core rules:       ~3,000 tokens (always loaded)
Pack-specific rules:        ~2,000 tokens (injected per installed pack)
Active skill SKILL.md:      ~1,000 tokens (loaded on demand)
Skill references:           ~500-2,000 tokens (lazy loaded)
────────────────────────────────────────────
Available for user work:    Remaining context window
```

### Strategies That Save Tokens

1. **Skill-level granularity**: Instead of one massive instructions file, knowledge is split across ~80 skills. Only the relevant 1-2 are loaded per interaction.

2. **Lazy reference loading**: Skill references are read only when the agent needs them, not upfront.

3. **Script execution over context loading**: Python scripts are tools the agent *calls*, not documents it *reads*. A 500-line lint script costs 0 tokens in context.

4. **Assertive brevity in AGENTS.md**: Rules are written as terse directives, not explanatory prose. Compare:
   ```
   # Verbose (costs tokens, adds no enforcement value)
   When working with Python environments, it's important to remember
   that this project uses uv as its package manager. Please make sure
   to use uv for all Python-related operations.

   # Terse (same enforcement, fewer tokens)
   Python environments: uv only. No pip. No bare python3 for scripts
   with dependencies.
   ```

5. **Pack-conditional loading**: Pack rules only exist in AGENTS.md if the pack is installed. A project using only `course` and `petfish` packs doesn't pay tokens for `deploy` rules.

---

## AGENTS.md as an Instruction Merge Target

PEtFiSh treats AGENTS.md as a **merge target**, not a template. Multiple packs contribute rules to the same file without overwriting each other.

### Merge Mechanism

```text
Base AGENTS.md (project-level rules)
  + companion pack rules (between markers)
  + deploy pack rules (between markers)
  + course pack rules (between markers)
  + research pack rules (between markers)
  = Final AGENTS.md
```

Each pack owns its section. Install adds it, upgrade replaces it, uninstall removes it. The rest of the file is untouched.

### Why Not Separate Files?

Most AI platforms read exactly one instructions file (`AGENTS.md`, `CLAUDE.md`, `.cursorrules`). PEtFiSh can't control the platform's file loading — so it merges everything into the single file the platform expects.

This is a pragmatic constraint, not a design preference. If platforms supported multi-file instructions, PEtFiSh would use them.

---

## Multi-Platform Adaptation

PEtFiSh supports 8 AI platforms, each with different instructions file formats:

| Platform | File | Token Sensitivity |
|---|---|---|
| OpenCode | `AGENTS.md` | Low (large context) |
| Claude Code | `CLAUDE.md` | Medium |
| Cursor | `.cursor/rules/*.mdc` | High (multiple small files) |
| GitHub Copilot | `.github/copilot-instructions.md` | High |
| Windsurf | `.windsurfrules` | Medium |

The installer adapts content for each platform:

- **Full content** for platforms with large context windows (OpenCode)
- **Condensed content** for token-limited platforms (Cursor, Copilot)
- **Platform-specific hooks** where needed (Claude Code shell hooks)

---

## Design Lessons

### 1. Description Is the Only Trigger Surface

The agent only sees skill descriptions when deciding what to load. Body content is invisible at decision time. This means:

- Every trigger keyword must appear in the description
- Description-body alignment must be enforced (PEtFiSh uses `skill-lint` for this)
- Chinese and English keywords both matter — users may use either

### 2. Rules Must Be Enforceable

Vague instructions ("try to...", "consider...") are ignored under token pressure. Effective rules are:

- **Binary**: Do X or don't do X
- **Observable**: Can be verified by checking the output
- **Consequential**: Breaking the rule has stated consequences

### 3. Lessons Belong in AGENTS.md

When a production incident reveals a non-obvious pattern, it should be captured as a rule in AGENTS.md — not left in commit messages or issue threads. PEtFiSh's AGENTS.md includes a "Development Lessons" section for exactly this purpose.

Example from a real incident:
```markdown
### bash-embedded Python: use chr() instead of escape literals
When Python code runs inside bash double-quoted strings, backslash
escaping compounds across layers. Use chr(92) for backslash, chr(47)
for forward slash. This lesson cost two patch releases (v0.11.10, v0.11.11).
```

### 4. One File, Multiple Owners

The merge-target pattern works but requires discipline:

- Each pack must own exactly one section between unique markers
- Pack rules must not reference content outside their section
- Uninstall must cleanly remove the section without side effects

---

## Further Reading

- [Companion Gateway](companion-gateway.md) — The always-on pre-processing pipeline
- [Token Cost Engineering](compaction.md) — Strategies for managing context window budget
- [Skill Authoring Guide](../developer/skill-authoring.md) — How to create effective skills
