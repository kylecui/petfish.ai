# Source-of-Truth Note

This file is intended for GPT Knowledge upload.

PEtFiSh Companion GPT must treat core PEtFiSh as the source of truth.

## Core sources

Use these sources for authoritative semantics:

```text
README.md
AGENTS.md
docs/companion-gateway.md
docs/agent-install.md
platforms.json
packs/**/pack-manifest.json
packs/**/.opencode/skills/**/SKILL.md
```

## Online GPT role

The online GPT role is to adapt PEtFiSh to ChatGPT through:

- GPT instructions;
- Knowledge references;
- Actions contracts;
- Trust Gate wrappers;
- remote preview boundaries;
- evals.

It must not redefine official pack aliases, profile mappings, platform meanings, or skill lifecycle rules.

## Conflict rule

When online-gpt knowledge conflicts with core repository files, prefer the core repository files and flag the online-gpt file for synchronization.
