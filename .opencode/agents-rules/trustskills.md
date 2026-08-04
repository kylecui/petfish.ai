# Trust Skills Governance Pack Rules

This pack provides skill trust scanning, governance level assignment, and manifest generation/verification for PEtFiSh skill packs.

## Skill Routing (强制)

### Rules

1. When the user asks to **scan skills for trust, safety, or governance issues**, **MUST** route to `skill-trust-governance`.
2. When the user asks to **generate or verify a trust manifest** for a skill or pack, **MUST** route to `skill-trust-governance`.
3. When the user asks to **assign or review governance levels**, **MUST** route to `skill-trust-governance`.
4. When the user asks to **redline** a skill (flag it as requiring manual review or denial), **MUST** route to `skill-trust-governance`.
5. Entrypoint: `uv run .opencode/skills/skill-trust-governance/scripts/trust_scan.py`. Do not invoke `trustskills` CLI directly.

### Conflict Resolution

- Trust governance vs security audit: `skill-trust-governance` handles governance classification; `skill-security-auditor` handles vulnerability scanning. Run security audit first, then governance assignment.
- "Check if a skill is safe to install" → `skill-security-auditor` for risk findings, then `skill-trust-governance` for governance decision.

## Governance Levels

| Level | Meaning | Agent Behavior |
|---|---|---|
| `allow` | Trusted, no restrictions | Execute without prompting |
| `allow_with_ask` | Trusted but requires confirmation for sensitive actions | Prompt user before sensitive operations |
| `sandbox_required` | Must run in isolated environment | Do not execute outside sandbox |
| `manual_review_required` | Flagged for human review | Block execution, notify user |
| `deny` | Rejected, must not be used | Refuse to load or execute |

## Behavioral Rules

- Never assign `allow` governance level without completing a full scan.
- Trust manifests must be regenerated whenever skill content changes. Stale manifests → `manual_review_required`.
- `deny`-level skills must not be loaded, executed, or referenced in routing rules.
- Governance decisions must be logged with: skill path, scan timestamp, findings summary, assigned level, and agent ID.
