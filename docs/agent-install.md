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

> **Important**: You are an AI agent — you already know which platform you are running on. Use your own platform identity directly (e.g. `--platform codex` if you are Codex, `--platform claude` if you are Claude Code). Do NOT rely on `--detect`, which uses marker files and may guess wrong.

Tell the user which OS and platform you detected.

---

## Step 2: Ask the user what they need

Ask: "What type of project is this?"

Offer these choices:
1. **code** — General coding project (installs: deploy, petfish, testdocs)
2. **course** — Course development (installs: course, petfish)
3. **ops** — Operations/infrastructure (installs: deploy, petfish)
4. **security** — Security research (installs: deploy, petfish, testdocs, trust)
5. **research** — Research project (installs: petfish, research)
6. **writing** — Writing/documentation (installs: petfish, ppt)
7. **minimal** — Just the basics (installs: petfish only)
8. **comprehensive** — Everything (installs: course, deploy, petfish, ppt, testdocs, trust, context, research)
9. **custom** — Let me choose specific packs

If user chooses **research** or any profile that includes the research pack, ask a follow-up question:

```
What kind of research will this project focus on?

1. Academic — scientific literature, experiments, papers
2. Business — product research, market analysis, competitor analysis, decisions, procurement
3. Planning — strategy, stakeholders, scenarios, learning paths
4. Experiential — events, travel, venues, logistics
5. Mixed — all research domains
6. Custom — pick specific domains
```

This determines how the research workspace is scaffolded and which skill chains agents prioritize.

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
- `research` — Research workbench — 50 skills across 8 domains (scientific, product, planning, learning, decision, risk-procurement, experience-event, adapters)

Ask which packs they want. If they include `research`, ask the research domain follow-up question above.

---

## Step 3: Install

### 3a: Install init + companion together

**Bash:**
```bash
curl -fsSL https://raw.githubusercontent.com/kylecui/petfish.ai/master/remote-install.sh | bash -s -- --pack init,companion --platform <PLATFORM>
```

**PowerShell:**
```powershell
& ([scriptblock]::Create((irm https://raw.githubusercontent.com/kylecui/petfish.ai/master/remote-install.ps1))) -Pack "init,companion" -Platform <PLATFORM>
```

Replace `<PLATFORM>` with the platform you detected in Step 1 (e.g. `codex`, `opencode`, `claude`, etc.).

Run this command and verify it succeeds.

> **Note**: The install script automatically downloads from the **latest stable release**. No need to specify a version — you always get the latest verified build.

### 3b: Install the packs based on the user's choice from Step 2

For each pack the user selected, run:

**Bash:**
```bash
curl -fsSL https://raw.githubusercontent.com/kylecui/petfish.ai/master/remote-install.sh | bash -s -- --pack <ALIAS> --platform <PLATFORM>
```

**PowerShell:**
```powershell
& ([scriptblock]::Create((irm https://raw.githubusercontent.com/kylecui/petfish.ai/master/remote-install.ps1))) -Pack <ALIAS> -Platform <PLATFORM>
```

Replace `<ALIAS>` with each pack alias (e.g., `course`, `deploy`, `petfish`, etc.) and `<PLATFORM>` with the platform from Step 1.

---

## Step 4: Restart and verify

> **Important**: Most AI coding platforms (OpenCode, Claude Code, Cursor, etc.) load skills at session start. Newly installed skills are NOT available in the current session. Tell the user to **exit and re-launch** their AI coding tool before proceeding.

When the install output shows at least one item installed, use the platform-specific restart hint:

| Platform | Hint |
|---|---|
| opencode | `⚠️  Restart needed. Exit: Ctrl+C | Resume: opencode -s <session_id>` |
| claude | `⚠️  Restart needed. Exit: /exit or Ctrl+C | Resume: claude --continue` |
| codex | `ℹ️  Restart may be needed. Skills might reload dynamically; if not, exit with Ctrl+C and re-launch.` |
| cursor | `⚠️  Restart needed. Reload window: Ctrl+Shift+P → "Reload Window"` |
| copilot | `⚠️  Restart needed. Reload window: Ctrl+Shift+P → "Reload Window"` |
| windsurf | `⚠️  Restart needed. Reload window: Ctrl+Shift+P → "Reload Window"` |
| antigravity | `⚠️  Restart needed. Exit: Ctrl+C` |

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
- If platform auto-detection fails or picks the wrong platform: detection is marker-based (looks for `.opencode/`, `.claude/`, `.codex/`, etc.). As an AI agent, you should always use `--platform <name>` explicitly instead of `--detect` — you know your own runtime platform

---

## About PEtFiSh

**GitHub**: https://github.com/kylecui/petfish.ai
**Website**: https://petfish.ai
**What it does**: Manages AI skill lifecycle across 8 platforms — discover, create, validate, optimize, install, track.
