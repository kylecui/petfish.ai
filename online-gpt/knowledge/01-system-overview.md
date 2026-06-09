# PEtFiSh System Overview for Companion GPT

This file is intended for GPT Knowledge upload. It is reference material, not behavior policy.

## What PEtFiSh is

PEtFiSh is an AI companion framework for AI-assisted projects. It installs packs, skills, commands, MCP servers, plugins, and project conventions into local agent environments.

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
