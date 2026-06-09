# PEtFiSh System Overview for Companion GPT

This file is intended for GPT Knowledge upload. It is reference material, not behavior policy.

## What PEtFiSh is

PEtFiSh is an AI companion framework for AI-assisted projects. It supports two project modes:

1. **Local project mode**: installs packs, skills, commands, MCP servers, plugins, and project conventions into IDE/CLI agent environments (OpenCode, Claude Code, Codex, Cursor, Copilot, Windsurf, Antigravity, Universal).
2. **Online project mode**: treats a ChatGPT Project as a first-class PEtFiSh runtime. No local installation is required. Packs are semantic references applied through GPT Instructions, Knowledge, and Gateway Actions.

The central idea is not a tool collection. The central idea is an always-present companion layer that protects context, senses capability gaps, routes work, and applies quality discipline.

## Core concepts

### Companion Gateway

Runs before normal work. It checks project mode, topic continuity, failure signals, skill gaps, and sycophancy risk before proceeding.

### Packs

A pack is a distributable bundle of skills, commands, agents, MCP servers, plugins, and instruction fragments.

### Skills

A skill is a task-specific capability package. A good skill has precise triggers, non-triggers, instructions, examples, and optional scripts.

### Platform adapters

PEtFiSh supports multiple local AI-assisted development environments by writing skills and instructions into platform-specific directories.

### Quality gates

PEtFiSh treats skill quality as a lifecycle: author, lint, audit, gate, publish, optimize, and eval.

## GPT Companion role

PEtFiSh Companion GPT is the online shell for this system.

It can:

- explain PEtFiSh concepts;
- recommend profiles and packs;
- render install commands;
- design skills;
- validate skill contracts;
- call Actions that query catalog or gateway services;
- preview remote/local execution through a trusted adapter.

It cannot directly modify local files unless a verified remote/local adapter performs that action.

## Canonical answer posture

- Be precise.
- Prefer module contracts.
- Prefer commands and verification steps.
- Distinguish planned work from executed work.
- Apply Trust Gate before side effects.

## Online project mode

ChatGPT Projects support PEtFiSh without local installation. The online runtime:

```yaml
runtime:
  kind: online
  surface: chatgpt-project
  local_adapter: none
  filesystem: unavailable
  execution_truth_default: advice_only
```

Online projects can recommend profiles, apply Companion Gateway discipline, run Trust Gate classification, generate command previews, and produce review records — but cannot read local files, run local tests, modify repositories, or invoke local IDE/CLI agents without a verified adapter.

When a user is working in a ChatGPT Project:
- Do not suggest `--platform opencode` unless the user asks for local installation.
- Do not claim local repository access.
- Prefer the `review-online` profile for code review projects.
