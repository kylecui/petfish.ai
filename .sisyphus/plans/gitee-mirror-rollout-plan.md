# Gitee Mirror Rollout Plan for petfish.ai

## 1. Goal

Introduce a China-accessible Gitee mirror strategy that improves one-line install and upgrade reliability **without changing GitHub as the single source of truth**.

Primary outcomes:

1. Keep GitHub as the only authoritative source for development, merge, tags, releases, and version truth.
2. Add Gitee as a **read-only fallback distribution source** for domestic network conditions.
3. Preserve the current release discipline: merge to `master` => immediate GitHub Release.
4. Avoid double-latest / double-release ambiguity.
5. Make the rollout incremental, testable, and reversible.

---

## 2. Problem Statement

Current installer paths depend heavily on GitHub raw/archive access and third-party GitHub proxy mirrors (`ghfast`, `ghproxy`). This creates reliability risk for users in China when:

- `raw.githubusercontent.com` is slow or inaccessible
- GitHub archive/release downloads are unstable
- third-party proxy services are degraded

The project requirement is stronger than “nice-to-have performance”:

> Users using one-line install or upgrade should be able to install or migrate successfully to the latest version.

The current architecture already contains fallback logic, but it is still **GitHub-centric** and not backed by a true second origin under project control.

---

## 3. Scope

### In Scope

- Main repo mirror strategy for `petfish.ai`
- `petfish-market` mirror strategy for market index availability
- Installer source resolution design for GitHub → proxy → Gitee fallback
- Release workflow extension for mirror sync/check
- Smoke-test and verification plan
- Future-ready market schema additions to support mirrored optional pack repos

### Out of Scope (for initial rollout)

- Migrating source-of-truth from GitHub to Gitee
- Treating Gitee as a second release authority
- Replacing GitHub Releases with Gitee release attachments
- Mirroring all optional pack repos in phase 1
- Reworking the whole installer architecture beyond source resolution abstraction

---

## 4. Constraints and Non-Negotiables

1. **GitHub remains source of truth.**
   - Development, PRs, merge, tags, releases all remain on GitHub.
2. **No dual truth for latest version.**
   - “Latest” is determined by GitHub release/tag state only.
3. **Release discipline remains unchanged.**
   - `master` merges must immediately result in a GitHub Release.
4. **Installer behavior must stay deterministic.**
   - Gitee is fallback, not an alternate version authority.
5. **No unsafe assumption that Gitee release asset URLs are stable.**
   - Plan around raw files + archive endpoints, not signed release attachment links.
6. **Changes must be incremental and reversible.**

---

## 5. Evidence and Current-State Findings

### 5.1 Current installer architecture touchpoints

Based on repo inspection, current mirror-related logic is distributed across four installer entrypoints:

- `install.sh`
- `remote-install.sh`
- `install.ps1`
- `remote-install.ps1`

Key current behaviors:

1. **Market index is hard-coded to GitHub raw**
   - `install.sh` `query_market_index()` → `https://raw.githubusercontent.com/kylecui/petfish-market/main/index.json`
   - `remote-install.sh` `query_market_index()` uses the same path
   - `install.ps1` / `remote-install.ps1` `Get-MarketIndexData()` use the same path

2. **Current fallback chain already includes GitHub proxy mirrors**
   - `ghfast.top`
   - `mirror.ghproxy.com`

3. **Market pack downloads are GitHub archive-based**
   - Bash installs use GitHub tarball/archive download paths
   - PowerShell installs use GitHub zip archive download paths

4. **There is no unified source resolver yet**
   - URL construction and fallback behavior are duplicated across installer files
   - Market index and market pack archive download use different but related code paths

5. **Remote-installers are especially sensitive**
   - `remote-install.sh` is designed to be piped from GitHub raw URL
   - `remote-install.ps1` is designed to be evaluated from raw URL

### 5.2 Current release automation state

The current workflow directory contains:

- `.github/workflows/ci.yml`
- `.github/workflows/docs.yml`
- `.github/workflows/petfish-eval.yml`
- `.github/workflows/website.yml`

Observed gap:

- There is currently **no dedicated Gitee mirror sync workflow**
- There is currently **no post-release mirror verification workflow**

### 5.3 External constraints from Gitee research

Confirmed planning-relevant facts:

1. Gitee supports repo mirroring/import and can act as a synced mirror target.
2. Gitee raw file access is viable for direct script fetching.
3. Gitee release attachments are not ideal as stable installer download links because attachment download URLs are signed/time-limited.
4. Therefore the safe planning assumption is:
   - Use **Gitee raw** for install scripts and market index.
   - Use **archive/tag endpoints** for mirrored repo content where needed.
   - Do **not** make Gitee release attachments part of the core installer contract.

---

## 6. Decision

### Recommended Architecture

Adopt a **single-truth, dual-source distribution model**:

- **Truth layer:** GitHub only
- **Delivery layer:** GitHub primary + GitHub proxy mirrors + Gitee fallback

This means:

- Version resolution remains GitHub-defined.
- Download source resolution may fall back to Gitee when GitHub-origin paths fail.

### Explicitly rejected architecture

Do **not** adopt “GitHub + Gitee dual-primary release management”.

Reasons:

- introduces dual latest semantics
- increases release drift risk
- complicates debugging and support
- forces double governance on tags/releases

---

## 7. Rollout Phases

## Phase 1 — Minimal Reliable Fallback (recommended first implementation)

### Objective

Improve reliability of the two most critical access paths:

1. remote installer script fetch
2. `petfish-market/index.json` fetch

### Deliverables

1. Create/maintain Gitee mirrors for:
   - `petfish.ai`
   - `petfish-market`
2. Extend installer source lists so raw/index retrieval can fall back to Gitee.
3. Add post-release mirror sync/check automation.
4. Add smoke tests for one-line install using mirrored raw script path.

### Why this phase first

This phase delivers the highest reliability gain with the smallest blast radius. It improves the install entry chain without immediately needing to mirror every optional pack repo.

### Code areas expected to be touched in implementation

- `remote-install.sh`
- `remote-install.ps1`
- `install.sh`
- `install.ps1`
- likely one new workflow file under `.github/workflows/`
- possibly docs/install docs if user-visible fallback policy needs mention

### Acceptance criteria

1. Gitee raw URLs for `remote-install.sh` and `remote-install.ps1` are accessible.
2. Installer market-index lookup can fall back to Gitee when GitHub raw and proxies fail.
3. Release pipeline can confirm mirrored content is available after GitHub release.
4. One-line smoke test succeeds from mirrored raw installer URL for both bash and PowerShell.

---

## Phase 2 — Optional Pack Mirror Readiness

### Objective

Extend fallback beyond script/index entrypoints to support market-only optional packs via mirrored repos.

### Deliverables

1. Mirror selected optional pack repos to Gitee.
2. Extend market index schema to carry mirror metadata.
3. Update installer source resolution so pack archive fetches can choose GitHub or Gitee mirror repo.

### Proposed market schema extension

Add an optional field like:

```json
{
  "name": "petfish-pack-fat-slim-writer",
  "repo": "kylecui/petfish-pack-fat-slim-writer",
  "mirror_repo": "petfish-team/petfish-pack-fat-slim-writer",
  "ref": "v0.2.0",
  "path": ".opencode"
}
```

### Rules

- `repo` remains canonical GitHub repo
- `mirror_repo` is delivery-only mirror hint
- `ref` is still determined by GitHub version truth
- absence of `mirror_repo` should not break existing installs

### Acceptance criteria

1. A market-only pack can be downloaded from Gitee mirror repo when GitHub paths fail.
2. Existing GitHub-only packs still install unchanged.
3. No version ambiguity is introduced.

---

## Phase 3 — Observability, Gating, and Safe Enablement

### Objective

Make Gitee fallback measurable and controlled instead of “best effort only”.

### Deliverables

1. Mirror sync check workflow
2. Content integrity checks (hash/tag/file existence)
3. Post-release smoke tests
4. Optional telemetry/logging on which source succeeded
5. Enable/disable policy for Gitee fallback based on mirror readiness

### Acceptance criteria

1. Failed Gitee sync is visible in CI/workflow output.
2. GitHub release is still authoritative even if Gitee lag exists.
3. Installer does not silently prefer stale Gitee content over fresh GitHub content.

---

## 8. Technical Design Direction

## 8.1 Introduce a unified source resolver

### Problem

The installer currently duplicates download path construction and mirror fallback logic.

### Plan

Add a small source-resolution abstraction per shell family.

#### Bash

Potential helper functions:

- `resolve_source_candidates_raw()`
- `resolve_source_candidates_archive()`
- `resolve_source_candidates_market_index()`

or a more generic:

- `resolve_source_candidates <repo> <ref> <kind>`

#### PowerShell

Potential helper function:

- `Resolve-SourceCandidates -Repo <repo> -Ref <ref> -Kind <kind>`

### Candidate ordering policy

For phase 1:

1. GitHub primary URL
2. `ghfast.top`
3. `mirror.ghproxy.com`
4. Gitee mirror URL

### Important rule

The resolver decides **where to try**.
The download function decides **how to try**.

This separation reduces duplication and makes future sources (CDN/OSS/internal mirror) easier to add.

---

## 8.2 Separate “version truth” from “file delivery”

### Rule

- Version truth (`latest`, release number, tag semantics) must stay GitHub-driven.
- File delivery (raw/index/archive) may fall back to Gitee.

### Why

This avoids:

- stale-mirror latest confusion
- dual latest APIs
- accidental Gitee-first old-version installs

---

## 8.3 Do not rely on Gitee release attachment links

### Rule

Avoid designing the installer around Gitee release asset direct links.

### Use instead

- raw file URLs for scripts/index
- repo archive/tag archive paths for mirrored content

### Reason

Gitee release attachment URLs are not good stable installer contracts.

---

## 9. Workflow / Automation Plan

## 9.1 Proposed new workflow

Add a new workflow, likely something like:

- `.github/workflows/gitee-mirror.yml`

### Trigger strategy

Recommended trigger points:

- on push to `master`
- optionally on published GitHub Release
- manual dispatch for resync/recovery

### Responsibilities

1. Sync `petfish.ai` to Gitee mirror
2. Sync `petfish-market` to Gitee mirror
3. Verify key raw files exist on Gitee
4. Verify market index is readable on Gitee
5. Optionally run smoke tests against Gitee raw script path

### Important policy

Mirror sync/check should be a **post-release reliability enhancement**, not a blocker for the GitHub release contract.

Meaning:

- GitHub release success should not depend on Gitee availability.
- But mirror failure should produce actionable warning/failure signals.

---

## 9.2 Post-release verification

### Minimum smoke matrix

#### Bash

```bash
curl -fsSL <gitee-raw-remote-install.sh> | bash -s -- --pack init --target /tmp/... --platform opencode
```

#### PowerShell

```powershell
& ([scriptblock]::Create((irm <gitee-raw-remote-install.ps1>))) -Pack init -Target <path> -Platform opencode
```

### Additional checks

- mirrored `index.json` readable
- mirrored archive path for `petfish.ai` retrievable
- hash / content presence for critical files

---

## 10. Risks and Mitigations

## Risk 1 — Mirror lag causes stale installs

### Impact

Installer might fall back to Gitee and retrieve an older mirrored state.

### Mitigation

- keep GitHub first in priority order
- never use Gitee to decide latest version
- add release-after-sync verification
- consider mirror readiness flagging before enabling fallback for specific asset kinds

---

## Risk 2 — Over-scoping phase 1 by mirroring all optional packs immediately

### Impact

Large coordination cost, more repos to sync, more drift points.

### Mitigation

- phase 1 only mirrors `petfish.ai` and `petfish-market`
- optional pack mirrors move to phase 2

---

## Risk 3 — Code duplication across four installer files increases regression probability

### Impact

One installer gets updated while another misses the same fallback logic.

### Mitigation

- unify source-resolution design per shell family
- define one rollout checklist that explicitly names all four installer files
- verify local/remote bash/PowerShell parity in every related change

---

## Risk 4 — Gitee attachment download behavior pushes team toward unstable implementation choices

### Impact

Trying to mirror GitHub release-asset semantics on top of signed expiring URLs could create brittle install flows.

### Mitigation

- explicitly avoid Gitee attachment direct-link dependency in the initial design
- prefer raw/index/archive

---

## 11. Verification Strategy

## Phase 1 verification

1. Gitee raw fetch success:
   - `remote-install.sh`
   - `remote-install.ps1`
2. Gitee market index fallback success
3. Bash one-line mirrored install smoke
4. PowerShell one-line mirrored install smoke
5. CI/workflow report shows sync/check status

## Phase 2 verification

1. mirrored optional pack repo archive fetch works
2. market entry with `mirror_repo` resolves correctly
3. GitHub-primary path remains unchanged when available
4. fallback works when GitHub/archive path is intentionally unavailable

## Regression guardrails

Every implementation PR for this plan should verify at minimum:

- bash syntax
- PowerShell parser checks
- local installer smoke
- remote installer smoke
- market index retrieval behavior
- fallback ordering behavior

---

## 12. Rollback Strategy

If Gitee rollout causes problems:

1. Disable Gitee source candidates in source resolver
2. Leave GitHub + current proxy mirrors intact
3. Keep mirrored infra out-of-band until fixed

Rollback must be possible without changing release truth or market schema semantics.

---

## 13. Recommended Execution Order

1. Define mirror ownership and naming convention on Gitee
2. Create mirrors for `petfish.ai` and `petfish-market`
3. Add source-resolver abstraction design
4. Implement phase-1 raw/index fallback
5. Add Gitee mirror workflow
6. Add post-release smoke checks
7. Validate and document
8. After stable phase-1 operation, design `mirror_repo` support for market packs

---

## 14. Proposed File-Level Implementation Targets (future work, not in this plan step)

### Likely phase-1 code targets

- `install.sh`
- `remote-install.sh`
- `install.ps1`
- `remote-install.ps1`
- `.github/workflows/gitee-mirror.yml` (new)
- `docs/agent-install.md` (if user-facing fallback guidance is added)
- `docs/agent-upgrade.md` (if user-facing fallback guidance is added)
- possibly `README.md` if architecture/distribution model should be documented

### Likely phase-2 code/data targets

- `petfish-market/index.json` schema/content
- market resolver logic in the four installers

---

## 15. Decision Summary

### Recommended now

Proceed with a **two-stage rollout**:

- **Stage 1:** mirror main repo + market repo; add Gitee fallback for raw/index only
- **Stage 2:** mirror optional pack repos and add `mirror_repo` metadata support

### Not recommended now

- dual-primary release governance
- Gitee-first installs
- Gitee release-attachment dependency
- mirroring every optional repo before validating phase 1

---

## 16. Open Questions to resolve before implementation

1. Final Gitee org/user naming convention for mirrored repos
2. Whether the project wants Gitee fallback always enabled or guarded behind a mirror-health signal
3. Whether phase-1 docs should mention Gitee explicitly or keep it transparent as implementation detail
4. Whether optional-pack mirror rollout should be selective (high-demand packs first) or full coverage

---

## 17. Plan Quality Notes

This plan intentionally prioritizes:

- deterministic release truth
- low-regret phase-1 scope
- reversible rollout
- minimizing installer regression risk

It does **not** attempt to optimize for maximum mirror coverage in the first change set.
