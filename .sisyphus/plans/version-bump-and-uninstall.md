# Plan: Version Bump + Uninstall Capability

## Problem Statement

### P1: Pack versions not bumped → users can't upgrade
Most packs have had significant changes (trigger coverage fixes, new features, bug fixes) since their version was last set, but `pack-manifest.json` version fields were never bumped. Without `--force`, the installer skips packs where installed version ≥ source version → users get no updates.

### P2: No uninstall capability
Users have no way to cleanly remove an installed pack. Install touches 4 artifacts:
1. Skill directories in `.opencode/skills/` (or platform equivalent)
2. AGENTS.md sections wrapped in `<!-- BEGIN pack: {name} -->` / `<!-- END pack: {name} -->`
3. `opencode.json` MCP config entries (merged from `opencode.example.json`)
4. `installed-packs.json` registry entry

## Plan

### Task 1: Version Bumps

For each pack with changes since its last version bump, increment patch version in `pack-manifest.json`.

**Git log confirmed — ALL 11 packs have changes since last version bump:**

| Pack | Current | Bump To | Key Changes |
|------|---------|---------|-------------|
| companion | v1.0.0 | v1.1.0 | Gateway enhancements, --check-failures, --upgrade, KNOWN_PACKS fix, trigger fixes, description compression |
| deploy | v1.0.0 | v1.0.1 | Trigger coverage fix, SKILL.md schema fixes |
| testdocs | v1.0.0 | v1.0.1 | Trigger coverage fix, description compression |
| calibrate | v0.1.0 | v0.1.1 | Gateway anti-sycophancy integration, trigger fix, description compression |
| context | v1.0.0 | v1.0.1 | Trigger coverage fix, description compression |
| trust | v0.1.0 | v0.1.1 | Trigger coverage fix, description compression |
| ppt | v1.0.0 | v1.0.1 | Trigger coverage fix, description compression |
| petfish | v4.0.0 | v4.0.1 | Trigger coverage fix, description compression |
| init | v1.0.0 | v1.1.0 | Gateway enhancements, init_project.py updates, todo discipline, description compression, trigger fix |
| course | v1.3.1 | v1.3.2 | Trigger coverage fix, description compression, QA script fix |
| research | v0.8.1 | v0.9.0 | Metadata fixes, trigger regression fix, CJK token estimation, 100% trigger eval pass rate, description compression |

**Versioning rationale:**
- Patch bump (x.y.Z): trigger/description fixes only
- Minor bump (x.Y.0): new features or significant functional changes
- companion → v1.1.0: Gateway is a feature addition
- init → v1.1.0: new init capabilities
- research → v0.9.0: substantial quality + metadata improvements

**Files changed**: `packs/*/pack-manifest.json` (11 files, one field each)

### Task 2: Uninstall Capability

#### 2a: Design

**Uninstall flow (reverse of install):**
1. Read `installed-packs.json` to get pack's skill list
2. Remove skill directories listed in the pack entry
3. Remove AGENTS.md section between `<!-- BEGIN pack: {name} -->` and `<!-- END pack: {name} -->`
4. Remove opencode.json MCP entries that were added by the pack (read from pack's `opencode.example.json` to know which keys)
5. Remove pack entry from `installed-packs.json`

**Edge cases:**
- Pack not installed → error message, exit
- User modified AGENTS.md content within markers → still remove (markers are authoritative)
- User added custom content to a skill directory → warn, but still remove
- opencode.json keys shared between packs → only remove keys unique to this pack (check other installed packs' opencode.example.json)
- Global vs project scope → respect same logic as install

**Invocation:**
```powershell
.\install.ps1 -Uninstall -Pack <alias> [-Target .]
```
```bash
./install.sh --uninstall --pack <alias> [--target .]
```

Remote installers: NOT supported for uninstall (remote script is ephemeral, uninstall needs local context). Print guidance to use local installer instead.

#### 2b: Implementation — install.ps1

Add `[switch]$Uninstall` parameter. Add `Uninstall-Pack` function that:
1. Resolves pack alias → pack directory name
2. Reads installed-packs.json, validates pack is installed
3. Reads pack-manifest.json from the source pack directory to get the full list of skills, commands, and agents (installed-packs.json only stores skills; manifest is the authoritative source for all artifact types)
4. Removes skill/command/agent directories based on manifest data
5. Removes AGENTS.md markers + content between them
6. Removes opencode.json entries (compare with opencode.example.json)
7. Removes pack from installed-packs.json
8. Reports what was removed

#### 2c: Implementation — install.sh

Mirror the PowerShell implementation in bash.

#### 2d: Remote installers

Add error message: "Uninstall is not supported via remote installer. Use local installer instead: .\install.ps1 -Uninstall -Pack <alias>"

#### 2e: /petfish uninstall command

Add to companion SKILL.md and catalog_query.py. Shows the local uninstall command.

## Risks

1. **opencode.json shared keys**: Two packs might add the same MCP entry. Removing it when one pack uninstalls would break the other. Mitigation: check all other installed packs' opencode.example.json before removing a key.
2. **AGENTS.md manual edits**: Users might edit content within pack markers. Mitigation: accept this — markers are authoritative boundaries.
3. **Partial uninstall failure**: If script fails midway, state is inconsistent. Mitigation: do removals in order (files first, registry last) so re-running uninstall can recover.

## Files Touched

- `packs/*/pack-manifest.json` — version bumps (up to 11 files)
- `install.ps1` — add -Uninstall parameter + Uninstall-Pack function
- `install.sh` — add --uninstall flag + uninstall_pack function
- `remote-install.ps1` — add error message for --uninstall
- `remote-install.sh` — add error message for --uninstall
- `packs/core/petfish-companion-skill/.opencode/skills/petfish-companion/SKILL.md` — add /petfish uninstall docs
- `packs/core/petfish-companion-skill/.opencode/skills/petfish-companion/scripts/catalog_query.py` — add /petfish uninstall command support

## QA Scenarios

### Task 1 QA: Version Bumps

**Steps:**
1. For each of the 11 `pack-manifest.json` files, read the `version` field and confirm it matches the "Bump To" column above
2. Run `lsp_diagnostics` on each modified JSON file to confirm valid JSON syntax
3. Verify no other fields in pack-manifest.json were changed (only `version`)

**Expected result:** All 11 files show updated versions, valid JSON, no other field changes.

### Task 2 QA: Uninstall Capability

**QA 2a — install.ps1 uninstall parameter:**
1. Read install.ps1, confirm `[switch]$Uninstall` parameter exists in param block
2. Confirm `Uninstall-Pack` function exists and follows the 8-step flow
3. Confirm it reads pack-manifest.json (not just installed-packs.json) for artifact names

**QA 2b — install.sh uninstall flag:**
1. Read install.sh, confirm `--uninstall` flag is parsed in argument handling
2. Confirm `uninstall_pack` function exists and mirrors PowerShell logic
3. Confirm it reads pack-manifest.json for artifact names

**QA 2c — Remote installers:**
1. Read remote-install.ps1 and remote-install.sh
2. Confirm both detect uninstall flag and print error message pointing to local installer
3. Confirm they do NOT attempt any removal

**QA 2d — /petfish uninstall command:**
1. Read companion SKILL.md, confirm `/petfish uninstall` is documented in the command table
2. Read catalog_query.py, confirm uninstall subcommand is handled and outputs the correct local installer command

**Expected result:** All 4 installers updated, remote ones reject gracefully, /petfish uninstall shows correct guidance.
