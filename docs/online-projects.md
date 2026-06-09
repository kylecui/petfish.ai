# PEtFiSh Online Projects

PEtFiSh supports two project modes: local and online. This document covers the online mode -- running PEtFiSh on a hosted chat surface, such as a ChatGPT Project, without local IDE/CLI tooling.

## 1. Overview

### What it is

The `online-gpt/` subsystem is PEtFiSh's GPT-native online companion runtime. It brings PEtFiSh's companion discipline, profiles, packs, skill lifecycle, quality gates, and trust boundaries into a ChatGPT-native surface. It is a first-class PEtFiSh runtime, not a reduced copy or wrapper.

The online runtime operates in three modes, prioritized by architecture:

- **P0 Standalone**: GPT Instructions + Knowledge + Answer Contracts. No external runtime.
- **P1 Gateway**: Adds PEtFiSh Online Gateway APIs via GPT Actions (catalog, profile, install, trust, skill APIs).
- **P2 Adapter**: Optional local daemon/IDE/CLI execution. Low priority.

The first release ships P0 Standalone + P1 Gateway-only Actions. P2 Adapter is boundary/regression only.

### What it is not

- Not a lightweight chatbot copy of PEtFiSh
- Not a wrapper around OpenCode, Codex, or Antigravity
- Not a replacement for local project mode
- Not dependent on any local IDE, CLI, daemon, or filesystem

### Design principle

Standalone Mode and Gateway Mode must remain useful even if Adapter Mode never ships. Online mode is a separate runtime with its own contracts, boundaries, and execution truth defaults -- not "simpler local."

## 2. Architecture

```
P0 STANDALONE (no external runtime)
============================================
  ChatGPT GPT
       |
       v
  Instructions + Knowledge + Answer Contracts
  Identity / Safety / Source-of-Truth Alignment
       |
       v
  Standalone Capabilities
  Explain | Recommend | Design | Render | Review

P1 GATEWAY (online APIs, no local tools)
============================================
  ChatGPT GPT
       |  GPT Actions
       v
  PEtFiSh Online Gateway
  Catalog | Profile | Install Render | Trust | Skill Workbench
       |
       v
  Server-Side State and Services
  Pack Index | Policy | Eval | Logs

P2 ADAPTER (optional, low priority)
============================================
  PEtFiSh Online Gateway
       |  optional
       v
  Local Daemon / Desktop Bridge
       |  optional
       v
  OpenCode / Codex / Antigravity / Shell
```

The GPT shell sits on top in all three modes. Only the capability substrate changes: from pure reasoning (P0), to online APIs (P1), to optional local execution (P2).

## 3. Capability Matrix

| Capability | P0 Standalone | P1 Gateway | P2 Adapter |
|---|---|---|---|
| Explain PEtFiSh and Companion Gateway | yes | yes | yes |
| Recommend profiles and packs | yes | yes | yes |
| Design skills, triggers, and non-triggers | yes | yes | yes |
| Render install/upgrade/uninstall commands | yes | yes | yes |
| Produce test plans and quality-gate plans | yes | yes | yes |
| Critical review and anti-sycophancy | yes | yes | yes |
| Source-of-truth alignment checks | yes | yes | yes |
| Live catalog search | no | yes | yes |
| Profile suggestion (online) | no | yes | yes |
| Pack resolution via API | no | yes | yes |
| Trust Gate classification (online) | no | yes | yes |
| Skill contract rendering (API) | no | yes | yes |
| Deterministic routing | no | yes | yes |
| Local workspace preview | no | no | yes |
| Local execution (test, build, deploy) | no | no | optional |
| Requires local IDE/CLI agent | no | no | only selected adapter |

## 4. What Online Projects Can Do

### In P0 Standalone Mode

- Explain PEtFiSh concepts, Companion Gateway flow, profiles, and packs
- Recommend the right profile and pack combination for a given task
- Design new skills, including trigger phrases, non-triggers, and boundaries
- Produce install, upgrade, and uninstall commands for any supported platform
- Generate test plans and quality-gate evaluation plans
- Perform critical review with anti-sycophancy calibration
- Verify alignment with core PEtFiSh source of truth
- Apply Companion Gateway discipline: mode read, topic check, failure signal detection, skill sense, anti-sycophancy check
- Run Trust Gate classification on proposed changes or actions
- Produce review policies, structured review comments, and decision records

### In P1 Gateway Mode (additional)

- Search the PEtFiSh catalog for packs, skills, MCP servers, and plugins
- Resolve pack dependencies and render platform-specific install commands from live data
- Classify action risk via the Trust Gate API
- Render skill contracts with validated schema
- Preview command shapes without side effects (dry-run)

## 5. What Online Projects Cannot Do

By default, an online project cannot:

- Read local files that were not uploaded or pasted by the user
- Run local tests, builds, or lint checks
- Modify repositories (commit, branch, merge, rebase)
- Invoke local IDE or CLI agents (OpenCode, Codex, Cursor, etc.)
- Push, deploy, or publish artifacts
- Access the local filesystem or shell

These actions require a verified adapter result (P2 Adapter Mode). The GPT must never claim local state changed unless an adapter returned a confirmed execution result.

### Execution Truth Levels

| Level | Side Effect | Available In |
|---|---|---|
| `advice_only` | none | P0, P1, P2 |
| `command_rendered` | none -- user runs locally | P0, P1, P2 |
| `dry_run` | none -- gateway validated shape | P1, P2 |
| `previewed` | none -- preview result only | P1, P2 |
| `executed` | confirmed by adapter result | P2 only |
| `audit_logged` | durable audit trace exists | P2 only |

Standalone and Gateway Mode normally operate at `advice_only`, `command_rendered`, or `dry_run`.

## 6. Profile: review-online

The `review-online` profile is designed for code review workflows in a ChatGPT Project. It assumes no local filesystem, no IDE/CLI adapter, and no repository access unless the user uploads or pastes context.

```yaml
profile: review-online
name: Online Code Review
runtime: online
surface: chatgpt-project
base_profile: security

packs:
  core:
    - companion
    - context
    - petfish
    - testdocs
    - trust
  optional:
    - calibrate
    - deploy

default_execution_truth: advice_only

review_dimensions:
  - correctness
  - security
  - tests
  - maintainability
  - architecture
  - release_risk
  - missing_evidence

gateway_policy:
  topic_check: strict_per_pr
  anti_sycophancy: required_for_approval
  failure_signal_detection: enabled
  skill_sense: enabled
  trust_gate: enabled_for_risky_changes

non_goals:
  - local test execution
  - repository mutation
  - git operations
  - deployment
  - publishing
  - hidden remote execution
```

### Pack responsibilities under review-online

| Pack | Role |
|---|---|
| companion | Lightweight Companion Gateway before substantive review work |
| context | Isolate PRs, modules, topics, and review threads |
| petfish | Keep review writing precise and actionable |
| testdocs | Reason about tests, coverage, usage docs, and acceptance cases |
| trust | Classify risky changes, side effects, and policy boundaries |
| calibrate | Avoid rubber-stamping and overconfident approvals |
| deploy | Only if review covers CI/CD, Docker, or release (optional) |

### Review output format

```
Verdict:
Blocking issues:
Non-blocking issues:
Test gaps:
Risk classification:
Suggested review comments:
Evidence needed before approval:
```

Before approving a change, the GPT identifies at least one serious counterargument, failure mode, or missing-evidence scenario. This is the anti-sycophancy rule enforced by the `calibrate` pack.

## 7. Surface Compatibility

The online runtime targets ChatGPT Projects. Key behavioral notes:

- **Project Instructions are natural language**, not YAML. The GPT consumes the profile as a natural-language policy description. YAML is produced only when the user explicitly asks for it.
- **Knowledge files are reference material** loaded into the GPT's knowledge retrieval. Behavioral rules live in Instructions. Knowledge provides factual grounding.
- **GPT Actions are optional**. The GPT works in Standalone Mode without any Actions configured. Gateway Mode adds Actions for catalog, profile, install, trust, and skill APIs.
- **No local adapter required**. The GPT does not assume it can read files, run commands, or access the network beyond configured Actions.
- **The GPT is the runtime**. All Companion Gateway steps (mode read, topic check, failure signal detection, skill sense, anti-sycophancy check) execute as instruction-following behavior within the GPT, not as external tool calls.

### Two skillsets

The online GPT carries two skillsets drawn from PEtFiSh's core:

**Companion skillset**: gateway step execution, 3-tier capability sensing, `/petfish` command handling, fish-market cross-source search.

**fish-\* classic skillset**: fish-trail topic governance (context isolation, contamination scoring), fish-brain orchestration and routing, fish-market marketplace search.

## 8. When to Use Online vs Local

| Scenario | Mode | Reason |
|---|---|---|
| Install PEtFiSh in an IDE/CLI environment | Local | Requires filesystem and platform adapter |
| Review code without local repo access | Online | Works from uploaded diffs and pasted context |
| Run a quality gate on a skill | Local | Requires lint scripts, security audit, metadata validation |
| Deploy a service | Local | Requires host access, build toolchain, runtime control |
| Design a skill contract | Either | Both modes can reason about trigger design and boundaries |
| Classify risk of a change | Either | Trust Gate runs locally or via Gateway API |
| Search the PEtFiSh catalog | Online (Gateway) | Live catalog search via Gateway API; local mode uses installed data |
| Produce install commands for a team | Online | Renders commands without needing the target platform locally |
| Apply Companion Gateway discipline to a conversation | Online | GPT Instructions enforce gateway steps before every response |

**Decision heuristic**: if the task requires filesystem access, build toolchains, or runtime control, use local mode. If the task is reasoning-heavy and the user can provide context through uploads or pastes, online mode is a better fit.

## 9. Getting Started

### Setting up a ChatGPT Project for code review

1. Create a new ChatGPT Project.
2. Add the Project Instructions from `online-gpt/project-instructions/code-review.md`.
3. Upload PEtFiSh Knowledge files as project knowledge (the GPT references them for factual grounding).
4. (Optional) Configure GPT Actions using the Gateway OpenAPI spec at `online-gpt/actions/openapi.gateway-only.yaml` to enable live catalog search and Trust Gate classification.

### Using the online GPT

Once configured, the GPT applies Companion Gateway discipline automatically:

- It runs mode read, topic check, failure signal detection, skill sense, and anti-sycophancy check before substantive responses.
- It classifies all output using execution truth levels (default: `advice_only`).
- It renders install commands, profile recommendations, and skill designs on request.
- It refuses to claim local state changes without verified adapter results.

### No installation required

Online mode requires no `install.ps1`, no `install.sh`, no uv, and no Python environment. Packs are referenced semantically -- the GPT applies their discipline through Instructions, Knowledge, and Gateway Actions.

---

## Further Reading

- [online-gpt/README.md](../online-gpt/README.md) -- internal/developer documentation for the online subsystem
- [online-gpt/ARCHITECTURE.md](../online-gpt/ARCHITECTURE.md) -- full architecture with layer model, module contracts, and rules
- [online-gpt/OPERATING-MODES.md](../online-gpt/OPERATING-MODES.md) -- detailed operating mode contracts and dependency rules
- [docs/companion-gateway.md](companion-gateway.md) -- Companion Gateway step-by-step flow
- [docs/agent-install.md](agent-install.md) -- local project mode installation
