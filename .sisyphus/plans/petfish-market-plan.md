# PEtFiSh Market — GitHub-based Skill Marketplace

## Problem

PEtFiSh has 12 built-in skill packs but no way for the community to share skills. Users who create useful skills with `skill-author` have no distribution path. The existing `marketplace-connector` searches external sources (Glama, Smithery, etc.) but PEtFiSh's own ecosystem has no community contribution mechanism.

## Goal

Build a GitHub-based skill marketplace where:
1. Developers submit skills via PR to an index repo
2. Automated CI validates submissions (lint + security audit + quality gate)
3. Approved skills become discoverable via `marketplace-connector` (priority #1 source)
4. Users install community skills via existing install scripts

## Non-Goals

- No web backend or database (GitHub IS the backend)
- No paid/premium skill tier (all Apache-2.0 or compatible)
- No runtime telemetry or analytics beyond what `skill-usage-tracker` already provides locally
- No breaking changes to existing install scripts for built-in packs

## Architecture

### Index Repo: `kylecui/petfish-market`

A dedicated GitHub repo serving as the registry:

```
petfish-market/
├── index.json                    # Machine-readable skill index
├── skills/                       # Skill metadata entries (one per skill)
│   ├── community--pdf-processor.json
│   ├── community--api-tester.json
│   └── ...
├── .github/
│   └── workflows/
│       ├── validate-submission.yml   # PR validation CI
│       └── publish-index.yml         # Rebuild index.json on merge
├── CONTRIBUTING.md               # Submission guide
├── SUBMISSION_TEMPLATE.md        # PR template
└── README.md
```

### Skill Metadata Entry Format

Each `skills/*.json` file:

```json
{
  "name": "pdf-processor",
  "namespace": "community",
  "display_name": "PDF Processor",
  "description": "Extract text, tables, and metadata from PDF files",
  "version": "1.0.0",
  "author": "github-username",
  "repo": "github-username/my-pdf-skill",
  "ref": "v1.0.0",
  "path": ".opencode/skills/pdf-processor",
  "license": "Apache-2.0",
  "platforms": ["opencode", "claude"],
  "dependencies": [],
  "gate_result": {
    "decision": "PASS",
    "lint_score": 92,
    "security_risk": 0.1,
    "validated_at": "2026-05-17T12:00:00Z",
    "gate_version": "0.13.x"
  },
  "submitted_at": "2026-05-17T12:00:00Z",
  "updated_at": "2026-05-17T12:00:00Z"
}
```

### `index.json` (Auto-generated)

Aggregated from all `skills/*.json`, sorted by name. This is the file `marketplace_search.py` will query.

```json
{
  "version": 1,
  "generated_at": "2026-05-17T12:00:00Z",
  "skills": [
    { "name": "pdf-processor", "namespace": "community", ... },
    { "name": "api-tester", "namespace": "community", ... }
  ]
}
```

### CI Validation Workflow (`validate-submission.yml`)

Triggered on PRs that add/modify `skills/*.json`:

1. **Schema validation** — JSON structure, required fields, valid license
2. **Repo accessibility check** — Clone the `repo` at `ref`, verify `path` exists and contains `SKILL.md`
3. **Obtain gate tooling** — Checkout `kylecui/petfish.ai` at latest release tag to get the quality gate stack:
   - `packs/core/petfish-companion-skill/.opencode/skills/quality-gate/scripts/run_gate.py`
   - `packs/core/petfish-companion-skill/.opencode/skills/skill-lint/scripts/lint_skill.py`
   - `packs/core/petfish-companion-skill/.opencode/skills/skill-security-auditor/scripts/audit_skill.py`
   - These scripts are invoked via `uv run` with the `petfish.ai` checkout as working context
4. **Quality gate** — Run `uv run <petfish.ai-checkout>/packs/core/petfish-companion-skill/.opencode/skills/quality-gate/scripts/run_gate.py --path <cloned-skill-dir> --json`
   - Lint score ≥ 80
   - Security risk ≤ 0.5
   - No CRITICAL findings
5. **Report** — Post gate results as PR comment
6. **Auto-label** — `gate:pass`, `gate:conditional`, `gate:fail`

Human review required for merge even if CI passes (prevent malicious skills slipping through).

### Publish Workflow (`publish-index.yml`)

Triggered on push to `main`:

1. Aggregate all `skills/*.json` into `index.json`
2. Commit updated `index.json`
3. Create GitHub Release with updated index (enables CDN caching via raw.githubusercontent.com)

### Discovery Integration

Modify `marketplace_search.py` to add PEtFiSh Market as priority #1 source:

```python
# New source: PEtFiSh Market (community)
# Fetch: https://raw.githubusercontent.com/kylecui/petfish-market/main/index.json
# Cache locally for 1 hour
# Search: fuzzy match on name + description
```

Current source priority becomes:
1. **PEtFiSh Market** (community skills) ← NEW
2. PEtFiSh built-in packs (existing)
3. Glama
4. Smithery
5. SkillKit
6. anthropics/skills
7. GitHub search

### Installation Path

Community skills use a different install path from built-in packs:

```bash
# Built-in (unchanged):
/petfish install deploy

# Community (new):
/petfish install community/pdf-processor
```

Implementation: Add a `install_community_skill()` function to install scripts that:
1. Fetches skill metadata from `index.json` (or specific `skills/*.json`)
2. Clones the author's repo at the pinned `ref`
3. Copies the skill from `path` into the target project's skills directory
4. Runs a local quality gate verification (optional, configurable)

This does NOT modify the `ALL_PACKS` arrays — community skills are orthogonal to built-in packs.

## Implementation Phases

### Phase 1: Index Repo Setup
**Files changed:** None in petfish.ai repo. New repo `petfish-market` created.
- Create `kylecui/petfish-market` repo
- `index.json` schema and initial empty state
- `CONTRIBUTING.md` with submission guide
- PR template
- `validate-submission.yml` CI workflow
- `publish-index.yml` workflow
- README

**Verification:**
1. Run `gh repo view kylecui/petfish-market --json name` → confirms repo exists, returns `{"name":"petfish-market"}`
2. Run `gh api repos/kylecui/petfish-market/contents/index.json --jq '.name'` → returns `index.json`
3. Run `gh api repos/kylecui/petfish-market/contents/CONTRIBUTING.md --jq '.name'` → returns `CONTRIBUTING.md`
4. Run `gh api repos/kylecui/petfish-market/actions/workflows --jq '.workflows[].name'` → returns both `validate-submission` and `publish-index`
5. Submit a test skill PR with a valid `skills/community--test-skill.json` → CI workflow triggers, posts gate result comment, applies `gate:pass` or `gate:fail` label (verify via `gh pr view <number> --json labels`)
6. Merge test PR → `publish-index.yml` triggers, `index.json` updated (verify via `gh api repos/kylecui/petfish-market/contents/index.json` and decode content, confirm test skill present in `skills` array)
7. Submit a malformed PR (missing required fields) → CI labels `gate:fail`, PR comment explains validation errors

### Phase 2: Discovery Integration
**Files changed in petfish.ai:**
- `packs/core/petfish-companion-skill/.opencode/skills/marketplace-connector/scripts/marketplace_search.py` — add PEtFiSh Market source
- `packs/core/petfish-companion-skill/.opencode/skills/marketplace-connector/SKILL.md` — update source priority table

**Verification:**
- `/petfish search <test-skill>` returns community skill results
- Results show namespace, gate status, install command

### Phase 3: Install Support & Command Surface
**Files changed in petfish.ai:**
- `install.ps1` — add `install_community_skill` function, detect `community/` prefix in pack arg
- `install.sh` — add `install_community_skill` function, detect `community/` prefix in pack arg
- `remote-install.ps1` — add community skill install support
- `remote-install.sh` — add community skill install support
- `packs/core/petfish-companion-skill/.opencode/commands/petfish.md` — update `/petfish install` to document `community/<name>` syntax and route to installer with `--pack community/<name>`
- `packs/core/petfish-companion-skill/.opencode/skills/petfish-companion/scripts/catalog_query.py` — handle `community/` namespace in `--install` flag; fetch metadata from `index.json` and display install command

**Verification:**
1. Run `.\install.ps1 -Pack "community/test-skill" -Target . -Detect` → skill cloned from author repo, placed in `.opencode/skills/test-skill/`, `SKILL.md` present
2. Run `.\install.ps1 -Pack deploy -Target . -Detect` → existing behavior unchanged, no regression
3. Run `.\install.ps1 -Pack all -Target . -Detect` → does NOT attempt community skills (different namespace)
4. In agent session, `/petfish install community/test-skill` → returns correct install command with `community/` prefix
5. Repeat steps 1-3 with `install.sh` on Linux/WSL

### Phase 4: Documentation & Launch
**Files changed in petfish.ai:**
- `README.md` — add Market section
- `docs/agent-install.md` — community skill install guide
- `website/` — add Market page/section
- `docs/zh/README.md` — Chinese translation

**Verification:**
1. Run `Select-String -Pattern "community/" README.md` → matches found in Market section describing submission and install flow
2. Run `Select-String -Pattern "community/" docs/agent-install.md` → matches found documenting `community/<name>` install syntax
3. Run `Select-String -Pattern "community/" docs/zh/README.md` → matches found in Chinese translation with same content coverage
4. Run `Select-String -Pattern "market" website/index.html` → matches found for Market page/section link
5. Cross-check: every command shown in docs (`/petfish search`, `/petfish install community/<name>`, submission PR flow) matches the actual implementation from Phase 1-3 — no stale or invented commands

## Risks

| Risk | Mitigation |
|------|-----------|
| Malicious skill passes CI | Human review required for merge; security audit catches most patterns; pinned `ref` prevents post-merge tampering |
| Author deletes their repo after merge | `index.json` stores `ref` (git tag); could add periodic liveness checks later |
| CI running untrusted code (quality gate clones and analyzes user repos) | Gate runs in GitHub Actions sandbox; `run_gate.py` is static analysis only (no execution); repo cloned at pinned ref |
| Index grows large | JSON is compact; 1000 skills ≈ 500KB; CDN-cached via GitHub raw |
| Breaking changes to quality gate | `gate_version` field enables graceful migration |

## What Could Go Wrong

1. **Schema drift** — `index.json` schema evolves but old entries aren't migrated → Add `version` field, maintain backward compat
2. **Namespace collision** — Two authors submit same skill name → First-come-first-served; `namespace` prevents collision with built-in packs
3. **Install script complexity** — Community install path adds significant code to already-complex installers → Keep community install as a separate function, minimal coupling to existing logic
4. **Stale skills** — Community skills abandoned, become incompatible → Add `last_verified` timestamp; periodic re-validation workflow (Phase 5, future)

## Dependencies

- `run_gate.py` works standalone (confirmed — takes `--path` and `--json`)
- `lint_skill.py` works standalone (confirmed)  
- `audit_skill.py` works standalone (confirmed)
- `marketplace_search.py` already supports multiple sources with priority (confirmed)
- GitHub Actions can run `uv` (standard setup)

## Success Criteria

- A community developer can submit a skill via PR and have it validated automatically
- Users can discover community skills via `/petfish search`
- Users can install community skills via `/petfish install community/<name>`
- Built-in pack install flow is completely unaffected
- The entire system works without any backend infrastructure beyond GitHub
