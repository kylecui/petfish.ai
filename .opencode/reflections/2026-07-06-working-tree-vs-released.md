# L2 Task Debrief: Working Tree Edit ≠ Released Code

**Date**: 2026-07-06
**Trigger**: Issue #272 reopened by reporter — commands/agents dict handling fix claimed shipped but not on master

## Failure-Correction Chain

| # | Trigger | Root Cause | Correction | Prevention Rule |
|---|---------|------------|------------|-----------------|
| 1 | User reported #272: commands/agents loops crash with `WindowsPath / dict` on dict-format manifest entries | Code fix was applied to working tree (edit) but never committed/pushed — remained as uncommitted diff for 2 releases | Committed fix, pushed, PR #273 merged, released v2.4.7 | After any code edit that addresses an issue, verify `git diff origin/master` is empty before claiming "fixed" |
| 2 | I closed #272 with "已在v2.4.6中修复" without verifying the fix reached master | In long sessions with multiple PR/release cycles, lost track of "edited locally" vs "committed and pushed" boundary | Verified via `git show origin/master:install.py` that commands/agents dict handling absent from master | Never claim an issue is fixed without verifying the code exists on the release branch |

## Root Cause Analysis

**Mechanism**: In a 6+ hour session with 7 releases (v2.4.0 through v2.4.7), 20+ files changed, and multiple parallel subagent delegations, I applied the commands/agents dict fix to the working tree as part of a batch edit. I then proceeded to pytest (passed) and assumed the fix was "in." But the subsequent PR/commit only captured the skills loop fix (from v2.4.5 PR #270). The commands/agents fix sat in the working tree across 2 releases without being staged.

**Why this happened**:
1. **No commit boundary discipline**: I edited, tested, and moved on without creating a commit checkpoint
2. **Verification gap**: I claimed "fixed" based on reading my local working tree, not origin/master
3. **Session length**: Extended sessions increase the risk of uncommitted edits accumulating

## Prevention Rules

1. **After any edit that fixes an issue**: Run `git diff --cached` to confirm the change is staged. If nothing shows, the edit is still in the working tree.
2. **Before claiming "fixed" or closing an issue**: Run `git show origin/master:<file>` to verify the fix code exists on the remote release branch.
3. **Commit checkpoint discipline**: After each logical fix (not just each release), create a commit. Don't accumulate multiple fixes in the working tree.
4. **For multi-file fixes**: Use `git add -A && git diff --cached --stat` to verify ALL intended files are staged before committing.

## Lessons

1. **Working tree edits are invisible to users.** An edit that isn't pushed to master might as well not exist.
2. **"I edited it" ≠ "it's shipped".** The gap between these two states is a commit + push + merge + release.
3. **Long sessions amplify this risk.** More edits = more chances for uncommitted changes to accumulate.
4. **Reporter was right to reopen.** The correct response to a reopened issue is immediate verification, not defensive argument.

## Sedimentation Recommendation

- **Scope**: `universal`
- **Target**: AGENTS.md `开发经验沉淀` section
- **Proposed addition**:

> ### Working tree edit ≠ released code
>
> 修复issue后，必须通过 `git show origin/master:<file>` 验证修复代码存在于远程release分支，而非仅存在于本地working tree。在长session中多次edit→test→release循环时，容易将"已编辑"误认为"已提交"——每次logical fix后立即commit，不要在working tree中积累多个fix。
>
> 此教训源自#272：commands/agents dict handling fix在working tree中存在了2个release周期但从未提交，reporter正确地reopen了issue。
