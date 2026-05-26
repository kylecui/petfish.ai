# Installer Community Pack Feature — Investigation & Implementation Plan

## Status: UNCOMMITTED (~735 insertions across 3 files)

## 1. What Exists

### Modified Files
| File | Insertions | Key Functions |
|------|-----------|---------------|
| `install.ps1` | ~192 | `Test-CommunityPack`, `Parse-CommunitySpec`, `Download-CommunityPack` |
| `install.sh` | ~414 | `is_community_pack`, `parse_community_spec`, `download_community_pack` |
| `remote-install.sh` | ~193 | Same as install.sh (adapted for remote context) |
| `remote-install.ps1` | **0** | ❌ NO CHANGES — critical gap |

### Feature Specification
- **Syntax**: `community/<owner>/<repo>[/<ref>]` (e.g., `community/someuser/my-skills/main`)
- **Download mechanism**: GitHub tarball API with optional `$GITHUB_TOKEN` auth; fallback to `git clone --depth 1`
- **Validation**: Checks for `.opencode/` directory with skills/commands/agents subdirectories
- **Auto-generation**: Creates `pack-manifest.json` if missing (infers name, version, skills list)
- **Staging**: Uses temporary directory with cleanup trap
- **Uninstall**: Supported (tracks community packs in registry)

### Architecture
```
User input: --pack community/owner/repo/ref
  → Parse spec → {owner, repo, ref}
  → Download tarball (or git clone fallback)
  → Extract to staging dir
  → Validate .opencode/ structure
  → Generate manifest if missing
  → Copy to target (same as built-in packs)
  → Register in installed-packs.json
```

## 2. What's Missing

### Critical
1. **`remote-install.ps1` has NO community pack code** — users on Windows using the remote installer cannot install community packs
2. **No GitHub issue** — feature is untraceable in project history
3. **No branch** — changes are on working tree only, no stash, no commit
4. **No tests** — no smoke test, no edge case coverage
5. **No documentation** — README, docs/agent-install.md, docs/zh/README.md don't mention community packs

### Important
6. **No rate limit handling** — GitHub API returns 403 when rate-limited; no backoff/retry
7. **No manifest schema validation** — auto-generated manifest may not match pack-manifest.json schema
8. **No version pinning** — `ref` defaults to HEAD/main if omitted; no lockfile mechanism
9. **No security review** — downloads arbitrary code from GitHub; no trust/audit gate

### Nice-to-Have
10. **No offline/cache support** — always re-downloads
11. **No `--list` integration** — community packs don't appear in `--list` output
12. **No upgrade path** — how to upgrade a community pack to newer ref?

## 3. Risk Assessment

| Risk | Severity | Mitigation |
|------|----------|-----------|
| Windows remote users get no community pack support | HIGH | Implement in remote-install.ps1 |
| Arbitrary code execution from untrusted repos | HIGH | Document trust model; recommend `--audit` post-install |
| Rate limiting breaks install silently | MEDIUM | Add retry + clear error message |
| No traceability (no issue, no branch) | MEDIUM | Create issue, create branch, commit properly |
| Manifest auto-generation produces invalid schema | LOW | Validate against pack-manifest.json schema |

## 4. Implementation Plan

### Phase 1: Stabilize & Document (before commit)
1. Create GitHub issue documenting the feature
2. Create feature branch `feature/community-packs`
3. Port community pack code to `remote-install.ps1`
4. Add rate limit retry (3 attempts with backoff)
5. Validate auto-generated manifest against schema
6. Add `--list` integration for installed community packs

### Phase 2: Test & QA
7. Write smoke test: install a known public community pack
8. Test edge cases: missing .opencode/, private repo, invalid ref, rate limit
9. Test all 4 installers: local PS1, local sh, remote PS1, remote sh
10. Test uninstall of community packs

### Phase 3: Documentation & Release
11. Update README (Install Commands section)
12. Update docs/agent-install.md
13. Update docs/zh/README.md
14. Update website if applicable
15. Add security note about community pack trust model

### Phase 4: Commit & Release
16. Commit to feature branch
17. PR to dev
18. Merge to dev, test
19. PR to master
20. Release with minor version bump (community packs = new feature = minor)

## 5. QA Gate Checklist

- [ ] All 4 installers handle `community/owner/repo` syntax
- [ ] All 4 installers handle `community/owner/repo/ref` syntax
- [ ] Fallback from tarball to git clone works
- [ ] Private repo with GITHUB_TOKEN works
- [ ] Missing .opencode/ produces clear error
- [ ] Auto-generated manifest is valid JSON matching schema
- [ ] Uninstall removes community pack cleanly
- [ ] `--list` shows installed community packs
- [ ] Rate limit produces retry + clear error (not silent failure)
- [ ] Documentation updated in EN and ZH

## 6. Decision Required

**Question for user**: Should we proceed with Phase 1 (stabilize + port to remote-install.ps1), or defer this feature entirely?

Arguments for proceeding:
- ~735 lines already written and working in 3/4 installers
- Completes the "install from anywhere" story
- Enables community skill sharing without central registry

Arguments for deferring:
- No issue, no branch — origin untraceable
- Security model undefined (arbitrary code download)
- Significant testing surface (4 installers × multiple edge cases)
- Could ship as v0.12.0 after current paper work completes

**Recommendation**: Defer to post-paper. Create the GitHub issue now for traceability, but don't invest implementation time until paper + ablation experiments are done.
