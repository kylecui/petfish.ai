# /petfish Commands

The `/petfish` command is your main entry point for managing PEtFiSh. Run it in your AI assistant's chat.

---

## Status & Discovery

### `/petfish`

Show installed packs, skill counts, and current version.

```
/petfish
```

Displays: installed packs, skill/command/agent counts per pack, platform detected, and version info.

### `/petfish catalog`

Browse all available packs and skills — including those not yet installed.

```
/petfish catalog
```

Shows: pack name, description, skill count, install status, and profile associations.

### `/petfish suggest`

Get pack recommendations based on your project's structure and files.

```
/petfish suggest
```

Scans your project for signals (Dockerfile → `deploy`, `.opencode/skills/course-*` → `course`, etc.) and recommends matching packs.

### `/petfish detect`

Detect the current AI platform.

```
/petfish detect
```

Returns the detected platform (opencode, claude, cursor, etc.) and the signals used for detection.

---

## Install & Upgrade

### `/petfish install <alias>`

Get the install command for a pack. Does not install directly — shows the command for you to run.

```
/petfish install deploy
```

Output includes OS-appropriate commands for macOS/Linux and Windows PowerShell.

??? note "Available pack aliases"
    `init`, `companion`, `course`, `testdocs`, `deploy`, `petfish`, `ppt`, `calibrate`, `context`, `trust`, `research`, `reflect`

### `/petfish upgrade`

Show the upgrade command for all installed packs.

```
/petfish upgrade
```

Checks the latest GitHub release, compares with installed versions, and shows the OS-appropriate upgrade command with `--force`.

### `/petfish uninstall <alias>`

Show the uninstall command for a pack (local installer only).

```
/petfish uninstall deploy
```

---

## Search & Discover

### `/petfish search <keyword>`

Search for skills and MCP servers across external marketplaces (PEtFiSh, Glama, Smithery, SkillKit, anthropics/skills, GitHub).

```
/petfish search "email notification"
```

Returns ranked results with install/config guidance. Use when the Skill Sense gap detection suggests searching.

### `/petfish mine <repo>`

Analyze a GitHub repository or local repo to discover reusable workflows that could become skills.

```
/petfish mine https://github.com/org/repo
```

Scans docs and executable entrypoints, filters one-off or unsafe ideas, and outputs candidate skills with boundaries, required tools, risks, and priority ranking.

---

## Skill Lifecycle

### `/petfish create <name>`

Scaffold a new skill from scratch.

```
/petfish create my-skill
```

Generates a valid skill directory with `SKILL.md` (role, activation, workflow, boundaries), plus optional `references/`, `scripts/`, `assets/`, and `evals/` directories.

### `/petfish lint [path]`

Run format and quality checks on a skill.

```
/petfish lint .opencode/skills/my-skill/
```

Reports ERROR/WARN/INFO findings with rule IDs, a quality score out of 100, and optional fix suggestions.

### `/petfish audit <path>`

Run a security audit on a skill.

```
/petfish audit .opencode/skills/my-skill/
```

Scans `SKILL.md`, `scripts/`, `references/`, and MCP/tool scope for prompt injection, secret access, dangerous commands, remote execution, and excessive permissions. Returns a 0.0–1.0 risk score with pass/fail and remediation guidance.

### `/petfish gate <path>`

Run the full publish quality gate (lint + security audit + metadata validation).

```
/petfish gate .opencode/skills/my-skill/
```

Returns a decision: **PASS**, **CONDITIONAL**, or **FAIL**. Use before publishing or merging skills.

??? tip "Recursive gating"
    Gate all skills in a directory:
    ```
    /petfish gate .opencode/skills/ --recursive
    ```

### `/petfish optimize <path>`

Analyze and improve a skill's description for trigger precision.

```
/petfish optimize .opencode/skills/my-skill/
```

Checks description length, trigger phrase density, specificity score, activation boundaries, and sibling overlap. Outputs rewrite suggestions and a replacement description.

### `/petfish eval <path>`

Test trigger accuracy using positive and negative query sets.

```
/petfish eval .opencode/skills/my-skill/
```

Reports pass rate, false positive/negative rates, per-query decisions, and sibling cross-trigger conflicts.

### `/petfish stats`

View skill usage analytics.

```
/petfish stats
```

Shows activation counts, session coverage, helpful/not_helpful feedback, and identifies high-value vs. low-activity skills.

---

## Quick Reference

| Command | Purpose |
|---|---|
| `/petfish` | Installed pack and skill status |
| `/petfish catalog` | Browse all available packs |
| `/petfish suggest` | Recommend packs for your project |
| `/petfish detect` | Detect current AI platform |
| `/petfish install <alias>` | Get install command |
| `/petfish upgrade` | Show upgrade command |
| `/petfish uninstall <alias>` | Show uninstall command |
| `/petfish search <keyword>` | Search external marketplaces |
| `/petfish mine <repo>` | Mine repo for skill candidates |
| `/petfish create <name>` | Scaffold a new skill |
| `/petfish lint [path]` | Quality and format checks |
| `/petfish audit <path>` | Security audit |
| `/petfish gate <path>` | Full publish gate |
| `/petfish optimize <path>` | Improve descriptions |
| `/petfish eval <path>` | Test trigger accuracy |
| `/petfish stats` | Usage analytics |
