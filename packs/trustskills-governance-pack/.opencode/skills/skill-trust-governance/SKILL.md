---
name: skill-trust-governance
description: Skill trust/governance requests: skill trust, skill安全, 治理, 可信度, trust scan, risk score, redline check, pre-publish trust verification. It wraps trustskills CLI via scripts/trust_scan.py for single-skill or root scans, manifest generation/verification, custom policy YAML, and returns governance level (allow/allow_with_ask/sandbox_required/manual_review_required/deny) with JSON-ready output.
version: 0.1.0
compatibility: opencode
---

# skill-trust-governance

## Description

`skill-trust-governance` is a governance wrapper skill for the external `trustskills` engine.

Use it to evaluate a skill pack's executable behavior rather than trusting prose alone. It supports single-skill scans, multi-skill root scans, manifest generation, manifest verification, redline checks, and governance-level reporting.

Primary entrypoint:

```bash
uv run .opencode/skills/skill-trust-governance/scripts/trust_scan.py --path <skill-dir>
```

## Triggers/Activation

Trigger this skill when the user asks for any of the following or clearly equivalent intent:

- skill trust
- skill安全
- 治理
- 可信度
- trust scan
- governance
- risk score
- redline check

Also trigger when the user wants to:

- scan one skill before publish
- batch-scan a skills root
- generate trust manifests
- verify existing manifests
- apply a custom governance policy YAML

## Workflow

1. Decide scope: single skill with `--path`, or multi-skill root with `--root`.
2. Decide mode: default scan, `--manifest` for manifest generation, or `--verify` for manifest verification.
3. Run `scripts/trust_scan.py` instead of calling the external CLI ad hoc.
4. If a custom policy is provided, pass it with `--policy`.
5. Use `--detail` for expanded output and `--output` when a Markdown report is needed.
6. Prefer `--json` when the result will be consumed by quality-gate, CI, or other automation.
7. Report the governance level, overall risk score, triggered redlines, and any required follow-up action.

## Must Do

- Use the bundled `scripts/trust_scan.py` wrapper as the default interface.
- Preserve `trustskills` as an external dependency; do not vendor or inline the engine.
- Surface the five governance levels clearly: `allow`, `allow_with_ask`, `sandbox_required`, `manual_review_required`, `deny`.
- Call out redline violations explicitly because they are hard DENY gates.
- If `trustskills` is missing, return install guidance: `uv add trustskills` or `uv pip install trustskills`.
- Use machine-readable JSON output when integrating with quality-gate or other automated checks.

## Must Not Do

- Do not copy `trustskills` source code into the project.
- Do not import `trustskills` directly inside the wrapper; invoke it through subprocess only.
- Do not hide redline violations behind a summary-only response.
- Do not hardcode absolute paths.
- Do not create commands or agents for this pack.
