# Authoring Quality Gate

Run this checklist before delivering any skill. Every item must pass.

## Structural

- [ ] Name: 1-64 chars, lowercase/numbers/hyphens, no leading/trailing hyphen
- [ ] Name matches directory name exactly
- [ ] Directory structure valid: SKILL.md + references/ + assets/ + evals/ (as needed)

## Frontmatter

- [ ] Description under 1024 characters
- [ ] Description contains: what it does + when to use it
- [ ] Description includes at least one near-miss boundary
- [ ] No optional fields with no real value

## SKILL.md Body

- [ ] Under 500 lines (ideally under 200)
- [ ] Has Role section
- [ ] Has Activation or When to Use section
- [ ] Has Workflow with numbered steps
- [ ] Has Output Contract (what must be delivered)
- [ ] Has Must Do / Must Not Do
- [ ] Has Domain Rules (or reference to them)
- [ ] Has Decision Points (workflow branches)
- [ ] Has Execution Modes (interactive/auto/review)
- [ ] Has Anti-patterns (at least 2)
- [ ] Has Handoff & Boundaries (owns / does not own)

## References

- [ ] No duplication of SKILL.md content
- [ ] Each file adds actionable knowledge
- [ ] File names are descriptive (not "guide.md" or "notes.md")

## Assets

- [ ] Templates have real placeholder sections, not just comments
- [ ] Templates match the skill type declared in taxonomy

## Evals

- [ ] At least 3 should-trigger prompts
- [ ] At least 2 should-not-trigger prompts
- [ ] Each eval has 2+ assertions
- [ ] At least 1 boundary case between this skill and an adjacent skill

## Scripts (if present)

- [ ] Has --help output
- [ ] Has clear error messages
- [ ] Uses relative paths, no hardcoded absolutes
- [ ] Cross-platform compatible

## Decision

- All pass → deliver
- 1-2 non-blocking fails → deliver with warnings, list what to fix
- 3+ fails or any blocking fail → do not deliver, iterate
