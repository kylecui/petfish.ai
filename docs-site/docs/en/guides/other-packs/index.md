# Other Packs Guide

This guide covers the remaining PEtFiSh skill packs that don't warrant a full dedicated guide but are still powerful tools in the right context.

---

## PPT Pack

**Alias:** `ppt` | **Skills:** 2 (`ppt-reader`, `ppt-writer`)

The PPT pack reads, audits, and generates PowerPoint decks programmatically. It bridges the gap between structured Markdown content and polished slide decks.

### Install

=== "Windows PowerShell"

    ```powershell
    & ([scriptblock]::Create((irm https://raw.githubusercontent.com/kylecui/petfish.ai/master/remote-install.ps1))) -Pack ppt
    ```

=== "macOS / Linux / WSL"

    ```bash
    curl -fsSL https://raw.githubusercontent.com/kylecui/petfish.ai/master/remote-install.sh | bash -s -- --pack ppt
    ```

### What It Does

| Skill | Purpose |
|---|---|
| `ppt-reader` | Extract slide inventory, notes, comments, media links, and structure from existing PPTX files |
| `ppt-writer` | Generate new decks from Markdown/documents, apply templates, run visual QA |

### When to Use

- Converting course content or research reports into presentation slides
- Auditing existing decks for consistency, sensitive info, or structural problems
- Generating slide decks from structured Markdown notes or meeting minutes
- Unifying slide templates across a deck

### Workflow

```text
ppt-reader (audit existing deck)
    → produce rewrite brief
    → ppt-writer (generate new deck)
    → ppt-writer qa_deck (visual QA)
    → fix issues → re-verify
```

### Example Prompts

```text
Read this PPTX and give me a slide inventory with notes and structure.
```

```text
Generate a 15-slide deck from docs/02-content/module-01.md using our corporate template.
```

!!! tip "Iterative QA Loop"
    The `ppt-writer` skill uses a generate → QA → fix → re-verify cycle. Don't expect a perfect deck on the first pass. The QA step catches layout issues, missing content, and template violations.

---

## Calibrate Pack

**Alias:** `calibrate` | **Skills:** 2 (`anti-sycophancy-calibration`, `council-thinking`)

The Calibrate pack prevents the AI from blindly agreeing with you and enhances decision robustness through adversarial reasoning. It injects structured evaluation discipline into any judgment-heavy task.

### Install

=== "Windows PowerShell"

    ```powershell
    & ([scriptblock]::Create((irm https://raw.githubusercontent.com/kylecui/petfish.ai/master/remote-install.ps1))) -Pack calibrate
    ```

=== "macOS / Linux / WSL"

    ```bash
    curl -fsSL https://raw.githubusercontent.com/kylecui/petfish.ai/master/remote-install.sh | bash -s -- --pack calibrate
    ```

### What It Does

The `anti-sycophancy-calibration` skill activates whenever you ask for reviews, critiques, evaluations, or decisions. It forces the AI to:

1. **Neutralize leading prompts** — strip out your implied preferred answer before evaluating
2. **Define rubrics first** — establish what "good" means before saying whether something is good
3. **Find counter-arguments** — identify at least one reason the proposal might be wrong
4. **Separate conclusion from confidence** — state both what it thinks AND how sure it is

The `council-thinking` skill provides multi-perspective adversarial reasoning using a 5+1 model:

1. **Perspective 1 (Support)** — What arguments support this proposal?
2. **Perspective 2 (Oppose)** — What arguments oppose it?
3. **Perspective 3 (Practical)** — What are the implementation challenges?
4. **Perspective 4 (Conservative)** — What risks could sink this?
5. **Perspective 5 (Innovative)** — What alternatives or improvements exist?
6. **Perspective 6 (Synthesis)** — Integrated judgment with confidence levels

This 5+1 model exposes blind spots, examines hidden assumptions, and strengthens decision robustness for high-stakes judgments like strategic decisions, architecture reviews, product planning, and technology selection.

### When to Use

- Code reviews ("Is this architecture correct?")
- Proposal critiques ("What do you think of this plan?")
- Design reviews ("Is this UI good?")
- Strategic decisions ("Should we proceed with this?")
- Any time you catch yourself wanting the AI to validate your existing belief

### Example Prompts

```text
Review this architecture proposal and tell me if it's production-ready.
```

```text
Is my approach to error handling correct here?
```

```text
Use council-thinking to evaluate this strategic decision: should we migrate to microservices?
```

!!! warning "It Won't Flatter You"
    The whole point is to get honest feedback. If you ask "Is this good?" and the answer is "No, here's why," that's the skill working correctly. Don't disable it because you don't like the answer.

### Combination Patterns

The calibrate pack works well when combined with other skills:

- `course-outline-design` + `anti-sycophancy-calibration` → Prevents course outlines from just confirming your initial vision
- `research-report-writer` + `anti-sycophancy-calibration` → Forces the report to acknowledge opposing evidence
- `decision-recommendation` + `anti-sycophancy-calibration` → Ensures recommendations aren't just echoing your preference
- `product-opportunity-mapper` + `council-thinking` → Multi-perspective evaluation of opportunity strength and risks
- `planning-roadmap-developer` + `council-thinking` → Strategic roadmap stress-tested through adversarial perspectives

---

## Petfish Style Pack

**Alias:** `petfish` | **Skills:** 1 (`petfish-style-rewriter`)

The Petfish Style pack rewrites text into a clear, structured, engineering-oriented voice. It removes AI slop, internet cliches, and rhetorical fluff.

### Install

=== "Windows PowerShell"

    ```powershell
    & ([scriptblock]::Create((irm https://raw.githubusercontent.com/kylecui/petfish.ai/master/remote-install.ps1))) -Pack petfish
    ```

=== "macOS / Linux / WSL"

    ```bash
    curl -fsSL https://raw.githubusercontent.com/kylecui/petfish.ai/master/remote-install.sh | bash -s -- --pack petfish
    ```

### What It Does

Rewrites Chinese or English content (technical docs, proposals, patents, emails, course materials) into the Petfish writing style:

- **Structured** — clear total-part-total organization
- **Concise** — no filler, no hedging, no "it's important to note"
- **Evidence-based** — claims backed by data, not rhetoric
- **Engineering-oriented** — problem-driven analysis, not narrative fluff

### When to Use

- Polishing technical documentation
- De-AI-ing generated text (removing "delve", "it's worth noting", "in conclusion")
- Rewriting proposals to be more direct and actionable
- Converting verbose academic writing into sharp engineering prose

### Example Prompts

```text
用我的语言习惯表达：[paste text]
```

```text
去AI味，按工程化风格重写这段：[paste text]
```

```text
Make this sound human but still professional: [paste text]
```

### What Gets Removed

| AI Slop Pattern | Replacement |
|---|---|
| "It's important to note that..." | (deleted, or replaced with direct statement) |
| "Delving into the intricacies of..." | State the point directly |
| "In today's rapidly evolving landscape..." | (deleted) |
| "This comprehensive guide will..." | (deleted, just start the guide) |
| Unnecessary conclusions restating the intro | (deleted) |

---

## TestDocs Pack

**Alias:** `testdocs` | **Skills:** 2 (`generate-test-cases`, `generate-usage-docs`)

The TestDocs pack generates test cases and usage documentation grounded in actual repository code, not generic templates.

### Install

=== "Windows PowerShell"

    ```powershell
    & ([scriptblock]::Create((irm https://raw.githubusercontent.com/kylecui/petfish.ai/master/remote-install.ps1))) -Pack testdocs
    ```

=== "macOS / Linux / WSL"

    ```bash
    curl -fsSL https://raw.githubusercontent.com/kylecui/petfish.ai/master/remote-install.sh | bash -s -- --pack testdocs
    ```

### What It Does

| Skill | Purpose |
|---|---|
| `generate-test-cases` | Produce test matrices (smoke, regression, boundary, negative) from actual code and design docs |
| `generate-usage-docs` | Generate README, Quick Start, API docs, troubleshooting guides from the codebase |

### When to Use

- After implementing a feature and needing test coverage
- When onboarding documentation is missing or outdated
- When you need to generate API/CLI/SDK documentation from source
- When preparing for a release and need coverage gap analysis

### Example Prompts

```text
Generate test cases for the authentication module. Include boundary and negative tests.
```

```text
Generate a Quick Start guide and API reference from the current codebase.
```

!!! tip "Grounded, Not Generic"
    These skills read your actual code before generating output. The test cases reference real function signatures, the docs reference real CLI flags. They are not generic templates — they are project-specific artifacts.

---

## Context Pack

**Alias:** `context` | **Skills:** 1 (`fish-trail`) | **MCP Server:** `context-state`

The Context pack provides topic governance — it prevents cross-topic contamination when you switch between unrelated tasks in the same session.

### Install

=== "Windows PowerShell"

    ```powershell
    & ([scriptblock]::Create((irm https://raw.githubusercontent.com/kylecui/petfish.ai/master/remote-install.ps1))) -Pack context
    ```

=== "macOS / Linux / WSL"

    ```bash
    curl -fsSL https://raw.githubusercontent.com/kylecui/petfish.ai/master/remote-install.sh | bash -s -- --pack context
    ```

### What It Does

The `fish-trail` skill and its `context-state` MCP server maintain a topic graph that tracks what you're working on and detects when context is drifting or getting polluted.

**Key capabilities:**

- **Topic detection** — classifies each message's relationship to the active topic
- **Contamination scoring** — quantifies risk of cross-topic pollution
- **Context packages** — builds isolated context bundles per topic
- **Session management** — tracks which sessions worked on which topics
- **Topic routing** — routes queries to the most relevant topic with a context firewall

### When to Use

- Working on multiple unrelated projects in the same AI session
- Long-running sessions where context accumulates and drifts
- Handoffs between sessions (the context package preserves state)
- When you notice the AI confusing details from different tasks

### How It Works (Always-On)

When installed, fish-trail runs automatically as part of the Companion Gateway:

1. **Every message** → `topic_detect` classifies the relationship (continue/fork/switch/merge/archive/reset)
2. **Low risk (0-30)** → silent, no interruption
3. **Medium risk (31-60)** → brief note about context inheritance
4. **High risk (61-100)** → pauses and suggests fork/switch/reset

### Example Interactions

```text
User: "Let's switch to the billing feature now"
Agent: [topic_detect → switch detected, risk=72]
       "I detect a topic switch from 'auth-module' to 'billing-feature'.
        Suggesting a fork to preserve auth context separately.
        Should I fork, switch, or continue in the current topic?"
```

```text
User: "整理一下话题"
Agent: [loads fish-trail skill for deep governance]
       Shows topic graph, recommends archiving stale topics,
       and builds fresh context packages for active ones.
```

### MCP Tools Available

The `context-state` MCP server exposes 30+ tools for programmatic topic management:

| Tool Category | Examples |
|---|---|
| Topic CRUD | `topic_create`, `topic_update`, `topic_archive`, `topic_search` |
| Relationships | `topic_link`, `topic_unlink`, `topic_graph`, `topic_recommend` |
| Context | `context_build`, `context_freeze`, `context_export` |
| Contamination | `contamination_score`, `contamination_explain` |
| Sessions | `session_bind`, `session_resume`, `session_query`, `session_agents` |
| Routing | `topic_route`, `topic_detect`, `topic_report` |

!!! tip "Best With Long Sessions"
    The context pack shines in sessions lasting hours or spanning multiple days. For quick one-off tasks, the overhead isn't worth it. But for sustained development work across multiple features, it prevents the subtle context bleed that causes bugs.

---

## Pack Comparison Matrix

| Pack | Skills | Primary Use Case | Effort Level |
|---|---|---|---|
| `ppt` | 2 | Slide generation and audit | Medium |
| `calibrate` | 2 | Judgment calibration and adversarial reasoning | Low (always-on) |
| `petfish` | 1 | Writing style enforcement | Low |
| `testdocs` | 2 | Test cases and docs from code | Medium |
| `context` | 1 + MCP | Topic isolation and governance | Low (always-on) |

### Which to Install?

- **Everyone** should install `petfish` (writing quality) and `calibrate` (honest feedback)
- **Developers** should add `testdocs` (test coverage) and `context` (long sessions)
- **Presenters** should add `ppt` (slide generation)
- **Or just use a profile**: `comprehensive` installs everything
