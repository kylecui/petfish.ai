# PEtFiSh Install Guide

---

## One-Line Install (Recommended)

Paste this into any AI coding assistant — it handles the rest:

```
Install PEtFiSh by following: https://raw.githubusercontent.com/kylecui/petfish.ai/master/docs/agent-install.md
```

**How it works**: The AI assistant reads the install doc from that URL, auto-detects your OS and AI platform, asks a few questions, then runs the right install commands. Conversational — just answer the prompts.

**Works with**: Any AI coding assistant that can run terminal commands — OpenCode, Claude Code, Cursor, Copilot, Windsurf, Codex, Antigravity.

---

## Command-Line Install

Prefer running commands directly?

**Bash (macOS / Linux / WSL):**
```bash
curl -fsSL https://raw.githubusercontent.com/kylecui/petfish.ai/master/remote-install.sh \
  | bash -s -- --pack init,companion --detect
```

**PowerShell (Windows):**
```powershell
& ([scriptblock]::Create((irm https://raw.githubusercontent.com/kylecui/petfish.ai/master/remote-install.ps1))) -Pack "init,companion" -Detect
```

After install, type `/initproject` — PEtFiSh asks your project type and auto-installs matching packs.

---

## Install Everything

```bash
curl -fsSL https://raw.githubusercontent.com/kylecui/petfish.ai/master/remote-install.sh \
  | bash -s -- --pack all --detect
```

---

## Upgrade

Already installed? Re-run with `--force` to upgrade.

```bash
curl -fsSL https://raw.githubusercontent.com/kylecui/petfish.ai/master/remote-install.sh \
  | bash -s -- --pack all --force
```

Or let your AI handle it:

```
Upgrade PEtFiSh by following: https://raw.githubusercontent.com/kylecui/petfish.ai/master/docs/agent-upgrade.md
```

---

## Notes

- The installer auto-resolves the latest stable release — no version pinning needed.
- `--detect` auto-detects your AI platform and installs to the right path.
- `--pack init,companion` installs the initializer and companion first — add more packs later as needed.
- Need a specific platform? Use `--platform cursor` / `--platform claude` / `--platform copilot`.
- Need a specific version? Use `--branch v0.6.4` (Bash) or `-Branch v0.6.4` (PowerShell).

---

*><(((^> PEtFiSh — Your AI Companion*
