# Source-of-Truth Policy

`online-gpt/` must track core PEtFiSh. It is not an independent semantic fork.

## Authoritative sources

The following files and directories are authoritative for PEtFiSh semantics:

```text
README.md
AGENTS.md
docs/companion-gateway.md
docs/agent-install.md
platforms.json
packs/core/**/pack-manifest.json
packs/optional/**/pack-manifest.json
packs/**/.opencode/skills/**/SKILL.md
```

When optional packs are distributed outside this repository, the authoritative source is the corresponding petfish-market registry entry and pack repository.

## Derived online-gpt files

These online-gpt files are derived or summarized from core sources:

```text
knowledge/01-system-overview.md
knowledge/02-companion-gateway.md
knowledge/03-pack-index.md
knowledge/04-platform-adapters.md
knowledge/05-install-command-reference.md
knowledge/06-quality-gate-reference.md
knowledge/08-failure-playbook.md
```

These files should not be manually changed in ways that contradict the authoritative sources.

## Online-only adapter files

These files define online adapter behavior and may contain online-specific rules, as long as they do not redefine PEtFiSh semantics:

```text
instructions/*.md
actions/openapi.yaml
gateway/*.py
gateway/modules/*.py
remote-daemon/*.md
evals/**/*.jsonl
```

Allowed online-only additions:

- execution truth labels;
- GPT answer contracts;
- GPT Actions schema;
- remote preview and approval wrappers;
- Trust Gate strengthening;
- evals that prevent drift.

Disallowed online-only changes:

- new official pack aliases;
- incompatible profile mappings;
- different install semantics;
- weakened quality gates;
- replacement Companion Gateway semantics.

## Drift prevention workflow

When enriching online-gpt:

1. identify whether the change is core semantic, derived reference, or adapter behavior;
2. if core semantic, change core PEtFiSh first;
3. if derived reference, regenerate or update Knowledge from core;
4. if adapter behavior, ensure it wraps rather than replaces core semantics;
5. add or update alignment evals.

## Sync markers

Use this marker when a file intentionally duplicates facts from core:

```text
SYNC_REQUIRED: source=<path>
```

Example:

```text
SYNC_REQUIRED: source=README.md#Profile → Auto-Install Mapping
```

A future alignment checker should scan for these markers and verify that the referenced source still exists.
