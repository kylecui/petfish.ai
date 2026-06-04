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
2. **course** — Course development (installs: course, doc-reader, petfish)
3. **ops** — Operations/infrastructure (installs: deploy, petfish)
4. **security** — Security research (installs: deploy, petfish, testdocs, trust)
5. **research** — Research project (installs: doc-reader, petfish, research)
6. **writing** — Writing/documentation (installs: petfish, ppt)
7. **minimal** — Just the basics (installs: petfish only)
8. **comprehensive** — Everything (installs: course, deploy, doc-reader, petfish, ppt, testdocs, trust, context, research, reflect)
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
- `companion` — PEtFiSh core (2 core skills: fish-brain + fish-market, + /petfish command)
- `toolchain` — Skill lifecycle pipeline (9 skills: author, lint, mine, audit, gate, publish, optimize, eval, tracker)
- `course` — Course development (15 skills, 10 commands, 8 agents)
- `deploy` — Deployment & operations (7 skills)
- `testdocs` — Test cases & documentation (2 skills)
- `petfish` — Engineering writing style (1 skill)
- `ppt` — Presentation design (2 skills)
- `calibrate` — Anti-sycophancy calibration for reviews (1 skill)
- `context` — Topic governance and context isolation (1 skill)
- `trust` — Skill trust governance engine (1 skill)
- `research` — Research workbench — 50 skills across 8 domains (scientific, product, planning, learning, decision, risk-procurement, experience-event, adapters)
- `reflect` — Structured reflection — capture what went wrong, why, and corrective actions (1 skill)
- `doc-reader` — Document-to-Markdown conversion — PDF/DOCX/XLSX/HTML/PPTX reading via markitdown (1 skill)

Ask which packs they want. If they include `research`, ask the research domain follow-up question above.

> **Note**: Packs are split into **core** (init, companion, petfish, toolchain — shipped on petfish.ai) and **optional** (course, deploy, doc-reader, testdocs, ppt, calibrate, context, trust, research, reflect — distributed via petfish-market). Install commands resolve automatically — no user-visible difference.

---

## Step 3: Install

### 3a: Install init + companion together

```bash
uv run https://raw.githubusercontent.com/kylecui/petfish.ai/master/install.py --pack init,companion --platform <PLATFORM>
```

Replace `<PLATFORM>` with the platform you detected in Step 1 (e.g. `codex`, `opencode`, `claude`, etc.).

Run this command and verify it succeeds.

> **Note**: The installer automatically downloads optional packs from **petfish-market**. No need to specify a version — you always get the latest verified build. Core packs are bundled in the repo.

### 3b: Install the packs based on the user's choice from Step 2

For each pack the user selected, run:

```bash
uv run https://raw.githubusercontent.com/kylecui/petfish.ai/master/install.py --pack <ALIAS> --platform <PLATFORM>
```

Or install multiple packs at once:
```bash
uv run https://raw.githubusercontent.com/kylecui/petfish.ai/master/install.py --pack <ALIAS1>,<ALIAS2>,<ALIAS3> --platform <PLATFORM>
```

Replace `<ALIAS>` with each pack alias (e.g., `course`, `deploy`, `petfish`, etc.) and `<PLATFORM>` with the platform from Step 1.

> **Core vs Optional**: Core packs (init, companion, petfish, toolchain) download directly from the petfish.ai release. Optional packs (course, research, etc.) resolve via petfish-market — same command, same experience. The installer queries the market index automatically when a pack is not found in the core set.

> **Legacy shell installers** (install.sh, install.ps1, remote-install.sh, remote-install.ps1) are deprecated. If `uv` is not available, see the legacy commands in the README.

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

## Offline / Network-Restricted Install

If the user's environment cannot access GitHub (firewall, air-gapped, China network issues), use local install instead of remote.

### Option 1: Pre-download and run locally

1. On a machine with network access, download these files to the same directory:
   - `install.ps1` (or `install.sh`)
   - `platforms.json`
   - The target pack directory under `packs/` (e.g. `packs/petfish-style-skill/`)

   The easiest way is to clone the entire repo:
   ```bash
   git clone https://github.com/kylecui/petfish.ai.git
   ```

2. Transfer the files (or the whole repo) to the target machine via USB, internal file share, or SCP.

3. Run the local installer:
   **PowerShell:**
   ```powershell
   .\install.ps1 -Pack <alias> -Platform <PLATFORM> -Target .
   ```

   **Bash:**
   ```bash
   ./install.sh --pack <alias> --platform <PLATFORM> --target .
   ```

   > The local installer scans the `packs/` directory dynamically — no internet access needed. `platforms.json` provides platform metadata; if missing, the installer falls back to hardcoded defaults.

### Option 2: Mirror-enhanced remote install (China network)

The remote installer (`remote-install.ps1` v0.11.12+) includes automatic mirror fallback for China network environments:

- Tries the original GitHub URL first
- Falls back to `ghfast.top` mirror
- Falls back to `ghproxy.com` mirror
- Retries up to 3 times with exponential backoff

No extra flags needed — mirror fallback is automatic on download failure.

### Option 3: Private repo with GitHub token

If the repo is private or rate-limited:

**Bash:**
```bash
curl -fsSL -H "Authorization: token $GITHUB_TOKEN" \
  https://raw.githubusercontent.com/kylecui/petfish.ai/master/remote-install.sh \
  | GITHUB_TOKEN=$GITHUB_TOKEN bash -s -- --pack <alias> --platform <PLATFORM>
```

**PowerShell:**
```powershell
& ([scriptblock]::Create((irm https://raw.githubusercontent.com/kylecui/petfish.ai/master/remote-install.ps1))) -Pack <alias> -Platform <PLATFORM> -GitHubToken $env:GITHUB_TOKEN
```

### Minimum files for local install

| File | Required | Notes |
|------|----------|-------|
| `install.ps1` or `install.sh` | Yes | Main installer script |
| `platforms.json` | Recommended | Platform metadata; fallback defaults exist if missing |
| `packs/<pack-dir>/` | Yes | At least the pack you want to install |
| `packs/<pack-dir>/pack-manifest.json` | Yes | Pack metadata read by installer |

---

## UTF-8 Terminal Requirement

PEtFiSh pack descriptions and status messages may contain Chinese text. If these appear garbled (e.g., `æªå¨è¿ç¨` instead of Chinese characters), your terminal is using a non-UTF-8 encoding.

**Fix:**
- **Linux/macOS**: Ensure `LANG` is set to a UTF-8 locale: `export LANG=en_US.UTF-8`
- **Windows PowerShell**: Set the console code page to UTF-8: `chcp 65001`
- The installers automatically set UTF-8 locale, but the AI agent's output may still be garbled if the terminal itself is not configured for UTF-8.

---

## About PEtFiSh

**GitHub**: https://github.com/kylecui/petfish.ai
**Website**: https://petfish.ai
**What it does**: Manages AI skill lifecycle across 8 platforms — discover, create, validate, optimize, install, track. 4 core packs + 10 optional packs via petfish-market.
