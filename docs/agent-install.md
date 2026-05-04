# PEtFiSh Installation Guide (for AI Agents)

> If you are an AI coding assistant reading this document, follow the steps below to install PEtFiSh for the user. Do NOT summarize or skip steps. Execute them in order.

---

## Step 0: Greet the user

Say:

```
><(((^> 胖鱼 PEtFiSh — AI Worker's Companion

I'm setting up PEtFiSh for you. Let me ask a few questions first.
```

---

## Step 1: Detect environment

1. Detect the operating system:
   - If macOS or Linux or WSL → use **Bash** commands
   - If Windows → use **PowerShell** commands

2. Detect the current AI platform by checking for these files in the project root:
   - `.opencode/` or `opencode.json` → **opencode**
   - `.claude/` or `CLAUDE.md` → **claude**
   - `.codex/` → **codex**
   - `.cursor/` or `.cursorrules` → **cursor**
   - `.github/copilot-instructions.md` → **copilot**
   - `.windsurf/` or `.windsurfrules` → **windsurf**
   - `.agents/` and `GEMINI.md` → **antigravity**
   - None of the above → **universal**

Tell the user which OS and platform you detected.

---

## Step 2: Ask the user what they need

Ask: "What type of project is this?"

Offer these choices:
1. **code** — General coding project (installs: deploy, petfish, testdocs)
2. **course** — Course development (installs: course, petfish)
3. **ops** — Operations/infrastructure (installs: deploy, petfish)
4. **writing** — Writing/documentation (installs: petfish, ppt)
5. **minimal** — Just the basics (installs: petfish only)
6. **comprehensive** — Everything (installs: course, deploy, petfish, ppt, testdocs)
7. **custom** — Let me choose specific packs

If user chooses **custom**, show available packs:
- `init` — Project initializer + wizard
- `companion` — PEtFiSh core (10 skill lifecycle tools + /petfish command)
- `course` — Course development (15 skills, 10 commands, 8 agents)
- `deploy` — Deployment & operations (7 skills)
- `testdocs` — Test cases & documentation (2 skills)
- `petfish` — Engineering writing style (1 skill)
- `ppt` — Presentation design (2 skills)
- `calibrate` — Anti-sycophancy calibration for reviews (1 skill)
- `context` — Topic governance and context isolation (1 skill)
- `trust` — Skill trust governance engine (1 skill)

Ask which packs they want.

---

## Step 3: Install

### 3a: Install init + companion together

**Bash:**
```bash
curl -fsSL https://raw.githubusercontent.com/kylecui/SKILL_builder/master/remote-install.sh | bash -s -- --pack init,companion --detect
```

**PowerShell:**
```powershell
& ([scriptblock]::Create((irm https://raw.githubusercontent.com/kylecui/SKILL_builder/master/remote-install.ps1))) -Pack "init,companion" -Detect
```

Run this command and verify it succeeds.

> **Note**: The install script automatically downloads from the **latest stable release** (currently v0.2.0). No need to specify a version — you always get the latest verified build.

### 3b: Install the packs based on the user's choice from Step 2

For each pack the user selected, run:

**Bash:**
```bash
curl -fsSL https://raw.githubusercontent.com/kylecui/SKILL_builder/master/remote-install.sh | bash -s -- --pack <ALIAS> --detect
```

**PowerShell:**
```powershell
& ([scriptblock]::Create((irm https://raw.githubusercontent.com/kylecui/SKILL_builder/master/remote-install.ps1))) -Pack <ALIAS> -Detect
```

Replace `<ALIAS>` with each pack alias (e.g., `course`, `deploy`, `petfish`, etc.).

---

## Step 4: Restart and verify

> **Important**: Most AI coding platforms (OpenCode, Claude Code, Cursor, etc.) load skills at session start. Newly installed skills are NOT available in the current session. Tell the user to **exit and re-launch** their AI coding tool before proceeding.

After restart, run `/petfish` to verify the companion is working. It should show installed skill status.

If it works, tell the user:

```
><(((^> PEtFiSh is ready!

Installed packs: [list what was installed]
Platform: [detected platform]

Try these commands:
  /petfish catalog    — Browse all available skills
  /petfish suggest    — Get recommendations for your project
  /petfish lint       — Check skill quality
  /petfish search     — Search for skills across marketplaces
```

---

## Step 5: Optional — trust governance

If the user chose `trust` pack or if they are building a security-sensitive project, also suggest:

```bash
uv add trustskills
```

This installs the external trust governance engine for behavioral analysis of skills.

---

## Troubleshooting

- If `curl` is not found: suggest `wget -qO- <url> | bash -s -- <args>` as alternative
- If PowerShell execution policy blocks the script: suggest `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`
- If the install says "uv not found": suggest installing uv from https://docs.astral.sh/uv/getting-started/installation/
- If platform auto-detection fails: add `--platform <name>` explicitly

---

## About PEtFiSh

**GitHub**: https://github.com/kylecui/SKILL_builder
**Website**: https://petfish.ai
**What it does**: Manages AI skill lifecycle across 8 platforms — discover, create, validate, optimize, install, track.
