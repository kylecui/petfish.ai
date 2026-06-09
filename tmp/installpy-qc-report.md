# QC Report: install.py Unified Python Installer

Date: 2026-06-05
Status: **BLOCKED / CANNOT VERIFY**

## Verdict

**FAIL (blocking issue)** — Cannot execute QA/QC because the target artifact is not reachable.

## What We Were Asked To Verify

The petfish team delivered a unified Python installer (`install.py`) claimed to:
- Replace all 4 shell installers (~9335 lines total) with a single 2372-line Python script
- Use stdlib only (no external dependencies)
- Be invoked via `uv run https://raw.githubusercontent.com/kylecui/petfish.ai/master/install.py --pack <alias>`
- Achieve full feature parity with existing bash/PowerShell installers

Provided commit chain:
| Phase | Commit | Claim |
|-------|--------|-------|
| 0+1: Core | `f837219` | Core installer |
| 2: Merge | `9cef162` | Merge |
| 3: Dist | `749555f` | Distribution |
| 4: Ops | `e184c3a` | Ops |
| 5: Docs | `b6142b5` | Documentation |

## Blocking Issue

**None of the 5 commits are reachable in `kylecui/petfish.ai`.**

Evidence of verification attempts:

| Check | Result |
|-------|--------|
| `https://raw.githubusercontent.com/kylecui/petfish.ai/master/install.py` | HTTP 404 |
| `gh api repos/kylecui/petfish.ai/commits/f837219` | 404 "No commit found" |
| Search all 8 branches for `install.py` | Not found on any branch |
| Search recent 100 commits for any of the 5 SHAs | No match |
| GitHub code search for `install.py` | No results |

Branches checked: `master`, `dev`, `skills-dev`, `feat/fish-trail-tiered-memory-v2`, `feat/v1.3-module-decomposition`, `feat/v1.4-market-first`, `fix/issue-135-context-filter`, `fix/207-dir-name-mismatch`

## Possible Causes

1. **Commits are on a fork**, not pushed to `kylecui/petfish.ai` yet
2. **Commits are in a draft PR** that hasn't been pushed to a branch on the main repo
3. **Commits are local-only** and haven't been pushed
4. **The commits are in a different repo** (e.g. a team member's fork)

## What QA Needs To Execute

Once the artifact is reachable, the following test matrix must be executed:

### Critical (P0)

| ID | Scenario | Rationale |
|----|----------|-----------|
| T1 | `uv run install.py --pack petfish --platform opencode` project-local | Basic smoke test |
| T2 | `uv run install.py --pack init,companion --platform opencode` | **#215 regression** — must NOT escalate all packs to global |
| T3 | `uv run install.py --pack init,companion,deploy,petfish --platform opencode` | **#215 regression** — merged command must split init (global) from rest (local) |
| T4 | `uv run install.py --pack petfish --platform opencode --global` | Explicit global flag |
| T5 | Feature parity: all flags from bash installer (`--target`, `--platform`, `--detect`, `--global`, `--force`, `--list`, `--uninstall`, `--offline`) | Must match bash installer behavior |
| T6 | `uv run install.py --pack research --platform opencode` | Market pack download (optional pack) |
| T7 | `uv run install.py --list` | Pack listing |

### High (P1)

| ID | Scenario | Rationale |
|----|----------|-----------|
| T8 | `uv run install.py --pack all --platform opencode` | All packs install |
| T9 | `uv run install.py --uninstall --pack petfish --platform opencode` | Uninstall |
| T10 | `uv run install.py --pack petfish --platform claude` | Cross-platform (non-opencode) |
| T11 | `uv run install.py --pack petfish --platform opencode --target /tmp/nonexistent` | Target dir creation |
| T12 | `uv run install.py --pack nonexistent --platform opencode` | Error handling |
| T13 | `uv run install.py --pack petfish --force --platform opencode` | Force overwrite |

### Medium (P2)

| ID | Scenario | Rationale |
|----|----------|-----------|
| T14 | `uv run install.py --detect` | Platform auto-detection |
| T15 | `uv run install.py --pack petfish --offline` | Offline mode |
| T16 | `uv run install.py --pack community/some/repo` | Community pack |
| T17 | Run from non-project directory (cwd = /tmp) | Default TARGET behavior |
| T18 | Python 3.10 / 3.11 / 3.12 / 3.13 compatibility | stdlib-only claim |
| T19 | Windows execution | Cross-OS support |

### Specific #215 Regression Tests

These MUST pass for any installer to ship:

```bash
# Test A: init alone → global (intended behavior)
uv run install.py --pack init --platform opencode
# Expect: init skills in ~/.config/opencode/skills/

# Test B: init + companion → init global, companion local
uv run install.py --pack init,companion --platform opencode
# Expect: init in ~/.config/opencode/skills/, companion in .opencode/skills/

# Test C: init + companion + deploy + petfish → init global, rest local
uv run install.py --pack init,companion,deploy,petfish --platform opencode
# Expect: init in global, others in project-local

# Test D: non-init packs → always project-local
uv run install.py --pack deploy,petfish --platform opencode
# Expect: all in .opencode/skills/, nothing in global
```

## Recommendation

**Request petfish team to:**

1. **Push commits to a reachable branch** on `kylecui/petfish.ai` (or provide the fork repo URL)
2. **Or provide the install.py file content directly** so we can run static analysis
3. **Or open a draft PR** so commits become reachable via the PR's ref

Without access to the artifact, no QA/QC can be performed. This is a hard gate — we cannot certify code we cannot inspect.

## Next Steps

Once the artifact is reachable:
1. Download and hash-verify
2. Static analysis: structure, flags, globals handling, #215 fix presence
3. Dynamic tests: T1-T19 per matrix above
4. Cross-reference with bash installer feature list
5. Produce updated QC report with PASS/CONDITIONAL/FAIL
