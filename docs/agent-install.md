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
   - If macOS or Linux or WSL → **Bash** is available
   - If Windows → **PowerShell** is available

2. Check that `uv` is installed:
   ```bash
   uv --version
   ```
   If `uv` is not found, install it from https://docs.astral.sh/uv/getting-started/installation/ before continuing.

3. Detect the current AI platform by checking for these files in the project root:
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
8. **comprehensive** — Everything (installs: course, deploy, petfish, ppt, testdocs, trust, context, research, reflect)
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

Ask which packs they want. If they include `research`, ask the research domain follow-up question above.

> **Note**: Packs are split into **core** (init, companion, petfish, toolchain — shipped on petfish.ai) and **optional** (course, deploy, testdocs, ppt, calibrate, context, trust, research, reflect — distributed via petfish-market). Install commands resolve automatically — no user-visible difference.

---

## Step 3: Install

### 3a: Install init + companion (global)

```bash
uv run https://raw.githubusercontent.com/kylecui/petfish.ai/master/install.py --pack init,companion --platform <PLATFORM> --global
```

Replace `<PLATFORM>` with the platform you detected in Step 1 (e.g. `codex`, `opencode`, `claude`, etc.).

Run this command and verify it succeeds.

> **Note**: The install script automatically downloads from the **latest stable release**. No need to specify a version — you always get the latest verified build. The script includes automatic mirror fallback (`ghfast.top`, `ghproxy.com`) for China network environments.

### 3b: Install the packs based on the user's choice from Step 2

Install all selected packs in one command:

```bash
uv run https://raw.githubusercontent.com/kylecui/petfish.ai/master/install.py --pack <ALIAS1,ALIAS2,...> --platform <PLATFORM>
```

Replace `<ALIAS1,ALIAS2,...>` with a comma-separated list of the packs the user selected (e.g. `course,petfish` for the course profile, or `deploy,petfish,testdocs` for the code profile).

Example — **course** profile:

```bash
uv run https://raw.githubusercontent.com/kylecui/petfish.ai/master/install.py --pack course,petfish --platform opencode
```

Example — **code** profile (init + companion already installed in 3a):

```bash
uv run https://raw.githubusercontent.com/kylecui/petfish.ai/master/install.py --pack deploy,petfish,testdocs --platform claude
```

Example — **comprehensive** profile (all packs at once, init+companion already done):

```bash
uv run https://raw.githubusercontent.com/kylecui/petfish.ai/master/install.py --pack course,deploy,petfish,ppt,testdocs,trust,context,research,reflect --platform opencode
```

> **Core vs Optional**: Core packs (init, companion, petfish, toolchain) download directly from the petfish.ai release. Optional packs (course, research, etc.) resolve via petfish-market — same command, same experience. The installer queries the market index automatically when a pack is not found in the core set.

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

- **`uv` not found**: Install uv from https://docs.astral.sh/uv/getting-started/installation/
- **`uv run` fails to fetch `install.py`**: The script includes automatic mirror fallback (`ghfast.top` → `ghproxy.com`). If all mirrors fail, see the Offline / Network-Restricted section below.
- **Platform auto-detection picks the wrong platform**: As an AI agent, you should always use `--platform <name>` explicitly instead of `--detect` — you know your own runtime platform.
- **PEP 723 bootstrap is slow on first run**: `uv run` resolves inline script metadata on first invocation. Subsequent runs are cached. If timeout occurs, retry once.
- **Permission denied on `--global`**: The global install directory may need to be created. The installer handles this automatically; if it fails, check `uv` permissions.

---

## Offline / Network-Restricted Install

If the user's environment cannot access GitHub (firewall, air-gapped, China network issues), use one of these options.

### Option 1: Clone and run locally

1. On a machine with network access, clone the repo:
   ```bash
   git clone https://github.com/kylecui/petfish.ai.git
   ```

2. Transfer the cloned repo to the target machine via USB, internal file share, or SCP.

3. Run the installer locally with `--offline`:
   ```bash
   cd petfish.ai
   uv run ./install.py --pack <alias> --platform <PLATFORM> --offline
   ```

   The `--offline` flag forces the installer to use only local files — no network requests, no mirror fallback.

### Option 2: GitHub token for private repo or rate limiting

If the repo is private or rate-limited, set `GITHUB_TOKEN` in the environment:

```bash
GITHUB_TOKEN=xxx uv run https://raw.githubusercontent.com/kylecui/petfish.ai/master/install.py --pack <alias> --platform <PLATFORM>
```

The installer reads `GITHUB_TOKEN` from the environment and uses it for all GitHub API and download requests.

---

## About PEtFiSh

**GitHub**: https://github.com/kylecui/petfish.ai
**Website**: https://petfish.ai
**What it does**: Manages AI skill lifecycle across 8 platforms — discover, create, validate, optimize, install, track. 4 core packs + 9 optional packs via petfish-market.
