# Knowledge Bundle

This directory contains compiled reference material for GPT Knowledge upload.

Knowledge files should help the GPT retrieve PEtFiSh facts. They should not carry high-priority behavior rules. Behavior rules belong in `online-gpt/instructions/`.

## Upload set

Recommended upload files:

```text
01-system-overview.md
02-companion-gateway.md
03-pack-index.md
04-platform-adapters.md
05-install-command-reference.md
06-quality-gate-reference.md
07-remote-control-model.md
08-failure-playbook.md
09-skill-workbench-reference.md
10-trust-gate-reference.md
```

## Do not include

- secrets;
- tokens;
- private customer material;
- local filesystem paths unless intentionally sanitized;
- raw logs containing credentials;
- policy rules that should override instructions.

## Regeneration rule

When pack aliases, profile mapping, platform adapters, or install commands change, regenerate the relevant Knowledge file and update evals.

## Staleness handling

GPT responses should treat Knowledge as a reference snapshot. If the user asks for current release or latest branch behavior, verify against the repository or release notes before producing commands.
