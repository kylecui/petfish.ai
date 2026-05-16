# Quality Gate Pipeline

The Quality Gate is PEtFiSh's publish decision system. It runs three checks in sequence — lint, security audit, and metadata validation — then outputs a PASS, CONDITIONAL, or FAIL decision.

---

## Overview

```text
skill/
  │
  ├─ 1. Lint
  │    └─ Score ≥ 80/100
  │
  ├─ 2. Security Audit
  │    └─ Risk ≤ 0.5 and no CRITICAL
  │
  ├─ 3. Metadata Validation
  │    └─ Name, version, description valid
  │
  └─ 4. Decision
       ├─ PASS         → Ready to publish
       ├─ CONDITIONAL   → Proceed with noted concerns
       └─ FAIL          → Must fix before publishing
```

---

## Running the Gate

### Via /petfish

```bash
/petfish gate .opencode/skills/my-skill/
```

### Via Script

```bash
# Single skill
uv run python .opencode/skills/quality-gate/scripts/run_gate.py \
  --path .opencode/skills/my-skill/

# Recursive — all skills in a directory
uv run python .opencode/skills/quality-gate/scripts/run_gate.py \
  --path .opencode/skills/ --recursive
```

---

## Stage 1: Lint

Runs `lint_skill.py` to check structure, formatting, and trigger reliability.

### What It Checks

| Check | Rule | Severity |
|---|---|---|
| Frontmatter fields | `name`, `version`, `description` present | ERROR |
| Name format | Lowercase kebab-case, matches directory | ERROR |
| Description length | ≤500 characters | WARNING |
| Trigger coverage | Description covers ≥80% of body trigger keywords | ERROR (<50%), WARNING (50–80%) |
| File structure | SKILL.md exists at expected path | ERROR |
| Script conventions | No `pip install`, no bare `python3` | WARNING |

### Scoring

Each rule contributes to a 0–100 score. The gate requires **≥80** to pass this stage.

### Running Lint Standalone

```bash
/petfish lint .opencode/skills/my-skill/

# Or directly:
uv run python .opencode/skills/skill-lint/scripts/lint_skill.py \
  --path .opencode/skills/my-skill/

# JSON output for CI:
uv run python .opencode/skills/skill-lint/scripts/lint_skill.py \
  --path .opencode/skills/my-skill/ --json
```

---

## Stage 2: Security Audit

Runs `audit_skill.py` to scan for security risks.

### What It Scans

| Area | Examples |
|---|---|
| SKILL.md instructions | Prompt injection vectors, credential access patterns |
| `scripts/` | Dangerous commands (`rm -rf`, `eval`), network access, file writes outside scope |
| `references/` | Embedded secrets, hardcoded tokens |
| MCP/tool scope | Excessive permissions, unscoped tool access |

### Risk Score

Outputs a 0.0–1.0 risk score. The gate requires **≤0.5** and **no CRITICAL findings**.

| Score Range | Meaning |
|---|---|
| 0.0–0.2 | Low risk |
| 0.2–0.5 | Moderate risk — review recommended |
| 0.5–0.8 | High risk — likely blocked |
| 0.8–1.0 | Critical risk — must remediate |

### Running Audit Standalone

```bash
/petfish audit .opencode/skills/my-skill/

# Or directly:
uv run python .opencode/skills/skill-security-auditor/scripts/audit_skill.py \
  --path .opencode/skills/my-skill/
```

---

## Stage 3: Metadata Validation

Validates pack-level metadata if the skill belongs to a pack:

- `name` field matches directory name
- `version` follows semver
- `description` is present and non-empty
- Pack manifest (if exists) lists the skill

---

## Decision Logic

| Condition | Decision |
|---|---|
| Lint ≥80 AND audit ≤0.5 AND no CRITICAL AND metadata valid | **PASS** |
| Lint ≥60 AND audit ≤0.7 AND trigger-coverage ERROR exists | **CONDITIONAL** |
| Lint <60 OR audit >0.7 OR CRITICAL finding | **FAIL** |

### CONDITIONAL Handling

A CONDITIONAL result means minor issues exist but aren't blocking. Common causes:

- Trigger coverage between 50–80% (WARNING level)
- Moderate security risk (0.2–0.5)
- Missing optional fields

You may proceed but should address the noted concerns.

---

## CI Integration

The gate scripts support JSON output for CI pipelines:

```bash
# Returns exit code 0 for PASS, 1 for CONDITIONAL, 2 for FAIL
uv run python .opencode/skills/quality-gate/scripts/run_gate.py \
  --path .opencode/skills/my-skill/ --json
```

### Batch Gating

Gate all skills in a pack before release:

```bash
uv run python .opencode/skills/quality-gate/scripts/run_gate.py \
  --path packs/my-pack/.opencode/skills/ --recursive
```

---

## Fixing Common Failures

### Trigger Coverage Too Low

```
ERROR: trigger-coverage 35% (threshold: 50%)
```

**Fix**: Add missing trigger keywords from the body's activation section into the frontmatter `description`. Both Chinese and English keywords must be covered.

### Lint Score Below 80

Review the detailed rule violations in the lint output. Most common issues:

- Missing `version` field
- Description over 500 characters
- Directory name doesn't match `name` field

### Security Audit Flags

Review each finding. Common false positives:

- Network access in scripts that legitimately need it (e.g., API clients)
- File write operations that are part of the skill's core function

For legitimate operations, document the justification. For real risks, remediate.
